"""Generic component toggle system for modes, rules, and other CLAUDE.md references.

Components are toggled via HTML comments in CLAUDE.md:
- Active:   @{type}/{Name}.md
- Inactive: <!-- @{type}/{Name}.md -->
"""

from __future__ import annotations

import re
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
    _update_with_backup,
)


def parse_claude_md_components(
    claude_dir: Path,
    component_type: str
) -> Tuple[List[str], List[str]]:
    """Parse CLAUDE.md to find active and inactive components.

    Args:
        claude_dir: Path to Claude directory
        component_type: Type of component (e.g., "modes", "rules")

    Returns:
        Tuple of (active_components, inactive_components) as lists of names
    """
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.is_file():
        return [], []

    content = claude_md.read_text(encoding="utf-8")

    # Active: @{type}/{Name}.md
    active_pattern = re.compile(
        rf'^@{re.escape(component_type)}/([^/]+)\.md\s*$',
        re.MULTILINE
    )
    # Inactive: <!-- @{type}/{Name}.md -->
    inactive_pattern = re.compile(
        rf'^<!--\s*@{re.escape(component_type)}/([^/]+)\.md\s*-->\s*$',
        re.MULTILINE
    )

    active = active_pattern.findall(content)
    inactive = inactive_pattern.findall(content)

    return active, inactive


def get_all_available_components(claude_dir: Path, component_type: str) -> List[str]:
    """Get all component files from the component directory.

    Args:
        claude_dir: Path to Claude directory
        component_type: Type of component (e.g., "modes", "rules")

    Returns:
        Sorted list of component names (without .md extension)
    """
    component_dir = claude_dir / component_type
    if not component_dir.is_dir():
        return []

    components = []
    for path in _iter_md_files(component_dir):
        # Skip subdirectories
        if path.parent == component_dir:
            components.append(path.stem)
    return sorted(components)


def toggle_component_in_claude_md(
    claude_dir: Path,
    component_type: str,
    name: str,
    activate: bool
) -> Tuple[bool, str]:
    """Toggle a component in CLAUDE.md by adding/removing HTML comments.

    Args:
        claude_dir: Path to Claude directory
        component_type: Type of component (e.g., "modes", "rules")
        name: Component name (without .md extension)
        activate: True to activate (remove comment), False to deactivate (add comment)

    Returns:
        Tuple of (success, error_message)
    """
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.is_file():
        return False, f"CLAUDE.md not found at {claude_md}"

    content = claude_md.read_text(encoding="utf-8")
    original_content = content

    type_singular = component_type.rstrip('s')  # "modes" -> "mode"

    if activate:
        # Remove HTML comment: <!-- @type/Name.md --> → @type/Name.md
        pattern = re.compile(
            rf'^<!--\s*@{re.escape(component_type)}/{re.escape(name)}\.md\s*-->[ \t]*$',
            re.MULTILINE
        )
        replacement = f'@{component_type}/{name}.md'

        if not pattern.search(content):
            # Check if already active
            active_pattern = re.compile(
                rf'^@{re.escape(component_type)}/{re.escape(name)}\.md\s*$',
                re.MULTILINE
            )
            if active_pattern.search(content):
                return False, f"{type_singular.capitalize()} '{name}' is already active"
            return False, f"{type_singular.capitalize()} '{name}' not found in CLAUDE.md (inactive section)"

        content = pattern.sub(replacement, content)
    else:
        # Add HTML comment: @type/Name.md → <!-- @type/Name.md -->
        pattern = re.compile(
            rf'^@{re.escape(component_type)}/{re.escape(name)}\.md\s*$',
            re.MULTILINE
        )
        replacement = f'<!-- @{component_type}/{name}.md -->'

        if not pattern.search(content):
            # Check if already inactive
            inactive_pattern = re.compile(
                rf'^<!--\s*@{re.escape(component_type)}/{re.escape(name)}\.md\s*-->',
                re.MULTILINE
            )
            if inactive_pattern.search(content):
                return False, f"{type_singular.capitalize()} '{name}' is already inactive"
            return False, f"{type_singular.capitalize()} '{name}' not found in CLAUDE.md (active section)"

        content = pattern.sub(replacement, content)

    if content != original_content:
        _update_with_backup(claude_md, lambda _: content)
        return True, ""

    return False, "No changes made"


def component_activate(
    component_type: str,
    name: str,
    home: Path | None = None
) -> Tuple[int, str]:
    """Activate a component by removing HTML comment in CLAUDE.md.

    Args:
        component_type: Type of component (e.g., "modes", "rules")
        name: Component name (without .md extension)
        home: Optional home directory override

    Returns:
        Tuple of (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    type_singular = component_type.rstrip('s')

    # Verify component file exists
    component_path = claude_dir / component_type / f"{name}.md"
    if not component_path.is_file():
        return 1, _color(f"{type_singular.capitalize()} file not found: {component_type}/{name}.md", RED)

    success, error = toggle_component_in_claude_md(claude_dir, component_type, name, activate=True)

    if success:
        return 0, _color(f"Activated {type_singular}: {name}", GREEN)
    else:
        return 1, _color(error, RED)


def component_deactivate(
    component_type: str,
    name: str,
    home: Path | None = None
) -> Tuple[int, str]:
    """Deactivate a component by adding HTML comment in CLAUDE.md.

    Args:
        component_type: Type of component (e.g., "modes", "rules")
        name: Component name (without .md extension)
        home: Optional home directory override

    Returns:
        Tuple of (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    type_singular = component_type.rstrip('s')

    success, error = toggle_component_in_claude_md(claude_dir, component_type, name, activate=False)

    if success:
        return 0, _color(f"Deactivated {type_singular}: {name}", YELLOW)
    else:
        return 1, _color(error, RED)


def list_components(
    component_type: str,
    home: Path | None = None
) -> str:
    """List all components with their status from CLAUDE.md and directory.

    Args:
        component_type: Type of component (e.g., "modes", "rules")
        home: Optional home directory override

    Returns:
        Formatted string listing all components
    """
    claude_dir = _resolve_claude_dir(home)

    # Parse CLAUDE.md for current state
    active, inactive = parse_claude_md_components(claude_dir, component_type)

    # Get all available component files
    available = get_all_available_components(claude_dir, component_type)

    # Build output
    lines: List[str] = [_color(f"Available {component_type}:", BLUE)]

    # Track which we've listed
    listed = set()

    # Active (from CLAUDE.md)
    for name in sorted(active):
        lines.append(f"  {_color(f'{name} (active)', GREEN)}")
        listed.add(name)

    # Inactive (from CLAUDE.md)
    for name in sorted(inactive):
        lines.append(f"  {name} (inactive)")
        listed.add(name)

    # In directory but not in CLAUDE.md
    for name in available:
        if name not in listed:
            lines.append(f"  {_color(f'{name} (not in CLAUDE.md)', YELLOW)}")

    if len(lines) == 1:
        lines.append(f"  No {component_type} found")

    return "\n".join(lines)


def component_status(
    component_type: str,
    home: Path | None = None
) -> str:
    """Show currently active components from CLAUDE.md.

    Args:
        component_type: Type of component (e.g., "modes", "rules")
        home: Optional home directory override

    Returns:
        Formatted string listing active components
    """
    claude_dir = _resolve_claude_dir(home)

    active, _ = parse_claude_md_components(claude_dir, component_type)

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
    home: Path | None = None
) -> Tuple[int, str]:
    """Add a component reference to CLAUDE.md if not already present.

    Args:
        component_type: Type of component (e.g., "modes", "rules")
        name: Component name (without .md extension)
        section_pattern: Regex pattern to find the section header
        active: If True, add as active; if False, add as inactive (commented)
        home: Optional home directory override

    Returns:
        Tuple of (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    claude_md = claude_dir / "CLAUDE.md"
    type_singular = component_type.rstrip('s')

    # Verify component file exists
    component_path = claude_dir / component_type / f"{name}.md"
    if not component_path.is_file():
        return 1, _color(f"{type_singular.capitalize()} file not found: {component_type}/{name}.md", RED)

    if not claude_md.is_file():
        return 1, _color(f"CLAUDE.md not found at {claude_md}", RED)

    content = claude_md.read_text(encoding="utf-8")

    # Check if already present
    active_list, inactive_list = parse_claude_md_components(claude_dir, component_type)
    if name in active_list or name in inactive_list:
        status = "active" if name in active_list else "inactive"
        return 1, _color(f"{type_singular.capitalize()} '{name}' already in CLAUDE.md ({status})", YELLOW)

    # Find the section to add the new component
    pattern = re.compile(section_pattern, re.IGNORECASE)

    match = pattern.search(content)
    if match:
        insert_pos = match.end()
        if active:
            new_line = f"@{component_type}/{name}.md\n"
        else:
            new_line = f"<!-- @{component_type}/{name}.md -->\n"

        new_content = content[:insert_pos] + new_line + content[insert_pos:]
        _update_with_backup(claude_md, lambda _: new_content)

        status = "active" if active else "inactive"
        return 0, _color(f"Added {type_singular} '{name}' to CLAUDE.md ({status})", GREEN)

    return 1, _color(f"Could not find section matching '{section_pattern}' in CLAUDE.md", RED)
