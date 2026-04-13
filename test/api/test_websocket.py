"""WebSocket endpoint smoke test."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.models.events import EventType
from api.services.event_service import get_event_service


def test_websocket_receives_events():
    client = TestClient(app)
    with client.websocket_connect("/ws/ws-test-session") as ws:
        first = ws.receive_json()
        assert first["type"] == "connected"
        assert first["data"]["session_id"] == "ws-test-session"

        import asyncio

        async def _emit():
            await get_event_service().emit(
                session_id="ws-test-session",
                event_type=EventType.SCOPE_BRIEF,
                title="Scope Brief",
                content="hello",
                is_intermediate=False,
            )

        asyncio.get_event_loop().run_until_complete(_emit())

        # Read messages until we find our event (pings may precede it).
        for _ in range(10):
            msg = ws.receive_json()
            if msg["type"] == "event":
                assert msg["data"]["content"] == "hello"
                return
        pytest.fail("Did not receive emitted event within 10 messages")
