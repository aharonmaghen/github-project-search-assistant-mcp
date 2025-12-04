"""MCP tool definitions for GitHub project discovery."""

from typing import Any
from src.github_api import search_repositories, get_repo_metadata, fetch_readme
from src.query_builder import build_search_query
from src.markdown_parser import extract_markdown_sections, extract_code_blocks
from src.config import DEFAULT_MAX_RESULTS, MAX_RESULTS_LIMIT


async def search_github_projects(
    task: str,
    language: str | None = None,
    max_results: int = DEFAULT_MAX_RESULTS
) -> dict[str, Any]:
    """
    Search GitHub for projects relevant to a specific task.
    
    Args:
        task: Description of what the user wants to accomplish (e.g., "track my personal finances")
        language: Optional programming language filter (e.g., "Python", "JavaScript")
        max_results: Maximum number of results to return (default: 8, max: 15)
    
    Returns:
        Dictionary with list of repositories including name, description, stars, language, and topics
    """
    if max_results > MAX_RESULTS_LIMIT:
        max_results = MAX_RESULTS_LIMIT
    
    # Generate multiple search queries
    queries = build_search_query(task, language)
    
    all_repos = {}
    seen_full_names = set()
    
    for query in queries:
        result = await search_repositories(query, per_page=max_results)
        
        if "error" in result:
            continue
        
        if "items" in result:
            for repo in result["items"]:
                full_name = repo["full_name"]
                if full_name not in seen_full_names:
                    seen_full_names.add(full_name)
                    all_repos[full_name] = {
                        "name": repo["name"],
                        "owner": repo["owner"]["login"],
                        "full_name": full_name,
                        "description": repo.get("description", ""),
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"],
                        "language": repo.get("language", ""),
                        "topics": repo.get("topics", []),
                        "url": repo["html_url"],
                        "homepage": repo.get("homepage", ""),
                        "updated_at": repo["updated_at"],
                        "open_issues": repo.get("open_issues_count", 0),
                    }
        
        # Stop if we have enough results
        if len(all_repos) >= max_results:
            break
    
    # Sort by stars and limit results
    sorted_repos = sorted(all_repos.values(), key=lambda x: x["stars"], reverse=True)[:max_results]
    
    return {
        "task": task,
        "query_strategies": queries,
        "total_found": len(sorted_repos),
        "repositories": sorted_repos,
    }


async def get_github_repository_details(owner: str, repo: str) -> dict[str, Any]:
    """
    Get comprehensive metadata and details for a specific GitHub repository.
    
    Args:
        owner: GitHub username or organization name
        repo: GitHub repository name
    
    Returns:
        Detailed repository information including stats, topics, and links
    """
    result = await get_repo_metadata(owner, repo)
    
    if "error" in result:
        return result
    
    return {
        "name": result["name"],
        "full_name": result["full_name"],
        "owner": result["owner"]["login"],
        "description": result.get("description", ""),
        "url": result["html_url"],
        "homepage": result.get("homepage", ""),
        "language": result.get("language", ""),
        "topics": result.get("topics", []),
        "stars": result["stargazers_count"],
        "forks": result["forks_count"],
        "watchers": result["subscribers_count"],
        "open_issues": result["open_issues_count"],
        "created_at": result["created_at"],
        "updated_at": result["updated_at"],
        "pushed_at": result["pushed_at"],
        "size": result["size"],
        "license": result.get("license", {}).get("name", "No license specified") if result.get("license") else "No license specified",
        "default_branch": result["default_branch"],
        "archived": result["archived"],
        "has_wiki": result["has_wiki"],
        "has_discussions": result.get("has_discussions", False),
    }


async def analyze_github_project_for_task(
    owner: str,
    repo: str,
    user_task: str
) -> dict[str, Any]:
    """
    Analyze a GitHub project and provide guidance on using it for a specific task.
    Fetches README, extracts key sections, and synthesizes actionable advice.
    
    Args:
        owner: GitHub username or organization name
        repo: GitHub repository name
        user_task: The task the user wants to accomplish
    
    Returns:
        Analysis including why the project helps, how to get started, key features, and requirements
    """
    # Fetch repo metadata and README in parallel
    metadata_result = await get_repo_metadata(owner, repo)
    readme_content = await fetch_readme(owner, repo)
    
    if "error" in metadata_result:
        return metadata_result
    
    if not readme_content:
        return {
            "error": "README not found or inaccessible",
            "suggestion": "Check the repository directly or try the homepage",
            "url": metadata_result["html_url"],
            "homepage": metadata_result.get("homepage", ""),
        }
    
    # Extract key sections
    sections = extract_markdown_sections(readme_content)
    
    # Extract code examples from relevant sections
    install_commands = []
    usage_examples = []
    
    if sections["installation"]:
        install_commands = extract_code_blocks(sections["installation"])
    
    if sections["usage"] or sections["quickstart"]:
        usage_text = sections["usage"] or sections["quickstart"]
        usage_examples = extract_code_blocks(usage_text)
    
    # Build structured analysis
    analysis = {
        "repository": f"{owner}/{repo}",
        "url": metadata_result["html_url"],
        "task_context": user_task,
        
        "why_this_helps": {
            "description": metadata_result.get("description", ""),
            "key_topics": metadata_result.get("topics", [])[:5],
            "popularity": {
                "stars": metadata_result["stargazers_count"],
                "forks": metadata_result["forks_count"],
            },
            "activity": {
                "last_updated": metadata_result["updated_at"],
                "open_issues": metadata_result["open_issues_count"],
            },
            "language": metadata_result.get("language", ""),
        },
        
        "getting_started": {
            "prerequisites": sections.get("prerequisites", "")[:500] if sections.get("prerequisites") else "Check README for requirements",
            "installation_steps": install_commands[:3] if install_commands else ["See installation section in README"],
            "installation_text": sections.get("installation", "")[:800] if sections.get("installation") else "",
        },
        
        "usage_guidance": {
            "quick_start": sections.get("quickstart", "")[:600] if sections.get("quickstart") else sections.get("usage", "")[:600],
            "example_code": usage_examples[:2] if usage_examples else [],
        },
        
        "key_features": sections.get("features", "")[:500] if sections.get("features") else "See README for detailed features",
        
        "additional_resources": {
            "homepage": metadata_result.get("homepage", ""),
            "has_wiki": metadata_result["has_wiki"],
            "has_discussions": metadata_result.get("has_discussions", False),
            "license": metadata_result.get("license", {}).get("name", "Not specified") if metadata_result.get("license") else "Not specified",
        },
    }
    
    return analysis
