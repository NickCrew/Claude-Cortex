"""Unit tests for core/skill_link.py — project-scope skill indirection."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from claude_ctx_py.core.skill_link import (
    DriftStatus,
    link_skill,
    skill_drift_status,
    unlink_skill,
)


def _make_bundle_skill(tmp_path: Path, name: str = "my-skill") -> Path:
    """Create a minimal bundle skill directory."""
    skill_dir = tmp_path / "cortex_root" / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# My Skill\n")
    (skill_dir / "extra.txt").write_text("data\n")
    return skill_dir


def _project_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Return (project_root, claude_dir) under tmp_path."""
    project_root = tmp_path / "myproject"
    project_root.mkdir()
    claude_dir = project_root / ".claude"
    claude_dir.mkdir()
    return project_root, claude_dir


# ── project scope ─────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_project_scope_creates_agents_copy_and_relative_symlink(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root, claude_dir = _project_dirs(tmp_path)

    code, _ = link_skill(bundle, claude_dir, scope="project")

    assert code == 0
    agents_copy = project_root / ".agents" / "skills" / bundle.name
    assert agents_copy.is_dir()
    assert (agents_copy / "SKILL.md").read_text() == "# My Skill\n"

    symlink = claude_dir / "skills" / bundle.name
    assert symlink.is_symlink()
    # Must be a relative symlink, not absolute
    assert not Path(os.readlink(symlink)).is_absolute()
    # Must resolve to the agents copy
    assert symlink.resolve() == agents_copy.resolve()


@pytest.mark.unit
def test_project_scope_is_idempotent(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    _, claude_dir = _project_dirs(tmp_path)

    link_skill(bundle, claude_dir, scope="project")
    code, _ = link_skill(bundle, claude_dir, scope="project")  # second call

    assert code == 0
    symlink = claude_dir / "skills" / bundle.name
    assert symlink.is_symlink()


@pytest.mark.unit
def test_project_scope_unlink_removes_both_link_and_agents_copy(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root, claude_dir = _project_dirs(tmp_path)

    link_skill(bundle, claude_dir, scope="project")
    code, _ = unlink_skill(claude_dir, bundle.name, scope="project")

    assert code == 0
    assert not (claude_dir / "skills" / bundle.name).exists()
    assert not (project_root / ".agents" / "skills" / bundle.name).exists()


# ── global scope ──────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_global_scope_creates_direct_bundle_symlink(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    code, _ = link_skill(bundle, claude_dir, scope="global")

    assert code == 0
    symlink = claude_dir / "skills" / bundle.name
    assert symlink.is_symlink()
    # Global link resolves directly to the bundle
    assert symlink.resolve() == bundle.resolve()


@pytest.mark.unit
def test_global_scope_does_not_create_agents_dir(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    link_skill(bundle, claude_dir, scope="global")

    assert not (tmp_path / ".agents").exists()


@pytest.mark.unit
def test_global_scope_unlink_does_not_touch_agents(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root = tmp_path
    claude_dir = project_root / ".claude"
    claude_dir.mkdir()
    # Create a stray .agents dir to confirm it's untouched
    stray = project_root / ".agents" / "skills" / bundle.name
    stray.mkdir(parents=True)

    link_skill(bundle, claude_dir, scope="global")
    unlink_skill(claude_dir, bundle.name, scope="global")

    assert stray.exists(), ".agents copy must not be removed on global unlink"


# ── drift detection ───────────────────────────────────────────────────────────


@pytest.mark.unit
def test_drift_same_when_copy_matches_bundle(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root, claude_dir = _project_dirs(tmp_path)
    link_skill(bundle, claude_dir, scope="project")

    status = skill_drift_status(project_root, bundle.name, bundle.parent.parent)
    assert status == DriftStatus.SAME


@pytest.mark.unit
def test_drift_stale_when_bundle_mutated(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root, claude_dir = _project_dirs(tmp_path)
    link_skill(bundle, claude_dir, scope="project")

    # Mutate the bundle after install
    (bundle / "SKILL.md").write_text("# Updated\n")

    status = skill_drift_status(project_root, bundle.name, bundle.parent.parent)
    assert status == DriftStatus.STALE


@pytest.mark.unit
def test_drift_not_installed_when_copy_absent(tmp_path: Path) -> None:
    bundle = _make_bundle_skill(tmp_path)
    project_root, _ = _project_dirs(tmp_path)

    status = skill_drift_status(project_root, bundle.name, bundle.parent.parent)
    assert status == DriftStatus.NOT_INSTALLED


# ── error handling ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_link_skill_returns_error_for_missing_source(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    missing = tmp_path / "skills" / "nonexistent"

    code, msg = link_skill(missing, claude_dir, scope="global")

    assert code != 0
    assert "not found" in msg.lower() or "nonexistent" in msg


@pytest.mark.unit
def test_unlink_skill_returns_error_when_not_installed(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()

    code, _ = unlink_skill(claude_dir, "ghost-skill", scope="global")

    assert code != 0
