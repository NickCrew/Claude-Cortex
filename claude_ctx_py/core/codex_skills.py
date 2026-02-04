"""Codex skills symlinking management."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from .base import _resolve_plugin_assets_root


def _resolve_codex_skills_dir() -> Path:
    """Resolve ~/.codex/skills directory, create if needed."""
    codex_skills = Path.home() / ".codex" / "skills"
    codex_skills.mkdir(parents=True, exist_ok=True)
    return codex_skills


def _resolve_cortex_skills_root() -> Path:
    """Resolve bundled cortex skills directory."""
    return _resolve_plugin_assets_root() / "skills"


def _ensure_skill_symlink(source: Path, target: Path) -> Optional[str]:
    """Create a skill symlink, returning warning if it fails.

    Pattern adapted from rules.py::_ensure_symlink.
    """
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source.resolve():
            return None  # Already correct
        if target.is_symlink():
            target.unlink()  # Remove stale symlink
        else:
            return f"Skipping non-symlink file: {target}"
    target.symlink_to(source)
    return None


def scan_codex_skill_status() -> Dict[str, bool]:
    """Scan ~/.codex/skills and return linked status.

    Returns:
        Dict mapping skill_name -> is_linked (bool)
    """
    codex_skills_dir = _resolve_codex_skills_dir()
    cortex_skills_root = _resolve_cortex_skills_root()

    status = {}
    if not cortex_skills_root.exists():
        return status

    # Check each skill in cortex/skills
    for skill_dir in cortex_skills_root.iterdir():
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue

        skill_name = skill_dir.name
        target = codex_skills_dir / skill_name

        # Check if symlink exists and points to cortex
        is_linked = (
            target.is_symlink()
            and target.resolve() == skill_dir.resolve()
        )
        status[skill_name] = is_linked

    return status


def link_codex_skill(skill_name: str) -> Tuple[int, str]:
    """Create symlink for a single skill."""
    cortex_skills_root = _resolve_cortex_skills_root()
    codex_skills_dir = _resolve_codex_skills_dir()

    source = cortex_skills_root / skill_name
    target = codex_skills_dir / skill_name

    if not source.exists():
        return 1, f"Skill not found: {skill_name}"

    warning = _ensure_skill_symlink(source, target)
    if warning:
        return 1, warning

    return 0, f"Linked: {skill_name}"


def unlink_codex_skill(skill_name: str) -> Tuple[int, str]:
    """Remove symlink for a single skill."""
    codex_skills_dir = _resolve_codex_skills_dir()
    target = codex_skills_dir / skill_name

    if not target.exists() and not target.is_symlink():
        return 1, f"Not linked: {skill_name}"

    if not target.is_symlink():
        return 1, f"Cannot unlink non-symlink: {skill_name}"

    target.unlink()
    return 0, f"Unlinked: {skill_name}"


def link_codex_skills_by_category(category: str, registry: dict) -> Tuple[int, List[str]]:
    """Link all skills in a category."""
    messages = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name, skill_info in skills_data.items():
        categories = skill_info.get("categories", [])
        if category in categories:
            exit_code, msg = link_codex_skill(skill_name)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1

    return success_count, messages


def unlink_codex_skills_by_category(category: str, registry: dict) -> Tuple[int, List[str]]:
    """Unlink all skills in a category."""
    messages = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name, skill_info in skills_data.items():
        categories = skill_info.get("categories", [])
        if category in categories:
            exit_code, msg = unlink_codex_skill(skill_name)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1

    return success_count, messages


def link_all_codex_skills(registry: dict) -> Tuple[int, List[str]]:
    """Link all available skills."""
    messages = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name in skills_data.keys():
        exit_code, msg = link_codex_skill(skill_name)
        messages.append(msg)
        if exit_code == 0:
            success_count += 1

    return success_count, messages


def unlink_all_codex_skills() -> Tuple[int, List[str]]:
    """Unlink all Codex skills."""
    messages = []
    success_count = 0

    codex_skills_dir = _resolve_codex_skills_dir()
    if not codex_skills_dir.exists():
        return 0, []

    for item in codex_skills_dir.iterdir():
        if item.is_symlink():
            try:
                item.unlink()
                messages.append(f"Unlinked: {item.name}")
                success_count += 1
            except OSError as e:
                messages.append(f"Failed to unlink {item.name}: {e}")

    return success_count, messages
