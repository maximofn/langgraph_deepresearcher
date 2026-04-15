"""Catalog endpoint for selectable LLM models.

The frontend settings modal calls ``GET /models`` once at startup to render
the per-role selectors. Models whose API key is not present in the backend
environment are filtered out so the user only sees options that will work.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from api.utils.paths import ensure_src_on_path

ensure_src_on_path()
from LLM_models.model_catalog import (  # type: ignore[import-not-found]
    DEFAULT_MODELS_BY_ROLE,
    MODEL_CATALOG,
    ROLES,
)


router = APIRouter(prefix="/models", tags=["models"])


class ModelInfo(BaseModel):
    name: str
    label: str
    provider: str
    api_key_env: str


class ModelsCatalogResponse(BaseModel):
    models: List[ModelInfo]
    defaults: Dict[str, str]
    roles: List[str]


@router.get("/", response_model=ModelsCatalogResponse)
async def get_models() -> ModelsCatalogResponse:
    # Always expose the full catalog; the frontend decides which models are
    # usable based on the API keys the user has entered in settings.
    models: List[ModelInfo] = [
        ModelInfo(
            name=name,
            label=entry["label"],
            provider=entry["provider"],
            api_key_env=entry["api_key_env"],
        )
        for name, entry in MODEL_CATALOG.items()
    ]

    return ModelsCatalogResponse(
        models=models,
        defaults=dict(DEFAULT_MODELS_BY_ROLE),
        roles=list(ROLES),
    )
