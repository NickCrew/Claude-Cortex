# API Reference

Complete API documentation for the cortex Python modules.

## Core Modules

| Module | Description |
|--------|-------------|
| [prompts](prompts.md) | Prompt library management (discover, activate, deactivate) |
| [installer](installer.md) | Post-install helpers (completions, manpages, docs) |

## TUI Modules

| Module | Description |
|--------|-------------|
| shell_integration | Shell alias installation for bash/zsh/fish |
| tui_workflow_viz | Workflow visualization (timeline, Gantt, dependency trees) |

## Core Subsystem

| Module | Description |
|--------|-------------|
| core/migration | Config migration from v1 to v2 format |
| core/scenarios | Multi-phase scenario orchestration |

## Intelligence Modules

| Module | Description |
|--------|-------------|
| intelligence/context_health | Context alignment analysis and health scoring |

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
