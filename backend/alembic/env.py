from logging.config import fileConfig

from alembic import context
# Import our application components
from app.core.config import settings
from app.core.database import Base
from sqlalchemy import pool
from sqlalchemy.engine import Connection

config = context.config


# Convert async URL to sync for Alembic migrations
sync_database_url = settings.database_url.replace(
    "postgresql+asyncpg://", "postgresql://"
)
config.set_main_option("sqlalchemy.url", sync_database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
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


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
