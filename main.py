"""
GitHub Repository Search Assistant MCP Server

An MCP server that helps discover and analyze GitHub repositories.
Provides two core tools: search for repositories and get repository details.
"""

import os
import httpx
from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HTTP_TIMEOUT = 30.0

# Create MCP server
mcp = FastMCP("GitHub Repository Search Assistant", json_response=True)


# Helper functions

async def make_github_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Make an authenticated request to GitHub API."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=HTTP_TIMEOUT)
            
            if response.status_code == 403 and "rate limit" in response.text.lower():
                return {"error": "GitHub API rate limit exceeded. Add GITHUB_TOKEN to .env"}
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "Resource not found"}
            return {"error": f"GitHub API error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}


def build_search_query(task: str, language: str | None = None) -> str:
    """
    Build a GitHub search query from a task description.
    Uses the task words directly with quality filters.
    """
    # Clean up the task (remove common filler words)
    import re
    task_lower = task.lower()
    filler_words = {
        "need", "help", "want", "like", "make", "create", "build", "using",
        "with", "how", "what", "where", "when", "find", "get", "look",
        "can", "will", "should", "could", "would", "does", "don't"
    }
    
    # Extract meaningful words (3+ chars)
    words = re.findall(r'\b\w{3,}\b', task_lower)
    meaningful_words = [w for w in words if w not in filler_words]
    
    # Build query with top keywords
    if meaningful_words:
        query = " ".join(meaningful_words[:3])
    else:
        query = task_lower[:30]  # Fallback to first 30 chars
    
    # Add quality filters
    query += " stars:>50"
    
    # Add language filter if specified
    if language:
        query += f" language:{language}"
    
    return query


# MCP Tools

@mcp.tool()
async def search_github_repositories(
    task: str,
    language: str | None = None,
    max_results: int = 10
) -> dict[str, Any]:
    """
    Search GitHub for repositories relevant to a specific task.
    
    Use this to find repositories that can help accomplish a specific goal.
    
    Args:
        task: What you want to accomplish (e.g., "track my expenses", "build a chat app")
        language: Optional programming language to filter by (e.g., "Python", "JavaScript")
        max_results: Number of results to return (1-15, default: 10)
    
    Returns:
        List of matching repositories with name, description, stars, language, and URL
    """
    # Validate input
    if max_results < 1 or max_results > 15:
        max_results = 10
    
    # Build search query
    query = build_search_query(task, language)
    
    # Search GitHub
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": max_results,
    }
    
    result = await make_github_request(url, params)
    
    if "error" in result:
        return result
    
    # Format results
    repositories = []
    if "items" in result:
        for repo in result["items"]:
            repositories.append({
                "name": repo["name"],
                "owner": repo["owner"]["login"],
                "description": repo.get("description") or "No description available",
                "stars": repo["stargazers_count"],
                "language": repo.get("language") or "Not specified",
                "url": repo["html_url"],
                "topics": repo.get("topics", [])[:5],  # Top 5 topics
            })
    
    return {
        "task": task,
        "total_found": len(repositories),
        "repositories": repositories,
    }


@mcp.tool()
async def get_repository_details(owner: str, repository: str) -> dict[str, Any]:
    """
    Get detailed information about a specific GitHub repository.
    
    Use this to learn more about a repository before deciding to use it.
    
    Args:
        owner: Repository owner (username or organization)
        repository: Repository namey name
    
    Returns:
        Detailed metadata including description, stats, license, and links
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repository}"
    result = await make_github_request(url)
    
    if "error" in result:
        return result
    
    # Extract README URL for documentation
    readme_url = f"https://github.com/{owner}/{repository}/blob/{result.get('default_branch', 'main')}/README.md"
    
    return {
        "name": result["name"],
        "owner": result["owner"]["login"],
        "description": result.get("description") or "No description",
        "url": result["html_url"],
        "readme_url": readme_url,
        "language": result.get("language") or "Not specified",
        "topics": result.get("topics", []),
        "stars": result["stargazers_count"],
        "forks": result["forks_count"],
        "watchers": result["subscribers_count"],
        "open_issues": result.get("open_issues_count", 0),
        "last_updated": result["updated_at"],
        "license": result.get("license", {}).get("name") if result.get("license") else "No license specified",
        "homepage": result.get("homepage") or "No homepage provided",
        "created_at": result["created_at"],
        "archived": result["archived"],
        "size_kb": result["size"],
    }



# Run the server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")