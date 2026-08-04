"""Multi-agent orchestration API endpoints."""

import asyncio
import json
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.agents.legal import LegalAgent
from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError
from app.core.logging import get_logger
from app.db.session import get_db
from app.graphs.multi_agent_graph import build_multi_agent_graph
from app.models.user import User
from app.schemas.agents import (
    AgentAnswer,
    AgentQueryRequest,
    AgentQueryResponse,
    AgentSynthesisResult,
    LegalAnalysisJobCreateResponse,
    LegalAnalysisJobRequest,
    LegalAnalysisJobStatusResponse,
    LegalAnalysisResponse,
    LegalAnalyzeRequest,
    SynthesisJobCreateResponse,
    SynthesisJobRequest,
    SynthesisJobStatusResponse,
)
from app.services.agent_stream import AgentStreamService
from app.services.analysis_job import (
    get_analysis_job_store,
    get_synthesis_job_store,
)
from app.services.contract_analysis import ContractAnalysisService
from app.services.contract_synthesis import ContractSynthesisService
from app.services.conversation import ConversationService
from app.services.generator import GeneratorService
from app.services.langfuse_service import get_langfuse_service
from app.state.graph_state import GraphState
from app.repositories.document import DocumentRepository
from app.tasks.analysis import process_analysis_job_task
from app.tasks.synthesis import process_synthesis_job_task

logger = get_logger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


def get_generator_service(db: AsyncSession = Depends(get_db)) -> GeneratorService:
    return GeneratorService(db)


def get_conversation_service(
    db: AsyncSession = Depends(get_db),
) -> ConversationService:
    return ConversationService(db)


def get_legal_agent(
    generator: GeneratorService = Depends(get_generator_service),
) -> LegalAgent:
    return LegalAgent(generator)


def _to_answer(result: dict[str, Any] | None) -> AgentAnswer | None:
    """Adapt a graph agent-result dict to the API schema (``None`` if absent)."""
    if not result:
        return None
    return AgentAnswer.model_validate(result)


@router.post(
    "/query",
    response_model=AgentQueryResponse,
    summary="Route a question through the multi-agent LangGraph",
    description=(
        "Runs the multi-agent StateGraph. A leading '/legal', '/finance' or "
        "'/compliance' command runs only that agent; otherwise the legal, "
        "finance and compliance agents run and a synthesis agent produces a "
        "final recommendation from their three analyses."
    ),
)
async def agents_query(
    body: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentQueryResponse:
    settings = get_settings()
    langfuse = get_langfuse_service()

    # Parent trace grouping every node of this run into one readable tree.
    trace = langfuse.start_trace("multi_agent", input={"question": body.question})
    graph = build_multi_agent_graph(
        session=db, settings=settings, langfuse=langfuse, trace=trace
    )
    initial: GraphState = {
        "user_query": body.question,
        "metadata": {
            "user_id": str(current_user.id),
            "top_k": body.top_k,
            "final_k": body.final_k,
            "temperature": body.temperature,
            "max_tokens": body.max_tokens,
            "document_id": body.document_id,
        },
        "errors": [],
    }
    try:
        final: GraphState = await graph.ainvoke(initial)
    except Exception as exc:
        langfuse.end_trace(trace, error=exc)
        raise
    langfuse.end_trace(trace, output={"target_agent": final.get("target_agent")})

    target = final.get("target_agent")
    if target:
        result = final.get(f"{target}_result")
        return AgentQueryResponse(
            question=body.question,
            mode="single",
            agent=(result or {}).get("agent"),
            response=_to_answer(result),
        )

    return AgentQueryResponse(
        question=body.question,
        mode="multi",
        recommendation=final.get("final_recommendation"),
        legal=_to_answer(final.get("legal_result")),
        finance=_to_answer(final.get("finance_result")),
        compliance=_to_answer(final.get("compliance_result")),
    )


@router.post(
    "/stream",
    summary="Stream an agent answer (fragmented) over Server-Sent Events",
    description=(
        "Streaming counterpart of POST /agents/query. A leading '/legal', "
        "'/finance' or '/compliance' command streams that single agent's grounded "
        "answer token-by-token. Without a command, the three agents run and the "
        "synthesis recommendation is streamed after their analyses. "
        "Events: 'agent' (once), 'status'/'analyses' (multi mode), 'sources', "
        "'delta' (many), 'done' (once), 'error'."
    ),
)
async def agents_stream(
    body: AgentQueryRequest,
    generator: GeneratorService = Depends(get_generator_service),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    service = AgentStreamService(generator)

    async def event_source():
        try:
            async for event in service.stream(
                body.question,
                user_id=current_user.id,
                document_id=body.document_id,
                top_k=body.top_k,
                final_k=body.final_k,
                temperature=body.temperature,
                max_tokens=body.max_tokens,
            ):
                yield f"data: {json.dumps(event, default=str)}\n\n"
        except AppError as exc:
            logger.warning("Agent stream failed: %s", getattr(exc, "detail", exc.message))
            payload = {
                "type": "error",
                "message": exc.message,
                "code": exc.code,
                "retryable": exc.retryable,
            }
            yield f"data: {json.dumps(payload)}\n\n"
        except Exception:  # never leak internals to the client
            logger.exception("Agent stream failed")
            payload = {
                "type": "error",
                "message": (
                    "Une erreur inattendue est survenue pendant l'interrogation "
                    "des agents. Veuillez réessayer."
                ),
                "code": "internal_error",
                "retryable": True,
            }
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/legal/analyze/jobs",
    response_model=LegalAnalysisJobCreateResponse,
    status_code=202,
    summary="Start a durable background contract analysis",
)
async def create_legal_analysis_job(
    body: LegalAnalysisJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegalAnalysisJobCreateResponse:
    document = await DocumentRepository(db).get_by_id(
        body.document_id,
        user_id=current_user.id,
    )
    if document is None:
        raise NotFoundError("Ce contrat est introuvable.")

    proposed_job_id = uuid4()
    store = get_analysis_job_store()
    job_id, created = await store.create_or_get_active(
        str(proposed_job_id),
        user_id=current_user.id,
        document_id=body.document_id,
        title=f"Analyse — {document.original_filename}",
    )
    if not created:
        logger.info(
            "Reusing active analysis job job_id=%s document_id=%s user_id=%s",
            job_id,
            body.document_id,
            current_user.id,
        )
        return LegalAnalysisJobCreateResponse(
            job_id=UUID(job_id),
            document_id=body.document_id,
            status="queued",
        )

    try:
        task = await asyncio.to_thread(
            process_analysis_job_task.delay,
            str(job_id),
            str(current_user.id),
            body.model_dump(mode="json"),
        )
        await store.set_task_id(str(job_id), task.id)
    except Exception as exc:
        logger.exception("Could not queue analysis job job_id=%s", job_id)
        await store.mark_failed(
            str(job_id),
            "L’analyse n’a pas pu être démarrée. Veuillez réessayer.",
        )
        raise AppError(
            "L’analyse n’a pas pu être démarrée. Veuillez réessayer.",
            status_code=503,
            code="analysis_job_enqueue_failed",
            retryable=True,
        ) from exc
    return LegalAnalysisJobCreateResponse(
        job_id=UUID(job_id),
        document_id=body.document_id,
        status="queued",
    )


@router.get(
    "/legal/analyze/jobs/{job_id}",
    response_model=LegalAnalysisJobStatusResponse,
    summary="Resume a durable contract analysis",
)
async def get_legal_analysis_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
) -> LegalAnalysisJobStatusResponse:
    payload = await get_analysis_job_store().get_for_user(
        str(job_id),
        user_id=current_user.id,
    )
    return LegalAnalysisJobStatusResponse(
        job_id=job_id,
        document_id=UUID(payload["document_id"]),
        status=payload["status"],
        progress=payload["progress"],
        message=payload["message"],
        result=payload["result"],
        error=payload["error"],
    )


@router.get(
    "/synthesis/{document_id}",
    response_model=AgentSynthesisResult,
    summary="Return a cached multi-agent synthesis (never computes)",
    description=(
        "Returns the stored multi-agent synthesis (legal + finance + compliance "
        "→ synthesis recommendation) for a contract, or 404 if none has been "
        "generated yet. Computation is only triggered by the durable job "
        "endpoint below."
    ),
)
async def get_cached_synthesis(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentSynthesisResult:
    cached = await ContractSynthesisService(db).get_cached(
        document_id, user_id=current_user.id
    )
    if cached is None:
        raise NotFoundError("Aucune synthèse enregistrée pour ce contrat.")
    return AgentSynthesisResult.model_validate(cached)


@router.post(
    "/synthesis/jobs",
    response_model=SynthesisJobCreateResponse,
    status_code=202,
    summary="Start a durable, reconnectable multi-agent synthesis",
)
async def create_synthesis_job(
    body: SynthesisJobRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SynthesisJobCreateResponse:
    document = await DocumentRepository(db).get_by_id(
        body.document_id,
        user_id=current_user.id,
    )
    if document is None:
        raise NotFoundError("Ce contrat est introuvable.")

    proposed_job_id = uuid4()
    store = get_synthesis_job_store()
    job_id, created = await store.create_or_get_active(
        str(proposed_job_id),
        user_id=current_user.id,
        document_id=body.document_id,
        title=f"Synthèse — {document.original_filename}",
    )
    if not created:
        logger.info(
            "Reusing active synthesis job job_id=%s document_id=%s user_id=%s",
            job_id,
            body.document_id,
            current_user.id,
        )
        return SynthesisJobCreateResponse(
            job_id=UUID(job_id),
            document_id=body.document_id,
            status="queued",
        )

    try:
        task = await asyncio.to_thread(
            process_synthesis_job_task.delay,
            str(job_id),
            str(current_user.id),
            body.model_dump(mode="json"),
        )
        await store.set_task_id(str(job_id), task.id)
    except Exception as exc:
        logger.exception("Could not queue synthesis job job_id=%s", job_id)
        await store.mark_failed(
            str(job_id),
            "La synthèse n’a pas pu être démarrée. Veuillez réessayer.",
        )
        raise AppError(
            "La synthèse n’a pas pu être démarrée. Veuillez réessayer.",
            status_code=503,
            code="synthesis_job_enqueue_failed",
            retryable=True,
        ) from exc
    return SynthesisJobCreateResponse(
        job_id=UUID(job_id),
        document_id=body.document_id,
        status="queued",
    )


@router.get(
    "/synthesis/jobs/{job_id}",
    response_model=SynthesisJobStatusResponse,
    summary="Resume a durable multi-agent synthesis",
)
async def get_synthesis_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
) -> SynthesisJobStatusResponse:
    payload = await get_synthesis_job_store().get_for_user(
        str(job_id),
        user_id=current_user.id,
    )
    return SynthesisJobStatusResponse(
        job_id=job_id,
        document_id=UUID(payload["document_id"]),
        status=payload["status"],
        progress=payload["progress"],
        message=payload["message"],
        result=payload["result"],
        error=payload["error"],
    )


@router.post(
    "/legal/analyze",
    response_model=LegalAnalysisResponse,
    summary="Analyze a contract with the LegalAgent",
    description=(
        "Runs the specialized LegalAgent over the shared RAG pipeline: explains "
        "clauses, identifies obligations/rights, flags missing or ambiguous "
        "clauses, and returns a structured legal risk assessment. For a scoped "
        "document, an existing analysis is returned unless force_refresh is true."
    ),
)
async def legal_analyze(
    body: LegalAnalyzeRequest,
    legal_agent: LegalAgent = Depends(get_legal_agent),
    conversations: ConversationService = Depends(get_conversation_service),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LegalAnalysisResponse:
    history = None
    if body.conversation_id is not None:
        messages = await conversations.load_history(
            body.conversation_id, user_id=current_user.id
        )
        history = ConversationService.messages_to_prompt_turns(messages)

    service = ContractAnalysisService(db, legal_agent)
    payload = await service.get_or_analyze(
        body.question,
        user_id=current_user.id,
        document_id=body.document_id,
        force_refresh=body.force_refresh,
        top_k=body.top_k,
        final_k=body.final_k,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        history=history,
    )
    return LegalAnalysisResponse.model_validate(payload)
