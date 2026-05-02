"""Unit tests for claude_ctx_py.tmux.windows."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.windows import tmux_kill, tmux_list, tmux_new, tmux_rename

_MOD = "claude_ctx_py.tmux.windows"


@pytest.mark.unit
class TestTmuxList:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "0: main (active)\n1: build\n", ""))
    @patch(f"{_MOD}.ensure_session", return_value=("test", None))
    def test_success(self, _sess, _run):
        code, msg = tmux_list("test")
        assert code == 0
        assert "main" in msg

    @patch(f"{_MOD}.ensure_session", return_value=("test", "Session not found"))
    def test_no_session(self, _sess):
        code, msg = tmux_list("test")
        assert code == 1


@pytest.mark.unit
class TestTmuxNew:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_session", return_value=("test", None))
    def test_success(self, _sess, _run):
        code, msg = tmux_new("build", "test")
        assert code == 0
        assert "build" in msg

    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_session", return_value=("test", None))
    def test_no_cwd_omits_c_flag(self, _sess, mock_run):
        tmux_new("build", "test")
        sent_args = mock_run.call_args.args[0]
        assert "-c" not in sent_args

    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_session", return_value=("test", None))
    def test_cwd_passes_c_flag(self, _sess, mock_run):
        tmux_new("build", "test", cwd="/tmp/work")
        sent_args = mock_run.call_args.args[0]
        assert "-c" in sent_args
        assert "/tmp/work" in sent_args

    def test_empty_name(self):
        code, msg = tmux_new("")
        assert code == 1
        assert "name" in msg.lower()


@pytest.mark.unit
class TestTmuxRename:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, mock_run):
        code, msg = tmux_rename("old", "new", "test")
        assert code == 0
        assert "old -> new" in msg
        sent = mock_run.call_args.args[0]
        assert sent[0] == "rename-window"
        assert "new" in sent

    def test_empty_old(self):
        code, _msg = tmux_rename("", "new")
        assert code == 1

    def test_empty_new(self):
        code, _msg = tmux_rename("old", "")
        assert code == 1

    @patch(f"{_MOD}.ensure_window", return_value=("test", "Window not found"))
    def test_window_missing(self, _win):
        code, msg = tmux_rename("nope", "new", "test")
        assert code == 1
        assert "not found" in msg


@pytest.mark.unit
class TestTmuxKill:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_kill("build", "test")
        assert code == 0
        assert "build" in msg

    def test_empty_name(self):
        code, msg = tmux_kill("")
        assert code == 1
