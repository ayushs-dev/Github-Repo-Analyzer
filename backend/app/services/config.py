# This file manages app configuration — things like API keys and database URLs.
# Instead of hardcoding sensitive values like tokens directly in the code
# (which would expose them in git), we read them from a .env file at runtime.
# pydantic-settings handles all of this automatically.
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Your GitHub Personal Access Token — required.
    # Without it, GitHub limits you to 60 API requests per hour.
    # With it, you get 5,000 per hour.
    # This MUST be set in the .env file (GITHUB_TOKEN=your_token_here).
    github_token: str

    # The base URL for the GitHub REST API.
    # Unlikely to change, but having it here makes it easy to mock in tests
    # by pointing to a local test server instead of the real GitHub.
    github_api_base: str = "https://api.github.com"

    # PostgreSQL connection string in SQLAlchemy format.
    # asyncpg is the async PostgreSQL driver we use.
    # Default assumes a local Postgres instance — override in .env for production.
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/repoanalyzer"

    class Config:
        # Tell pydantic-settings to load values from a .env file.
        # Values in .env override the defaults above.
        # The .env file should NEVER be committed to git (add it to .gitignore).
        env_file = ".env"


# Create a single shared instance of Settings.
# This is imported by other files (e.g. `from app.services.config import settings`).
# pydantic validates all values on startup — if GITHUB_TOKEN is missing,
# the app will crash immediately with a clear error instead of failing silently later.
settings = Settings()
