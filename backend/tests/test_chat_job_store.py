"""Tests for owner-scoped replay of Redis-backed chat events."""

from __future__ import annotations

import json
from uuid import uuid4

import pytest

from app.core.exceptions import NotFoundError
from app.services.chat_job import ChatJobStore


class FakeRedis:
    def __init__(self, meta: dict[str, str], events: list[dict]) -> None:
        self.meta = meta
        self.events = [json.dumps(event) for event in events]

    def hgetall(self, _key: str) -> dict[str, str]:
        return self.meta

    def lrange(self, _key: str, start: int, _end: int) -> list[str]:
        return self.events[start:]

    def hget(self, _key: str, field: str) -> str | None:
        return self.meta.get(field)

    def llen(self, _key: str) -> int:
        return len(self.events)

    def pipeline(self) -> "FakeRedis":
        self._results: list[object] = []
        return self

    def rpush(self, _key: str, value: str) -> int:
        self.events.append(value)
        self._results.append(len(self.events))
        return len(self.events)

    def hset(self, _key: str, mapping: dict[str, str]) -> None:
        self.meta.update(mapping)
        self._results.append(None)

    def expire(self, _key: str, _ttl: int) -> None:
        self._results.append(None)

    def execute(self) -> list[object]:
        return self._results


@pytest.mark.asyncio
async def test_replays_events_from_requested_offset_for_owner() -> None:
    owner_id = uuid4()
    client = FakeRedis(
        {"user_id": str(owner_id), "status": "completed", "mode": "chat"},
        [
            {"type": "delta", "text": "A"},
            {"type": "delta", "text": "B"},
            {"type": "done", "answer": "AB"},
        ],
    )
    store = ChatJobStore(client)

    meta = await store.get_meta_for_user("job-1", user_id=owner_id)
    events, cursor = await store.get_events("job-1", after=1)

    assert meta["status"] == "completed"
    assert events == [
        {"type": "delta", "text": "B"},
        {"type": "done", "answer": "AB"},
    ]
    assert cursor == 3


@pytest.mark.asyncio
async def test_foreign_user_cannot_read_chat_job() -> None:
    client = FakeRedis(
        {"user_id": str(uuid4()), "status": "processing", "mode": "agent"},
        [],
    )
    store = ChatJobStore(client)

    with pytest.raises(NotFoundError):
        await store.get_meta_for_user("job-1", user_id=uuid4())


@pytest.mark.asyncio
async def test_cancelled_job_rejects_late_completion() -> None:
    client = FakeRedis(
        {"user_id": str(uuid4()), "status": "processing", "mode": "chat"},
        [{"type": "delta", "text": "Réponse partielle"}],
    )
    store = ChatJobStore(client)

    await store.mark_cancelled("job-1")
    await store.append_event("job-1", {"type": "done", "answer": "Trop tard"})

    assert client.meta["status"] == "cancelled"
    assert len(client.events) == 2
    assert json.loads(client.events[-1])["type"] == "cancelled"
