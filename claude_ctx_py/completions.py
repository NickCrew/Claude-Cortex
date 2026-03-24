"""Shell completion generation for cortex.

All completions are auto-discovered from the argparse parser tree,
so they stay in sync with the CLI without manual updates.
"""

from __future__ import annotations

import argparse
from typing import Dict, List, Tuple


def _discover_commands(
    parser: argparse.ArgumentParser,
) -> Tuple[List[Tuple[str, str]], Dict[str, List[str]]]:
    """Walk the parser tree and return top-level commands + their subcommands.

    Returns:
        (commands, subcommands) where
        - commands is a list of (name, help_text) for top-level commands
        - subcommands is a dict mapping command name → list of subcommand names
    """
    commands: List[Tuple[str, str]] = []
    subcommands: Dict[str, List[str]] = {}

    for action in parser._subparsers._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue

        # Build help lookup
        help_lookup: Dict[str, str] = {}
        for choice_action in action._choices_actions:
            help_lookup[choice_action.dest] = choice_action.help or ""

        for name, subparser in action.choices.items():
            commands.append((name, help_lookup.get(name, "")))

            # Look for nested subcommands
            subs: List[str] = []
            if subparser._subparsers:
                for sub_action in subparser._subparsers._actions:
                    if isinstance(sub_action, argparse._SubParsersAction):
                        subs.extend(sub_action.choices.keys())
            if subs:
                subcommands[name] = sorted(subs)

    return sorted(commands), subcommands


def generate_bash_completion(parser: argparse.ArgumentParser) -> str:
    """Generate bash completion script from parser."""
    commands, subcommands = _discover_commands(parser)
    cmd_names = " ".join(name for name, _ in commands)

    lines = [
        "# Bash completion for cortex (auto-generated)",
        "_cortex_completion() {",
        "    local cur prev",
        "    COMPREPLY=()",
        '    cur="${COMP_WORDS[COMP_CWORD]}"',
        '    prev="${COMP_WORDS[COMP_CWORD-1]}"',
        "",
        f'    local commands="{cmd_names}"',
        "",
        "    if [[ ${{COMP_CWORD}} -eq 1 ]]; then",
        '        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))',
        "        return 0",
        "    fi",
        "",
        '    local cmd="${COMP_WORDS[1]}"',
        "",
        '    case "${cmd}" in',
    ]

    for name, subs in sorted(subcommands.items()):
        sub_str = " ".join(subs)
        lines.extend([
            f"        {name})",
            f'            local {name}_cmds="{sub_str}"',
            "            if [[ ${COMP_CWORD} -eq 2 ]]; then",
            f'                COMPREPLY=($(compgen -W "${{{name}_cmds}}" -- ${{cur}}))',
            "            fi",
            "            ;;",
        ])

    lines.extend([
        "    esac",
        "    return 0",
        "}",
        "complete -F _cortex_completion cortex",
    ])
    return "\n".join(lines) + "\n"


def generate_zsh_completion(parser: argparse.ArgumentParser) -> str:
    """Generate zsh completion script from parser."""
    commands, subcommands = _discover_commands(parser)

    lines = [
        "#compdef cortex",
        "# Zsh completion for cortex (auto-generated)",
        "_cortex() {",
        "    local -a commands",
        "    commands=(",
    ]

    for name, help_text in commands:
        desc = help_text or name
        # Escape single quotes in descriptions
        desc = desc.replace("'", "'\\''")
        lines.append(f"        '{name}:{desc}'")

    lines.append("    )")
    lines.append("")

    # Declare subcommand arrays
    for name, subs in sorted(subcommands.items()):
        sub_items = " ".join(f"'{s}'" for s in subs)
        lines.append(f"    local -a {name}_commands=({sub_items})")

    lines.extend([
        "",
        "    _arguments -C '1: :->command' '*::arg:->args'",
        "",
        "    case $state in",
        "        command)",
        "            _describe -t commands 'cortex command' commands",
        "            ;;",
        "        args)",
        "            case $words[1] in",
    ])

    for name in sorted(subcommands.keys()):
        lines.append(
            f"                {name}) _describe -t {name}_commands '{name} command' {name}_commands ;;"
        )

    lines.extend([
        "            esac",
        "            ;;",
        "    esac",
        "}",
        '_cortex "$@"',
    ])
    return "\n".join(lines) + "\n"


def generate_fish_completion(parser: argparse.ArgumentParser) -> str:
    """Generate fish completion script from parser."""
    commands, subcommands = _discover_commands(parser)

    lines = ["# Fish completion for cortex (auto-generated)", ""]

    # Top-level commands
    lines.append("# Top-level commands")
    for name, help_text in commands:
        desc = help_text or name
        lines.append(
            f'complete -c cortex -f -n "__fish_use_subcommand" -a "{name}" -d "{desc}"'
        )

    lines.append("")

    # Subcommands
    for name, subs in sorted(subcommands.items()):
        sub_str = " ".join(subs)
        lines.append(f"# {name.capitalize()} subcommands")
        lines.append(
            f'complete -c cortex -f -n "__fish_seen_subcommand_from {name}" -a "{sub_str}"'
        )
        lines.append("")

    return "\n".join(lines)


def get_completion_script(shell: str, parser: argparse.ArgumentParser | None = None) -> str:
    """Get completion script for the specified shell.

    If *parser* is ``None``, builds one from :func:`claude_ctx_py.cli.build_parser`.
    """
    if parser is None:
        from .cli import build_parser
        parser = build_parser()

    shell = shell.lower()
    if shell == "bash":
        return generate_bash_completion(parser)
    elif shell == "zsh":
        return generate_zsh_completion(parser)
    elif shell == "fish":
        return generate_fish_completion(parser)
    else:
        raise ValueError(f"Unsupported shell: {shell}. Supported: bash, zsh, fish")
