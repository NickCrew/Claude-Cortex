# Shell Completions for cortex

The `cortex` CLI supports Bash, Zsh, and Fish completions via `cortex install completions`.

## Quick Start

```bash
# Auto-detect shell and install to default location
cortex install completions

# Or specify shell explicitly
cortex install completions --shell bash
cortex install completions --shell zsh
cortex install completions --shell fish
```

## Common options

```bash
# Preview without writing files
cortex install completions --dry-run

# Overwrite existing completion file
cortex install completions --force

# Install to system path (may require sudo)
cortex install completions --system

# Custom output path
cortex install completions --shell zsh --path ~/.zsh/completions/_cortex
```

## Post-install bundle

To install completions and manpages together:

```bash
cortex install post
```

## Features

Completions cover:

- top-level commands (`agent`, `skills`, `mcp`, `ai`, etc.)
- subcommands and options
- common dynamic argument suggestions

When CLI commands change, regenerate completions:

```bash
cortex install completions --force
```

## Troubleshooting

### Bash

- Ensure `bash-completion` is installed.
- Reload shell after installation.

### Zsh

- Ensure your completion path is in `fpath` and `compinit` runs.
- Clear stale `.zcompdump*` if needed.

### Fish

- Verify completion file exists under `~/.config/fish/completions/`.
- Start a new shell or source the file.

## Development

Completion generation code lives in `claude_ctx_py/completions.py`.

When adding CLI commands, update completion definitions and re-run completion install locally for verification.
