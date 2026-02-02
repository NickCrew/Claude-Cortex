"""First-run setup for cortex CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from . import shell_integration


def should_run_wizard() -> bool:
    """Check if setup should run (first time only)."""
    if os.environ.get("CORTEX_SKIP_WIZARD"):
        return False
    if not sys.stdin.isatty():
        return False
    
    # Check if rules are already linked (either as symlink or cortex subdir)
    claude_rules = Path.home() / ".claude" / "rules"
    if claude_rules.is_symlink():
        return False
    if (claude_rules / "cortex").exists():
        return False
    return True


def _symlink_rules(console: Console, dry_run: bool = False) -> Tuple[int, str]:
    """Symlink content directories to ~/.claude/."""
    from .installer import link_content
    
    if dry_run:
        return link_content(dry_run=True)
    
    return link_content(force=False)


def run_wizard(console: Optional[Console] = None) -> Tuple[int, str]:
    """Run first-time setup.
    
    1. Symlink rules to ~/.claude/rules/cortex/
    2. Optionally install shell completions/aliases
    """
    if console is None:
        console = Console()
    
    console.print()
    console.print(Panel(
        "[bold]Cortex Setup[/bold]\n\n"
        "This will:\n"
        "  • Symlink agents, skills, rules, mcp to ~/.claude/\n"
        "  • Optionally install shell completions",
        border_style="cyan",
    ))
    console.print()
    
    if not Confirm.ask("Continue?", default=True, console=console):
        return 1, "Setup cancelled"
    
    # 1. Symlink rules
    code, msg = _symlink_rules(console)
    console.print(msg)
    if code != 0:
        return code, msg
    
    # 2. Shell integration (optional)
    console.print()
    try:
        detected_shell, rc_path = shell_integration.detect_shell()
        console.print(f"Detected shell: [cyan]{detected_shell}[/cyan]")
        
        if Confirm.ask("Install shell completions?", default=True, console=console):
            from . import installer
            code, msg = installer.install_completions(shell=detected_shell)
            console.print(msg.split('\n')[0])  # Just first line
        
        if Confirm.ask("Install shell aliases (ctx, ctx-copy)?", default=True, console=console):
            code, msg = shell_integration.install_aliases(
                shell=detected_shell,
                rc_file=rc_path,
            )
            console.print(msg.split('\n')[0])
            
    except RuntimeError:
        console.print("[dim]Shell not detected, skipping shell integration[/dim]")
    
    # Done
    console.print()
    console.print(Panel(
        "[bold green]Setup complete![/bold green]\n\n"
        "Rules are now available to Claude Code.\n"
        "Run [cyan]cortex agent list[/cyan] to see available agents.",
        border_style="green",
    ))
    
    return 0, "Setup complete"


def run_wizard_non_interactive() -> Tuple[int, str]:
    """Non-interactive setup (CI, scripts)."""
    console = Console()
    return _symlink_rules(console)
