"""Interceptor concurrency tests — two sessions must not cross-contaminate events."""

from __future__ import annotations

import asyncio

import pytest

from api.models.events import EventType
from api.services.event_service import get_event_service
from api.websockets.message_interceptor import (
    install_interceptor,
    set_session_context,
)


@pytest.mark.asyncio
async def test_concurrent_sessions_isolated():
    install_interceptor()

    from utils import message_utils  # type: ignore[import-not-found]

    event_service = get_event_service()
    q_a = await event_service.register_consumer("session-a")
    q_b = await event_service.register_consumer("session-b")

    async def run(session_id: str, payload: str):
        with set_session_context(session_id):
            message_utils.format_messages([payload], title="Scope Brief Generated")
            await asyncio.sleep(0.01)

    await asyncio.gather(run("session-a", "A"), run("session-b", "B"))
    await asyncio.sleep(0.05)

    events_a = []
    events_b = []
    while not q_a.empty():
        events_a.append(q_a.get_nowait())
    while not q_b.empty():
        events_b.append(q_b.get_nowait())

    assert len(events_a) == 1
    assert len(events_b) == 1
    assert events_a[0].event_type == EventType.SCOPE_BRIEF
    assert "A" in events_a[0].content
    assert "B" in events_b[0].content

    await event_service.unregister_consumer("session-a", q_a)
    await event_service.unregister_consumer("session-b", q_b)


@pytest.mark.asyncio
async def test_interceptor_no_session_context_is_noop():
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    # Should not raise and should not emit (no consumers registered).
    message_utils.format_messages(["hello"], title="Scope Brief Generated")
