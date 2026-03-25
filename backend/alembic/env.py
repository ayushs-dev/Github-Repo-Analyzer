# This is Alembic's environment configuration file.
# Alembic is a database migration tool — it tracks changes to your database schema
# over time (like adding columns, creating tables, etc.) similar to how git tracks
# code changes. This file tells Alembic how to connect to your database
# and where to find your models.
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import sys
import os

# Add the backend directory to Python's module search path so we can import
# our app code (models, database, etc.) from within this script.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# `config` is Alembic's config object — it reads values from alembic.ini.
config = context.config

# Set up Python's standard logging using the config from alembic.ini.
# This means Alembic migration output shows up in a readable format.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import our model and Base so Alembic knows what the database schema should look like.
# target_metadata tells Alembic "compare the DB to this schema when generating migrations".
# Without this, `alembic revision --autogenerate` wouldn't know what tables to create.
from app.models.repo import RepoCache   # noqa: F401 — imported so Base.metadata includes it
from app.database import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    In offline mode, Alembic doesn't need an actual database connection.
    Instead it just generates the SQL statements and prints them (or writes to a file).
    Useful when you want to review migrations before running them,
    or when you can't connect to the DB directly (e.g. in CI).
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,           # embed values directly in SQL instead of using bind params
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In online mode, Alembic connects to the real database and runs the
    migration SQL directly. This is the normal mode you'd use in development
    or when deploying to production.

    NOTE: This uses the synchronous psycopg2 driver (from alembic.ini),
    NOT the async asyncpg driver the main app uses. That's intentional —
    Alembic doesn't support async engines, so we use sync here just for migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # don't pool connections — each migration gets a fresh one
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Alembic decides which mode to use based on how it was invoked.
# `alembic upgrade head` → online mode (connects to DB and runs migrations)
# `alembic upgrade head --sql` → offline mode (just prints the SQL)
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
