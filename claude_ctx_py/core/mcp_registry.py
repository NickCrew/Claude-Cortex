"""MCP Server Registry - Curated catalog of popular MCP servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PackageManager(Enum):
    """Supported package managers for MCP server installation."""
    NPX = "npx"  # Node.js (runs without global install)
    NPM = "npm"  # Node.js (global install)
    PIP = "pip"  # Python
    PIPX = "pipx"  # Python (isolated)
    BREW = "brew"  # Homebrew
    CARGO = "cargo"  # Rust
    BINARY = "binary"  # Direct binary download
    MANUAL = "manual"  # Manual installation required


class ServerCategory(Enum):
    """Categories for MCP servers."""
    DOCUMENTATION = "Documentation"
    CODE_INTELLIGENCE = "Code Intelligence"
    REASONING = "Reasoning"
    DATABASE = "Database"
    WEB = "Web & Browser"
    FILE_SYSTEM = "File System"
    PRODUCTIVITY = "Productivity"
    AI_TOOLS = "AI Tools"
    DEVELOPMENT = "Development"
    OTHER = "Other"


@dataclass
class EnvVarConfig:
    """Configuration for an environment variable."""
    name: str
    description: str
    required: bool = False
    default: Optional[str] = None
    secret: bool = False  # If true, mask input


@dataclass
class MCPServerDefinition:
    """Definition of an MCP server from the registry."""
    name: str
    description: str
    package: str
    package_manager: PackageManager
    category: ServerCategory

    # Installation details
    args: List[str] = field(default_factory=list)
    env_vars: List[EnvVarConfig] = field(default_factory=list)

    # Metadata
    homepage: Optional[str] = None
    docs_url: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Installation hints
    install_notes: Optional[str] = None
    post_install_notes: Optional[str] = None

    def get_command(self) -> str:
        """Get the command to run this server."""
        if self.package_manager == PackageManager.NPX:
            return "npx"
        elif self.package_manager == PackageManager.NPM:
            return self.package.split("/")[-1]  # Global command name
        elif self.package_manager in (PackageManager.PIP, PackageManager.PIPX):
            return self.package.replace("-", "_")  # Python module name
        elif self.package_manager == PackageManager.CARGO:
            return self.package
        else:
            return self.package

    def get_default_args(self) -> List[str]:
        """Get default arguments for the server."""
        if self.package_manager == PackageManager.NPX:
            return ["-y", self.package] + self.args
        return self.args

    def get_install_command(self) -> Optional[List[str]]:
        """Get the command to install this server."""
        if self.package_manager == PackageManager.NPX:
            return None  # npx doesn't need pre-installation
        elif self.package_manager == PackageManager.NPM:
            return ["npm", "install", "-g", self.package]
        elif self.package_manager == PackageManager.PIP:
            return ["pip", "install", self.package]
        elif self.package_manager == PackageManager.PIPX:
            return ["pipx", "install", self.package]
        elif self.package_manager == PackageManager.BREW:
            return ["brew", "install", self.package]
        elif self.package_manager == PackageManager.CARGO:
            return ["cargo", "install", self.package]
        return None


# =============================================================================
# MCP SERVER REGISTRY
# =============================================================================
# Curated list of popular and useful MCP servers

MCP_SERVER_REGISTRY: Dict[str, MCPServerDefinition] = {}


def _register(server: MCPServerDefinition) -> MCPServerDefinition:
    """Register a server in the registry."""
    MCP_SERVER_REGISTRY[server.name] = server
    return server


# -----------------------------------------------------------------------------
# Documentation & Knowledge
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="context7",
    description="Official library documentation lookup. Get up-to-date docs for any library.",
    package="@upstash/context7-mcp",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DOCUMENTATION,
    homepage="https://context7.com",
    author="Upstash",
    tags=["docs", "libraries", "api-reference"],
))

_register(MCPServerDefinition(
    name="brave-search",
    description="Web search using Brave Search API. Search the web from Claude.",
    package="@anthropics/mcp-server-brave-search",
    package_manager=PackageManager.NPX,
    category=ServerCategory.WEB,
    env_vars=[
        EnvVarConfig(
            name="BRAVE_API_KEY",
            description="Brave Search API key (get from brave.com/search/api)",
            required=True,
            secret=True,
        ),
    ],
    homepage="https://brave.com/search/api",
    author="Anthropic",
    tags=["search", "web", "brave"],
))

_register(MCPServerDefinition(
    name="fetch",
    description="Fetch and process web content. Read web pages and extract content.",
    package="@anthropics/mcp-server-fetch",
    package_manager=PackageManager.NPX,
    category=ServerCategory.WEB,
    author="Anthropic",
    tags=["web", "fetch", "scrape"],
))

# -----------------------------------------------------------------------------
# Code Intelligence
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="codanna",
    description="Code intelligence and semantic search. Navigate large codebases with ease.",
    package="codanna",
    package_manager=PackageManager.PIPX,
    category=ServerCategory.CODE_INTELLIGENCE,
    args=["serve", "--watch"],
    homepage="https://github.com/codanna/codanna",
    tags=["code", "search", "navigation", "semantic"],
    install_notes="Requires Python 3.10+",
))

_register(MCPServerDefinition(
    name="github",
    description="GitHub integration. Manage repos, issues, PRs, and more.",
    package="@anthropics/mcp-server-github",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    env_vars=[
        EnvVarConfig(
            name="GITHUB_TOKEN",
            description="GitHub Personal Access Token",
            required=True,
            secret=True,
        ),
    ],
    author="Anthropic",
    tags=["github", "git", "repos", "issues"],
))

# -----------------------------------------------------------------------------
# Reasoning & Thinking
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="sequential-thinking",
    description="Structured multi-step reasoning. Systematic problem-solving and analysis.",
    package="@modelcontextprotocol/server-sequential-thinking",
    package_manager=PackageManager.NPX,
    category=ServerCategory.REASONING,
    author="Model Context Protocol",
    tags=["reasoning", "thinking", "analysis"],
))

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="postgres",
    description="PostgreSQL database integration. Query and manage Postgres databases.",
    package="@anthropics/mcp-server-postgres",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DATABASE,
    env_vars=[
        EnvVarConfig(
            name="POSTGRES_URL",
            description="PostgreSQL connection URL (postgres://user:pass@host:port/db)",
            required=True,
            secret=True,
        ),
    ],
    author="Anthropic",
    tags=["database", "postgres", "sql"],
))

_register(MCPServerDefinition(
    name="sqlite",
    description="SQLite database integration. Query and manage SQLite databases.",
    package="@anthropics/mcp-server-sqlite",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DATABASE,
    args=["--db-path", ""],  # User needs to specify path
    author="Anthropic",
    tags=["database", "sqlite", "sql"],
    install_notes="Specify the database path during configuration.",
))

# -----------------------------------------------------------------------------
# File System
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="filesystem",
    description="File system access. Read, write, and manage files.",
    package="@anthropics/mcp-server-filesystem",
    package_manager=PackageManager.NPX,
    category=ServerCategory.FILE_SYSTEM,
    args=[],  # Paths added during config
    author="Anthropic",
    tags=["files", "filesystem", "read", "write"],
    install_notes="Specify allowed directories during configuration.",
))

_register(MCPServerDefinition(
    name="memory",
    description="Persistent memory across conversations. Remember context and notes.",
    package="@anthropics/mcp-server-memory",
    package_manager=PackageManager.NPX,
    category=ServerCategory.PRODUCTIVITY,
    author="Anthropic",
    tags=["memory", "context", "persistence"],
))

# -----------------------------------------------------------------------------
# Browser & Automation
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="puppeteer",
    description="Browser automation with Puppeteer. Control Chrome programmatically.",
    package="@anthropics/mcp-server-puppeteer",
    package_manager=PackageManager.NPX,
    category=ServerCategory.WEB,
    author="Anthropic",
    tags=["browser", "automation", "puppeteer", "chrome"],
))

_register(MCPServerDefinition(
    name="playwright",
    description="Browser automation with Playwright. Cross-browser testing and automation.",
    package="@anthropics/mcp-server-playwright",
    package_manager=PackageManager.NPX,
    category=ServerCategory.WEB,
    author="Anthropic",
    tags=["browser", "automation", "playwright", "testing"],
))

_register(MCPServerDefinition(
    name="browser-tools",
    description="Browser DevTools integration. Access console, network, and debugging.",
    package="@anthropics/mcp-server-browser-tools",
    package_manager=PackageManager.NPX,
    category=ServerCategory.WEB,
    author="Anthropic",
    tags=["browser", "devtools", "debugging"],
))

# -----------------------------------------------------------------------------
# Productivity
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="slack",
    description="Slack integration. Send messages, read channels, manage workspace.",
    package="@anthropics/mcp-server-slack",
    package_manager=PackageManager.NPX,
    category=ServerCategory.PRODUCTIVITY,
    env_vars=[
        EnvVarConfig(
            name="SLACK_BOT_TOKEN",
            description="Slack Bot OAuth Token (xoxb-...)",
            required=True,
            secret=True,
        ),
    ],
    author="Anthropic",
    tags=["slack", "messaging", "team"],
))

_register(MCPServerDefinition(
    name="google-drive",
    description="Google Drive integration. Access and manage Drive files.",
    package="@anthropics/mcp-server-gdrive",
    package_manager=PackageManager.NPX,
    category=ServerCategory.PRODUCTIVITY,
    env_vars=[
        EnvVarConfig(
            name="GOOGLE_CREDENTIALS_PATH",
            description="Path to Google OAuth credentials JSON file",
            required=True,
        ),
    ],
    author="Anthropic",
    tags=["google", "drive", "files", "cloud"],
))

_register(MCPServerDefinition(
    name="notion",
    description="Notion integration. Access pages, databases, and workspaces.",
    package="@anthropics/mcp-server-notion",
    package_manager=PackageManager.NPX,
    category=ServerCategory.PRODUCTIVITY,
    env_vars=[
        EnvVarConfig(
            name="NOTION_API_KEY",
            description="Notion Integration API Key",
            required=True,
            secret=True,
        ),
    ],
    author="Anthropic",
    tags=["notion", "notes", "wiki", "database"],
))

# -----------------------------------------------------------------------------
# AI Tools
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="exa",
    description="AI-powered web search with Exa. Semantic search and content retrieval.",
    package="@anthropics/mcp-server-exa",
    package_manager=PackageManager.NPX,
    category=ServerCategory.AI_TOOLS,
    env_vars=[
        EnvVarConfig(
            name="EXA_API_KEY",
            description="Exa API Key",
            required=True,
            secret=True,
        ),
    ],
    homepage="https://exa.ai",
    author="Anthropic",
    tags=["search", "ai", "semantic"],
))

_register(MCPServerDefinition(
    name="sentry",
    description="Sentry error tracking integration. Monitor and debug errors.",
    package="@anthropics/mcp-server-sentry",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    env_vars=[
        EnvVarConfig(
            name="SENTRY_AUTH_TOKEN",
            description="Sentry Auth Token",
            required=True,
            secret=True,
        ),
        EnvVarConfig(
            name="SENTRY_ORG",
            description="Sentry Organization Slug",
            required=True,
        ),
    ],
    homepage="https://sentry.io",
    author="Anthropic",
    tags=["sentry", "errors", "monitoring", "debugging"],
))

# -----------------------------------------------------------------------------
# Development Tools
# -----------------------------------------------------------------------------

_register(MCPServerDefinition(
    name="docker",
    description="Docker integration. Manage containers, images, and compose.",
    package="@anthropics/mcp-server-docker",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    author="Anthropic",
    tags=["docker", "containers", "devops"],
))

_register(MCPServerDefinition(
    name="kubernetes",
    description="Kubernetes integration. Manage clusters, pods, and deployments.",
    package="@anthropics/mcp-server-kubernetes",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    author="Anthropic",
    tags=["kubernetes", "k8s", "containers", "devops"],
))

_register(MCPServerDefinition(
    name="aws",
    description="AWS integration. Manage S3, EC2, Lambda, and more.",
    package="@anthropics/mcp-server-aws",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    env_vars=[
        EnvVarConfig(
            name="AWS_ACCESS_KEY_ID",
            description="AWS Access Key ID",
            required=True,
            secret=True,
        ),
        EnvVarConfig(
            name="AWS_SECRET_ACCESS_KEY",
            description="AWS Secret Access Key",
            required=True,
            secret=True,
        ),
        EnvVarConfig(
            name="AWS_REGION",
            description="AWS Region (e.g., us-east-1)",
            required=False,
            default="us-east-1",
        ),
    ],
    author="Anthropic",
    tags=["aws", "cloud", "s3", "lambda"],
))


# =============================================================================
# Registry API Functions
# =============================================================================

def get_all_servers() -> List[MCPServerDefinition]:
    """Get all servers in the registry."""
    return list(MCP_SERVER_REGISTRY.values())


def get_server(name: str) -> Optional[MCPServerDefinition]:
    """Get a server by name."""
    return MCP_SERVER_REGISTRY.get(name)


def get_servers_by_category(category: ServerCategory) -> List[MCPServerDefinition]:
    """Get all servers in a category."""
    return [s for s in MCP_SERVER_REGISTRY.values() if s.category == category]


def search_servers(query: str) -> List[MCPServerDefinition]:
    """Search servers by name, description, or tags."""
    query = query.lower()
    results = []
    for server in MCP_SERVER_REGISTRY.values():
        if (
            query in server.name.lower()
            or query in server.description.lower()
            or any(query in tag.lower() for tag in server.tags)
        ):
            results.append(server)
    return results


def get_categories() -> List[ServerCategory]:
    """Get all categories that have servers."""
    categories = set()
    for server in MCP_SERVER_REGISTRY.values():
        categories.add(server.category)
    return sorted(categories, key=lambda c: c.value)
