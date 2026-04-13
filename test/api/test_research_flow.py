"""End-to-end research flow tests with a mocked writer_builder."""

from __future__ import annotations

import asyncio

import pytest

from api.database.db import db_session_context
from api.database.models import SessionStatus
from api.services.session_service import SessionService


async def _wait_for_status(session_id: str, target: SessionStatus, timeout: float = 3.0):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        async with db_session_context() as db:
            session = await SessionService(db).get_session(session_id)
            if session and session.status == target:
                return session
        await asyncio.sleep(0.05)
    raise AssertionError(f"session {session_id} never reached {target}")


@pytest.mark.asyncio
async def test_start_research_completes(
    app_client, fake_writer_builder, stub_checkpointer
):
    created = await app_client.post("/sessions/", json={"query": "topic"})
    sid = created.json()["session"]["id"]

    resp = await app_client.post(f"/sessions/{sid}/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "started"

    session = await _wait_for_status(sid, SessionStatus.COMPLETED)
    assert session.research_brief == "test brief"
    assert session.final_report.startswith("# Report")

    messages = await app_client.get(f"/sessions/{sid}/messages")
    roles = [m["role"] for m in messages.json()]
    assert "user" in roles
    assert "system" in roles
    assert "assistant" in roles


@pytest.mark.asyncio
async def test_start_research_clarification_flow(
    app_client, fake_writer_builder_clarify, stub_checkpointer
):
    created = await app_client.post("/sessions/", json={"query": "ambiguous topic"})
    sid = created.json()["session"]["id"]

    await app_client.post(f"/sessions/{sid}/start")
    await _wait_for_status(sid, SessionStatus.CLARIFICATION_NEEDED)

    resp = await app_client.post(
        f"/sessions/{sid}/clarify", json={"clarification": "focus on X"}
    )
    assert resp.status_code == 200

    session = await _wait_for_status(sid, SessionStatus.COMPLETED)
    assert session.research_brief == "clarified brief"


@pytest.mark.asyncio
async def test_start_research_wrong_state_rejected(
    app_client, fake_writer_builder, stub_checkpointer
):
    created = await app_client.post("/sessions/", json={"query": "x"})
    sid = created.json()["session"]["id"]

    first = await app_client.post(f"/sessions/{sid}/start")
    assert first.status_code == 200

    second = await app_client.post(f"/sessions/{sid}/start")
    assert second.status_code == 400
    assert second.json()["code"] == "invalid_session_state"


@pytest.mark.asyncio
async def test_clarify_when_not_needed_rejected(app_client):
    created = await app_client.post("/sessions/", json={"query": "x"})
    sid = created.json()["session"]["id"]

    resp = await app_client.post(f"/sessions/{sid}/clarify", json={"clarification": "y"})
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_session_state"
