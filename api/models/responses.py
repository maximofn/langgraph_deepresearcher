"""
Response models for the API.
"""

from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, List
from datetime import datetime

from api.database.models import SessionStatus


class SessionResponse(BaseModel):
    """Response model for a research session"""

    model_config = ConfigDict(from_attributes=True)

    id: str
    thread_id: str
    status: SessionStatus
    initial_query: str
    clarification_response: Optional[str] = None
    research_brief: Optional[str] = None
    final_report: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    max_iterations: int
    max_concurrent_researchers: int
    models_config: Optional[Dict[str, str]] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class CreateSessionResponse(BaseModel):
    """Response when creating a new session"""

    session: SessionResponse
    websocket_url: str


class MessageResponse(BaseModel):
    """Response model for a message"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime


class SessionListResponse(BaseModel):
    """Response for listing sessions"""

    sessions: List[SessionResponse]
    total: int
    limit: int
    offset: int


class StartResearchResponse(BaseModel):
    """Response when starting research"""

    status: str
    session_id: str
    message: str
