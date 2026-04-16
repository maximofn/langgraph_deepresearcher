"""
Request models for the API.
"""

import re
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

# Lightweight email check — avoids adding the ``email-validator`` dep just to
# validate an address at the API boundary. Good enough for UX feedback; real
# validation happens when we actually try to send.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

from api.utils.paths import ensure_src_on_path

ensure_src_on_path()
from LLM_models.model_catalog import ROLES, is_known_model, is_known_role  # type: ignore[import-not-found]


# Closed whitelist of API key env-var names the frontend is allowed to send.
# TAVILY_API_KEY is deliberately excluded — web search keys stay in the
# backend .env, they are not a per-user credential.
ALLOWED_API_KEY_ENVS = frozenset(
    {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "KIMI_K2_API_KEY",
        "CEREBRAS_API_KEY",
        "GITHUB_API_KEY",
    }
)


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
    models: Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Optional per-role model overrides. Keys must be known roles "
            f"({', '.join(ROLES)}); values must be model names from the catalog "
            "exposed by GET /models."
        ),
    )
    # User-provided LLM API keys. NEVER persist to DB, NEVER log. Only live
    # in memory during graph execution. See api/services/research_service.py.
    api_keys: Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Optional per-provider API keys. Keys must be one of "
            f"{sorted(ALLOWED_API_KEY_ENVS)}. Values are used only for this "
            "session and never persisted."
        ),
    )
    # Optional contact info used to deliver the final report by email when
    # the research completes. Persisted on the session row so the delivery
    # task can pick them up even after a backend restart.
    user_name: Optional[str] = Field(default=None, max_length=200)
    user_email: Optional[str] = Field(default=None, max_length=320)

    @field_validator("user_name")
    @classmethod
    def _normalize_user_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("user_email")
    @classmethod
    def _normalize_user_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not _EMAIL_RE.match(value):
            raise ValueError(f"Invalid email address: {value!r}")
        return value

    @field_validator("models")
    @classmethod
    def _validate_models(cls, value: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        for role, model_name in value.items():
            if not is_known_role(role):
                raise ValueError(f"Unknown role: {role!r}. Allowed: {sorted(ROLES)}")
            if not is_known_model(model_name):
                raise ValueError(
                    f"Unknown model {model_name!r} for role {role!r}. "
                    "Use GET /models to list supported models."
                )
        return value

    @field_validator("api_keys")
    @classmethod
    def _validate_api_keys(
        cls, value: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        cleaned: Dict[str, str] = {}
        for env_name, key_value in value.items():
            if env_name not in ALLOWED_API_KEY_ENVS:
                raise ValueError(
                    f"API key {env_name!r} is not allowed. "
                    f"Allowed: {sorted(ALLOWED_API_KEY_ENVS)}"
                )
            if not isinstance(key_value, str) or not key_value.strip():
                raise ValueError(
                    f"API key value for {env_name!r} must be a non-empty string"
                )
            cleaned[env_name] = key_value.strip()
        return cleaned or None


class ChatSessionRequest(BaseModel):
    """Request para enviar un mensaje de chat en una sesión completada."""

    message: str = Field(
        ...,
        min_length=1,
        description="Pregunta de seguimiento sobre la investigación",
        max_length=5000,
    )


class ContinueSessionRequest(BaseModel):
    """Request to continue a session with clarification"""

    clarification: str = Field(
        ...,
        min_length=1,
        description="User's response to clarification question",
        max_length=5000,
    )
    # Re-sent from the frontend on clarification so the continuation run can
    # use the user's keys. Never persisted.
    api_keys: Optional[Dict[str, str]] = Field(default=None)

    @field_validator("api_keys")
    @classmethod
    def _validate_api_keys(
        cls, value: Optional[Dict[str, str]]
    ) -> Optional[Dict[str, str]]:
        if value is None:
            return None
        cleaned: Dict[str, str] = {}
        for env_name, key_value in value.items():
            if env_name not in ALLOWED_API_KEY_ENVS:
                raise ValueError(
                    f"API key {env_name!r} is not allowed. "
                    f"Allowed: {sorted(ALLOWED_API_KEY_ENVS)}"
                )
            if not isinstance(key_value, str) or not key_value.strip():
                raise ValueError(
                    f"API key value for {env_name!r} must be a non-empty string"
                )
            cleaned[env_name] = key_value.strip()
        return cleaned or None
