"""
Model catalog and per-role resolution.

This module centralizes model metadata so the FastAPI layer can expose a
catalog endpoint (``GET /models``) and the LangGraph nodes can build their
LLM instances on the fly from the per-session ``RunnableConfig`` that the
frontend sends with each research run.

The previous design kept one ``initialize_model()`` singleton per role at
module import time inside ``LLM_models.py``. That made it impossible to pick
a different model per session without restarting the backend. Now each role
reads ``config["configurable"]["models"][role]`` inside the node function
and falls back to ``DEFAULT_MODELS_BY_ROLE`` when the user hasn't chosen
anything.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig

from utils.initialize_model import initialize_model

# ---------------------------------------------------------------------------
# Provider / endpoint constants (mirror what LLM_models.py used to define).
# ---------------------------------------------------------------------------

PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_GEMINI = "google_genai"

OPENAI_BASE_URL = "https://api.openai.com/v1"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
GITHUB_BASE_URL = "https://models.github.ai/inference"
CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"
KIMI_BASE_URL = "https://api.moonshot.ai/v1"


# ---------------------------------------------------------------------------
# Catalog of supported models.
#
# Each entry holds:
#   - label:           human-readable name shown in the UI
#   - provider:        langchain provider id passed to init_chat_model
#   - base_url:        REST endpoint (only used by OpenAI-compatible providers)
#   - api_key_env:     name of the env var that must be set for the model to
#                      be usable. The /models endpoint filters out entries
#                      whose key is missing so the user only sees what works.
#   - default_temperature
#   - default_max_tokens
# ---------------------------------------------------------------------------

MODEL_CATALOG: Dict[str, Dict[str, Any]] = {
    "gpt-4.1": {
        "label": "OpenAI GPT-4.1",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gpt-4.1-mini": {
        "label": "OpenAI GPT-4.1 Mini",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gpt-5": {
        "label": "OpenAI GPT-5",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gpt-5-mini": {
        "label": "OpenAI GPT-5 Mini",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gpt-5-nano": {
        "label": "OpenAI GPT-5 Nano",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gpt-5.1-2025-11-13": {
        "label": "OpenAI GPT-5.1",
        "provider": PROVIDER_OPENAI,
        "base_url": OPENAI_BASE_URL,
        "api_key_env": "OPENAI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "claude-sonnet-4-5": {
        "label": "Anthropic Claude Sonnet 4.5",
        "provider": PROVIDER_ANTHROPIC,
        "base_url": ANTHROPIC_BASE_URL,
        "api_key_env": "ANTHROPIC_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": 4096,
    },
    "kimi-k2-thinking": {
        "label": "Moonshot Kimi K2 Thinking",
        "provider": PROVIDER_OPENAI,  # OpenAI-compatible
        "base_url": KIMI_BASE_URL,
        "api_key_env": "KIMI_K2_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "gemini-3-pro-preview": {
        "label": "Google Gemini 3 Pro Preview",
        "provider": PROVIDER_GEMINI,
        "base_url": "",  # not used by google_genai provider
        "api_key_env": "GEMINI_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
    "qwen-3-coder-480b": {
        "label": "Cerebras Qwen 3 Coder 480B",
        "provider": PROVIDER_OPENAI,  # OpenAI-compatible via Cerebras
        "base_url": CEREBRAS_BASE_URL,
        "api_key_env": "CEREBRAS_API_KEY",
        "default_temperature": 0.0,
        "default_max_tokens": None,
    },
}


# ---------------------------------------------------------------------------
# Roles and their defaults.
#
# These mirror the historical hardcoded picks in LLM_models.py and are used
# both as the fallback inside ``get_role_model`` and as the ``defaults`` field
# of the catalog endpoint so the UI can preselect them on first load.
# ---------------------------------------------------------------------------

ROLES = ("scope", "supervisor", "research", "compress", "summarization", "writer")

DEFAULT_MODELS_BY_ROLE: Dict[str, str] = {
    "scope": "gpt-4.1",
    "supervisor": "claude-sonnet-4-5",
    "research": "claude-sonnet-4-5",
    "compress": "gpt-4.1",
    "summarization": "gpt-4.1-mini",
    "writer": "gpt-4.1",
}

# Roles that need a non-default ``max_tokens`` regardless of the model picked.
# These come from the original constants in LLM_models.py:
#   - research / supervisor: 4096   (tool-calling agents, short responses)
#   - compress / writer:     32000  (long-form output)
ROLE_MAX_TOKENS_OVERRIDES: Dict[str, int] = {
    "research": 4096,
    "supervisor": 4096,
    "compress": 32000,
    "writer": 32000,
}


# ---------------------------------------------------------------------------
# Dynamic registry — populated at runtime by /models/discover responses.
#
# Process-local; lost on backend restart. When the user picks a model that
# the live /models/discover call returned but isn't in MODEL_CATALOG,
# resolve_model_config falls back to this registry.
# ---------------------------------------------------------------------------

_dynamic_registry: Dict[str, Dict[str, Any]] = {}


def register_dynamic_models(entries: Any) -> None:
    """Add or update discovered models in the in-memory registry.

    ``entries`` is an iterable of dicts carrying at minimum ``name``,
    ``provider``, ``base_url``, ``api_key_env``, and optionally
    ``default_max_tokens`` and ``default_temperature``.
    """
    for entry in entries:
        name = entry.get("name")
        if not name:
            continue
        _dynamic_registry[name] = {
            "label": entry.get("label", name),
            "provider": entry["provider"],
            "base_url": entry.get("base_url", ""),
            "api_key_env": entry["api_key_env"],
            "default_temperature": entry.get("default_temperature", 0.0),
            "default_max_tokens": entry.get("default_max_tokens"),
        }


def _lookup_catalog_entry(model_name: str) -> Optional[Dict[str, Any]]:
    if model_name in MODEL_CATALOG:
        return MODEL_CATALOG[model_name]
    if model_name in _dynamic_registry:
        return _dynamic_registry[model_name]
    return None


def is_known_model(model_name: str) -> bool:
    return model_name in MODEL_CATALOG or model_name in _dynamic_registry


def is_known_role(role: str) -> bool:
    return role in ROLES


def get_api_key_for_provider(
    api_key_env: str, api_keys: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """Return the API key for ``api_key_env``, preferring user-provided ones.

    ``api_keys`` is the per-request dict sent from the frontend in
    ``config["configurable"]["api_keys"]``. If the user provided a non-empty
    value for ``api_key_env``, that wins; otherwise we fall back to the
    process environment (``.env`` on the backend). May return ``None`` if
    neither source has a value.
    """
    if api_keys:
        candidate = api_keys.get(api_key_env)
        if candidate:
            return candidate
    return os.getenv(api_key_env)


def resolve_model_config(
    model_name: str,
    role: Optional[str] = None,
    api_keys: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Return the kwargs needed by ``initialize_model`` for ``model_name``.

    If ``role`` is given and that role has an entry in
    ``ROLE_MAX_TOKENS_OVERRIDES``, the override wins over the model's default.
    If ``api_keys`` is given, it is used to look up the provider API key
    before falling back to the environment.
    """
    entry = _lookup_catalog_entry(model_name)
    if entry is None:
        raise ValueError(f"Unknown model: {model_name}")

    api_key_env = entry["api_key_env"]
    api_key = get_api_key_for_provider(api_key_env, api_keys=api_keys)

    max_tokens = entry["default_max_tokens"]
    if role is not None and role in ROLE_MAX_TOKENS_OVERRIDES:
        max_tokens = ROLE_MAX_TOKENS_OVERRIDES[role]

    return {
        "model_name": model_name,
        "model_provider": entry["provider"],
        "base_url": entry["base_url"],
        "temperature": entry["default_temperature"],
        "api_key": api_key,
        "max_tokens": max_tokens,
    }


def get_role_model(role: str, config: Optional[RunnableConfig] = None) -> BaseChatModel:
    """Build the chat model for ``role`` using the per-session config.

    Reads ``config["configurable"]["models"][role]`` and falls back to
    ``DEFAULT_MODELS_BY_ROLE[role]`` if no override was provided. Reads
    ``config["configurable"]["api_keys"]`` for user-supplied API keys.
    """
    if not is_known_role(role):
        raise ValueError(f"Unknown role: {role}")

    model_name: Optional[str] = None
    api_keys: Optional[Dict[str, str]] = None
    if config is not None:
        configurable = config.get("configurable", {}) or {}
        models_override = configurable.get("models") or {}
        candidate = models_override.get(role)
        if candidate and is_known_model(candidate):
            model_name = candidate
        api_keys = configurable.get("api_keys") or None

    if model_name is None:
        model_name = DEFAULT_MODELS_BY_ROLE[role]

    kwargs = resolve_model_config(model_name, role=role, api_keys=api_keys)

    entry = _lookup_catalog_entry(model_name) or {}
    env_name = entry.get("api_key_env", "unknown")
    has_key = bool(kwargs.get("api_key"))
    import logging as _logging
    _logging.getLogger(__name__).info(
        "get_role_model role=%s model=%s env=%s key_found=%s (from_config=%s from_env=%s)",
        role, model_name, env_name, has_key,
        bool(api_keys and api_keys.get(env_name)),
        bool(os.getenv(env_name)),
    )

    if not has_key:
        provider = entry.get("provider", "unknown")
        raise ValueError(
            f"Missing API key for model '{model_name}' (provider "
            f"'{provider}', env {env_name}). "
            "Please provide it in the frontend settings or set it in the "
            "backend .env."
        )

    return initialize_model(**kwargs)


def list_available_models() -> Dict[str, Dict[str, Any]]:
    """Deprecated: env-based filtering is no longer used by the /models endpoint.

    The frontend now decides which models are usable based on the API keys the
    user has entered in the settings modal. Kept here for backward compatibility
    with any callers (tests, scripts) that might still rely on it.
    """
    available: Dict[str, Dict[str, Any]] = {}
    for name, entry in MODEL_CATALOG.items():
        if os.getenv(entry["api_key_env"]):
            available[name] = entry
    return available
