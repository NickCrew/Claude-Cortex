"""Unit tests for claude_ctx_py.tmux.run."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from claude_ctx_py.tmux.run import (
    _strip_pane,
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

    @patch(f"{_MOD}.run_tmux")
    def test_pane_suffix_stripped(self, mock_run):
        mock_run.side_effect = [
            (0, "", ""),             # has-session
            (0, "claude\nshell\n", ""),  # list-windows
        ]
        # `claude.1` should validate against window `claude`.
        sess, err = ensure_window("claude.1", "test")
        assert err is None

    @patch(f"{_MOD}.run_tmux")
    def test_dotted_window_name_preserved(self, mock_run):
        # A window literally named `my.config` (non-numeric suffix) is
        # not stripped — the regex only matches `.<digits>$`.
        mock_run.side_effect = [
            (0, "", ""),
            (0, "my.config\n", ""),
        ]
        sess, err = ensure_window("my.config", "test")
        assert err is None


@pytest.mark.unit
class TestStripPane:
    def test_strips_numeric_suffix(self):
        assert _strip_pane("claude.1") == "claude"
        assert _strip_pane("shell.0") == "shell"
        assert _strip_pane("name.42") == "name"

    def test_preserves_non_numeric_suffix(self):
        assert _strip_pane("my.config") == "my.config"
        assert _strip_pane("file.tsx") == "file.tsx"

    def test_no_suffix(self):
        assert _strip_pane("claude") == "claude"
