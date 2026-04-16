"""
Research service for executing research workflows.

Wraps the LangGraph ``writer_builder`` multi-agent pipeline, emits events to
subscribed WebSocket clients, and persists key messages to the session's
message history.
"""

from __future__ import annotations

import logging
import time
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


_PENDING_API_KEY_TTL_SECONDS = 300


class ResearchService:
    """Executes research runs and records their outputs."""

    # Class-level dict so all ResearchService() instances share the same
    # in-memory stash. Keys are session_ids; values are (timestamp, api_keys).
    # Never written to disk. Never logged.
    _pending_api_keys: Dict[str, tuple] = {}

    def __init__(self) -> None:
        self.checkpointer_manager = get_checkpointer_manager()
        self.event_service = get_event_service()

    @classmethod
    def stash_api_keys(cls, session_id: str, api_keys: Dict[str, str]) -> None:
        """Park user-provided API keys in memory until the research bg task picks them up."""
        cls._cleanup_expired_api_keys()
        cls._pending_api_keys[session_id] = (time.monotonic(), dict(api_keys))

    @classmethod
    def pop_api_keys(cls, session_id: str) -> Optional[Dict[str, str]]:
        """Retrieve and remove parked API keys for ``session_id``."""
        entry = cls._pending_api_keys.pop(session_id, None)
        if entry is None:
            return None
        _, api_keys = entry
        return api_keys

    @classmethod
    def _cleanup_expired_api_keys(cls) -> None:
        """Drop parked keys older than the TTL — defense in depth."""
        now = time.monotonic()
        stale = [
            sid
            for sid, (ts, _) in cls._pending_api_keys.items()
            if now - ts > _PENDING_API_KEY_TTL_SECONDS
        ]
        for sid in stale:
            cls._pending_api_keys.pop(sid, None)

    async def start_research(
        self,
        session_id: str,
        thread_id: str,
        user_message: str,
        db: Optional[AsyncSession] = None,
        models_config: Optional[Dict[str, str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
        max_iterations: Optional[int] = None,
        max_concurrent_researchers: Optional[int] = None,
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
        configurable: Dict[str, Any] = {
            "thread_id": thread_id,
            "models": models_config or {},
            "api_keys": api_keys or {},
        }
        if max_iterations is not None:
            configurable["max_iterations"] = max_iterations
        if max_concurrent_researchers is not None:
            configurable["max_concurrent_researchers"] = max_concurrent_researchers
        config = {"configurable": configurable}

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
        models_config: Optional[Dict[str, str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Resume a paused research run after the user clarifies."""
        if db is not None:
            await SessionService(db).add_message(session_id, "user", clarification)

        # Same thread_id => LangGraph resumes from the checkpointed state and
        # merges the new HumanMessage into the existing message list.
        agent = _get_writer_builder().compile(checkpointer=self.checkpointer_manager.get_checkpointer())
        config = {
            "configurable": {
                "thread_id": thread_id,
                "models": models_config or {},
                "api_keys": api_keys or {},
            }
        }

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

    async def chat_with_research(
        self,
        session_id: str,
        thread_id: str,
        message: str,
        db: Optional[AsyncSession] = None,
        models_config: Optional[Dict[str, str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Envía una pregunta de seguimiento al writer tras completar la investigación."""
        if db is not None:
            await SessionService(db).add_message(session_id, "user", message)

        agent = _get_writer_builder().compile(checkpointer=self.checkpointer_manager.get_checkpointer())
        config = {
            "configurable": {
                "thread_id": thread_id,
                "models": models_config or {},
                "api_keys": api_keys or {},
            }
        }

        try:
            with set_session_context(session_id):
                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=message)]},
                    config=config,
                )
        except Exception as exc:
            logger.exception("Chat run failed for session %s", session_id)
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.ERROR,
                title="Chat Error",
                content=str(exc),
                is_intermediate=False,
            )
            raise

        messages = result.get("messages", [])
        response_text = ""
        if messages:
            last = messages[-1]
            response_text = last.content if hasattr(last, "content") else str(last)

        if db is not None and response_text:
            await SessionService(db).add_message(session_id, "assistant", response_text)

        await self.event_service.emit(
            session_id=session_id,
            event_type=EventType.CHAT_RESPONSE,
            title="Chat Response",
            content=response_text,
            is_intermediate=False,
        )

        return {"response": response_text}

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
