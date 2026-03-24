"""Unit tests for claude_ctx_py.tmux.output."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.output import (
    tmux_dump,
    tmux_read,
    tmux_running,
    tmux_status,
)

_MOD = "claude_ctx_py.tmux.output"


@pytest.mark.unit
class TestTmuxRead:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "line1\nline2\n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_read("build", 50, "test")
        assert code == 0
        assert "line1" in msg

    def test_empty_window(self):
        code, msg = tmux_read("")
        assert code == 1

    @patch(f"{_MOD}.ensure_window", return_value=("test", "Window not found"))
    def test_window_missing(self, _win):
        code, msg = tmux_read("nope", session="test")
        assert code == 1


@pytest.mark.unit
class TestTmuxDump:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "full scrollback\n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_dump("build", "test")
        assert code == 0
        assert "scrollback" in msg


@pytest.mark.unit
class TestTmuxStatus:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "compiling...\ndone\n$\n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_status("build", "test")
        assert code == 0
        assert "window: build" in msg


@pytest.mark.unit
class TestTmuxRunning:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "compiling...\nbuilding\n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_running(self, _win, _run):
        code, msg = tmux_running("build", "test")
        assert code == 0
        assert "running" in msg.lower()

    @patch(f"{_MOD}.run_tmux", return_value=(0, "done\n$ \n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_at_prompt(self, _win, _run):
        code, msg = tmux_running("build", "test")
        assert code == 1
        assert "prompt" in msg.lower()

    @patch(f"{_MOD}.run_tmux", return_value=(0, "\n\n\n", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_empty_output_is_running(self, _win, _run):
        code, msg = tmux_running("build", "test")
        assert code == 0
