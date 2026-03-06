# API Reference

Complete API documentation for the cortex Python modules.

## Core Modules

| Module | Description |
|--------|-------------|
| [installer](installer.md) | Post-install helpers (completions, manpages, docs) |

## TUI Modules

| Module | Description |
|--------|-------------|
| shell_integration | Shell alias installation for bash/zsh/fish |
| tui_workflow_viz | Workflow visualization (timeline, Gantt, dependency trees) |

## Core Subsystem

| Module | Description |
|--------|-------------|
| core/agents | Agent graph, dependencies, activation |
| core/skills | Skill discovery, metrics, community integration |
| core/rules | Rule management |
| core/hooks | Hook installation and validation |
| core/mcp | MCP server discovery and configuration |
| core/worktrees | Git worktree management |
| core/backup | Configuration backup/restore |
| core/asset_installer | Asset installation (symlinks) |
| core/asset_discovery | Asset discovery across scopes |

## Common Patterns

### Return Convention

Most functions return `Tuple[int, str]`:
- `int`: Exit code (0 = success, non-zero = error)
- `str`: Human-readable message

```python
code, msg = some_function()
if code == 0:
    print(f"Success: {msg}")
else:
    print(f"Error: {msg}")
```

### Home Directory Override

Functions accept `home: Path | None` for testing:

```python
# Use default (~)
result = discover_prompts()

# Override for testing
result = discover_prompts(home=Path("/tmp/test-home"))
```

### Dry Run Support

Installer functions support `dry_run=True`:

```python
# Preview without making changes
code, msg = install_completions(dry_run=True)
print(msg)  # "Would install bash completions to: ~/.bash_completion.d/..."
```

## Quick Links

- [Tutorials](/tutorials/) - Step-by-step guides
- [Architecture](/reference/architecture/) - System design documentation
- [CLI Reference](/reference/cli/) - Command-line interface
