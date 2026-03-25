# This file sets up the database connection and gives us a way to talk to it.
# We're using SQLAlchemy (an ORM — Object Relational Mapper) which lets us
# write Python instead of raw SQL to interact with the database.
# The "async" versions are used because our app is async (non-blocking),
# meaning it can handle multiple requests at once without waiting around.
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.services.config import settings  # our app settings (reads from .env file)

# Create the async database engine — this is the actual connection to PostgreSQL.
# The URL comes from our .env file (e.g. postgresql+asyncpg://user:pass@host/dbname).
# asyncpg is a fast async PostgreSQL driver.
engine = create_async_engine(
    settings.database_url,
    echo=True,  # logs every SQL query to the console — great for debugging, turn off in production
)

# A session is like a "conversation" with the database — you open one,
# run queries, then close it. AsyncSessionLocal is a factory that creates
# new sessions whenever we need one.
# expire_on_commit=False means objects stay usable after we commit a transaction
# (otherwise SQLAlchemy would clear them and force a re-fetch, which breaks async code).
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base is the parent class all our database models will inherit from.
# SQLAlchemy uses this to know which classes represent database tables.
class Base(DeclarativeBase):
    pass


# This is a FastAPI "dependency" — a function that FastAPI calls automatically
# to provide a database session to any route that asks for one.
# The `yield` makes it a context manager: it opens the session, hands it to the
# route, and then closes it cleanly when the request is done (even if it crashes).
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
