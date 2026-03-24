"""Unit tests for claude_ctx_py.git.branch."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.git.branch import git_branch_create, git_branch_switch

_MOD = "claude_ctx_py.git.branch"


@pytest.mark.unit
class TestGitBranchCreate:
    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_create_simple(self, _root, _run):
        code, msg = git_branch_create("feat")
        assert code == 0
        assert "feat" in msg

    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_create_from_ref(self, _root, _run):
        code, msg = git_branch_create("feat", from_ref="develop")
        assert code == 0
        assert "develop" in msg

    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_empty_name(self, _root):
        code, msg = git_branch_create("")
        assert code == 1

    @patch(f"{_MOD}.run_git", return_value=(128, "", "already exists"))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_already_exists(self, _root, _run):
        code, msg = git_branch_create("feat")
        assert code == 1

    @patch(f"{_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_branch_create("feat")
        assert code == 1


@pytest.mark.unit
class TestGitBranchSwitch:
    @patch(f"{_MOD}.run_git", return_value=(0, "", ""))
    @patch(f"{_MOD}.check_dirty_tree", return_value=(False, []))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_switch_clean(self, _root, _dirty, _run):
        code, msg = git_branch_switch("main")
        assert code == 0
        assert "main" in msg

    @patch(f"{_MOD}.check_dirty_tree", return_value=(True, ["file.py", "other.py"]))
    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_switch_dirty_refused(self, _root, _dirty):
        code, msg = git_branch_switch("main")
        assert code == 1
        assert "uncommitted" in msg.lower()
        assert "file.py" in msg

    @patch(f"{_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_switch_empty_name(self, _root):
        code, msg = git_branch_switch("")
        assert code == 1

    @patch(f"{_MOD}.resolve_repo_root", return_value=(None, "Not a git repository"))
    def test_not_in_repo(self, _root):
        code, msg = git_branch_switch("main")
        assert code == 1
