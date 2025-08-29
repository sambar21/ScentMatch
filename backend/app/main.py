from contextlib import asynccontextmanager
from typing import Annotated

from app.core.config import settings
from app.core.database import check_db_connection, get_db
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
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
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.version,
    }


@app.get("/health/db")
async def health_check_db():
    is_healthy = await check_db_connection()

    if is_healthy:
        return {
            "status": "healthy",
            "database": "connected",
            "service": settings.app_name,
        }
    else:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "service": settings.app_name,
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
