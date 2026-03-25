# This file defines the database table for caching GitHub repo data.
# A "model" in SQLAlchemy is just a Python class that maps 1-to-1 with a database table.
# Every attribute here becomes a column in the table.
from sqlalchemy import String, Integer, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base  # the shared base class all models must inherit from


# This class represents the "repo_cache" table in PostgreSQL.
# We cache GitHub API responses here so we don't have to hit the GitHub API
# on every single request — GitHub has rate limits, so caching is important.
class RepoCache(Base):
    __tablename__ = "repo_cache"  # the actual table name in the database

    # A unique auto-incrementing ID for each row — standard primary key.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # The "owner/repo" string, e.g. "torvalds/linux".
    # unique=True means no two rows can have the same repo.
    # index=True makes lookups by this column much faster (the DB builds an index on it).
    full_name: Mapped[str] = mapped_column(String, unique=True, index=True)

    # The full GitHub API response stored as JSON.
    # Rather than splitting into 20 columns, we just dump the whole thing here.
    # This makes it flexible — if the API adds new fields, we don't need a migration.
    data: Mapped[dict] = mapped_column(JSON)

    # When we last fetched this data from GitHub.
    # Used to check if the cache is stale (older than 1 hour = re-fetch).
    # Note: datetime.utcnow is deprecated in Python 3.12+ — ideally replace
    # with lambda: datetime.now(timezone.utc) in a future update.
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
