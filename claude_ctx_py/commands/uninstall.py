#!/usr/bin/env python3
"""Uninstall command for cortex."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def uninstall(dry_run: bool = False, keep_config: bool = False) -> Tuple[int, str]:
    """Uninstall cortex rules and optionally the package.

    Args:
        dry_run: Show what would be done without actually doing it
        keep_config: Keep configuration files in ~/.claude/

    Returns:
        (exit_code, message) tuple
    """
    messages = []
    messages.append("=== Cortex Uninstall ===")
    messages.append("")

    rules_target = Path.home() / ".claude" / "rules" / "cortex"

    # Remove rule symlinks
    if rules_target.exists():
        if dry_run:
            messages.append(f"Would remove: {rules_target}")
        else:
            messages.append("Removing rule symlinks...")
            shutil.rmtree(rules_target)
            messages.append(f"  Removed: {rules_target}")
    else:
        messages.append("No rule symlinks found.")

    # Remove config files if requested
    if not keep_config:
        config_files = [
            Path.home() / ".claude" / "cortex" / "docs-bookmarks.json",
            Path.home() / ".claude" / "tour-state.json",
        ]
        removed_configs = []
        for config_file in config_files:
            if config_file.exists():
                if dry_run:
                    messages.append(f"Would remove: {config_file}")
                else:
                    config_file.unlink()
                    removed_configs.append(str(config_file))

        if removed_configs and not dry_run:
            messages.append("")
            messages.append("Removed config files:")
            for cf in removed_configs:
                messages.append(f"  {cf}")

    # Check if package is installed
    try:
        result = subprocess.run(
            ["pip", "show", "claude-cortex"],
            capture_output=True,
            text=True,
            check=False,
        )
        package_installed = result.returncode == 0
    except FileNotFoundError:
        package_installed = False

    if package_installed:
        messages.append("")
        if dry_run:
            messages.append("Would prompt to uninstall Python package")
        else:
            messages.append("Python package 'claude-cortex' is installed.")
            messages.append("")
            messages.append("To uninstall the package, run:")
            messages.append("  pip uninstall claude-cortex")
            messages.append("  # or")
            messages.append("  pipx uninstall claude-cortex")

    messages.append("")
    if dry_run:
        messages.append("=== Dry Run Complete ===")
    else:
        messages.append("=== Uninstall Complete ===")

    return 0, "\n".join(messages)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for uninstall command."""
    import argparse

    parser = argparse.ArgumentParser(description="Uninstall cortex")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Keep configuration files in ~/.claude/",
    )

    args = parser.parse_args(argv)

    exit_code, message = uninstall(
        dry_run=args.dry_run,
        keep_config=args.keep_config,
    )
    print(message)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
