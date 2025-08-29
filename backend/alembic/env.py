"""
Alembic environment configuration for async SQLAlchemy
Connects our migration system to our enterprise database setup
"""

import asyncio
from logging.config import fileConfig

from alembic import context
# Import our application components
from app.core.config import settings
from app.core.database import Base
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

"""
Tutorial Connection: Sanjeev probably had simple Alembic setup
Enterprise Upgrade: We connect Alembic to our config system and async database
"""

# This is the Alembic Config object, which provides access to values within .ini file
config = context.config

# Set the database URL from our settings (not hardcoded in alembic.ini)
# Convert async URL to sync for Alembic migrations
sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql://"
)
config.set_main_option("sqlalchemy.url", sync_database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Other values from the config, defined by needs of env.py
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Enterprise feature: Better migration file naming
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run migrations with database connection
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Enterprise feature: Better migration handling
        render_as_batch=True,
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using sync engine
    Simplified version that works with our sync database URL
    """
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = context.config.get_main_option("sqlalchemy.url")
        from sqlalchemy import create_engine

        connectable = create_engine(connectable, poolclass=pool.NullPool)

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                render_as_batch=True,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    else:
        do_run_migrations(connectable)


# Determine which mode to run migrations
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
