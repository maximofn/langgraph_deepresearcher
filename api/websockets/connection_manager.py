"""
WebSocket connection manager for handling multiple concurrent connections.
"""

from fastapi import WebSocket
from typing import Dict, Set, Optional
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for multiple sessions"""

    def __init__(self):
        # session_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and register a WebSocket connection"""
        await websocket.accept()

        async with self._lock:
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)

        print(f"[WS] Client connected to session {session_id}")

    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection"""
        async with self._lock:
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]

        print(f"[WS] Client disconnected from session {session_id}")

    async def send_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"[WS] Error sending message: {e}")

    async def broadcast_to_session(self, message: dict, session_id: str):
        """Broadcast message to all connections in a session"""
        async with self._lock:
            if session_id in self.active_connections:
                websockets = list(self.active_connections[session_id])
            else:
                websockets = []

        # Send outside lock to avoid blocking
        for websocket in websockets:
            await self.send_message(message, websocket)

    def get_session_connection_count(self, session_id: str) -> int:
        """Get number of active connections for a session"""
        return len(self.active_connections.get(session_id, set()))


# Global instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
