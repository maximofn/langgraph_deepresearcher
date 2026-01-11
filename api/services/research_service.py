"""
Research service for executing research workflows.
Adapted from front/deep_researcher_wrapper.py for API usage.
"""

import sys
import os
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage

from api.database.checkpointer import get_checkpointer_manager
from api.websockets.message_interceptor import enable_interception, disable_interception
from api.services.event_service import get_event_service
from api.models.events import EventType


class ResearchService:
    """
    Service for executing research workflows.
    Wraps the LangGraph write_agent and manages event emission.
    """

    def __init__(self):
        self.checkpointer_manager = get_checkpointer_manager()
        self.event_service = get_event_service()
        self._writer_builder = None

    def _get_writer_builder(self):
        """Lazy load writer_builder to avoid import issues"""
        if self._writer_builder is None:
            # Add src to path if not already
            src_path = os.path.join(os.getcwd(), "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from write.write_agent import writer_builder

            self._writer_builder = writer_builder

        return self._writer_builder

    async def start_research(
        self, session_id: str, thread_id: str, user_message: str
    ) -> Dict[str, Any]:
        """
        Start a new research session.

        Args:
            session_id: Unique session identifier
            thread_id: LangGraph thread ID for state persistence
            user_message: User's research query

        Returns:
            dict with keys:
                - needs_clarification: bool
                - clarification_question: str or None
                - research_brief: str or None
                - final_report: str or None
        """
        # Enable message interception for this session
        enable_interception(session_id)

        try:
            # Emit session start event
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.SESSION_STARTED,
                title="Research Session Started",
                content=f"Starting research for: {user_message}",
                is_intermediate=True,
            )

            # Get checkpointer
            checkpointer = self.checkpointer_manager.get_checkpointer()

            # Compile agent with checkpointer
            writer_builder = self._get_writer_builder()
            agent = writer_builder.compile(checkpointer=checkpointer)

            # Create thread config
            config = {"configurable": {"thread_id": thread_id}}

            # Invoke agent
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_message)]}, config=config
            )

            # Check if clarification is needed
            if result.get("research_brief") is None:
                messages = result.get("messages", [])
                if messages:
                    clarification_msg = messages[-1]
                    clarification_text = (
                        clarification_msg.content
                        if hasattr(clarification_msg, "content")
                        else str(clarification_msg)
                    )

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

            # Research completed
            final_report = result.get("final_report", "")

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
                "research_brief": result.get("research_brief"),
                "final_report": final_report,
            }

        except Exception as e:
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.ERROR,
                title="Research Error",
                content=str(e),
                is_intermediate=False,
            )
            raise

        finally:
            disable_interception()

    async def continue_with_clarification(
        self, session_id: str, thread_id: str, clarification: str
    ) -> Dict[str, Any]:
        """
        Continue research after user provides clarification.

        Args:
            session_id: Unique session identifier
            thread_id: LangGraph thread ID for state persistence
            clarification: User's clarification response

        Returns:
            dict with keys:
                - needs_clarification: bool
                - research_brief: str or None
                - final_report: str or None
        """
        enable_interception(session_id)

        try:
            checkpointer = self.checkpointer_manager.get_checkpointer()

            writer_builder = self._get_writer_builder()
            agent = writer_builder.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": thread_id}}

            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=clarification)]}, config=config
            )

            final_report = result.get("final_report", "")

            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.FINAL_REPORT,
                title="Research Complete",
                content=final_report,
                is_intermediate=False,
            )

            return {
                "needs_clarification": False,
                "research_brief": result.get("research_brief"),
                "final_report": final_report,
            }

        except Exception as e:
            await self.event_service.emit(
                session_id=session_id,
                event_type=EventType.ERROR,
                title="Research Error",
                content=str(e),
                is_intermediate=False,
            )
            raise

        finally:
            disable_interception()
