"""
LangGraph checkpointer manager using ``AsyncSqliteSaver``.

``AsyncSqliteSaver.from_conn_string`` returns an async context manager rather
than the instance itself, so we keep it open for the whole application lifespan
via an ``AsyncExitStack`` and close it on shutdown.
"""

from __future__ import annotations

import logging
from contextlib import AsyncExitStack
from typing import Optional

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from api.config import settings

logger = logging.getLogger(__name__)


# langgraph-checkpoint-sqlite 3.x calls ``self.conn.is_alive()`` inside
# ``AsyncSqliteSaver.setup``. That method only existed while ``aiosqlite.Connection``
# subclassed ``threading.Thread`` (≤0.19). Since 0.20 the class is a plain object,
# so we shim the method back: a connection is "alive" once its internal
# ``_connection`` handle has been initialized via ``await conn``.
if not hasattr(aiosqlite.Connection, "is_alive"):
    def _is_alive(self) -> bool:  # type: ignore[no-redef]
        return getattr(self, "_connection", None) is not None

    aiosqlite.Connection.is_alive = _is_alive  # type: ignore[attr-defined]


class CheckpointerManager:
    """Owns a long-lived ``AsyncSqliteSaver`` bound to the app lifespan."""

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.checkpoints_db
        self._checkpointer: Optional[AsyncSqliteSaver] = None
        self._stack: Optional[AsyncExitStack] = None

    async def initialize(self) -> None:
        """Open the ``AsyncSqliteSaver`` context and retain the live instance."""
        if self._checkpointer is not None:
            return

        self._stack = AsyncExitStack()
        await self._stack.__aenter__()
        self._checkpointer = await self._stack.enter_async_context(
            AsyncSqliteSaver.from_conn_string(self.db_path)
        )
        logger.info("Checkpointer initialized with database: %s", self.db_path)

    async def close(self) -> None:
        """Close the underlying saver and its connection pool."""
        if self._stack is None:
            return

        try:
            await self._stack.__aexit__(None, None, None)
        finally:
            self._stack = None
            self._checkpointer = None
            logger.info("Checkpointer closed")

    def get_checkpointer(self) -> AsyncSqliteSaver:
        if self._checkpointer is None:
            raise RuntimeError("Checkpointer not initialized. Call initialize() first.")
        return self._checkpointer


_checkpointer_manager: Optional[CheckpointerManager] = None


def get_checkpointer_manager() -> CheckpointerManager:
    """Return the process-wide ``CheckpointerManager`` singleton."""
    global _checkpointer_manager
    if _checkpointer_manager is None:
        _checkpointer_manager = CheckpointerManager()
    return _checkpointer_manager
