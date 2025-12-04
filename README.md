# GitHub Project Search Assistant MCP

A simple, lightweight MCP (Model Context Protocol) server that helps discover and analyze GitHub projects relevant to specific tasks. Get started quickly without configuration complexity.

## Features

- **Simple Search**: Find GitHub repositories relevant to what you want to build or accomplish
- **Language Filtering**: Optionally filter results by programming language
- **Detailed Repository Information**: Get stats, license info, topics, and links
- **Lightweight**: All functionality in a single file with minimal dependencies

## Tools

### `search_github_projects`
Search GitHub for repositories that match your task.

**Parameters:**
- `task` (str): What you want to accomplish (e.g., "build a chat app", "track expenses")
- `language` (str, optional): Programming language to filter by (e.g., "Python", "JavaScript")
- `max_results` (int, optional): Number of results to return (default: 10, max: 15)

**Returns:** List of repositories with name, description, stars, language, topics, and URL.

**Example:**
```
search_github_projects(task="build a REST API", language="Python", max_results=8)
```

### `get_repo_details`
Get detailed information about a specific GitHub repository.

**Parameters:**
- `owner` (str): Repository owner (username or organization)
- `repo` (str): Repository name

**Returns:** Repository metadata including description, stars, forks, license, last updated, and links.

**Example:**
```
get_repo_details(owner="django", repo="django")
```

## Setup

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)
- Python 3.10+
- GitHub account (optional but recommended for higher API rate limits)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd github-project-search-assistant-mcp
```

2. Install the MCP server:
```bash
uv run mcp install main.py
```

Done! The server is now registered and ready to use.

### Optional: GitHub Token

To get higher API rate limits (1000 requests/hour instead of 60), create a GitHub personal access token:

1. Go to https://github.com/settings/tokens
2. Create a new token (classic) with `public_repo` scope
3. Create a `.env` file in this directory:
```
GITHUB_TOKEN=your_token_here
```

## Usage

Once installed, the MCP server works with any MCP-compatible client. Here's how to use it:

### Basic Workflow

1. **Search for repositories** matching your task
   ```
   search_github_projects(task="build a REST API in Python")
   ```

2. **Get details** about interesting repositories
   ```
   get_repo_details(owner="django", repo="django")
   ```

3. **Visit the repository** to access documentation and start using it

### Example Scenarios

**"I want to build a web scraper"**
- Search: `search_github_projects(task="web scraper", language="Python")`
- Get details: `get_repo_details(owner="scrapy", repo="scrapy")`

**"I need a real-time chat system"**
- Search: `search_github_projects(task="real-time chat", language="JavaScript")`
- Get details: `get_repo_details(owner="socketio", repo="socket.io")`

**"I want a task management system"**
- Search: `search_github_projects(task="task management todo list")`
- Pick your favorite and get details

## Rate Limits

- **Without token**: 60 GitHub API requests per hour
- **With token**: 1000 requests per hour

Adding a GitHub token is recommended to avoid hitting rate limits.

## Project Structure

Everything is in a single file for simplicity:

```
├── main.py                    # Complete server with all functionality
├── .env                       # Optional GitHub token (create if needed)
└── README.md                  # This file
```

## How It Works

1. **Search**: Takes your task description, extracts key words, and searches GitHub repos with quality filters (minimum stars, recent activity)
2. **Get Details**: Retrieves comprehensive repository metadata from the GitHub API
3. **Filter**: Optionally filters results by programming language

The search uses a simple but effective approach:
- Removes common filler words from your search task
- Extracts meaningful keywords (3+ characters)
- Adds quality filters (stars, recency)
- Optionally filters by language

## Contributing

Contributions welcome! Feel free to open issues or submit pull requests.
