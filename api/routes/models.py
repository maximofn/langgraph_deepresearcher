"""Catalog endpoints for selectable LLM models.

``GET /models/`` returns the static catalog. ``POST /models/discover`` takes
a set of user-supplied API keys and queries each provider's live
``/v1/models`` endpoint to build a dynamic list. The discovered entries are
also registered in the in-process catalog so that later research runs can
resolve models that are not in the hardcoded ``MODEL_CATALOG``.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from api.services.model_discovery import discover_models
from api.utils.paths import ensure_src_on_path

ensure_src_on_path()
from LLM_models.model_catalog import (  # type: ignore[import-not-found]
    DEFAULT_MODELS_BY_ROLE,
    MODEL_CATALOG,
    ROLES,
    register_dynamic_models,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])


# Must match ALLOWED_API_KEY_ENVS in api/models/requests.py. Kept inline here
# to avoid a circular import between routes and request models.
_ALLOWED_API_KEY_ENVS = frozenset(
    {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "KIMI_K2_API_KEY",
        "CEREBRAS_API_KEY",
        "GITHUB_API_KEY",
    }
)


class ModelInfo(BaseModel):
    name: str
    label: str
    provider: str
    api_key_env: str


class ProviderStatus(BaseModel):
    ok: bool
    count: Optional[int] = None
    error: Optional[str] = None


class ModelsCatalogResponse(BaseModel):
    models: List[ModelInfo]
    defaults: Dict[str, str]
    roles: List[str]
    providers: Optional[Dict[str, ProviderStatus]] = None


class ModelsDiscoverRequest(BaseModel):
    api_keys: Dict[str, str] = Field(
        default_factory=dict,
        description=(
            "User-provided API keys per provider. Keys must be from the same "
            "whitelist accepted by CreateSessionRequest."
        ),
    )

    @field_validator("api_keys")
    @classmethod
    def _validate_api_keys(cls, value: Dict[str, str]) -> Dict[str, str]:
        cleaned: Dict[str, str] = {}
        for env_name, key_value in value.items():
            if env_name not in _ALLOWED_API_KEY_ENVS:
                raise ValueError(
                    f"API key {env_name!r} is not allowed. "
                    f"Allowed: {sorted(_ALLOWED_API_KEY_ENVS)}"
                )
            if not isinstance(key_value, str) or not key_value.strip():
                raise ValueError(
                    f"API key value for {env_name!r} must be a non-empty string"
                )
            cleaned[env_name] = key_value.strip()
        return cleaned


def _static_catalog_models() -> List[ModelInfo]:
    return [
        ModelInfo(
            name=name,
            label=entry["label"],
            provider=entry["provider"],
            api_key_env=entry["api_key_env"],
        )
        for name, entry in MODEL_CATALOG.items()
    ]


@router.get("/", response_model=ModelsCatalogResponse)
async def get_models() -> ModelsCatalogResponse:
    """Return the static backend catalog.

    The frontend uses this as a fallback when no API keys are available and
    live discovery cannot run.
    """
    return ModelsCatalogResponse(
        models=_static_catalog_models(),
        defaults=dict(DEFAULT_MODELS_BY_ROLE),
        roles=list(ROLES),
    )


@router.post("/discover", response_model=ModelsCatalogResponse)
async def post_discover(request: ModelsDiscoverRequest) -> ModelsCatalogResponse:
    """Query provider APIs in parallel to build a live model catalog.

    For each provider whose API key is present in ``request.api_keys``, query
    the corresponding list-models endpoint, normalize results, register them
    in the in-process catalog, and return the union. Providers without a key
    fall back to the entries in the static catalog so the UI can still show
    them marked as "missing key".
    """
    result = await discover_models(request.api_keys)

    # Register discovered entries so later POST /sessions/ requests can pick
    # a dynamic model and have the runtime resolve its provider/base_url.
    register_dynamic_models(result["models"])

    queried_envs = set(result["providers"].keys())
    seen_names: set[str] = set()
    combined: List[ModelInfo] = []

    # Dynamic entries first: those are the authoritative list for each
    # successfully-queried provider.
    for entry in result["models"]:
        if entry["name"] in seen_names:
            continue
        seen_names.add(entry["name"])
        combined.append(
            ModelInfo(
                name=entry["name"],
                label=entry["label"],
                provider=entry["provider"],
                api_key_env=entry["api_key_env"],
            )
        )

    # Static fallback: only for providers that were NOT queried (no key). If
    # a provider was queried but failed, we still include its static entries
    # so the user has something to click on once they fix the key.
    for name, entry in MODEL_CATALOG.items():
        if name in seen_names:
            continue
        env = entry["api_key_env"]
        provider_status = result["providers"].get(env)
        if env not in queried_envs or (provider_status and not provider_status.get("ok")):
            combined.append(
                ModelInfo(
                    name=name,
                    label=entry["label"],
                    provider=entry["provider"],
                    api_key_env=env,
                )
            )
            seen_names.add(name)

    provider_statuses: Dict[str, ProviderStatus] = {
        env: ProviderStatus(**status) for env, status in result["providers"].items()
    }

    return ModelsCatalogResponse(
        models=combined,
        defaults=dict(DEFAULT_MODELS_BY_ROLE),
        roles=list(ROLES),
        providers=provider_statuses,
    )
