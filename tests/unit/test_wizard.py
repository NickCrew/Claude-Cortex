"""Comprehensive tests for claude_ctx_py/wizard.py

Tests cover:
- should_run_wizard detection logic
- WizardConfig defaults
- Non-interactive wizard execution
- CLI skip flag integration
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from claude_ctx_py.wizard import (
    WizardConfig,
    should_run_wizard,
    run_wizard_non_interactive,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_home(tmp_path):
    """Create a mock home directory."""
    return tmp_path


@pytest.fixture
def mock_cortex_root(mock_home):
    """Return path to mock cortex root (doesn't exist by default)."""
    return mock_home / ".cortex"


@pytest.fixture
def existing_cortex_root(mock_cortex_root):
    """Create an existing cortex root directory."""
    mock_cortex_root.mkdir(parents=True, exist_ok=True)
    return mock_cortex_root


# =============================================================================
# Tests: should_run_wizard
# =============================================================================


class TestShouldRunWizard:
    """Tests for should_run_wizard() detection logic."""

    def test_should_run_when_cortex_not_exists(self, mock_cortex_root):
        """Wizard should run when ~/.cortex doesn't exist."""
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            # Clear skip env var if set
            with patch.dict(os.environ, {}, clear=True):
                # Mock stdin.isatty() to return True (interactive)
                with patch("sys.stdin.isatty", return_value=True):
                    assert should_run_wizard() is True

    def test_should_not_run_when_cortex_exists(self, existing_cortex_root):
        """Wizard should not run when ~/.cortex exists."""
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=existing_cortex_root
        ):
            with patch.dict(os.environ, {}, clear=True):
                with patch("sys.stdin.isatty", return_value=True):
                    assert should_run_wizard() is False

    def test_should_not_run_with_skip_env_var(self, mock_cortex_root):
        """Wizard should not run when CORTEX_SKIP_WIZARD is set."""
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            with patch.dict(os.environ, {"CORTEX_SKIP_WIZARD": "1"}):
                with patch("sys.stdin.isatty", return_value=True):
                    assert should_run_wizard() is False

    def test_should_not_run_in_non_interactive(self, mock_cortex_root):
        """Wizard should not run when stdin is not a TTY (CI, pipes)."""
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            with patch.dict(os.environ, {}, clear=True):
                # Mock stdin.isatty() to return False (non-interactive)
                with patch("sys.stdin.isatty", return_value=False):
                    assert should_run_wizard() is False


# =============================================================================
# Tests: WizardConfig
# =============================================================================


class TestWizardConfig:
    """Tests for WizardConfig dataclass."""

    def test_default_values(self):
        """Config should have sensible defaults."""
        # The target_dir uses _resolve_cortex_root() which returns ~/.cortex by default
        # We just check it resolves to a Path ending in .cortex
        config = WizardConfig()

        assert config.target_dir.name == ".cortex"
        assert config.install_completions is True
        assert config.install_aliases is True
        assert config.link_rules is True
        assert config.detected_shell == ""
        assert config.shell_rc_path is None

    def test_custom_values(self, mock_home):
        """Config should accept custom values."""
        custom_path = mock_home / "custom_cortex"
        rc_path = mock_home / ".zshrc"

        config = WizardConfig(
            target_dir=custom_path,
            install_completions=False,
            install_aliases=False,
            link_rules=False,
            detected_shell="zsh",
            shell_rc_path=rc_path,
        )

        assert config.target_dir == custom_path
        assert config.install_completions is False
        assert config.install_aliases is False
        assert config.link_rules is False
        assert config.detected_shell == "zsh"
        assert config.shell_rc_path == rc_path


# =============================================================================
# Tests: run_wizard_non_interactive
# =============================================================================


class TestRunWizardNonInteractive:
    """Tests for non-interactive wizard execution."""

    def test_non_interactive_calls_bootstrap(self, mock_cortex_root):
        """Non-interactive wizard should call bootstrap with correct args."""
        with patch("claude_ctx_py.wizard.installer.bootstrap") as mock_bootstrap:
            mock_bootstrap.return_value = (0, "Success")

            exit_code, message = run_wizard_non_interactive(
                target_dir=mock_cortex_root,
                link_rules=True,
            )

            mock_bootstrap.assert_called_once_with(
                target_dir=mock_cortex_root,
                force=False,
                dry_run=False,
                link_rules=True,
            )
            assert exit_code == 0
            assert message == "Success"

    def test_non_interactive_with_defaults(self):
        """Non-interactive wizard should work with defaults."""
        with patch("claude_ctx_py.wizard.installer.bootstrap") as mock_bootstrap:
            mock_bootstrap.return_value = (0, "Success")

            exit_code, _ = run_wizard_non_interactive()

            mock_bootstrap.assert_called_once_with(
                target_dir=None,
                force=False,
                dry_run=False,
                link_rules=True,
            )
            assert exit_code == 0

    def test_non_interactive_propagates_errors(self, mock_cortex_root):
        """Non-interactive wizard should propagate bootstrap errors."""
        with patch("claude_ctx_py.wizard.installer.bootstrap") as mock_bootstrap:
            mock_bootstrap.return_value = (1, "Permission denied")

            exit_code, message = run_wizard_non_interactive(
                target_dir=mock_cortex_root,
            )

            assert exit_code == 1
            assert "Permission denied" in message


# =============================================================================
# Tests: CLI Integration (skip flag)
# =============================================================================


class TestCLIIntegration:
    """Tests for CLI integration with --skip-wizard flag."""

    def test_skip_wizard_flag_prevents_wizard(self, mock_cortex_root):
        """--skip-wizard flag should prevent wizard from running."""
        from claude_ctx_py.cli import main

        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            with patch("claude_ctx_py.wizard.run_wizard") as mock_wizard:
                with patch("sys.stdin.isatty", return_value=True):
                    # Run with --skip-wizard flag
                    main(["--skip-wizard", "status"])

                    # Wizard should not have been called
                    mock_wizard.assert_not_called()

    def test_no_init_alias_prevents_wizard(self, mock_cortex_root):
        """--no-init alias should also prevent wizard from running."""
        from claude_ctx_py.cli import main

        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            with patch("claude_ctx_py.wizard.run_wizard") as mock_wizard:
                with patch("sys.stdin.isatty", return_value=True):
                    # Run with --no-init alias
                    main(["--no-init", "status"])

                    # Wizard should not have been called
                    mock_wizard.assert_not_called()


# =============================================================================
# Tests: Interactive Wizard (mocked)
# =============================================================================


class TestInteractiveWizard:
    """Tests for interactive wizard flow with mocked prompts."""

    def test_wizard_cancelled_at_welcome(self):
        """Wizard should exit cleanly when cancelled at welcome."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)

        with patch("claude_ctx_py.wizard._show_welcome", return_value=False):
            exit_code, message = run_wizard(console)

            assert exit_code == 1
            assert "cancelled" in message.lower()

    def test_wizard_cancelled_at_summary(self, mock_cortex_root):
        """Wizard should exit cleanly when cancelled at summary."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)

        with patch("claude_ctx_py.wizard._show_welcome", return_value=True):
            with patch(
                "claude_ctx_py.wizard._get_target_directory", return_value=mock_cortex_root
            ):
                with patch(
                    "claude_ctx_py.wizard._get_shell_config",
                    return_value=("zsh", Path.home() / ".zshrc", True, True),
                ):
                    with patch("claude_ctx_py.wizard._get_rule_linking_config", return_value=True):
                        with patch("claude_ctx_py.wizard._show_summary", return_value=False):
                            exit_code, message = run_wizard(console)

                            assert exit_code == 1
                            assert "cancelled" in message.lower()

    def test_wizard_handles_keyboard_interrupt(self):
        """Wizard should handle Ctrl+C gracefully."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)

        with patch("claude_ctx_py.wizard._show_welcome", side_effect=KeyboardInterrupt):
            exit_code, message = run_wizard(console)

            assert exit_code == 1
            assert "cancelled" in message.lower()

    def test_wizard_handles_permission_error(self, mock_cortex_root):
        """Wizard should handle permission errors gracefully."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)

        with patch("claude_ctx_py.wizard._show_welcome", return_value=True):
            with patch(
                "claude_ctx_py.wizard._get_target_directory",
                side_effect=PermissionError("/forbidden"),
            ):
                exit_code, message = run_wizard(console)

                assert exit_code == 1
                assert "permission" in message.lower()

    def test_wizard_successful_flow(self, mock_cortex_root, tmp_path):
        """Wizard should complete successfully with all steps."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)
        mock_rc = tmp_path / ".zshrc"
        mock_rc.write_text("# zshrc")

        with patch("claude_ctx_py.wizard._show_welcome", return_value=True):
            with patch(
                "claude_ctx_py.wizard._get_target_directory", return_value=mock_cortex_root
            ):
                with patch(
                    "claude_ctx_py.wizard._get_shell_config",
                    return_value=("zsh", mock_rc, False, False),  # Disable shell integration
                ):
                    with patch("claude_ctx_py.wizard._get_rule_linking_config", return_value=False):
                        with patch("claude_ctx_py.wizard._show_summary", return_value=True):
                            with patch(
                                "claude_ctx_py.wizard.installer.bootstrap",
                                return_value=(0, "✓ Bootstrap complete"),
                            ):
                                exit_code, message = run_wizard(console)

                                assert exit_code == 0
                                assert "success" in message.lower()
