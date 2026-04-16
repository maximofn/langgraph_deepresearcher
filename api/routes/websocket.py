"""
WebSocket endpoint for real-time research updates.
"""

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.database.db import db_session_context
from api.models.events import WebSocketMessage
from api.services.event_service import get_event_service
from api.services.session_service import SessionService
from api.websockets.connection_manager import get_connection_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    client_id: Optional[str] = None,
):
    """
    WebSocket endpoint for real-time research updates.

    Flow:
    1. Client connects with session_id
    2. Register with ConnectionManager and EventService
    3. Listen for events from EventService queue
    4. Send events to client as WebSocket messages
    5. Handle client disconnection

    Args:
        websocket: WebSocket connection
        session_id: Unique session identifier
    """
    # Verify session ownership before accepting the connection
    async with db_session_context() as db:
        svc = SessionService(db)
        session = await svc.get_session(session_id)
        if session is None or session.client_id != client_id:
            await websocket.close(code=4403)
            return

    connection_manager = get_connection_manager()
    event_service = get_event_service()

    # Accept connection
    await connection_manager.connect(websocket, session_id)

    # Register as event consumer
    event_queue = await event_service.register_consumer(session_id)

    try:
        # Send connection confirmation
        await websocket.send_json(
            {"type": "connected", "data": {"session_id": session_id}}
        )

        # Replay any events already persisted for this session so late joiners
        # (new tab, page reload, API restart) see the full timeline — not only
        # what arrives after connection.
        history = await event_service.get_session_events(session_id)
        last_replayed_ts = 0.0
        for event in history:
            last_replayed_ts = max(last_replayed_ts, event.timestamp or 0.0)
            await websocket.send_json(
                WebSocketMessage(
                    type="event",
                    data={
                        "event_type": event.event_type,
                        "session_id": event.session_id,
                        "title": event.title,
                        "content": event.content,
                        "is_intermediate": event.is_intermediate,
                        "timestamp": event.timestamp,
                        "metadata": event.metadata,
                        "message_type": event.message_type,
                        "message_subtype": event.message_subtype,
                        "agent": event.agent,
                        "tool_name": event.tool_name,
                        "tool_args": event.tool_args,
                        "tool_call_id": event.tool_call_id,
                    },
                ).model_dump()
            )

        # Listen for events and forward to WebSocket
        while True:
            try:
                # Wait for next event (with timeout to check connection)
                event = await asyncio.wait_for(event_queue.get(), timeout=1.0)

                # Skip events already delivered via the replay snapshot.
                if (event.timestamp or 0.0) <= last_replayed_ts:
                    continue

                # Convert event to WebSocket message
                message = WebSocketMessage(
                    type="event",
                    data={
                        "event_type": event.event_type,
                        "session_id": event.session_id,
                        "title": event.title,
                        "content": event.content,
                        "is_intermediate": event.is_intermediate,
                        "timestamp": event.timestamp,
                        "metadata": event.metadata,
                        "message_type": event.message_type,
                        "message_subtype": event.message_subtype,
                        "agent": event.agent,
                        "tool_name": event.tool_name,
                        "tool_args": event.tool_args,
                        "tool_call_id": event.tool_call_id,
                    },
                )

                await websocket.send_json(message.model_dump())

            except asyncio.TimeoutError:
                # Timeout is normal; check the connection is alive via ping.
                try:
                    await websocket.send_json({"type": "ping", "data": {}})
                except Exception:
                    logger.info("WS connection closed during ping for %s", session_id)
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected from session %s", session_id)

    except Exception as e:
        logger.exception("WebSocket handler error for session %s", session_id)
        try:
            await websocket.send_json({"type": "error", "data": {"message": str(e)}})
        except Exception:
            logger.warning("Failed to notify client of WS error", exc_info=True)

    finally:
        # Cleanup
        await event_service.unregister_consumer(session_id, event_queue)
        await connection_manager.disconnect(websocket, session_id)
