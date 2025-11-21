"""
Message Interceptor for capturing format_messages calls

This module provides a monkey-patching mechanism to intercept calls to
format_messages and emit events for the Gradio UI without modifying
the original source code.
"""

import sys
from typing import Optional, Callable

sys.path.append('src')

from front.event_tracker import get_tracker, EventType


# Store the original format_messages function
_original_format_messages: Optional[Callable] = None
_interception_enabled = False


def enable_interception():
    """Enable interception of format_messages calls"""
    global _original_format_messages, _interception_enabled

    if _interception_enabled:
        return

    try:
        from utils import message_utils

        # Store the original function
        _original_format_messages = message_utils.format_messages

        # Replace with our intercepting version
        message_utils.format_messages = _intercepting_format_messages

        _interception_enabled = True
        print("✓ Message interception enabled")

    except ImportError as e:
        print(f"Failed to enable interception: {e}")


def disable_interception():
    """Disable interception and restore original function"""
    global _original_format_messages, _interception_enabled

    if not _interception_enabled:
        return

    try:
        from utils import message_utils

        if _original_format_messages:
            message_utils.format_messages = _original_format_messages

        _interception_enabled = False
        print("✓ Message interception disabled")

    except ImportError as e:
        print(f"Failed to disable interception: {e}")


def _intercepting_format_messages(messages, title: str = "", border_style: str = "white", msg_subtype: str = ""):
    """
    Intercepting version of format_messages that emits events
    before calling the original function
    """
    tracker = get_tracker()

    # Determine event type and emit event based on title
    event_type, is_intermediate = _determine_event_type(title, msg_subtype)

    # Extract message content
    content = _extract_message_content(messages)

    # Emit event (always emit, even if event_type is None, for debugging)
    if event_type:
        tracker.emit(
            event_type=event_type,
            title=title if title else "System Message",
            content=content,
            is_intermediate=is_intermediate
        )
        print(f"[INTERCEPTOR] ✓ Event emitted: {event_type.value} - {title[:50] if len(title) > 50 else title}")
    else:
        # Still log for debugging
        if title and msg_subtype != "RealHumanMessage":
            print(f"[INTERCEPTOR] ⊘ Skipped event for title: {title}")

    # Call the original function to maintain console output
    if _original_format_messages:
        _original_format_messages(messages, title, border_style, msg_subtype)


def _determine_event_type(title: str, msg_subtype: str) -> tuple[Optional[EventType], bool]:
    """
    Determine the event type based on title and message subtype

    Returns:
        tuple: (EventType or None, is_intermediate)
    """
    title_lower = title.lower()

    # User messages
    if msg_subtype == "RealHumanMessage":
        return (None, False)  # Don't emit for real user messages

    # Scope Agent
    if "scope" in title_lower:
        if "clarification" in title_lower or "need clarification" in title_lower:
            return (EventType.SCOPE_CLARIFICATION, True)
        elif "research brief" in title_lower or "brief generated" in title_lower:
            return (EventType.SCOPE_BRIEF, True)
        else:
            return (EventType.SCOPE_START, True)

    # Supervisor Agent
    if "supervisor" in title_lower:
        if "think" in title_lower:
            return (EventType.SUPERVISOR_THINKING, True)
        elif "conduct research" in title_lower or "delegation" in title_lower:
            return (EventType.SUPERVISOR_DELEGATION, True)
        else:
            return (EventType.SUPERVISOR_START, True)

    # Research Agent
    if "research" in title_lower:
        if "tool" in title_lower and "call" in title_lower:
            return (EventType.RESEARCH_TOOL_CALL, True)
        elif "tool" in title_lower and "output" in title_lower:
            return (EventType.RESEARCH_TOOL_OUTPUT, True)
        elif "complete" in title_lower:
            return (EventType.RESEARCH_COMPLETE, True)
        else:
            return (EventType.RESEARCH_START, True)

    # Writer Agent
    if "writer" in title_lower:
        if "final report" in title_lower:
            return (EventType.WRITER_COMPLETE, False)
        else:
            return (EventType.WRITER_START, True)

    # Compression
    if "compression" in title_lower or "compress" in title_lower:
        return (EventType.COMPRESSION, True)

    return (None, True)


def _extract_message_content(messages) -> str:
    """
    Extract readable content from messages

    Args:
        messages: Message or list of messages

    Returns:
        String representation of the message content
    """
    if isinstance(messages, str):
        return messages

    if isinstance(messages, list):
        if len(messages) == 0:
            return ""

        # Get the first message's content
        msg = messages[0]
        if isinstance(msg, str):
            return msg
        elif hasattr(msg, 'content'):
            return str(msg.content)
        elif isinstance(msg, dict):
            # Handle structured outputs like ClarifyWithUser, ResearchQuestion
            if 'question' in msg:
                return f"Question: {msg.get('question', '')}"
            elif 'research_brief' in msg:
                return f"Research Brief: {msg.get('research_brief', '')}"
            elif 'verification' in msg:
                return f"Verification: {msg.get('verification', '')}"
            else:
                return str(msg)
        else:
            return str(msg)

    # Single message
    if hasattr(messages, 'content'):
        return str(messages.content)
    elif isinstance(messages, dict):
        if 'question' in messages:
            return f"Question: {messages.get('question', '')}"
        elif 'research_brief' in messages:
            return f"Research Brief: {messages.get('research_brief', '')}"
        elif 'verification' in messages:
            return f"Verification: {messages.get('verification', '')}"
        else:
            return str(messages)

    return str(messages)
