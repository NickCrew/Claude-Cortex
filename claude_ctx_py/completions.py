"""Shell completion generation for cortex."""

from __future__ import annotations


def generate_bash_completion() -> str:
    """Generate bash completion script."""
    return """# Bash completion for cortex
_cortex_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    local commands="agent rules hooks skills mcp worktree ai export memory review tui status install version"

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))
        return 0
    fi

    local cmd="${COMP_WORDS[1]}"

    case "${cmd}" in
        agent)
            local agent_cmds="list status activate deactivate deps graph validate"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${agent_cmds}" -- ${cur}))
            fi
            ;;
        rules)
            local rules_cmds="list status activate deactivate"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${rules_cmds}" -- ${cur}))
            fi
            ;;
        hooks)
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "validate" -- ${cur}))
            fi
            ;;
        skills)
            local skills_cmds="list info validate analyze suggest metrics deps agents compose versions analytics report trending recommend feedback rate ratings top-rated export-ratings community"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${skills_cmds}" -- ${cur}))
            fi
            ;;
        mcp)
            local mcp_cmds="list list-docs status activate deactivate show docs test diagnose snippet"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${mcp_cmds}" -- ${cur}))
            fi
            ;;
        worktree)
            local worktree_cmds="list add remove prune dir"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${worktree_cmds}" -- ${cur}))
            fi
            ;;
        ai)
            local ai_cmds="recommend auto-activate export record watch"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${ai_cmds}" -- ${cur}))
            fi
            ;;
        export)
            local export_cmds="list context agents"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${export_cmds}" -- ${cur}))
            fi
            ;;
        memory)
            local memory_cmds="remember project capture fix auto list search stats"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${memory_cmds}" -- ${cur}))
            fi
            ;;
        install)
            local install_cmds="link aliases completions manpage post"
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=($(compgen -W "${install_cmds}" -- ${cur}))
            fi
            ;;
    esac
    return 0
}
complete -F _cortex_completion cortex
"""


def generate_zsh_completion() -> str:
    """Generate zsh completion script."""
    return """#compdef cortex
_cortex() {
    local -a commands
    commands=(
        'agent:Agent management'
        'rules:Rule management'
        'hooks:Hook commands'
        'skills:Skill management'
        'mcp:MCP server management'
        'worktree:Git worktree management'
        'ai:AI assistant commands'
        'export:Export context'
        'memory:Memory vault commands'
        'review:Run review gate'
        'tui:Launch terminal UI'
        'status:Show overall status'
        'install:Install integrations'
        'version:Show version'
    )

    local -a agent_commands=('list' 'status' 'activate' 'deactivate' 'deps' 'graph' 'validate')
    local -a rules_commands=('list' 'status' 'activate' 'deactivate')
    local -a hooks_commands=('validate')
    local -a skills_commands=('list' 'info' 'validate' 'analyze' 'suggest' 'metrics' 'deps' 'agents' 'compose' 'versions' 'analytics' 'report' 'trending' 'recommend' 'feedback' 'rate' 'ratings' 'top-rated' 'export-ratings' 'community')
    local -a mcp_commands=('list' 'list-docs' 'status' 'activate' 'deactivate' 'show' 'docs' 'test' 'diagnose' 'snippet')
    local -a worktree_commands=('list' 'add' 'remove' 'prune' 'dir')
    local -a ai_commands=('recommend' 'auto-activate' 'export' 'record' 'watch')
    local -a export_commands=('list' 'context' 'agents')
    local -a memory_commands=('remember' 'project' 'capture' 'fix' 'auto' 'list' 'search' 'stats')
    local -a install_commands=('link' 'aliases' 'completions' 'manpage' 'post')

    _arguments -C '1: :->command' '*::arg:->args'

    case $state in
        command)
            _describe -t commands 'cortex command' commands
            ;;
        args)
            case $words[1] in
                agent) _describe -t agent_commands 'agent command' agent_commands ;;
                rules) _describe -t rules_commands 'rules command' rules_commands ;;
                hooks) _describe -t hooks_commands 'hooks command' hooks_commands ;;
                skills) _describe -t skills_commands 'skills command' skills_commands ;;
                mcp) _describe -t mcp_commands 'mcp command' mcp_commands ;;
                worktree) _describe -t worktree_commands 'worktree command' worktree_commands ;;
                ai) _describe -t ai_commands 'ai command' ai_commands ;;
                export) _describe -t export_commands 'export command' export_commands ;;
                memory) _describe -t memory_commands 'memory command' memory_commands ;;
                install) _describe -t install_commands 'install command' install_commands ;;
            esac
            ;;
    esac
}
_cortex "$@"
"""


def generate_fish_completion() -> str:
    """Generate fish completion script."""
    return """# Fish completion for cortex

# Top-level commands
complete -c cortex -f -n "__fish_use_subcommand" -a "agent" -d "Agent management"
complete -c cortex -f -n "__fish_use_subcommand" -a "rules" -d "Rule management"
complete -c cortex -f -n "__fish_use_subcommand" -a "hooks" -d "Hook commands"
complete -c cortex -f -n "__fish_use_subcommand" -a "skills" -d "Skill management"
complete -c cortex -f -n "__fish_use_subcommand" -a "mcp" -d "MCP server management"
complete -c cortex -f -n "__fish_use_subcommand" -a "worktree" -d "Git worktree management"
complete -c cortex -f -n "__fish_use_subcommand" -a "ai" -d "AI assistant commands"
complete -c cortex -f -n "__fish_use_subcommand" -a "export" -d "Export context"
complete -c cortex -f -n "__fish_use_subcommand" -a "memory" -d "Memory vault commands"
complete -c cortex -f -n "__fish_use_subcommand" -a "review" -d "Run review gate"
complete -c cortex -f -n "__fish_use_subcommand" -a "tui" -d "Launch terminal UI"
complete -c cortex -f -n "__fish_use_subcommand" -a "status" -d "Show overall status"
complete -c cortex -f -n "__fish_use_subcommand" -a "install" -d "Install integrations"
complete -c cortex -f -n "__fish_use_subcommand" -a "version" -d "Show version"

# Agent subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from agent" -a "list status activate deactivate deps graph validate"

# Rules subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from rules" -a "list status activate deactivate"

# Hooks subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from hooks" -a "validate"

# Skills subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from skills" -a "list info validate analyze suggest metrics deps agents compose versions analytics report trending recommend feedback rate ratings top-rated export-ratings community"

# MCP subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from mcp" -a "list list-docs status activate deactivate show docs test diagnose snippet"

# Worktree subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from worktree" -a "list add remove prune dir"

# AI subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from ai" -a "recommend auto-activate export record watch"

# Export subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from export" -a "list context agents"

# Memory subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from memory" -a "remember project capture fix auto list search stats"

# Install subcommands
complete -c cortex -f -n "__fish_seen_subcommand_from install" -a "link aliases completions manpage post"
"""


def get_completion_script(shell: str) -> str:
    """Get completion script for the specified shell."""
    shell = shell.lower()
    if shell == "bash":
        return generate_bash_completion()
    elif shell == "zsh":
        return generate_zsh_completion()
    elif shell == "fish":
        return generate_fish_completion()
    else:
        raise ValueError(f"Unsupported shell: {shell}. Supported: bash, zsh, fish")
