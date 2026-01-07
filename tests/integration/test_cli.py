"""Integration tests for CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from claude_ctx_py import cli


@pytest.mark.integration
class TestCLIParser:
    """Tests for CLI argument parsing."""

    def test_build_parser(self) -> None:
        """Test that parser is built successfully."""
        parser = cli.build_parser()

        assert parser is not None
        assert parser.prog == "cortex"

    def test_parser_help(self) -> None:
        """Test parser help output."""
        parser = cli.build_parser()
        
        # This should not raise
        help_text = parser.format_help()
        assert "cortex" in help_text


@pytest.mark.integration
class TestModeCommands:
    """Tests for mode-related CLI commands."""

    def test_mode_list_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing modes when none exist."""
        # Change to a directory that would use our mock claude dir
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["mode", "list"])
        
        # Should complete successfully even with no modes
        assert result == 0

    def test_mode_status_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test mode status when no modes are active."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["mode", "status"])
        
        assert result == 0


@pytest.mark.integration
class TestAgentCommands:
    """Tests for agent-related CLI commands."""

    def test_agent_list_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing agents when none exist."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["agent", "list"])
        
        assert result == 0

    def test_agent_status_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test agent status when no agents are active."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["agent", "status"])
        
        assert result == 0


@pytest.mark.integration
class TestSkillCommands:
    """Tests for skill-related CLI commands."""

    def test_skill_list_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing skills when none exist."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["skills", "list"])
        
        assert result == 0

    def test_skill_metrics_empty(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test skill metrics when no metrics exist."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["skills", "metrics"])
        
        assert result == 0

    def test_skill_metrics_with_data(
        self, tmp_claude_dir: Path, mock_claude_home: Path, metrics_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test skill metrics with actual metrics data."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["skills", "metrics"])
        
        assert result == 0

    def test_skill_metrics_reset(
        self, tmp_claude_dir: Path, mock_claude_home: Path, metrics_file: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test resetting skill metrics."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        # Verify file exists
        assert metrics_file.exists()
        
        result = cli.main(["skills", "metrics", "--reset"])
        
        assert result == 0
        # File should be deleted
        assert not metrics_file.exists()


@pytest.mark.integration
class TestProfileCommands:
    """Tests for profile-related CLI commands."""

    def test_profile_list(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing profiles."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["profile", "list"])
        
        assert result == 0


@pytest.mark.integration
class TestStatusCommand:
    """Tests for overall status command."""

    def test_status_command(
        self, tmp_claude_dir: Path, mock_claude_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test overall status command."""
        monkeypatch.chdir(tmp_claude_dir.parent)
        
        result = cli.main(["status"])
        
        assert result == 0


@pytest.mark.integration
class TestInvalidCommands:
    """Tests for invalid command handling."""

    def test_no_command(self) -> None:
        """Test running with no command."""
        result = cli.main([])
        
        # Should show help and return 1
        assert result == 1

    def test_invalid_command(self) -> None:
        """Test running with invalid command."""
        # argparse raises SystemExit for invalid commands
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["invalid-command"])

        # Should exit with error code 2 (argparse convention)
        assert exc_info.value.code == 2


@pytest.mark.integration
class TestMainFunction:
    """Tests for main() function behavior."""

    def test_main_with_argv_list(self) -> None:
        """Test main function with argv as list."""
        result = cli.main(["status"])
        
        # Should not raise and return an integer
        assert isinstance(result, int)

    def test_main_with_argv_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test main function with argv as None (uses sys.argv)."""
        # Mock sys.argv
        import sys
        monkeypatch.setattr(sys, "argv", ["cortex", "status"])
        
        result = cli.main(None)
        
        assert isinstance(result, int)
