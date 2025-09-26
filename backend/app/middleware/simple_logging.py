# backend/app/middleware/simple_logging.py
import os
import time
import uuid
from contextvars import ContextVar

from app.core.structured_logger import log_request, setup_json_logging
from fastapi import Request

# Set up JSON logging if in production
if os.getenv("ENVIRONMENT") == "production":
    setup_json_logging()

# Context variable for correlation ID
correlation_id: ContextVar[str] = ContextVar("correlation_id")


def get_correlation_id() -> str:
    """Get current correlation ID"""
    return correlation_id.get("unknown")


async def log_requests(request: Request, call_next):
    


    # Generate or extract correlation ID
    corr_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())[:8]
    correlation_id.set(corr_id)

    start_time = time.time()

    # Development Pretty logs
    if os.getenv("ENVIRONMENT") != "production":
        print(f" [{corr_id}] {request.method} {request.url.path} - START")

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log the request (JSON in production, pretty in dev)
        log_request(
            corr_id,
            request.method,
            str(request.url.path),
            response.status_code,
            duration_ms,
        )

        # Development: Pretty logs
        if os.getenv("ENVIRONMENT") != "production":
            print(
                f" [{corr_id}] {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)"
            )

        # Add correlation ID to response headers
        response.headers["x-correlation-id"] = corr_id
        return response

    except Exception as e:
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 2)

        # Log the error
        log_request(corr_id, request.method, str(request.url.path), 500, duration_ms)

        # Development: Pretty logs
        if os.getenv("ENVIRONMENT") != "production":
            print(
                f" [{corr_id}] {request.method} {request.url.path} - ERROR: {str(e)} ({duration:.3f}s)"
            )

        raise
