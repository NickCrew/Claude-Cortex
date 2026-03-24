"""Unit tests for claude_ctx_py.tmux.run."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.run import (
    ensure_session,
    ensure_window,
    resolve_session,
    run_tmux,
)

_MOD = "claude_ctx_py.tmux.run"


@pytest.mark.unit
class TestRunTmux:
    @patch(f"{_MOD}.subprocess.run")
    def test_success(self, mock_sub):
        mock_sub.return_value.returncode = 0
        mock_sub.return_value.stdout = "ok\n"
        mock_sub.return_value.stderr = ""
        code, out, err = run_tmux(["list-sessions"])
        assert code == 0
        assert out == "ok\n"

    @patch(f"{_MOD}.subprocess.run", side_effect=FileNotFoundError)
    def test_tmux_not_found(self, _):
        code, out, err = run_tmux(["list-sessions"])
        assert code == 127
        assert "not found" in err


@pytest.mark.unit
class TestResolveSession:
    @patch.dict("os.environ", {"TMUX_SESSION": "my-session"})
    def test_from_env(self):
        assert resolve_session() == "my-session"

    @patch.dict("os.environ", {}, clear=True)
    @patch(f"{_MOD}.Path")
    def test_from_cwd(self, mock_path):
        mock_path.cwd.return_value.name = "My Project"
        assert resolve_session() == "my-project"

    @patch.dict("os.environ", {"TMUX_SESSION": ""})
    @patch(f"{_MOD}.Path")
    def test_empty_env_falls_back(self, mock_path):
        mock_path.cwd.return_value.name = "Cortex"
        assert resolve_session() == "cortex"


@pytest.mark.unit
class TestEnsureSession:
    @patch(f"{_MOD}.run_tmux", return_value=(0, "", ""))
    def test_session_exists(self, _):
        sess, err = ensure_session("test")
        assert sess == "test"
        assert err is None

    @patch(f"{_MOD}.run_tmux", return_value=(1, "", ""))
    def test_session_missing(self, _):
        sess, err = ensure_session("missing")
        assert err is not None
        assert "not found" in err.lower()


@pytest.mark.unit
class TestEnsureWindow:
    @patch(f"{_MOD}.run_tmux")
    def test_window_exists(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),             # has-session
            (0, "win1\nwin2\n", ""),  # list-windows
        ]
        sess, err = ensure_window("win1", "test")
        assert err is None

    @patch(f"{_MOD}.run_tmux")
    def test_window_missing(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),             # has-session
            (0, "win1\nwin2\n", ""),  # list-windows
        ]
        sess, err = ensure_window("nope", "test")
        assert err is not None
        assert "not found" in err.lower()

    @patch(f"{_MOD}.run_tmux", return_value=(1, "", ""))
    def test_session_missing(self, _):
        sess, err = ensure_window("win", "missing")
        assert err is not None
