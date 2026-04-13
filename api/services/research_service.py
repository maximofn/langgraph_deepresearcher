"""
Research service for executing research workflows.

Wraps the LangGraph ``writer_builder`` multi-agent pipeline, emits events to
subscribed WebSocket clients, and persists key messages to the session's
message history.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.checkpointer import get_checkpointer_manager
from api.models.events import EventType
from api.services.event_service import get_event_service
from api.services.session_service import SessionService
from api.utils.paths import ensure_src_on_path
from api.websockets.message_interceptor import set_session_context

logger = logging.getLogger(__name__)


def _get_writer_builder():
    """Import ``writer_builder`` lazily.

    ``src/LLM_models/LLM_models.py`` resolves API keys at import time, so we
    defer the import until the env has been loaded by the application.
    """
    ensure_src_on_path()
    from write.write_agent import writer_builder  # type: ignore[import-not-found]

    return writer_builder


class ResearchService:
    """Executes research runs and records their outputs."""

    def __init__(self) -> None:
        self.checkpointer_manager = get_checkpointer_manager()
        self.event_service = get_event_service()

    async def start_research(
        self,
        session_id: str,
        thread_id: str,
        user_message: str,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """Start a new research session for ``user_message``."""
        if db is not None:
            await SessionService(db).add_message(session_id, "user", user_message)

        await self.event_service.emit(
            session_id=session_id,
            event_type=EventType.SESSION_STARTED,
            title="Research Session Started",
            content=f"Starting research for: {user_message}",
            is_intermediate=True,
        )

        agent = _get_writer_builder().compile(checkpointer=self.checkpointer_manager.get_checkpointer())
        config = {"configurable": {"thread_id": thread_id}}

        try:
            with set_session_context(session_id):
                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=user_message)]},
                    config=config,
                )
        except Exception as exc:
            logger.exception("Research execution failed for session %s", session_id)
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.ERROR,
                title="Research Error",
                content=str(exc),
                is_intermediate=False,
            )
            raise

        return await self._handle_result(session_id, result, db)

    async def continue_with_clarification(
        self,
        session_id: str,
        thread_id: str,
        clarification: str,
        db: Optional[AsyncSession] = None,
    ) -> Dict[str, Any]:
        """Resume a paused research run after the user clarifies."""
        if db is not None:
            await SessionService(db).add_message(session_id, "user", clarification)

        # Same thread_id => LangGraph resumes from the checkpointed state and
        # merges the new HumanMessage into the existing message list.
        agent = _get_writer_builder().compile(checkpointer=self.checkpointer_manager.get_checkpointer())
        config = {"configurable": {"thread_id": thread_id}}

        try:
            with set_session_context(session_id):
                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=clarification)]},
                    config=config,
                )
        except Exception as exc:
            logger.exception("Clarification run failed for session %s", session_id)
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.ERROR,
                title="Research Error",
                content=str(exc),
                is_intermediate=False,
            )
            raise

        return await self._handle_result(session_id, result, db)

    async def _handle_result(
        self,
        session_id: str,
        result: Dict[str, Any],
        db: Optional[AsyncSession],
    ) -> Dict[str, Any]:
        research_brief = result.get("research_brief")

        if research_brief is None:
            messages = result.get("messages", [])
            clarification_text = ""
            if messages:
                last = messages[-1]
                clarification_text = last.content if hasattr(last, "content") else str(last)

            if db is not None and clarification_text:
                await SessionService(db).add_message(session_id, "assistant", clarification_text)

            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.CLARIFICATION_NEEDED,
                title="Clarification Needed",
                content=clarification_text,
                is_intermediate=False,
            )

            return {
                "needs_clarification": True,
                "clarification_question": clarification_text,
                "research_brief": None,
                "final_report": None,
            }

        final_report = result.get("final_report", "") or ""

        if db is not None:
            svc = SessionService(db)
            await svc.add_message(session_id, "system", research_brief)
            if final_report:
                await svc.add_message(session_id, "assistant", final_report)

        await self.event_service.emit(
            session_id=session_id,
            event_type=EventType.FINAL_REPORT,
            title="Research Complete",
            content=final_report,
            is_intermediate=False,
        )

        return {
            "needs_clarification": False,
            "clarification_question": None,
            "research_brief": research_brief,
            "final_report": final_report,
        }
