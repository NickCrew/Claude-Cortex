"""Tests for claude_ctx_py/wizard.py

Tests cover:
- should_run_wizard detection logic
- run_wizard_non_interactive execution
- _symlink_rules utility
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from claude_ctx_py.wizard import (
    should_run_wizard,
    run_wizard_non_interactive,
    _symlink_rules,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_home(tmp_path):
    """Create a mock home directory."""
    return tmp_path


@pytest.fixture
def mock_claude_rules_dir(mock_home):
    """Return path to mock claude rules directory."""
    return mock_home / ".claude" / "rules" / "cortex"


# =============================================================================
# should_run_wizard tests
# =============================================================================


class TestShouldRunWizard:
    """Tests for should_run_wizard function."""

    def test_returns_false_when_skip_env_set(self):
        """Should return False when CORTEX_SKIP_WIZARD is set."""
        with patch.dict(os.environ, {"CORTEX_SKIP_WIZARD": "1"}):
            assert should_run_wizard() is False

    def test_returns_false_when_not_tty(self):
        """Should return False when stdin is not a TTY."""
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            with patch.dict(os.environ, {}, clear=True):
                # Also need to patch home to control the rules check
                with patch("pathlib.Path.home") as mock_home:
                    mock_path = MagicMock()
                    mock_path.__truediv__ = MagicMock(return_value=mock_path)
                    mock_path.exists.return_value = False
                    mock_home.return_value = mock_path
                    assert should_run_wizard() is False

    def test_returns_false_when_rules_exist(self, mock_home, mock_claude_rules_dir):
        """Should return False when cortex rules already exist."""
        mock_claude_rules_dir.mkdir(parents=True)

        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = True
                with patch("pathlib.Path.home", return_value=mock_home):
                    assert should_run_wizard() is False

    def test_returns_true_when_rules_missing(self, mock_home):
        """Should return True when cortex rules don't exist."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("sys.stdin") as mock_stdin:
                mock_stdin.isatty.return_value = True
                with patch("pathlib.Path.home", return_value=mock_home):
                    assert should_run_wizard() is True


# =============================================================================
# _symlink_rules tests
# =============================================================================


class TestSymlinkRules:
    """Tests for _symlink_rules utility."""

    def test_dry_run_returns_message(self, tmp_path):
        """Dry run should not create symlink."""
        mock_console = MagicMock()

        with patch("claude_ctx_py.wizard._resolve_cortex_root", return_value=tmp_path):
            # Create source rules dir
            rules_dir = tmp_path / "rules"
            rules_dir.mkdir()

            code, msg = _symlink_rules(mock_console, dry_run=True)

            assert code == 0
            assert "Would symlink" in msg

    def test_fails_when_rules_missing(self, tmp_path):
        """Should fail when source rules directory doesn't exist."""
        mock_console = MagicMock()

        with patch("claude_ctx_py.wizard._resolve_cortex_root", return_value=tmp_path):
            code, msg = _symlink_rules(mock_console)

            assert code == 1
            assert "not found" in msg


# =============================================================================
# run_wizard_non_interactive tests
# =============================================================================


class TestRunWizardNonInteractive:
    """Tests for run_wizard_non_interactive function."""

    def test_calls_symlink_rules(self, tmp_path):
        """Non-interactive wizard should call _symlink_rules."""
        with patch("claude_ctx_py.wizard._symlink_rules") as mock_symlink:
            mock_symlink.return_value = (0, "success")

            code, msg = run_wizard_non_interactive()

            mock_symlink.assert_called_once()
            assert code == 0
