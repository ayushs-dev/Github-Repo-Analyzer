# This is the service layer that actually talks to the GitHub API.
# The router (repos.py) handles HTTP routing logic; this file handles
# the external API calls. Keeping them separate makes the code easier to test
# and reason about — the router doesn't need to know GitHub API details.
import asyncio
import httpx
from app.services.config import settings
from app.schemas.repo import RepoStats, ContributorStat, RepoFullAnalysis

# These headers are sent with every request to GitHub's API.
# Authorization: our personal access token — without this we only get 60 requests/hour.
# Accept: tells GitHub we want the latest stable JSON format.
# X-GitHub-Api-Version: pins us to a specific API version so GitHub changes don't break us.
HEADERS = {
    "Authorization": f"Bearer {settings.github_token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


async def get_repo_analysis(owner: str, repo: str) -> RepoFullAnalysis:
    """
    Fetches repo stats, top contributors, and language breakdown from GitHub
    and bundles them into a single RepoFullAnalysis object.
    """
    # Open a single reusable HTTP client for all three requests.
    # base_url means we don't have to repeat "https://api.github.com" on every call.
    async with httpx.AsyncClient(
        base_url=settings.github_api_base,
        headers=HEADERS
    ) as client:
        # Fire all three API requests at the same time using asyncio.gather.
        # This is much faster than doing them one after another — instead of
        # waiting 3 * ~300ms = 900ms, we wait ~300ms total (they run in parallel).
        repo_res, contributors_res, languages_res = await asyncio.gather(
            client.get(f"/repos/{owner}/{repo}"),                              # main repo info
            client.get(f"/repos/{owner}/{repo}/contributors", params={"per_page": 5}),  # top 5 contributors
            client.get(f"/repos/{owner}/{repo}/languages"),                    # language breakdown
        )

    # raise_for_status() throws an exception if GitHub returned a 4xx or 5xx response.
    # The router catches these and converts them into clean API error messages.
    repo_res.raise_for_status()
    contributors_res.raise_for_status()
    languages_res.raise_for_status()

    # Parse the main repo response JSON into a dict.
    data = repo_res.json()

    # Build a RepoStats object by picking out the fields we care about.
    # We use .get() for optional fields (description, language, etc.) so we
    # get None instead of a KeyError if GitHub doesn't include them.
    repo_stats = RepoStats(
        full_name=data["full_name"],
        description=data.get("description"),
        stars=data["stargazers_count"],
        forks=data["forks_count"],
        open_issues=data["open_issues_count"],
        watchers=data["watchers_count"],
        language=data.get("language"),         # e.g. "Python" — may be None for docs repos
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        topics=data.get("topics", []),         # tags like ["web", "api"] — defaults to empty list
        homepage=data.get("homepage"),         # optional project website
        size_kb=data["size"],                  # GitHub reports size in KB
        default_branch=data["default_branch"], # usually "main" or "master"
    )

    # Build a list of ContributorStat objects from the contributors response.
    # We filter out bots (type != "User") to keep the list human contributors only.
    # GitHub sometimes includes bot accounts (like "dependabot") in the contributor list.
    contributors = [
        ContributorStat(
            login=c["login"],              # GitHub username
            contributions=c["contributions"],  # number of commits
            avatar_url=c["avatar_url"],    # their profile picture URL
            html_url=c["html_url"],        # link to their GitHub profile
        )
        for c in contributors_res.json()
        if c.get("type") == "User"  # skip bots and non-human accounts
    ]

    # Bundle everything together and return.
    # languages_res.json() returns something like {"Python": 48210, "Shell": 1234}
    # where the values are the number of bytes of code in that language.
    return RepoFullAnalysis(
        repo=repo_stats,
        top_contributors=contributors,
        languages=languages_res.json(),
    )
