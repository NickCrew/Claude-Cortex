# TUI MCP Server Management View

The MCP View provides a comprehensive interface for managing MCP (Model Context Protocol) servers within the cortex TUI. Press `7` from the main TUI to open it (or use the command palette).

## Features

### Main Dashboard

The MCP view displays all configured MCP servers with:

- **Status Indicator**: Shows if server is configured (● green)
- **Server Name**: The identifier for the MCP server
- **Command**: The executable command
- **Arguments**: Command-line arguments (truncated if long)
- **Documentation**: ✓ if local docs available, - otherwise

### Navigation

#### List View

| Key | Action |
|-----|--------|
| `j` or `↓` | Move down in server list |
| `k` or `↑` | Move up in server list |
| `Enter` | Show detailed information for selected server |
| `/` | Filter servers by name/command/description |
| `r` | Reload server list from config |
| `t` | Test server connection (coming soon) |
| `d` | View server documentation |
| `c` | Copy config snippet to clipboard |
| `v` | Validate server configuration |

#### Details View

| Key | Action |
|-----|--------|
| `Esc` | Return to server list |
| `d` | View full documentation |
| `c` | Copy config snippet |
| `v` | Validate configuration |

## Server Details

When viewing a server's details, you'll see:

1. **Command Information**
   - Full command path
   - Command-line arguments (each on separate line)

2. **Environment Variables**
   - All configured env vars
   - Sensitive values (keys, tokens, passwords) are masked

3. **Documentation**
   - Path to local documentation if available
   - Link to view full docs

4. **Configuration Status**
   - Validation results
   - Any errors or warnings
   - Full command line for manual execution

## Filtering Servers

Press `/` to activate filter mode. Type to search across:
- Server names
- Command paths
- Descriptions

The list will update in real-time to show matching servers only.

Press `Esc` to clear the filter.

## Validating Servers

Press `v` to validate the selected server's configuration. The system checks:

- Server exists in config
- Command is specified
- Command is executable (if absolute path)
- Environment variables are valid
- Documentation is available (warning if missing)

Validation results appear in the status bar:
- `✓ Valid configuration` (green) - All checks passed
- `✗ Validation failed: <error>` (red) - Configuration issue found

## Configuration Snippets

Press `c` to generate a JSON configuration snippet for the selected server. The snippet includes:

- Server name
- Command
- Arguments
- Environment variables
- Formatted as ready-to-paste JSON

Use this to:
- Share server configurations
- Backup server settings
- Document server setup
- Migrate to new machines

## Documentation

Press `d` to view documentation for a server. The system looks for docs in:
- `~/.claude/mcp/docs/<server-name>.md`

If documentation is found:
- A preview appears in the status bar
- Full documentation can be viewed separately (coming soon)

If no documentation is found:
- Status message indicates "No documentation found"
- You can add documentation by creating the file

## Testing Servers

Press `t` to test connectivity to a server (coming soon). This will:
1. Start the server process
2. Attempt to connect
3. Send initialization request
4. Query available tools/capabilities
5. Report success or failure

## Integration with TUI

The MCP view integrates seamlessly with the main TUI:

```python
from claude_ctx_py.tui import AgentTUI
from claude_ctx_py.tui_mcp import MCPViewMixin

class EnhancedTUI(MCPViewMixin, AgentTUI):
    """TUI with MCP management support."""

    def __init__(self):
        super().__init__()
        self.load_mcp_servers()
```

## Configuration Location

MCP servers are configured in the Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Example configuration:

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"],
      "env": {
        "API_KEY": "your-key-here"
      }
    },
    "sequential": {
      "command": "npx",
      "args": ["-y", "@sequential/mcp-server"]
    }
  }
}
```

## Error Handling

The MCP view handles various error conditions gracefully:

1. **Config Not Found**: Shows message "Config file not found"
2. **Invalid JSON**: Shows "Invalid JSON in config"
3. **Server Not Found**: Shows "Server not found" with available servers
4. **Command Not Found**: Shows validation error with recovery hint
5. **Read Errors**: Shows "Failed to read config" with specific error

All errors appear in the status bar with helpful context.

## Status Messages

The status bar shows real-time feedback:

- `Loaded N MCP server(s)` - After successful load
- `Testing <server>...` - During server test
- `✓ <server> configuration is valid` - After validation success
- `✗ Validation failed: <error>` - After validation failure
- `Config snippet generated` - After copying config
- `No documentation found for <server>` - When docs unavailable
- `Docs only: <server>` - Documentation exists but MCP server isn’t installed
- `Error: <message>` - For any errors encountered

When documentation lives in `~/.claude/mcp/docs` but the Claude Desktop config lacks a matching `mcpServers` entry, the TUI now surfaces a “Docs only” row. This makes gaps obvious (for example, `BrowserTools` will appear with a yellow warning until you add it via “Add MCP” or `cortex mcp add browser-tools`).

## Future Enhancements

Planned features for the MCP view:

1. **Server Testing**: Full connection testing with capability discovery
2. **Tool Browser**: View and test individual server tools
3. **Documentation Viewer**: Full-screen doc viewer with syntax highlighting
4. **Clipboard Support**: Actual clipboard integration for config snippets
5. **Server Logs**: View real-time server logs and debug output
6. **Configuration Editor**: Edit server configs directly in TUI
7. **Server Templates**: Quick setup from common server templates
8. **Health Monitoring**: Real-time server health and performance metrics

## Architecture

The MCP view is implemented as a mixin class (`MCPViewMixin`) that can be composed with other TUI components:

```
MCPViewMixin
├── Server Discovery (from claude_desktop_config.json)
├── Doc-only Detection (~/.claude/mcp/docs vs config)
├── Server Filtering (name, command, description)
├── Validation (config checks, command existence)
├── Documentation Lookup (~/.claude/mcp/docs/)
└── Config Generation (JSON snippets)
```

This follows the same pattern as:
- `ProfileViewMixin` - Profile management
- `ExportViewMixin` - Context export
- `WizardViewMixin` - Init wizard

## Related Documentation

- [MCP Core Module](../claude_ctx_py/core/mcp.py) - Backend server management
- [TUI Extensions](../claude_ctx_py/tui_extensions.py) - Other view mixins
- [TUI Main](../claude_ctx_py/tui.py) - Main TUI implementation
- [MCP Protocol Spec](https://modelcontextprotocol.io/) - Official MCP documentation

## Example Session

```
┌─ MCP Servers ─────────────────────────────────────────────────────┐
│   Status  Server Name  Command              Args                   │
│ > ●       context7     npx                  -y @context7/mcp-...   │
│   ●       sequential   npx                  -y @sequential/m...    │
│   ○       BrowserTools Not configured      -                      ✓ │
└───────────────────────────────────────────────────────────────────┘
Controls: Enter=Details  t=Test  d=Docs  c=Copy Config  /=Filter  r=Reload

Status: Loaded 2 MCP server(s) + 1 docs
```

After pressing Enter:

```
┌─ Server Details: context7 ────────────────────────────────────────┐
│ context7                                                           │
│ ────────────────────────────────────────────────────────────────  │
│                                                                    │
│ Command:                                                           │
│   npx                                                              │
│                                                                    │
│ Arguments:                                                         │
│   • -y                                                             │
│   • @context7/mcp-server                                           │
│                                                                    │
│ Environment Variables:                                             │
│   API_KEY=********                                                 │
│                                                                    │
│ Documentation:                                                     │
│   ✓ Available at: /Users/user/.claude/mcp/docs/context7.md       │
│                                                                    │
│ Configuration Status:                                              │
│   ✓ Valid configuration                                            │
│                                                                    │
│ Full Command:                                                      │
│   npx -y @context7/mcp-server                                     │
│                                                                    │
│ Controls: Esc=Back  d=View Docs  c=Copy Config  v=Validate       │
└───────────────────────────────────────────────────────────────────┘
```
