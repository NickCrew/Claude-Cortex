# MCP Server Management

Complete guide to managing Model Context Protocol (MCP) servers in cortex.

## Overview

Cortex provides comprehensive MCP server management through three interfaces:

1. **CLI Commands** - Terminal commands for quick operations
2. **TUI View** - Visual dashboard for interactive management
3. **Core Module** - Python API for programmatic access

## Philosophy: Read-Only + Intelligence

Cortex observes and assists with MCP servers, not controls them:

- ✅ Reads Claude Desktop config (`~/.config/Claude/claude_desktop_config.json`)
- ✅ Validates and diagnoses server configurations
- ✅ Provides curated documentation and best practices
- ✅ Generates config snippets for easy setup
- ❌ Does not edit config automatically
- ❌ Does not manage server lifecycle

**Why?** Claude Desktop owns MCP servers. We provide intelligence, not control.

## Quick Start

### View All Servers

```bash
cortex mcp list
```

### Get Server Details

```bash
cortex mcp show context7
```

### View Documentation

```bash
cortex mcp docs serena
```

### Test Configuration

```bash
cortex mcp test context7
```

### Diagnose All Servers

```bash
cortex mcp diagnose
```

### Generate Config Snippet

```bash
cortex mcp snippet playwright
```

## CLI Reference

### `cortex mcp list`

List all configured MCP servers with validation status.

**Output:**

- Server name
- Command and arguments
- Environment variables (if any)
- Documentation availability
- Validation status (✓ or ✗)

**Example:**

```
MCP Servers (2 configured):

● context7
  Command: npx -y @context7/mcp
  Args: []
  Env: (none)
  Docs: ~/.claude/mcp/docs/Context7.md ✓
  Status: Valid ✓

● serena
  Command: npx -y @modelcontextprotocol/server-serena
  Args: []
  Env: (none)
  Docs: Not found
  Status: Warning ⚠ (No documentation)
```

### `cortex mcp show <server>`

Show detailed information about a specific server.

**Arguments:**

- `<server>`: Server name (case-insensitive)

**Output:**

- Full command line
- All arguments
- Environment variables
- Documentation path
- Validation results
- Configuration snippet

**Example:**

```bash
cortex mcp show context7
```

### `cortex mcp docs <server>`

Display curated documentation for an MCP server.

**Arguments:**

- `<server>`: Server name (case-insensitive)

**Output:**

- Server purpose
- When to use triggers
- Decision criteria ("Choose When")
- Integration patterns
- Usage examples
- Quality gates

**Example:**

```bash
cortex mcp docs sequential
```

### `cortex mcp test <server>`

Test server configuration and display diagnostic information.

**Arguments:**

- `<server>`: Server name (case-insensitive)

**Checks:**

- Config file readable
- Server definition valid
- Command specified
- Environment variables valid
- Documentation available

**Example:**

```bash
cortex mcp test browser-tools
```

### `cortex mcp diagnose`

Run comprehensive diagnostics on all configured servers.

**Output:**

- Total server count
- Valid server count
- Servers with errors
- Servers with warnings
- Detailed issue reports

**Example:**

```bash
cortex mcp diagnose
```

### `cortex mcp snippet <server>`

Generate a JSON configuration snippet for a server.

**Arguments:**

- `<server>`: Server name (case-insensitive)

**Output:**

- JSON snippet ready to paste into `claude_desktop_config.json`
- Properly formatted with indentation
- Includes command, args, and env

**Example:**

```bash
cortex mcp snippet magic
# Copy output to claude_desktop_config.json
```

## TUI Interface

### Accessing MCP View

1. Launch TUI: `cortex tui`
2. Press `7` to navigate to MCP Servers view

### MCP View Features

**List View:**

- All configured servers with status indicators
- Server name, command, and args
- Documentation availability (✓ or -)
- Visual selection highlighting

**Details View:**

- Full command and arguments
- Environment variables (sensitive values masked)
- Documentation paths
- Configuration validation status
- Full command line preview

### Keyboard Shortcuts

**Navigation:**

- `j` / `k` or `↑` / `↓` - Navigate servers
- `Enter` - Show detailed server information
- `Esc` - Return from details to list

**Actions:**

- `t` - Test server connection
- `d` - View server documentation
- `c` - Copy configuration snippet
- `v` - Validate server configuration
- `r` - Reload servers from config

**Global:**

- `?` - Show help
- `q` - Quit TUI
- `1-0` - Navigate to other views

### Status Indicators

- **● Green** - Server configured and valid
- **○ Gray** - Server configured but not validated
- **⚠ Yellow** - Server has warnings (e.g., missing docs)
- **✗ Red** - Server has errors (invalid config)

## MCP Server Documentation

Cortex includes curated documentation for popular MCP servers in `~/.claude/mcp/docs/`:

### Available Docs

1. **Context7.md** - Official library documentation lookup
2. **Serena.md** - Project memory and semantic understanding
3. **Sequential.md** - Multi-step reasoning and debugging
4. **Magic.md** - UI component generation (21st.dev patterns)
5. **Morphllm.md** - Bulk code transformations
6. **BrowserTools.md** - Web automation and scraping
7. **Playwright.md** - E2E testing and accessibility

### Documentation Format

Each doc includes:

- **Purpose**: What the server does
- **Triggers**: When to use it
- **Choose When**: Decision criteria vs other tools
- **Works Best With**: Complementary servers
- **Examples**: Practical usage scenarios
- **Quality Gates**: Checklists for proper usage

### Adding Custom Docs

Create a new markdown file in `~/.claude/mcp/docs/`:

```markdown
# MyServer MCP Server

**Purpose**: Brief description

## Triggers
- When to use condition 1
- When to use condition 2

## Choose When
- Over other tool: When specific scenario

## Examples
\`\`\`
"user request" → MyServer (reason)
\`\`\`
```

Name the file with the server name: `MyServer.md`

## Configuration

### Claude Desktop Config Location

**macOS:**

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**

```
~/.config/Claude/claude_desktop_config.json
```

**Windows:**

```
%APPDATA%/Claude/claude_desktop_config.json
```

### Config Format

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp"]
    },
    "serena": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-serena"],
      "env": {
        "SERENA_PROJECT_ROOT": "/path/to/project"
      }
    }
  }
}
```

## Programmatic Usage

### Python API

```python
from claude_ctx_py.core.mcp import (
    discover_servers,
    get_server_info,
    validate_server_config,
    get_server_docs_path,
    generate_config_snippet
)

# Discover all servers
success, servers, error = discover_servers()
if success:
    for server in servers:
        print(f"Found: {server.name}")

# Get server details
server = get_server_info("context7")
if server:
    print(f"Command: {server.command}")
    print(f"Args: {server.args}")

# Validate server
valid, errors, warnings = validate_server_config("context7")
if valid:
    print("✓ Configuration valid")
else:
    print(f"✗ Errors: {', '.join(errors)}")

# Get docs path
docs = get_server_docs_path("serena")
if docs:
    print(f"Documentation: {docs}")

# Generate snippet
snippet = generate_config_snippet("magic")
print(snippet)
```

### Data Classes

```python
from claude_ctx_py.core.mcp import MCPServerInfo

@dataclass
class MCPServerInfo:
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str = ""
    tools: List[str] = field(default_factory=list)
    docs_path: Optional[Path] = None
```

## Troubleshooting

### "No MCP servers configured"

**Cause:** Claude Desktop config file not found or has no `mcpServers` section.

**Solution:**

1. Check config file exists at platform-specific location
2. Add `mcpServers` object to JSON
3. Run `cortex mcp diagnose` to verify

### "Server not found: xyz"

**Cause:** Server name not in config or case mismatch.

**Solution:**

1. Run `cortex mcp list` to see available servers
2. Check spelling and case (search is case-insensitive)
3. Verify server in Claude Desktop config

### "Invalid JSON in config file"

**Cause:** Malformed JSON in `claude_desktop_config.json`.

**Solution:**

1. Open config in editor
2. Fix JSON syntax (use JSON validator)
3. Common issues: trailing commas, missing quotes

### "Documentation not found"

**Cause:** No `.md` file in `~/.claude/mcp/docs/` for server.

**Solution:**

1. Check if file exists: `ls ~/.claude/mcp/docs/`
2. Create custom doc (see "Adding Custom Docs")
3. Use exact server name for filename

### "Permission denied reading config"

**Cause:** Config file not readable.

**Solution:**

```bash
# macOS/Linux
chmod 644 ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Or run with proper permissions
sudo cortex mcp list
```

## Best Practices

### 1. Document Your Servers

Create documentation for all custom MCP servers in `~/.claude/mcp/docs/`.

### 2. Validate Regularly

Run `cortex mcp diagnose` after config changes.

### 3. Use Snippets

Generate and review snippets before manual config edits:

```bash
cortex mcp snippet myserver > snippet.json
# Review snippet.json before adding to config
```

### 4. Organize Documentation

Group related servers in docs:

- Web automation: BrowserTools, Playwright
- Code transformation: Serena, Morphllm
- Reasoning: Sequential
- UI generation: Magic

### 5. Version Control

Track `~/.claude/mcp/docs/` in git for team consistency.

### 6. Test New Servers

Always test after adding:

```bash
cortex mcp test newserver
```

## Integration with /tools:select

The `/tools:select` command uses MCP server information to recommend optimal tools:

```bash
# In Claude Code session
/tools:select "rename function across 10 files"
# Recommendation: Serena MCP (semantic understanding)

/tools:select "update console.log to logger.info"
# Recommendation: Morphllm MCP (pattern transformation)
```

This integration enables intelligent tool routing based on:

- Operation complexity
- File count
- Pattern vs semantic requirements
- Available server capabilities

## Future Enhancements

Planned features:

- [ ] Real-time server health monitoring
- [ ] Active connection testing via MCP protocol
- [ ] Server capability introspection
- [ ] Log viewer for MCP server output
- [ ] Server installation helper
- [ ] Configuration wizard for common setups

## Related Documentation

- [Core MCP Module README](./MCP_MODULE_README.md)
- [MCP Module Usage Guide](./MCP_MODULE_USAGE.md)
- [TUI MCP View Guide](../tui/tui-mcp-view.md)
- [TUI Keyboard Reference](../tui/tui-keyboard-reference.md)
