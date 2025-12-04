"""
MCP server for discovering and analyzing GitHub projects.

Helps users find relevant GitHub repositories and provides
actionable guidance on using them to complete specific tasks.
"""

import os
import re
from typing import Any
from dotenv import load_dotenv
import httpx
from markdown_it import MarkdownIt
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Create an MCP server
mcp = FastMCP("GitHub Project Discovery", json_response=True)

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


# GitHub API Helper Functions
async def _make_github_request(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Make an authenticated request to GitHub API with error handling."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
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


async def _search_repositories(query: str, per_page: int = 10) -> dict[str, Any]:
    """Search GitHub repositories with the given query."""
    url = f"{GITHUB_API_BASE}/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    return await _make_github_request(url, params)


async def _get_repo_metadata(owner: str, repo: str) -> dict[str, Any]:
    """Get detailed metadata for a specific repository."""
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    return await _make_github_request(url)


async def _fetch_readme(owner: str, repo: str) -> str | None:
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
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
        except Exception:
            return None


def _build_search_query(task: str, language: str | None = None) -> list[str]:
    """
    Build creative GitHub search queries from a user task.
    Returns multiple query variations for better coverage.
    """
    # Synonym mapping for common terms
    synonyms = {
        "finance": ["finance", "budget", "expense", "accounting", "money", "financial"],
        "track": ["track", "manage", "monitor", "organize"],
        "todo": ["todo", "task", "checklist", "productivity"],
        "notes": ["notes", "note-taking", "notebook", "knowledge"],
        "password": ["password", "credential", "secret", "vault"],
        "web": ["web", "website", "webapp", "frontend"],
        "api": ["api", "rest", "graphql", "backend"],
        "database": ["database", "db", "sql", "data-storage"],
        "chat": ["chat", "messaging", "communication"],
        "blog": ["blog", "cms", "content"],
        "ecommerce": ["ecommerce", "shop", "store", "commerce"],
        "analytics": ["analytics", "metrics", "tracking", "insights"],
        "automation": ["automation", "workflow", "ci-cd"],
        "ml": ["machine-learning", "ml", "ai", "deep-learning"],
    }
    
    # Extract key terms and expand with synonyms
    task_lower = task.lower()
    expanded_terms = set()
    
    for key, values in synonyms.items():
        if key in task_lower or any(v in task_lower for v in values):
            expanded_terms.update(values[:3])  # Use top 3 synonyms
    
    # If no matches, use the task words directly
    if not expanded_terms:
        # Extract meaningful words (filter out common words)
        words = re.findall(r'\b\w{3,}\b', task_lower)
        common_words = {"need", "help", "want", "like", "make", "create", "build", "using", "with"}
        expanded_terms = {w for w in words if w not in common_words}
    
    # Build queries
    queries = []
    
    # Query 1: Broad OR search with popularity filter
    if expanded_terms:
        or_terms = " OR ".join(list(expanded_terms)[:5])
        base_query = f"{or_terms} stars:>100"
        if language:
            base_query += f" language:{language}"
        queries.append(base_query)
    
    # Query 2: Exact phrase from task + recent activity
    task_clean = re.sub(r'\b(i|need|help|want|to|a|an|the)\b', '', task_lower).strip()
    if task_clean:
        recent_query = f"{task_clean} pushed:>2024-01-01"
        if language:
            recent_query += f" language:{language}"
        queries.append(recent_query)
    
    # Query 3: High quality filter (many stars, good topics)
    if expanded_terms:
        main_terms = " ".join(list(expanded_terms)[:3])
        quality_query = f"{main_terms} stars:>500 forks:>50"
        if language:
            quality_query += f" language:{language}"
        queries.append(quality_query)
    
    return queries[:2]  # Return top 2 queries to avoid too many API calls


def _extract_markdown_sections(markdown_content: str) -> dict[str, str]:
    """Extract key sections from markdown README."""
    sections = {
        "installation": "",
        "quickstart": "",
        "usage": "",
        "prerequisites": "",
        "features": "",
        "getting_started": "",
    }
    
    if not markdown_content:
        return sections
    
    # Parse markdown to get structure
    lines = markdown_content.split('\n')
    current_section = None
    current_content = []
    
    # Section header patterns
    install_patterns = [r'install', r'installation', r'setup', r'getting.?started']
    usage_patterns = [r'usage', r'how.?to', r'quickstart', r'quick.?start', r'example']
    prereq_patterns = [r'prerequisite', r'requirement', r'dependencies', r'before']
    feature_patterns = [r'feature', r'what', r'about', r'overview']
    
    for line in lines:
        # Check if it's a header
        if line.startswith('#'):
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Determine new section
            header_text = line.lower()
            current_content = []
            
            if any(re.search(p, header_text) for p in install_patterns):
                current_section = "installation"
            elif any(re.search(p, header_text) for p in usage_patterns):
                current_section = "usage"
            elif any(re.search(p, header_text) for p in prereq_patterns):
                current_section = "prerequisites"
            elif any(re.search(p, header_text) for p in feature_patterns):
                current_section = "features"
            else:
                current_section = None
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Consolidate quickstart/getting_started
    if sections["usage"] and len(sections["usage"]) < 1000:
        sections["quickstart"] = sections["usage"]
    
    return sections


def _extract_code_blocks(text: str) -> list[str]:
    """Extract code blocks from markdown text."""
    code_blocks = re.findall(r'```[\w]*\n(.*?)```', text, re.DOTALL)
    return [block.strip() for block in code_blocks if block.strip()]


# MCP Tools

@mcp.tool()
async def search_github_projects(
    task: str,
    language: str | None = None,
    max_results: int = 8
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
    if max_results > 15:
        max_results = 15
    
    # Generate multiple search queries
    queries = _build_search_query(task, language)
    
    all_repos = {}
    seen_full_names = set()
    
    for query in queries:
        result = await _search_repositories(query, per_page=max_results)
        
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


@mcp.tool()
async def get_github_repository_details(owner: str, repo: str) -> dict[str, Any]:
    """
    Get comprehensive metadata and details for a specific GitHub repository.
    
    Args:
        owner: GitHub username or organization name
        repo: GitHub repository name
    
    Returns:
        Detailed repository information including stats, topics, and links
    """
    result = await _get_repo_metadata(owner, repo)
    
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


@mcp.tool()
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
    metadata_result = await _get_repo_metadata(owner, repo)
    readme_content = await _fetch_readme(owner, repo)
    
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
    sections = _extract_markdown_sections(readme_content)
    
    # Extract code examples from relevant sections
    install_commands = []
    usage_examples = []
    
    if sections["installation"]:
        install_commands = _extract_code_blocks(sections["installation"])
    
    if sections["usage"] or sections["quickstart"]:
        usage_text = sections["usage"] or sections["quickstart"]
        usage_examples = _extract_code_blocks(usage_text)
    
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


# Run with streamable HTTP transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")