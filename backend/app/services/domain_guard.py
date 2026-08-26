"""Deterministic scope guard for explicitly selected specialist agents."""

from __future__ import annotations

from dataclasses import dataclass

from app.agents.intent import IntentRouter

_LABELS = {
    "legal": "juridique",
    "finance": "financier",
    "compliance": "conformité",
}
_COMMANDS = {
    "legal": "/legal",
    "finance": "/finance",
    "compliance": "/compliance",
}


@dataclass(frozen=True, slots=True)
class DomainAssessment:
    """Result of checking one question against a selected agent domain."""

    allowed: bool
    target_domain: str
    detected_domains: tuple[str, ...]
    keywords_hit: tuple[str, ...]
    message: str | None = None


class DomainGuardService:
    """Prevent a selected specialist from answering outside its mandate.

    A selected agent may answer only when its domain is at least as strong as
    every other domain (keyword-hit majority, ties keep the selected agent).
    Foreign-dominated or out-of-scope questions are refused immediately — no
    retrieval, no LLM.
    """

    def __init__(self, router: IntentRouter | None = None) -> None:
        self._router = router or IntentRouter()

    def assess(self, query: str, *, target_domain: str) -> DomainAssessment:
        match = self._router.detect(query)
        detected = match.domains
        scores = match.domain_scores
        target_hits = scores.get(target_domain, 0)
        other_max = max(
            (score for domain, score in scores.items() if domain != target_domain),
            default=0,
        )

        # Target must not be dominated by another specialty.
        if target_hits > 0 and target_hits >= other_max:
            return DomainAssessment(
                allowed=True,
                target_domain=target_domain,
                detected_domains=detected,
                keywords_hit=match.keywords_hit,
            )

        target_label = _LABELS.get(target_domain, target_domain)
        if detected:
            # Prefer the strongest foreign domain for the redirect hint.
            suggested = next(
                (domain for domain in detected if domain != target_domain),
                detected[0],
            )
            suggested_label = _LABELS.get(suggested, suggested)
            if target_hits > 0 and other_max > target_hits:
                message = (
                    f"Cette question dépasse le domaine {target_label} "
                    f"(elle touche surtout le domaine {suggested_label}). "
                    f"Utilisez {_COMMANDS.get(suggested, f'/{suggested}')} "
                    "ou retirez le préfixe d’agent pour une analyse croisée."
                )
            else:
                message = (
                    f"Cette question ne relève pas du domaine {target_label}. "
                    f"Elle semble relever du domaine {suggested_label}. "
                    f"Utilisez la commande {_COMMANDS.get(suggested, f'/{suggested}')}."
                )
        else:
            message = (
                f"Cette question ne relève pas clairement du domaine {target_label}. "
                "Reformulez-la avec des éléments propres à ce domaine ou choisissez "
                "un autre assistant."
            )

        return DomainAssessment(
            allowed=False,
            target_domain=target_domain,
            detected_domains=detected,
            keywords_hit=match.keywords_hit,
            message=message,
        )


__all__ = ["DomainAssessment", "DomainGuardService"]
