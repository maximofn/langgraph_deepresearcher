from typing import Dict, Set, Optional
from asyncio import Queue
import asyncio
import time

from api.models.events import Event, EventType


class EventService:
    """
    Centralized event service for capturing and distributing events.
    Adapted from front/event_tracker.py for multi-user WebSocket emission.
    """

    def __init__(self):
        # Session-specific event queues for WebSocket consumers
        self._session_queues: Dict[str, Set[Queue]] = {}

        # Session event history (for reconnection and state recovery)
        self._session_events: Dict[str, list[Event]] = {}

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def register_consumer(self, session_id: str) -> Queue:
        """Register a WebSocket consumer for a session"""
        async with self._lock:
            queue: Queue = Queue()
            if session_id not in self._session_queues:
                self._session_queues[session_id] = set()
            self._session_queues[session_id].add(queue)
            return queue

    async def unregister_consumer(self, session_id: str, queue: Queue):
        """Unregister a WebSocket consumer"""
        async with self._lock:
            if session_id in self._session_queues:
                self._session_queues[session_id].discard(queue)
                if not self._session_queues[session_id]:
                    del self._session_queues[session_id]

    async def emit(
        self,
        session_id: str,
        event_type: EventType,
        title: str,
        content: str,
        metadata: Optional[dict] = None,
        is_intermediate: bool = True,
    ):
        """Emit an event to all consumers of a session"""
        event = Event(
            event_type=event_type,
            session_id=session_id,
            title=title,
            content=content,
            metadata=metadata or {},
            is_intermediate=is_intermediate,
            timestamp=time.time(),
        )

        # Store in session history
        async with self._lock:
            if session_id not in self._session_events:
                self._session_events[session_id] = []
            self._session_events[session_id].append(event)

            # Emit to all consumers
            if session_id in self._session_queues:
                for queue in self._session_queues[session_id]:
                    await queue.put(event)

    async def get_session_events(
        self, session_id: str, from_index: int = 0
    ) -> list[Event]:
        """Get session event history (for reconnection)"""
        async with self._lock:
            events = self._session_events.get(session_id, [])
            return events[from_index:]

    async def clear_session(self, session_id: str):
        """Clear session events after completion or expiration"""
        async with self._lock:
            self._session_events.pop(session_id, None)
            self._session_queues.pop(session_id, None)


# Global singleton
_event_service: Optional[EventService] = None


def get_event_service() -> EventService:
    """Get the global event service instance"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
