"""Unit tests for claude_ctx_py.cmd_git (argument parsing and handler dispatch)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.cli import build_parser
from claude_ctx_py.cmd_git import handle_git_command

_CMD = "claude_ctx_py.cmd_git"


def _parse(args: list[str]):
    return build_parser().parse_args(args)


# ── Argument Parsing ─────────────────────────────────────────────────


@pytest.mark.unit
class TestCommitParsing:
    def test_basic(self):
        ns = _parse(["git", "commit", "fix: bug", "file.py"])
        assert ns.git_command == "commit"
        assert ns.message == "fix: bug"
        assert ns.files == ["file.py"]
        assert ns.force is False

    def test_multiple_files(self):
        ns = _parse(["git", "commit", "feat: add", "a.py", "b.py"])
        assert ns.files == ["a.py", "b.py"]

    def test_force(self):
        ns = _parse(["git", "commit", "--force", "fix: lock", "f.py"])
        assert ns.force is True


@pytest.mark.unit
class TestPatchParsing:
    def test_basic(self):
        ns = _parse(["git", "patch", "--diff", "f.diff", "fix: bug", "file.py"])
        assert ns.git_command == "patch"
        assert ns.diff_files == ["f.diff"]
        assert ns.message == "fix: bug"
        assert ns.files == ["file.py"]

    def test_multiple_diffs(self):
        ns = _parse(["git", "patch", "--diff", "a.diff", "--diff", "b.diff", "msg", "f.py"])
        assert ns.diff_files == ["a.diff", "b.diff"]


@pytest.mark.unit
class TestPushParsing:
    def test_no_args(self):
        ns = _parse(["git", "push"])
        assert ns.git_command == "push"
        assert ns.remote is None
        assert ns.branch is None
        assert ns.force is False

    def test_with_remote_and_branch(self):
        ns = _parse(["git", "push", "origin", "main"])
        assert ns.remote == "origin"
        assert ns.branch == "main"

    def test_force(self):
        ns = _parse(["git", "push", "--force", "origin", "main"])
        assert ns.force is True


@pytest.mark.unit
class TestStashParsing:
    def test_save_with_message(self):
        ns = _parse(["git", "stash", "save", "wip"])
        assert ns.stash_command == "save"
        assert ns.stash_message == "wip"

    def test_save_no_message(self):
        ns = _parse(["git", "stash", "save"])
        assert ns.stash_command == "save"
        assert ns.stash_message is None

    def test_apply_default(self):
        ns = _parse(["git", "stash", "apply"])
        assert ns.stash_command == "apply"
        assert ns.stash_index == 0

    def test_drop_confirm(self):
        ns = _parse(["git", "stash", "drop", "--confirm", "2"])
        assert ns.stash_command == "drop"
        assert ns.confirm is True
        assert ns.stash_index == 2

    def test_drop_no_confirm(self):
        ns = _parse(["git", "stash", "drop", "1"])
        assert ns.confirm is False
        assert ns.stash_index == 1


@pytest.mark.unit
class TestBranchParsing:
    def test_create(self):
        ns = _parse(["git", "branch", "create", "feat"])
        assert ns.branch_command == "create"
        assert ns.name == "feat"

    def test_create_from(self):
        ns = _parse(["git", "branch", "create", "feat", "--from", "develop"])
        assert ns.from_ref == "develop"

    def test_switch(self):
        ns = _parse(["git", "branch", "switch", "main"])
        assert ns.branch_command == "switch"
        assert ns.name == "main"


# ── Handler Dispatch ─────────────────────────────────────────────────


_GIT = "claude_ctx_py.git"


@pytest.mark.unit
class TestHandlerDispatch:
    @patch(f"{_GIT}.git_commit", return_value=(0, "Committed"))
    def test_commit(self, mock_fn):
        ns = _parse(["git", "commit", "fix: bug", "file.py"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_push", return_value=(0, "Pushed"))
    def test_push(self, mock_fn):
        ns = _parse(["git", "push"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_stash_save", return_value=(0, "Stashed"))
    def test_stash_save(self, mock_fn):
        ns = _parse(["git", "stash", "save", "wip"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_stash_drop", return_value=(0, "Dropped"))
    def test_stash_drop(self, mock_fn):
        ns = _parse(["git", "stash", "drop", "--confirm", "0"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_branch_create", return_value=(0, "Created"))
    def test_branch_create(self, mock_fn):
        ns = _parse(["git", "branch", "create", "feat"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_branch_switch", return_value=(0, "Switched"))
    def test_branch_switch(self, mock_fn):
        ns = _parse(["git", "branch", "switch", "main"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_GIT}.git_patch", return_value=(0, "Patched"))
    def test_patch(self, mock_fn, tmp_path):
        diff_file = tmp_path / "test.diff"
        diff_file.write_text("diff content")
        ns = _parse(["git", "patch", "--diff", str(diff_file), "fix: bug", "f.py"])
        code = handle_git_command(ns)
        assert code == 0
        mock_fn.assert_called_once()
