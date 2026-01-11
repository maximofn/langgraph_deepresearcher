"""
Message interceptor for capturing agent outputs.
Adapted from front/message_interceptor.py for WebSocket event emission.
"""

from typing import Optional
import sys
import os
import asyncio

from api.services.event_service import get_event_service
from api.models.events import EventType


# Global state
_original_format_messages: Optional[callable] = None
_interception_enabled = False
_current_session_id: Optional[str] = None


def enable_interception(session_id: str):
    """
    Enable message interception for a specific session.
    Must be called before agents are executed.
    """
    global _original_format_messages, _interception_enabled, _current_session_id

    if _interception_enabled and _current_session_id == session_id:
        # Already enabled for this session
        return

    try:
        # Add src to path if not already
        src_path = os.path.join(os.getcwd(), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        from utils import message_utils

        # Store original and current session
        if _original_format_messages is None:
            _original_format_messages = message_utils.format_messages

        _current_session_id = session_id

        # Replace with intercepting version
        message_utils.format_messages = _intercepting_format_messages

        _interception_enabled = True
        print(f"[INTERCEPTOR] Enabled for session {session_id}")

    except ImportError as e:
        print(f"[INTERCEPTOR] Failed to enable: {e}")


def disable_interception():
    """Disable interception and restore original function"""
    global _original_format_messages, _interception_enabled, _current_session_id

    if not _interception_enabled:
        return

    try:
        from utils import message_utils

        if _original_format_messages:
            message_utils.format_messages = _original_format_messages

        _interception_enabled = False
        _current_session_id = None
        print("[INTERCEPTOR] Disabled")

    except ImportError as e:
        print(f"[INTERCEPTOR] Failed to disable: {e}")


def _intercepting_format_messages(
    messages, title: str = "", border_style: str = "white", msg_subtype: str = ""
):
    """
    Intercepting version that emits events to WebSocket.
    This function replaces the original format_messages().
    """
    event_service = get_event_service()

    # Determine event type
    event_type, is_intermediate = _determine_event_type(title, msg_subtype)

    # Extract content
    content = _extract_message_content(messages)

    # Emit event if we have a session ID
    if event_type and _current_session_id:
        # Schedule async emit in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    event_service.emit(
                        session_id=_current_session_id,
                        event_type=event_type,
                        title=title or "System Message",
                        content=content,
                        is_intermediate=is_intermediate,
                    )
                )
            else:
                # If loop is not running, run it synchronously
                loop.run_until_complete(
                    event_service.emit(
                        session_id=_current_session_id,
                        event_type=event_type,
                        title=title or "System Message",
                        content=content,
                        is_intermediate=is_intermediate,
                    )
                )
        except Exception as e:
            print(f"[INTERCEPTOR] Error emitting event: {e}")

    # Call original to maintain console output
    if _original_format_messages:
        _original_format_messages(messages, title, border_style, msg_subtype)


def _determine_event_type(title: str, msg_subtype: str) -> tuple[Optional[EventType], bool]:
    """
    Determine event type from title and msg_subtype.
    Returns (EventType, is_intermediate)
    """
    title_lower = title.lower()

    # Skip real human messages to avoid duplication
    if msg_subtype == "RealHumanMessage":
        return (None, True)

    # Scope Agent events
    if "scope" in title_lower:
        if "clarification" in title_lower:
            return (EventType.SCOPE_CLARIFICATION, False)
        elif "research brief" in title_lower or "brief generated" in title_lower:
            return (EventType.SCOPE_BRIEF, False)
        else:
            return (EventType.SCOPE_START, True)

    # Supervisor Agent events
    if "supervisor" in title_lower:
        if "think" in title_lower or "planning" in title_lower:
            return (EventType.SUPERVISOR_THINKING, True)
        elif "delegation" in title_lower or "delegat" in title_lower:
            return (EventType.SUPERVISOR_DELEGATION, True)
        else:
            return (EventType.SUPERVISOR_START, True)

    # Research Agent events
    if "research" in title_lower:
        if "tool call" in title_lower or "search" in title_lower:
            return (EventType.RESEARCH_TOOL_CALL, True)
        elif "tool output" in title_lower or "result" in title_lower:
            return (EventType.RESEARCH_TOOL_OUTPUT, True)
        elif "complete" in title_lower or "compress" in title_lower:
            return (EventType.RESEARCH_COMPLETE, False)
        else:
            return (EventType.RESEARCH_START, True)

    # Compression
    if "compress" in title_lower or "synthesis" in title_lower:
        return (EventType.COMPRESSION, True)

    # Writer Agent events
    if "writer" in title_lower or "report" in title_lower:
        if "complete" in title_lower or "final" in title_lower:
            return (EventType.WRITER_COMPLETE, False)
        else:
            return (EventType.WRITER_START, True)

    # Final report
    if "final report" in title_lower:
        return (EventType.FINAL_REPORT, False)

    # User message
    if "human" in title_lower:
        return (EventType.USER_MESSAGE, False)

    # Default: treat as intermediate event
    return (None, True)


def _extract_message_content(messages) -> str:
    """
    Extract content from messages.
    Simplified version that handles common message formats.
    """
    if isinstance(messages, str):
        return messages

    if isinstance(messages, list):
        parts = []
        for msg in messages:
            if hasattr(msg, "content"):
                if isinstance(msg.content, str):
                    parts.append(msg.content)
                elif isinstance(msg.content, list):
                    # Handle complex content (Anthropic format)
                    for item in msg.content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                parts.append(item.get("text", ""))
                            elif item.get("type") == "tool_use":
                                parts.append(
                                    f"Tool Call: {item.get('name', 'unknown')}"
                                )
                else:
                    parts.append(str(msg.content))
            elif isinstance(msg, dict):
                parts.append(str(msg.get("content", msg)))
            else:
                parts.append(str(msg))
        return "\n".join(parts)

    return str(messages)
