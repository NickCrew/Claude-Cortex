#!/usr/bin/env python3
"""Generate manpages from argparse definitions."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import cli module
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_ctx_py.cli import build_parser


def generate_manpage(parser: argparse.ArgumentParser, name: str, section: int = 1) -> str:
    """Generate a manpage from an argparse parser.
    
    Args:
        parser: The argparse parser to generate from
        name: The command name
        section: Man section number (default: 1)
        
    Returns:
        The generated manpage content
    """
    today = datetime.now().strftime("%Y-%m-%d")
    version = "2.0.0"  # TODO: Extract from pyproject.toml
    
    lines = [
        f'.TH {name.upper()} {section} "{today}" "{name} {version}" "User Commands"',
        ".SH NAME",
        f"{name} \\- {parser.description or 'Command-line tool'}",
        ".SH SYNOPSIS",
        f".B {name}",
    ]
    
    # Add usage pattern
    if parser._subparsers:
        lines.extend([
            "[",
            "B-h",
            "    R | ",
            "        B--help",
            "               R]",
            ".br",
            f".B {name}",
            "",
            "ICOMMAND",
            "        R [",
            "           ISUBCOMMAND",
            "                      R] [",
            "                          IARGS",
            "                               R...]"
        ])
    else:
        lines.append("[IOPTIONS...R]")
    
    # Description
    lines.extend([
        ".SH DESCRIPTION",
        f".B {name}",
    ])
    
    if parser.description:
        lines.append(f"is {parser.description}")
    
    # Commands
    if parser._subparsers:
        lines.extend([
            ".SH COMMANDS",
            "Available commands:",
            ".TP",
        ])
        
        for action in parser._subparsers._actions:
            if isinstance(action, argparse._SubParsersAction):
                for choice, subparser in action.choices.items():
                    help_text = action._choices_actions[0].help if action._choices_actions else ""
                    # Find the actual help text for this choice
                    for choice_action in action._choices_actions:
                        if choice_action.dest == choice or getattr(choice_action, 'metavar', None) == choice:
                            help_text = choice_action.help or ""
                            break
                    
                    lines.extend([
                        f".B {choice}",
                        help_text or "No description available",
                        ".TP",
                    ])
    
    # Options
    lines.extend([
        ".SH OPTIONS",
        ".TP",
        ".B \\-h, \\-\\-help",
        "Show help message and exit",
    ])
    
    # Environment
    lines.extend([
        ".SH ENVIRONMENT",
        ".TP",
        ".B CLAUDE_PLUGIN_ROOT",
        "Override for context directory (set automatically by Claude Code when running plugin commands)",
    ])
    
    # Files
    lines.extend([
        ".SH FILES",
        ".TP",
        ".B ~/.claude/",
        "Default context directory containing agents, modes, rules, and other configuration",
    ])
    
    # See also
    lines.extend([
        ".SH SEE ALSO",
        f".BR {name}-tui (1),",
        f".BR {name}-workflow (1)",
    ])
    
    # Authors
    lines.extend([
        ".SH AUTHORS",
        "Nicholas Ferguson <ncf423@gmail.com>",
    ])
    
    return "\n".join(lines)


def extract_subparser(parser: argparse.ArgumentParser, command: str) -> argparse.ArgumentParser | None:
    """Extract a subparser for a specific command."""
    for action in parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices.get(command)
    return None


def main() -> int:
    """Generate all manpages."""
    parser = build_parser()
    docs_dir = Path(__file__).parent.parent / "docs" / "reference"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main manpage
    print("📄 Generating cortex.1...")
    main_manpage = generate_manpage(parser, "cortex")
    main_path = docs_dir / "cortex.1"
    main_path.write_text(main_manpage)
    print(f"   ✓ {main_path}")
    
    # Generate subcommand manpages
    subcommands = [
        ("tui", "Interactive TUI for agent management"),
        ("workflow", "Workflow management commands"),
    ]
    
    for cmd, description in subcommands:
        print(f"📄 Generating cortex-{cmd}.1...")
        subparser = extract_subparser(parser, cmd)
        if subparser:
            manpage = generate_manpage(subparser, f"cortex-{cmd}")
        else:
            # Generate minimal manpage if subparser not found
            minimal_parser = argparse.ArgumentParser(
                prog=f"cortex-{cmd}",
                description=description
            )
            manpage = generate_manpage(minimal_parser, f"cortex-{cmd}")
        
        path = docs_dir / f"cortex-{cmd}.1"
        path.write_text(manpage)
        print(f"   ✓ {path}")
    
    print("\n✓ All manpages generated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
