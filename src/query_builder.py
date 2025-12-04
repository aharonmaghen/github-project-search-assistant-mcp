"""Search query builder for GitHub repositories."""

import re
from src.config import (
    DEFAULT_STARS_THRESHOLD,
    QUALITY_STARS_THRESHOLD,
    QUALITY_FORKS_THRESHOLD,
)


def build_search_query(task: str, language: str | None = None) -> list[str]:
    """
    Build creative GitHub search queries from a user task.
    Returns multiple query variations for better coverage across technical and non-technical topics.
    """
    # Comprehensive synonym mapping for diverse topic areas
    synonyms = {
        # Financial & Business
        "finance": ["finance", "budget", "expense", "accounting", "money", "financial", "invoice", "ledger"],
        "business": ["business", "company", "enterprise", "startup", "organization"],
        "investment": ["investment", "stock", "portfolio", "trading", "forex"],
        
        # Task Management & Productivity
        "task": ["task", "todo", "todo-list", "checklist", "project-management"],
        "track": ["track", "manage", "monitor", "organize", "oversee", "supervise"],
        "productivity": ["productivity", "time-tracking", "focus", "efficiency", "workflow"],
        "collaboration": ["collaboration", "team", "communication", "project"],
        
        # Knowledge & Documentation
        "notes": ["notes", "note-taking", "notebook", "knowledge", "documentation", "wiki"],
        "learning": ["learning", "education", "tutorial", "course", "training"],
        "research": ["research", "study", "analysis", "data-science"],
        
        # Security & Privacy
        "password": ["password", "credential", "secret", "vault", "security", "authentication"],
        "encryption": ["encryption", "cipher", "cryptography", "secure"],
        "privacy": ["privacy", "anonymity", "data-protection", "gdpr"],
        
        # Web & Frontend
        "web": ["web", "website", "webapp", "frontend", "ui", "ux", "browser"],
        "javascript": ["javascript", "js", "typescript", "react", "vue", "angular"],
        "html-css": ["html", "css", "styling", "design", "template"],
        "responsive": ["responsive", "mobile", "phone", "tablet"],
        
        # Backend & APIs
        "api": ["api", "rest", "graphql", "backend", "server", "endpoint"],
        "authentication": ["authentication", "auth", "oauth", "jwt", "login"],
        "microservice": ["microservice", "service", "distributed", "architecture"],
        
        # Database & Storage
        "database": ["database", "db", "sql", "data-storage", "nosql", "mongodb", "postgres"],
        "cache": ["cache", "caching", "redis", "memcached"],
        "search": ["search", "elasticsearch", "indexing", "query"],
        
        # Real-time & Communication
        "chat": ["chat", "messaging", "communication", "conversation", "messenger"],
        "notification": ["notification", "alert", "push-notification", "email"],
        "realtime": ["realtime", "real-time", "live", "websocket"],
        
        # Content & Publishing
        "blog": ["blog", "cms", "content", "publishing", "article"],
        "static-site": ["static-site", "static", "ssg", "jekyll", "hugo"],
        "markdown": ["markdown", "documentation", "doc", "readme"],
        
        # E-commerce & Shopping
        "ecommerce": ["ecommerce", "shop", "store", "commerce", "selling", "products"],
        "payment": ["payment", "checkout", "stripe", "paypal", "billing"],
        "shopping": ["shopping", "cart", "inventory", "retail"],
        
        # Data & Analytics
        "analytics": ["analytics", "metrics", "tracking", "insights", "monitoring"],
        "logging": ["logging", "log", "logs", "debugging"],
        "visualization": ["visualization", "chart", "graph", "dashboard"],
        
        # Automation & DevOps
        "automation": ["automation", "workflow", "ci-cd", "pipeline", "deployment"],
        "devops": ["devops", "docker", "kubernetes", "container"],
        "monitoring": ["monitoring", "health-check", "alerting", "observability"],
        
        # Machine Learning & AI
        "ml": ["machine-learning", "ml", "ai", "deep-learning", "neural", "tensorflow"],
        "nlp": ["nlp", "natural-language", "text", "language-processing"],
        "computer-vision": ["computer-vision", "image", "opencv", "recognition"],
        "data-science": ["data-science", "data", "analysis", "statistics"],
        
        # Gaming & Graphics
        "game": ["game", "gaming", "game-development", "gamedev", "engine"],
        "graphics": ["graphics", "3d", "rendering", "webgl", "shader"],
        "game-engine": ["game-engine", "unity", "unreal", "godot"],
        
        # Music & Media
        "audio": ["audio", "music", "sound", "dsp", "synthesis"],
        "video": ["video", "streaming", "ffmpeg", "encoding"],
        "media": ["media", "multimedia", "player", "player"],
        
        # IoT & Hardware
        "iot": ["iot", "embedded", "hardware", "microcontroller", "raspberry-pi"],
        "sensor": ["sensor", "arduino", "esp32", "measurement"],
        
        # Mobile Development
        "mobile": ["mobile", "app", "ios", "android", "flutter", "react-native"],
        "app": ["app", "application", "mobile-app", "native"],
        
        # Testing & Quality
        "testing": ["testing", "test", "unittest", "qa", "quality-assurance"],
        "ci": ["ci", "ci-cd", "github-actions", "gitlab-ci"],
        "integration": ["integration", "integration-testing", "e2e"],
        
        # Cloud & Infrastructure
        "cloud": ["cloud", "aws", "azure", "gcp", "cloud-computing"],
        "serverless": ["serverless", "lambda", "function", "faas"],
        "infrastructure": ["infrastructure", "terraform", "iac"],
        
        # Version Control & Collaboration
        "git": ["git", "version-control", "scm", "github", "gitlab"],
        "open-source": ["open-source", "opensource", "foss", "community"],
        
        # Development Tools
        "cli": ["cli", "command-line", "terminal", "shell", "bash"],
        "editor": ["editor", "ide", "vscode", "development-tools"],
        "build": ["build", "compiler", "webpack", "build-tool"],
        
        # Language-Specific
        "python": ["python", "django", "flask", "fastapi"],
        "nodejs": ["nodejs", "node", "express", "npm"],
        "java": ["java", "spring", "maven"],
        "csharp": [".net", "csharp", "dotnet", "asp.net"],
        "ruby": ["ruby", "rails", "sinatra"],
        "go": ["go", "golang", "gin"],
        "rust": ["rust", "cargo", "wasm"],
        "php": ["php", "laravel", "symfony"],
        
        # Utilities & Tools
        "utility": ["utility", "tool", "helper", "library"],
        "parser": ["parser", "lexer", "compiler"],
        "formatter": ["formatter", "linter", "beautifier"],
        
        # Networking
        "network": ["network", "networking", "http", "tcp", "protocol"],
        "vpn": ["vpn", "proxy", "tunnel", "firewall"],
        "dns": ["dns", "dns-server", "domain"],
        
        # Virtualization
        "virtual": ["virtual", "vm", "hypervisor", "vmware"],
    }
    
    # Extract key terms and expand with synonyms
    task_lower = task.lower()
    expanded_terms = set()
    matched_categories = []
    
    for key, values in synonyms.items():
        if key in task_lower or any(v in task_lower for v in values):
            matched_categories.append(key)
            expanded_terms.update(values[:3])  # Use top 3 synonyms
    
    # If no matches, use the task words directly
    if not expanded_terms:
        # Extract meaningful words (filter out common words)
        words = re.findall(r'\b\w{3,}\b', task_lower)
        common_words = {
            "need", "help", "want", "like", "make", "create", "build", "using", 
            "with", "how", "what", "where", "when", "find", "get", "look",
            "can", "will", "should", "could", "would", "does", "don't"
        }
        expanded_terms = {w for w in words if w not in common_words}
    
    # Build queries with various strategies
    queries = []
    
    # Query 1: Broad OR search with popularity filter
    if expanded_terms:
        or_terms = " OR ".join(list(expanded_terms)[:5])
        base_query = f"{or_terms} stars:>{DEFAULT_STARS_THRESHOLD}"
        if language:
            base_query += f" language:{language}"
        queries.append(base_query)
    
    # Query 2: Exact phrase from task + recent activity (2023 onwards)
    task_clean = re.sub(r'\b(i|need|help|want|to|a|an|the|for|and|or|but)\b', '', task_lower).strip()
    if task_clean:
        recent_query = f'"{task_clean}" pushed:>2023-01-01'
        if language:
            recent_query += f" language:{language}"
        queries.append(recent_query)
    
    # Query 3: High quality filter with popularity and activity
    if expanded_terms:
        main_terms = " ".join(list(expanded_terms)[:3])
        quality_query = f"{main_terms} stars:>{QUALITY_STARS_THRESHOLD} forks:>{QUALITY_FORKS_THRESHOLD} pushed:>2023-01-01"
        if language:
            quality_query += f" language:{language}"
        queries.append(quality_query)
    
    # Query 4: Alternative synonyms from different categories
    if len(matched_categories) > 1:
        alt_terms = []
        for cat in matched_categories[1:3]:
            alt_terms.extend(synonyms[cat][:2])
        if alt_terms:
            alt_query = " OR ".join(alt_terms[:4]) + f" stars:>{DEFAULT_STARS_THRESHOLD}"
            if language:
                alt_query += f" language:{language}"
            queries.append(alt_query)
    
    return queries[:3]  # Return top 3 queries for broader coverage
