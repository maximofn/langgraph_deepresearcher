"""
Request models for the API.
"""

from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    """Request to create a new research session"""

    query: str = Field(
        ..., min_length=1, description="Research question or query", max_length=5000
    )
    max_iterations: int = Field(
        default=6,
        ge=1,
        le=20,
        description="Maximum research iterations for supervisor agent",
    )
    max_concurrent_researchers: int = Field(
        default=3, ge=1, le=10, description="Maximum concurrent research agents"
    )


class ContinueSessionRequest(BaseModel):
    """Request to continue a session with clarification"""

    clarification: str = Field(
        ...,
        min_length=1,
        description="User's response to clarification question",
        max_length=5000,
    )
