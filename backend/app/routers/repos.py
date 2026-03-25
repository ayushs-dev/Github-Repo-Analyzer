# This file defines the API routes related to repositories.
# A "router" is a mini-app that groups related endpoints together.
# All routes here are prefixed with /repos (e.g. GET /repos/torvalds/linux).
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.github import get_repo_analysis   # the function that calls GitHub's API
from app.schemas.repo import RepoFullAnalysis        # the shape of our response
from app.database import get_db                      # gives us a DB session per request
from app.models.repo import RepoCache                # the database table for caching
from datetime import datetime, timedelta
import httpx  # for catching HTTP errors from the GitHub API call

# NOTE: `import json` was here but is unused — removed to keep things clean.

# Create the router. FastAPI will register all routes defined here
# under the /repos prefix, and group them under the "repos" tag in /docs.
router = APIRouter(prefix="/repos", tags=["repos"])

# How long before we consider cached data "stale" and re-fetch from GitHub.
# Set to 1 hour — GitHub's API has rate limits, so we don't want to call it
# on every single request. If data is less than 1 hour old, we return it from DB.
CACHE_TTL_HOURS = 1


# GET /repos/{owner}/{repo}
# e.g. GET /repos/torvalds/linux
# This is the main endpoint — it returns a full analysis of any public GitHub repo.
@router.get("/{owner}/{repo}", response_model=RepoFullAnalysis)
async def analyze_repo(
    owner: str,        # the GitHub username or org (e.g. "torvalds")
    repo: str,         # the repo name (e.g. "linux")
    db: AsyncSession = Depends(get_db)  # FastAPI injects a DB session automatically
):
    # Combine owner + repo into "owner/repo" format — this is how GitHub identifies repos.
    full_name = f"{owner}/{repo}"

    # --- Step 1: Check if we already have this repo cached in our database ---
    # We run a SELECT query to find a matching row in the repo_cache table.
    result = await db.execute(
        select(RepoCache).where(RepoCache.full_name == full_name)
    )
    cached = result.scalar_one_or_none()  # returns the row, or None if not found

    if cached:
        # We have a cached entry — check how old it is.
        age = datetime.utcnow() - cached.fetched_at
        if age < timedelta(hours=CACHE_TTL_HOURS):
            # Cache is fresh (less than 1 hour old) — return it directly.
            # We unpack the stored JSON dict back into our Pydantic model.
            return RepoFullAnalysis(**cached.data)
        # If we fall through here, the cache exists but is stale — we'll re-fetch below.

    # --- Step 2: Cache miss or stale cache — go fetch fresh data from GitHub ---
    try:
        analysis = await get_repo_analysis(owner, repo)
    except httpx.HTTPStatusError as e:
        # GitHub returned a 4xx/5xx — translate it into a friendly API error.
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Repo '{full_name}' not found on GitHub"
            )
        if e.response.status_code == 403:
            # 403 usually means we've hit GitHub's rate limit (60 req/hr unauthenticated,
            # 5000/hr with a token). It can also mean the token is wrong/expired.
            raise HTTPException(
                status_code=403,
                detail="GitHub rate limit hit or token is invalid"
            )
        # Any other error (500, 502, etc.) — blame the upstream GitHub API.
        raise HTTPException(status_code=502, detail="GitHub API returned an error")

    # --- Step 3: Save the fresh data back to the database for next time ---
    # Convert the Pydantic model to a plain dict so it can be stored as JSON.
    # mode="json" ensures datetimes etc. are serialized to strings properly.
    data_dict = analysis.model_dump(mode="json")

    if cached:
        # Row already exists — just update it in-place with the new data and timestamp.
        cached.data = data_dict
        cached.fetched_at = datetime.utcnow()
    else:
        # No row yet — create a brand new cache entry.
        db.add(RepoCache(full_name=full_name, data=data_dict))

    # Commit the transaction so the changes are actually saved to the database.
    await db.commit()

    # Return the fresh analysis to the caller.
    return analysis
