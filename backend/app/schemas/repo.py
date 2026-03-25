# Schemas define the shape of data coming in and going out of the API.
# These are NOT database tables — they're just validation/serialization blueprints.
# Pydantic checks that data matches these shapes and raises clear errors if not.
# FastAPI uses them as response_model= to auto-validate and document API responses.
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Represents the core stats of a single GitHub repository.
# Fields marked Optional[...] = None mean GitHub might not return them
# (e.g. a repo with no description, or no detected language).
class RepoStats(BaseModel):
    full_name: str            # e.g. "torvalds/linux"
    description: Optional[str] = None   # the repo's description blurb (can be empty)
    stars: int                # how many people starred it
    forks: int                # how many times it's been forked
    open_issues: int          # currently open issues/bugs
    watchers: int             # people watching for activity
    language: Optional[str] = None      # primary detected language (e.g. "Python")
    created_at: datetime      # when the repo was first created
    updated_at: datetime      # when it was last pushed to
    topics: list[str]         # tags the owner added (e.g. ["machine-learning", "python"])
    homepage: Optional[str] = None      # optional project website URL
    size_kb: int              # total repo size in kilobytes
    default_branch: str       # usually "main" or "master"


# Represents a single contributor to the repo.
# We only fetch the top 5, but this schema applies to each one.
class ContributorStat(BaseModel):
    login: str           # GitHub username
    contributions: int   # total number of commits they've made
    avatar_url: str      # URL to their profile picture
    html_url: str        # link to their GitHub profile page


# The full analysis response — this is what the API actually returns.
# It bundles together the repo stats, top contributors, and language breakdown
# into one neat object so the frontend only needs to make one request.
class RepoFullAnalysis(BaseModel):
    repo: RepoStats                      # the repo's main stats
    top_contributors: list[ContributorStat]   # top 5 contributors
    languages: dict[str, int]            # e.g. {"Python": 48210, "Shell": 1234}
                                         # values are bytes of code in that language
