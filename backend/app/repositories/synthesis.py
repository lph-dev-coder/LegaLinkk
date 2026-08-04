"""Data-access layer for persisted multi-agent syntheses."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.synthesis import DocumentSynthesis


class DocumentSynthesisRepository:
    """Persistence operations for one synthesis per document."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_document_id(
        self, document_id: UUID
    ) -> DocumentSynthesis | None:
        result = await self._session.execute(
            select(DocumentSynthesis).where(
                DocumentSynthesis.document_id == document_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, synthesis: DocumentSynthesis) -> DocumentSynthesis:
        self._session.add(synthesis)
        await self._session.flush()
        return synthesis
