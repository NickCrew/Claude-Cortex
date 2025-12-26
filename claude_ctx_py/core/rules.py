"""Rule management functions (file-based activation)."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .components import (
    component_activate,
    component_deactivate,
    list_components,
    component_status,
    add_component_to_claude_md,
    get_all_available_components,
)

COMPONENT_TYPE = "rules"


def _get_all_available_rules(claude_dir: Path) -> List[str]:
    """Get all rule files from the rules directory."""
    return get_all_available_components(claude_dir, COMPONENT_TYPE)


def rules_activate(rule: str, home: Path | None = None) -> str:
    """Activate a rule by moving it into the active rules directory."""
    exit_code, message = component_activate(COMPONENT_TYPE, rule, home)
    return message


def rules_deactivate(rule: str, home: Path | None = None) -> str:
    """Deactivate a rule by moving it into the inactive rules directory."""
    exit_code, message = component_deactivate(COMPONENT_TYPE, rule, home)
    return message


def list_rules(home: Path | None = None) -> str:
    """List all rules with their status from filesystem state."""
    return list_components(COMPONENT_TYPE, home)


def rules_status(home: Path | None = None) -> str:
    """Show currently active rules from filesystem state."""
    return component_status(COMPONENT_TYPE, home)


def rule_add_to_claude_md(
    rule: str,
    active: bool = False,
    home: Path | None = None
) -> Tuple[int, str]:
    """Legacy helper; validates rule exists on disk."""
    return add_component_to_claude_md(COMPONENT_TYPE, rule, "", active, home)
