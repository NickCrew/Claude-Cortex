"""Unit tests for claude_ctx_py.git.run."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.run import (
    check_dirty_tree,
    get_current_branch,
    get_tracking_remote,
    is_protected_branch,
    resolve_repo_root,
    run_git,
)

_MOD = "claude_ctx_py.git.run"


@pytest.mark.unit
class TestRunGit:
    @patch(f"{_MOD}.subprocess.run")
    def test_success(self, mock_sub):
        mock_sub.return_value.returncode = 0
        mock_sub.return_value.stdout = "ok\n"
        mock_sub.return_value.stderr = ""
        code, out, err = run_git(["status"], Path("/repo"))
        assert code == 0
        assert out == "ok\n"

    @patch(f"{_MOD}.subprocess.run", side_effect=FileNotFoundError)
    def test_git_not_found(self, _):
        code, out, err = run_git(["status"], Path("/repo"))
        assert code == 127
        assert "not found" in err

    @patch(f"{_MOD}.subprocess.run", side_effect=OSError("disk error"))
    def test_os_error(self, _):
        code, out, err = run_git(["status"], Path("/repo"))
        assert code == 1
        assert "disk error" in err


@pytest.mark.unit
class TestResolveRepoRoot:
    @patch(f"{_MOD}.run_git", return_value=(0, "/home/user/repo\n", ""))
    def test_success(self, _):
        root, err = resolve_repo_root(Path("/home/user/repo/sub"))
        assert root == Path("/home/user/repo")
        assert err is None

    @patch(f"{_MOD}.run_git", return_value=(128, "", "fatal: not a git repo"))
    def test_not_a_repo(self, _):
        root, err = resolve_repo_root(Path("/tmp"))
        assert root is None
        assert "not a git repo" in err.lower()


@pytest.mark.unit
class TestIsProtectedBranch:
    def test_main_protected(self):
        assert is_protected_branch("main") is True

    def test_master_protected(self):
        assert is_protected_branch("master") is True

    def test_feature_not_protected(self):
        assert is_protected_branch("feature/foo") is False

    def test_custom_set(self):
        assert is_protected_branch("prod", frozenset({"prod", "staging"})) is True


@pytest.mark.unit
class TestCheckDirtyTree:
    @patch(f"{_MOD}.run_git", return_value=(0, " M file.py\n?? new.py\n", ""))
    def test_dirty(self, _):
        dirty, files = check_dirty_tree(Path("/repo"))
        assert dirty is True
        assert "file.py" in files
        assert "new.py" in files

    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    def test_clean(self, _):
        dirty, files = check_dirty_tree(Path("/repo"))
        assert dirty is False
        assert files == []


@pytest.mark.unit
class TestGetCurrentBranch:
    @patch(f"{_MOD}.run_git", return_value=(0, "main\n", ""))
    def test_on_branch(self, _):
        assert get_current_branch(Path("/repo")) == "main"

    @patch(f"{_MOD}.run_git", return_value=(0, "\n", ""))
    def test_detached(self, _):
        assert get_current_branch(Path("/repo")) is None


@pytest.mark.unit
class TestGetTrackingRemote:
    @patch(f"{_MOD}.run_git", return_value=(0, "origin\n", ""))
    def test_has_remote(self, _):
        assert get_tracking_remote("main", Path("/repo")) == "origin"

    @patch(f"{_MOD}.run_git", return_value=(1, "", ""))
    def test_no_remote(self, _):
        assert get_tracking_remote("local-only", Path("/repo")) is None
