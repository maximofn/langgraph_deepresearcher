"""
Utility module for managing progress bars with nested execution support.

This module provides a context manager that safely handles nested calls
to alive_progress, preventing the "Nested use of alive_progress is not yet supported" error.
"""

from contextvars import ContextVar
from contextlib import contextmanager
from alive_progress import alive_bar

# Context variable to track if a progress bar is currently active
# This works correctly with asyncio and threading
_progress_bar_active: ContextVar[bool] = ContextVar('progress_bar_active', default=False)


@contextmanager
def safe_progress_bar(**kwargs):
    """
    Safe context manager for progress bars that prevents nested execution.
    
    This function checks if a progress bar is already active in the current context.
    If one is active, it yields a no-op function. Otherwise, it creates a real
    progress bar using alive_bar.
    
    Args:
        **kwargs: Arguments to pass to alive_bar (monitor, stats, title, spinner, bar, etc.)
    
    Usage:
        with safe_progress_bar(monitor=False, stats=False, title="", spinner='dots_waves', bar='blocks') as bar:
            # Your code here
            bar()  # Call bar() to update progress (safe even if it's a no-op)
    
    Example:
        # This is safe even if called from within another safe_progress_bar context
        with safe_progress_bar(monitor=False, stats=False) as bar:
            result = some_async_operation()
            bar()
    """
    
    # Check if a progress bar is already active in this context
    is_nested = _progress_bar_active.get()
    
    if is_nested:
        # We're in a nested call - yield a no-op function
        # This function does nothing when called, preventing errors
        yield lambda: None
    else:
        # No active progress bar - create a real one
        # Set the context variable to True to mark this context as having an active bar
        token = _progress_bar_active.set(True)
        try:
            # Create and use the real progress bar
            with alive_bar(**kwargs) as bar:
                yield bar
        finally:
            # Reset the context variable when we're done
            # This allows subsequent non-nested calls to create progress bars
            _progress_bar_active.reset(token)

