"""
Event tracking system for Deep Researcher UI

This module provides a centralized event tracking system that allows
the Deep Researcher components to emit events that can be captured
and displayed in the Gradio interface.
"""

from typing import Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    """Types of events that can be emitted during research"""
    SCOPE_START = "scope_start"
    SCOPE_CLARIFICATION = "scope_clarification"
    SCOPE_BRIEF = "scope_brief"
    SUPERVISOR_START = "supervisor_start"
    SUPERVISOR_THINKING = "supervisor_thinking"
    SUPERVISOR_DELEGATION = "supervisor_delegation"
    RESEARCH_START = "research_start"
    RESEARCH_TOOL_CALL = "research_tool_call"
    RESEARCH_TOOL_OUTPUT = "research_tool_output"
    RESEARCH_COMPLETE = "research_complete"
    COMPRESSION = "compression"
    WRITER_START = "writer_start"
    WRITER_COMPLETE = "writer_complete"
    FINAL_REPORT = "final_report"
    ERROR = "error"

@dataclass
class Event:
    """Represents an event emitted during research"""
    event_type: EventType
    title: str
    content: str
    metadata: Optional[dict] = None
    is_intermediate: bool = True  # True for intermediate outputs (shown with transparency)

class EventTracker:
    """
    Central event tracker for capturing and distributing events
    from the Deep Researcher system to the UI
    """

    def __init__(self):
        self.callbacks: list[Callable[[Event], None]] = []
        self.events: list[Event] = []

    def register_callback(self, callback: Callable[[Event], None]):
        """Register a callback function to receive events"""
        self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[Event], None]):
        """Unregister a callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def emit(self, event_type: EventType, title: str, content: str,
             metadata: Optional[dict] = None, is_intermediate: bool = True):
        """Emit an event to all registered callbacks"""
        event = Event(
            event_type=event_type,
            title=title,
            content=content,
            metadata=metadata,
            is_intermediate=is_intermediate
        )
        self.events.append(event)

        # Notify all callbacks
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")

    def clear(self):
        """Clear all events"""
        self.events = []

    def get_events(self) -> list[Event]:
        """Get all events"""
        return self.events.copy()

# Global event tracker instance
_global_tracker: Optional[EventTracker] = None

def get_tracker() -> EventTracker:
    """Get the global event tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = EventTracker()
    return _global_tracker

def reset_tracker():
    """Reset the global event tracker"""
    global _global_tracker
    _global_tracker = EventTracker()
