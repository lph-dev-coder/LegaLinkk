import json
from fnmatch import fnmatch
from uuid import uuid4

import pytest

from app.services.task_center import TaskCenterService


class FakeRedis:
    def __init__(self, values: dict[str, dict[str, str]]) -> None:
        self.values = values

    def scan_iter(self, match: str, count: int = 10):
        return (key for key in self.values if fnmatch(key, match))

    def hgetall(self, key: str) -> dict[str, str]:
        return self.values[key]

    def get(self, key: str) -> str | None:
        payload = self.values.get(key)
        return json.dumps(payload) if payload else None


@pytest.mark.asyncio
async def test_task_center_is_owner_scoped_and_normalizes_types() -> None:
    owner = uuid4()
    foreign_owner = uuid4()
    report_id = uuid4()
    analysis_id = uuid4()
    ingestion_id = uuid4()
    client = FakeRedis(
        {
            f"chat:job:{report_id}:meta": {
                "job_id": str(report_id),
                "user_id": str(owner),
                "mode": "report",
                "title": "Rapport du bail",
                "status": "processing",
                "created_at": "2026-07-28T10:00:00+00:00",
                "updated_at": "2026-07-28T10:01:00+00:00",
            },
            f"analysis:job:{analysis_id}": {
                "job_id": str(analysis_id),
                "user_id": str(owner),
                "document_id": str(uuid4()),
                "title": "Analyse du bail",
                "status": "completed",
                "progress": "100",
                "created_at": "2026-07-28T09:00:00+00:00",
                "updated_at": "2026-07-28T09:02:00+00:00",
            },
            f"chat:job:{uuid4()}:meta": {
                "job_id": str(uuid4()),
                "user_id": str(foreign_owner),
                "mode": "chat",
                "status": "queued",
            },
            f"ingestion:progress:{ingestion_id}": {
                "document_id": str(ingestion_id),
                "user_id": str(owner),
                "title": "Contrat.pdf",
                "status": "processing",
                "stage": "embedding",
                "progress": "80",
                "created_at": "2026-07-28T08:00:00+00:00",
                "updated_at": "2026-07-28T08:02:00+00:00",
            },
        }
    )

    tasks = await TaskCenterService(client).list_for_user(owner)

    assert [task["type"] for task in tasks] == [
        "report",
        "analysis",
        "ingestion",
    ]
    assert tasks[0]["destination"] == "/consultation"
    assert tasks[1]["destination"].startswith("/analysis/")
    assert tasks[1]["progress"] == 100
    assert tasks[2]["destination"] == "/documents"
    assert tasks[2]["progress"] == 80
