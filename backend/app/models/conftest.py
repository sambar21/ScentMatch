"""
app/models/conftest.py
Global event loop and engine that persists across all tests
"""
import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# GLOBAL event loop and engine - created once, never closed during tests
_loop = None
_engine = None
_SessionLocal = None


def get_or_create_loop():
    """Get or create the global event loop."""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def get_or_create_engine():
    """Get or create the global test engine."""
    global _engine, _SessionLocal
    if _engine is None:
        loop = get_or_create_loop()
        
        # Create engine that stays alive
        # Only add check_same_thread for SQLite
        connect_args = {}
        if "sqlite" in settings.database_url.lower():
            connect_args = {"check_same_thread": False}
        
        _engine = create_async_engine(
            settings.database_url,
            poolclass=StaticPool,
            connect_args=connect_args,
            echo=False,
        )
        
        _SessionLocal = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    return _engine, _SessionLocal


@pytest.fixture(scope="function")
def db():
    """Provide database session."""
    loop = get_or_create_loop()
    engine, SessionLocal = get_or_create_engine()
    
    # Create session synchronously
    async def get_session():
        async with SessionLocal() as session:
            yield session
            await session.rollback()
    
    gen = get_session()
    session = loop.run_until_complete(gen.__anext__())
    
    yield session
    
    # Cleanup session (but NOT loop or engine)
    try:
        loop.run_until_complete(gen.__anext__())
    except StopAsyncIteration:
        pass


# Don't let pytest close our loop
@pytest.fixture(scope="session", autouse=True)
def prevent_loop_close():
    """Prevent the event loop from being closed."""
    yield
    # Cleanup at the very end
    global _loop, _engine
    if _engine:
        _loop.run_until_complete(_engine.dispose())