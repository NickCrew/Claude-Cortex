"""Shell completion generation for claude-ctx."""

from __future__ import annotations


def generate_bash_completion() -> str:
    """Generate bash completion script."""
    return """# Bash completion for claude-ctx
# Source this file or add it to ~/.bash_completion.d/

_claude_ctx_completion() {
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Top-level commands
    local commands="mode agent rules principles skills mcp init profile workflow tui version completion help doctor"

    # Complete top-level commands
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
        return 0
    fi

    # Get the main command
    local cmd="${COMP_WORDS[1]}"

    case "${cmd}" in
        mode)
            local mode_cmds="list status activate deactivate"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${mode_cmds}" -- ${cur}))
            elif [[ ${prev} == "activate" ]] || [[ ${prev} == "deactivate" ]]; then
                # Complete with available modes
                local modes=$(claude-ctx mode list 2>/dev/null | grep -v "^Available" | grep -v "^  " | awk '{print $1}')
                COMPREPLY=($(compgen -W "${modes}" -- ${cur}))
            fi
            ;;
        agent)
            local agent_cmds="list status activate deactivate deps graph validate"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${agent_cmds}" -- ${cur}))
            elif [[ ${prev} == "activate" ]] || [[ ${prev} == "deactivate" ]] || [[ ${prev} == "deps" ]]; then
                # Complete with available agents
                local agents=$(claude-ctx agent list 2>/dev/null | grep -v "^Available" | sed 's/ .*//' | awk '{print $1}')
                COMPREPLY=($(compgen -W "${agents}" -- ${cur}))
            fi
            ;;
        rules)
            local rules_cmds="list status activate deactivate"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${rules_cmds}" -- ${cur}))
            fi
            ;;
        principles)
            local principles_cmds="list status activate deactivate build"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${principles_cmds}" -- ${cur}))
            fi
            ;;
        skills)
            local skills_cmds="list info validate analyze suggest metrics deps agents compose versions analytics report trending community"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${skills_cmds}" -- ${cur}))
            fi
            ;;
        mcp)
            local mcp_cmds="list show docs test diagnose snippet"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${mcp_cmds}" -- ${cur}))
            fi
            ;;
        init)
            local init_cmds="detect minimal profile status reset resume wizard"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${init_cmds}" -- ${cur}))
            fi
            ;;
        profile)
            local profile_cmds="list apply create edit show"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${profile_cmds}" -- ${cur}))
            fi
            ;;
        workflow)
            local workflow_cmds="list run resume stop status"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${workflow_cmds}" -- ${cur}))
            fi
            ;;
        completion)
            local shells="bash zsh fish"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${shells}" -- ${cur}))
            fi
            ;;
    esac

    return 0
}

complete -F _claude_ctx_completion claude-ctx
"""


def generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return """#compdef claude-ctx
# Zsh completion for claude-ctx

_claude_ctx() {
    local -a commands
    commands=(
        'mode:Mode management commands'
        'agent:Agent management commands'
        'rules:Rule management commands'
        'principles:Principles snippet commands'
        'skills:Skill management commands'
        'mcp:MCP server management'
        'init:Initialize project configuration'
        'profile:Profile management'
        'workflow:Workflow management'
        'tui:Launch terminal UI'
        'doctor:Diagnose and fix context issues'
        'version:Show version information'
        'completion:Generate shell completions'
        'help:Show help information'
    )

    local -a mode_commands
    mode_commands=(
        'list:List available modes'
        'status:Show active modes'
        'activate:Activate one or more modes'
        'deactivate:Deactivate one or more modes'
    )

    local -a agent_commands
    agent_commands=(
        'list:List available agents'
        'status:Show active agents'
        'activate:Activate one or more agents'
        'deactivate:Deactivate one or more agents'
        'deps:Show agent dependencies'
        'graph:Display dependency graph'
        'validate:Validate agent metadata'
    )

    local -a rules_commands
    rules_commands=(
        'list:List available rules'
        'status:Show active rules'
        'activate:Activate one or more rules'
        'deactivate:Deactivate one or more rules'
    )

    local -a principles_commands
    principles_commands=(
        'list:List available principle snippets'
        'status:Show active principle snippets'
        'activate:Activate one or more principle snippets'
        'deactivate:Deactivate one or more principle snippets'
        'build:Build PRINCIPLES.md from active snippets'
    )

    local -a skills_commands
    skills_commands=(
        'list:List available skills'
        'info:Show skill details'
        'validate:Validate skill metadata'
        'analyze:Analyze text for skill suggestions'
        'suggest:Suggest skills for project'
        'metrics:Show skill usage metrics'
        'deps:Show which agents use a skill'
        'agents:Show which agents use a skill'
        'compose:Show dependency tree'
        'versions:Show version information'
        'analytics:Show effectiveness analytics'
        'report:Generate analytics report'
        'trending:Show trending skills'
        'community:Community skill commands'
    )

    local -a mcp_commands
    mcp_commands=(
        'list:List all MCP servers'
        'show:Show detailed server info'
        'docs:Display server documentation'
        'test:Test server configuration'
        'diagnose:Diagnose server issues'
        'snippet:Generate config snippet'
    )

    local -a completion_shells
    completion_shells=(
        'bash:Generate bash completion'
        'zsh:Generate zsh completion'
        'fish:Generate fish completion'
    )

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _describe -t commands 'claude-ctx command' commands
            ;;
        args)
            case $words[1] in
                mode)
                    _arguments \
                        '1: :->mode_command' \
                        '*::mode_arg:->mode_args'
                    case $state in
                        mode_command)
                            _describe -t mode_commands 'mode command' mode_commands
                            ;;
                    esac
                    ;;
                agent)
                    _arguments \
                        '1: :->agent_command' \
                        '*::agent_arg:->agent_args'
                    case $state in
                        agent_command)
                            _describe -t agent_commands 'agent command' agent_commands
                            ;;
                    esac
                    ;;
                rules)
                    _arguments \
                        '1: :->rules_command' \
                        '*::rules_arg:->rules_args'
                    case $state in
                        rules_command)
                            _describe -t rules_commands 'rules command' rules_commands
                            ;;
                    esac
                    ;;
                principles)
                    _arguments \
                        '1: :->principles_command' \
                        '*::principles_arg:->principles_args'
                    case $state in
                        principles_command)
                            _describe -t principles_commands 'principles command' principles_commands
                            ;;
                    esac
                    ;;
                skills)
                    _arguments \
                        '1: :->skills_command' \
                        '*::skills_arg:->skills_args'
                    case $state in
                        skills_command)
                            _describe -t skills_commands 'skills command' skills_commands
                            ;;
                    esac
                    ;;
                mcp)
                    _arguments \
                        '1: :->mcp_command' \
                        '*::mcp_arg:->mcp_args'
                    case $state in
                        mcp_command)
                            _describe -t mcp_commands 'mcp command' mcp_commands
                            ;;
                    esac
                    ;;
                completion)
                    _arguments \
                        '1: :->shell'
                    case $state in
                        shell)
                            _describe -t completion_shells 'shell' completion_shells
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac
}

_claude_ctx "$@"
"""


def generate_fish_completion() -> str:
    """Generate fish completion script."""
    return """# Fish completion for claude-ctx

# Top-level commands
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "mode" -d "Mode management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "agent" -d "Agent management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "rules" -d "Rule management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "principles" -d "Principles snippet management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "skills" -d "Skill management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "mcp" -d "MCP server management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "init" -d "Initialize project"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "profile" -d "Profile management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "workflow" -d "Workflow management"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "tui" -d "Launch terminal UI"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "doctor" -d "System diagnostics"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "version" -d "Show version"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "completion" -d "Generate completions"
complete -c claude-ctx -f -n "__fish_use_subcommand" -a "help" -d "Show help"

# Doctor subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from doctor" -l "fix" -d "Attempt auto-fix"

# Mode subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mode; and not __fish_seen_subcommand_from list status activate deactivate" -a "list" -d "List available modes"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mode; and not __fish_seen_subcommand_from list status activate deactivate" -a "status" -d "Show active modes"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mode; and not __fish_seen_subcommand_from list status activate deactivate" -a "activate" -d "Activate modes"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mode; and not __fish_seen_subcommand_from list status activate deactivate" -a "deactivate" -d "Deactivate modes"

# Agent subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "list" -d "List available agents"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "status" -d "Show active agents"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "activate" -d "Activate agents"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "deactivate" -d "Deactivate agents"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "deps" -d "Show dependencies"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "graph" -d "Display graph"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and not __fish_seen_subcommand_from list status activate deactivate deps graph validate" -a "validate" -d "Validate metadata"

# Agent deactivate flags
complete -c claude-ctx -f -n "__fish_seen_subcommand_from agent; and __fish_seen_subcommand_from deactivate" -l "force" -d "Override dependency checks"

# Rules subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from rules; and not __fish_seen_subcommand_from list status activate deactivate" -a "list" -d "List available rules"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from rules; and not __fish_seen_subcommand_from list status activate deactivate" -a "status" -d "Show active rules"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from rules; and not __fish_seen_subcommand_from list status activate deactivate" -a "activate" -d "Activate rules"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from rules; and not __fish_seen_subcommand_from list status activate deactivate" -a "deactivate" -d "Deactivate rules"

# Principles subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from principles; and not __fish_seen_subcommand_from list status activate deactivate build" -a "list" -d "List available principle snippets"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from principles; and not __fish_seen_subcommand_from list status activate deactivate build" -a "status" -d "Show active principle snippets"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from principles; and not __fish_seen_subcommand_from list status activate deactivate build" -a "activate" -d "Activate principle snippets"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from principles; and not __fish_seen_subcommand_from list status activate deactivate build" -a "deactivate" -d "Deactivate principle snippets"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from principles; and not __fish_seen_subcommand_from list status activate deactivate build" -a "build" -d "Build PRINCIPLES.md"

# Skills subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "list" -d "List skills"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "info" -d "Show skill details"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "validate" -d "Validate metadata"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "analyze" -d "Analyze text"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "suggest" -d "Suggest skills"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "metrics" -d "Show metrics"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from skills; and not __fish_seen_subcommand_from list info validate analyze suggest metrics deps agents compose versions analytics report trending community" -a "community" -d "Community skills"

# MCP subcommands
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "list" -d "List servers"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "show" -d "Show server info"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "docs" -d "Show documentation"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "test" -d "Test configuration"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "diagnose" -d "Diagnose issues"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from mcp; and not __fish_seen_subcommand_from list show docs test diagnose snippet" -a "snippet" -d "Config snippet"

# Completion shells
complete -c claude-ctx -f -n "__fish_seen_subcommand_from completion" -a "bash" -d "Bash completion"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from completion" -a "zsh" -d "Zsh completion"
complete -c claude-ctx -f -n "__fish_seen_subcommand_from completion" -a "fish" -d "Fish completion"
"""


def get_completion_script(shell: str) -> str:
    """Get completion script for the specified shell.

    Args:
        shell: Shell name (bash, zsh, or fish)

    Returns:
        Completion script content

    Raises:
        ValueError: If shell is not supported
    """
    shell = shell.lower()
    if shell == "bash":
        return generate_bash_completion()
    elif shell == "zsh":
        return generate_zsh_completion()
    elif shell == "fish":
        return generate_fish_completion()
    else:
        raise ValueError(
            f"Unsupported shell: {shell}. Supported shells: bash, zsh, fish"
        )


def get_installation_instructions(shell: str) -> str:
    """Get installation instructions for the specified shell.

    Args:
        shell: Shell name (bash, zsh, or fish)

    Returns:
        Installation instructions
    """
    shell = shell.lower()

    if shell == "bash":
        return """
# Bash Completion Installation

## Option 1: System-wide (requires sudo)
sudo claude-ctx completion bash > /etc/bash_completion.d/claude-ctx

## Option 2: User-specific
mkdir -p ~/.bash_completion.d
claude-ctx completion bash > ~/.bash_completion.d/claude-ctx

# Then add to ~/.bashrc:
if [ -f ~/.bash_completion.d/claude-ctx ]; then
    . ~/.bash_completion.d/claude-ctx
fi

# Reload your shell:
source ~/.bashrc
"""

    elif shell == "zsh":
        return """
# Zsh Completion Installation

## Option 1: Using fpath (recommended)
# Create completion directory if it doesn't exist
mkdir -p ~/.zsh/completions

# Generate completion file
claude-ctx completion zsh > ~/.zsh/completions/_claude-ctx

# Add to ~/.zshrc (before compinit):
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit
compinit

## Option 2: Direct sourcing
claude-ctx completion zsh > ~/.zsh/_claude-ctx
echo 'source ~/.zsh/_claude-ctx' >> ~/.zshrc

# Reload your shell:
source ~/.zshrc
"""

    elif shell == "fish":
        return """
# Fish Completion Installation

## Automatic installation
claude-ctx completion fish > ~/.config/fish/completions/claude-ctx.fish

# Completions are loaded automatically on next shell start
# Or reload immediately:
source ~/.config/fish/completions/claude-ctx.fish
"""

    else:
        return f"No installation instructions for shell: {shell}"
