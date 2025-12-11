import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.database import Base
from app.config import settings

import app.api.models.models

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is still acceptable
    here as it will be used to derive a DBAPI connection from the URL.

    When we run in this mode, we go through the migrations
    and emit the SQL to a file strategy.
    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # configuration for 'autogenerate' support
    # (used by 'alembic revision --autogenerate')
    connectable = create_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # include_object=include_object # Если у вас есть функция include_object для фильтрации таблиц
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
