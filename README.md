# Github Project Search Assistant MCP

An MCP (Model Context Protocol) server that helps LLMs discover and analyze GitHub projects to assist users in completing specific tasks. This server searches GitHub for relevant repositories, analyzes their documentation, and provides actionable guidance on how to use them.

## Features

- **Intelligent Search**: Converts natural language task descriptions into optimized GitHub queries with synonym expansion and smart filtering
- **Language-Specific Filtering**: Optionally filter results by programming language
- **Comprehensive Analysis**: Extracts and parses README files to provide structured guidance
- **Actionable Insights**: Returns installation steps, usage examples, prerequisites, and feature highlights
- **Repository Metadata**: Provides detailed information about stars, activity, topics, and more

## Tools

### `search_github_projects`
Search GitHub for GitHub projects relevant to a specific task.

**Parameters:**
- `task` (str): Description of what the user wants to accomplish (e.g., "track my personal finances")
- `language` (str, optional): Programming language filter (e.g., "Python", "JavaScript")
- `max_results` (int, optional): Maximum results to return (default: 8, max: 15)

**Returns:** List of repositories with metadata including name, description, stars, language, topics, and URL.

### `get_github_repository_details`
Get comprehensive metadata for a specific GitHub repository.

**Parameters:**
- `owner` (str): Repository owner (username or organization)
- `repo` (str): Repository name

**Returns:** Detailed repository information including stats, topics, license, activity, and links.

### `analyze_github_repository_for_task`
Analyze a repository and provide guidance on using it for a specific task.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `user_task` (str): The task the user wants to accomplish

**Returns:** Structured analysis including:
- Why this repository helps with the task
- Installation steps and prerequisites
- Usage guidance and example code
- Key features
- Additional resources

## Setup

### Prerequisites

- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)
- GitHub account (optional, but recommended for higher API rate limits)

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

That's it! The server is now registered and ready to use.

### Optional: GitHub Token

For higher API rate limits, you can add a GitHub personal access token:

1. Create a GitHub personal access token:
   - Go to https://github.com/settings/tokens
   - Generate a new token (classic)
   - Select `public_repo` scope (or just `read:user` for public repos)
   - Copy the token

2. Create a `.env` file:
```bash
cp .env.example .env
```

3. Add your GitHub token to `.env`:
```
GITHUB_TOKEN=your_token_here
```

## Usage

Once installed, the MCP server will be available to any MCP-compatible client (like Claude Desktop). The server exposes three tools that LLMs can use to help users discover and use GitHub projects.

### Example Workflow

**User:** "I need help keeping track of my finances"

1. **LLM calls:** `search_github_projects(task="track my finances", language="Python", max_results=8)`
   - Server returns top 8 Python repos (e.g., firefly-iii, actual, maybe)

2. **LLM calls:** `analyze_github_repository_for_task(owner="firefly-iii", repo="firefly-iii", user_task="track my finances")`
   - Server returns structured guidance including:
     - Why Firefly III helps with finance tracking
     - Docker installation steps
     - Quick start guide
     - Key features (budgets, recurring transactions, reports)

3. **LLM calls:** `get_github_repository_details(owner="firefly-iii", repo="firefly-iii")`
   - Server returns comprehensive metadata:
     - Stars, forks, watchers
     - License information
     - Activity and maintenance status
     - Topics and tags
     - Links to documentation and homepage

4. **LLM synthesizes** the information and guides the user through setup

## Rate Limits

- **Without token**: 60 GitHub API requests per hour
- **With token**: 1000 requests per hour, per repository

Adding a GitHub token is highly recommended to avoid hitting rate limits.

## Architecture

The server is organized into modular components for clean separation of concerns:

### Project Structure

```
├── main.py                    # Entry point and MCP tool registration
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration and constants
│   ├── github_api.py         # GitHub API utilities and HTTP client
│   ├── query_builder.py      # Search query generation logic
│   ├── markdown_parser.py    # README parsing and extraction
│   └── tools.py              # Core business logic for MCP tools
```

### Module Responsibilities

- **`main.py`**: FastMCP server initialization and tool registration
- **`config.py`**: Centralized configuration, constants, and environment variables
- **`github_api.py`**: All GitHub API interactions (search, metadata, README fetching)
- **`query_builder.py`**: Intelligent search query generation with 50+ topic categories
- **`markdown_parser.py`**: README parsing and section extraction
- **`tools.py`**: Business logic that orchestrates the above modules

This modular structure provides:
- Easy testing of individual components
- Clear separation between API integration, logic, and tool definition
- Simple configuration management
- Extensibility for adding new tools or API integrations

### Technology Stack

The server uses:
- **FastMCP**: MCP server framework with decorator-based tool definitions
- **httpx**: Async HTTP client for GitHub API requests
- **markdown-it-py**: Markdown parsing for README extraction
- **python-dotenv**: Environment variable management

### Search Algorithm

Search queries are generated using:
- Synonym expansion across 50+ technical and non-technical topic categories
- GitHub search qualifiers (stars, forks, language, recency)
- Multiple query strategies for comprehensive coverage

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[Specify your license here]
