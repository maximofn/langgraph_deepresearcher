"""
LangGraph checkpointer manager using AsyncSqliteSaver.
Provides persistent state management for multi-user sessions.
"""

from typing import Optional
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from api.config import settings


class CheckpointerManager:
    """Manages LangGraph AsyncSqliteSaver instances"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.checkpoints_db
        self._checkpointer: Optional[AsyncSqliteSaver] = None

    async def initialize(self):
        """Initialize the checkpointer"""
        self._checkpointer = AsyncSqliteSaver.from_conn_string(self.db_path)
        # AsyncSqliteSaver handles setup automatically
        print(f"[CHECKPOINTER] Initialized with database: {self.db_path}")

    async def close(self):
        """Close the checkpointer"""
        if self._checkpointer:
            # AsyncSqliteSaver doesn't have explicit close in current version
            # But we set it to None to indicate it's closed
            self._checkpointer = None
            print("[CHECKPOINTER] Closed")

    def get_checkpointer(self) -> AsyncSqliteSaver:
        """Get the checkpointer instance"""
        if not self._checkpointer:
            raise RuntimeError("Checkpointer not initialized. Call initialize() first.")
        return self._checkpointer


# Global instance
_checkpointer_manager: Optional[CheckpointerManager] = None


def get_checkpointer_manager() -> CheckpointerManager:
    """Get the global checkpointer manager"""
    global _checkpointer_manager
    if _checkpointer_manager is None:
        _checkpointer_manager = CheckpointerManager()
    return _checkpointer_manager
