"""Redis state store for durable, reconnectable analysis/synthesis jobs.

The same store powers two owner-scoped, document-scoped background jobs — the
legal contract analysis and the multi-agent synthesis — distinguished only by
their Redis key prefixes and user-facing messages.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError
from app.services.progress import get_redis_client

_PREFIX = "analysis:job:"
_ACTIVE_PREFIX = "analysis:active:"
_SYNTHESIS_PREFIX = "synthesis:job:"
_SYNTHESIS_ACTIVE_PREFIX = "synthesis:active:"

# An in-flight job whose state has not advanced for this long is considered
# orphaned (its worker died) and must not be reused for idempotency.
_STALE_AFTER = timedelta(minutes=15)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _is_stale(row: dict[str, str]) -> bool:
    raw = row.get("updated_at")
    if not raw:
        return False
    try:
        updated = datetime.fromisoformat(str(raw))
    except ValueError:
        return False
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - updated >= _STALE_AFTER


class AnalysisJobStore:
    def __init__(
        self,
        client: Any | None = None,
        *,
        prefix: str = _PREFIX,
        active_prefix: str = _ACTIVE_PREFIX,
        kind: str = "analysis",
        messages: dict[str, str] | None = None,
        not_found_message: str = "Cette analyse est introuvable.",
    ) -> None:
        self._client = client if client is not None else get_redis_client()
        self._ttl = get_settings().chat_job_ttl_seconds
        self._prefix = prefix
        self._active_prefix = active_prefix
        # Task-center discriminator: analysis and synthesis jobs share the same
        # hash shape, so a stored ``kind`` field tells them apart.
        self._kind = kind
        self._messages = {
            "queued": "Analyse en attente…",
            "processing": "Analyse juridique en cours…",
            "completed": "Analyse terminée.",
            "failed": "L’analyse a échoué.",
            "cancelled": "Analyse arrêtée à votre demande.",
            **(messages or {}),
        }
        self._not_found_message = not_found_message

    def _require_client(self) -> Any:
        if self._client is None:
            raise AppError(
                "Le service de reprise des tâches est momentanément indisponible.",
                status_code=503,
                code="jobs_unavailable",
                retryable=True,
            )
        return self._client

    def _key(self, job_id: str) -> str:
        return f"{self._prefix}{job_id}"

    def _active_key(self, user_id: UUID, document_id: UUID) -> str:
        return f"{self._active_prefix}{user_id}:{document_id}"

    async def create(
        self,
        job_id: str,
        *,
        user_id: UUID,
        document_id: UUID,
        title: str | None = None,
    ) -> None:
        client = self._require_client()
        key = self._key(job_id)
        await asyncio.to_thread(
            client.hset,
            key,
            mapping={
                "job_id": job_id,
                "user_id": str(user_id),
                "document_id": str(document_id),
                "kind": self._kind,
                "title": (title or "").strip()[:255],
                "status": "queued",
                "progress": "5",
                "message": self._messages["queued"],
                "task_id": "",
                "result": "",
                "error": "",
                "created_at": _now_iso(),
                "updated_at": _now_iso(),
            },
        )
        await asyncio.to_thread(client.expire, key, self._ttl)

    async def create_or_get_active(
        self,
        job_id: str,
        *,
        user_id: UUID,
        document_id: UUID,
        title: str | None = None,
    ) -> tuple[str, bool]:
        """Atomically reuse an active job for the same owner/document."""
        client = self._require_client()
        active_key = self._active_key(user_id, document_id)
        lock_key = f"{active_key}:lock"
        key = self._key(job_id)
        mapping = {
            "job_id": job_id,
            "user_id": str(user_id),
            "document_id": str(document_id),
            "kind": self._kind,
            "title": (title or "").strip()[:255],
            "status": "queued",
            "progress": "5",
            "message": self._messages["queued"],
            "task_id": "",
            "result": "",
            "error": "",
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
        }

        def claim() -> tuple[str, bool]:
            with client.lock(lock_key, timeout=5, blocking_timeout=3):
                existing_id = client.get(active_key)
                if existing_id:
                    existing = client.hgetall(self._key(existing_id))
                    if (
                        existing.get("status") in {"queued", "processing"}
                        and not _is_stale(existing)
                    ):
                        return str(existing_id), False
                    client.delete(active_key)
                else:
                    # Backfill jobs created before the active-index existed.
                    for existing_key in client.scan_iter(
                        match=f"{self._prefix}*", count=200
                    ):
                        existing = client.hgetall(existing_key)
                        if (
                            existing.get("user_id") == str(user_id)
                            and existing.get("document_id") == str(document_id)
                            and existing.get("status") in {"queued", "processing"}
                            and not _is_stale(existing)
                        ):
                            existing_id = existing.get("job_id")
                            if existing_id:
                                client.set(
                                    active_key,
                                    existing_id,
                                    ex=self._ttl,
                                )
                                return str(existing_id), False

                pipe = client.pipeline()
                pipe.hset(key, mapping=mapping)
                pipe.expire(key, self._ttl)
                pipe.set(active_key, job_id, ex=self._ttl)
                pipe.execute()
                return job_id, True

        return await asyncio.to_thread(claim)

    async def set_task_id(self, job_id: str, task_id: str) -> None:
        await self._update(job_id, task_id=task_id)

    async def is_cancelled(self, job_id: str) -> bool:
        """Whether the job was cancelled — used to short-circuit worker reruns."""
        client = self._client
        if client is None:
            return False
        status = await asyncio.to_thread(client.hget, self._key(job_id), "status")
        return status == "cancelled"

    async def mark_processing(self, job_id: str) -> None:
        # Never resurrect a job the user has cancelled (e.g. an acks_late redelivery
        # of a revoked task re-entering the worker).
        if await self.is_cancelled(job_id):
            return
        await self._update(
            job_id,
            status="processing",
            progress="20",
            message=self._messages["processing"],
        )

    async def mark_completed(
        self,
        job_id: str,
        result: dict[str, Any],
    ) -> None:
        if await self.is_cancelled(job_id):
            await self._release_active(job_id)
            return
        await self._update(
            job_id,
            status="completed",
            progress="100",
            message=self._messages["completed"],
            result=json.dumps(result, default=str, ensure_ascii=False),
            error="",
        )
        await self._release_active(job_id)

    async def mark_failed(self, job_id: str, message: str) -> None:
        if await self.is_cancelled(job_id):
            await self._release_active(job_id)
            return
        await self._update(
            job_id,
            status="failed",
            progress="100",
            message=self._messages["failed"],
            error=message,
        )
        await self._release_active(job_id)

    async def mark_cancelled(self, job_id: str) -> None:
        await self._update(
            job_id,
            status="cancelled",
            progress="100",
            message=self._messages["cancelled"],
            error="",
        )
        await self._release_active(job_id)

    async def get_for_user(
        self,
        job_id: str,
        *,
        user_id: UUID,
    ) -> dict[str, Any]:
        client = self._require_client()
        raw = await asyncio.to_thread(client.hgetall, self._key(job_id))
        if not raw or raw.get("user_id") != str(user_id):
            raise NotFoundError(self._not_found_message)
        result = None
        if raw.get("result"):
            try:
                result = json.loads(raw["result"])
            except (TypeError, ValueError):
                result = None
        return {
            **raw,
            "progress": int(raw.get("progress") or 0),
            "result": result,
            "error": raw.get("error") or None,
        }

    async def _update(self, job_id: str, **fields: str) -> None:
        client = self._require_client()
        key = self._key(job_id)
        await asyncio.to_thread(
            client.hset,
            key,
            mapping={**fields, "updated_at": _now_iso()},
        )
        await asyncio.to_thread(client.expire, key, self._ttl)

    async def _release_active(self, job_id: str) -> None:
        client = self._require_client()
        meta = await asyncio.to_thread(client.hgetall, self._key(job_id))
        if not meta.get("user_id") or not meta.get("document_id"):
            return
        active_key = self._active_key(
            UUID(meta["user_id"]),
            UUID(meta["document_id"]),
        )

        def release() -> None:
            if client.get(active_key) == job_id:
                client.delete(active_key)

        await asyncio.to_thread(release)


@lru_cache
def get_analysis_job_store() -> AnalysisJobStore:
    return AnalysisJobStore()


@lru_cache
def get_synthesis_job_store() -> AnalysisJobStore:
    return AnalysisJobStore(
        prefix=_SYNTHESIS_PREFIX,
        active_prefix=_SYNTHESIS_ACTIVE_PREFIX,
        kind="synthesis",
        messages={
            "queued": "Synthèse en attente…",
            "processing": "Synthèse multi-agents en cours…",
            "completed": "Synthèse terminée.",
            "failed": "La synthèse a échoué.",
        },
        not_found_message="Cette synthèse est introuvable.",
    )


__all__ = [
    "AnalysisJobStore",
    "get_analysis_job_store",
    "get_synthesis_job_store",
]
