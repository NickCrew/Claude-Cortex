"""Mode management functions (reference-based activation)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .components import (
    get_all_available_components,
    add_component_to_claude_md,
    ref_activate,
    ref_deactivate,
    ref_list,
    ref_status,
)

COMPONENT_TYPE = "modes"
BASE_PATH = "modes"
SECTION_PATTERN = r'(#\s*Inactive\s+Modes.*?\n)'


def _parse_claude_md_modes(claude_dir: Path) -> Tuple[List[str], List[str]]:
    """Legacy placeholder; returns no CLAUDE.md-derived state."""
    return ([], [])


def _get_all_available_modes(claude_dir: Path) -> List[str]:
    """Get all mode files from the modes directory."""
    return get_all_available_components(claude_dir, COMPONENT_TYPE)


def _toggle_mode_in_claude_md(
    claude_dir: Path,
    mode: str,
    activate: bool
) -> Tuple[bool, str]:
    """Deprecated: comment toggling no longer used."""
    return False, "Comment-based toggling is deprecated"


def mode_activate(mode: str, home: Path | None = None) -> Tuple[int, str]:
    """Activate a mode by adding it to .active-modes."""
    return ref_activate(COMPONENT_TYPE, mode, BASE_PATH, home)


def mode_deactivate(mode: str, home: Path | None = None) -> Tuple[int, str]:
    """Deactivate a mode by removing it from .active-modes."""
    return ref_deactivate(COMPONENT_TYPE, mode, home)


def list_modes(home: Path | None = None) -> str:
    """List all modes with their status."""
    return ref_list(COMPONENT_TYPE, BASE_PATH, home)


def mode_status(home: Path | None = None) -> str:
    """Show currently active modes."""
    return ref_status(COMPONENT_TYPE, home)


def mode_add_to_claude_md(
    mode: str,
    active: bool = False,
    home: Path | None = None
) -> Tuple[int, str]:
    """Add a mode reference to CLAUDE.md if not already present."""
    return add_component_to_claude_md(COMPONENT_TYPE, mode, SECTION_PATTERN, active, home)


# Helper functions for backward compatibility
def _get_active_modes(claude_dir: Path) -> List[str]:
    """Get list of currently active mode names."""
    active_modes, _ = _parse_claude_md_modes(claude_dir)
    return active_modes


def _mode_active_file(claude_dir: Path) -> Path:
    """Legacy: Return path to .active-modes file (for backward compatibility)."""
    return claude_dir / ".active-modes"


def _mode_inactive_dir(claude_dir: Path) -> Path:
    """Legacy: Return path to inactive modes dir (for backward compatibility)."""
    return claude_dir / "inactive" / "modes"


def mode_activate_intelligent(
    mode: str,
    auto_resolve: bool = True,
    home: Path | None = None
) -> Tuple[int, str, List[str]]:
    """Activate mode with intelligent conflict resolution.

    This is a simplified version that uses HTML comment toggling.
    Conflict resolution is not yet implemented for the HTML comment approach.
    """
    exit_code, message = mode_activate(mode, home)
    return exit_code, message, []


def mode_deactivate_intelligent(
    mode: str,
    check_dependents: bool = True,
    home: Path | None = None
) -> Tuple[int, str, List[str]]:
    """Deactivate mode and warn about dependent modes.

    This is a simplified version that uses HTML comment toggling.
    Dependency checking is not yet implemented for the HTML comment approach.
    """
    exit_code, message = mode_deactivate(mode, home)
    return exit_code, message, []
