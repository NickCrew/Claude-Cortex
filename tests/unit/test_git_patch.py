"""Unit tests for claude_ctx_py.git.patch."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.patch import git_patch

_PATCH_MOD = "claude_ctx_py.git.patch"
_COMMIT_MOD = "claude_ctx_py.git.commit"


@pytest.mark.unit
class TestGitPatch:
    @patch(f"{_COMMIT_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_success(self, _root, mock_patch_run, mock_commit_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        # patch.py's run_git: apply, diff --cached --name-only, diff --staged --quiet
        mock_patch_run.side_effect = [
            (0, "", ""),                # apply --cached
            (0, str(f) + "\n", ""),     # diff --cached --name-only
            (1, "", ""),                # diff --staged --quiet (1 = has changes)
        ]
        # commit.py's run_git: restore --staged, then commit
        mock_commit_run.side_effect = [
            (0, "", ""),                # restore --staged (via _unstage_all)
            (0, "", ""),                # git commit
        ]
        code, msg = git_patch("fix: bug", [str(f)], "diff content", cwd=tmp_path)
        assert code == 0
        assert "Committed" in msg

    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_empty_diff(self, _root, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        code, msg = git_patch("fix: bug", [str(f)], "", cwd=tmp_path)
        assert code == 1
        assert "empty" in msg.lower()

    @patch(f"{_COMMIT_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_apply_fails(self, _root, mock_patch_run, mock_commit_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_commit_run.side_effect = [
            (0, "", ""),                # restore --staged
        ]
        mock_patch_run.side_effect = [
            (1, "", "patch does not apply"),  # apply fails
        ]
        code, msg = git_patch("fix: bug", [str(f)], "bad diff", cwd=tmp_path)
        assert code == 1
        assert "apply" in msg.lower()

    @patch(f"{_COMMIT_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_unexpected_file_staged(self, _root, mock_patch_run, mock_commit_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_commit_run.side_effect = [
            (0, "", ""),                      # restore --staged
        ]
        mock_patch_run.side_effect = [
            (0, "", ""),                      # apply --cached
            (0, str(f) + "\nother.py\n", ""),  # staged includes unexpected file
        ]
        code, msg = git_patch("fix: bug", [str(f)], "diff", cwd=tmp_path)
        assert code == 1
        assert "unexpected" in msg.lower()

    @patch(f"{_COMMIT_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_no_staged_after_apply(self, _root, mock_patch_run, mock_commit_run, tmp_path):
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_commit_run.side_effect = [
            (0, "", ""),   # restore --staged
        ]
        mock_patch_run.side_effect = [
            (0, "", ""),   # apply --cached
            (0, "", ""),   # diff --cached --name-only (empty)
        ]
        code, msg = git_patch("fix: bug", [str(f)], "diff", cwd=tmp_path)
        assert code == 1
        assert "no staged" in msg.lower()

    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_patch("fix: bug", ["f.py"], "diff")
        assert code == 1
