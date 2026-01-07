"""Tests for principles snippet management."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.core import principles


@pytest.fixture
def claude_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))
    return claude_dir


def _write_snippets(claude_dir: Path) -> None:
    principles_dir = claude_dir / "principles"
    principles_dir.mkdir(parents=True, exist_ok=True)
    (principles_dir / "00-alpha.md").write_text("# Alpha\n", encoding="utf-8")
    (principles_dir / "10-beta.md").write_text("# Beta\n", encoding="utf-8")


def test_principles_build_defaults_to_all(claude_home: Path) -> None:
    _write_snippets(claude_home)

    exit_code, message = principles.principles_build()

    assert exit_code == 0
    assert "Built PRINCIPLES.md" in message
    content = (claude_home / "PRINCIPLES.md").read_text(encoding="utf-8")
    assert "Alpha" in content
    assert "Beta" in content

    active = (claude_home / ".active-principles").read_text(encoding="utf-8").splitlines()
    assert active == ["00-alpha", "10-beta"]


def test_principles_deactivate_updates_build(claude_home: Path) -> None:
    _write_snippets(claude_home)
    (claude_home / ".active-principles").write_text(
        "00-alpha\n10-beta\n", encoding="utf-8"
    )

    exit_code, message = principles.principles_deactivate("10-beta")

    assert exit_code == 0
    assert "Deactivated" in message
    content = (claude_home / "PRINCIPLES.md").read_text(encoding="utf-8")
    assert "Alpha" in content
    assert "Beta" not in content
