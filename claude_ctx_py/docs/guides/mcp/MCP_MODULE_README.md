# MCP Module

**Core functionality for managing MCP (Model Context Protocol) servers in Claude Desktop**

## Overview

The MCP module (`claude_ctx_py/core/mcp.py`) provides a comprehensive toolkit for discovering, validating, and managing MCP servers configured in Claude Desktop. It offers both low-level APIs for programmatic access and high-level CLI-friendly functions.

## Key Features

✅ **Cross-Platform Support** - Automatic path detection for macOS, Linux, and Windows
✅ **Server Discovery** - Parse Claude Desktop config and discover all MCP servers
✅ **Configuration Validation** - Validate server configs with detailed error reporting
✅ **Documentation Integration** - Automatic discovery of server documentation
✅ **Config Generation** - Generate JSON snippets for new server configurations
✅ **Multiple Export Formats** - Export server lists as text, JSON, or Markdown
✅ **Comprehensive Testing** - 50 unit tests with 100% coverage of core functionality
✅ **Type Safety** - Full type hints for Python 3.9+
✅ **Error Handling** - Custom exceptions with recovery hints

## Quick Start

```python
from claude_ctx_py.core.mcp import discover_servers, validate_server_config

# Discover all servers
success, servers, error = discover_servers()
if success:
    for server in servers:
        print(f"Found: {server.name}")

        # Validate each server
        valid, errors, warnings = validate_server_config(server.name)
        if valid:
            print(f"  ✓ Valid configuration")
        else:
            print(f"  ✗ Errors: {', '.join(errors)}")
```

## Module Structure

### Core Functions

- **`discover_servers()`** - Find all MCP servers in config
- **`get_server_info(name)`** - Get details about a specific server
- **`validate_server_config(name)`** - Validate server configuration
- **`get_server_docs_path(name)`** - Find server documentation
- **`generate_config_snippet(...)`** - Generate JSON config for a server
- **`list_available_servers()`** - Get list of server names
- **`get_server_command_line(name)`** - Get full command line for server
- **`export_servers_list(format)`** - Export servers in various formats

### CLI-Friendly Functions

- **`mcp_list()`** - List all servers with status
- **`mcp_show(name)`** - Show detailed server info
- **`mcp_docs(name)`** - Display server documentation
- **`mcp_test(name)`** - Test server configuration
- **`mcp_diagnose()`** - Diagnose all server issues
- **`mcp_snippet(name)`** - Generate config snippet for server

### Data Classes

- **`MCPServerInfo`** - Server configuration and metadata
- **`MCPServerCapabilities`** - Server capabilities (tools, resources, prompts)

### Exceptions

- **`MCPConfigError`** - Configuration file errors
- **`MCPServerNotFoundError`** - Server not found errors

## Platform Support

The module automatically detects the correct Claude Desktop config location:

| Platform | Config Path |
|----------|-------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%/Claude/claude_desktop_config.json` |

## Usage Examples

### Validate All Servers

```python
from claude_ctx_py.core.mcp import discover_servers, validate_server_config

success, servers, error = discover_servers()
if success:
    for server in servers:
        valid, errors, warnings = validate_server_config(server.name)
        status = "✓" if valid else "✗"
        print(f"{status} {server.name}")
        for err in errors:
            print(f"  Error: {err}")
```

### Generate Config for New Server

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

### Export Server List as Markdown

```python
from claude_ctx_py.core.mcp import export_servers_list

success, output, error = export_servers_list(format_type="markdown")
if success:
    print(output)
```

## Testing

The module includes comprehensive tests:

```bash
# Run all MCP tests
pytest tests/unit/test_mcp.py -v

# Run with coverage
pytest tests/unit/test_mcp.py --cov=claude_ctx_py.core.mcp --cov-report=html
```

**Test Coverage:**
- 50 unit tests
- Platform detection (macOS, Linux, Windows)
- Server discovery and validation
- Documentation lookup
- Config generation
- Export formats (text, JSON, Markdown)
- Error handling and edge cases
- Unicode support
- Custom exceptions

## Implementation Details

### Design Principles

1. **Cross-Platform First** - Works on macOS, Linux, and Windows out of the box
2. **Graceful Degradation** - Missing config or docs don't cause crashes
3. **Type Safety** - Full type hints for IDE support and static analysis
4. **Comprehensive Error Handling** - Clear error messages with recovery hints
5. **Testing** - Every function has multiple test cases

### Code Organization

```
claude_ctx_py/core/mcp.py          # Core implementation (~820 lines)
tests/unit/test_mcp.py             # Comprehensive tests (~590 lines)
docs/guides/mcp/MCP_MODULE_USAGE.md           # Usage guide
docs/MCP_MODULE_README.md          # This file
```

### Dependencies

- **Python 3.9+** - Uses modern type hints
- **pathlib** - Cross-platform path handling
- **json** - Config parsing
- **platform** - OS detection
- **dataclasses** - Structured data

## Future Enhancements

Planned features for future releases:

- [ ] **Active Capability Discovery** - Query running MCP servers for capabilities
- [ ] **Health Checks** - Test actual connectivity to servers
- [ ] **Config Management** - Add/remove/modify configs programmatically
- [ ] **Server Templates** - Pre-configured templates for common servers
- [ ] **Auto-Discovery** - Scan for locally installed MCP servers
- [ ] **Server Monitoring** - Track server health and performance

## API Documentation

### Function Signatures

```python
# Discovery
def discover_servers(
    config_path: Optional[Path] = None
) -> Tuple[bool, List[MCPServerInfo], str]

def get_server_info(
    name: str,
    config_path: Optional[Path] = None
) -> Tuple[bool, Optional[MCPServerInfo], str]

# Validation
def validate_server_config(
    name: str,
    config_path: Optional[Path] = None
) -> Tuple[bool, List[str], List[str]]

# Documentation
def get_server_docs_path(
    name: str,
    claude_dir: Optional[Path] = None
) -> Optional[Path]

# Config Generation
def generate_config_snippet(
    name: str,
    command: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    indent: int = 2
) -> str

# Export
def export_servers_list(
    config_path: Optional[Path] = None,
    format_type: str = "text"
) -> Tuple[bool, str, str]

# CLI Functions (return exit_code, message)
def mcp_list(config_path: Optional[Path] = None) -> Tuple[int, str]
def mcp_show(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]
def mcp_docs(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]
def mcp_test(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]
def mcp_diagnose(config_path: Optional[Path] = None) -> Tuple[int, str]
def mcp_snippet(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]
```

## Contributing

To contribute to the MCP module:

1. Add new functionality to `claude_ctx_py/core/mcp.py`
2. Export new functions in `claude_ctx_py/core/__init__.py`
3. Add tests to `tests/unit/test_mcp.py`
4. Update documentation in `docs/MCP_MODULE_USAGE.md`
5. Run tests: `pytest tests/unit/test_mcp.py -v`
6. Ensure type checking passes: `mypy claude_ctx_py/core/mcp.py`

## License

Part of the cortex-py project. See main project README for license information.

---

**Status**: ✅ Production Ready
**Tests**: 50 passing
**Python**: 3.9+
**Platforms**: macOS, Linux, Windows
**Last Updated**: 2025-01-05
