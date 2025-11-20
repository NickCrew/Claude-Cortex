"""Mode management functions."""

from __future__ import annotations


import builtins
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple

# Import from base module
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    NC,
    _color,
    _is_disabled,
    _iter_md_files,
    _refresh_claude_md,
    _remove_exact_entries,
    _inactive_category_dir,
    _inactive_dir_candidates,
    _ensure_inactive_category_dir,
    _resolve_claude_dir,
    _update_with_backup,
)
from .mode_metadata import (
    parse_mode_metadata,
    get_mode_conflicts,
    check_mode_dependencies,
    get_priority_action,
    ModeMetadata,
)


def _mode_active_file(claude_dir: Path) -> Path:
    return claude_dir / ".active-modes"


def _mode_inactive_dir(claude_dir: Path) -> Path:
    return _ensure_inactive_category_dir(claude_dir, "modes")


def _find_inactive_mode_file(claude_dir: Path, mode: str) -> Optional[Path]:
    filename = f"{mode}.md"
    for directory in _inactive_dir_candidates(claude_dir, "modes"):
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    return None


def mode_activate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = _find_inactive_mode_file(claude_dir, mode)
    active_path = modes_dir / f"{mode}.md"

    if inactive_path is None:
        return 1, _color(f"Mode '{mode}' not found in inactive modes", RED)

    modes_dir.mkdir(parents=True, exist_ok=True)
    active_path.parent.mkdir(parents=True, exist_ok=True)

    if active_path.exists():
        active_path.unlink()
    inactive_path.replace(active_path)

    active_modes = _mode_active_file(claude_dir)
    with active_modes.open("a", encoding="utf-8") as handle:
        handle.write(f"{mode}\n")

    _refresh_claude_md(claude_dir)
    return 0, _color(f"Activated mode: {mode}", GREEN)


def mode_deactivate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    active_path = modes_dir / f"{mode}.md"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = _find_inactive_mode_file(claude_dir, mode)

    if not active_path.is_file():
        return 1, _color(f"Mode '{mode}' is not currently active", RED)

    inactive_dir.mkdir(parents=True, exist_ok=True)
    if inactive_path.exists():
        inactive_path.unlink()
    active_path.replace(inactive_path)

    active_modes = _mode_active_file(claude_dir)
    if active_modes.is_file():
        _update_with_backup(
            active_modes, lambda content: _remove_exact_entries(content, mode)
        )
    else:
        active_modes.touch(exist_ok=True)

    _refresh_claude_md(claude_dir)

    return 0, _color(f"Deactivated mode: {mode}", YELLOW)


def list_modes(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"

    lines: List[str] = [_color("Available modes:", BLUE)]

    for directory in _inactive_dir_candidates(claude_dir, "modes"):
        for path in _iter_md_files(directory):
            lines.append(f"  {path.stem} (inactive)")

    for path in _iter_md_files(modes_dir):
        if _is_disabled(path):
            continue
        lines.append(f"  {_color(f'{path.stem} (active)', GREEN)}")

    return "\n".join(lines)


def mode_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    active_file = claude_dir / ".active-modes"

    lines: List[str] = [_color("Active modes:", BLUE)]
    if active_file.is_file():
        for raw in active_file.read_text(encoding="utf-8").splitlines():
            lines.append(f"  {_color(raw, GREEN)}")
    else:
        lines.append("  None")
    return "\n".join(lines)


def _get_active_modes(claude_dir: Path) -> List[str]:
    """Get list of currently active mode names."""
    active_file = _mode_active_file(claude_dir)
    if not active_file.is_file():
        return []

    return [
        line.strip()
        for line in active_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _get_active_mode_metadata(claude_dir: Path) -> List[ModeMetadata]:
    """Get metadata for all currently active modes."""
    active_names = _get_active_modes(claude_dir)
    modes_dir = claude_dir / "modes"
    metadata_list = []

    for mode_name in active_names:
        mode_path = modes_dir / f"{mode_name}.md"
        if mode_path.is_file():
            metadata = parse_mode_metadata(mode_path)
            if metadata:
                metadata_list.append(metadata)

    return metadata_list


def _get_active_rules(claude_dir: Path) -> List[str]:
    """Get list of currently active rule names."""
    active_file = claude_dir / ".active-rules"
    if not active_file.is_file():
        return []

    return [
        line.strip()
        for line in active_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def mode_activate_intelligent(
    mode: str,
    auto_resolve: bool = True,
    home: Path | None = None
) -> tuple[int, str, List[str]]:
    """
    Activate mode with intelligent conflict resolution.

    Args:
        mode: Mode name to activate
        auto_resolve: If True, auto-deactivate conflicting modes based on priority
        home: Optional home directory path

    Returns:
        (exit_code, message, deactivated_modes)
        - exit_code: 0 on success, 1 on failure
        - message: Status message
        - deactivated_modes: List of modes that were deactivated
    """
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = inactive_dir / f"{mode}.md"
    active_path = modes_dir / f"{mode}.md"

    # Check if mode exists
    if inactive_path is None:
        return 1, _color(f"Mode '{mode}' not found in inactive modes", RED), []

    # Parse metadata for the mode we're activating
    mode_metadata = parse_mode_metadata(inactive_path)
    if not mode_metadata:
        # Fall back to simple activation if we can't parse metadata
        exit_code, msg = mode_activate(mode, home)
        return exit_code, msg, []

    # Get currently active modes and their metadata
    active_mode_metadata = _get_active_mode_metadata(claude_dir)
    active_mode_names = _get_active_modes(claude_dir)
    active_rule_names = _get_active_rules(claude_dir)

    # Check dependencies
    deps_satisfied, missing_deps = check_mode_dependencies(
        mode_metadata, active_mode_names, active_rule_names
    )

    if not deps_satisfied:
        dep_list = ", ".join(missing_deps)
        return (
            1,
            _color(f"Cannot activate '{mode}': missing dependencies: {dep_list}", RED),
            []
        )

    # Check for conflicts
    conflicts = get_mode_conflicts(mode_metadata, active_mode_metadata)
    deactivated = []

    if conflicts:
        if auto_resolve:
            # Auto-deactivate conflicts based on priority or group
            for conflicting_mode in conflicts:
                # Check if it's a group conflict (always auto-deactivate)
                is_group_conflict = (
                    mode_metadata.group
                    and conflicting_mode.group
                    and mode_metadata.group == conflicting_mode.group
                )

                if is_group_conflict:
                    # Group conflicts always auto-deactivate (only one mode per group)
                    exit_code, _ = mode_deactivate(conflicting_mode.name, home)
                    if exit_code == 0:
                        deactivated.append(conflicting_mode.name)
                else:
                    # Priority-based conflict resolution
                    action = get_priority_action(mode_metadata, conflicting_mode)

                    if action == "auto_deactivate":
                        # New mode has higher priority, auto-deactivate conflicting mode
                        exit_code, _ = mode_deactivate(conflicting_mode.name, home)
                        if exit_code == 0:
                            deactivated.append(conflicting_mode.name)
                    else:
                        # Equal or lower priority, return error asking user to resolve
                        conflict_names = ", ".join(c.name for c in conflicts)
                        return (
                            1,
                            _color(
                                f"Cannot activate '{mode}': conflicts with active modes: {conflict_names}. "
                                f"Please deactivate them first or use force mode.",
                                RED
                            ),
                            []
                        )
        else:
            # No auto-resolve, just report conflicts
            conflict_names = ", ".join(c.name for c in conflicts)
            return (
                1,
                _color(
                    f"Cannot activate '{mode}': conflicts with active modes: {conflict_names}",
                    RED
                ),
                []
            )

    # Activate the mode
    modes_dir.mkdir(parents=True, exist_ok=True)
    active_path.parent.mkdir(parents=True, exist_ok=True)

    if active_path.exists():
        active_path.unlink()
    inactive_path.replace(active_path)

    active_modes_file = _mode_active_file(claude_dir)
    with active_modes_file.open("a", encoding="utf-8") as handle:
        handle.write(f"{mode}\n")

    _refresh_claude_md(claude_dir)

    # Build success message
    msg = _color(f"Activated mode: {mode}", GREEN)
    if deactivated:
        deactivated_list = ", ".join(deactivated)
        msg += _color(f"\nAuto-deactivated: {deactivated_list}", YELLOW)

    return 0, msg, deactivated


def mode_deactivate_intelligent(
    mode: str,
    check_dependents: bool = True,
    home: Path | None = None
) -> tuple[int, str, List[str]]:
    """
    Deactivate mode and warn about dependent modes.

    Args:
        mode: Mode name to deactivate
        check_dependents: If True, warn about modes that depend on this one
        home: Optional home directory path

    Returns:
        (exit_code, message, affected_modes)
        - exit_code: 0 on success, 1 on failure
        - message: Status message
        - affected_modes: List of modes that depend on this mode
    """
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    active_path = modes_dir / f"{mode}.md"

    if not active_path.is_file():
        return 1, _color(f"Mode '{mode}' is not currently active", RED), []

    affected_modes = []

    if check_dependents:
        # Check if any active modes depend on this one
        active_mode_metadata = _get_active_mode_metadata(claude_dir)

        for other_mode in active_mode_metadata:
            if mode in other_mode.dependencies:
                affected_modes.append(other_mode.name)

    # Deactivate the mode
    exit_code, msg = mode_deactivate(mode, home)

    # Add warning about dependent modes
    if affected_modes:
        affected_list = ", ".join(affected_modes)
        msg += _color(
            f"\nWarning: These modes depend on '{mode}': {affected_list}",
            YELLOW
        )

    return exit_code, msg, affected_modes
