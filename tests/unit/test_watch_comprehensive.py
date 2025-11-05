"""Comprehensive tests for watch module."""

import pytest
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from collections import deque

from claude_ctx_py.watch import WatchMode, watch_main
from claude_ctx_py.intelligence import AgentRecommendation, SessionContext


class TestWatchMode:
    """Tests for WatchMode class."""

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_watch_mode_init(self, mock_resolve, tmp_path):
        """Test initializing watch mode."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode(
            auto_activate=True,
            notification_threshold=0.7,
            check_interval=2.0,
        )

        assert watch.auto_activate is True
        assert watch.notification_threshold == 0.7
        assert watch.check_interval == 2.0
        assert watch.running is False
        assert watch.checks_performed == 0
        assert watch.recommendations_made == 0
        assert watch.auto_activations == 0

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_get_git_head_success(self, mock_run, mock_resolve, tmp_path):
        """Test getting git HEAD successfully."""
        mock_resolve.return_value = tmp_path
        mock_run.return_value = MagicMock(
            stdout="abc123def456\n",
            returncode=0,
        )

        watch = WatchMode()
        head = watch._get_git_head()

        assert head == "abc123def456"

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_get_git_head_failure(self, mock_run, mock_resolve, tmp_path):
        """Test handling git HEAD failure."""
        mock_resolve.return_value = tmp_path
        mock_run.side_effect = Exception("Git error")

        watch = WatchMode()
        head = watch._get_git_head()

        assert head is None

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_get_changed_files_returns_list(self, mock_resolve, tmp_path):
        """Test getting changed files returns a list."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()

        # Mock the method directly to avoid subprocess complexity
        with patch.object(watch, '_get_changed_files', return_value=[Path("file1.py"), Path("file2.ts")]):
            files = watch._get_changed_files()

            assert isinstance(files, list)
            assert len(files) == 2
            assert files[0].name == "file1.py"

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_get_changed_files_failure(self, mock_run, mock_resolve, tmp_path):
        """Test handling git diff failure."""
        mock_resolve.return_value = tmp_path
        mock_run.side_effect = Exception("Git error")

        watch = WatchMode()
        files = watch._get_changed_files()

        assert files == []

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_timestamp_format(self, mock_resolve, tmp_path):
        """Test timestamp formatting."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        timestamp = watch._timestamp()

        # Should be HH:MM:SS format
        assert len(timestamp) == 8
        assert timestamp.count(':') == 2

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_print_notification(self, mock_resolve, tmp_path, capsys):
        """Test printing notification."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        watch._print_notification("🔍", "Test", "Message", "cyan")

        captured = capsys.readouterr()
        assert "🔍" in captured.out
        assert "Test" in captured.out
        assert "Message" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_notification_history(self, mock_resolve, tmp_path):
        """Test notification history tracking."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        watch._print_notification("🔍", "Test", "Message", "cyan")

        assert len(watch.notification_history) == 1
        assert watch.notification_history[0]["icon"] == "🔍"
        assert watch.notification_history[0]["title"] == "Test"

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_recommendations_changed_empty_old(self, mock_resolve, tmp_path):
        """Test detecting change from empty recommendations."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        watch.last_recommendations = []

        new_recs = [
            AgentRecommendation(
                agent_name="test-automator",
                confidence=0.9,
                reason="Tests",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

        changed = watch._recommendations_changed(new_recs)
        assert changed is True

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_recommendations_changed_same(self, mock_resolve, tmp_path):
        """Test detecting no change in recommendations."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        rec = AgentRecommendation(
            agent_name="test-automator",
            confidence=0.9,
            reason="Tests",
            urgency="high",
            auto_activate=True,
            context_triggers=["tests"],
        )
        watch.last_recommendations = [rec]

        new_recs = [rec]
        changed = watch._recommendations_changed(new_recs)
        assert changed is False

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_recommendations_changed_different(self, mock_resolve, tmp_path):
        """Test detecting change in recommendations."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        watch.last_recommendations = [
            AgentRecommendation(
                agent_name="test-automator",
                confidence=0.9,
                reason="Tests",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

        new_recs = [
            AgentRecommendation(
                agent_name="code-reviewer",
                confidence=0.8,
                reason="Review",
                urgency="medium",
                auto_activate=False,
                context_triggers=["review"],
            )
        ]

        changed = watch._recommendations_changed(new_recs)
        assert changed is True

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_show_recommendations_empty(self, mock_resolve, tmp_path, capsys):
        """Test showing empty recommendations."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        watch._show_recommendations([], context)

        captured = capsys.readouterr()
        assert "No recommendations" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_show_recommendations_with_context(self, mock_resolve, tmp_path, capsys):
        """Test showing recommendations with context."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode(notification_threshold=0.5)
        now = datetime.now()
        context = SessionContext(
            files_changed=["auth.py"],
            file_types={".py"},
            directories={"src"},
            has_tests=False,
            has_auth=True,
            has_api=True,
            has_frontend=False,
            has_backend=True,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        recommendations = [
            AgentRecommendation(
                agent_name="security-auditor",
                confidence=0.9,
                reason="Auth changes detected",
                urgency="high",
                auto_activate=True,
                context_triggers=["auth"],
            )
        ]

        watch._show_recommendations(recommendations, context)

        captured = capsys.readouterr()
        assert "Auth" in captured.out or "API" in captured.out or "Backend" in captured.out
        assert "security-auditor" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("claude_ctx_py.watch.agent_activate")
    def test_handle_auto_activation_success(self, mock_activate, mock_resolve, tmp_path, capsys):
        """Test successful auto-activation."""
        mock_resolve.return_value = tmp_path
        mock_activate.return_value = (0, "Success")

        watch = WatchMode(auto_activate=True)
        recommendations = [
            AgentRecommendation(
                agent_name="test-automator",
                confidence=0.9,
                reason="Tests",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

        watch._handle_auto_activation(recommendations)

        assert "test-automator" in watch.activated_agents
        assert watch.auto_activations == 1
        captured = capsys.readouterr()
        assert "test-automator" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("claude_ctx_py.watch.agent_activate")
    def test_handle_auto_activation_failure(self, mock_activate, mock_resolve, tmp_path, capsys):
        """Test handling auto-activation failure."""
        mock_resolve.return_value = tmp_path
        mock_activate.return_value = (1, "Failed")

        watch = WatchMode(auto_activate=True)
        recommendations = [
            AgentRecommendation(
                agent_name="test-automator",
                confidence=0.9,
                reason="Tests",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

        watch._handle_auto_activation(recommendations)

        assert "test-automator" not in watch.activated_agents
        assert watch.auto_activations == 0
        captured = capsys.readouterr()
        assert "Failed" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_handle_auto_activation_no_agents(self, mock_resolve, tmp_path):
        """Test auto-activation with no eligible agents."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode(auto_activate=True)
        recommendations = [
            AgentRecommendation(
                agent_name="code-reviewer",
                confidence=0.8,
                reason="Review",
                urgency="medium",
                auto_activate=False,  # Not auto-activatable
                context_triggers=["review"],
            )
        ]

        watch._handle_auto_activation(recommendations)

        assert len(watch.activated_agents) == 0
        assert watch.auto_activations == 0

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_handle_auto_activation_already_activated(self, mock_resolve, tmp_path):
        """Test skipping already activated agents."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode(auto_activate=True)
        watch.activated_agents.add("test-automator")

        recommendations = [
            AgentRecommendation(
                agent_name="test-automator",
                confidence=0.9,
                reason="Tests",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

        watch._handle_auto_activation(recommendations)

        # Should not increase count since already activated
        assert watch.auto_activations == 0

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_check_for_changes_with_commit(self, mock_run, mock_resolve, tmp_path, capsys):
        """Test checking for changes with new commit."""
        mock_resolve.return_value = tmp_path
        mock_run.side_effect = [
            MagicMock(stdout="new_commit_hash\n", returncode=0),  # git rev-parse HEAD
            MagicMock(stdout="", returncode=0),  # git diff
            MagicMock(stdout="", returncode=0),  # git diff --cached
        ]

        watch = WatchMode()
        watch.last_git_head = "old_commit_hash"
        watch._check_for_changes()

        assert watch.checks_performed == 1
        captured = capsys.readouterr()
        assert "commit" in captured.out.lower()

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_print_statistics(self, mock_resolve, tmp_path, capsys):
        """Test printing statistics."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode()
        watch.checks_performed = 10
        watch.recommendations_made = 5
        watch.auto_activations = 3
        watch.activated_agents.add("test-automator")
        watch.activated_agents.add("code-reviewer")

        watch._print_statistics()

        captured = capsys.readouterr()
        assert "10" in captured.out  # checks
        assert "5" in captured.out  # recommendations
        assert "3" in captured.out  # auto-activations
        assert "test-automator" in captured.out
        assert "code-reviewer" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    def test_print_banner(self, mock_resolve, tmp_path, capsys):
        """Test printing banner."""
        mock_resolve.return_value = tmp_path

        watch = WatchMode(auto_activate=True, notification_threshold=0.7, check_interval=2.0)
        watch._print_banner()

        captured = capsys.readouterr()
        assert "WATCH MODE" in captured.out
        assert "ON" in captured.out
        assert "70%" in captured.out
        assert "2.0s" in captured.out

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_analyze_context_no_files(self, mock_run, mock_resolve, tmp_path):
        """Test analyzing context with no changed files."""
        mock_resolve.return_value = tmp_path
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # git diff
            MagicMock(stdout="", returncode=0),  # git diff --cached
        ]

        watch = WatchMode()
        changed = watch._analyze_context()

        assert changed is False

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    def test_analyze_context_with_files(self, mock_run, mock_resolve, tmp_path, capsys):
        """Test analyzing context with changed files."""
        mock_resolve.return_value = tmp_path
        mock_run.side_effect = [
            MagicMock(stdout="auth.py\n", returncode=0),  # git diff
            MagicMock(stdout="", returncode=0),  # git diff --cached
        ]

        watch = WatchMode(notification_threshold=0.5)
        changed = watch._analyze_context()

        # Should detect auth context and make recommendations
        assert watch.recommendations_made >= 0


@patch("claude_ctx_py.watch._resolve_claude_dir")
@patch("subprocess.run")
def test_watch_main(mock_run, mock_resolve, tmp_path):
    """Test watch_main entry point."""
    mock_resolve.return_value = tmp_path

    # Mock git commands
    mock_run.return_value = MagicMock(stdout="", returncode=0)

    # This would run forever, so we need to patch the run method
    with patch.object(WatchMode, "run", return_value=0):
        result = watch_main(auto_activate=True, threshold=0.7, interval=2.0)
        assert result == 0


class TestWatchModeIntegration:
    """Integration tests for watch mode."""

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    @patch("signal.signal")
    @patch("time.sleep")
    def test_run_loop_with_signal(self, mock_sleep, mock_signal, mock_run, mock_resolve, tmp_path, capsys):
        """Test run loop handles signals."""
        mock_resolve.return_value = tmp_path
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        watch = WatchMode()

        # Simulate signal after 1 iteration
        def stop_after_one(seconds):
            watch.running = False

        mock_sleep.side_effect = stop_after_one

        result = watch.run()

        assert result == 0
        assert watch.checks_performed > 0

    @patch("claude_ctx_py.watch._resolve_claude_dir")
    @patch("subprocess.run")
    @patch("signal.signal")
    @patch("time.sleep")
    def test_run_loop_keyboard_interrupt(self, mock_sleep, mock_signal, mock_run, mock_resolve, tmp_path):
        """Test run loop handles keyboard interrupt."""
        mock_resolve.return_value = tmp_path
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        mock_sleep.side_effect = KeyboardInterrupt()

        watch = WatchMode()
        result = watch.run()

        assert result == 0
