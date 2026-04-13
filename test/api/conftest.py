"""Shared fixtures for API tests.

Provides an in-memory SQLite DB, a stubbed LangGraph ``writer_builder``,
and an async httpx client wired through the ASGI app with full lifespan.
"""

from __future__ import annotations

import os
from typing import Any, AsyncIterator, Dict, List
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage


# Use a file-based sqlite DB per test session to keep async driver happy.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ENABLE_RATE_LIMIT", "false")
os.environ.setdefault("ENABLE_METRICS", "false")
os.environ.setdefault("LOG_LEVEL", "WARNING")


class FakeCompiledAgent:
    """Deterministic stand-in for a compiled LangGraph agent."""

    def __init__(self, responses: List[Dict[str, Any]]):
        # Share the same list across all compiles so sequential invokes advance it.
        self._responses = responses
        self.calls: List[Dict[str, Any]] = []

    async def ainvoke(self, state, config=None):
        self.calls.append({"state": state, "config": config})
        if not self._responses:
            return {"messages": [], "research_brief": "brief", "final_report": "report"}
        return self._responses.pop(0)


class FakeWriterBuilder:
    """Stand-in for ``writer_builder`` that returns a ``FakeCompiledAgent``."""

    def __init__(self, responses: List[Dict[str, Any]] | None = None):
        self.responses = responses or []
        self.last_compiled: FakeCompiledAgent | None = None

    def compile(self, checkpointer=None):  # noqa: D401
        self.last_compiled = FakeCompiledAgent(self.responses)
        return self.last_compiled


@pytest.fixture
def fake_writer_builder(monkeypatch):
    """Patch ``_get_writer_builder`` to return a programmable fake."""
    from api.services import research_service

    fake = FakeWriterBuilder(
        responses=[
            {
                "messages": [AIMessage(content="final answer")],
                "research_brief": "test brief",
                "final_report": "# Report\n\nBody",
            }
        ]
    )
    monkeypatch.setattr(research_service, "_get_writer_builder", lambda: fake)
    return fake


@pytest.fixture
def fake_writer_builder_clarify(monkeypatch):
    """Fake that first asks for clarification, then returns a report."""
    from api.services import research_service

    fake = FakeWriterBuilder(
        responses=[
            {
                "messages": [AIMessage(content="Can you clarify scope?")],
                "research_brief": None,
                "final_report": None,
            },
            {
                "messages": [AIMessage(content="done")],
                "research_brief": "clarified brief",
                "final_report": "# Report",
            },
        ]
    )
    monkeypatch.setattr(research_service, "_get_writer_builder", lambda: fake)
    return fake


@pytest_asyncio.fixture
async def app_client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client with full lifespan (startup/shutdown)."""
    from api.main import app

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client


@pytest.fixture
def stub_checkpointer(monkeypatch):
    """Replace the real checkpointer with a no-op so tests don't touch SQLite files."""
    from api.database import checkpointer as checkpointer_module

    class _NoopManager:
        async def initialize(self):
            return None

        async def close(self):
            return None

        def get_checkpointer(self):
            return None

    manager = _NoopManager()
    monkeypatch.setattr(
        checkpointer_module, "get_checkpointer_manager", lambda: manager
    )
    # Also patch the already-imported reference in research_service.
    from api.services import research_service

    monkeypatch.setattr(
        research_service, "get_checkpointer_manager", lambda: manager
    )
