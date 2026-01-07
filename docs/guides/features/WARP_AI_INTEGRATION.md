# Warp AI Integration

This guide shows how to integrate `cortex` with Warp AI and other terminal AI tools.

## Quick Start

Install the context export aliases:

```bash
cortex install aliases
```

Then reload your shell:

```bash
# Bash
source ~/.bashrc

# Zsh
source ~/.zshrc

# Fish
source ~/.config/fish/config.fish
```

## Available Aliases

After installation, you have these convenient aliases:

### Context Export

- **`ctx`** - Export full context (all components)
- **`ctx-light`** - Export lightweight context (excludes skills, mcp_docs)
- **`ctx-rules`** - Export rules only
- **`ctx-agents`** - Export agents only
- **`ctx-modes`** - Export modes only
- **`ctx-core`** - Export core framework (FLAGS, PRINCIPLES, RULES)

### Utilities

- **`ctx-list`** - List available components
- **`ctx-copy`** - Copy context to clipboard (macOS)

### Management

- **`ctx-agent-list`** - List available agents
- **`ctx-mode-list`** - List available modes
- **`ctx-tui`** - Launch terminal UI

## Usage with Warp AI

### Basic Workflow

1. **Export context** before asking Warp AI a question:
   ```bash
   ctx
   ```

2. **Ask Warp AI** your question using Cmd+` (or your configured hotkey)

3. Warp AI will have access to your exported context in the command output

### Example Workflows

#### Full Context Export

For comprehensive context when working on complex tasks:

```bash
# Export everything
ctx

# Now ask Warp AI questions like:
# "Based on my active agents, suggest improvements to my workflow"
# "What rules are currently active in my setup?"
```

#### Lightweight Export

For faster exports when you don't need skills or MCP docs:

```bash
# Export without heavy components
ctx-light

# Ask focused questions like:
# "What agents do I have active?"
# "Show me my current modes"
```

#### Specific Component Exports

Export only what's relevant to your current task:

```bash
# Working with agents
ctx-agents

# Working with rules
ctx-rules

# Understanding modes
ctx-modes

# Core framework only
ctx-core
```

#### Clipboard Integration

Copy context to clipboard for pasting into any AI chat:

```bash
# Copy to clipboard
ctx-copy

# Paste into ChatGPT, Claude, or any other AI tool
```

## Advanced Usage

### Custom Exports

Use the full `cortex export` command for fine-grained control:

```bash
# Exclude multiple categories
cortex export context - \
  --exclude skills \
  --exclude mcp_docs \
  --exclude agents

# Include only specific categories
cortex export context - \
  --include rules \
  --include core

# Exclude specific files
cortex export context - \
  --exclude-file rules/quality-rules.md \
  --exclude-file modes/Super_Saiyan.md

# Export to file instead of stdout
cortex export context ~/my-context.md
```

### Shell-Specific Installation

Specify target shell explicitly:

```bash
# Install for bash
cortex install aliases --shell bash

# Install for zsh
cortex install aliases --shell zsh

# Install for fish
cortex install aliases --shell fish
```

### Custom RC File

Specify a custom RC file location:

```bash
cortex install aliases --rc-file ~/.bash_aliases
```

### Dry Run

Preview what will be installed without making changes:

```bash
cortex install aliases --dry-run
```

### Force Reinstall

Reinstall aliases even if already installed:

```bash
cortex install aliases --force
```

### Uninstall

Remove installed aliases:

```bash
cortex install aliases --uninstall
```

## Integration with Other Terminal AI Tools

These aliases work with any terminal AI tool that can access command output context:

- **Warp AI** - Built-in AI assistant
- **GitHub Copilot for CLI** - AI-powered command suggestions
- **Fig** - Terminal autocomplete with AI
- **Shell GPT** - ChatGPT in your terminal
- **Any custom AI wrapper** - Using command output as context

## Troubleshooting

### Aliases not found after installation

1. Verify installation:
   ```bash
   grep "cortex aliases" ~/.zshrc  # or ~/.bashrc, ~/.config/fish/config.fish
   ```

2. Reload your shell:
   ```bash
   source ~/.zshrc  # or appropriate RC file
   ```

3. Check that cortex is in your PATH:
   ```bash
   which cortex
   ```

### Context too large

Use lighter exports:

```bash
# Use lightweight export
ctx-light

# Or export specific components
ctx-rules
ctx-agents
ctx-modes
ctx-core
```

### pbcopy not available (Linux)

The `ctx-copy` alias uses `pbcopy` which is macOS-specific. On Linux, install `xclip` and create a custom alias:

```bash
# Install xclip
sudo apt-get install xclip  # Ubuntu/Debian
sudo yum install xclip      # Fedora/RHEL

# Add to your RC file
alias ctx-copy='cortex export context - 2>/dev/null | xclip -selection clipboard && echo "✓ Context copied to clipboard"'
```

Or use `wl-copy` for Wayland:

```bash
alias ctx-copy='cortex export context - 2>/dev/null | wl-copy && echo "✓ Context copied to clipboard"'
```

## Best Practices

1. **Use appropriate context level**: Don't export full context if you only need rules or agents

2. **Export before asking**: Run the export command right before asking your question for fresh context

3. **Combine with specific questions**: The more specific your question, the better AI can use the context

4. **Update regularly**: Keep your agents, modes, and rules up to date

5. **Use ctx-list**: Check what's available before exporting

## Show Available Aliases

To see all available aliases without installing:

```bash
cortex install aliases --show
```

## Examples

### Example 1: Debugging workflow

```bash
# Export full context
ctx

# Ask Warp AI:
# "I'm getting an error with my python-pro agent.
#  What might be causing it based on my configuration?"
```

### Example 2: Configuration review

```bash
# Export agents only
ctx-agents

# Ask Warp AI:
# "Review my active agents and suggest which ones I might
#  want to activate for a React project"
```

### Example 3: Rule optimization

```bash
# Export rules
ctx-rules

# Ask Warp AI:
# "Are there any conflicting rules in my configuration?"
```

### Example 4: Quick clipboard copy

```bash
# Copy to clipboard
ctx-copy

# Now paste into any AI chat interface
```

## Related Commands

- `cortex export list` - List all available components
- `cortex agent list` - List available agents
- `cortex mode list` - List available modes
- `cortex tui` - Launch interactive TUI
- `cortex completion bash` - Generate shell completions

## Further Reading

- [Export Context Documentation](./EXPORT_CONTEXT.md)
- [Agent Management](../agents.md)
- [Mode Management](../modes.md)
- [Shell Completions](../COMPLETIONS.md)
