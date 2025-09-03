# backend/app/core/structured_logger.py
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for production logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Build the base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "pdf-annotator-api",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }

        # Add any extra data that was passed to the logger
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "path"):
            log_entry["path"] = record.path

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_json_logging():
    """Configure JSON logging for production"""

    # Remove all existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    json_formatter = JSONFormatter()
    console_handler.setFormatter(json_formatter)

    # Set up root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


def log_request(
    correlation_id: str, method: str, path: str, status_code: int, duration_ms: float
):
    """Log HTTP request in structured format"""
    logger = get_logger("http.request")
    logger.info(
        "HTTP request completed",
        extra={
            "correlation_id": correlation_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "event_type": "http_request",
        },
    )


def log_business_event(event_name: str, correlation_id: str, **kwargs):
    """Log business events in structured format"""
    logger = get_logger("business.event")
    extra_data = {
        "correlation_id": correlation_id,
        "event_name": event_name,
        "event_type": "business",
        **kwargs,
    }
    logger.info(f"Business event: {event_name}", extra=extra_data)
