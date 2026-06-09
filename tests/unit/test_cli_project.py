"""Unit tests for cortex project and skills move CLI commands."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from claude_ctx_py.cli import build_parser


def _parse(args: list[str]):
    return build_parser().parse_args(args)


# ── parser smoke tests ────────────────────────────────────────────────────────


@pytest.mark.unit
def test_project_init_parses() -> None:
    ns = _parse(["project", "init"])
    assert ns.command == "project"
    assert ns.project_command == "init"


@pytest.mark.unit
def test_project_init_with_skills_parses() -> None:
    ns = _parse(["project", "init", "--with-skills", "a,b,c"])
    assert ns.init_skills == "a,b,c"


@pytest.mark.unit
def test_project_sync_parses() -> None:
    ns = _parse(["project", "sync"])
    assert ns.project_command == "sync"


@pytest.mark.unit
def test_project_status_parses() -> None:
    ns = _parse(["project", "status"])
    assert ns.project_command == "status"


@pytest.mark.unit
def test_skills_move_parses() -> None:
    ns = _parse(["skills", "move", "my-skill", "--to", "project"])
    assert ns.skills_command == "move"
    assert ns.skill == "my-skill"
    assert ns.move_to == "project"


@pytest.mark.unit
def test_skills_move_global_parses() -> None:
    ns = _parse(["skills", "move", "my-skill", "--to", "global"])
    assert ns.move_to == "global"


@pytest.mark.unit
def test_skills_move_requires_to_flag() -> None:
    with pytest.raises(SystemExit):
        _parse(["skills", "move", "my-skill"])


# ── integration: project init writes valid YAML ───────────────────────────────


@pytest.mark.unit
def test_project_init_writes_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import yaml
    from claude_ctx_py.cli import main

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".claude").mkdir()

    rc = main(["project", "init", "--with-skills", "systematic-debugging,atomic-commits"])
    assert rc == 0

    manifest_path = tmp_path / ".cortex" / "manifest.yaml"
    assert manifest_path.exists()
    data = yaml.safe_load(manifest_path.read_text())
    assert "skills" in data
    assert set(data["skills"]["enabled"]) == {"systematic-debugging", "atomic-commits"}


@pytest.mark.unit
def test_project_init_merges_with_existing_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml
    from claude_ctx_py.cli import main

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".claude").mkdir()
    # Pre-existing manifest
    (tmp_path / ".cortex").mkdir()
    (tmp_path / ".cortex" / "manifest.yaml").write_text(
        "skills:\n  enabled:\n    - existing-skill\n"
    )

    rc = main(["project", "init", "--with-skills", "new-skill"])
    assert rc == 0

    data = yaml.safe_load((tmp_path / ".cortex" / "manifest.yaml").read_text())
    enabled = data["skills"]["enabled"]
    assert "existing-skill" in enabled
    assert "new-skill" in enabled


# ── integration: project sync materialises skills ────────────────────────────


@pytest.mark.unit
def test_project_sync_materialises_skills(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import yaml
    from claude_ctx_py.cli import main

    monkeypatch.chdir(tmp_path)
    (tmp_path / ".claude").mkdir()

    # Create a minimal bundle skill
    cortex_root = tmp_path / "bundle"
    skill_dir = cortex_root / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Test\n")

    # Write manifest + point CORTEX_ROOT at our bundle
    (tmp_path / ".cortex").mkdir()
    (tmp_path / ".cortex" / "manifest.yaml").write_text(
        "skills:\n  enabled:\n    - test-skill\n"
    )
    monkeypatch.setenv("CORTEX_ROOT", str(cortex_root))

    rc = main(["project", "sync"])
    assert rc == 0

    assert (tmp_path / ".agents" / "skills" / "test-skill" / "SKILL.md").is_file()
    assert (tmp_path / ".claude" / "skills" / "test-skill").is_symlink()
