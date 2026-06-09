"""Shared helpers for installing/removing skills at the filesystem level.

Two calling paths need identical skill-link semantics:

  * ``skills.skill_activate`` / ``skills.skill_deactivate``  (TUI toggle, slug-based)
  * ``asset_installer._install_skill`` / ``_uninstall_skill``  (asset-install flow)

Both paths previously hard-coded a direct symlink from the bundle into
``.claude/skills/<name>``.  Project-scope installs now use one indirection
layer so the canonical artifact lives in provider-neutral ``.agents/skills/``
and is committed with the project:

  bundle (cortex_root/skills/<name>)
    ── copy ──▶  <project>/.agents/skills/<name>        (real files, committable)
    ── symlink ▶ <project>/.claude/skills/<name>  →  ../../.agents/skills/<name>

Global scope is unchanged: a direct absolute symlink from the bundle into
``~/.claude/skills/<name>``.

The relative symlink is load-bearing — it makes the ``.claude`` link survive a
``git clone`` to a different path and avoids absolute home-directory paths in
committed files.
"""

from __future__ import annotations

import filecmp
import os
import shutil
from enum import Enum
from pathlib import Path
from typing import Tuple

from .base import GREEN, RED, YELLOW, _color


class DriftStatus(Enum):
    """Whether a project-scope skill copy is current with the bundle."""

    SAME = "same"
    STALE = "stale"  # copy differs from bundle
    NOT_INSTALLED = "not_installed"


def link_skill(
    source_skill: Path,
    claude_dir: Path,
    scope: str,
) -> Tuple[int, str]:
    """Install a skill into *claude_dir*, routing through .agents on project scope.

    Args:
        source_skill: Path to the bundle skill directory (cortex_root/skills/<name>).
        claude_dir: Resolved ``.claude`` directory (global ``~/.claude`` or project).
        scope: ``"project"`` for project-local indirection; anything else for global.

    Returns:
        (exit_code, message)
    """
    if not source_skill.exists() or not source_skill.is_dir():
        return 1, _color(f"Skill source not found: {source_skill}", RED)

    name = source_skill.name

    try:
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        symlink_path = skills_dir / name

        # Remove existing link/directory idempotently
        _remove_skill_link(symlink_path)

        if scope == "project":
            project_root = claude_dir.parent
            agents_skill_dir = project_root / ".agents" / "skills" / name
            agents_skill_dir.parent.mkdir(parents=True, exist_ok=True)

            # Remove stale copy before re-copying
            if agents_skill_dir.exists() or agents_skill_dir.is_symlink():
                if agents_skill_dir.is_symlink():
                    agents_skill_dir.unlink()
                else:
                    shutil.rmtree(agents_skill_dir)

            shutil.copytree(source_skill, agents_skill_dir)

            # Relative symlink: .claude/skills/<name> -> ../../.agents/skills/<name>
            rel_target = Path(
                os.path.relpath(agents_skill_dir, start=symlink_path.parent)
            )
            symlink_path.symlink_to(rel_target)
            return 0, _color(f"Installed skill (project copy): {name}", GREEN)
        else:
            # Global: direct absolute symlink to bundle
            symlink_path.symlink_to(source_skill)
            return 0, _color(f"Installed skill (symlink): {name}", GREEN)

    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to install skill {name}: {e}", RED)


def unlink_skill(
    claude_dir: Path,
    name: str,
    scope: str,
) -> Tuple[int, str]:
    """Remove a skill from *claude_dir*, also dropping the .agents copy on project scope.

    Args:
        claude_dir: Resolved ``.claude`` directory.
        name: Skill slug.
        scope: ``"project"`` also removes ``<project_root>/.agents/skills/<name>``.

    Returns:
        (exit_code, message)
    """
    symlink_path = claude_dir / "skills" / name

    if not symlink_path.exists() and not symlink_path.is_symlink():
        return 1, _color(f"Skill not installed: {name}", YELLOW)

    try:
        _remove_skill_link(symlink_path)

        if scope == "project":
            project_root = claude_dir.parent
            agents_skill_dir = project_root / ".agents" / "skills" / name
            if agents_skill_dir.exists() or agents_skill_dir.is_symlink():
                if agents_skill_dir.is_symlink():
                    agents_skill_dir.unlink()
                else:
                    shutil.rmtree(agents_skill_dir)

        return 0, _color(f"Uninstalled skill: {name}", GREEN)

    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to uninstall skill {name}: {e}", RED)


def skill_drift_status(
    project_root: Path,
    name: str,
    cortex_root: Path,
) -> DriftStatus:
    """Compare a project-scope ``.agents`` copy against the bundle.

    The ``.claude/skills/<name>`` symlink resolves to ``.agents/skills/<name>``,
    not to the bundle, so the existing symlink-resolve compare in
    ``check_installation_status`` would always report INSTALLED_DIFFERENT.
    Instead we compare the ``.agents`` copy against ``cortex_root/skills/<name>``
    by content.

    Args:
        project_root: Root of the project (parent of ``.claude``).
        name: Skill slug.
        cortex_root: Bundle root (from ``_resolve_cortex_root()``).

    Returns:
        DriftStatus enum value.
    """
    agents_copy = project_root / ".agents" / "skills" / name
    bundle = cortex_root / "skills" / name

    if not agents_copy.exists():
        return DriftStatus.NOT_INSTALLED

    if not bundle.exists():
        # Bundle skill gone — treat as stale rather than crashing
        return DriftStatus.STALE

    return DriftStatus.SAME if _dirs_equal(agents_copy, bundle) else DriftStatus.STALE


# ── internal helpers ──────────────────────────────────────────────────────────


def _remove_skill_link(path: Path) -> None:
    """Remove a skill symlink or directory at *path* if present."""
    if path.is_symlink():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _dirs_equal(a: Path, b: Path) -> bool:
    """Return True if directory trees *a* and *b* have identical content."""
    cmp = filecmp.dircmp(str(a), str(b))
    if cmp.left_only or cmp.right_only or cmp.diff_files:
        return False
    for subdir in cmp.common_dirs:
        if not _dirs_equal(a / subdir, b / subdir):
            return False
    return True
