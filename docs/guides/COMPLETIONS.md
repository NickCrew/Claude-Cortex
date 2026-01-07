# Shell Completions for cortex

The `cortex` CLI provides shell completion support for Bash, Zsh, and Fish shells.

## Quick Start

Generate and install completions for your shell:

### Bash

```bash
# Generate completion script
cortex completion bash > ~/.bash_completion.d/cortex

# Add to ~/.bashrc
echo 'source ~/.bash_completion.d/cortex' >> ~/.bashrc

# Reload shell
source ~/.bashrc
```

### Zsh

```bash
# Generate completion script
mkdir -p ~/.zsh/completions
cortex completion zsh > ~/.zsh/completions/_cortex

# Add to ~/.zshrc (before compinit)
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -Uz compinit' >> ~/.zshrc
echo 'compinit' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

### Fish

```bash
# Generate completion script
cortex completion fish > ~/.config/fish/completions/cortex.fish

# Completions are loaded automatically on next shell start
# Or reload immediately:
source ~/.config/fish/completions/cortex.fish
```

## Usage

The `completion` command generates shell-specific completion scripts:

```bash
# Generate completion script
cortex completion <shell>

# Show installation instructions
cortex completion <shell> --install
```

Where `<shell>` is one of: `bash`, `zsh`, `fish`

## Features

Shell completions provide:

- **Command completion**: Complete main commands (mode, agent, rules, skills, etc.)
- **Subcommand completion**: Complete subcommands for each main command
- **Flag completion**: Complete command-line flags and options
- **Dynamic completion**: Complete agent names, mode names, etc. from your configuration

If you update the CLI (for example, adding `setup migrate-commands`), regenerate the completion script so the new subcommands and flags appear.

## Examples

```bash
# Type and press Tab:
cortex ag[Tab]          # Completes to: cortex agent
cortex agent act[Tab]   # Completes to: cortex agent activate
cortex agent deps [Tab] # Shows available agents

# With flags:
cortex agent deactivate --[Tab]  # Shows: --force
```

## Installation Instructions

To see detailed installation instructions for your shell:

```bash
cortex completion bash --install
cortex completion zsh --install
cortex completion fish --install
```

## System-Wide Installation

For system-wide completions (requires sudo):

### Bash
```bash
sudo cortex completion bash > /etc/bash_completion.d/cortex
```

### Zsh
```bash
# Location varies by system:
# macOS: /usr/local/share/zsh/site-functions
# Linux: /usr/share/zsh/site-functions
sudo cortex completion zsh > /usr/local/share/zsh/site-functions/_cortex
```

### Fish
```bash
sudo cortex completion fish > /usr/share/fish/vendor_completions.d/cortex.fish
```

## Troubleshooting

### Completions not working in Bash

1. Ensure bash-completion package is installed:
   ```bash
   # macOS
   brew install bash-completion@2

   # Ubuntu/Debian
   sudo apt install bash-completion

   # Fedora/RHEL
   sudo dnf install bash-completion
   ```

2. Verify completion script is sourced in `~/.bashrc`

3. Reload your shell: `source ~/.bashrc`

### Completions not working in Zsh

1. Ensure `compinit` is called in `~/.zshrc`:
   ```zsh
   autoload -Uz compinit
   compinit
   ```

2. Clear completion cache:
   ```zsh
   rm ~/.zcompdump*
   compinit
   ```

3. Reload your shell: `source ~/.zshrc`

### Completions not working in Fish

1. Verify the completion file exists:
   ```bash
   ls ~/.config/fish/completions/cortex.fish
   ```

2. Fish loads completions automatically on startup. Start a new shell or source manually:
   ```fish
   source ~/.config/fish/completions/cortex.fish
   ```

## Development

The completion module is located at `claude_ctx_py/completions.py` and provides:

- `generate_bash_completion()`: Generate Bash completion script
- `generate_zsh_completion()`: Generate Zsh completion script
- `generate_fish_completion()`: Generate Fish completion script
- `get_completion_script(shell)`: Get completion for any supported shell
- `get_installation_instructions(shell)`: Get installation instructions

## Contributing

When adding new commands or subcommands to the CLI, update the completion scripts in `claude_ctx_py/completions.py` to ensure they're included in tab completion.
