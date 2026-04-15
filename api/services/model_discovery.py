"""
Live model discovery across LLM providers.

Given a map of user API keys, query each provider's ``/v1/models`` (or
equivalent) endpoint in parallel, filter out non-chat models by heuristic,
and return a normalized unified list. Each returned ``ModelEntry`` carries
enough metadata (``provider``, ``api_key_env``, ``base_url``) for
``model_catalog.resolve_model_config`` to build the runtime model later.

API keys received here are **never logged** and only used to set auth
headers on outbound HTTP calls. Errors caught from providers are truncated
and anonymized before being returned.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, TypedDict

import httpx

from api.utils.paths import ensure_src_on_path

ensure_src_on_path()
from LLM_models.model_catalog import (  # type: ignore[import-not-found]
    ANTHROPIC_BASE_URL,
    CEREBRAS_BASE_URL,
    GITHUB_BASE_URL,
    KIMI_BASE_URL,
    OPENAI_BASE_URL,
    PROVIDER_ANTHROPIC,
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
)

logger = logging.getLogger(__name__)

# Per-provider timeout: 3s to connect, 8s total. Matches the plan's budget.
_TIMEOUT = httpx.Timeout(8.0, connect=3.0)

GEMINI_BASE_URL_LIST = "https://generativelanguage.googleapis.com/v1beta/models"
GITHUB_MODELS_CATALOG_URL = "https://models.github.ai/catalog/models"


class ModelEntry(TypedDict):
    name: str
    label: str
    provider: str
    api_key_env: str
    base_url: str
    default_max_tokens: Optional[int]
    source: str  # "dynamic" | "static"


class ProviderStatus(TypedDict, total=False):
    ok: bool
    count: int
    error: str


class DiscoveryResult(TypedDict):
    models: List[ModelEntry]
    providers: Dict[str, ProviderStatus]


Fetcher = Callable[[httpx.AsyncClient, str], Awaitable[List[ModelEntry]]]


# ---------------------------------------------------------------------------
# Per-provider filters
# ---------------------------------------------------------------------------

# OpenAI returns everything (embeddings, whisper, tts, dall-e, moderation,
# realtime, transcribe, etc.). We keep only chat completion models by an
# allowlist of id prefixes and a blocklist of substrings.
_OPENAI_PREFIXES = ("gpt", "o1", "o3", "o4", "chatgpt")
_OPENAI_BLOCKLIST = (
    "embed",
    "whisper",
    "tts",
    "dall",
    "moderation",
    "davinci",
    "babbage",
    "ada",
    "realtime",
    "audio",
    "search",
    "transcribe",
    "computer-use",
    "image",
)


def _is_openai_chat(model_id: str) -> bool:
    lower = model_id.lower()
    if any(bad in lower for bad in _OPENAI_BLOCKLIST):
        return False
    return any(lower.startswith(p) for p in _OPENAI_PREFIXES)


def _humanize(provider_label: str, model_id: str) -> str:
    return f"{provider_label} {model_id}"


# ---------------------------------------------------------------------------
# Provider fetchers — each returns normalized ModelEntry list or raises
# ---------------------------------------------------------------------------


async def _fetch_openai(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    resp = await client.get(
        f"{OPENAI_BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    entries: List[ModelEntry] = []
    for item in data:
        model_id = item.get("id", "")
        if not _is_openai_chat(model_id):
            continue
        entries.append(
            {
                "name": model_id,
                "label": _humanize("OpenAI", model_id),
                "provider": PROVIDER_OPENAI,
                "api_key_env": "OPENAI_API_KEY",
                "base_url": OPENAI_BASE_URL,
                "default_max_tokens": None,
                "source": "dynamic",
            }
        )
    return entries


async def _fetch_anthropic(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    resp = await client.get(
        f"{ANTHROPIC_BASE_URL}/models",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])
    entries: List[ModelEntry] = []
    for item in data:
        model_id = item.get("id", "")
        if not model_id.startswith("claude-"):
            continue
        label = item.get("display_name") or _humanize("Anthropic", model_id)
        entries.append(
            {
                "name": model_id,
                "label": label,
                "provider": PROVIDER_ANTHROPIC,
                "api_key_env": "ANTHROPIC_API_KEY",
                "base_url": ANTHROPIC_BASE_URL,
                "default_max_tokens": 4096,
                "source": "dynamic",
            }
        )
    return entries


_GEMINI_BLOCKLIST = ("embedding", "aqa", "text-bison")


async def _fetch_gemini(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    resp = await client.get(
        GEMINI_BASE_URL_LIST,
        params={"key": api_key},
    )
    resp.raise_for_status()
    data = resp.json().get("models", [])
    entries: List[ModelEntry] = []
    for item in data:
        raw_name: str = item.get("name", "")
        if not raw_name:
            continue
        name = raw_name.removeprefix("models/")
        if any(bad in name.lower() for bad in _GEMINI_BLOCKLIST):
            continue
        methods = item.get("supportedGenerationMethods", []) or []
        if "generateContent" not in methods:
            continue
        label = item.get("displayName") or _humanize("Google", name)
        entries.append(
            {
                "name": name,
                "label": label,
                "provider": PROVIDER_GEMINI,
                "api_key_env": "GEMINI_API_KEY",
                "base_url": "",
                "default_max_tokens": None,
                "source": "dynamic",
            }
        )
    return entries


async def _fetch_openai_compat(
    client: httpx.AsyncClient,
    api_key: str,
    base_url: str,
    label_prefix: str,
    api_key_env: str,
) -> List[ModelEntry]:
    """Shared OpenAI-compatible /v1/models call used by Cerebras and Kimi."""
    resp = await client.get(
        f"{base_url}/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    resp.raise_for_status()
    payload = resp.json()
    data = payload.get("data", payload if isinstance(payload, list) else [])
    entries: List[ModelEntry] = []
    for item in data:
        if isinstance(item, str):
            model_id = item
        else:
            model_id = item.get("id") or item.get("name") or ""
        if not model_id:
            continue
        entries.append(
            {
                "name": model_id,
                "label": _humanize(label_prefix, model_id),
                "provider": PROVIDER_OPENAI,  # OpenAI-compatible clients
                "api_key_env": api_key_env,
                "base_url": base_url,
                "default_max_tokens": None,
                "source": "dynamic",
            }
        )
    return entries


async def _fetch_cerebras(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    return await _fetch_openai_compat(
        client,
        api_key,
        base_url=CEREBRAS_BASE_URL,
        label_prefix="Cerebras",
        api_key_env="CEREBRAS_API_KEY",
    )


async def _fetch_kimi(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    return await _fetch_openai_compat(
        client,
        api_key,
        base_url=KIMI_BASE_URL,
        label_prefix="Moonshot",
        api_key_env="KIMI_K2_API_KEY",
    )


async def _fetch_github(client: httpx.AsyncClient, api_key: str) -> List[ModelEntry]:
    resp = await client.get(
        GITHUB_MODELS_CATALOG_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/vnd.github+json",
        },
    )
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list):
        data = data.get("models", [])
    entries: List[ModelEntry] = []
    for item in data:
        capabilities = item.get("capabilities") or []
        if "chat-completion" not in capabilities and "chat" not in capabilities:
            continue
        model_id = item.get("id") or item.get("name") or ""
        if not model_id:
            continue
        label = item.get("display_name") or item.get("friendly_name") or _humanize("GitHub", model_id)
        entries.append(
            {
                "name": model_id,
                "label": label,
                "provider": PROVIDER_OPENAI,  # GitHub Models speaks OpenAI
                "api_key_env": "GITHUB_API_KEY",
                "base_url": GITHUB_BASE_URL,
                "default_max_tokens": None,
                "source": "dynamic",
            }
        )
    return entries


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


_PROVIDERS: Dict[str, Fetcher] = {
    "OPENAI_API_KEY": _fetch_openai,
    "ANTHROPIC_API_KEY": _fetch_anthropic,
    "GEMINI_API_KEY": _fetch_gemini,
    "CEREBRAS_API_KEY": _fetch_cerebras,
    "KIMI_K2_API_KEY": _fetch_kimi,
    "GITHUB_API_KEY": _fetch_github,
}


async def discover_models(api_keys: Dict[str, str]) -> DiscoveryResult:
    """Query every provider with a matching API key in parallel.

    Returns a list of normalized ``ModelEntry`` and a per-provider status map.
    A provider that raised is reported with ``ok: False`` and a truncated
    error message, and its entries are simply absent from the ``models`` list.
    """
    envs = [env for env in _PROVIDERS if api_keys.get(env)]
    if not envs:
        return {"models": [], "providers": {}}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        coros = [_PROVIDERS[env](client, api_keys[env]) for env in envs]
        results = await asyncio.gather(*coros, return_exceptions=True)

    merged: List[ModelEntry] = []
    providers: Dict[str, ProviderStatus] = {}
    for env, result in zip(envs, results):
        if isinstance(result, Exception):
            providers[env] = {"ok": False, "error": _format_error(result)}
            # Intentionally do NOT log the api_key. The logger line carries
            # only the env name and the error class.
            logger.warning(
                "Model discovery failed for %s: %s",
                env,
                type(result).__name__,
            )
            continue
        providers[env] = {"ok": True, "count": len(result)}
        merged.extend(result)

    # Sort so the UI shows a deterministic order across runs.
    merged.sort(key=lambda e: (e["api_key_env"], e["name"]))

    return {"models": merged, "providers": providers}


def _format_error(exc: BaseException) -> str:
    msg: str
    if isinstance(exc, httpx.HTTPStatusError):
        msg = f"HTTP {exc.response.status_code}"
    elif isinstance(exc, httpx.TimeoutException):
        msg = "Timed out"
    elif isinstance(exc, httpx.RequestError):
        msg = f"Request error: {type(exc).__name__}"
    else:
        msg = str(exc) or type(exc).__name__
    return msg[:200]
