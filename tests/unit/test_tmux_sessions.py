"""Unit tests for claude_ctx_py.tmux.sessions."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.sessions import (
    tmux_attach,
    tmux_session_kill,
    tmux_session_new,
)

_MOD = "claude_ctx_py.tmux.sessions"


@pytest.mark.unit
class TestSessionNew:
    @patch(f"{_MOD}.run_tmux")
    def test_creates_when_missing(self, mock_run):
        # First call: has-session returns 1 (missing). Second call: new-session ok.
        mock_run.side_effect = [
            (1, "", "no server"),  # has-session
            (0, "", ""),            # new-session
        ]
        code, msg = tmux_session_new("proj")
        assert code == 0
        assert "Created session: proj" in msg
        # Second call must be `new-session -d -s proj -n shell` (default window)
        new_args = mock_run.call_args_list[1].args[0]
        assert new_args[:5] == ["new-session", "-d", "-s", "proj", "-n"]
        assert new_args[5] == "shell"

    @patch(f"{_MOD}.run_tmux")
    def test_idempotent_when_exists(self, mock_run):
        mock_run.return_value = (0, "", "")  # has-session ok
        code, msg = tmux_session_new("proj")
        assert code == 0
        assert "already exists" in msg
        # Only the has-session call should have run.
        assert mock_run.call_count == 1

    @patch(f"{_MOD}.run_tmux")
    def test_passes_cwd_when_given(self, mock_run):
        mock_run.side_effect = [(1, "", ""), (0, "", "")]
        tmux_session_new("proj", cwd="/work/here")
        new_args = mock_run.call_args_list[1].args[0]
        assert "-c" in new_args
        assert "/work/here" in new_args

    @patch(f"{_MOD}.run_tmux")
    def test_omits_cwd_flag_when_none(self, mock_run):
        mock_run.side_effect = [(1, "", ""), (0, "", "")]
        tmux_session_new("proj")
        new_args = mock_run.call_args_list[1].args[0]
        assert "-c" not in new_args

    @patch(f"{_MOD}.run_tmux")
    def test_custom_initial_window(self, mock_run):
        mock_run.side_effect = [(1, "", ""), (0, "", "")]
        tmux_session_new("proj", window="main")
        new_args = mock_run.call_args_list[1].args[0]
        assert new_args[-1] == "main"

    @patch(f"{_MOD}.run_tmux")
    @patch(f"{_MOD}.resolve_session", return_value="from-cwd")
    def test_resolves_session_when_no_name(self, _resolve, mock_run):
        mock_run.return_value = (0, "", "")
        code, msg = tmux_session_new()
        assert code == 0
        assert "from-cwd" in msg

    @patch(f"{_MOD}.run_tmux")
    def test_create_failure_reports(self, mock_run):
        mock_run.side_effect = [(1, "", ""), (1, "", "duplicate")]
        code, msg = tmux_session_new("proj")
        assert code == 1
        assert "Failed" in msg


@pytest.mark.unit
class TestSessionKill:
    @patch(f"{_MOD}.run_tmux")
    def test_kills_existing(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),  # has-session ok
            (0, "", ""),  # kill-session ok
        ]
        code, msg = tmux_session_kill("proj")
        assert code == 0
        assert "Killed session: proj" in msg

    @patch(f"{_MOD}.run_tmux", return_value=(1, "", ""))
    def test_missing_errors_loudly(self, _run):
        code, msg = tmux_session_kill("ghost")
        assert code == 1
        assert "not found" in msg

    @patch(f"{_MOD}.run_tmux")
    @patch(f"{_MOD}.resolve_session", return_value="from-cwd")
    def test_resolves_session_when_no_name(self, _resolve, mock_run):
        mock_run.side_effect = [(0, "", ""), (0, "", "")]
        code, _msg = tmux_session_kill()
        assert code == 0


@pytest.mark.unit
class TestAttach:
    @patch.dict("os.environ", {"TMUX": "/tmp/tmux"}, clear=False)
    @patch(f"{_MOD}.run_tmux")
    def test_inside_tmux_uses_switch_client(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),  # has-session
            (0, "", ""),  # switch-client
        ]
        code, msg = tmux_attach("proj")
        assert code == 0
        assert "Switched" in msg
        switch_args = mock_run.call_args_list[1].args[0]
        assert switch_args[0] == "switch-client"

    @patch.dict("os.environ", {}, clear=True)
    @patch(f"{_MOD}.subprocess.run")
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    def test_outside_tmux_uses_attach_session(self, _run_tmux, mock_sub):
        mock_sub.return_value.returncode = 0
        code, msg = tmux_attach("proj")
        assert code == 0
        assert "Detached" in msg
        attach_args = mock_sub.call_args.args[0]
        assert attach_args == ["tmux", "attach-session", "-t", "proj"]

    @patch(f"{_MOD}.run_tmux", return_value=(1, "", ""))
    def test_session_missing(self, _run):
        code, msg = tmux_attach("ghost")
        assert code == 1
        assert "not found" in msg

    @patch.dict("os.environ", {"TMUX": "/tmp/tmux"}, clear=False)
    @patch(f"{_MOD}.run_tmux")
    def test_window_selected_before_attach(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),  # has-session
            (0, "", ""),  # select-window
            (0, "", ""),  # switch-client
        ]
        code, _msg = tmux_attach("proj", window="shell")
        assert code == 0
        select_args = mock_run.call_args_list[1].args[0]
        assert select_args[:3] == ["select-window", "-t", "proj:shell"]

    @patch.dict("os.environ", {}, clear=True)
    @patch(f"{_MOD}.subprocess.run", side_effect=FileNotFoundError)
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    def test_tmux_not_found(self, _run_tmux, _sub):
        code, msg = tmux_attach("proj")
        assert code == 127
        assert "not found" in msg
