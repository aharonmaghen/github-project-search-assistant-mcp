# Open Source Discovery MCP Server

An MCP (Model Context Protocol) server that helps LLMs discover and analyze open source projects to assist users in completing specific tasks. This server searches GitHub for relevant repositories, analyzes their documentation, and provides actionable guidance on how to use them.

## Features

- **Intelligent Search**: Converts natural language task descriptions into optimized GitHub queries with synonym expansion and smart filtering
- **Language-Specific Filtering**: Optionally filter results by programming language
- **Comprehensive Analysis**: Extracts and parses README files to provide structured guidance
- **Actionable Insights**: Returns installation steps, usage examples, prerequisites, and feature highlights
- **Repository Metadata**: Provides detailed information about stars, activity, topics, and more

## Tools

### `search_open_source_projects`
Search GitHub for open source projects relevant to a specific task.

**Parameters:**
- `task` (str): Description of what the user wants to accomplish (e.g., "track my personal finances")
- `language` (str, optional): Programming language filter (e.g., "Python", "JavaScript")
- `max_results` (int, optional): Maximum results to return (default: 8, max: 15)

**Returns:** List of repositories with metadata including name, description, stars, language, topics, and URL.

### `get_repository_details`
Get comprehensive metadata for a specific GitHub repository.

**Parameters:**
- `owner` (str): Repository owner (username or organization)
- `repo` (str): Repository name

**Returns:** Detailed repository information including stats, topics, license, activity, and links.

### `analyze_repository_for_task`
Analyze a repository and provide guidance on using it for a specific task.

**Parameters:**
- `owner` (str): Repository owner
- `repo` (str): Repository name
- `user_task` (str): The task the user wants to accomplish

**Returns:** Structured analysis including:
- Why this project helps with the task
- Installation steps and prerequisites
- Usage guidance and example code
- Key features
- Additional resources

## Setup

### Prerequisites

- Python 3.13 or higher
- GitHub account (optional, but recommended for higher API rate limits)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd open-source-mcp-server
```

2. Install dependencies:
```bash
pip install -e .
```

3. (Optional but recommended) Create a GitHub personal access token:
   - Go to https://github.com/settings/tokens
   - Generate a new token (classic)
   - Select `public_repo` scope (or just `read:user` for public repos)
   - Copy the token

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Add your GitHub token to `.env`:
```
GITHUB_TOKEN=your_token_here
```

## Usage

### Running the Server

```bash
python main.py
```

The server runs on streamable HTTP transport and exposes three tools that LLMs can use to help users discover and use open source projects.

### Example Workflow

**User:** "I need help keeping track of my finances"

1. **LLM calls:** `search_open_source_projects("finance tracking budgeting expense personal")`
   - Server returns top 8 repos (e.g., firefly-iii, actual, maybe)

2. **LLM calls:** `analyze_repository_for_task("firefly-iii", "firefly-iii", "track my finances")`
   - Server returns structured guidance including:
     - Why Firefly III helps with finance tracking
     - Docker installation steps
     - Quick start guide
     - Key features (budgets, recurring transactions, reports)

3. **LLM synthesizes** the information and guides the user through setup

## Rate Limits

- **Without token**: 10 GitHub API requests per minute
- **With token**: 30 search requests per minute, 5000 total requests per hour

Adding a GitHub token is highly recommended to avoid hitting rate limits.

## Architecture

The server uses:
- **FastMCP**: MCP server framework with decorator-based tool definitions
- **httpx**: Async HTTP client for GitHub API requests
- **markdown-it-py**: Markdown parsing for README extraction
- **python-dotenv**: Environment variable management

Search queries are generated using:
- Synonym expansion for common terms
- GitHub search qualifiers (stars, language, recency)
- Multiple query strategies for better coverage

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

[Specify your license here]
