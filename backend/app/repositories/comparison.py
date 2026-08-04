"""Data access for persisted contract comparisons."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comparison import ContractComparison


class ContractComparisonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_pair(
        self,
        base_document_id: UUID,
        target_document_id: UUID,
    ) -> ContractComparison | None:
        result = await self._session.execute(
            select(ContractComparison).where(
                ContractComparison.base_document_id == base_document_id,
                ContractComparison.target_document_id == target_document_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, comparison: ContractComparison) -> ContractComparison:
        self._session.add(comparison)
        await self._session.flush()
        return comparison


__all__ = ["ContractComparisonRepository"]
