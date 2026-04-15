from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class EventType(str, Enum):
    """Event types emitted during research workflow"""

    # Session events
    SESSION_CREATED = "session_created"
    SESSION_STARTED = "session_started"

    # Scope Agent events
    SCOPE_START = "scope_start"
    SCOPE_CLARIFICATION = "scope_clarification"
    SCOPE_BRIEF = "scope_brief"

    # Supervisor Agent events
    SUPERVISOR_START = "supervisor_start"
    SUPERVISOR_THINKING = "supervisor_thinking"
    SUPERVISOR_DELEGATION = "supervisor_delegation"

    # Research Agent events
    RESEARCH_START = "research_start"
    RESEARCH_TOOL_CALL = "research_tool_call"
    RESEARCH_TOOL_OUTPUT = "research_tool_output"
    RESEARCH_COMPLETE = "research_complete"

    # Writer Agent events
    COMPRESSION = "compression"
    WRITER_START = "writer_start"
    WRITER_COMPLETE = "writer_complete"

    # Final output events
    FINAL_REPORT = "final_report"
    CLARIFICATION_NEEDED = "clarification_needed"

    # Error and user events
    ERROR = "error"
    USER_MESSAGE = "user_message"


class MessageKind(str, Enum):
    """Python class of the underlying LangChain message, as detected by the interceptor."""

    HUMAN = "Human"
    AI = "AI"
    TOOL = "Tool"  # tool output (ToolMessage)
    TOOL_CALL = "ToolCall"  # tool call dict { name, args, id }
    CLARIFY = "ClarifyWithUser"
    RESEARCH_QUESTION = "ResearchQuestion"
    SYSTEM = "System"
    OTHER = "Other"


class AgentName(str, Enum):
    """Which agent produced the message."""

    SCOPE = "scope"
    SUPERVISOR = "supervisor"
    RESEARCH = "research"
    WRITER = "writer"
    UNKNOWN = "unknown"


class Event(BaseModel):
    """Event emitted during research.

    Legacy phase fields (``event_type``/``title``/``content``) remain for
    backward compatibility. New fields carry per-message metadata so the
    frontend can render each message in its own typed block.
    """

    event_type: EventType
    session_id: str
    title: str
    content: str
    metadata: Optional[dict] = None
    is_intermediate: bool = True
    timestamp: float  # Unix timestamp

    # Per-message metadata (new)
    message_type: Optional[MessageKind] = None
    message_subtype: Optional[str] = None  # e.g. "RealHumanMessage"
    agent: Optional[AgentName] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict[str, Any]] = None
    tool_call_id: Optional[str] = None


class WebSocketMessage(BaseModel):
    """WebSocket message format"""

    type: str  # "event", "error", "status", "complete", "ping", "connected"
    data: dict
