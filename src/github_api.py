"""GitHub API utilities for making authenticated requests."""

from typing import Any
import httpx
from src.config import GITHUB_API_BASE, GITHUB_TOKEN, HTTP_TIMEOUT


async def make_github_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make an authenticated request to GitHub API with error handling."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=HTTP_TIMEOUT)
            
            # Handle rate limiting
            if response.status_code == 403 and "rate limit" in response.text.lower():
                return {"error": "GitHub API rate limit exceeded. Please add a GITHUB_TOKEN to .env file."}
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Resource not found"}
            return {"error": f"GitHub API error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


async def search_repositories(query: str, per_page: int = 10) -> dict[str, Any]:
    """Search GitHub repositories with the given query."""
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    return await make_github_request(url, params)


async def get_repo_metadata(owner: str, repo: str) -> dict[str, Any]:
    """Get detailed metadata for a specific repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    return await make_github_request(url)


async def fetch_readme(owner: str, repo: str) -> str | None:
    """Fetch the README content for a repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/readme"
    headers = {
        "Accept": "application/vnd.github.raw",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            return response.text
        except Exception:
            return None
