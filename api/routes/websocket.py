"""
WebSocket endpoint for real-time research updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio

from api.websockets.connection_manager import get_connection_manager
from api.services.event_service import get_event_service
from api.models.events import WebSocketMessage


router = APIRouter()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
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

        # Listen for events and forward to WebSocket
        while True:
            try:
                # Wait for next event (with timeout to check connection)
                event = await asyncio.wait_for(event_queue.get(), timeout=1.0)

                # Convert event to WebSocket message
                message = WebSocketMessage(
                    type="event",
                    data={
                        "event_type": event.event_type,
                        "title": event.title,
                        "content": event.content,
                        "is_intermediate": event.is_intermediate,
                        "timestamp": event.timestamp,
                        "metadata": event.metadata,
                    },
                )

                await websocket.send_json(message.model_dump())

            except asyncio.TimeoutError:
                # Timeout is normal, just check if connection is alive
                try:
                    await websocket.send_json({"type": "ping", "data": {}})
                except Exception:
                    # Connection is dead
                    break

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected from session {session_id}")

    except Exception as e:
        print(f"[WS] Error in WebSocket handler: {e}")
        try:
            await websocket.send_json(
                {"type": "error", "data": {"message": str(e)}}
            )
        except Exception:
            pass

    finally:
        # Cleanup
        await event_service.unregister_consumer(session_id, event_queue)
        await connection_manager.disconnect(websocket, session_id)
