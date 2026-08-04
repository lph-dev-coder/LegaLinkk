"""Full-document semantic comparison for two owned contracts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.analysis import AnalysisStatus
from app.models.comparison import COMPARISON_VERSION, ContractComparison
from app.repositories.comparison import ContractComparisonRepository
from app.repositories.document import DocumentRepository
from app.services.context_formatter import chunks_from_reranked, merge_chunks
from app.services.llm import LLMProvider, get_llm_provider
from app.services.retrieval import RetrievalService

logger = get_logger(__name__)

_PROCESS_STARTED_AT: dict[tuple[UUID, UUID], datetime] = {}
_STALE_AFTER_SECONDS = 15 * 60

COMPARISON_SYSTEM_PROMPT = """Tu es LegalLink Compare, expert en comparaison contractuelle.

Tu reçois deux versions complètes de contrats : VERSION A (contrat de référence) et VERSION B
(nouvelle version). Compare-les clause par clause, sans inventer de texte absent.

Règles strictes :
1. Couvre toutes les clauses des deux versions. Une clause présente uniquement dans B est un ajout ;
   présente uniquement dans A est une suppression ; présente dans les deux avec un sens différent
   est une modification ; sinon elle est inchangée.
2. Fais un rapprochement sémantique : les numéros/titres peuvent avoir changé. Compare le sens,
   les obligations, droits, montants, délais, plafonds, résiliation et conformité.
3. Chaque différence doit inclure un impact de risque : low, medium ou high, avec justification.
4. Ne cite aucun montant, pourcentage, article ou délai qui n'apparaisse pas explicitement dans les
   documents. Reproduis les noms de fichiers exactement.
5. Retourne uniquement un JSON valide, sans Markdown ni commentaire, avec cette structure exacte :
{
  "summary": "synthèse exécutive claire",
  "overall_risk_impact": "low | medium | high",
  "added_count": 0,
  "removed_count": 0,
  "modified_count": 0,
  "unchanged_count": 0,
  "changes": [
    {
      "clause": "numéro/titre ou description stable",
      "change_type": "added | removed | modified | unchanged",
      "base_text": "résumé fidèle de A ou chaîne vide",
      "target_text": "résumé fidèle de B ou chaîne vide",
      "risk_impact": "low | medium | high",
      "risk_reason": "impact concret",
      "base_pages": [1],
      "target_pages": [1]
    }
  ],
  "recommendations": ["actions prioritaires"]
}
"""


def _strip_json_fence(text: str) -> str:
    value = (text or "").strip()
    if value.startswith("```"):
        value = value.split("\n", 1)[1] if "\n" in value else value[3:]
        if value.endswith("```"):
            value = value[:-3]
    return value.strip()


class ContractComparisonService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        retrieval: RetrievalService | None = None,
        llm: LLMProvider | None = None,
    ) -> None:
        self._session = session
        self._settings = settings or get_settings()
        self._documents = DocumentRepository(session)
        self._comparisons = ContractComparisonRepository(session)
        self._retrieval = retrieval or RetrievalService(session, settings=self._settings)
        self._llm = llm

    def _get_llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider(self._settings)
        return self._llm

    async def get_cached(
        self,
        *,
        user_id: UUID,
        base_document_id: UUID,
        target_document_id: UUID,
    ) -> dict[str, Any] | None:
        await self._require_documents(user_id, base_document_id, target_document_id)
        row = await self._comparisons.get_by_pair(
            base_document_id, target_document_id
        )
        if (
            row is not None
            and row.status == AnalysisStatus.COMPLETED
            and row.comparison_version == COMPARISON_VERSION
            and row.payload
        ):
            return {**row.payload, "cached": True}
        return None

    async def get_or_compare(
        self,
        *,
        user_id: UUID,
        base_document_id: UUID,
        target_document_id: UUID,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        base, target = await self._require_documents(
            user_id, base_document_id, target_document_id
        )
        fingerprint = hashlib.sha256(
            f"{COMPARISON_VERSION}:{base_document_id}:{target_document_id}".encode()
        ).hexdigest()
        row = await self._comparisons.get_by_pair(
            base_document_id, target_document_id
        )
        if (
            not force_refresh
            and row is not None
            and row.status == AnalysisStatus.COMPLETED
            and row.comparison_version == COMPARISON_VERSION
            and row.request_fingerprint == fingerprint
            and row.payload
        ):
            return {**row.payload, "cached": True}

        pair = (base_document_id, target_document_id)
        if row is not None and row.status == AnalysisStatus.PROCESSING:
            started = _PROCESS_STARTED_AT.get(pair)
            if started and (datetime.now(timezone.utc) - started).total_seconds() < _STALE_AFTER_SECONDS:
                raise AppError(
                    "La comparaison de ces contrats est déjà en cours.",
                    status_code=409,
                    code="comparison_in_progress",
                    retryable=True,
                )

        created = row is None
        if row is None:
            row = ContractComparison(
                base_document_id=base_document_id,
                target_document_id=target_document_id,
                request_fingerprint=fingerprint,
            )
            await self._comparisons.create(row)
        row.status = AnalysisStatus.PROCESSING
        row.payload = None
        row.comparison_version = COMPARISON_VERSION
        row.request_fingerprint = fingerprint
        row.error_message = None
        _PROCESS_STARTED_AT[pair] = datetime.now(timezone.utc)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise AppError(
                "La comparaison de ces contrats est déjà en cours.",
                status_code=409,
                code="comparison_in_progress",
                retryable=True,
            ) from exc

        try:
            payload = await self._compute(
                user_id=user_id,
                base_document_id=base_document_id,
                target_document_id=target_document_id,
                base_filename=base.original_filename,
                target_filename=target.original_filename,
            )
        except Exception as exc:
            logger.exception(
                "Contract comparison failed base=%s target=%s",
                base_document_id,
                target_document_id,
            )
            row.status = AnalysisStatus.FAILED
            row.error_message = (
                exc.message if isinstance(exc, AppError) else "La comparaison a échoué."
            )
            await self._session.commit()
            raise
        finally:
            _PROCESS_STARTED_AT.pop(pair, None)

        row.status = AnalysisStatus.COMPLETED
        row.payload = payload
        row.model = str(payload.get("metadata", {}).get("model") or "") or None
        row.error_message = None
        await self._session.commit()
        return {**payload, "cached": False}

    async def _require_documents(
        self,
        user_id: UUID,
        base_document_id: UUID,
        target_document_id: UUID,
    ):
        if base_document_id == target_document_id:
            raise ValidationError("Sélectionnez deux contrats différents.")
        base = await self._documents.get_by_id(base_document_id, user_id=user_id)
        target = await self._documents.get_by_id(target_document_id, user_id=user_id)
        if base is None or target is None:
            raise NotFoundError("Un des contrats sélectionnés est introuvable.")
        return base, target

    async def _compute(
        self,
        *,
        user_id: UUID,
        base_document_id: UUID,
        target_document_id: UUID,
        base_filename: str,
        target_filename: str,
    ) -> dict[str, Any]:
        base_hits = await self._retrieval.get_document_chunks(
            base_document_id, user_id=user_id
        )
        target_hits = await self._retrieval.get_document_chunks(
            target_document_id, user_id=user_id
        )
        if not base_hits or not target_hits:
            raise ValidationError(
                "Les deux contrats doivent être entièrement préparés avant comparaison."
            )

        per_document_budget = max(
            20_000, self._settings.comparison_context_chars // 2
        )
        base_context, base_used = merge_chunks(
            chunks_from_reranked(base_hits), max_chars=per_document_budget
        )
        target_context, target_used = merge_chunks(
            chunks_from_reranked(target_hits), max_chars=per_document_budget
        )
        logger.info(
            "Comparison full-document contexts base_chunks=%s base_chars=%s "
            "target_chunks=%s target_chars=%s",
            len(base_used),
            len(base_context),
            len(target_used),
            len(target_context),
        )

        user_prompt = (
            f"VERSION A — {base_filename}\n"
            "---------------------\n"
            f"{base_context}\n"
            "=====================\n"
            f"VERSION B — {target_filename}\n"
            "---------------------\n"
            f"{target_context}\n"
            "=====================\n"
            "Produis maintenant le JSON de comparaison clause par clause."
        )
        llm = self._get_llm()
        completion = await llm.complete(
            [
                {"role": "system", "content": COMPARISON_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._settings.llm_temperature,
            max_tokens=self._settings.comparison_max_tokens,
        )
        try:
            parsed = json.loads(_strip_json_fence(completion.content))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AppError(
                "La comparaison générée est incomplète. Veuillez réessayer.",
                status_code=502,
                code="comparison_invalid_response",
                retryable=True,
            ) from exc
        if not isinstance(parsed, dict) or not isinstance(parsed.get("changes"), list):
            raise AppError(
                "La comparaison générée est invalide. Veuillez réessayer.",
                status_code=502,
                code="comparison_invalid_response",
                retryable=True,
            )
        return {
            **parsed,
            "base_document_id": str(base_document_id),
            "target_document_id": str(target_document_id),
            "base_filename": base_filename,
            "target_filename": target_filename,
            "metadata": {
                "provider": llm.provider_name,
                "model": completion.model,
                "tokens_used": completion.total_tokens,
                "base_chunks": len(base_used),
                "target_chunks": len(target_used),
                "base_context_chars": len(base_context),
                "target_context_chars": len(target_context),
                "comparison_version": COMPARISON_VERSION,
            },
        }


__all__ = ["COMPARISON_SYSTEM_PROMPT", "ContractComparisonService"]
