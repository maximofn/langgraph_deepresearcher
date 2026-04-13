"""Error handling / standard response tests."""

from __future__ import annotations

import pytest

from api.utils.exceptions import APIException, ErrorResponse


def test_error_response_schema():
    err = ErrorResponse(code="x", message="oops")
    assert err.model_dump() == {"code": "x", "message": "oops", "details": None}


def test_api_exception_carries_details():
    exc = APIException("boom", details={"field": "q"})
    assert exc.message == "boom"
    assert exc.details == {"field": "q"}
    assert exc.code == "api_error"
    assert exc.status_code == 500


@pytest.mark.asyncio
async def test_api_exception_returns_structured_response(app_client):
    """Our custom SessionNotFoundError maps to 404 + structured body."""
    resp = await app_client.get("/sessions/nonexistent-id")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "session_not_found"
    assert "message" in body
    assert "details" in body
