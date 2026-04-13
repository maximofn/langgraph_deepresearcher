"""
Message interceptor for capturing agent outputs.

Installs a one-shot monkey-patch on ``src/utils/message_utils.format_messages``
at application startup. The patch is aware of the currently active session via
``contextvars`` so multiple concurrent research runs stay isolated.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Callable, Iterator, Optional, Tuple

from api.models.events import EventType
from api.services.event_service import get_event_service
from api.utils.paths import ensure_src_on_path

logger = logging.getLogger(__name__)

# Context-local current session — each asyncio task inherits its own copy, so
# two concurrent research runs never step on each other.
current_session_id: ContextVar[Optional[str]] = ContextVar(
    "current_session_id", default=None
)

_original_format_messages: Optional[Callable] = None
_installed: bool = False


def install_interceptor() -> None:
    """Patch ``message_utils.format_messages`` once, at startup."""
    global _original_format_messages, _installed

    if _installed:
        return

    ensure_src_on_path()
    try:
        from utils import message_utils  # type: ignore[import-not-found]
    except ImportError:
        logger.exception("Interceptor install failed: cannot import utils.message_utils")
        return

    _original_format_messages = message_utils.format_messages
    message_utils.format_messages = _intercepting_format_messages
    _installed = True
    logger.info("Message interceptor installed")


def uninstall_interceptor() -> None:
    """Restore the original function (useful for tests)."""
    global _installed

    if not _installed or _original_format_messages is None:
        return

    try:
        from utils import message_utils  # type: ignore[import-not-found]

        message_utils.format_messages = _original_format_messages
        _installed = False
        logger.info("Message interceptor uninstalled")
    except ImportError:
        logger.exception("Interceptor uninstall failed")


@contextmanager
def set_session_context(session_id: str) -> Iterator[None]:
    """Bind ``session_id`` to the current async task for the duration of the block."""
    token = current_session_id.set(session_id)
    try:
        yield
    finally:
        current_session_id.reset(token)


def _intercepting_format_messages(
    messages, title: str = "", border_style: str = "white", msg_subtype: str = ""
):
    """Replacement for ``format_messages`` that emits events then delegates."""
    session_id = current_session_id.get()

    if session_id is not None:
        event_type, is_intermediate = _determine_event_type(title, msg_subtype)
        if event_type is not None:
            content = _extract_message_content(messages)
            _schedule_emit(session_id, event_type, title or "System Message", content, is_intermediate)

    if _original_format_messages is not None:
        _original_format_messages(messages, title, border_style, msg_subtype)


def _schedule_emit(
    session_id: str,
    event_type: EventType,
    title: str,
    content: str,
    is_intermediate: bool,
) -> None:
    event_service = get_event_service()
    coro = event_service.emit(
        session_id=session_id,
        event_type=event_type,
        title=title,
        content=content,
        is_intermediate=is_intermediate,
    )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — we're being called from sync code outside an event loop.
        # Fire-and-forget via a fresh loop.
        try:
            asyncio.run(coro)
        except Exception:
            logger.exception("Failed to emit event synchronously")
        return

    loop.create_task(coro)


def _determine_event_type(title: str, msg_subtype: str) -> Tuple[Optional[EventType], bool]:
    """Map a format_messages title/subtype to an EventType + intermediate flag."""
    title_lower = title.lower()

    if msg_subtype == "RealHumanMessage":
        return (None, True)

    if "scope" in title_lower:
        if "clarification" in title_lower:
            return (EventType.SCOPE_CLARIFICATION, False)
        if "research brief" in title_lower or "brief generated" in title_lower:
            return (EventType.SCOPE_BRIEF, False)
        return (EventType.SCOPE_START, True)

    if "supervisor" in title_lower:
        if "think" in title_lower or "planning" in title_lower:
            return (EventType.SUPERVISOR_THINKING, True)
        if "delegat" in title_lower:
            return (EventType.SUPERVISOR_DELEGATION, True)
        return (EventType.SUPERVISOR_START, True)

    if "research" in title_lower:
        if "tool call" in title_lower or "search" in title_lower:
            return (EventType.RESEARCH_TOOL_CALL, True)
        if "tool output" in title_lower or "result" in title_lower:
            return (EventType.RESEARCH_TOOL_OUTPUT, True)
        if "complete" in title_lower or "compress" in title_lower:
            return (EventType.RESEARCH_COMPLETE, False)
        return (EventType.RESEARCH_START, True)

    if "compress" in title_lower or "synthesis" in title_lower:
        return (EventType.COMPRESSION, True)

    if "writer" in title_lower or "report" in title_lower:
        if "complete" in title_lower or "final" in title_lower:
            return (EventType.WRITER_COMPLETE, False)
        return (EventType.WRITER_START, True)

    if "final report" in title_lower:
        return (EventType.FINAL_REPORT, False)

    if "human" in title_lower:
        return (EventType.USER_MESSAGE, False)

    return (None, True)


def _extract_message_content(messages) -> str:
    """Best-effort extraction of human-readable content from a messages payload."""
    if isinstance(messages, str):
        return messages

    if isinstance(messages, list):
        parts = []
        for msg in messages:
            if hasattr(msg, "content"):
                content = msg.content
                if isinstance(content, str):
                    parts.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                parts.append(item.get("text", ""))
                            elif item.get("type") == "tool_use":
                                parts.append(f"Tool Call: {item.get('name', 'unknown')}")
                else:
                    parts.append(str(content))
            elif isinstance(msg, dict):
                parts.append(str(msg.get("content", msg)))
            else:
                parts.append(str(msg))
        return "\n".join(parts)

    return str(messages)
