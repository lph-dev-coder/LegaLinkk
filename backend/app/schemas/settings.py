"""API contracts for account settings (agent system prompts)."""

from pydantic import BaseModel, Field


class AgentPromptField(BaseModel):
    label: str
    value: str
    default: str
    customized: bool
    uses_no_answer: bool = False


class AgentPromptsResponse(BaseModel):
    legal: AgentPromptField
    finance: AgentPromptField
    compliance: AgentPromptField
    synthesis: AgentPromptField


class AgentPromptsUpdate(BaseModel):
    legal: str | None = Field(default=None, max_length=20000)
    finance: str | None = Field(default=None, max_length=20000)
    compliance: str | None = Field(default=None, max_length=20000)
    synthesis: str | None = Field(default=None, max_length=20000)


__all__ = [
    "AgentPromptField",
    "AgentPromptsResponse",
    "AgentPromptsUpdate",
]
