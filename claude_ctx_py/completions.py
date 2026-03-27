"""Shell completion generation for cortex.

All completions are auto-discovered from the argparse parser tree,
so they stay in sync with the CLI without manual updates.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Parser tree discovery
# ---------------------------------------------------------------------------


@dataclass
class CommandInfo:
    """Parsed metadata for a single CLI command/subcommand."""

    name: str
    help: str = ""
    flags: List[Tuple[str, str]] = field(default_factory=list)  # (flag, help)
    subcommands: List["CommandInfo"] = field(default_factory=list)


def _extract_flags(parser: argparse.ArgumentParser) -> List[Tuple[str, str]]:
    """Extract flag names and help text from a parser."""
    flags: List[Tuple[str, str]] = []
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            continue
        if isinstance(action, argparse._HelpAction):
            continue
        for opt in action.option_strings:
            if opt.startswith("--"):
                help_text = action.help or ""
                if isinstance(help_text, str):
                    help_text = help_text.replace("%default", str(action.default or ""))
                flags.append((opt, help_text))
                break  # only take the long form
    return flags


def _discover_tree(parser: argparse.ArgumentParser) -> List[CommandInfo]:
    """Recursively walk the parser tree and return the full command hierarchy."""
    commands: List[CommandInfo] = []

    if parser._subparsers is None:
        return commands

    for action in parser._subparsers._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue

        # Build help lookup from _choices_actions
        help_lookup: Dict[str, str] = {}
        for choice_action in action._choices_actions:
            help_lookup[choice_action.dest] = choice_action.help or ""

        for name, subparser in action.choices.items():
            info = CommandInfo(
                name=name,
                help=help_lookup.get(name, ""),
                flags=_extract_flags(subparser),
                subcommands=_discover_tree(subparser),
            )
            commands.append(info)

    return sorted(commands, key=lambda c: c.name)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _escape_zsh(text: str) -> str:
    """Escape text for zsh completion descriptions."""
    return text.replace("'", "'\\''").replace("[", "\\[").replace("]", "\\]")


def _escape_bash(text: str) -> str:
    """Escape text for bash."""
    return text.replace('"', '\\"')


def _escape_fish(text: str) -> str:
    """Escape text for fish descriptions."""
    return text.replace('"', '\\"').replace("'", "\\'")


# ---------------------------------------------------------------------------
# Zsh completion
# ---------------------------------------------------------------------------


def _zsh_command_function(
    func_name: str,
    cmd: CommandInfo,
    depth: int = 0,
) -> List[str]:
    """Generate a zsh completion function for a command and its children."""
    lines: List[str] = []
    indent = "    "

    lines.append(f"{func_name}() {{")

    # Flags for this command
    if cmd.flags or cmd.subcommands:
        lines.append(f"{indent}local -a args")
        lines.append(f"{indent}args=(")
        for flag, help_text in cmd.flags:
            desc = _escape_zsh(help_text) if help_text else flag
            lines.append(f"{indent}    '{flag}[{desc}]'")
        lines.append(f"{indent})")
        lines.append("")

    if cmd.subcommands:
        # Has subcommands — use _arguments with state machine
        lines.append(f"{indent}local -a subcmds")
        lines.append(f"{indent}subcmds=(")
        for sub in cmd.subcommands:
            desc = _escape_zsh(sub.help) if sub.help else sub.name
            lines.append(f"{indent}    '{sub.name}:{desc}'")
        lines.append(f"{indent})")
        lines.append("")

        if cmd.flags:
            lines.append(f"{indent}_arguments -C $args '1: :->subcmd' '*::arg:->args'")
        else:
            lines.append(f"{indent}_arguments -C '1: :->subcmd' '*::arg:->args'")
        lines.append("")
        lines.append(f"{indent}case $state in")
        lines.append(f"{indent}    subcmd)")
        lines.append(f"{indent}        _describe -t subcmds '{cmd.name} command' subcmds")
        lines.append(f"{indent}        ;;")
        lines.append(f"{indent}    args)")
        lines.append(f"{indent}        case $words[1] in")
        for sub in cmd.subcommands:
            child_func = f"_cortex_{cmd.name}_{sub.name}".replace("-", "_")
            lines.append(f"{indent}            {sub.name}) {child_func} ;;")
        lines.append(f"{indent}        esac")
        lines.append(f"{indent}        ;;")
        lines.append(f"{indent}esac")
    elif cmd.flags:
        # Leaf command with flags — just complete flags
        lines.append(f"{indent}_arguments $args")
    else:
        lines.append(f"{indent}_default")

    lines.append("}")
    lines.append("")
    return lines


def generate_zsh_completion(parser: argparse.ArgumentParser) -> str:
    """Generate zsh completion script from parser."""
    tree = _discover_tree(parser)

    lines = [
        "#compdef cortex",
        "# Zsh completion for cortex (auto-generated)",
        "# Regenerate: cortex install completions --force",
        "",
    ]

    # Generate child functions first (bottom-up)
    for cmd in tree:
        for sub in cmd.subcommands:
            # Leaf subcommand functions
            child_func = f"_cortex_{cmd.name}_{sub.name}".replace("-", "_")
            lines.extend(_zsh_command_function(child_func, sub, depth=2))

        # Parent command functions
        if cmd.subcommands or cmd.flags:
            parent_func = f"_cortex_{cmd.name}".replace("-", "_")
            lines.extend(_zsh_command_function(parent_func, cmd, depth=1))

    # Main function
    lines.append("_cortex() {")
    lines.append("    local -a commands")
    lines.append("    commands=(")
    for cmd in tree:
        desc = _escape_zsh(cmd.help) if cmd.help else cmd.name
        lines.append(f"        '{cmd.name}:{desc}'")
    lines.append("    )")
    lines.append("")

    # Global flags from the root parser
    root_flags = _extract_flags(parser)
    if root_flags:
        lines.append("    local -a global_args")
        lines.append("    global_args=(")
        for flag, help_text in root_flags:
            desc = _escape_zsh(help_text) if help_text else flag
            lines.append(f"        '{flag}[{desc}]'")
        lines.append("    )")
        lines.append("")
        lines.append("    _arguments -C $global_args '1: :->command' '*::arg:->args'")
    else:
        lines.append("    _arguments -C '1: :->command' '*::arg:->args'")

    lines.append("")
    lines.append("    case $state in")
    lines.append("        command)")
    lines.append("            _describe -t commands 'cortex command' commands")
    lines.append("            ;;")
    lines.append("        args)")
    lines.append("            case $words[1] in")
    for cmd in tree:
        func_name = f"_cortex_{cmd.name}".replace("-", "_")
        if cmd.subcommands or cmd.flags:
            lines.append(f"                {cmd.name}) {func_name} ;;")
        else:
            lines.append(f"                {cmd.name}) _default ;;")
    lines.append("            esac")
    lines.append("            ;;")
    lines.append("    esac")
    lines.append("}")
    lines.append('_cortex "$@"')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Bash completion
# ---------------------------------------------------------------------------


def generate_bash_completion(parser: argparse.ArgumentParser) -> str:
    """Generate bash completion script from parser."""
    tree = _discover_tree(parser)

    lines = [
        "# Bash completion for cortex (auto-generated)",
        "# Regenerate: cortex install completions --force",
        "_cortex_completion() {",
        "    local cur prev cmd subcmd",
        "    COMPREPLY=()",
        '    cur="${COMP_WORDS[COMP_CWORD]}"',
        '    prev="${COMP_WORDS[COMP_CWORD-1]}"',
        "",
    ]

    # Top-level commands
    cmd_names = " ".join(cmd.name for cmd in tree)
    lines.append(f'    local commands="{cmd_names}"')
    lines.append("")

    # Collect all flags per command path
    lines.append("    if [[ ${COMP_CWORD} -eq 1 ]]; then")
    lines.append('        COMPREPLY=($(compgen -W "${commands}" -- ${cur}))')
    lines.append("        return 0")
    lines.append("    fi")
    lines.append("")
    lines.append('    cmd="${COMP_WORDS[1]}"')
    lines.append("")

    # Handle --flags at any position
    lines.append('    if [[ "${cur}" == --* ]]; then')
    lines.append('        case "${cmd}" in')
    for cmd in tree:
        if cmd.flags:
            flag_names = " ".join(f for f, _ in cmd.flags)
            lines.append(f"            {cmd.name})")

            # If there are subcommands, also check subcommand flags
            if cmd.subcommands:
                lines.append("                if [[ ${COMP_CWORD} -ge 3 ]]; then")
                lines.append('                    subcmd="${COMP_WORDS[2]}"')
                lines.append('                    case "${subcmd}" in')
                for sub in cmd.subcommands:
                    if sub.flags:
                        sub_flags = " ".join(f for f, _ in sub.flags)
                        lines.append(f'                        {sub.name}) COMPREPLY=($(compgen -W "{sub_flags}" -- ${{cur}})) ;;')
                lines.append("                    esac")
                lines.append("                else")
                lines.append(f'                    COMPREPLY=($(compgen -W "{flag_names}" -- ${{cur}}))')
                lines.append("                fi")
            else:
                lines.append(f'                COMPREPLY=($(compgen -W "{flag_names}" -- ${{cur}}))')
            lines.append("                ;;")
    lines.append("        esac")
    lines.append("        return 0")
    lines.append("    fi")
    lines.append("")

    # Handle subcommand completion
    lines.append("    if [[ ${COMP_CWORD} -eq 2 ]]; then")
    lines.append('        case "${cmd}" in')
    for cmd in tree:
        if cmd.subcommands:
            sub_names = " ".join(sub.name for sub in cmd.subcommands)
            lines.append(f'            {cmd.name}) COMPREPLY=($(compgen -W "{sub_names}" -- ${{cur}})) ;;')
    lines.append("        esac")
    lines.append("    fi")
    lines.append("")

    lines.extend([
        "    return 0",
        "}",
        "complete -F _cortex_completion cortex",
    ])
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Fish completion
# ---------------------------------------------------------------------------


def generate_fish_completion(parser: argparse.ArgumentParser) -> str:
    """Generate fish completion script from parser."""
    tree = _discover_tree(parser)

    lines = [
        "# Fish completion for cortex (auto-generated)",
        "# Regenerate: cortex install completions --force",
        "",
    ]

    # Top-level commands
    lines.append("# Top-level commands")
    for cmd in tree:
        desc = _escape_fish(cmd.help) if cmd.help else cmd.name
        lines.append(
            f'complete -c cortex -f -n "__fish_use_subcommand" -a "{cmd.name}" -d "{desc}"'
        )
    lines.append("")

    # Subcommands and flags per command
    for cmd in tree:
        if cmd.subcommands:
            lines.append(f"# {cmd.name} subcommands")
            for sub in cmd.subcommands:
                desc = _escape_fish(sub.help) if sub.help else sub.name
                lines.append(
                    f'complete -c cortex -f -n "__fish_seen_subcommand_from {cmd.name}" -a "{sub.name}" -d "{desc}"'
                )
            lines.append("")

        # Flags for the command itself
        if cmd.flags:
            lines.append(f"# {cmd.name} flags")
            for flag, help_text in cmd.flags:
                long_name = flag.lstrip("-")
                desc = _escape_fish(help_text) if help_text else long_name
                lines.append(
                    f'complete -c cortex -f -n "__fish_seen_subcommand_from {cmd.name}" -l "{long_name}" -d "{desc}"'
                )
            lines.append("")

        # Flags for subcommands
        for sub in cmd.subcommands:
            if sub.flags:
                lines.append(f"# {cmd.name} {sub.name} flags")
                for flag, help_text in sub.flags:
                    long_name = flag.lstrip("-")
                    desc = _escape_fish(help_text) if help_text else long_name
                    # Fish doesn't have great 3-level condition support, approximate with seen_subcommand
                    lines.append(
                        f'complete -c cortex -f -n "__fish_seen_subcommand_from {sub.name}" -l "{long_name}" -d "{desc}"'
                    )
                lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Compatibility shim
# ---------------------------------------------------------------------------

def _discover_commands(
    parser: argparse.ArgumentParser,
) -> Tuple[List[Tuple[str, str]], Dict[str, List[str]]]:
    """Legacy API: return flat command list + subcommand dict."""
    tree = _discover_tree(parser)
    commands = [(cmd.name, cmd.help) for cmd in tree]
    subcommands = {
        cmd.name: [sub.name for sub in cmd.subcommands]
        for cmd in tree
        if cmd.subcommands
    }
    return commands, subcommands


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


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
