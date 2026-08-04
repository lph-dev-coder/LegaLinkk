"""Generate, brand, render and persist a report as one reusable operation."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.generated_document import GeneratedDocumentKind
from app.services.domain_guard import DomainGuardService
from app.services.generated_document import GeneratedDocumentService
from app.services.generator import GeneratorService
from app.services.pdf import brand_report_html, render_html_to_pdf

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class _DomainReport:
    """A specialist lens for a slash-command PDF report."""

    focus: str
    title_prefix: str
    default_question: str
    #: Domain enforced by ``DomainGuardService`` (``legal`` | ``finance`` |
    #: ``compliance``). ``None`` for the cross-disciplinary synthesis, which by
    #: design accepts any angle and is therefore never guarded.
    guard_domain: str | None = None


# A leading ``/command`` in *Génération PDF* mode produces a domain-oriented
# report. The focus text is prepended (brace-free) to the shared document
# instructions in ``GeneratorService`` — it sets ONLY the analytical lens; the
# HTML format and the reproducible-scoring method stay the single source of
# truth in ``DOCUMENT_SYSTEM_INSTRUCTIONS``.
_DOMAIN_REPORTS: dict[str, _DomainReport] = {
    "legal": _DomainReport(
        focus=(
            "REPORT FOCUS — JURIDIQUE. Adopt the perspective of a contract "
            "lawyer. Prioritise legal risk: clause validity, unlawful / abusive "
            "/ léonine clauses, imbalance between the parties, liability, "
            "termination, penalties, missing or broken references and "
            "enforceability. Frame every finding and the risk table around legal "
            "exposure."
        ),
        title_prefix="Rapport juridique",
        default_question=(
            "Analyse les clauses et les risques juridiques de ce contrat et "
            "produis un rapport complet."
        ),
        guard_domain="legal",
    ),
    "finance": _DomainReport(
        focus=(
            "REPORT FOCUS — FINANCIER. Adopt the perspective of a financial "
            "analyst. Prioritise the financial impact of the contract: prices "
            "and amounts, payment terms and delays, penalties and late-payment "
            "interest, indexation / price revision, caps and monetary liability "
            "exposure, cash-flow and budget risk. Quantify amounts and delays "
            "wherever the contract states them and frame the risk table around "
            "financial exposure."
        ),
        title_prefix="Rapport financier",
        default_question=(
            "Analyse les montants, paiements et risques financiers de ce contrat "
            "et produis un rapport complet."
        ),
        guard_domain="finance",
    ),
    "compliance": _DomainReport(
        focus=(
            "REPORT FOCUS — CONFORMITÉ. Adopt the perspective of a regulatory & "
            "compliance officer. Prioritise regulatory conformity: RGPD / "
            "personal-data processing, applicable law and mandatory provisions, "
            "consumer / public-order rules, audit and reporting obligations, and "
            "any clause that is non-compliant or exposes the party to sanctions. "
            "Frame the risk table around compliance and regulatory exposure."
        ),
        title_prefix="Rapport de conformité",
        default_question=(
            "Analyse la conformité réglementaire et RGPD de ce contrat et "
            "produis un rapport complet."
        ),
        guard_domain="compliance",
    ),
    "synthese": _DomainReport(
        focus=(
            "REPORT FOCUS — SYNTHÈSE GLOBALE. Produce a cross-disciplinary "
            "report that explicitly crosses and weighs three angles: juridique, "
            "financier et conformité (RGPD / réglementaire). Cover each angle, "
            "then give a consolidated global recommendation that balances the "
            "three. In the risk table, flag for each problematic clause which "
            "angle(s) it concerns."
        ),
        title_prefix="Rapport de synthèse",
        default_question=(
            "Analyse ce contrat sous les angles juridique, financier et "
            "conformité, et produis un rapport de synthèse complet."
        ),
    ),
}

# Aliases → canonical domain. ``/juridique`` mirrors the French label the user
# sees; the synthesis synonyms mirror the frontend slash menu.
_DOMAIN_ALIASES: dict[str, str] = {
    "legal": "legal",
    "juridique": "legal",
    "finance": "finance",
    "financier": "finance",
    "compliance": "compliance",
    "conformite": "compliance",
    "conformité": "compliance",
    "synthese": "synthese",
    "synthèse": "synthese",
    "synth": "synthese",
    "tous": "synthese",
    "all": "synthese",
}

_COMMAND_RE = re.compile(
    r"^\s*/([\wàâçéèêëîïôûùüÿñæœ]+)\b[ \t]*(.*)$",
    re.IGNORECASE | re.DOTALL,
)


def resolve_report_request(question: str) -> tuple[_DomainReport | None, str]:
    """Split a leading ``/command`` off the report request.

    Returns ``(domain_report | None, clean_question)``. When a specialist
    command is present the slash token is stripped (so it never leaks into the
    LLM prompt) and, if the user typed only the command, a domain default
    question is used. A plain request returns ``(None, question)`` — the
    standard general report.
    """
    raw = (question or "").strip()
    match = _COMMAND_RE.match(raw)
    if not match:
        return None, raw
    canonical = _DOMAIN_ALIASES.get(match.group(1).lower())
    if canonical is None:
        return None, raw
    domain = _DOMAIN_REPORTS[canonical]
    remainder = (match.group(2) or "").strip()
    return domain, (remainder or domain.default_question)


class ReportGenerationService:
    def __init__(self, session: AsyncSession) -> None:
        self._generator = GeneratorService(session)
        self._documents = GeneratedDocumentService(session)
        self._domain_guard = DomainGuardService()

    async def generate(
        self,
        question: str,
        *,
        user_id: UUID,
        document_id: UUID | None = None,
        top_k: int | None = None,
        final_k: int | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        domain, clean_question = resolve_report_request(question)

        # A specialist slash command (/legal, /finance, /compliance) is a scoped
        # mandate: refuse — without generating a PDF — when the request clearly
        # belongs to another domain (e.g. "/legal" + a purely financial ask).
        # The synthesis lens (guard_domain=None) is cross-disciplinary and never
        # guarded.
        if domain is not None and domain.guard_domain is not None:
            assessment = self._domain_guard.assess(
                clean_question,
                target_domain=domain.guard_domain,
            )
            if not assessment.allowed:
                logger.info(
                    "[report] rejected out-of-domain target=%s detected=%s",
                    domain.guard_domain,
                    assessment.detected_domains,
                )
                return {
                    "status": "out_of_scope",
                    "message": assessment.message,
                    "answer": assessment.message,
                    "sources": [],
                    "metadata": {
                        "target_domain": domain.guard_domain,
                        "detected_domains": list(assessment.detected_domains),
                    },
                }

        result = await self._generator.generate_document(
            clean_question,
            user_id=user_id,
            top_k=top_k,
            final_k=final_k,
            temperature=temperature,
            max_tokens=max_tokens,
            document_id=document_id,
            report_focus=domain.focus if domain else None,
        )
        result["html"] = brand_report_html(result["html"])
        pdf_bytes = await asyncio.to_thread(render_html_to_pdf, result["html"])
        title_prefix = domain.title_prefix if domain else "Rapport"
        title = f"{title_prefix} — {clean_question.strip()[:100]}"
        source_ids = {
            UUID(str(source["document_id"]))
            for source in result.get("sources", [])
            if source.get("document_id")
        }
        source_document_id = document_id or (
            next(iter(source_ids)) if len(source_ids) == 1 else None
        )
        generated = await self._documents.save_pdf(
            pdf_bytes,
            user_id=user_id,
            source_document_id=source_document_id,
            title=title,
            filename=f"{title}.pdf",
            kind=GeneratedDocumentKind.CHAT_REPORT,
            question=clean_question,
        )
        return {**result, "status": "ok", "generated_document_id": generated.id}


__all__ = ["ReportGenerationService", "resolve_report_request"]
