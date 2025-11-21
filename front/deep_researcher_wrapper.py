"""
Deep Researcher Wrapper for Gradio UI

This module provides a wrapper around the Deep Researcher system that
captures all outputs and emits events for display in the Gradio interface.
"""

import sys
from typing import AsyncGenerator

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

sys.path.append('src')

from write.write_agent import writer_builder
from front.event_tracker import get_tracker, EventType, reset_tracker
from front.message_interceptor import enable_interception, disable_interception


class DeepResearcherWrapper:
    """
    Wrapper around the Deep Researcher system that captures outputs
    and emits events for the Gradio UI
    """

    def __init__(self):
        self.tracker = get_tracker()
        self.checkpointer = InMemorySaver()
        self.agent = writer_builder.compile(checkpointer=self.checkpointer)

        # Enable message interception
        enable_interception()

    async def run_research(self, user_message: str) -> AsyncGenerator[dict, None]:
        """
        Run the deep researcher and yield events as they occur

        Args:
            user_message: The user's research question

        Yields:
            dict: Event data containing type, title, content, and styling info
        """
        # Reset tracker for new research session
        reset_tracker()

        # Track which events we've already yielded
        yielded_count = 0

        try:
            # Create thread
            thread = {"configurable": {"thread_id": "1"}}

            # Yield initial user message
            yield {
                "type": "user_message",
                "content": user_message,
                "is_intermediate": False
            }

            # Start research in the background
            import asyncio

            # Create a task to run the research
            research_task = asyncio.create_task(
                self.agent.ainvoke(
                    {"messages": [HumanMessage(content=f"{user_message}.")]},
                    config=thread
                )
            )

            # Poll for events while research is running
            while not research_task.done():
                # Get new events
                all_events = self.tracker.get_events()
                new_events = all_events[yielded_count:]

                # Yield new events
                for event in new_events:
                    yield self._event_to_dict(event)
                    yielded_count += 1

                # Small delay to avoid busy waiting
                await asyncio.sleep(0.1)

            # Get the result
            result = await research_task

            # Yield any remaining events
            all_events = self.tracker.get_events()
            new_events = all_events[yielded_count:]
            for event in new_events:
                yield self._event_to_dict(event)
                yielded_count += 1

            # Check if clarification was needed
            if result.get("research_brief", None) is None:
                # Clarification needed
                messages = result.get("messages", [])
                if messages:
                    clarification_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
                    yield {
                        "type": "clarification",
                        "content": clarification_message,
                        "is_intermediate": False
                    }
                    return

            # Yield the final report
            final_report = result.get("final_report", "")
            if final_report:
                yield {
                    "type": "final_report",
                    "content": final_report,
                    "is_intermediate": False
                }

        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error durante la investigación: {str(e)}",
                "is_intermediate": False
            }

    async def continue_with_clarification(self, clarification: str) -> AsyncGenerator[dict, None]:
        """
        Continue research after user provides clarification

        Args:
            clarification: User's clarification message

        Yields:
            dict: Event data containing type, title, content, and styling info
        """
        # Reset tracker
        reset_tracker()

        # Track which events we've already yielded
        yielded_count = 0

        try:
            thread = {"configurable": {"thread_id": "1"}}

            # Yield user clarification
            yield {
                "type": "user_message",
                "content": clarification,
                "is_intermediate": False
            }

            # Start research in the background
            import asyncio

            # Create a task to run the research
            research_task = asyncio.create_task(
                self.agent.ainvoke(
                    {"messages": [HumanMessage(content=clarification)]},
                    config=thread
                )
            )

            # Poll for events while research is running
            while not research_task.done():
                # Get new events
                all_events = self.tracker.get_events()
                new_events = all_events[yielded_count:]

                # Yield new events
                for event in new_events:
                    yield self._event_to_dict(event)
                    yielded_count += 1

                # Small delay to avoid busy waiting
                await asyncio.sleep(0.1)

            # Get the result
            result = await research_task

            # Yield any remaining events
            all_events = self.tracker.get_events()
            new_events = all_events[yielded_count:]
            for event in new_events:
                yield self._event_to_dict(event)
                yielded_count += 1

            # Yield the final report
            final_report = result.get("final_report", "")
            if final_report:
                yield {
                    "type": "final_report",
                    "content": final_report,
                    "is_intermediate": False
                }

        except Exception as e:
            yield {
                "type": "error",
                "content": f"Error durante la investigación: {str(e)}",
                "is_intermediate": False
            }

    def _event_to_dict(self, event) -> dict:
        """Convert an Event object to a dictionary for Gradio"""
        return {
            "type": event.event_type.value,
            "title": event.title,
            "content": event.content,
            "is_intermediate": event.is_intermediate,
            "metadata": event.metadata or {}
        }
