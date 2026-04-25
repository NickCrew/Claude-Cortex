"""Unit tests for claude_ctx_py.git.patch."""
from __future__ import annotations

import subprocess
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

    @patch(f"{_COMMIT_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.run_git")
    @patch(f"{_PATCH_MOD}.resolve_repo_root", return_value=(Path("/repo"), None))
    def test_commit_invocation_has_no_pathspec(
        self, _root, mock_patch_run, mock_commit_run, tmp_path
    ):
        """``git commit`` must not receive pathspec args from ``git_patch``.

        Pathspec on commit triggers ``--only`` mode, which re-stages
        working-tree content and silently destroys the hunks staged by
        ``git apply --cached``. Asserting argv shape here freezes the
        contract so a future refactor can't reintroduce the bug.
        """
        f = tmp_path / "file.py"
        f.write_text("x")
        mock_patch_run.side_effect = [
            (0, "", ""),                # apply --cached
            (0, str(f) + "\n", ""),     # diff --cached --name-only
            (1, "", ""),                # diff --staged --quiet
        ]
        mock_commit_run.side_effect = [
            (0, "", ""),                # restore --staged
            (0, "", ""),                # git commit
        ]
        code, _msg = git_patch("fix: bug", [str(f)], "diff content", cwd=tmp_path)
        assert code == 0
        # The commit call is the second invocation on commit.py's run_git
        # (the first is ``restore --staged`` from _unstage_all).
        commit_call = mock_commit_run.call_args_list[1]
        argv = commit_call.args[0]
        assert argv[:3] == ["commit", "-m", "fix: bug"]
        assert "--" not in argv, (
            f"git_patch must not pass pathspec to git commit; "
            f"got argv={argv}"
        )
        assert str(f) not in argv


@pytest.mark.integration
class TestGitPatchIntegration:
    """Real-git integration tests for ``git_patch``.

    Mocked unit tests can pass even when the commit argv silently destroys
    the staged index (the original bug). These tests run real ``git``
    against a ``tmp_path`` repo to verify what actually lands.
    """

    @staticmethod
    def _git(*args: str, cwd: Path) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
        ).stdout

    def test_partial_diff_commits_only_named_hunks(self, tmp_path):
        """Hand-crafted diff with one hunk must commit only that hunk.

        Reproduces the original bug: working tree has two unrelated hunks
        (top + bottom), patch input contains only the top hunk. After
        ``git_patch``, HEAD must contain only the top hunk; the bottom
        hunk must remain in the working tree, unstaged.
        """
        repo = tmp_path
        self._git("init", "-q", cwd=repo)
        self._git("config", "user.email", "t@t", cwd=repo)
        self._git("config", "user.name", "t", cwd=repo)

        f = repo / "f.txt"
        f.write_text("line1\nline2\nline3\nline4\nline5\n")
        self._git("add", "f.txt", cwd=repo)
        self._git("commit", "-qm", "init", cwd=repo)

        # Working tree gets two unrelated hunks.
        f.write_text("LINE1-changed\nline2\nline3\nline4\nLINE5-changed\n")

        # Hand-crafted patch containing ONLY the top hunk.
        top_hunk_only = (
            "diff --git a/f.txt b/f.txt\n"
            "--- a/f.txt\n"
            "+++ b/f.txt\n"
            "@@ -1,3 +1,3 @@\n"
            "-line1\n"
            "+LINE1-changed\n"
            " line2\n"
            " line3\n"
        )

        code, msg = git_patch(
            "fix: rename line1", ["f.txt"], top_hunk_only, cwd=repo
        )
        assert code == 0, msg

        # HEAD must contain LINE1 change but NOT LINE5 change.
        committed_diff = self._git("show", "HEAD", "--", "f.txt", cwd=repo)
        assert "+LINE1-changed" in committed_diff
        assert "+LINE5-changed" not in committed_diff, (
            "Bug regression: git_patch committed a hunk that was not in the "
            "patch input — pathspec on git commit triggered --only mode and "
            "re-staged working-tree content."
        )

        # The unrelated hunk must still be in the working tree, unstaged.
        worktree_diff = self._git("diff", "--", "f.txt", cwd=repo)
        assert "+LINE5-changed" in worktree_diff
