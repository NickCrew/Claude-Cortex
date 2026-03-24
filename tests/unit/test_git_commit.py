"""Unit tests for claude_ctx_py.git.commit."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.commit import git_commit

_MOD = "claude_ctx_py.git.commit"


def _side_effects(*returns):
    """Build a side_effect list for sequential run_git calls."""
    return list(returns)


@pytest.mark.unit
class TestGitCommit:
    @patch(f"{_MOD}.run_git")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_success(self, _root, mock_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_run.side_effect = [
            (0, "", ""),   # restore --staged
            (0, "", ""),   # add -A
            (1, "", ""),   # diff --staged --quiet (1 = has changes)
            (0, "", ""),   # commit
        ]
        code, msg = git_commit("fix: bug", [str(f)], cwd=tmp_path)
        assert code == 0
        assert "Committed" in msg

    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_empty_message(self, _root):
        code, msg = git_commit("", ["file.py"])
        assert code == 1
        assert "empty" in msg.lower()

    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_no_files(self, _root):
        code, msg = git_commit("fix: bug", [])
        assert code == 1

    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_dot_rejected(self, _root):
        code, msg = git_commit("fix: bug", ["."])
        assert code == 1
        assert '"."' in msg

    @patch(f"{_MOD}.run_git")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_no_staged_changes(self, _root, mock_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_run.side_effect = [
            (0, "", ""),   # restore --staged
            (0, "", ""),   # add -A
            (0, "", ""),   # diff --staged --quiet (0 = no changes)
        ]
        code, msg = git_commit("fix: bug", [str(f)], cwd=tmp_path)
        assert code == 1
        assert "no staged" in msg.lower()

    @patch(f"{_MOD}.run_git")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_commit_failure(self, _root, mock_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_run.side_effect = [
            (0, "", ""),   # restore --staged
            (0, "", ""),   # add -A
            (1, "", ""),   # diff --staged --quiet
            (1, "", "something went wrong"),  # commit fails
        ]
        code, msg = git_commit("fix: bug", [str(f)], cwd=tmp_path)
        assert code == 1

    @patch(f"{_MOD}.run_git")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_lock_retry(self, _root, mock_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        lock = tmp_path / ".git" / "index.lock"
        lock.parent.mkdir(parents=True)
        lock.write_text("")

        mock_run.side_effect = [
            (0, "", ""),   # restore --staged
            (0, "", ""),   # add -A
            (1, "", ""),   # diff --staged --quiet
            (1, "", f"Unable to create '{lock}'"),  # commit fails with lock
            (0, "", ""),   # retry commit succeeds
        ]
        code, msg = git_commit("fix: bug", [str(f)], force_lock=True, cwd=tmp_path)
        assert code == 0
        assert not lock.exists()

    @patch(f"{_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_commit("fix: bug", ["file.py"])
        assert code == 1
        assert "git" in msg.lower() or "repository" in msg.lower()

    @patch(f"{_MOD}.run_git")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_file_not_found(self, _root, mock_run, tmp_path):
        # File doesn't exist on disk, not in index, not in HEAD
        mock_run.side_effect = [
            (1, "", ""),   # ls-files --error-unmatch
            (1, "", ""),   # cat-file -e HEAD:file
        ]
        code, msg = git_commit("fix: bug", ["nonexistent.py"], cwd=tmp_path)
        assert code == 1
        assert "not found" in msg.lower()
