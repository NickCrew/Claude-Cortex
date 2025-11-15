"""Mode metadata parsing and intelligent switching logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


@dataclass
class ModeMetadata:
    """Metadata for a mode with conflict and dependency information."""

    name: str
    category: str = "general"
    priority: str = "medium"  # low, medium, high
    conflicts: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    overrides: Dict[str, Any] = field(default_factory=dict)
    group: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    auto_activate_triggers: List[str] = field(default_factory=list)

    @property
    def priority_value(self) -> int:
        """Convert priority string to numeric value for comparison."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority.lower(), 2)


def parse_yaml_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Tuple of (metadata_dict, remaining_content)
    """
    if not content.strip().startswith("---"):
        return None, content

    # Find the closing ---
    lines = content.split("\n")
    if len(lines) < 3:
        return None, content

    # Find end of frontmatter
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, content

    # Extract YAML content
    yaml_content = "\n".join(lines[1:end_idx])
    remaining_content = "\n".join(lines[end_idx + 1 :])

    if yaml is None:
        # Can't parse YAML without library
        return None, content  # type: ignore[unreachable]

    try:
        metadata = yaml.safe_load(yaml_content)
        if isinstance(metadata, dict):
            return metadata, remaining_content
        return None, content
    except yaml.YAMLError:
        return None, content


def parse_mode_metadata(mode_path: Path) -> Optional[ModeMetadata]:
    """
    Parse mode metadata from YAML frontmatter.

    Args:
        mode_path: Path to mode markdown file

    Returns:
        ModeMetadata object or None if parsing fails
    """
    if not mode_path.is_file():
        return None

    try:
        content = mode_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    metadata_dict, _ = parse_yaml_frontmatter(content)

    if metadata_dict is None:
        # No frontmatter, create default metadata
        return ModeMetadata(name=mode_path.stem)

    # Extract fields with defaults
    return ModeMetadata(
        name=metadata_dict.get("name", mode_path.stem),
        category=metadata_dict.get("category", "general"),
        priority=metadata_dict.get("priority", "medium"),
        conflicts=metadata_dict.get("conflicts", []),
        dependencies=metadata_dict.get("dependencies", []),
        overrides=metadata_dict.get("overrides", {}),
        group=metadata_dict.get("group"),
        tags=metadata_dict.get("tags", []),
        auto_activate_triggers=metadata_dict.get("auto_activate_triggers", []),
    )


def get_mode_conflicts(
    mode_metadata: ModeMetadata, active_modes: List[ModeMetadata]
) -> List[ModeMetadata]:
    """
    Get list of active modes that conflict with given mode.

    Args:
        mode_metadata: Metadata for mode to check
        active_modes: List of currently active mode metadata

    Returns:
        List of conflicting active modes
    """
    conflicts = []

    for active in active_modes:
        # Direct conflict declaration
        if active.name in mode_metadata.conflicts:
            conflicts.append(active)
            continue

        # Group conflict (only one mode per group)
        if (
            mode_metadata.group
            and active.group
            and mode_metadata.group == active.group
            and active.name != mode_metadata.name
        ):
            conflicts.append(active)

    return conflicts


def check_mode_dependencies(
    mode_metadata: ModeMetadata, active_modes: List[str], active_rules: List[str]
) -> Tuple[bool, List[str]]:
    """
    Check if mode dependencies are satisfied.

    Args:
        mode_metadata: Metadata for mode to check
        active_modes: List of currently active mode names
        active_rules: List of currently active rule names

    Returns:
        Tuple of (all_satisfied, missing_dependencies)
    """
    missing = []

    for dep in mode_metadata.dependencies:
        # Check if it's a rule dependency (ends with -rules or starts with rule:)
        is_rule = dep.endswith("-rules") or dep.endswith(".md") or dep.startswith("rule:")
        dep_name = dep.replace("rule:", "").replace(".md", "")

        if is_rule:
            # Rule dependency
            if dep_name not in active_rules:
                missing.append(f"rule:{dep_name}")
        else:
            # Mode dependency
            if dep_name not in active_modes:
                missing.append(f"mode:{dep_name}")

    return len(missing) == 0, missing


def get_priority_action(
    new_mode: ModeMetadata, conflicting_mode: ModeMetadata
) -> str:
    """
    Determine action based on priority comparison.

    Args:
        new_mode: Metadata for mode being activated
        conflicting_mode: Metadata for conflicting active mode

    Returns:
        "auto_deactivate" if new mode has higher priority
        "prompt" if equal or lower priority
    """
    if new_mode.priority_value > conflicting_mode.priority_value:
        return "auto_deactivate"
    else:
        return "prompt"


def format_metadata_summary(metadata: ModeMetadata) -> str:
    """
    Format mode metadata as readable summary.

    Args:
        metadata: Mode metadata to format

    Returns:
        Formatted string summary
    """
    lines = []
    lines.append(f"Category: {metadata.category}")
    lines.append(f"Priority: {metadata.priority}")

    if metadata.group:
        lines.append(f"Group: {metadata.group}")

    if metadata.conflicts:
        lines.append(f"Conflicts: {', '.join(metadata.conflicts)}")

    if metadata.dependencies:
        lines.append(f"Dependencies: {', '.join(metadata.dependencies)}")

    if metadata.overrides:
        overrides_str = ", ".join(f"{k}={v}" for k, v in metadata.overrides.items())
        lines.append(f"Overrides: {overrides_str}")

    if metadata.tags:
        lines.append(f"Tags: {', '.join(metadata.tags)}")

    return "\n".join(lines)
