from typing import Any, Dict, List, Optional, Set
from asyncio import Queue
import asyncio
import logging
import time

from sqlalchemy import select

from api.database.db import db_session_context
from api.database.models import ResearchEvent as ResearchEventRow
from api.models.events import AgentName, Event, EventType, MessageKind

logger = logging.getLogger(__name__)


class EventService:
    """
    Centralized event service for capturing and distributing events.

    - Live streaming: per-session asyncio queues feed WebSocket consumers.
    - Durable history: every emitted event is also persisted to the
      ``research_events`` table so late joiners (page reload, new tab,
      API restart) can replay the full timeline.
    """

    def __init__(self):
        self._session_queues: Dict[str, Set[Queue]] = {}
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
        message_type: Optional[MessageKind] = None,
        message_subtype: Optional[str] = None,
        agent: Optional[AgentName] = None,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        tool_call_id: Optional[str] = None,
    ):
        """Emit an event to all live consumers and persist it to DB."""
        event = Event(
            event_type=event_type,
            session_id=session_id,
            title=title,
            content=content,
            metadata=metadata or {},
            is_intermediate=is_intermediate,
            timestamp=time.time(),
            message_type=message_type,
            message_subtype=message_subtype,
            agent=agent,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_call_id=tool_call_id,
        )

        # Persist to DB first so replay snapshots are authoritative.
        # Best-effort: live streaming must not fail if DB errors.
        try:
            async with db_session_context() as db:
                row = ResearchEventRow(
                    session_id=session_id,
                    event_type=event_type.value if hasattr(event_type, "value") else str(event_type),
                    title=title,
                    content=content,
                    is_intermediate=is_intermediate,
                    timestamp=event.timestamp,
                    message_type=message_type.value if message_type else None,
                    message_subtype=message_subtype,
                    agent=agent.value if agent else None,
                    tool_name=tool_name,
                    tool_args=tool_args,
                    tool_call_id=tool_call_id,
                    metadata_json=event.metadata or None,
                )
                db.add(row)
                await db.commit()
        except Exception:
            logger.exception("Failed to persist event for session %s", session_id)

        # Fan-out to active WS queues after persistence.
        async with self._lock:
            queues = list(self._session_queues.get(session_id, ()))
        for queue in queues:
            await queue.put(event)

    async def get_session_events(
        self, session_id: str, from_index: int = 0
    ) -> List[Event]:
        """Load session event history from DB, ordered by id (insertion order)."""
        try:
            async with db_session_context() as db:
                stmt = (
                    select(ResearchEventRow)
                    .where(ResearchEventRow.session_id == session_id)
                    .order_by(ResearchEventRow.id.asc())
                )
                result = await db.execute(stmt)
                rows = list(result.scalars().all())
        except Exception:
            logger.exception("Failed to load events for session %s", session_id)
            return []

        events: List[Event] = [_row_to_event(r) for r in rows]
        return events[from_index:]

    async def clear_session(self, session_id: str):
        """Drop live queues for a session (DB rows remain for history)."""
        async with self._lock:
            self._session_queues.pop(session_id, None)


def _row_to_event(row: ResearchEventRow) -> Event:
    def _enum_or_none(enum_cls, value):
        if value is None:
            return None
        try:
            return enum_cls(value)
        except ValueError:
            return None

    return Event(
        event_type=_enum_or_none(EventType, row.event_type) or EventType.USER_MESSAGE,
        session_id=row.session_id,
        title=row.title,
        content=row.content,
        metadata=row.metadata_json or {},
        is_intermediate=bool(row.is_intermediate),
        timestamp=row.timestamp or 0.0,
        message_type=_enum_or_none(MessageKind, row.message_type),
        message_subtype=row.message_subtype,
        agent=_enum_or_none(AgentName, row.agent),
        tool_name=row.tool_name,
        tool_args=row.tool_args,
        tool_call_id=row.tool_call_id,
    )


# Global singleton
_event_service: Optional[EventService] = None


def get_event_service() -> EventService:
    """Get the global event service instance"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
