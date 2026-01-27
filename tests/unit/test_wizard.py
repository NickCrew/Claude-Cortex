"""Comprehensive tests for claude_ctx_py/wizard.py

Tests cover:
- should_run_wizard detection logic
- WizardConfig defaults
- ExperienceLevel enum
- OnboardingState persistence
- Non-interactive wizard execution
- CLI skip flag integration
"""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from claude_ctx_py.wizard import (
    ExperienceLevel,
    OnboardingState,
    WizardConfig,
    should_run_wizard,
    run_wizard_non_interactive,
    _load_onboarding_state,
    _save_onboarding_state,
    _get_onboarding_state_path,
    _map_detection_to_profile,
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

    def test_should_run_when_config_not_exists(self, mock_cortex_root):
        """Wizard should run when cortex-config.json doesn't exist."""
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            # Clear skip env var if set
            with patch.dict(os.environ, {}, clear=True):
                # Mock stdin.isatty() to return True (interactive)
                with patch("sys.stdin.isatty", return_value=True):
                    assert should_run_wizard() is True

    def test_should_not_run_when_config_exists(self, existing_cortex_root):
        """Wizard should not run when cortex-config.json exists."""
        # Create the config file to simulate bootstrapped state
        config_file = existing_cortex_root / "cortex-config.json"
        config_file.write_text("{}")
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=existing_cortex_root
        ):
            with patch.dict(os.environ, {}, clear=True):
                with patch("sys.stdin.isatty", return_value=True):
                    assert should_run_wizard() is False

    def test_should_run_when_only_logs_dir_exists(self, mock_cortex_root):
        """Wizard should run even if ~/.cortex/logs exists (from hooks)."""
        # Create just the logs directory (simulating hook behavior)
        mock_cortex_root.mkdir(parents=True, exist_ok=True)
        (mock_cortex_root / "logs").mkdir()
        with patch(
            "claude_ctx_py.wizard._resolve_cortex_root", return_value=mock_cortex_root
        ):
            with patch.dict(os.environ, {}, clear=True):
                with patch("sys.stdin.isatty", return_value=True):
                    # Should still run because cortex-config.json doesn't exist
                    assert should_run_wizard() is True

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
    """Tests for interactive wizard flow with mocked prompts.

    Note: These tests mock the new wizard flow which starts with experience level
    selection, followed by welcome, project detection, profile selection, etc.
    """

    def test_wizard_cancelled_at_welcome(self):
        """Wizard should exit cleanly when cancelled at welcome."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard, ExperienceLevel

        console = Console(force_terminal=True, no_color=True)

        with patch(
            "claude_ctx_py.wizard._get_experience_level",
            return_value=ExperienceLevel.NEW,
        ):
            with patch("claude_ctx_py.wizard._show_welcome", return_value=False):
                exit_code, message = run_wizard(console)

                assert exit_code == 1
                assert "cancelled" in message.lower()

    def test_wizard_cancelled_at_summary(self, mock_cortex_root, tmp_path):
        """Wizard should exit cleanly when cancelled at summary."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard, ExperienceLevel

        console = Console(force_terminal=True, no_color=True)
        mock_rc = tmp_path / ".zshrc"
        mock_rc.write_text("# zshrc")

        with patch(
            "claude_ctx_py.wizard._get_experience_level",
            return_value=ExperienceLevel.EXPERIENCED,
        ):
            with patch("claude_ctx_py.wizard._show_welcome", return_value=True):
                with patch(
                    "claude_ctx_py.wizard._get_target_directory",
                    return_value=mock_cortex_root,
                ):
                    with patch(
                        "claude_ctx_py.wizard._detect_project_and_recommend",
                        return_value=({}, "minimal"),
                    ):
                        with patch(
                            "claude_ctx_py.wizard._get_profile_selection",
                            return_value="minimal",
                        ):
                            with patch(
                                "claude_ctx_py.wizard._get_shell_config",
                                return_value=("zsh", mock_rc, True, True),
                            ):
                                with patch(
                                    "claude_ctx_py.wizard._get_rule_linking_config",
                                    return_value=True,
                                ):
                                    with patch(
                                        "claude_ctx_py.wizard._setup_claude_integration",
                                        return_value=(True, [], True, True),
                                    ):
                                        with patch(
                                            "claude_ctx_py.wizard._prompt_post_setup_action",
                                            return_value="none",
                                        ):
                                            with patch(
                                                "claude_ctx_py.wizard._show_summary",
                                                return_value=False,
                                            ):
                                                exit_code, message = run_wizard(console)

                                                assert exit_code == 1
                                                assert "cancelled" in message.lower()

    def test_wizard_handles_keyboard_interrupt(self):
        """Wizard should handle Ctrl+C gracefully."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard

        console = Console(force_terminal=True, no_color=True)

        with patch(
            "claude_ctx_py.wizard._get_experience_level",
            side_effect=KeyboardInterrupt,
        ):
            exit_code, message = run_wizard(console)

            assert exit_code == 1
            assert "cancelled" in message.lower()

    def test_wizard_handles_permission_error(self, mock_cortex_root):
        """Wizard should handle permission errors gracefully."""
        from rich.console import Console
        from claude_ctx_py.wizard import run_wizard, ExperienceLevel

        console = Console(force_terminal=True, no_color=True)

        with patch(
            "claude_ctx_py.wizard._get_experience_level",
            return_value=ExperienceLevel.EXPERIENCED,
        ):
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
        from claude_ctx_py.wizard import run_wizard, ExperienceLevel

        console = Console(force_terminal=True, no_color=True)
        mock_rc = tmp_path / ".zshrc"
        mock_rc.write_text("# zshrc")

        with patch(
            "claude_ctx_py.wizard._get_experience_level",
            return_value=ExperienceLevel.EXPERIENCED,
        ):
            with patch("claude_ctx_py.wizard._show_welcome", return_value=True):
                with patch(
                    "claude_ctx_py.wizard._get_target_directory",
                    return_value=mock_cortex_root,
                ):
                    with patch(
                        "claude_ctx_py.wizard._detect_project_and_recommend",
                        return_value=({}, "minimal"),
                    ):
                        with patch(
                            "claude_ctx_py.wizard._get_profile_selection",
                            return_value="minimal",
                        ):
                            with patch(
                                "claude_ctx_py.wizard._get_shell_config",
                                return_value=("zsh", mock_rc, False, False),
                            ):
                                with patch(
                                    "claude_ctx_py.wizard._get_rule_linking_config",
                                    return_value=False,
                                ):
                                    with patch(
                                        "claude_ctx_py.wizard._setup_claude_integration",
                                        return_value=(False, [], False, False),
                                    ):
                                        with patch(
                                            "claude_ctx_py.wizard._prompt_post_setup_action",
                                            return_value="none",
                                        ):
                                            with patch(
                                                "claude_ctx_py.wizard._show_summary",
                                                return_value=True,
                                            ):
                                                with patch(
                                                    "claude_ctx_py.wizard.installer.bootstrap",
                                                    return_value=(0, "* Bootstrap complete"),
                                                ):
                                                    with patch(
                                                        "claude_ctx_py.wizard._save_onboarding_state",
                                                        return_value=True,
                                                    ):
                                                        exit_code, message = run_wizard(
                                                            console
                                                        )

                                                        assert exit_code == 0
                                                        assert "success" in message.lower()


# =============================================================================
# Tests: ExperienceLevel enum
# =============================================================================


class TestExperienceLevel:
    """Tests for ExperienceLevel enum."""

    def test_values(self):
        """ExperienceLevel should have expected values."""
        assert ExperienceLevel.NEW.value == "new"
        assert ExperienceLevel.EXPERIENCED.value == "experienced"
        assert ExperienceLevel.POWER_USER.value == "power_user"

    def test_all_members(self):
        """ExperienceLevel should have exactly 3 members."""
        assert len(ExperienceLevel) == 3


# =============================================================================
# Tests: OnboardingState
# =============================================================================


class TestOnboardingState:
    """Tests for OnboardingState dataclass."""

    def test_default_values(self):
        """OnboardingState should have sensible defaults."""
        state = OnboardingState()

        assert state.completed_at is None
        assert state.experience_level == "new"
        assert state.profile_applied == "minimal"
        assert state.tui_tour_shown is False
        assert state.version == "1.0"

    def test_to_dict(self):
        """OnboardingState.to_dict should serialize correctly."""
        state = OnboardingState(
            completed_at="2024-01-01T00:00:00Z",
            experience_level="experienced",
            profile_applied="frontend",
            tui_tour_shown=True,
            version="1.0",
        )
        result = state.to_dict()

        assert result["completed_at"] == "2024-01-01T00:00:00Z"
        assert result["experience_level"] == "experienced"
        assert result["profile_applied"] == "frontend"
        assert result["tui_tour_shown"] is True
        assert result["version"] == "1.0"

    def test_from_dict(self):
        """OnboardingState.from_dict should deserialize correctly."""
        data = {
            "completed_at": "2024-01-01T00:00:00Z",
            "experience_level": "power_user",
            "profile_applied": "backend",
            "tui_tour_shown": True,
            "version": "1.0",
        }
        state = OnboardingState.from_dict(data)

        assert state.completed_at == "2024-01-01T00:00:00Z"
        assert state.experience_level == "power_user"
        assert state.profile_applied == "backend"
        assert state.tui_tour_shown is True

    def test_from_dict_with_missing_keys(self):
        """OnboardingState.from_dict should handle missing keys."""
        data = {}  # type: ignore
        state = OnboardingState.from_dict(data)

        assert state.completed_at is None
        assert state.experience_level == "new"
        assert state.profile_applied == "minimal"


# =============================================================================
# Tests: Onboarding State Persistence
# =============================================================================


class TestOnboardingStatePersistence:
    """Tests for onboarding state load/save functions."""

    def test_load_returns_none_when_file_missing(self, tmp_path):
        """_load_onboarding_state should return None when file doesn't exist."""
        with patch(
            "claude_ctx_py.wizard._get_onboarding_state_path",
            return_value=tmp_path / ".onboarding-state.json",
        ):
            result = _load_onboarding_state()
            assert result is None

    def test_load_returns_state_when_file_exists(self, tmp_path):
        """_load_onboarding_state should return OnboardingState when file exists."""
        state_path = tmp_path / ".onboarding-state.json"
        state_data = {
            "completed_at": "2024-01-01T00:00:00Z",
            "experience_level": "experienced",
            "profile_applied": "frontend",
            "tui_tour_shown": True,
            "version": "1.0",
        }
        state_path.write_text(json.dumps(state_data))

        with patch(
            "claude_ctx_py.wizard._get_onboarding_state_path",
            return_value=state_path,
        ):
            result = _load_onboarding_state()

            assert result is not None
            assert result.completed_at == "2024-01-01T00:00:00Z"
            assert result.experience_level == "experienced"

    def test_load_returns_none_on_invalid_json(self, tmp_path):
        """_load_onboarding_state should return None on invalid JSON."""
        state_path = tmp_path / ".onboarding-state.json"
        state_path.write_text("not valid json")

        with patch(
            "claude_ctx_py.wizard._get_onboarding_state_path",
            return_value=state_path,
        ):
            result = _load_onboarding_state()
            assert result is None

    def test_save_creates_file(self, tmp_path):
        """_save_onboarding_state should create state file."""
        state_path = tmp_path / ".onboarding-state.json"
        config = WizardConfig(
            experience_level=ExperienceLevel.EXPERIENCED,
            selected_profile="frontend",
        )

        with patch(
            "claude_ctx_py.wizard._get_onboarding_state_path",
            return_value=state_path,
        ):
            result = _save_onboarding_state(config)

            assert result is True
            assert state_path.exists()

            data = json.loads(state_path.read_text())
            assert data["experience_level"] == "experienced"
            assert data["profile_applied"] == "frontend"


# =============================================================================
# Tests: Profile Mapping
# =============================================================================


class TestProfileMapping:
    """Tests for _map_detection_to_profile function."""

    def test_react_maps_to_frontend(self):
        """React framework should map to frontend profile."""
        detection = {"language": "javascript", "framework": "react", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "frontend"

    def test_vue_maps_to_frontend(self):
        """Vue framework should map to frontend profile."""
        detection = {"language": "javascript", "framework": "vue", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "frontend"

    def test_nextjs_maps_to_frontend(self):
        """Next.js framework should map to frontend profile."""
        detection = {"language": "javascript", "framework": "nextjs", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "frontend"

    def test_django_maps_to_backend(self):
        """Django framework should map to backend profile."""
        detection = {"language": "python", "framework": "django", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_flask_maps_to_backend(self):
        """Flask framework should map to backend profile."""
        detection = {"language": "python", "framework": "flask", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_express_maps_to_backend(self):
        """Express framework should map to backend profile."""
        detection = {"language": "javascript", "framework": "express", "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_terraform_maps_to_devops(self):
        """Terraform infrastructure should map to devops profile."""
        detection = {"language": None, "framework": None, "infrastructure": "terraform", "types": []}
        assert _map_detection_to_profile(detection) == "devops"

    def test_docker_compose_maps_to_devops(self):
        """Docker Compose infrastructure should map to devops profile."""
        detection = {"language": None, "framework": None, "infrastructure": "docker-compose", "types": []}
        assert _map_detection_to_profile(detection) == "devops"

    def test_python_maps_to_backend(self):
        """Plain Python should map to backend profile."""
        detection = {"language": "python", "framework": None, "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_typescript_maps_to_frontend(self):
        """Plain TypeScript should map to frontend profile."""
        detection = {"language": "typescript", "framework": None, "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "frontend"

    def test_go_maps_to_backend(self):
        """Go language should map to backend profile."""
        detection = {"language": "go", "framework": None, "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_rust_maps_to_backend(self):
        """Rust language should map to backend profile."""
        detection = {"language": "rust", "framework": None, "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "backend"

    def test_unknown_maps_to_minimal(self):
        """Unknown detection should map to minimal profile."""
        detection = {"language": None, "framework": None, "infrastructure": None, "types": []}
        assert _map_detection_to_profile(detection) == "minimal"


# =============================================================================
# Tests: Enhanced WizardConfig
# =============================================================================


class TestEnhancedWizardConfig:
    """Tests for new WizardConfig fields."""

    def test_new_default_values(self):
        """WizardConfig should have new default values."""
        config = WizardConfig()

        assert config.experience_level == ExperienceLevel.NEW
        assert config.detected_language is None
        assert config.detected_framework is None
        assert config.recommended_profile == "minimal"
        assert config.selected_profile == "minimal"
        assert config.setup_mcp is True
        assert config.setup_hooks is True
        assert config.configure_settings is True
        assert config.post_setup_action == "none"

    def test_custom_experience_level(self):
        """WizardConfig should accept custom experience level."""
        config = WizardConfig(experience_level=ExperienceLevel.POWER_USER)
        assert config.experience_level == ExperienceLevel.POWER_USER

    def test_custom_profile_selection(self):
        """WizardConfig should accept custom profile selection."""
        config = WizardConfig(
            recommended_profile="frontend",
            selected_profile="backend",
        )
        assert config.recommended_profile == "frontend"
        assert config.selected_profile == "backend"
