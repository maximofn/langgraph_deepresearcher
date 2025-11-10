"""
Utility module for managing progress bars with nested execution support.

This module provides a context manager that safely handles nested calls
to alive_progress, preventing the "Nested use of alive_progress is not yet supported" error.

It uses a threading Lock and a global flag to coordinate access across all tasks (both sync and async),
ensuring that only one progress bar is active at any given time, even when multiple tasks run in parallel.
"""

import threading
from contextlib import contextmanager
from alive_progress import alive_bar

# Global lock to coordinate progress bar access across all tasks
# Using threading.Lock instead of asyncio.Lock because:
# 1. It works in both synchronous and asynchronous contexts
# 2. We use try_acquire (non-blocking) so we never block the event loop
_progress_bar_lock = threading.Lock()

# Global flag to track if any progress bar is currently active
# This is protected by _progress_bar_lock
_progress_bar_active = False


@contextmanager
def safe_progress_bar(**kwargs):
    """
    Safe context manager for progress bars that prevents nested/parallel execution.
    
    This function uses a global lock to ensure only one progress bar is active at a time,
    even across multiple parallel async tasks. If a progress bar is already active
    (either nested or in a parallel task), it yields a no-op function instead.
    
    How it works:
    1. Tries to acquire a global lock (non-blocking)
    2. If successful, creates a real progress bar
    3. If lock is already held, returns a no-op function
    4. This prevents the "Nested use of alive_progress is not yet supported" error
    
    Args:
        **kwargs: Arguments to pass to alive_bar (monitor, stats, title, spinner, bar, etc.)
    
    Usage:
        with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            # Your code here
            bar()  # Call bar() to update progress (safe even if it's a no-op)
    
    Example:
        # This is safe even if called from parallel tasks or nested contexts
        with safe_progress_bar(monitor=False, stats=False) as bar:
            result = some_operation()
            bar()
    
    Note:
        Works in both synchronous and asynchronous contexts.
        Uses non-blocking lock acquisition to avoid blocking the event loop.
    """
    
    global _progress_bar_active
    
    # Try to acquire the lock without blocking
    # If we can't get it immediately, another progress bar is active
    acquired = _progress_bar_lock.acquire(blocking=False)
    
    if not acquired:
        # Another progress bar is active (nested or parallel)
        # Yield a no-op function that's safe to call
        yield lambda: None
    else:
        # We got the lock - we can create a real progress bar
        _progress_bar_active = True
        try:
            # Create and use the real progress bar
            with alive_bar(**kwargs) as bar:
                yield bar
        finally:
            # Clean up: mark progress bar as inactive and release the lock
            _progress_bar_active = False
            _progress_bar_lock.release()

