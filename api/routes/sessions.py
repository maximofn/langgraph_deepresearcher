"""
REST API endpoints for session management.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from api.database.db import get_db
from api.database.models import SessionStatus
from api.services.session_service import SessionService
from api.services.research_service import ResearchService
from api.models.requests import CreateSessionRequest, ContinueSessionRequest
from api.models.responses import (
    SessionResponse,
    CreateSessionResponse,
    MessageResponse,
    SessionListResponse,
    StartResearchResponse,
)


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=CreateSessionResponse)
async def create_session(
    request: CreateSessionRequest, db: AsyncSession = Depends(get_db)
):
    """
    Create a new research session.

    Args:
        request: Session creation request with query and configuration
        db: Database session

    Returns:
        Session details and WebSocket URL
    """
    session_service = SessionService(db)
    session = await session_service.create_session(
        initial_query=request.query,
        max_iterations=request.max_iterations,
        max_concurrent_researchers=request.max_concurrent_researchers,
    )

    return CreateSessionResponse(
        session=SessionResponse.model_validate(session),
        websocket_url=f"/ws/{session.id}",
    )


@router.post("/{session_id}/start", response_model=StartResearchResponse)
async def start_research(
    session_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    """
    Start research for a session (runs in background).

    Args:
        session_id: Session identifier
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Status confirmation
    """
    session_service = SessionService(db)
    session = await session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.CREATED:
        raise HTTPException(
            status_code=400,
            detail=f"Session already started or completed (status: {session.status.value})",
        )

    # Update status to ACTIVE
    await session_service.update_session_status(session_id, SessionStatus.ACTIVE)

    # Start research in background
    async def run_research():
        research_service = ResearchService()
        # Create a new DB session for background task
        async for db_session in get_db():
            try:
                session_service_bg = SessionService(db_session)

                result = await research_service.start_research(
                    session_id=session.id,
                    thread_id=session.thread_id,
                    user_message=session.initial_query,
                )

                # Update session with results
                if result["needs_clarification"]:
                    await session_service_bg.update_session_status(
                        session_id, SessionStatus.CLARIFICATION_NEEDED
                    )
                else:
                    await session_service_bg.update_session_status(
                        session_id,
                        SessionStatus.COMPLETED,
                        research_brief=result["research_brief"],
                        final_report=result["final_report"],
                    )

            except Exception as e:
                await session_service_bg.update_session_status(
                    session_id, SessionStatus.FAILED
                )
                print(f"[API] Research failed for session {session_id}: {e}")
                import traceback
                traceback.print_exc()

            finally:
                break  # Exit the async generator

    background_tasks.add_task(run_research)

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
    """
    Provide clarification and continue research.

    Args:
        session_id: Session identifier
        request: Clarification request
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Status confirmation
    """
    session_service = SessionService(db)
    session = await session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.CLARIFICATION_NEEDED:
        raise HTTPException(
            status_code=400, detail="Session does not need clarification"
        )

    # Update clarification response and status
    await session_service.update_session_status(
        session_id,
        SessionStatus.ACTIVE,
        clarification_response=request.clarification,
    )

    # Continue research in background
    async def continue_research():
        research_service = ResearchService()
        # Create a new DB session for background task
        async for db_session in get_db():
            try:
                session_service_bg = SessionService(db_session)

                result = await research_service.continue_with_clarification(
                    session_id=session.id,
                    thread_id=session.thread_id,
                    clarification=request.clarification,
                )

                await session_service_bg.update_session_status(
                    session_id,
                    SessionStatus.COMPLETED,
                    research_brief=result["research_brief"],
                    final_report=result["final_report"],
                )

            except Exception as e:
                await session_service_bg.update_session_status(
                    session_id, SessionStatus.FAILED
                )
                print(f"[API] Research failed for session {session_id}: {e}")
                import traceback
                traceback.print_exc()

            finally:
                break  # Exit the async generator

    background_tasks.add_task(continue_research)

    return StartResearchResponse(
        status="continued",
        session_id=session_id,
        message="Research continued. Connect to WebSocket for real-time updates.",
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get session details.

    Args:
        session_id: Session identifier
        db: Database session

    Returns:
        Session details
    """
    session_service = SessionService(db)
    session = await session_service.get_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse.model_validate(session)


@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get all messages for a session.

    Args:
        session_id: Session identifier
        db: Database session

    Returns:
        List of messages
    """
    session_service = SessionService(db)

    # Verify session exists
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = await session_service.get_session_messages(session_id)

    return [MessageResponse.model_validate(msg) for msg in messages]


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """
    List all sessions with pagination.

    Args:
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        db: Database session

    Returns:
        List of sessions
    """
    session_service = SessionService(db)
    sessions = await session_service.list_sessions(limit=limit, offset=offset)

    return SessionListResponse(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=len(sessions),
        limit=limit,
        offset=offset,
    )
