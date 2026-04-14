"""
Session service for managing research sessions.
Provides CRUD operations for sessions and messages.
"""

from uuid import uuid4
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from typing import Optional, List

from api.database.models import Message, ResearchEvent, Session, SessionStatus


class SessionService:
    """Manages research sessions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        initial_query: str,
        max_iterations: int = 6,
        max_concurrent_researchers: int = 3,
    ) -> Session:
        """Create a new research session"""
        session = Session(
            id=str(uuid4()),
            thread_id=str(uuid4()),
            initial_query=initial_query,
            status=SessionStatus.CREATED,
            max_iterations=max_iterations,
            max_concurrent_researchers=max_concurrent_researchers,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_session_status(
        self, session_id: str, status: SessionStatus, **kwargs
    ) -> Session:
        """
        Update session status and optionally other fields.

        Args:
            session_id: Session ID
            status: New status
            **kwargs: Additional fields to update (research_brief, final_report, etc.)
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = status
        session.updated_at = datetime.now(timezone.utc)

        if status == SessionStatus.COMPLETED:
            session.completed_at = datetime.now(timezone.utc)

        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def add_message(self, session_id: str, role: str, content: str) -> Message:
        """Add a message to session history"""
        message = Message(session_id=session_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_session_messages(self, session_id: str) -> List[Message]:
        """Get all messages for a session"""
        result = await self.db.execute(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def list_sessions(
        self, limit: int = 50, offset: int = 0, status: Optional[SessionStatus] = None
    ) -> List[Session]:
        """List all sessions with pagination and optional filtering"""
        query = select(Session).order_by(Session.created_at.desc())

        if status:
            query = query.where(Session.status == status)

        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and cascade its messages + event log.

        Returns True if the session existed and was removed, False otherwise.
        """
        session = await self.get_session(session_id)
        if session is None:
            return False

        await self.db.execute(
            delete(Message).where(Message.session_id == session_id)
        )
        await self.db.execute(
            delete(ResearchEvent).where(ResearchEvent.session_id == session_id)
        )
        await self.db.delete(session)
        await self.db.commit()
        return True

    async def cleanup_expired_sessions(self, expiry_hours: int = 24) -> int:
        """Clean up sessions older than expiry_hours that are not completed"""
        expiry_time = datetime.now(timezone.utc) - timedelta(hours=expiry_hours)

        result = await self.db.execute(
            select(Session)
            .where(Session.created_at < expiry_time)
            .where(Session.status != SessionStatus.COMPLETED)
        )
        expired_sessions = result.scalars().all()

        count = 0
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED
            count += 1

        await self.db.commit()
        return count
