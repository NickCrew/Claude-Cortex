"""Unit tests for git worktree helpers."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pytest

from claude_ctx_py.core import worktrees


def test_parse_worktree_porcelain_parses_entries(tmp_path: Path) -> None:
    output = "\n".join(
        [
            "worktree /repo",
            "HEAD 0123456789abcdef",
            "branch refs/heads/main",
            "worktree /repo/.worktrees/feature",
            "HEAD abcdef0123456789",
            "branch refs/heads/feature",
            "locked reason",
            "prunable stale",
        ]
    )

    entries = worktrees._parse_worktree_porcelain(output)
    assert len(entries) == 2
    assert entries[0]["path"] == "/repo"
    assert entries[0]["branch"] == "refs/heads/main"
    assert entries[1]["locked"] == "reason"
    assert entries[1]["prunable"] == "stale"

    info = worktrees._build_worktree_info(entries[0], Path("/repo"))
    assert info.branch == "main"
    assert info.is_main is True


def test_worktree_default_path_prefers_existing_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".worktrees").mkdir()

    monkeypatch.setattr(
        worktrees,
        "_resolve_repo_root",
        lambda cwd=None: (repo_root, None),
    )

    path, error = worktrees.worktree_default_path("feature/test")
    assert error is None
    assert path == repo_root / ".worktrees" / "feature" / "test"


def test_worktree_add_updates_gitignore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    (repo_root / ".gitignore").write_text("# ignore\n", encoding="utf-8")

    calls: List[Tuple[str, ...]] = []

    def fake_run(args, cwd):  # type: ignore[no-untyped-def]
        calls.append(tuple(args))
        if args[:3] == ["show-ref", "--verify", "--quiet"]:
            return 1, "", ""
        if args[:2] == ["worktree", "add"]:
            return 0, "", ""
        return 0, "", ""

    monkeypatch.setattr(
        worktrees,
        "_resolve_repo_root",
        lambda cwd=None: (repo_root, None),
    )
    monkeypatch.setattr(worktrees, "_run_git", fake_run)

    exit_code, message = worktrees.worktree_add("feature/one")
    assert exit_code == 0
    assert "Worktree ready" in message

    gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
    assert ".worktrees/" in gitignore

    assert any(call[:2] == ("worktree", "add") for call in calls)


def test_worktree_get_base_dir_prefers_configured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    def fake_run(args, cwd):  # type: ignore[no-untyped-def]
        if args[:4] == ["config", "--local", "--get", worktrees._WORKTREE_DIR_KEY]:
            return 0, ".custom", ""
        return 0, "", ""

    monkeypatch.setattr(
        worktrees,
        "_resolve_repo_root",
        lambda cwd=None: (repo_root, None),
    )
    monkeypatch.setattr(worktrees, "_run_git", fake_run)

    path, source, error = worktrees.worktree_get_base_dir()
    assert error is None
    assert source == "configured"
    assert path == repo_root / ".custom"
