"""Read-only aggregation of a user's recent Redis-backed background tasks."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import AppError, NotFoundError
from app.core.logging import get_logger
from app.services.progress import get_redis_client

logger = get_logger(__name__)

_TERMINAL = {"completed", "failed", "cancelled"}

# An in-flight analysis/synthesis job whose Redis state has not advanced for
# this long is treated as orphaned (its worker died, e.g. a deploy/restart) and
# reaped so it stops blocking the active-job index and the "En cours" list.
_STALE_AFTER = timedelta(minutes=15)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


class TaskCenterService:
    def __init__(self, client: Any | None = None) -> None:
        self._client = client if client is not None else get_redis_client()

    async def list_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        if self._client is None:
            raise AppError(
                "Le centre des tâches est momentanément indisponible.",
                status_code=503,
                code="task_center_unavailable",
                retryable=True,
            )

        owner = str(user_id)

        def read() -> list[dict[str, str]]:
            rows: list[dict[str, str]] = []
            # (scan pattern, authoritative kind, active-index prefix). The kind is
            # derived from the key prefix — never from the stored field — so jobs
            # created before the ``kind`` column existed are still classified (and
            # therefore cancellable) correctly.
            job_patterns = (
                ("chat:job:*:meta", None, None),
                ("analysis:job:*", "analysis", "analysis:active:"),
                ("synthesis:job:*", "synthesis", "synthesis:active:"),
                ("comparison:job:*", "comparison", "comparison:active:"),
            )
            now = datetime.now(timezone.utc)
            for pattern, kind, active_prefix in job_patterns:
                for key in self._client.scan_iter(match=pattern, count=200):
                    payload = self._client.hgetall(key)
                    if not payload or payload.get("user_id") != owner:
                        continue
                    if kind is not None:
                        payload["kind"] = kind
                        if self._reap_if_stale(
                            key, payload, active_prefix, now
                        ):
                            payload = self._client.hgetall(key)
                            payload["kind"] = kind
                    rows.append(payload)
            for key in self._client.scan_iter(
                match="ingestion:progress:*", count=200
            ):
                raw = self._client.get(key)
                try:
                    payload = json.loads(raw) if raw else {}
                except (TypeError, ValueError):
                    payload = {}
                if payload.get("user_id") == owner:
                    rows.append(payload)
            return rows

        rows = await asyncio.to_thread(read)
        items = [self._normalize(row) for row in rows]
        active_analyses: dict[str, dict[str, Any]] = {}
        visible: list[dict[str, Any]] = []
        for item in items:
            if (
                item["type"] in {"analysis", "synthesis"}
                and item["status"] in {"queued", "processing"}
                and item["document_id"]
            ):
                key = f'{item["type"]}:{item["document_id"]}'
                current = active_analyses.get(key)
                if current is None or (
                    item["progress"],
                    item["updated_at"],
                ) > (
                    current["progress"],
                    current["updated_at"],
                ):
                    active_analyses[key] = item
            else:
                visible.append(item)
        # Collapse legacy terminal duplicates created by the same UI action.
        # Deliberate re-analyses performed later remain visible as separate work.
        visible.sort(key=lambda item: item["created_at"], reverse=True)
        deduplicated_visible: list[dict[str, Any]] = []
        latest_terminal_analysis: dict[str, datetime] = {}
        for item in visible:
            if item["type"] in {"analysis", "synthesis"} and item["document_id"]:
                try:
                    created_at = datetime.fromisoformat(str(item["created_at"]))
                except ValueError:
                    created_at = None
                key = f'{item["type"]}:{item["document_id"]}'
                previous = latest_terminal_analysis.get(key)
                if (
                    created_at is not None
                    and previous is not None
                    and abs((previous - created_at).total_seconds()) <= 5
                ):
                    continue
                if created_at is not None:
                    latest_terminal_analysis[key] = created_at
            deduplicated_visible.append(item)

        items = [*deduplicated_visible, *active_analyses.values()]
        items.sort(key=lambda item: item["created_at"], reverse=True)
        return items[:100]

    def _reap_if_stale(
        self,
        key: str,
        payload: dict[str, str],
        active_prefix: str | None,
        now: datetime,
    ) -> bool:
        """Fail an orphaned in-flight analysis/synthesis job in place.

        Returns ``True`` when the job was reaped so the caller can re-read it.
        A job counts as orphaned when it is still ``queued``/``processing`` but
        its ``updated_at`` is older than :data:`_STALE_AFTER` — its worker is
        gone (typically a restart/deploy), so it would otherwise block the
        active-job index forever.
        """
        if payload.get("status") not in {"queued", "processing"}:
            return False
        updated = _parse_iso(payload.get("updated_at"))
        if updated is None or now - updated < _STALE_AFTER:
            return False
        try:
            self._client.hset(
                key,
                mapping={
                    "status": "failed",
                    "progress": "100",
                    "message": "La tâche a été interrompue.",
                    "error": "Tâche interrompue (service indisponible). Relancez-la.",
                    "updated_at": now.isoformat(),
                },
            )
            if active_prefix:
                user_id = payload.get("user_id")
                document_id = payload.get("document_id")
                job_id = payload.get("job_id")
                if (
                    payload.get("kind") == "comparison"
                    and user_id
                    and payload.get("base_document_id")
                    and payload.get("target_document_id")
                    and job_id
                ):
                    active_key = (
                        f"{active_prefix}{user_id}:"
                        f'{payload["base_document_id"]}:'
                        f'{payload["target_document_id"]}'
                    )
                    if self._client.get(active_key) == job_id:
                        self._client.delete(active_key)
                if user_id and document_id and job_id:
                    active_key = f"{active_prefix}{user_id}:{document_id}"
                    if self._client.get(active_key) == job_id:
                        self._client.delete(active_key)
            logger.info("Reaped orphaned task key=%s", key)
        except Exception:  # pragma: no cover - best-effort cleanup
            logger.exception("Failed to reap orphaned task key=%s", key)
            return False
        return True

    async def cancel(
        self,
        task_id: str,
        *,
        task_type: str,
        user_id: UUID,
    ) -> None:
        """Stop a running background task and mark it cancelled.

        Dispatches to the store that owns the task, revokes the underlying
        Celery task (if any) and flips its Redis state to ``cancelled`` so the
        Task Center reflects the change immediately.
        """
        if task_type in {"chat", "agent", "report"}:
            from app.services.chat_job import get_chat_job_store

            store = get_chat_job_store()
            meta = await store.get_meta_for_user(task_id, user_id=user_id)
            if meta.get("status") in _TERMINAL:
                return
            await self._revoke(meta.get("task_id"))
            await store.mark_cancelled(task_id)
            return

        if task_type in {"analysis", "synthesis"}:
            from app.services.analysis_job import (
                get_analysis_job_store,
                get_synthesis_job_store,
            )

            store = (
                get_analysis_job_store()
                if task_type == "analysis"
                else get_synthesis_job_store()
            )
            meta = await store.get_for_user(task_id, user_id=user_id)
            if meta.get("status") in _TERMINAL:
                return
            await self._revoke(meta.get("task_id"))
            await store.mark_cancelled(task_id)
            return

        if task_type == "comparison":
            from app.services.comparison_job import get_comparison_job_store

            store = get_comparison_job_store()
            meta = await store.get_for_user(task_id, user_id=user_id)
            if meta.get("status") in _TERMINAL:
                return
            await self._revoke(meta.get("task_id"))
            await store.mark_cancelled(task_id)
            return

        if task_type == "ingestion":
            from app.services.progress import get_ingestion_progress_service

            tracker = get_ingestion_progress_service()
            payload = await tracker.get(task_id)
            if not payload or payload.get("user_id") != str(user_id):
                raise NotFoundError("Cette tâche est introuvable.")
            if payload.get("status") in _TERMINAL:
                return
            await self._revoke(payload.get("task_id"))
            await tracker.mark_cancelled(task_id)
            return

        raise AppError(
            "Ce type de tâche ne peut pas être arrêté.",
            status_code=400,
            code="task_not_cancellable",
        )

    @staticmethod
    async def _revoke(celery_task_id: str | None) -> None:
        if not celery_task_id:
            return
        from app.core.celery_app import celery_app

        try:
            await asyncio.to_thread(
                celery_app.control.revoke,
                celery_task_id,
                terminate=True,
                signal="SIGTERM",
            )
        except Exception as exc:  # pragma: no cover - broker/control failure
            logger.exception("Could not revoke task task_id=%s", celery_task_id)
            raise AppError(
                "La tâche n'a pas pu être arrêtée. Veuillez réessayer.",
                status_code=503,
                code="task_cancel_failed",
                retryable=True,
            ) from exc

    @staticmethod
    def _normalize(row: dict[str, str]) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        mode = row.get("mode")
        task_type = (
            mode
            if mode in {"chat", "agent", "report"}
            else "ingestion"
            if row.get("stage")
            else "synthesis"
            if row.get("kind") == "synthesis"
            else "comparison"
            if row.get("kind") == "comparison"
            else "analysis"
        )
        status = row.get("status") or "queued"
        progress = int(
            row.get("progress")
            or (
                100
                if status in {"completed", "failed", "cancelled"}
                else 35
                if status == "processing"
                else 5
            )
        )
        labels = {
            "chat": "Réponse à une question",
            "agent": "Consultation spécialisée",
            "report": "Génération d’un rapport",
            "analysis": "Analyse de contrat",
            "synthesis": "Synthèse multi-agents",
            "comparison": "Comparaison de contrats",
            "ingestion": "Préparation d’un document",
        }
        messages = {
            "queued": "En attente…",
            "processing": "Traitement en cours…",
            "completed": "Terminé",
            "failed": "Échec",
            "cancelled": "Annulée",
        }
        document_id = (
            row.get("document_id")
            or row.get("base_document_id")
            or None
        )
        base_document_id = row.get("base_document_id")
        target_document_id = row.get("target_document_id")
        comparison_destination = (
            f"/comparisons?base={base_document_id}&target={target_document_id}"
            if base_document_id and target_document_id
            else "/comparisons"
        )
        ingestion_destination = (
            f"/documents?upload={document_id}" if document_id else "/documents"
        )
        destination = (
            comparison_destination
            if task_type == "comparison"
            else
            f"/analysis/{document_id}"
            if task_type in {"analysis", "synthesis"} and document_id
            else ingestion_destination
            if task_type == "ingestion"
            else "/consultation"
        )
        raw_title = (row.get("title") or "").strip()
        title = (
            f"Préparation — {raw_title}"
            if task_type == "ingestion" and raw_title
            else raw_title or labels[task_type]
        )
        ingestion_messages = {
            "queued": "En attente de préparation…",
            "extracting": "Lecture du document…",
            "ocr": "Lecture des pages numérisées…",
            "cleaning": "Préparation du contenu…",
            "chunking": "Structuration du document…",
            "embedding": "Préparation pour la consultation…",
            "persisting": "Enregistrement du document…",
            "indexing": "Finalisation…",
            "completed": "Document prêt",
            "failed": "La préparation a échoué",
        }
        return {
            "id": row.get("job_id") or row["document_id"],
            "type": task_type,
            "title": title,
            "status": status,
            "progress": progress,
            "message": (
                ingestion_messages.get(row.get("stage", ""), messages.get(status, status))
                if task_type == "ingestion"
                else row.get("message") or messages.get(status, status)
            ),
            "document_id": document_id,
            "destination": destination,
            "created_at": row.get("created_at") or now,
            "updated_at": row.get("updated_at") or now,
            "error": row.get("error") or None,
        }


__all__ = ["TaskCenterService"]
