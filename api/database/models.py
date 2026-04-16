from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, Boolean, Integer, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum


Base = declarative_base()


class SessionStatus(str, enum.Enum):
    """Research session status"""

    CREATED = "created"
    ACTIVE = "active"
    CLARIFICATION_NEEDED = "clarification_needed"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class Session(Base):
    """Research session model"""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)  # UUID
    thread_id = Column(String(36), unique=True, nullable=False)  # LangGraph thread ID
    client_id = Column(String(36), nullable=True, index=True)  # Device-scoped UUID from frontend
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.CREATED)

    # User input
    initial_query = Column(Text, nullable=False)
    clarification_response = Column(Text, nullable=True)

    # Research outputs
    research_brief = Column(Text, nullable=True)
    final_report = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Configuration
    max_iterations = Column(Integer, default=6)
    max_concurrent_researchers = Column(Integer, default=3)
    # JSON map of role -> model name picked from the frontend settings modal.
    # Null means "use backend defaults" (see LLM_models/model_catalog.py).
    models_config = Column(JSON, nullable=True)

    # Contact info for final-report delivery.
    user_name = Column(String(200), nullable=True)
    user_email = Column(String(320), nullable=True)


class Message(Base):
    """Message history for sessions"""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user", "assistant", "system"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchEvent(Base):
    """Event log for research sessions"""

    __tablename__ = "research_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_intermediate = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamp emitted by the interceptor (Unix seconds), for ordering.
    timestamp = Column(Float, nullable=True)

    # Per-message metadata (mirrors api/models/events.Event)
    message_type = Column(String(32), nullable=True)
    message_subtype = Column(String(64), nullable=True)
    agent = Column(String(32), nullable=True)
    tool_name = Column(String(128), nullable=True)
    tool_args = Column(JSON, nullable=True)
    tool_call_id = Column(String(128), nullable=True)
    metadata_json = Column(JSON, nullable=True)
