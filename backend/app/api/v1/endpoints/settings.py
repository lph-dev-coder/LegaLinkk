"""Account settings: editable specialist-agent system prompts."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import AgentPromptsResponse, AgentPromptsUpdate
from app.services.agent_prompt import AgentPromptService

router = APIRouter(prefix="/settings", tags=["Settings"])


def get_prompt_service(
    db: AsyncSession = Depends(get_db),
) -> AgentPromptService:
    return AgentPromptService(db)


@router.get("/prompts", response_model=AgentPromptsResponse)
async def get_agent_prompts(
    current_user: User = Depends(get_current_user),
    service: AgentPromptService = Depends(get_prompt_service),
) -> AgentPromptsResponse:
    bundle = await service.get_bundle(current_user.id)
    return AgentPromptsResponse.model_validate(bundle)


@router.put("/prompts", response_model=AgentPromptsResponse)
async def update_agent_prompts(
    body: AgentPromptsUpdate,
    current_user: User = Depends(get_current_user),
    service: AgentPromptService = Depends(get_prompt_service),
) -> AgentPromptsResponse:
    bundle = await service.update(
        current_user.id,
        legal=body.legal,
        finance=body.finance,
        compliance=body.compliance,
        synthesis=body.synthesis,
    )
    return AgentPromptsResponse.model_validate(bundle)


__all__ = ["router"]
