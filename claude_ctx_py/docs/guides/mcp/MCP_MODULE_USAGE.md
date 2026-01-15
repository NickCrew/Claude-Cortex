# MCP Module Usage Guide

The MCP (Model Context Protocol) module provides utilities for managing MCP servers configured in Claude Desktop.

## Installation

The MCP module is part of the `cortex-py` package:

```bash
pip install cortex-py
```

## Basic Usage

### Discover All MCP Servers

```python
from claude_ctx_py.core.mcp import discover_servers

success, servers, error = discover_servers()
if success:
    for server in servers:
        print(f"Found: {server.name}")
        print(f"  Command: {server.command}")
        print(f"  Args: {server.args}")
        print(f"  Env vars: {len(server.env)}")
else:
    print(f"Error: {error}")
```

### Get Info About a Specific Server

```python
from claude_ctx_py.core.mcp import get_server_info

success, server, error = get_server_info("context7")
if success and server:
    print(f"Server: {server.name}")
    print(f"Command: {server.command}")
    print(f"Args: {' '.join(server.args)}")
    if server.docs_path:
        print(f"Documentation: {server.docs_path}")
```

### Validate Server Configuration

```python
from claude_ctx_py.core.mcp import validate_server_config

valid, errors, warnings = validate_server_config("context7")
if valid:
    print("✓ Configuration is valid")
else:
    print("✗ Configuration has errors:")
    for error in errors:
        print(f"  - {error}")

if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"  - {warning}")
```

### Generate Config Snippet

```python
from claude_ctx_py.core.mcp import generate_config_snippet

snippet = generate_config_snippet(
    "myserver",
    "npx",
    args=["-y", "@myorg/mcp-server"],
    env={"API_KEY": "your-key-here"}
)
print(snippet)
```

Output:
```json
// Add this to your Claude Desktop config under 'mcpServers':
{
  "mcpServers": {
    "myserver": {
      "command": "npx",
      "args": [
        "-y",
        "@myorg/mcp-server"
      ],
      "env": {
        "API_KEY": "your-key-here"
      }
    }
  }
}
```

### Export Server List

```python
from claude_ctx_py.core.mcp import export_servers_list

# Text format
success, output, error = export_servers_list(format_type="text")
print(output)

# JSON format
success, output, error = export_servers_list(format_type="json")
print(output)

# Markdown format
success, output, error = export_servers_list(format_type="markdown")
print(output)
```

## CLI-Friendly Functions

The module also provides CLI-friendly functions that return `(exit_code, message)` tuples:

### List All Servers

```python
from claude_ctx_py.core.mcp import mcp_list

exit_code, message = mcp_list()
print(message)
```

### Show Server Details

```python
from claude_ctx_py.core.mcp import mcp_show

exit_code, message = mcp_show("context7")
print(message)
```

### Display Documentation

```python
from claude_ctx_py.core.mcp import mcp_docs

exit_code, message = mcp_docs("context7")
if exit_code == 0:
    print(message)  # Documentation content
else:
    print(f"Error: {message}")
```

### Test Server Configuration

```python
from claude_ctx_py.core.mcp import mcp_test

exit_code, message = mcp_test("context7")
print(message)
```

### Diagnose All Servers

```python
from claude_ctx_py.core.mcp import mcp_diagnose

exit_code, message = mcp_diagnose()
print(message)
```

### Generate Config Snippet

```python
from claude_ctx_py.core.mcp import mcp_snippet

exit_code, message = mcp_snippet("context7")
print(message)
```

## Data Classes

### MCPServerInfo

Represents an MCP server configuration:

```python
from claude_ctx_py.core.mcp import MCPServerInfo

server = MCPServerInfo(
    name="myserver",
    command="python",
    args=["-m", "myserver"],
    env={"API_KEY": "test"},
    description="My custom server",
    docs_path=Path("/path/to/docs.md")
)

# Validate
is_valid, errors = server.is_valid()

# Convert to dict
data = server.to_dict()
```

### MCPServerCapabilities

Represents server capabilities (for future use):

```python
from claude_ctx_py.core.mcp import MCPServerCapabilities

capabilities = MCPServerCapabilities(
    tools=["search", "analyze"],
    resources=["docs", "code"],
    prompts=["help", "guide"],
    version="1.0.0"
)
```

## Platform Support

The module automatically detects the correct Claude Desktop config path for your platform:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

You can also specify a custom config path:

```python
from pathlib import Path
from claude_ctx_py.core.mcp import discover_servers

config_path = Path("/custom/path/to/config.json")
success, servers, error = discover_servers(config_path)
```

## Error Handling

The module uses custom exceptions for better error reporting:

```python
from claude_ctx_py.core.mcp import (
    MCPConfigError,
    MCPServerNotFoundError,
    discover_servers,
    get_server_info,
)

try:
    success, servers, error = discover_servers()
    if not success:
        raise MCPConfigError(error)

    success, server, error = get_server_info("nonexistent")
    if not success:
        available = [s.name for s in servers]
        raise MCPServerNotFoundError("nonexistent", available)

except MCPConfigError as e:
    print(f"Config error: {e}")
    print(f"Hint: {e.recovery_hint}")
except MCPServerNotFoundError as e:
    print(f"Server error: {e}")
    print(f"Available: {e.available_servers}")
```

## Advanced Usage

### Custom Validation Logic

```python
from claude_ctx_py.core.mcp import get_server_info, MCPServerInfo

def validate_production_server(server: MCPServerInfo) -> bool:
    """Custom validation for production servers."""
    # Check required environment variables
    required_env = ["API_KEY", "ENDPOINT_URL"]
    for var in required_env:
        if var not in server.env:
            print(f"Missing required env var: {var}")
            return False

    # Check command exists
    if not server.command:
        print("Command is empty")
        return False

    return True

success, server, error = get_server_info("production-server")
if success and server:
    if validate_production_server(server):
        print("✓ Production server is properly configured")
    else:
        print("✗ Production server validation failed")
```

### Batch Server Management

```python
from claude_ctx_py.core.mcp import discover_servers, validate_server_config

def audit_all_servers():
    """Audit all MCP servers and report issues."""
    success, servers, error = discover_servers()
    if not success:
        print(f"Error discovering servers: {error}")
        return

    results = []
    for server in servers:
        valid, errors, warnings = validate_server_config(server.name)
        results.append({
            "name": server.name,
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        })

    # Generate report
    print("MCP Server Audit Report")
    print("=" * 60)
    for result in results:
        status = "✓ PASS" if result["valid"] else "✗ FAIL"
        print(f"\n{status} {result['name']}")

        if result["errors"]:
            print("  Errors:")
            for error in result["errors"]:
                print(f"    - {error}")

        if result["warnings"]:
            print("  Warnings:")
            for warning in result["warnings"]:
                print(f"    - {warning}")

audit_all_servers()
```

## Documentation Integration

The module automatically discovers documentation in `~/.claude/mcp/docs/`:

```python
from claude_ctx_py.core.mcp import get_server_docs_path

# Find docs for a server
docs_path = get_server_docs_path("context7")
if docs_path:
    content = docs_path.read_text()
    print(content)
else:
    print("No documentation found")
```

## Testing

The module includes comprehensive tests. Run them with:

```bash
pytest tests/unit/test_mcp.py -v
```

## Future Enhancements

The following features are planned for future releases:

1. **Active Capability Discovery**: Query running MCP servers for their tools/capabilities
2. **Server Health Checks**: Test actual connectivity to MCP servers
3. **Configuration Management**: Add/remove/modify server configs programmatically
4. **Server Templates**: Pre-configured templates for common MCP servers
5. **Auto-Discovery**: Scan for locally installed MCP servers

## Contributing

To add new functionality to the MCP module:

1. Add functions to `claude_ctx_py/core/mcp.py`
2. Export them in `claude_ctx_py/core/__init__.py`
3. Add comprehensive tests in `tests/unit/test_mcp.py`
4. Update this documentation

## License

Part of the cortex-py project. See main README for license information.
