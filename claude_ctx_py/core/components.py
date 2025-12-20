"""Component management for rules, modes, and similar assets.

Activation is file-based:
- Active components live in ``{claude_dir}/{type}/`` (e.g., ``rules/`` or ``modes/``).
- Inactive components are parked in ``{claude_dir}/inactive/{type}/`` (legacy aliases respected).

HTML comment toggling in ``CLAUDE.md`` is deprecated; helpers remain only for migration.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    _color,
    _iter_md_files,
    _resolve_claude_dir,
    _inactive_category_dir,
    _inactive_dir_candidates,
    _write_active_entries,
    _parse_active_entries,
    _refresh_claude_md,
)


# ---------------------------------------------------------------------------
# Legacy parser (kept for migration tooling)
# ---------------------------------------------------------------------------

def parse_claude_md_components(
    claude_dir: Path,
    component_type: str,
) -> Tuple[List[str], List[str]]:
    """Legacy parser that extracted comment-based state from CLAUDE.md.

    New flow ignores CLAUDE.md comments; return empty lists to signal no state.
    """
    return [], []


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def get_all_available_components(claude_dir: Path, component_type: str) -> List[str]:
    """Get all component files from the active directory (no subdirs)."""
    component_dir = claude_dir / component_type
    if not component_dir.is_dir():
        return []

    components = []
    for path in _iter_md_files(component_dir):
        if path.parent == component_dir:
            components.append(path.stem)
    return sorted(components)


def _active_file(claude_dir: Path, component_type: str) -> Path:
    """Path to the ``.active-<type>`` tracking file."""
    return claude_dir / f".active-{component_type}"


def _active_set(claude_dir: Path, component_type: str) -> List[str]:
    """Read the active set from disk."""
    return _parse_active_entries(_active_file(claude_dir, component_type))


def _record_active(claude_dir: Path, component_type: str, entries: List[str]) -> None:
    """Persist active set."""
    _write_active_entries(_active_file(claude_dir, component_type), entries)


def _component_paths(
    claude_dir: Path,
    component_type: str,
    name: str,
) -> Tuple[Path, Path]:
    active_dir = claude_dir / component_type
    inactive_dir = _inactive_category_dir(claude_dir, component_type)
    return active_dir / f"{name}.md", inactive_dir / f"{name}.md"


def _activate_component(
    claude_dir: Path,
    component_type: str,
    name: str,
) -> Tuple[int, str]:
    """Move component into active directory."""
    type_singular = component_type.rstrip("s")
    active_path, inactive_path = _component_paths(claude_dir, component_type, name)

    # Already active
    if active_path.exists():
        return 1, _color(f"{type_singular.capitalize()} '{name}' is already active", YELLOW)

    # Promote from inactive
    if inactive_path.exists():
        active_path.parent.mkdir(parents=True, exist_ok=True)
        inactive_path.rename(active_path)
        return 0, _color(f"Activated {type_singular}: {name}", GREEN)

    return 1, _color(f"{type_singular.capitalize()} '{name}' not found (install first)", RED)


def _deactivate_component(
    claude_dir: Path,
    component_type: str,
    name: str,
) -> Tuple[int, str]:
    """Move component into inactive directory."""
    type_singular = component_type.rstrip("s")
    active_path, inactive_path = _component_paths(claude_dir, component_type, name)

    if not active_path.exists():
        if inactive_path.exists():
            return 1, _color(f"{type_singular.capitalize()} '{name}' is already inactive", YELLOW)
        return 1, _color(f"{type_singular.capitalize()} '{name}' not found", RED)

    inactive_path.parent.mkdir(parents=True, exist_ok=True)
    active_path.rename(inactive_path)
    return 0, _color(f"Deactivated {type_singular}: {name}", YELLOW)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def component_activate(
    component_type: str,
    name: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Activate a component by moving it into the active directory."""
    claude_dir = _resolve_claude_dir(home)
    exit_code, message = _activate_component(claude_dir, component_type, name)

    if exit_code == 0:
        active = _active_set(claude_dir, component_type)
        if name not in active:
            active.append(name)
            _record_active(claude_dir, component_type, active)
        _refresh_claude_md(claude_dir)

    return exit_code, message


def component_deactivate(
    component_type: str,
    name: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Deactivate a component by moving it into the inactive directory."""
    claude_dir = _resolve_claude_dir(home)
    exit_code, message = _deactivate_component(claude_dir, component_type, name)

    if exit_code == 0:
        active = _active_set(claude_dir, component_type)
        if name in active:
            active = [a for a in active if a != name]
            _record_active(claude_dir, component_type, active)
        _refresh_claude_md(claude_dir)

    return exit_code, message


def list_components(
    component_type: str,
    home: Path | None = None,
) -> str:
    """List all components with their status from filesystem state."""
    claude_dir = _resolve_claude_dir(home)

    active_dir = claude_dir / component_type
    inactive_dir = _inactive_category_dir(claude_dir, component_type)
    active = [p.stem for p in _iter_md_files(active_dir)]
    inactive: List[str] = []
    for candidate in _inactive_dir_candidates(claude_dir, component_type):
        inactive.extend(p.stem for p in _iter_md_files(candidate))

    lines: List[str] = [_color(f"Available {component_type}:", BLUE)]

    for name in sorted(set(active)):
        lines.append(f"  {_color(f'{name} (active)', GREEN)}")

    for name in sorted(set(inactive) - set(active)):
        lines.append(f"  {name} (inactive)")

    if len(lines) == 1:
        lines.append(f"  No {component_type} found")

    return "\n".join(lines)


def component_status(
    component_type: str,
    home: Path | None = None,
) -> str:
    """Show currently active components from filesystem state."""
    claude_dir = _resolve_claude_dir(home)

    active_dir = claude_dir / component_type
    active = [p.stem for p in _iter_md_files(active_dir)]

    lines: List[str] = [_color(f"Active {component_type}:", BLUE)]

    if active:
        for name in sorted(active):
            lines.append(f"  {_color(name, GREEN)}")
    else:
        lines.append("  None")

    return "\n".join(lines)


def add_component_to_claude_md(
    component_type: str,
    name: str,
    section_pattern: str,
    active: bool = False,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Deprecated: formerly added commented references to CLAUDE.md.

    Kept for CLI compatibility; now simply verifies presence on disk.
    """
    claude_dir = _resolve_claude_dir(home)
    component_path = claude_dir / component_type / f"{name}.md"
    if not component_path.is_file():
        type_singular = component_type.rstrip("s")
        return 1, _color(f"{type_singular.capitalize()} file not found: {component_type}/{name}.md", RED)
    return 0, _color(f"{component_type.rstrip('s').capitalize()} '{name}' available on disk (CLAUDE.md reference not required)", GREEN)


# ---------------------------------------------------------------------------
# Reference-based activation (files stay in place, only .active-* changes)
# ---------------------------------------------------------------------------

def ref_activate(
    component_type: str,
    name: str,
    base_path: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Activate a component by adding it to .active-{type} file.

    For components like modes and MCP docs where files don't move.
    """
    claude_dir = _resolve_claude_dir(home)
    type_singular = component_type.rstrip("s")

    # Check if the file exists
    component_path = claude_dir / base_path / f"{name}.md"
    if not component_path.is_file():
        return 1, _color(f"{type_singular.capitalize()} '{name}' not found at {base_path}/{name}.md", RED)

    active = _active_set(claude_dir, component_type)
    if name in active:
        return 1, _color(f"{type_singular.capitalize()} '{name}' is already active", YELLOW)

    active.append(name)
    _record_active(claude_dir, component_type, active)
    _refresh_claude_md(claude_dir)

    return 0, _color(f"Activated {type_singular}: {name}", GREEN)


def ref_deactivate(
    component_type: str,
    name: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Deactivate a component by removing it from .active-{type} file.

    For components like modes and MCP docs where files don't move.
    """
    claude_dir = _resolve_claude_dir(home)
    type_singular = component_type.rstrip("s")

    active = _active_set(claude_dir, component_type)
    if name not in active:
        return 1, _color(f"{type_singular.capitalize()} '{name}' is not active", YELLOW)

    active = [a for a in active if a != name]
    _record_active(claude_dir, component_type, active)
    _refresh_claude_md(claude_dir)

    return 0, _color(f"Deactivated {type_singular}: {name}", YELLOW)


def ref_list(
    component_type: str,
    base_path: str,
    home: Path | None = None,
) -> str:
    """List all reference-based components with their status."""
    claude_dir = _resolve_claude_dir(home)

    # All available files
    component_dir = claude_dir / base_path
    all_components = sorted(p.stem for p in _iter_md_files(component_dir)) if component_dir.is_dir() else []

    # Active ones from .active-* file
    active = set(_active_set(claude_dir, component_type))

    lines: List[str] = [_color(f"Available {component_type}:", BLUE)]

    for name in all_components:
        if name in active:
            lines.append(f"  {_color(f'{name} (active)', GREEN)}")
        else:
            lines.append(f"  {name} (inactive)")

    if len(lines) == 1:
        lines.append(f"  No {component_type} found")

    return "\n".join(lines)


def ref_status(
    component_type: str,
    home: Path | None = None,
) -> str:
    """Show currently active reference-based components."""
    claude_dir = _resolve_claude_dir(home)

    active = _active_set(claude_dir, component_type)
    type_singular = component_type.rstrip("s")

    lines: List[str] = [_color(f"Active {component_type}:", BLUE)]

    if active:
        for name in sorted(active):
            lines.append(f"  {_color(name, GREEN)}")
    else:
        lines.append("  None")

    return "\n".join(lines)
