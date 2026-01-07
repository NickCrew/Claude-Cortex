"""Skill composition and dependency resolution.

This module provides functionality for managing skill dependencies, including:
- Loading skill composition maps from YAML
- Resolving transitive dependencies
- Detecting circular dependencies
- Generating dependency trees for display
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:  # pragma: no cover - dependency availability exercised in tests
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

from .exceptions import (
    CircularDependencyError,
    InvalidCompositionError,
    MissingPackageError,
)
from .error_utils import safe_load_yaml


def load_composition_map(claude_dir: Path) -> Dict[str, List[str]]:
    """Load skill composition map from YAML file.

    Args:
        claude_dir: Path to cortex directory

    Returns:
        Dictionary mapping skill names to their dependencies

    Raises:
        MissingPackageError: If PyYAML is not installed
        YAMLValidationError: If YAML syntax is invalid
        InvalidCompositionError: If composition structure is invalid
    """
    composition_file = claude_dir / "skills" / "composition.yaml"

    if not composition_file.exists():
        return {}

    if yaml is None:
        raise MissingPackageError("pyyaml", purpose="skill composition")

    # Use safe_load_yaml which handles errors properly
    data = safe_load_yaml(composition_file)

    if not data:
        return {}

    if not isinstance(data, dict):
        raise InvalidCompositionError(
            "composition.yaml must contain a dictionary at root level"
        )

    # Validate structure
    composition_map: Dict[str, List[str]] = {}
    for skill, deps in data.items():
        # Skip non-string keys
        if not isinstance(skill, str):
            continue  # type: ignore[unreachable]

        if deps is None:
            composition_map[skill] = []
        elif isinstance(deps, list):
            composition_map[skill] = [str(d) for d in deps if isinstance(d, str)]
        else:
            raise InvalidCompositionError(
                f"Dependencies for '{skill}' must be a list, got {type(deps).__name__}"
            )

    return composition_map


def _detect_cycle(
    skill: str,
    composition_map: Dict[str, List[str]],
    visited: Set[str],
    rec_stack: Set[str],
) -> Tuple[bool, List[str]]:
    """Detect circular dependencies using DFS.

    Args:
        skill: Current skill being checked
        composition_map: Full composition map
        visited: Set of visited skills
        rec_stack: Current recursion stack for cycle detection

    Returns:
        Tuple of (has_cycle, cycle_path)
    """
    visited.add(skill)
    rec_stack.add(skill)

    for dep in composition_map.get(skill, []):
        if dep not in visited:
            has_cycle, path = _detect_cycle(dep, composition_map, visited, rec_stack)
            if has_cycle:
                return True, [skill] + path
        elif dep in rec_stack:
            # Found a cycle
            return True, [skill, dep]

    rec_stack.remove(skill)
    return False, []


def validate_no_cycles(composition_map: Dict[str, List[str]]) -> Tuple[bool, str]:
    """Check for circular dependencies in the composition map.

    Args:
        composition_map: Skill dependency map

    Returns:
        Tuple of (is_valid, error_message)
        is_valid is True if no cycles found, False otherwise

    Raises:
        CircularDependencyError: If a circular dependency is detected
            (only when used in strict mode, returns tuple otherwise)
    """
    visited: Set[str] = set()

    for skill in composition_map.keys():
        if skill not in visited:
            rec_stack: Set[str] = set()
            has_cycle, cycle_path = _detect_cycle(
                skill, composition_map, visited, rec_stack
            )
            if has_cycle:
                cycle_str = " → ".join(cycle_path)
                return False, f"Circular dependency detected: {cycle_str}"

    return True, ""


def get_dependencies(
    skill_name: str,
    composition_map: Dict[str, List[str]],
    visited: Set[str] | None = None,
    _root: str | None = None,
) -> List[str]:
    """Get all transitive dependencies for a skill.

    Args:
        skill_name: Name of the skill
        composition_map: Skill dependency map
        visited: Set of already visited skills (for cycle prevention)
        _root: Internal parameter to track the root skill

    Returns:
        List of skill names that are dependencies (in load order)

    Note:
        This uses topological ordering to ensure dependencies are loaded
        before the skills that depend on them.
    """
    if visited is None:
        visited = set()

    if _root is None:
        _root = skill_name

    if skill_name in visited:
        return []

    visited.add(skill_name)

    dependencies: List[str] = []
    direct_deps = composition_map.get(skill_name, [])

    # Recursively resolve dependencies (depth-first)
    for dep in direct_deps:
        # Add transitive dependencies first
        transitive = get_dependencies(dep, composition_map, visited, _root)
        for trans_dep in transitive:
            if trans_dep not in dependencies:
                dependencies.append(trans_dep)

        # Then add the direct dependency (skip if it's the root to prevent self-dependency)
        if dep not in dependencies and dep != _root:
            dependencies.append(dep)

    return dependencies


def get_dependency_tree(
    skill_name: str,
    composition_map: Dict[str, List[str]],
    level: int = 0,
    visited: Set[str] | None = None,
) -> Dict[str, Any]:
    """Get dependency tree structure for display.

    Args:
        skill_name: Name of the skill
        composition_map: Skill dependency map
        level: Current nesting level
        visited: Set of visited skills (for cycle detection)

    Returns:
        Dictionary representing the dependency tree with structure:
        {
            "name": skill_name,
            "dependencies": [dependency_trees...],
            "level": nesting_level
        }
    """
    if visited is None:
        visited = set()

    tree: Dict[str, Any] = {
        "name": skill_name,
        "level": level,
        "dependencies": [],
        "circular": skill_name in visited,
    }

    if skill_name in visited:
        return tree

    visited_copy = visited.copy()
    visited_copy.add(skill_name)

    direct_deps = composition_map.get(skill_name, [])
    for dep in direct_deps:
        dep_tree = get_dependency_tree(dep, composition_map, level + 1, visited_copy)
        tree["dependencies"].append(dep_tree)

    return tree


def format_dependency_tree(
    tree: Dict[str, Any],
    prefix: str = "",
    is_last: bool = True,
) -> str:
    """Format dependency tree as ASCII art for CLI display.

    Args:
        tree: Dependency tree from get_dependency_tree
        prefix: Current line prefix (for nested items)
        is_last: Whether this is the last item in its level

    Returns:
        Formatted tree string
    """
    lines = []

    # Current item
    connector = "└── " if is_last else "├── "
    circular = " (circular)" if tree.get("circular", False) else ""
    lines.append(f"{prefix}{connector}{tree['name']}{circular}")

    # Prepare prefix for children
    extension = "    " if is_last else "│   "
    new_prefix = prefix + extension

    # Process dependencies
    deps = tree.get("dependencies", [])
    for i, dep in enumerate(deps):
        is_last_dep = i == len(deps) - 1
        lines.append(format_dependency_tree(dep, new_prefix, is_last_dep))

    return "\n".join(lines)


def get_all_skills_with_dependencies(
    composition_map: Dict[str, List[str]],
) -> List[str]:
    """Get list of all skills that have at least one dependency.

    Args:
        composition_map: Skill dependency map

    Returns:
        Sorted list of skill names with dependencies
    """
    return sorted([skill for skill, deps in composition_map.items() if deps])
