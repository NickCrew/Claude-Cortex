"""Unit tests for claude_ctx_py.tmux.snapshot."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.snapshot import tmux_sessions, tmux_snapshot

_MOD = "claude_ctx_py.tmux.snapshot"


def _list_sessions_returns(*sessions: str):
    """Build a fake `run_tmux` reply for `list-sessions`."""
    return (0, "\n".join(sessions) + "\n", "")


def _list_windows_returns(*windows: str):
    return (0, "\n".join(windows) + "\n", "")


def _capture_returns(text: str):
    return (0, text, "")


@pytest.mark.unit
class TestTmuxSessions:
    @patch(f"{_MOD}.run_tmux")
    def test_lists_attached_and_detached(self, mock_run):
        mock_run.return_value = _list_sessions_returns(
            "main:1:3",
            "side:0:1",
        )
        code, msg = tmux_sessions()
        assert code == 0
        assert "main (attached): 3 windows" in msg
        assert "side (detached): 1 windows" in msg

    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    def test_no_sessions(self, _run):
        code, msg = tmux_sessions()
        assert code == 0
        assert "No tmux sessions" in msg

    @patch(f"{_MOD}.run_tmux", return_value=(1, "", "no server running"))
    def test_tmux_not_running(self, _run):
        code, msg = tmux_sessions()
        assert code == 1
        assert "Failed" in msg


@pytest.mark.unit
class TestTmuxSnapshot:
    @patch(f"{_MOD}.run_tmux")
    def test_renders_all_sessions(self, mock_run):
        # First call: list-sessions
        # Then for each session: list-windows + capture-pane per window
        mock_run.side_effect = [
            _list_sessions_returns("main:1:2"),
            _list_windows_returns("0:claude:1", "1:shell:0"),
            _capture_returns("running task\nstep 1\nstep 2\n"),
            _capture_returns("$ ls\nfile.txt\n"),
        ]
        code, msg = tmux_snapshot(lines=5)
        assert code == 0
        assert "=== main (attached) ===" in msg
        assert "[0] claude *" in msg  # active marker
        assert "[1] shell" in msg
        assert "step 2" in msg
        assert "file.txt" in msg

    @patch(f"{_MOD}.run_tmux")
    def test_session_filter(self, mock_run):
        mock_run.side_effect = [
            _list_sessions_returns("main:1:1", "other:0:1"),
            _list_windows_returns("0:claude:1"),
            _capture_returns("hello\n"),
        ]
        code, msg = tmux_snapshot(session="main")
        assert code == 0
        assert "main" in msg
        assert "other" not in msg

    @patch(f"{_MOD}.run_tmux")
    def test_session_filter_unknown(self, mock_run):
        mock_run.side_effect = [_list_sessions_returns("main:1:1")]
        code, msg = tmux_snapshot(session="nope")
        assert code == 1
        assert "nope" in msg

    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    def test_no_sessions(self, _run):
        code, msg = tmux_snapshot()
        assert code == 0
        assert "No tmux sessions" in msg

    @patch(f"{_MOD}.run_tmux")
    def test_window_with_no_recent_output(self, mock_run):
        mock_run.side_effect = [
            _list_sessions_returns("main:0:1"),
            _list_windows_returns("0:idle:1"),
            _capture_returns("\n\n  \n"),
        ]
        code, msg = tmux_snapshot()
        assert code == 0
        assert "(empty)" in msg
