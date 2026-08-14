"""Shared rate limiter instance.

Lives in its own module rather than in ``main.py`` so route modules can import
it and decorate individual endpoints. Limits are applied **per endpoint**, never
as ``default_limits`` on the Limiter: a global default would also throttle the
polling GETs the web UI uses to refresh the session list, which shows up as
"failed to load sessions" in the browser.
"""

from __future__ import annotations

import logging

from api.config import settings

logger = logging.getLogger(__name__)

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    SLOWAPI_AVAILABLE = True
    limiter = Limiter(key_func=get_remote_address, enabled=settings.enable_rate_limit)
except ImportError:  # pragma: no cover - depends on the deployment image
    SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not installed; rate limiting disabled")

    class _NoopLimiter:
        """Stand-in so the ``@limiter.limit(...)`` decorators stay valid."""

        enabled = False

        def limit(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    limiter = _NoopLimiter()  # type: ignore[assignment]
