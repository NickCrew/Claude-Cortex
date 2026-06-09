"""Unit tests for core/manifest.py — .cortex/manifest.yaml reconcile."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.core.manifest import (
    ReconcileReport,
    load_manifest,
    reconcile,
    write_manifest,
)


def _make_bundle(tmp_path: Path, *names: str) -> Path:
    """Create minimal bundle skills and return cortex_root."""
    cortex_root = tmp_path / "cortex_root"
    for name in names:
        skill_dir = cortex_root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {name}\n")
    return cortex_root


def _make_project(tmp_path: Path) -> Path:
    """Return a project root with an empty .claude directory."""
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    return project


# ── round-trip ────────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_write_and_load_manifest_roundtrip(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    data = {"skills": {"enabled": ["systematic-debugging", "atomic-commits"]}}
    write_manifest(project, data)
    loaded = load_manifest(project)
    assert loaded == data


@pytest.mark.unit
def test_load_manifest_returns_empty_when_missing(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    assert load_manifest(project) == {}


@pytest.mark.unit
def test_load_manifest_returns_empty_on_malformed_yaml(tmp_path: Path) -> None:
    project = _make_project(tmp_path)
    (project / ".cortex").mkdir()
    (project / ".cortex" / "manifest.yaml").write_text(": bad: yaml: {{{\n")
    assert load_manifest(project) == {}


# ── reconcile: adds missing ───────────────────────────────────────────────────


@pytest.mark.unit
def test_reconcile_adds_missing_skills(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a", "skill-b")
    project = _make_project(tmp_path)
    write_manifest(project, {"skills": {"enabled": ["skill-a", "skill-b"]}})

    report = reconcile(project, cortex_root=cortex_root)

    assert set(report.added) == {"skill-a", "skill-b"}
    assert not report.errors
    # .agents copies exist
    assert (project / ".agents" / "skills" / "skill-a" / "SKILL.md").is_file()
    assert (project / ".agents" / "skills" / "skill-b" / "SKILL.md").is_file()
    # .claude symlinks exist
    assert (project / ".claude" / "skills" / "skill-a").is_symlink()
    assert (project / ".claude" / "skills" / "skill-b").is_symlink()


@pytest.mark.unit
def test_reconcile_is_idempotent(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a")
    project = _make_project(tmp_path)
    write_manifest(project, {"skills": {"enabled": ["skill-a"]}})

    reconcile(project, cortex_root=cortex_root)
    report = reconcile(project, cortex_root=cortex_root)  # second run

    assert not report.added
    assert not report.errors
    assert "skill-a" in report.unchanged


# ── reconcile: removes undeclared ─────────────────────────────────────────────


@pytest.mark.unit
def test_reconcile_removes_undeclared_skills(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a", "skill-b")
    project = _make_project(tmp_path)
    # Install both initially
    write_manifest(project, {"skills": {"enabled": ["skill-a", "skill-b"]}})
    reconcile(project, cortex_root=cortex_root)

    # Now declare only skill-a
    write_manifest(project, {"skills": {"enabled": ["skill-a"]}})
    report = reconcile(project, cortex_root=cortex_root)

    assert "skill-b" in report.removed
    assert not (project / ".agents" / "skills" / "skill-b").exists()
    assert not (project / ".claude" / "skills" / "skill-b").exists()


# ── reconcile: refreshes stale ────────────────────────────────────────────────


@pytest.mark.unit
def test_reconcile_refreshes_stale_copy(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a")
    project = _make_project(tmp_path)
    write_manifest(project, {"skills": {"enabled": ["skill-a"]}})
    reconcile(project, cortex_root=cortex_root)

    # Mutate the bundle
    (cortex_root / "skills" / "skill-a" / "SKILL.md").write_text("# Updated\n")

    report = reconcile(project, refresh_drift=True, cortex_root=cortex_root)

    assert "skill-a" in report.refreshed
    # Copy should now match the updated bundle
    copy_content = (project / ".agents" / "skills" / "skill-a" / "SKILL.md").read_text()
    assert copy_content == "# Updated\n"


@pytest.mark.unit
def test_reconcile_does_not_refresh_when_refresh_drift_false(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a")
    project = _make_project(tmp_path)
    write_manifest(project, {"skills": {"enabled": ["skill-a"]}})
    reconcile(project, cortex_root=cortex_root)

    (cortex_root / "skills" / "skill-a" / "SKILL.md").write_text("# Updated\n")

    report = reconcile(project, refresh_drift=False, cortex_root=cortex_root)

    assert not report.refreshed
    # Old content preserved
    copy_content = (project / ".agents" / "skills" / "skill-a" / "SKILL.md").read_text()
    assert copy_content == "# skill-a\n"


# ── reconcile: degraded inputs ────────────────────────────────────────────────


@pytest.mark.unit
def test_reconcile_empty_manifest_degrades_gracefully(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path, "skill-a")
    project = _make_project(tmp_path)
    # No manifest written — should not crash

    report = reconcile(project, cortex_root=cortex_root)

    assert not report.added
    assert not report.errors


@pytest.mark.unit
def test_reconcile_records_error_for_missing_bundle(tmp_path: Path) -> None:
    cortex_root = _make_bundle(tmp_path)  # no skills created
    project = _make_project(tmp_path)
    write_manifest(project, {"skills": {"enabled": ["ghost-skill"]}})

    report = reconcile(project, cortex_root=cortex_root)

    assert any("ghost-skill" in e for e in report.errors)
    assert not report.added
