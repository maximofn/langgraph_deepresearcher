"""Interceptor concurrency + per-message emission tests."""

from __future__ import annotations

import asyncio

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from api.models.events import AgentName, EventType, MessageKind
from api.services.event_service import get_event_service
from api.websockets.message_interceptor import (
    install_interceptor,
    set_session_context,
)


async def _drain(queue) -> list:
    events = []
    while not queue.empty():
        events.append(queue.get_nowait())
    return events


@pytest.mark.asyncio
async def test_concurrent_sessions_isolated():
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    event_service = get_event_service()
    q_a = await event_service.register_consumer("session-a")
    q_b = await event_service.register_consumer("session-b")

    async def run(session_id: str, payload: str):
        with set_session_context(session_id):
            message_utils.format_messages(
                [AIMessage(content=payload)],
                title="Scope Brief Generated",
            )
            await asyncio.sleep(0.01)

    await asyncio.gather(run("session-a", "A"), run("session-b", "B"))
    await asyncio.sleep(0.05)

    ev_a = await _drain(q_a)
    ev_b = await _drain(q_b)

    assert len(ev_a) == 1
    assert len(ev_b) == 1
    assert ev_a[0].event_type == EventType.SCOPE_BRIEF
    assert ev_a[0].message_type == MessageKind.AI
    assert ev_a[0].agent == AgentName.SCOPE
    assert "A" in ev_a[0].content
    assert "B" in ev_b[0].content

    await event_service.unregister_consumer("session-a", q_a)
    await event_service.unregister_consumer("session-b", q_b)


@pytest.mark.asyncio
async def test_interceptor_emits_per_message():
    """Two messages in one call → two events with distinct message_type."""
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    event_service = get_event_service()
    q = await event_service.register_consumer("per-msg")

    with set_session_context("per-msg"):
        message_utils.format_messages(
            [
                HumanMessage(content="query text"),
                AIMessage(content="ai reply"),
            ],
            title="Scope Agent",
            msg_subtype="RealHumanMessage",
        )
        await asyncio.sleep(0.05)

    events = await _drain(q)
    # Real human message + AI reply = 2 events
    kinds = [e.message_type for e in events]
    assert MessageKind.HUMAN in kinds
    assert MessageKind.AI in kinds

    await event_service.unregister_consumer("per-msg", q)


@pytest.mark.asyncio
async def test_interceptor_extracts_anthropic_tool_calls():
    """An AIMessage with Anthropic-style tool_use content emits a TOOL_CALL event."""
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    event_service = get_event_service()
    q = await event_service.register_consumer("tc")

    ai = AIMessage(
        content=[
            {"type": "text", "text": "calling search"},
            {
                "type": "tool_use",
                "id": "toolu_1",
                "name": "tavily_search",
                "input": {"query": "madrid cafes"},
            },
        ]
    )

    with set_session_context("tc"):
        message_utils.format_messages([ai], title="Researcher Agent")
        await asyncio.sleep(0.05)

    events = await _drain(q)
    tool_events = [e for e in events if e.message_type == MessageKind.TOOL_CALL]
    assert len(tool_events) == 1
    tc = tool_events[0]
    assert tc.tool_name == "tavily_search"
    assert tc.tool_args == {"query": "madrid cafes"}
    assert tc.tool_call_id == "toolu_1"
    assert tc.agent == AgentName.RESEARCH

    await event_service.unregister_consumer("tc", q)


@pytest.mark.asyncio
async def test_interceptor_tool_output_event():
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    event_service = get_event_service()
    q = await event_service.register_consumer("to")

    tm = ToolMessage(content="result body", tool_call_id="toolu_1", name="tavily_search")

    with set_session_context("to"):
        message_utils.format_messages([tm], title="Researcher Tool Output")
        await asyncio.sleep(0.05)

    events = await _drain(q)
    assert len(events) == 1
    ev = events[0]
    assert ev.message_type == MessageKind.TOOL
    assert ev.tool_name == "tavily_search"
    assert ev.tool_call_id == "toolu_1"
    assert "result body" in ev.content

    await event_service.unregister_consumer("to", q)


@pytest.mark.asyncio
async def test_interceptor_no_session_context_is_noop():
    install_interceptor()
    from utils import message_utils  # type: ignore[import-not-found]

    # Should not raise; no consumers registered so nothing is emitted.
    message_utils.format_messages(
        [AIMessage(content="hello")], title="Scope Brief Generated"
    )
