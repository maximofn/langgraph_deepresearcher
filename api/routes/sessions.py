"""REST endpoints for session management."""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.db import db_session_context, get_db
from api.database.models import SessionStatus
from api.models.requests import ContinueSessionRequest, CreateSessionRequest
from api.models.responses import (
    CreateSessionResponse,
    MessageResponse,
    SessionListResponse,
    SessionResponse,
    StartResearchResponse,
)
from api.services.research_service import ResearchService
from api.services.session_service import SessionService
from api.utils.exceptions import InvalidSessionStateError, SessionNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


async def _run_research_bg(session_id: str) -> None:
    """Background task: execute a fresh research run and persist its outcome."""
    research_service = ResearchService()
    async with db_session_context() as db_session:
        svc = SessionService(db_session)
        session = await svc.get_session(session_id)
        if session is None:
            logger.error("Background task: session %s vanished", session_id)
            return

        api_keys = ResearchService.pop_api_keys(session_id)

        try:
            result = await research_service.start_research(
                session_id=session.id,
                thread_id=session.thread_id,
                user_message=session.initial_query,
                db=db_session,
                models_config=session.models_config,
                api_keys=api_keys,
            )

            if result["needs_clarification"]:
                await svc.update_session_status(session_id, SessionStatus.CLARIFICATION_NEEDED)
            else:
                await svc.update_session_status(
                    session_id,
                    SessionStatus.COMPLETED,
                    research_brief=result["research_brief"],
                    final_report=result["final_report"],
                )
        except Exception:
            logger.exception("Research failed for session %s", session_id)
            await svc.update_session_status(session_id, SessionStatus.FAILED)


async def _continue_research_bg(
    session_id: str,
    clarification: str,
    api_keys: Optional[dict] = None,
) -> None:
    """Background task: resume a paused research run with the user's clarification."""
    research_service = ResearchService()
    async with db_session_context() as db_session:
        svc = SessionService(db_session)
        session = await svc.get_session(session_id)
        if session is None:
            logger.error("Background task: session %s vanished", session_id)
            return

        try:
            result = await research_service.continue_with_clarification(
                session_id=session.id,
                thread_id=session.thread_id,
                clarification=clarification,
                db=db_session,
                models_config=session.models_config,
                api_keys=api_keys,
            )
            await svc.update_session_status(
                session_id,
                SessionStatus.COMPLETED,
                research_brief=result["research_brief"],
                final_report=result["final_report"],
            )
        except Exception:
            logger.exception("Clarification run failed for session %s", session_id)
            await svc.update_session_status(session_id, SessionStatus.FAILED)


@router.post("/", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new research session."""
    svc = SessionService(db)
    session = await svc.create_session(
        initial_query=request.query,
        max_iterations=request.max_iterations,
        max_concurrent_researchers=request.max_concurrent_researchers,
        models_config=request.models,
        user_name=request.user_name,
        user_email=request.user_email,
    )

    # User-supplied API keys are parked in memory keyed by session id and
    # consumed by the background task when research starts. They are NEVER
    # persisted to the database or to logs.
    if request.api_keys:
        ResearchService.stash_api_keys(session.id, request.api_keys)

    return CreateSessionResponse(
        session=SessionResponse.model_validate(session),
        websocket_url=f"/ws/{session.id}",
    )


@router.post("/{session_id}/start", response_model=StartResearchResponse)
async def start_research(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Start research for a session (runs in background)."""
    svc = SessionService(db)
    session = await svc.get_session(session_id)

    if session is None:
        raise SessionNotFoundError(f"Session {session_id} not found")

    if session.status != SessionStatus.CREATED:
        raise InvalidSessionStateError(
            f"Session already started or completed (status: {session.status.value})"
        )

    await svc.update_session_status(session_id, SessionStatus.ACTIVE)
    background_tasks.add_task(_run_research_bg, session_id)

    return StartResearchResponse(
        status="started",
        session_id=session_id,
        message="Research started. Connect to WebSocket for real-time updates.",
    )


@router.post("/{session_id}/clarify", response_model=StartResearchResponse)
async def provide_clarification(
    session_id: str,
    request: ContinueSessionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Provide clarification and continue research."""
    svc = SessionService(db)
    session = await svc.get_session(session_id)

    if session is None:
        raise SessionNotFoundError(f"Session {session_id} not found")

    if session.status != SessionStatus.CLARIFICATION_NEEDED:
        raise InvalidSessionStateError("Session does not need clarification")

    await svc.update_session_status(
        session_id,
        SessionStatus.ACTIVE,
        clarification_response=request.clarification,
    )
    background_tasks.add_task(
        _continue_research_bg, session_id, request.clarification, request.api_keys
    )

    return StartResearchResponse(
        status="continued",
        session_id=session_id,
        message="Research continued. Connect to WebSocket for real-time updates.",
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session details."""
    svc = SessionService(db)
    session = await svc.get_session(session_id)
    if session is None:
        raise SessionNotFoundError(f"Session {session_id} not found")
    return SessionResponse.model_validate(session)


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages for a session."""
    svc = SessionService(db)
    session = await svc.get_session(session_id)
    if session is None:
        raise SessionNotFoundError(f"Session {session_id} not found")

    messages = await svc.get_session_messages(session_id)
    return [MessageResponse.model_validate(msg) for msg in messages]


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a session and cascade its messages + events."""
    svc = SessionService(db)
    removed = await svc.delete_session(session_id)
    if not removed:
        raise SessionNotFoundError(f"Session {session_id} not found")
    return Response(status_code=204)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """List all sessions with pagination."""
    svc = SessionService(db)
    sessions = await svc.list_sessions(limit=limit, offset=offset)
    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=len(sessions),
        limit=limit,
        offset=offset,
    )
