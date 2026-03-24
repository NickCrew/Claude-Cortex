"""Unit tests for claude_ctx_py.git.push."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.push import git_push

_MOD = "claude_ctx_py.git.push"


@pytest.mark.unit
class TestGitPush:
    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.get_tracking_remote", return_value="origin")
    @patch(f"{_MOD}.get_current_branch", return_value="main")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_normal_push(self, _root, _branch, _remote, _run):
        code, msg = git_push()
        assert code == 0
        assert "Pushed" in msg

    @patch(f"{_MOD}.get_current_branch", return_value="main")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_force_push_protected_refused(self, _root, _branch):
        code, msg = git_push(force=True)
        assert code == 1
        assert "refusing" in msg.lower() or "protected" in msg.lower()

    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.get_tracking_remote", return_value="origin")
    @patch(f"{_MOD}.get_current_branch", return_value="feature/foo")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_force_push_feature_allowed(self, _root, _branch, _remote, _run):
        code, msg = git_push(force=True)
        assert code == 0

    @patch(f"{_MOD}.get_tracking_remote", return_value=None)
    @patch(f"{_MOD}.get_current_branch", return_value="new-branch")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_no_tracking_remote(self, _root, _branch, _remote):
        code, msg = git_push()
        assert code == 1
        assert "tracking" in msg.lower() or "push -u" in msg

    @patch(f"{_MOD}.get_current_branch", return_value=None)
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_detached_head(self, _root, _branch):
        code, msg = git_push()
        assert code == 1
        assert "detached" in msg.lower() or "cannot" in msg.lower()

    @patch(f"{_MOD}.run_git", return_value=(1, "", "rejected"))
    @patch(f"{_MOD}.get_tracking_remote", return_value="origin")
    @patch(f"{_MOD}.get_current_branch", return_value="main")
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_push_fails(self, _root, _branch, _remote, _run):
        code, msg = git_push()
        assert code == 1

    @patch(f"{_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_push()
        assert code == 1
