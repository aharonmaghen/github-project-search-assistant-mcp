"""
MCP server for discovering and analyzing GitHub projects.

Helps users find relevant GitHub repositories and provides
actionable guidance on using them to complete specific tasks.
"""

from mcp.server.fastmcp import FastMCP
from src.tools import (
    search_github_projects,
    get_github_repository_details,
    analyze_github_repository_for_task,
)

# Create an MCP server
mcp = FastMCP("GitHub Project Search Assistant", json_response=True)


# Register MCP Tools

@mcp.tool()
async def search_github_projects_tool(
    task: str,
    language: str | None = None,
    max_results: int = 8
):
    """
    Search GitHub for projects relevant to a specific task.
    
    Args:
        task: Description of what the user wants to accomplish (e.g., "track my personal finances")
        language: Optional programming language filter (e.g., "Python", "JavaScript")
        max_results: Maximum number of results to return (default: 8, max: 15)
    
    Returns:
        Dictionary with list of repositories including name, description, stars, language, and topics
    """
    return await search_github_projects(task, language, max_results)


@mcp.tool()
async def get_github_repository_details_tool(owner: str, repo: str):
    """
    Get comprehensive metadata and details for a specific GitHub repository.
    
    Args:
        owner: GitHub username or organization name
        repo: GitHub repository name
    
    Returns:
        Detailed repository information including stats, topics, and links
    """
    return await get_github_repository_details(owner, repo)


@mcp.tool()
async def analyze_github_repository_for_task_tool(
    owner: str,
    repo: str,
    user_task: str
):
    """
    Analyze a GitHub repository and provide guidance on using it for a specific task.
    Fetches README, extracts key sections, and synthesizes actionable advice.
    
    Args:
        owner: GitHub username or organization name
        repo: GitHub repository name
        user_task: The task the user wants to accomplish
    
    Returns:
        Analysis including why the repository helps, how to get started, key features, and requirements
    """
    return await analyze_github_repository_for_task(owner, repo, user_task)


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")