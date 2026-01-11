from enum import Enum
from typing import Optional
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


class Event(BaseModel):
    """Event emitted during research"""

    event_type: EventType
    session_id: str
    title: str
    content: str
    metadata: Optional[dict] = None
    is_intermediate: bool = True
    timestamp: float  # Unix timestamp


class WebSocketMessage(BaseModel):
    """WebSocket message format"""

    type: str  # "event", "error", "status", "complete", "ping", "connected"
    data: dict
