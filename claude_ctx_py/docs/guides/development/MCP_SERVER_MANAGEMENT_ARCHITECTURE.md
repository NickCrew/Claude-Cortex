# MCP Server Management System Architecture

**Technical Documentation** | Version 1.0 | Last Updated: December 6, 2025

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Core Architecture](#core-architecture)
4. [Server Discovery & Validation](#server-discovery--validation)
5. [Server Registry](#server-registry)
6. [Installation System](#installation-system)
7. [Configuration Management](#configuration-management)
8. [TUI Integration](#tui-integration)
9. [CLI Commands](#cli-commands)
10. [Data Models](#data-models)
11. [Developer Guide](#developer-guide)
12. [Performance & Best Practices](#performance--best-practices)

---

## Executive Summary

The **MCP Server Management System** provides comprehensive tools for discovering, validating, configuring, and managing Model Context Protocol (MCP) servers within Claude Desktop. It bridges the gap between Claude Code's AI capabilities and external data sources/tools through a curated registry, automated installation, and interactive management interfaces.

### Key Capabilities

- ✅ **Cross-platform server discovery** (macOS, Linux, Windows)
- ✅ **Curated server registry** with 25+ pre-configured popular MCP servers
- ✅ **Automated installation** with package manager detection
- ✅ **Configuration validation** with detailed error reporting
- ✅ **TUI browser & manager** (Key `7` for quick access)
- ✅ **Documentation integration** with local docs cache
- ✅ **Environment variable management** with secret masking
- ✅ **Config snippet generation** for easy setup

### Technology Stack

- **Core**: Python 3.9+ with dataclasses and Path-based I/O
- **Config Format**: JSON (Claude Desktop's `claude_desktop_config.json`)
- **TUI**: Textual framework with modal dialogs
- **Registry**: Enum-based categorization with 10 server categories
- **Docs**: Markdown files in `~/.claude/mcp/docs/`

---

## System Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Management System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Discovery  │  │   Registry   │  │  Installer   │          │
│  │   (mcp.py)   │  │ (registry.py)│  │(installer.py)│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                   │
│                            │                                      │
│         ┌──────────────────┴──────────────────┐                  │
│         │                                      │                  │
│  ┌──────▼───────┐                    ┌────────▼─────────┐        │
│  │     TUI      │                    │       CLI        │        │
│  │ (tui_mcp.py) │                    │ (mcp commands)   │        │
│  └──────┬───────┘                    └────────┬─────────┘        │
│         │                                      │                  │
│         └──────────────────┬──────────────────┘                  │
│                            │                                      │
│         ┌──────────────────▼──────────────────┐                  │
│         │   Claude Desktop Config             │                  │
│         │   ~/.../Claude/claude_desktop_       │                  │
│         │   config.json                       │                  │
│         └─────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Action → TUI/CLI → Discovery/Registry → Validation → Config Modification
                ↓
            Docs Lookup ← ~/.claude/mcp/docs/*.md
                ↓
        Installation → Package Manager (npx/pip/pipx/brew/cargo)
                ↓
        Config Update → claude_desktop_config.json
```

---

## Core Architecture

### Module Structure

#### `core/mcp.py` (1,070 lines)

**Purpose**: Core MCP server discovery, validation, and configuration management.

**Key Components**:

- `MCPServerInfo`: Dataclass representing server configuration
- `MCPServerCapabilities`: Server capabilities and metadata (tools, resources, prompts)
- Platform-specific config path resolution
- Server discovery and validation functions
- Config modification operations (add, remove, update)

**Critical Functions**:

```python
def discover_servers(config_path: Optional[Path] = None) -> Tuple[bool, List[MCPServerInfo], str]
def get_server_info(name: str, config_path: Optional[Path] = None) -> Tuple[bool, Optional[MCPServerInfo], str]
def validate_server_config(name: str, config_path: Optional[Path] = None) -> Tuple[bool, List[str], List[str]]
def add_mcp_server(name: str, command: str, args: Optional[List[str]] = None, ...) -> Tuple[bool, str]
```

#### `core/mcp_registry.py` (503 lines)

**Purpose**: Curated catalog of popular MCP servers with installation metadata.

**Key Components**:

- `PackageManager` enum: NPX, NPM, PIP, PIPX, BREW, CARGO, BINARY, MANUAL
- `ServerCategory` enum: 10 categories (Documentation, Code Intelligence, Reasoning, etc.)
- `EnvVarConfig`: Environment variable configuration with secret masking
- `MCPServerDefinition`: Complete server definition with install commands
- Registry of 25+ pre-configured servers

**Popular Servers**:

- **context7**: Official library documentation lookup
- **codanna**: Code intelligence and semantic search
- **brave-search**: Web search using Brave API
- **sequential-thinking**: Structured multi-step reasoning
- **github**: GitHub integration (repos, PRs, issues)
- **postgres/sqlite**: Database integrations
- **puppeteer/playwright**: Browser automation

#### `core/mcp_installer.py` (310 lines)

**Purpose**: Automated installation and configuration of MCP servers.

**Key Components**:

- `InstallResult`: Installation outcome with warnings
- Package manager availability checking
- Installation command execution with 5-minute timeout
- Environment variable collection and validation
- Integrated config generation and registration

**Installation Flow**:

```python
install_and_configure(server, env_values, extra_args)
    ↓
1. check_package_manager() → Verify npx/pip/etc available
2. install_package() → Run installation command
3. configure_server() → Build config with env vars
4. add_mcp_server() → Register in Claude Desktop config
```

#### `tui_mcp.py` (433 lines)

**Purpose**: TUI mixin providing interactive MCP server management.

**Key Components**:

- `MCPViewMixin`: Mixin class for TUI integration
- Server list view with status indicators
- Detailed server view with validation
- Keyboard navigation (j/k, Enter, Esc, t, d, c, v, r)
- Documentation viewer
- Config snippet generation with clipboard support

---

## Server Discovery & Validation

### Platform-Specific Config Paths

```python
def _get_claude_config_path() -> Path:
    # macOS
    ~/Library/Application Support/Claude/claude_desktop_config.json
    
    # Linux
    ~/.config/Claude/claude_desktop_config.json
    
    # Windows
    %APPDATA%/Claude/claude_desktop_config.json
```

### Discovery Process

**Step 1: Locate Config File**

```python
config_path = _get_claude_config_path()
if not config_path.exists():
    return False, [], "Config file not found"
```

**Step 2: Parse JSON**

```python
config = json.loads(config_path.read_text(encoding="utf-8"))
mcp_servers = config.get("mcpServers", {})
```

**Step 3: Extract Server Definitions**

```python
for name, server_config in mcp_servers.items():
    command = server_config.get("command", "")
    args = server_config.get("args", [])
    env = server_config.get("env", {})
    
    docs_path = get_server_docs_path(name)
    
    server = MCPServerInfo(
        name=name,
        command=command,
        args=args,
        env=env,
        docs_path=docs_path
    )
```

**Step 4: Documentation Lookup**

```python
def get_server_docs_path(name: str, claude_dir: Optional[Path] = None) -> Optional[Path]:
    docs_dir = claude_dir / "mcp" / "docs"
    exact_path = docs_dir / f"{name}.md"
    
    if exact_path.is_file():
        return exact_path
    
    # Case-insensitive fallback
    for doc_file in docs_dir.glob("*.md"):
        if doc_file.stem.lower() == name.lower():
            return doc_file
    
    return None
```

### Doc-Only Servers

Servers with documentation but no configuration entry are tracked separately:

```python
def list_doc_only_servers(configured_names: Iterable[str], claude_dir: Optional[Path] = None) -> List[MCPServerInfo]:
    docs_dir = claude_dir / "mcp" / "docs"
    configured = {name.lower() for name in configured_names}
    
    doc_servers = []
    for doc_path in sorted(docs_dir.glob("*.md")):
        name = doc_path.stem
        if name.lower() not in configured:
            doc_servers.append(MCPServerInfo(
                name=name,
                command="",
                description="Documentation installed – server not configured",
                docs_path=doc_path,
                doc_only=True
            ))
    
    return doc_servers
```

### Validation System

**Three-Level Validation**:

1. **Structural**: Name and command required
2. **Executable**: Command exists (for absolute paths)
3. **Documentation**: Docs availability (warning, not error)

```python
def validate_server_config(name: str, config_path: Optional[Path] = None) -> Tuple[bool, List[str], List[str]]:
    success, server, error = get_server_info(name, config_path)
    if not success:
        return False, [error], []
    
    errors = []
    warnings = []
    
    # Basic validation
    if not server.name:
        errors.append("Server name is required")
    if not server.command:
        errors.append("Server command is required")
    
    # Command existence check
    if os.path.isabs(server.command):
        if not Path(server.command).exists():
            errors.append(f"Command not found: {server.command}")
    
    # Documentation check
    if server.docs_path is None:
        warnings.append(f"No documentation found for '{name}'")
    
    # Environment variable validation
    if server.env:
        for key, value in server.env.items():
            if not key:
                errors.append("Environment variable name cannot be empty")
            if value == "" or value is None:
                warnings.append(f"Environment variable '{key}' has empty value")
    
    return len(errors) == 0, errors, warnings
```

---

## Server Registry

### Registry Structure

The registry contains 25+ curated MCP servers organized by category with complete installation metadata.

#### Category Distribution

| Category | Servers | Examples |
|----------|---------|----------|
| Documentation | 1 | context7 |
| Code Intelligence | 2 | codanna, github |
| Reasoning | 1 | sequential-thinking |
| Database | 2 | postgres, sqlite |
| Web & Browser | 5 | brave-search, fetch, puppeteer, playwright, browser-tools |
| File System | 2 | filesystem, memory |
| Productivity | 4 | slack, google-drive, notion |
| AI Tools | 2 | exa, sentry |
| Development | 3 | docker, kubernetes, aws |

### Server Definition Example

```python
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
```

### Registry API

```python
# Lookup functions
def get_server(name: str) -> Optional[MCPServerDefinition]
def get_all_servers() -> List[MCPServerDefinition]
def get_servers_by_category(category: ServerCategory) -> List[MCPServerDefinition]
def search_servers(query: str) -> List[MCPServerDefinition]
def get_categories() -> List[ServerCategory]

# Example usage
server = get_server("context7")
if server:
    print(f"Install with: {server.get_install_command()}")
    print(f"Run with: {server.get_command()} {' '.join(server.get_default_args())}")
```

### Environment Variable Configuration

```python
@dataclass
class EnvVarConfig:
    name: str                  # ENV_VAR_NAME
    description: str           # Human-readable description
    required: bool = False     # Must be provided?
    default: Optional[str] = None  # Default value
    secret: bool = False       # Mask in UI (passwords, API keys)
```

**Secret Masking Example**:

```python
if env_var.secret:
    # Mask sensitive values in displays
    display_value = "*" * 8
```

---

## Installation System

### Installation Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                     Installation Flow                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. User selects server from registry                        │
│                     ↓                                        │
│  2. Check package manager availability                       │
│     (npx, pip, pipx, brew, cargo)                            │
│                     ↓                                        │
│  3. Collect required environment variables                   │
│     (API keys, database URLs, etc.)                          │
│                     ↓                                        │
│  4. Install package (if needed)                              │
│     - NPX: Skip (runs without install)                       │
│     - Others: Run install command with 5min timeout          │
│                     ↓                                        │
│  5. Build configuration                                      │
│     - Command + args                                         │
│     - Environment variables                                  │
│     - Description                                            │
│                     ↓                                        │
│  6. Register in Claude Desktop config                        │
│     - Read existing config                                   │
│     - Add to mcpServers section                              │
│     - Write JSON with pretty formatting                      │
│                     ↓                                        │
│  7. Verify installation                                      │
│     - Validate config                                        │
│     - Check for warnings                                     │
│     - Confirm server appears in discovery                    │
│                     ↓                                        │
│  8. Success notification with warnings (if any)              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Package Manager Detection

```python
def check_package_manager(pm: PackageManager) -> Tuple[bool, str]:
    cmd_map = {
        PackageManager.NPX: "npx",
        PackageManager.NPM: "npm",
        PackageManager.PIP: "pip",
        PackageManager.PIPX: "pipx",
        PackageManager.BREW: "brew",
        PackageManager.CARGO: "cargo",
    }
    
    cmd = cmd_map.get(pm)
    path = shutil.which(cmd)
    
    if path:
        return True, path
    return False, f"{cmd} not found in PATH"
```

### Installation Execution

```python
def install_package(server: MCPServerDefinition) -> InstallResult:
    # Check availability
    available, path_or_error = check_package_manager(server.package_manager)
    if not available:
        return InstallResult(success=False, message=path_or_error)
    
    # NPX doesn't need pre-installation
    if server.package_manager == PackageManager.NPX:
        return InstallResult(
            success=True,
            message="NPX packages don't require pre-installation",
            server_name=server.name
        )
    
    # Get install command
    install_cmd = server.get_install_command()
    if not install_cmd:
        return InstallResult(success=False, message="No install command available")
    
    # Run installation with timeout
    try:
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        
        if result.returncode == 0:
            return InstallResult(
                success=True,
                message=f"Successfully installed {server.package}",
                server_name=server.name
            )
        else:
            return InstallResult(
                success=False,
                message=f"Installation failed: {result.stderr or result.stdout}"
            )
    
    except subprocess.TimeoutExpired:
        return InstallResult(success=False, message="Installation timed out after 5 minutes")
    except Exception as e:
        return InstallResult(success=False, message=f"Installation error: {str(e)}")
```

### Configuration Generation

```python
def configure_server(
    server: MCPServerDefinition,
    env_values: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None
) -> InstallResult:
    command = server.get_command()
    args = server.get_default_args() + (extra_args or [])
    
    # Build environment dict
    env = {}
    warnings = []
    
    for env_var in server.env_vars:
        if env_var.name in env_values:
            env[env_var.name] = env_values[env_var.name]
        elif env_var.default:
            env[env_var.name] = env_var.default
        elif env_var.required:
            warnings.append(f"Missing required env var: {env_var.name}")
    
    # Add to Claude config
    success, message = add_mcp_server(
        name=server.name,
        command=command,
        args=args,
        env=env if env else None,
        description=server.description
    )
    
    return InstallResult(
        success=success,
        message=message,
        server_name=server.name,
        warnings=warnings
    )
```

---

## Configuration Management

### Config File Structure

**Location**: Platform-specific (see Discovery section)

**Format**:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      },
      "description": "Web search using Brave Search API"
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropics/mcp-server-postgres"],
      "env": {
        "POSTGRES_URL": "postgres://user:pass@localhost:5432/dbname"
      }
    }
  }
}
```

### Add Server Operation

```python
def add_mcp_server(
    name: str,
    command: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    description: str = "",
    config_path: Optional[Path] = None
) -> Tuple[bool, str]:
    if config_path is None:
        config_path = _get_claude_config_path()
    
    # Validation
    if not name:
        return False, "Server name is required"
    if not command:
        return False, "Server command is required"
    
    # Read existing config
    try:
        if config_path.exists():
            text = config_path.read_text(encoding="utf-8")
            config = json.loads(text)
        else:
            config = {}
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Check if server already exists
    if name in config["mcpServers"]:
        return False, f"Server '{name}' already exists. Use update to modify it."
    
    # Create server config
    server_config = {"command": command}
    if args:
        server_config["args"] = args
    if env:
        server_config["env"] = env
    if description:
        server_config["description"] = description
    
    # Add server
    config["mcpServers"][name] = server_config
    
    # Write config
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8"
        )
        return True, f"Added server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"
```

### Remove Server Operation

```python
def remove_mcp_server(name: str, config_path: Optional[Path] = None) -> Tuple[bool, str]:
    if config_path is None:
        config_path = _get_claude_config_path()
    
    if not config_path.exists():
        return False, f"Config file not found: {config_path}"
    
    # Read config
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"
    
    # Validate structure
    if "mcpServers" not in config or not isinstance(config["mcpServers"], dict):
        return False, "No MCP servers configured"
    
    # Check existence
    if name not in config["mcpServers"]:
        return False, f"Server '{name}' not found"
    
    # Remove server
    del config["mcpServers"][name]
    
    # Write config
    try:
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8"
        )
        return True, f"Removed server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"
```

### Update Server Operation

```python
def update_mcp_server(
    name: str,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
    config_path: Optional[Path] = None
) -> Tuple[bool, str]:
    if config_path is None:
        config_path = _get_claude_config_path()
    
    if not config_path.exists():
        return False, f"Config file not found: {config_path}"
    
    # Read config
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"
    
    # Validate structure
    if "mcpServers" not in config or not isinstance(config["mcpServers"], dict):
        return False, "No MCP servers configured"
    
    # Check existence
    if name not in config["mcpServers"]:
        return False, f"Server '{name}' not found"
    
    # Update server config (selective updates)
    server_config = config["mcpServers"][name]
    if command is not None:
        server_config["command"] = command
    if args is not None:
        server_config["args"] = args
    if env is not None:
        server_config["env"] = env
    if description is not None:
        server_config["description"] = description
    
    # Write config
    try:
        config_path.write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8"
        )
        return True, f"Updated server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"
```

---

## TUI Integration

### Access Key: `7`

Press `7` from any TUI view to open the MCP Servers management screen.

```python
def action_view_mcp(self) -> None:
    """Switch to MCP servers view."""
    self.current_view = "mcp"
    self.load_mcp_servers()
    self.status_message = "Switched to MCP"
    self.notify("🛰 MCP Servers", severity="information", timeout=1)
```

### TUI View Structure

```
┌───────────────────────────────────────────────────────────────┐
│                      MCP Servers                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  Status │ Server Name      │ Command    │ Args    │ Docs     │
│  ───────┼──────────────────┼────────────┼─────────┼─────────  │
│  ● >    │ context7         │ npx        │ -y @... │ ✓        │
│  ●      │ brave-search     │ npx        │ -y @... │ ✓        │
│  ●      │ codanna          │ codanna    │ serve   │ ✓        │
│  -      │ github (docs)    │ -          │ -       │ ✓        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Filter: context                                               │
│ Controls: Enter=Details  t=Test  d=Docs  c=Copy Config       │
│           /=Filter  r=Reload                                  │
└───────────────────────────────────────────────────────────────┘
```

### Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| `j` / `↓` | Navigate down | Move to next server |
| `k` / `↑` | Navigate up | Move to previous server |
| `Enter` | Show details | Open detailed server view |
| `Esc` | Back | Return to server list from details |
| `t` | Test | Validate server configuration |
| `d` | Docs | View server documentation |
| `c` | Copy config | Generate and copy config snippet |
| `v` | Validate | Run full validation check |
| `/` | Filter | Filter servers by name/command/description |
| `r` | Reload | Refresh server list from config |

### Server List View

**Columns**:

- **Selection Indicator**: `>` marks current selection
- **Status**: `●` (green) for configured servers, `-` (dim) for doc-only
- **Server Name**: Cyan text
- **Command**: Truncated if long
- **Args**: Truncated to 18 chars with `...`
- **Docs**: `✓` (green) if available, `-` (dim) if missing

**Rendering Code**:

```python
def _render_mcp_list(self) -> Panel:
    servers = self.get_filtered_servers()
    
    table = Table(show_header=True, header_style="bold magenta", expand=True)
    table.add_column("", width=2)           # Selection
    table.add_column("Status", width=6)     # Status indicator
    table.add_column("Server Name", style="cyan")
    table.add_column("Command", width=30)
    table.add_column("Args", width=20)
    table.add_column("Docs", width=4)
    
    for idx, server in enumerate(servers):
        is_selected = idx == self.state.selected_index
        indicator = ">" if is_selected else ""
        
        status = Text("●", style="green")
        
        args_text = " ".join(server.args) if server.args else "-"
        if len(args_text) > 18:
            args_text = args_text[:15] + "..."
        
        docs_text = Text("✓", style="green") if server.docs_path else Text("-", style="dim")
        
        row_style = "reverse" if is_selected else None
        
        table.add_row(
            indicator,
            status,
            server.name,
            server.command,
            args_text,
            docs_text,
            style=row_style
        )
    
    return Panel(table, title="MCP Servers", border_style="cyan")
```

### Server Details View

**Information Displayed**:

- **Server Name**: Bold cyan header
- **Command**: Full command path
- **Arguments**: Bulleted list
- **Environment Variables**: Key-value pairs with secret masking
- **Documentation**: Path if available, error if missing
- **Configuration Status**: Valid/Invalid with error list
- **Full Command**: Preview of complete command line

**Secret Masking**:

```python
# Mask sensitive values in details view
if any(sensitive in key.lower() for sensitive in ["key", "secret", "token", "password"]):
    display_value = "*" * 8
else:
    display_value = value
```

**Validation Display**:

```python
is_valid, errors = server.is_valid()
if is_valid:
    content.append("  ✓ Valid configuration\n", style="green")
else:
    content.append("  ✗ Configuration errors:\n", style="red")
    for error in errors:
        content.append(f"    • {error}\n", style="red")
```

### MCP Browse Dialog

**Purpose**: Interactive browser for selecting servers from the curated registry to install.

**Features**:

- **Category Navigation**: Left sidebar with 10 categories + "All Servers"
- **Server List**: Right panel with search functionality
- **Status Indicators**: ✓ for installed servers, ⚠️ for missing package managers
- **Real-time Search**: Filter by name, description, or tags
- **Interactive Selection**: Click or Enter to select

**Dialog Layout**:

```
┌──────────────────────────────────────────────────────────────┐
│               🔌 Browse MCP Servers                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┬──────────────────────────────────────┐│
│  │ Categories       │ Servers                              ││
│  ├──────────────────┼──────────────────────────────────────┤│
│  │ 📋 All Servers   │ context7 ✓                          ││
│  │ 📚 Documentation │ Official library documentation      ││
│  │ 🧠 Code Intel... │                                      ││
│  │ 💭 Reasoning     │ brave-search ⚠️                      ││
│  │ 🗄️  Database     │ Web search using Brave API          ││
│  │ 🌐 Web & Browser │                                      ││
│  │ 📁 File System   │ codanna                             ││
│  │ ⚡ Productivity  │ Code intelligence and search        ││
│  │ 🤖 AI Tools      │                                      ││
│  │ 🛠️  Development  │ ...                                  ││
│  └──────────────────┴──────────────────────────────────────┘│
│                                                              │
│  [Search servers...]                                         │
│                                                              │
│  ↑/↓ Navigate • Enter Select • / Search • Esc Cancel        │
│                                                              │
│  [Install Selected]  [Cancel]                                │
└──────────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
class MCPBrowseDialog(ModalScreen[Optional[str]]):
    def on_mount(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        
        # Add "All" option
        all_item = ListItem(Static("📋 All Servers"), id="cat-all")
        category_list.append(all_item)
        
        # Add categories with icons
        category_icons = {
            ServerCategory.DOCUMENTATION: "📚",
            ServerCategory.CODE_INTELLIGENCE: "🧠",
            ServerCategory.REASONING: "💭",
            # ... more categories
        }
        
        for category in get_categories():
            icon = category_icons.get(category, "📦")
            item = ListItem(
                Static(f"{icon} {category.value}"),
                id=f"cat-{category.name.lower()}"
            )
            category_list.append(item)
        
        # Load all servers by default
        self._load_all_servers()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id = event.item.id or ""
        
        if item_id.startswith("cat-"):
            # Category selection
            cat_name = item_id[4:]
            if cat_name == "all":
                self._load_all_servers()
            else:
                for cat in ServerCategory:
                    if cat.name.lower() == cat_name:
                        self._load_category_servers(cat)
                        break
        elif item_id.startswith("srv-"):
            # Server selection
            self.selected_server = item_id[4:]
    
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            query = event.value.strip()
            if query:
                self.servers = search_servers(query)
            else:
                self._load_all_servers()
            self._update_server_list()
```

### MCP Install Dialog

**Purpose**: Configure environment variables and install selected MCP server.

**Features**:

- **Server Information**: Name, package, category, description
- **Requirements Display**: Package manager availability
- **Environment Variable Collection**: Masked input for secrets
- **Install Notes**: Special instructions or warnings
- **Validation**: Required fields must be filled

**Dialog Layout**:

```
┌──────────────────────────────────────────────────────────────┐
│               🔧 Install brave-search                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Server Information                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Name: brave-search                                   │   │
│  │ Package: @anthropics/mcp-server-brave-search        │   │
│  │ Category: Web & Browser                              │   │
│  │                                                      │   │
│  │ Web search using Brave Search API. Search the web   │   │
│  │ from Claude.                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Requirements                                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Package Manager: npx ✓                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Environment Variables                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ BRAVE_API_KEY *                                      │   │
│  │ Brave Search API key (get from brave.com/search/api)│   │
│  │ [********************]                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Ctrl+S Install • Esc Cancel                                 │
│                                                              │
│  [Install & Configure]  [Cancel]                             │
└──────────────────────────────────────────────────────────────┘
```

**Implementation**:

```python
class MCPInstallDialog(ModalScreen[Optional[Dict]]):
    def __init__(self, server_name: str) -> None:
        super().__init__()
        self.server_name = server_name
        self.server = get_server(server_name)
        self.requirements = get_server_requirements(self.server) if self.server else {}
    
    def compose(self) -> ComposeResult:
        # Server info section
        with Vertical(id="server-info"):
            yield Static("[bold]Server Information[/bold]")
            yield Static(f"[cyan]Name:[/cyan] {self.server.name}")
            yield Static(f"[cyan]Package:[/cyan] {self.server.package}")
            yield Static(f"[cyan]Category:[/cyan] {self.server.category.value}")
            yield Static(f"\n{self.server.description}")
        
        # Requirements section
        with Vertical(id="requirements"):
            yield Static("[bold]Requirements[/bold]")
            pm_status = "✓" if self.requirements["pm_available"] else "✗"
            pm_color = "green" if self.requirements["pm_available"] else "red"
            yield Static(
                f"[cyan]Package Manager:[/cyan] {self.requirements['package_manager']} "
                f"[{pm_color}]{pm_status}[/{pm_color}]"
            )
        
        # Environment variables section
        if self.requirements["env_vars"]:
            with VerticalScroll(id="env-vars-container"):
                yield Static("[bold]Environment Variables[/bold]")
                
                for env_var in self.requirements["env_vars"]:
                    required_marker = " [red]*[/red]" if env_var["required"] else ""
                    yield Label(f"{env_var['name']}{required_marker}")
                    yield Static(f"[dim]{env_var['description']}[/dim]")
                    yield Input(
                        placeholder=env_var.get("default", ""),
                        password=env_var.get("secret", False),
                        id=f"env-{env_var['name']}"
                    )
    
    def action_install(self) -> None:
        # Collect environment variable values
        env_values = {}
        for env_var in self.requirements.get("env_vars", []):
            try:
                input_widget = self.query_one(f"#env-{env_var['name']}", Input)
                value = input_widget.value.strip()
                if value:
                    env_values[env_var["name"]] = value
                elif env_var.get("default"):
                    env_values[env_var["name"]] = env_var["default"]
            except Exception:
                pass
        
        self.dismiss({
            "server_name": self.server_name,
            "env_values": env_values
        })
```

---

## CLI Commands

### `mcp:list` - List All MCP Servers

**Purpose**: Display all configured MCP servers with status indicators.

**Usage**:

```bash
cortex mcp:list
```

**Output Example**:

```
MCP Servers:

✓ context7
  Command: npx
  Args: -y @upstash/context7-mcp
  Docs: /Users/user/.claude/mcp/docs/context7.md

✓ brave-search
  Command: npx
  Args: -y @anthropics/mcp-server-brave-search
  Env: BRAVE_API_KEY
  Docs: /Users/user/.claude/mcp/docs/brave-search.md

✗ broken-server
  Command: /path/to/missing
  Error: Command not found: /path/to/missing
```

### `mcp:show <server>` - Show Server Details

**Purpose**: Display detailed information about a specific MCP server.

**Usage**:

```bash
cortex mcp:show context7
```

**Output Example**:

```
MCP Server: context7

Command: npx

Arguments:
  - -y
  - @upstash/context7-mcp

Documentation: /Users/user/.claude/mcp/docs/context7.md

Status: Valid
```

### `mcp:docs <server>` - View Server Documentation

**Purpose**: Display local documentation for an MCP server.

**Usage**:

```bash
cortex mcp:docs context7
```

**Output**: Full markdown content of the documentation file.

### `mcp:test <server>` - Test Server Configuration

**Purpose**: Validate server configuration and check command availability.

**Usage**:

```bash
cortex mcp:test context7
```

**Output Example**:

```
Testing MCP Server: context7

✓ Configuration is valid

Command:
  npx -y @upstash/context7-mcp

✓ Documentation found: /Users/user/.claude/mcp/docs/context7.md
```

### `mcp:diagnose` - Diagnose All Servers

**Purpose**: Run comprehensive validation on all configured servers.

**Usage**:

```bash
cortex mcp:diagnose
```

**Output Example**:

```
MCP Server Diagnostics
============================================================

✓ PASS context7
  No issues found

✓ PASS brave-search
  Warning: Environment variable 'BRAVE_API_KEY' has empty value

✗ FAIL broken-server
  Error: Command not found: /path/to/missing

============================================================
Some servers have errors ✗
```

### `mcp:snippet <server>` - Generate Config Snippet

**Purpose**: Generate JSON config snippet for easy copy-paste.

**Usage**:

```bash
cortex mcp:snippet context7
```

**Output Example**:

```json
// Add this to your Claude Desktop config under 'mcpServers':
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ]
    }
  }
}
```

---

## Data Models

### MCPServerInfo

**Purpose**: Represents a discovered MCP server configuration.

```python
@dataclass
class MCPServerInfo:
    """Information about an MCP server configuration."""
    
    name: str                              # Server identifier
    command: str                           # Executable command
    args: List[str] = field(default_factory=list)  # Command line arguments
    env: Dict[str, str] = field(default_factory=dict)  # Environment variables
    description: str = ""                  # Optional server description
    tools: List[str] = field(default_factory=list)  # Available tools/capabilities
    docs_path: Optional[Path] = None       # Path to local documentation
    doc_only: bool = False                 # True if docs exist but server not configured
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "description": self.description,
            "tools": self.tools,
            "docs_path": str(self.docs_path) if self.docs_path else None,
            "doc_only": self.doc_only,
        }
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate server configuration."""
        errors = []
        
        if not self.name:
            errors.append("Server name is required")
        
        if not self.command:
            errors.append("Server command is required")
        
        # Check if command exists (basic validation)
        if self.command and os.path.isabs(self.command):
            if not Path(self.command).exists():
                errors.append(f"Command not found: {self.command}")
        
        return len(errors) == 0, errors
```

### MCPServerCapabilities

**Purpose**: Represents server capabilities and metadata (future expansion).

```python
@dataclass
class MCPServerCapabilities:
    """MCP server capabilities and metadata."""
    
    tools: List[str] = field(default_factory=list)          # Available tool names
    resources: List[str] = field(default_factory=list)      # Available resources
    prompts: List[str] = field(default_factory=list)        # Available prompts
    version: str = ""                                       # Server/protocol version
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata
```

### MCPServerDefinition

**Purpose**: Registry entry with complete server definition and installation metadata.

```python
@dataclass
class MCPServerDefinition:
    """Definition of an MCP server from the registry."""
    
    name: str                              # Server identifier
    description: str                       # Human-readable description
    package: str                           # Package name (npm, PyPI, etc.)
    package_manager: PackageManager        # Installation method
    category: ServerCategory               # Classification category
    
    # Installation details
    args: List[str] = field(default_factory=list)  # Default arguments
    env_vars: List[EnvVarConfig] = field(default_factory=list)  # Environment variables
    
    # Metadata
    homepage: Optional[str] = None         # Project homepage URL
    docs_url: Optional[str] = None         # Official documentation URL
    author: Optional[str] = None           # Author/maintainer
    tags: List[str] = field(default_factory=list)  # Search tags
    
    # Installation hints
    install_notes: Optional[str] = None    # Pre-install notes
    post_install_notes: Optional[str] = None  # Post-install notes
    
    def get_command(self) -> str:
        """Get the command to run this server."""
        if self.package_manager == PackageManager.NPX:
            return "npx"
        elif self.package_manager == PackageManager.NPM:
            return self.package.split("/")[-1]  # Global command name
        elif self.package_manager in (PackageManager.PIP, PackageManager.PIPX):
            return self.package.replace("-", "_")  # Python module name
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
```

### EnvVarConfig

**Purpose**: Configuration for an environment variable requirement.

```python
@dataclass
class EnvVarConfig:
    """Configuration for an environment variable."""
    
    name: str                    # ENV_VAR_NAME (uppercase by convention)
    description: str             # Human-readable description
    required: bool = False       # Must be provided for server to work
    default: Optional[str] = None  # Default value if not provided
    secret: bool = False         # Mask in UI (passwords, API keys, tokens)
```

### InstallResult

**Purpose**: Result of an installation attempt with warnings.

```python
@dataclass
class InstallResult:
    """Result of an installation attempt."""
    
    success: bool                          # Installation succeeded
    message: str                           # Success/error message
    server_name: Optional[str] = None      # Server identifier
    warnings: List[str] = field(default_factory=list)  # Non-fatal warnings
```

---

## Developer Guide

### Adding a New Server to Registry

**Step 1: Define Server**

```python
# In core/mcp_registry.py

_register(MCPServerDefinition(
    name="my-awesome-server",
    description="Short, compelling description of what the server does",
    package="@org/mcp-server-my-awesome",
    package_manager=PackageManager.NPX,
    category=ServerCategory.DEVELOPMENT,
    
    # Optional: Arguments
    args=["--option", "value"],
    
    # Optional: Environment variables
    env_vars=[
        EnvVarConfig(
            name="MY_API_KEY",
            description="API key from provider.com/keys",
            required=True,
            secret=True,
        ),
        EnvVarConfig(
            name="MY_CONFIG_PATH",
            description="Path to config file",
            required=False,
            default="~/.my-config",
        ),
    ],
    
    # Optional: Metadata
    homepage="https://github.com/org/mcp-server-my-awesome",
    docs_url="https://my-awesome-docs.com",
    author="Your Name",
    tags=["awesome", "useful", "cool"],
    
    # Optional: Installation notes
    install_notes="Requires Node.js 18+ and some-dependency",
    post_install_notes="Run 'my-awesome init' after installation",
))
```

**Step 2: Add Documentation**

Create `/Users/user/.claude/mcp/docs/my-awesome-server.md`:

```markdown
# My Awesome Server

## Overview
Brief description of server capabilities.

## Installation
Installation instructions and requirements.

## Configuration
Environment variables and configuration options.

## Usage
How to use the server with Claude.

## Troubleshooting
Common issues and solutions.

## Links
- Homepage: https://github.com/org/mcp-server-my-awesome
- Docs: https://my-awesome-docs.com
```

**Step 3: Test**

```bash
# Verify server appears in registry
cortex mcp:registry

# Test installation
cortex tui
# Press 7, browse to server, install

# Verify configuration
cortex mcp:list
cortex mcp:show my-awesome-server
cortex mcp:test my-awesome-server
```

### Implementing Custom Server Discovery

**Use Case**: Discovery from non-standard config locations or formats.

```python
from claude_ctx_py.core.mcp import MCPServerInfo, get_server_docs_path

def discover_custom_servers(custom_config_path: Path) -> List[MCPServerInfo]:
    """Discover servers from custom config format."""
    
    # Read custom config
    with open(custom_config_path) as f:
        config = yaml.safe_load(f)  # or toml, ini, etc.
    
    servers = []
    for name, server_data in config.get("servers", {}).items():
        # Map custom format to MCPServerInfo
        docs_path = get_server_docs_path(name)
        
        server = MCPServerInfo(
            name=name,
            command=server_data["cmd"],
            args=server_data.get("args", []),
            env=server_data.get("environment", {}),
            description=server_data.get("desc", ""),
            docs_path=docs_path
        )
        
        servers.append(server)
    
    return servers
```

### Extending Validation Logic

**Use Case**: Add custom validation rules beyond basic checks.

```python
from claude_ctx_py.core.mcp import MCPServerInfo

def enhanced_validate_server(server: MCPServerInfo) -> Tuple[bool, List[str], List[str]]:
    """Enhanced validation with custom rules."""
    
    errors = []
    warnings = []
    
    # Basic validation
    is_valid, basic_errors = server.is_valid()
    errors.extend(basic_errors)
    
    # Custom rule: Check for deprecated servers
    deprecated = ["old-server-name", "legacy-tool"]
    if server.name in deprecated:
        warnings.append(f"Server '{server.name}' is deprecated. Consider alternatives.")
    
    # Custom rule: Validate environment variable format
    if server.env:
        for key, value in server.env.items():
            # Check for URL format if key contains "URL"
            if "URL" in key.upper() and value:
                if not value.startswith(("http://", "https://", "postgres://", "mysql://")):
                    warnings.append(f"Environment variable '{key}' may need a URL scheme")
            
            # Check for key format if key contains "KEY" or "TOKEN"
            if any(x in key.upper() for x in ["KEY", "TOKEN"]) and value:
                if len(value) < 10:
                    warnings.append(f"Environment variable '{key}' seems too short for a security token")
    
    # Custom rule: Check command accessibility
    if server.command and not os.path.isabs(server.command):
        # Check PATH
        if not shutil.which(server.command):
            warnings.append(f"Command '{server.command}' not found in PATH")
    
    return len(errors) == 0, errors, warnings
```

### Custom TUI Actions

**Use Case**: Add additional actions to the MCP view.

```python
from claude_ctx_py.tui_mcp import MCPViewMixin

class ExtendedMCPView(MCPViewMixin):
    """Extended MCP view with custom actions."""
    
    def handle_mcp_keys(self, key: str) -> bool:
        """Handle keyboard input with extensions."""
        
        # Custom action: Open server homepage
        if key == "h":
            server = self._get_selected_server()
            if server and server.homepage:
                import webbrowser
                webbrowser.open(server.homepage)
                self.state.status_message = f"Opened {server.homepage}"
            return True
        
        # Custom action: Export server list
        elif key == "e":
            self._export_server_list()
            return True
        
        # Fallback to default handling
        return super().handle_mcp_keys(key)
    
    def _export_server_list(self) -> None:
        """Export server list to markdown file."""
        from claude_ctx_py.core.mcp import export_servers_list
        
        success, output, error = export_servers_list(format_type="markdown")
        if success:
            export_path = Path.home() / "mcp-servers.md"
            export_path.write_text(output)
            self.state.status_message = f"Exported to {export_path}"
        else:
            self.state.status_message = f"Export failed: {error}"
```

---

## Performance & Best Practices

### Configuration File Parsing

**Caching Strategy**:

```python
# Avoid repeated file reads in tight loops
servers_cache: Optional[List[MCPServerInfo]] = None
cache_timestamp: float = 0.0

def get_servers_cached(ttl: float = 5.0) -> List[MCPServerInfo]:
    """Get servers with simple time-based caching."""
    global servers_cache, cache_timestamp
    
    now = time.time()
    if servers_cache is None or (now - cache_timestamp) > ttl:
        success, servers, error = discover_servers()
        if success:
            servers_cache = servers
            cache_timestamp = now
        else:
            # Return stale cache on error if available
            if servers_cache is None:
                servers_cache = []
    
    return servers_cache
```

**Lazy Documentation Loading**:

```python
# Don't read all docs upfront
def load_server_docs_lazy(server: MCPServerInfo) -> Optional[str]:
    """Load docs only when needed."""
    if not server.docs_path or not server.docs_path.exists():
        return None
    
    try:
        return server.docs_path.read_text(encoding="utf-8")
    except OSError:
        return None
```

### Registry Search Optimization

**Indexed Search**:

```python
from typing import Dict, Set

# Build search index once at module load
search_index: Dict[str, Set[str]] = {}

def build_search_index():
    """Build inverted index for fast search."""
    global search_index
    
    for server in get_all_servers():
        tokens = set()
        
        # Index name
        tokens.update(server.name.lower().split("-"))
        
        # Index description words
        tokens.update(server.description.lower().split())
        
        # Index tags
        tokens.update(tag.lower() for tag in server.tags)
        
        # Map tokens to server name
        for token in tokens:
            if token not in search_index:
                search_index[token] = set()
            search_index[token].add(server.name)

def fast_search_servers(query: str) -> List[MCPServerDefinition]:
    """Search using pre-built index."""
    if not search_index:
        build_search_index()
    
    query_tokens = query.lower().split()
    matching_names = None
    
    for token in query_tokens:
        token_matches = search_index.get(token, set())
        if matching_names is None:
            matching_names = token_matches
        else:
            matching_names = matching_names.intersection(token_matches)
    
    if matching_names is None:
        return []
    
    return [get_server(name) for name in matching_names if get_server(name)]
```

### Installation Timeouts

**Configurable Timeouts**:

```python
def install_package_with_progress(
    server: MCPServerDefinition,
    timeout: int = 300,
    progress_callback: Optional[Callable[[str], None]] = None
) -> InstallResult:
    """Install with progress reporting."""
    
    install_cmd = server.get_install_command()
    if not install_cmd:
        return InstallResult(success=False, message="No install command")
    
    try:
        process = subprocess.Popen(
            install_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        start_time = time.time()
        output_lines = []
        
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                process.kill()
                return InstallResult(
                    success=False,
                    message=f"Installation timed out after {timeout}s"
                )
            
            # Read output line
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                output_lines.append(line.rstrip())
                if progress_callback:
                    progress_callback(line.rstrip())
        
        returncode = process.wait()
        
        if returncode == 0:
            return InstallResult(
                success=True,
                message=f"Successfully installed {server.package}",
                server_name=server.name
            )
        else:
            return InstallResult(
                success=False,
                message=f"Installation failed:\n" + "\n".join(output_lines[-10:])
            )
    
    except Exception as e:
        return InstallResult(success=False, message=f"Installation error: {str(e)}")
```

### Validation Best Practices

**Fail-Fast Validation**:

```python
def quick_validate(server: MCPServerInfo) -> bool:
    """Quick validation for UI filtering."""
    # Only check critical fields
    return bool(server.name and server.command)

def full_validate(server: MCPServerInfo) -> Tuple[bool, List[str], List[str]]:
    """Comprehensive validation for installation."""
    # Run all checks
    return validate_server_config(server.name)
```

**Batch Validation**:

```python
def validate_all_servers_parallel(
    config_path: Optional[Path] = None,
    max_workers: int = 4
) -> Dict[str, Tuple[bool, List[str], List[str]]]:
    """Validate multiple servers in parallel."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    success, servers, error = discover_servers(config_path)
    if not success:
        return {}
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_server = {
            executor.submit(validate_server_config, server.name, config_path): server
            for server in servers
        }
        
        for future in as_completed(future_to_server):
            server = future_to_server[future]
            try:
                results[server.name] = future.result()
            except Exception as exc:
                results[server.name] = (False, [str(exc)], [])
    
    return results
```

### Memory Management

**Server Info Cleanup**:

```python
def cleanup_server_info(server: MCPServerInfo) -> MCPServerInfo:
    """Remove heavy fields for long-term storage."""
    # Clear documentation content (keep path only)
    # Clear large env values (keep keys only)
    
    cleaned = MCPServerInfo(
        name=server.name,
        command=server.command,
        args=server.args,
        env={k: "" for k in server.env.keys()},  # Keep keys, clear values
        description=server.description[:200],  # Truncate long descriptions
        tools=server.tools[:10],  # Limit tool list
        docs_path=server.docs_path,
        doc_only=server.doc_only
    )
    
    return cleaned
```

---

## Related Documentation

### Core Documentation

- [Master Architecture](MASTER_ARCHITECTURE.md) - System-wide architecture overview
- [TUI Architecture](TUI_ARCHITECTURE.md) - TUI framework and design patterns

### Feature Documentation

- [AI Intelligence System](AI_INTELLIGENCE_ARCHITECTURE.md) - Context-aware recommendations
- [Memory Vault System](MEMORY_VAULT_ARCHITECTURE.md) - Note-taking and retrieval

### Usage Guides

- [MCP Implementation Summary](../guides/mcp/MCP_IMPLEMENTATION_SUMMARY.md) - High-level MCP overview
- [MCP Management Guide](../guides/mcp/MCP_MANAGEMENT.md) - User-facing management guide
- [TUI MCP View](../guides/tui/tui-mcp-view.md) - TUI usage instructions

### API References

- [MCP Module Usage](../guides/mcp/MCP_MODULE_USAGE.md) - Python API documentation
- [MCP Module README](../guides/mcp/MCP_MODULE_README.md) - Module overview

---

## Changelog

### Version 1.0 (December 6, 2025)

- Initial comprehensive documentation
- Covered all 4 core modules (mcp.py, mcp_registry.py, mcp_installer.py, tui_mcp.py)
- Documented 25+ registry servers across 10 categories
- Complete TUI integration guide with Key 7 access
- CLI command reference with examples
- Developer guide with extension patterns
- Performance optimization best practices

---

**Document Maintainer**: Cortex Plugin Team  
**Last Review**: December 6, 2025  
**Next Review**: March 2026
