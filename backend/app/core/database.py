import logging
from typing import AsyncGenerator

from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

# Set up logging
logger = logging.getLogger(__name__)


# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=settings.debug,
    poolclass=StaticPool if settings.database_name == ":memory:" else None,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
    autoflush=False,  # Manual flush control
    autocommit=False,  # Manual commit control
)


Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Database session created")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            logger.debug("Database session closed")


async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they're registered

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_db_connection() -> bool:
  
    try:
        async with engine.begin() as conn:
            # Simple query to test connection
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
            logger.debug("Database connection check successful")
            return True

    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db() -> None:
   
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Database utilities for advanced operations
class DatabaseUtils:
    @staticmethod
    async def execute_raw_query(query: str, params: dict = None):
        """Execute raw SQL query with parameters"""
        async with AsyncSessionLocal() as session:
            try:
                result = await session.execute(query, params or {})
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"Raw query execution failed: {e}")
                raise

    @staticmethod
    async def get_table_info(table_name: str):
        """Get table schema information for debugging"""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = :table_name
        """
        return await DatabaseUtils.execute_raw_query(query, {"table_name": table_name})
