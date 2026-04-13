"""Tests for /sessions CRUD endpoints."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_create_session_returns_websocket_url(app_client):
    resp = await app_client.post("/sessions/", json={"query": "What is RAG?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["session"]["initial_query"] == "What is RAG?"
    assert body["websocket_url"] == f"/ws/{body['session']['id']}"
    assert body["session"]["status"] == "created"


@pytest.mark.asyncio
async def test_get_session_not_found_returns_structured_error(app_client):
    resp = await app_client.get("/sessions/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "session_not_found"
    assert "does-not-exist" in body["message"]


@pytest.mark.asyncio
async def test_list_sessions_pagination(app_client):
    for i in range(3):
        await app_client.post("/sessions/", json={"query": f"q{i}"})

    resp = await app_client.get("/sessions/?limit=2&offset=0")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["sessions"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0


@pytest.mark.asyncio
async def test_get_session_messages_empty(app_client):
    created = await app_client.post("/sessions/", json={"query": "x"})
    sid = created.json()["session"]["id"]
    resp = await app_client.get(f"/sessions/{sid}/messages")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_validation_error_returns_structured_code(app_client):
    resp = await app_client.post("/sessions/", json={})
    assert resp.status_code == 422
    body = resp.json()
    assert body["code"] == "validation_error"
