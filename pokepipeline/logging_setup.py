"""Logging configuration with JSON formatting and contextual logging."""

import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "run_id": getattr(record, "run_id", "unknown"),
            "component": getattr(record, "component", "unknown"),
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_data["extra"] = record.extra_fields

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ContextualAdapter(logging.LoggerAdapter):
    """Logger adapter that adds contextual information to log records."""

    def __init__(
        self,
        logger: logging.Logger,
        component: str,
        run_id: Optional[str] = None,
    ):
        """Initialize the contextual adapter.

        Args:
            logger: Base logger instance
            component: Name of the component logging
            run_id: Optional run ID for correlation
        """
        super().__init__(logger, {"component": component, "run_id": run_id})

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the logging message and kwargs.

        Args:
            msg: Log message
            kwargs: Logging kwargs

        Returns:
            Processed message and kwargs
        """
        extra = kwargs.get("extra", {})
        extra["component"] = self.extra["component"]
        extra["run_id"] = self.extra["run_id"]

        # Allow passing additional extra fields
        if "extra_fields" not in extra:
            extra["extra_fields"] = {}

        kwargs["extra"] = extra
        return msg, kwargs


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide logging with JSON formatting.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers = []

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(JSONFormatter())

    root_logger.addHandler(console_handler)


def get_logger(component: str, run_id: Optional[str] = None) -> ContextualAdapter:
    """Get a logger adapter with contextual information.

    Args:
        component: Name of the component (e.g., 'extract', 'transform', 'load')
        run_id: Optional run ID for correlation. If not provided, generates a new UUID.

    Returns:
        ContextualAdapter configured with component and run_id
    """
    if run_id is None:
        run_id = str(uuid.uuid4())

    base_logger = logging.getLogger(__name__)
    return ContextualAdapter(base_logger, component=component, run_id=run_id)

