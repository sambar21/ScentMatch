import time
from contextlib import asynccontextmanager
from typing import Annotated

import psutil
from app.core.config import settings
from app.core.database import check_db_connection, get_db
from app.core.error_handlers import (api_exception_handler,
                                     database_exception_handler,
                                     generic_exception_handler,
                                     validation_exception_handler)
from app.core.exceptions import BaseAPIException
from app.core.structured_logger import log_business_event
from app.core.validation import (validate_email,  # Fixed this line
                                 validate_filename)
from app.middleware.security_middleware import (request_size_middleware,
                                                security_middleware)
from app.middleware.simple_logging import get_correlation_id, log_requests
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print(f" Starting {settings.app_name} v{settings.version}")
    print(" API Documentation available at: http://localhost:8000/docs")

    # Test database connection on startup
    db_healthy = await check_db_connection()
    if db_healthy:
        print(" Database connection: Healthy")
    else:
        print(" Database connection: Failed")
        print("  Application starting without database connectivity")

    yield  # Application is running

    # Shutdown
    print(f" Shutting down {settings.app_name}")

    # Import here to avoid circular imports
    from app.core.database import close_db

    await close_db()
    print(" Database connections closed")


# Create FastAPI application instance with lifespan
app = FastAPI(
    title=settings.app_name,
    description="PDF annotation platform with real-time collaboration",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,  # Add lifespan parameter here
    # API documentation settings
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
)
app.middleware("http")(security_middleware)
app.middleware("http")(request_size_middleware)
app.middleware("http")(log_requests)
app.add_exception_handler(BaseAPIException, api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.middleware("http")(log_requests)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.version,
        "status": "running",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    corr_id = get_correlation_id()

    # Log business event
    log_business_event("health_check_requested", corr_id, endpoint="/health")

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
        "correlation_id": corr_id,
    }


@app.get("/health/db")
async def health_check_db():
    corr_id = get_correlation_id()

    is_healthy = await check_db_connection()

    # Log business event with database status
    log_business_event(
        "database_health_check",
        corr_id,
        database_status="healthy" if is_healthy else "unhealthy",
        endpoint="/health/db",
    )

    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "connected" if is_healthy else "disconnected",
        "service": settings.app_name,
        "correlation_id": corr_id,
    }


@app.get("/health/detailed")
async def detailed_health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        # Test database session
        result = await db.execute(text("SELECT 1 as test"))
        test_result = result.fetchone()

        db_status = "healthy" if test_result and test_result.test == 1 else "unhealthy"

        return {
            "status": "healthy" if db_status == "healthy" else "unhealthy",
            "checks": {
                "database_connection": db_status,
                "database_session": "healthy",
                "application": "healthy",
            },
            "service": settings.app_name,
            "version": settings.version,
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "checks": {
                "database_connection": "unhealthy",
                "database_session": "unhealthy",
                "application": "healthy",
            },
            "error": str(e),
            "service": settings.app_name,
            "version": settings.version,
        }


# Include API routers  (add these in future phases)
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info",
    )


@app.get("/health/system")
async def system_health_check():
    """Comprehensive system health check"""
    correlation_id = get_correlation_id()

    start_time = time.time()

    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # Check database
    db_healthy = await check_db_connection()

    # Determine overall health
    health_issues = []

    if cpu_percent > 80:
        health_issues.append("High CPU usage")
    if memory.percent > 85:
        health_issues.append("High memory usage")
    if disk.percent > 90:
        health_issues.append("Low disk space")
    if not db_healthy:
        health_issues.append("Database connection failed")

    overall_status = "healthy" if not health_issues else "degraded"

    response_time = (time.time() - start_time) * 1000

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "response_time_ms": round(response_time, 2),
        "checks": {
            "database": "healthy" if db_healthy else "unhealthy",
            "cpu_usage_percent": round(cpu_percent, 1),
            "memory_usage_percent": round(memory.percent, 1),
            "disk_usage_percent": round(disk.percent, 1),
        },
        "issues": health_issues,
        "service": settings.app_name,
        "version": settings.version,
        "correlation_id": correlation_id,
    }


@app.post("/test/validation")
async def test_validation(email: str, filename: str):
    """Test input validation"""
    correlation_id = get_correlation_id()

    # These will raise ValidationError if invalid
    clean_email = validate_email(email)
    clean_filename = validate_filename(filename)

    return {
        "message": "Validation successful",
        "clean_email": clean_email,
        "clean_filename": clean_filename,
        "correlation_id": correlation_id,
    }
