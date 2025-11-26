"""Mode management functions.

Modes are toggled via HTML comments in CLAUDE.md:
- Active:   @modes/ModeName.md
- Inactive: <!-- @modes/ModeName.md -->
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .components import (
    parse_claude_md_components,
    get_all_available_components,
    toggle_component_in_claude_md,
    component_activate,
    component_deactivate,
    list_components,
    component_status,
    add_component_to_claude_md,
)
from .base import _resolve_claude_dir

COMPONENT_TYPE = "modes"
SECTION_PATTERN = r'(#\s*Inactive\s+Modes.*?\n)'


def _parse_claude_md_modes(claude_dir: Path) -> Tuple[List[str], List[str]]:
    """Parse CLAUDE.md to find active and inactive modes."""
    return parse_claude_md_components(claude_dir, COMPONENT_TYPE)


def _get_all_available_modes(claude_dir: Path) -> List[str]:
    """Get all mode files from the modes directory."""
    return get_all_available_components(claude_dir, COMPONENT_TYPE)


def _toggle_mode_in_claude_md(
    claude_dir: Path,
    mode: str,
    activate: bool
) -> Tuple[bool, str]:
    """Toggle a mode in CLAUDE.md by adding/removing HTML comments."""
    return toggle_component_in_claude_md(claude_dir, COMPONENT_TYPE, mode, activate)


def mode_activate(mode: str, home: Path | None = None) -> Tuple[int, str]:
    """Activate a mode by removing HTML comment in CLAUDE.md."""
    return component_activate(COMPONENT_TYPE, mode, home)


def mode_deactivate(mode: str, home: Path | None = None) -> Tuple[int, str]:
    """Deactivate a mode by adding HTML comment in CLAUDE.md."""
    return component_deactivate(COMPONENT_TYPE, mode, home)


def list_modes(home: Path | None = None) -> str:
    """List all modes with their status from CLAUDE.md and modes directory."""
    return list_components(COMPONENT_TYPE, home)


def mode_status(home: Path | None = None) -> str:
    """Show currently active modes from CLAUDE.md."""
    return component_status(COMPONENT_TYPE, home)


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
