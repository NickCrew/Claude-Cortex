"""Unit tests for claude_ctx_py.cmd_tmux (argument parsing and handler dispatch)."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.cli import build_parser
from claude_ctx_py.cmd_tmux import handle_tmux_command

_TMUX = "claude_ctx_py.tmux"


def _parse(args: list[str]):
    return build_parser().parse_args(args)


# ── Argument Parsing ─────────────────────────────────────────────────


@pytest.mark.unit
class TestTmuxParsing:
    def test_list(self):
        ns = _parse(["tmux", "list"])
        assert ns.tmux_command == "list"

    def test_new(self):
        ns = _parse(["tmux", "new", "build"])
        assert ns.tmux_command == "new"
        assert ns.window == "build"

    def test_kill(self):
        ns = _parse(["tmux", "kill", "build"])
        assert ns.tmux_command == "kill"
        assert ns.window == "build"

    def test_send(self):
        ns = _parse(["tmux", "send", "build", "cargo", "build"])
        assert ns.tmux_command == "send"
        assert ns.window == "build"
        assert ns.command == ["cargo", "build"]

    def test_type(self):
        ns = _parse(["tmux", "type", "build", "hello"])
        assert ns.tmux_command == "type"
        assert ns.window == "build"

    def test_keys(self):
        ns = _parse(["tmux", "keys", "build", "C-c", "Enter"])
        assert ns.tmux_command == "keys"
        assert ns.key_sequence == ["C-c", "Enter"]

    def test_interrupt(self):
        ns = _parse(["tmux", "interrupt", "build"])
        assert ns.tmux_command == "interrupt"

    def test_read_default_lines(self):
        ns = _parse(["tmux", "read", "build"])
        assert ns.tmux_command == "read"
        assert ns.lines == 50

    def test_read_custom_lines(self):
        ns = _parse(["tmux", "read", "build", "20"])
        assert ns.lines == 20

    def test_dump(self):
        ns = _parse(["tmux", "dump", "build"])
        assert ns.tmux_command == "dump"

    def test_status(self):
        ns = _parse(["tmux", "status", "build"])
        assert ns.tmux_command == "status"

    def test_running(self):
        ns = _parse(["tmux", "running", "build"])
        assert ns.tmux_command == "running"

    def test_wait_default(self):
        ns = _parse(["tmux", "wait", "build"])
        assert ns.timeout == 60

    def test_wait_custom(self):
        ns = _parse(["tmux", "wait", "build", "120"])
        assert ns.timeout == 120

    def test_watch_no_pattern(self):
        ns = _parse(["tmux", "watch", "build"])
        assert ns.tmux_command == "watch"
        assert ns.pattern is None

    def test_watch_with_pattern(self):
        ns = _parse(["tmux", "watch", "build", "Finished"])
        assert ns.pattern == "Finished"


# ── Handler Dispatch ─────────────────────────────────────────────────


@pytest.mark.unit
class TestTmuxDispatch:
    @patch(f"{_TMUX}.tmux_list", return_value=(0, "0: main"))
    def test_list(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "list"]))
        assert code == 0
        mock_fn.assert_called_once()

    @patch(f"{_TMUX}.tmux_new", return_value=(0, "Created"))
    def test_new(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "new", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")

    @patch(f"{_TMUX}.tmux_kill", return_value=(0, "Killed"))
    def test_kill(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "kill", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")

    @patch(f"{_TMUX}.tmux_send", return_value=(0, "Sent"))
    def test_send(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "send", "build", "cargo", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build", "cargo build")

    @patch(f"{_TMUX}.tmux_interrupt", return_value=(0, "Interrupted"))
    def test_interrupt(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "interrupt", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")

    @patch(f"{_TMUX}.tmux_read", return_value=(0, "output"))
    def test_read(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "read", "build", "20"]))
        assert code == 0
        mock_fn.assert_called_once_with("build", lines=20)

    @patch(f"{_TMUX}.tmux_dump", return_value=(0, "scrollback"))
    def test_dump(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "dump", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")

    @patch(f"{_TMUX}.tmux_running", return_value=(0, "running"))
    def test_running(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "running", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")

    @patch(f"{_TMUX}.tmux_status", return_value=(0, "status info"))
    def test_status(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "status", "build"]))
        assert code == 0
        mock_fn.assert_called_once_with("build")
