"""
Message interceptor for capturing agent outputs.

Patches ``src/utils/message_utils.format_messages`` at startup and, for each
call, emits one structured event *per message* so the WebSocket stream carries
enough metadata for the frontend to render each item in its own typed block
(same colors/emoji the CLI uses via Rich).

Concurrency-safe across sessions thanks to a ``ContextVar`` that binds each
call to the currently active ``session_id``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

from api.models.events import AgentName, EventType, MessageKind
from api.services.event_service import get_event_service
from api.utils.paths import ensure_src_on_path

logger = logging.getLogger(__name__)

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
    token = current_session_id.set(session_id)
    try:
        yield
    finally:
        current_session_id.reset(token)


# ---------- intercepting function ----------


def _intercepting_format_messages(
    messages, title: str = "", border_style: str = "white", msg_subtype: str = ""
):
    session_id = current_session_id.get()

    if session_id is not None:
        try:
            _emit_messages(session_id, messages, title, msg_subtype)
        except Exception:
            logger.exception("Failed to emit events for intercepted format_messages")

    if _original_format_messages is not None:
        _original_format_messages(messages, title, border_style, msg_subtype)


def _emit_messages(session_id: str, messages, title: str, msg_subtype: str) -> None:
    """Dispatch ``messages`` (list or str) into one event per logical message."""
    phase_event_type, is_intermediate_default = _determine_event_type(title, msg_subtype)
    agent = _determine_agent(title)

    if isinstance(messages, str):
        _schedule(
            session_id=session_id,
            event_type=phase_event_type or EventType.USER_MESSAGE,
            title=title or "System Message",
            content=messages,
            is_intermediate=is_intermediate_default,
            message_type=MessageKind.OTHER,
            message_subtype=msg_subtype or None,
            agent=agent,
        )
        return

    if not isinstance(messages, list):
        return

    for m in messages:
        kind, subtype = _detect_message_kind(m, msg_subtype)
        if kind is MessageKind.HUMAN and msg_subtype != "RealHumanMessage":
            # Skip simulated human messages — they are internal plumbing
            # and the CLI prints them differently. We still forward real ones
            # so the user sees their own query echoed back.
            continue

        # Extract tool-call payload (Anthropic content-list format + OpenAI tool_calls)
        tool_calls = _extract_tool_calls(m)
        text_content = _extract_text_content(m)

        if tool_calls:
            # Emit the leading text (if any) as an AI message, then one event per tool call.
            if text_content.strip():
                _schedule(
                    session_id=session_id,
                    event_type=phase_event_type or EventType.RESEARCH_TOOL_CALL,
                    title=title or kind.value,
                    content=text_content,
                    is_intermediate=is_intermediate_default,
                    message_type=kind,
                    message_subtype=subtype,
                    agent=agent,
                )
            for tc in tool_calls:
                _schedule(
                    session_id=session_id,
                    event_type=EventType.RESEARCH_TOOL_CALL,
                    title=f"{tc.get('name') or 'tool'}",
                    content=_format_tool_call_preview(tc),
                    is_intermediate=True,
                    message_type=MessageKind.TOOL_CALL,
                    message_subtype=subtype,
                    agent=agent,
                    tool_name=tc.get("name"),
                    tool_args=tc.get("args") if isinstance(tc.get("args"), dict) else None,
                    tool_call_id=tc.get("id"),
                )
            continue

        # Regular (non-tool-call) message.
        _schedule(
            session_id=session_id,
            event_type=phase_event_type or _default_event_for_kind(kind),
            title=title or kind.value,
            content=text_content,
            is_intermediate=is_intermediate_default,
            message_type=kind,
            message_subtype=subtype,
            agent=agent,
            tool_name=_tool_name_from_msg(m) if kind is MessageKind.TOOL else None,
            tool_call_id=_tool_call_id_from_msg(m) if kind is MessageKind.TOOL else None,
        )


def _schedule(**kwargs) -> None:
    """Fire-and-forget async emit."""
    event_service = get_event_service()
    coro = event_service.emit(**kwargs)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(coro)
        except Exception:
            logger.exception("Failed to emit event synchronously")
        return
    loop.create_task(coro)


# ---------- type detection helpers ----------


def _detect_message_kind(m: Any, msg_subtype: str) -> Tuple[MessageKind, Optional[str]]:
    """Mirror ``format_messages`` class-name based detection."""
    if isinstance(m, dict):
        if "args" in m and "name" in m:
            return MessageKind.TOOL_CALL, msg_subtype or None
        return MessageKind.OTHER, msg_subtype or None

    cls = type(m).__name__
    base = cls.replace("Message", "")  # e.g. HumanMessage -> Human
    mapping = {
        "Human": MessageKind.HUMAN,
        "AI": MessageKind.AI,
        "Tool": MessageKind.TOOL,
        "System": MessageKind.SYSTEM,
        "ClarifyWithUser": MessageKind.CLARIFY,
        "ResearchQuestion": MessageKind.RESEARCH_QUESTION,
    }
    return mapping.get(base, MessageKind.OTHER), msg_subtype or None


def _default_event_for_kind(kind: MessageKind) -> EventType:
    if kind is MessageKind.HUMAN:
        return EventType.USER_MESSAGE
    if kind is MessageKind.CLARIFY:
        return EventType.SCOPE_CLARIFICATION
    if kind is MessageKind.RESEARCH_QUESTION:
        return EventType.SCOPE_BRIEF
    if kind is MessageKind.TOOL:
        return EventType.RESEARCH_TOOL_OUTPUT
    if kind is MessageKind.TOOL_CALL:
        return EventType.RESEARCH_TOOL_CALL
    return EventType.SUPERVISOR_THINKING


def _extract_tool_calls(m: Any) -> List[Dict[str, Any]]:
    """Return a list of ``{name, args, id}`` dicts for tool calls on ``m``."""
    calls: List[Dict[str, Any]] = []

    # Anthropic-style: message.content is a list of blocks, some `tool_use`.
    content = getattr(m, "content", None)
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                calls.append(
                    {
                        "name": item.get("name"),
                        "args": item.get("input") or {},
                        "id": item.get("id"),
                    }
                )

    # OpenAI-style: message.tool_calls
    tc_attr = getattr(m, "tool_calls", None) or []
    for tc in tc_attr:
        if isinstance(tc, dict):
            calls.append(
                {
                    "name": tc.get("name"),
                    "args": tc.get("args") or tc.get("arguments") or {},
                    "id": tc.get("id"),
                }
            )

    return calls


def _extract_text_content(m: Any) -> str:
    """Best-effort string extraction (text parts only, no tool-use)."""
    if isinstance(m, dict):
        if "content" in m:
            return str(m.get("content", ""))
        return str(m)

    content = getattr(m, "content", None)
    if content is None:
        return str(m)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "\n".join(parts)
    return str(content)


def _tool_name_from_msg(m: Any) -> Optional[str]:
    return getattr(m, "name", None)


def _tool_call_id_from_msg(m: Any) -> Optional[str]:
    return getattr(m, "tool_call_id", None)


def _format_tool_call_preview(tc: Dict[str, Any]) -> str:
    name = tc.get("name") or "tool"
    args = tc.get("args")
    try:
        args_str = json.dumps(args, ensure_ascii=False, indent=2) if args else "{}"
    except Exception:
        args_str = str(args)
    return f"{name}({args_str})"


def _determine_agent(title: str) -> AgentName:
    t = (title or "").lower()
    if "scope" in t:
        return AgentName.SCOPE
    if "supervisor" in t:
        return AgentName.SUPERVISOR
    if "research" in t or "researcher" in t or "compress" in t:
        return AgentName.RESEARCH
    if "writer" in t or "report" in t:
        return AgentName.WRITER
    return AgentName.UNKNOWN


def _determine_event_type(title: str, msg_subtype: str) -> Tuple[Optional[EventType], bool]:
    title_lower = (title or "").lower()

    if msg_subtype == "RealHumanMessage":
        return (EventType.USER_MESSAGE, False)

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
