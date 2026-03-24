#!/usr/bin/env python3
"""Validate that manpages are current with CLI definitions.

This script is used in pre-release checks to ensure manpages haven't
fallen out of sync with the actual CLI commands and options.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path to import cli module
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_ctx_py.commands.dev_manpages import (
    discover_subcommands,
    extract_subparser,
    generate_manpage,
)
from claude_ctx_py.cli import build_parser


def validate_manpages(docs_dir: Path | None = None, verbose: bool = False) -> Tuple[int, List[str]]:
    """Validate that manpages match current CLI definitions.

    Args:
        docs_dir: Directory containing manpage files (defaults to docs/reference)
        verbose: Print detailed comparison output

    Returns:
        Tuple of (exit_code, messages)
        - exit_code 0 if all manpages are current
        - exit_code 1 if any manpages are stale
    """
    if docs_dir is None:
        # Get the project root (parent of claude_ctx_py)
        docs_dir = Path(__file__).parent.parent.parent / "docs" / "reference"

    messages: List[str] = []
    stale_pages: List[str] = []

    parser = build_parser()

    # Check main manpage
    messages.append("Checking manpage versions...")
    main_manpage = generate_manpage(parser, "cortex")
    main_path = docs_dir / "cortex.1"

    if not main_path.exists():
        messages.append(f"  ✗ Missing: {main_path}")
        stale_pages.append("cortex.1")
    else:
        current = main_path.read_text()
        if current != main_manpage:
            messages.append("  ✗ Stale: cortex.1 (out of sync with CLI)")
            stale_pages.append("cortex.1")
            if verbose:
                messages.append("    Run: cortex dev manpages")
        else:
            messages.append("  ✓ cortex.1 is current")

    # Check subcommand manpages (auto-discovered from parser)
    subcommands = discover_subcommands(parser)

    for cmd, description in subcommands:
        subparser = extract_subparser(parser, cmd)
        if subparser:
            manpage = generate_manpage(subparser, f"cortex-{cmd}")
        else:
            minimal_parser = argparse.ArgumentParser(
                prog=f"cortex-{cmd}",
                description=description
            )
            manpage = generate_manpage(minimal_parser, f"cortex-{cmd}")

        path = docs_dir / f"cortex-{cmd}.1"

        if not path.exists():
            messages.append(f"  ✗ Missing: {path}")
            stale_pages.append(f"cortex-{cmd}.1")
        else:
            current = path.read_text()
            if current != manpage:
                messages.append(f"  ✗ Stale: cortex-{cmd}.1 (out of sync with CLI)")
                stale_pages.append(f"cortex-{cmd}.1")
                if verbose:
                    messages.append("    Run: cortex dev manpages")
            else:
                messages.append(f"  ✓ cortex-{cmd}.1 is current")

    # Summary
    messages.append("")
    if stale_pages:
        messages.append(f"Found {len(stale_pages)} stale manpage(s): {', '.join(stale_pages)}")
        messages.append("Run 'cortex dev manpages' to regenerate before releasing.")
        return 1, messages
    else:
        messages.append("✓ All manpages are current with CLI definitions")
        return 0, messages


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="cortex dev validate-manpages",
        description="Validate that manpages are current with CLI definitions"
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=None,
        help="Directory containing manpage files (default: docs/reference)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed comparison output"
    )

    args = parser.parse_args()
    exit_code, messages = validate_manpages(
        docs_dir=args.docs_dir,
        verbose=args.verbose
    )

    for message in messages:
        print(message)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
