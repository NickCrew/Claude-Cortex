"""Cortex setup - symlinks rules to ~/.claude/rules/cortex/"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.prompt import Confirm

from .core.base import _resolve_cortex_root


def _get_rules_source() -> Optional[Path]:
    """Find the rules directory in the package."""
    # Check relative to this file (installed package)
    pkg_root = Path(__file__).parent.parent
    candidates = [
        pkg_root / "rules",
        _resolve_cortex_root() / "rules",
    ]
    for candidate in candidates:
        if candidate.is_dir() and list(candidate.glob("*.md")):
            return candidate
    return None


def _symlink_rules(source_dir: Path, target_dir: Path, console: Console) -> Tuple[int, int]:
    """Symlink rule files from source to target directory.
    
    Returns (success_count, error_count)
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    
    success = 0
    errors = 0
    
    for rule_file in source_dir.glob("*.md"):
        target_link = target_dir / rule_file.name
        try:
            if target_link.is_symlink():
                target_link.unlink()
            elif target_link.exists():
                console.print(f"  [yellow]Skipped {rule_file.name} (file exists)[/yellow]")
                continue
            
            target_link.symlink_to(rule_file.resolve())
            console.print(f"  [green]✓[/green] {rule_file.name}")
            success += 1
        except OSError as e:
            console.print(f"  [red]✗[/red] {rule_file.name}: {e}")
            errors += 1
    
    return success, errors


def setup(console: Optional[Console] = None) -> Tuple[int, str]:
    """Run cortex setup - symlink rules to ~/.claude/rules/cortex/"""
    if console is None:
        console = Console()
    
    console.print()
    console.print("[bold]Cortex Setup[/bold]")
    console.print("-" * 40)
    
    # Find rules source
    rules_source = _get_rules_source()
    if rules_source is None:
        return 1, "Rules directory not found"
    
    rule_count = len(list(rules_source.glob("*.md")))
    console.print(f"Found {rule_count} rules in {rules_source}")
    
    # Target directory
    target_dir = Path.home() / ".claude" / "rules" / "cortex"
    console.print(f"Target: {target_dir}")
    console.print()
    
    if not Confirm.ask("Symlink rules to ~/.claude/rules/cortex/?", default=True, console=console):
        return 1, "Setup cancelled"
    
    console.print()
    success, errors = _symlink_rules(rules_source, target_dir, console)
    
    console.print()
    if errors == 0:
        console.print(f"[green]✓ Linked {success} rules[/green]")
        console.print()
        console.print("[dim]Claude Code will now auto-discover these rules.[/dim]")
        console.print("[dim]Run `claude` directly - no wrapper needed.[/dim]")
        return 0, f"Linked {success} rules"
    else:
        console.print(f"[yellow]Linked {success} rules with {errors} errors[/yellow]")
        return 1, f"Linked {success} rules with {errors} errors"


def should_run_setup() -> bool:
    """Check if setup should run (rules not yet linked)."""
    target_dir = Path.home() / ".claude" / "rules" / "cortex"
    if not target_dir.exists():
        return True
    # Check if any rules are linked
    return not any(target_dir.glob("*.md"))


if __name__ == "__main__":
    code, msg = setup()
    sys.exit(code)
