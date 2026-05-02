"""Unit tests for claude_ctx_py.tmux.commands."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.commands import (
    tmux_interrupt,
    tmux_keys,
    tmux_say,
    tmux_send,
    tmux_type,
)

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
class TestTmuxSay:
    @patch(f"{_MOD}.time.sleep")
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_success(self, _win, mock_run, mock_sleep):
        code, msg = tmux_say("claude", "hello there", "test", settle=0.5)
        assert code == 0
        assert "hello there" in msg
        # Two send-keys calls: text, then Enter — never combined.
        assert mock_run.call_count == 2
        first_call_args = mock_run.call_args_list[0].args[0]
        second_call_args = mock_run.call_args_list[1].args[0]
        assert "hello there" in first_call_args
        assert "Enter" not in first_call_args
        assert second_call_args[-1] == "Enter"
        # Settle pause happens between the two calls.
        mock_sleep.assert_called_once_with(0.5)

    @patch(f"{_MOD}.time.sleep")
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_no_c_c_clear(self, _win, mock_run, _sleep):
        # tmux_say must NOT prepend C-c — that would interrupt the TUI.
        tmux_say("claude", "hi", "test")
        for call in mock_run.call_args_list:
            assert "C-c" not in call.args[0]

    @patch(f"{_MOD}.time.sleep")
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    @patch(f"{_MOD}.ensure_window", return_value=("test", None))
    def test_zero_settle_skips_sleep(self, _win, _run, mock_sleep):
        tmux_say("claude", "hi", "test", settle=0)
        mock_sleep.assert_not_called()

    def test_empty_window(self):
        code, _msg = tmux_say("", "hi")
        assert code == 1

    def test_empty_message(self):
        code, _msg = tmux_say("claude", "")
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
