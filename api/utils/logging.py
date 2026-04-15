"""Logging configuration for the FastAPI app."""

from __future__ import annotations

import logging
import logging.config
from typing import Any, Dict


def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Install a process-wide logging configuration.

    Safe to call multiple times; idempotent thanks to ``disable_existing_loggers``.
    """
    if json_format:
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    else:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"default": {"format": fmt}},
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {"level": level, "handlers": ["default"]},
        "loggers": {
            "uvicorn": {"level": level, "handlers": ["default"], "propagate": False},
            "uvicorn.error": {"level": level, "handlers": ["default"], "propagate": False},
            "uvicorn.access": {"level": level, "handlers": ["default"], "propagate": False},
        },
    }

    logging.config.dictConfig(config)
