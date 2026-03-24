"""Unit tests for claude_ctx_py.tmux.commands."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.commands import tmux_interrupt, tmux_keys, tmux_send, tmux_type

_MOD = "claude_ctx_py.tmux.commands"


@pytest.mark.unit
class TestTmuxSend:
    @patch(f"{_MOD}.time.sleep")
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run, _sleep):
        code, msg = tmux_send("build", "cargo build", "test")
        assert code == 0
        assert "cargo build" in msg

    def test_empty_window(self):
        code, msg = tmux_send("", "cmd")
        assert code == 1

    def test_empty_command(self):
        code, msg = tmux_send("build", "")
        assert code == 1

    @patch(f"{_MOD}.ensure_window", return_value=("test", "Window not found"))
    def test_window_missing(self, _win):
        code, msg = tmux_send("nope", "cmd", "test")
        assert code == 1


@pytest.mark.unit
class TestTmuxType:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_type("build", "hello", "test")
        assert code == 0

    def test_empty_window(self):
        code, msg = tmux_type("", "text")
        assert code == 1


@pytest.mark.unit
class TestTmuxKeys:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_keys("build", "C-c Enter", "test")
        assert code == 0

    def test_empty_keys(self):
        code, msg = tmux_keys("build", "")
        assert code == 1


@pytest.mark.unit
class TestTmuxInterrupt:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, _run):
        code, msg = tmux_interrupt("build", "test")
        assert code == 0
        assert "interrupt" in msg.lower()

    def test_empty_window(self):
        code, msg = tmux_interrupt("")
        assert code == 1
