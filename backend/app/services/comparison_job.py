"""Redis store for durable, owner-scoped contract-comparison jobs."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError
from app.services.progress import get_redis_client

_PREFIX = "comparison:job:"
_ACTIVE_PREFIX = "comparison:active:"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ComparisonJobStore:
    def __init__(self, client: Any | None = None) -> None:
        self._client = client if client is not None else get_redis_client()
        self._ttl = get_settings().chat_job_ttl_seconds

    def _require(self):
        if self._client is None:
            raise AppError(
                "Le service de comparaison est momentanément indisponible.",
                status_code=503,
                code="comparison_jobs_unavailable",
                retryable=True,
            )
        return self._client

    @staticmethod
    def _key(job_id: str) -> str:
        return f"{_PREFIX}{job_id}"

    @staticmethod
    def _active_key(user_id: UUID, base_id: UUID, target_id: UUID) -> str:
        return f"{_ACTIVE_PREFIX}{user_id}:{base_id}:{target_id}"

    async def create_or_get_active(
        self,
        job_id: str,
        *,
        user_id: UUID,
        base_document_id: UUID,
        target_document_id: UUID,
        title: str,
    ) -> tuple[str, bool]:
        client = self._require()
        active_key = self._active_key(
            user_id, base_document_id, target_document_id
        )

        def claim() -> tuple[str, bool]:
            with client.lock(
                f"{active_key}:lock", timeout=5, blocking_timeout=3
            ):
                existing_id = client.get(active_key)
                if existing_id:
                    row = client.hgetall(self._key(existing_id))
                    if row.get("status") in {"queued", "processing"}:
                        return str(existing_id), False
                    client.delete(active_key)
                mapping = {
                    "job_id": job_id,
                    "user_id": str(user_id),
                    "base_document_id": str(base_document_id),
                    "target_document_id": str(target_document_id),
                    "kind": "comparison",
                    "title": title[:255],
                    "status": "queued",
                    "progress": "5",
                    "message": "Comparaison en attente…",
                    "task_id": "",
                    "result": "",
                    "error": "",
                    "created_at": _now(),
                    "updated_at": _now(),
                }
                pipe = client.pipeline()
                pipe.hset(self._key(job_id), mapping=mapping)
                pipe.expire(self._key(job_id), self._ttl)
                pipe.set(active_key, job_id, ex=self._ttl)
                pipe.execute()
                return job_id, True

        return await asyncio.to_thread(claim)

    async def set_task_id(self, job_id: str, task_id: str) -> None:
        await self._update(job_id, task_id=task_id)

    async def is_cancelled(self, job_id: str) -> bool:
        client = self._require()
        status = await asyncio.to_thread(
            client.hget, self._key(job_id), "status"
        )
        return status == "cancelled"

    async def mark_processing(self, job_id: str) -> None:
        if not await self.is_cancelled(job_id):
            await self._update(
                job_id,
                status="processing",
                progress="25",
                message="Comparaison clause par clause en cours…",
            )

    async def mark_completed(self, job_id: str, result: dict[str, Any]) -> None:
        if await self.is_cancelled(job_id):
            await self._release(job_id)
            return
        await self._update(
            job_id,
            status="completed",
            progress="100",
            message="Comparaison terminée.",
            result=json.dumps(result, default=str, ensure_ascii=False),
            error="",
        )
        await self._release(job_id)

    async def mark_failed(self, job_id: str, message: str) -> None:
        if await self.is_cancelled(job_id):
            return
        await self._update(
            job_id,
            status="failed",
            progress="100",
            message="La comparaison a échoué.",
            error=message,
        )
        await self._release(job_id)

    async def mark_cancelled(self, job_id: str) -> None:
        await self._update(
            job_id,
            status="cancelled",
            progress="100",
            message="Comparaison arrêtée à votre demande.",
        )
        await self._release(job_id)

    async def get_for_user(
        self, job_id: str, *, user_id: UUID
    ) -> dict[str, Any]:
        client = self._require()
        row = await asyncio.to_thread(client.hgetall, self._key(job_id))
        if not row or row.get("user_id") != str(user_id):
            raise NotFoundError("Cette comparaison est introuvable.")
        result = None
        if row.get("result"):
            try:
                result = json.loads(row["result"])
            except (TypeError, ValueError):
                pass
        return {
            **row,
            "progress": int(row.get("progress") or 0),
            "result": result,
            "error": row.get("error") or None,
        }

    async def _update(self, job_id: str, **fields: str) -> None:
        client = self._require()
        await asyncio.to_thread(
            client.hset,
            self._key(job_id),
            mapping={**fields, "updated_at": _now()},
        )
        await asyncio.to_thread(client.expire, self._key(job_id), self._ttl)

    async def _release(self, job_id: str) -> None:
        client = self._require()
        row = await asyncio.to_thread(client.hgetall, self._key(job_id))
        if not all(
            row.get(key)
            for key in (
                "user_id",
                "base_document_id",
                "target_document_id",
            )
        ):
            return
        active_key = self._active_key(
            UUID(row["user_id"]),
            UUID(row["base_document_id"]),
            UUID(row["target_document_id"]),
        )
        if await asyncio.to_thread(client.get, active_key) == job_id:
            await asyncio.to_thread(client.delete, active_key)


@lru_cache
def get_comparison_job_store() -> ComparisonJobStore:
    return ComparisonJobStore()


__all__ = ["ComparisonJobStore", "get_comparison_job_store"]
