"""Domain exceptions and standard error response schema."""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel


class APIException(Exception):
    """Base class for expected API errors that map to structured responses."""

    code: str = "api_error"
    status_code: int = 500

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SessionNotFoundError(APIException):
    code = "session_not_found"
    status_code = 404


class InvalidSessionStateError(APIException):
    code = "invalid_session_state"
    status_code = 400


class ResearchExecutionError(APIException):
    code = "research_execution_error"
    status_code = 500


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
