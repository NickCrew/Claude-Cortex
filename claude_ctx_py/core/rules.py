"""Rule management functions.

Rules are toggled via HTML comments in CLAUDE.md:
- Active:   @rules/RuleName.md
- Inactive: <!-- @rules/RuleName.md -->
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
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    _color,
    _resolve_claude_dir,
)

COMPONENT_TYPE = "rules"
SECTION_PATTERN = r'(#\s*Optional\s+Rules.*?\n)'


def _parse_claude_md_rules(claude_dir: Path) -> Tuple[List[str], List[str]]:
    """Parse CLAUDE.md to find active and inactive rules."""
    return parse_claude_md_components(claude_dir, COMPONENT_TYPE)


def _get_all_available_rules(claude_dir: Path) -> List[str]:
    """Get all rule files from the rules directory."""
    return get_all_available_components(claude_dir, COMPONENT_TYPE)


def _toggle_rule_in_claude_md(
    claude_dir: Path,
    rule: str,
    activate: bool
) -> Tuple[bool, str]:
    """Toggle a rule in CLAUDE.md by adding/removing HTML comments."""
    return toggle_component_in_claude_md(claude_dir, COMPONENT_TYPE, rule, activate)


def rules_activate(rule: str, home: Path | None = None) -> str:
    """Activate a rule by removing HTML comment in CLAUDE.md."""
    exit_code, message = component_activate(COMPONENT_TYPE, rule, home)
    return message


def rules_deactivate(rule: str, home: Path | None = None) -> str:
    """Deactivate a rule by adding HTML comment in CLAUDE.md."""
    exit_code, message = component_deactivate(COMPONENT_TYPE, rule, home)
    return message


def list_rules(home: Path | None = None) -> str:
    """List all rules with their status from CLAUDE.md and rules directory."""
    return list_components(COMPONENT_TYPE, home)


def rules_status(home: Path | None = None) -> str:
    """Show currently active rules from CLAUDE.md."""
    return component_status(COMPONENT_TYPE, home)


def rule_add_to_claude_md(
    rule: str,
    active: bool = False,
    home: Path | None = None
) -> Tuple[int, str]:
    """Add a rule reference to CLAUDE.md if not already present."""
    return add_component_to_claude_md(COMPONENT_TYPE, rule, SECTION_PATTERN, active, home)
