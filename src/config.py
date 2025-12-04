"""Configuration and constants for the GitHub Project Discovery server."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API configuration
GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Search configuration
DEFAULT_MAX_RESULTS = 8
MAX_RESULTS_LIMIT = 15
DEFAULT_STARS_THRESHOLD = 100
QUALITY_STARS_THRESHOLD = 500
QUALITY_FORKS_THRESHOLD = 50

# README parsing configuration
MARKDOWN_SECTIONS = {
    "installation": "",
    "quickstart": "",
    "usage": "",
    "prerequisites": "",
    "features": "",
    "getting_started": "",
}

INSTALL_PATTERNS = [r'install', r'installation', r'setup', r'getting.?started']
USAGE_PATTERNS = [r'usage', r'how.?to', r'quickstart', r'quick.?start', r'example']
PREREQ_PATTERNS = [r'prerequisite', r'requirement', r'dependencies', r'before']
FEATURE_PATTERNS = [r'feature', r'what', r'about', r'overview']

# HTTP configuration
HTTP_TIMEOUT = 30.0
