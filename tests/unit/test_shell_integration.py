"""Comprehensive tests for claude_ctx_py/shell_integration.py

Tests cover:
- Shell detection for bash, zsh, fish
- RC file path resolution for each shell
- Alias content generation
- install_aliases with various scenarios
- uninstall_aliases with various scenarios
- Edge cases: missing RC files, force reinstall, dry run
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.shell_integration import (
    BASH_ZSH_ALIASES,
    FISH_FUNCTIONS,
    MARKER_END,
    MARKER_START,
    check_aliases_installed,
    detect_shell,
    get_aliases_content,
    install_aliases,
    show_aliases,
    uninstall_aliases,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_home_dir(tmp_path):
    """Create a mock home directory."""
    return tmp_path


@pytest.fixture
def mock_bashrc(mock_home_dir):
    """Create a mock .bashrc file."""
    bashrc = mock_home_dir / ".bashrc"
    bashrc.write_text("# Existing bashrc content\nexport PATH=$PATH:/usr/local/bin\n")
    return bashrc


@pytest.fixture
def mock_zshrc(mock_home_dir):
    """Create a mock .zshrc file."""
    zshrc = mock_home_dir / ".zshrc"
    zshrc.write_text("# Existing zshrc content\nexport ZSH=$HOME/.oh-my-zsh\n")
    return zshrc


@pytest.fixture
def mock_fish_config(mock_home_dir):
    """Create a mock fish config file."""
    fish_dir = mock_home_dir / ".config" / "fish"
    fish_dir.mkdir(parents=True, exist_ok=True)
    fish_config = fish_dir / "config.fish"
    fish_config.write_text("# Existing fish config\nset -x PATH $PATH /usr/local/bin\n")
    return fish_config


@pytest.fixture
def bashrc_with_aliases(mock_home_dir):
    """Create bashrc with existing aliases."""
    bashrc = mock_home_dir / ".bashrc"
    content = f"""# Existing content
export PATH=$PATH:/usr/local/bin

{MARKER_START}
alias ctx='cortex export context -'
{MARKER_END}

# More content
export EDITOR=vim
"""
    bashrc.write_text(content)
    return bashrc


# =============================================================================
# Tests for detect_shell
# =============================================================================


class TestDetectShell:
    """Tests for detect_shell function."""

    def test_detect_bash_from_env(self, mock_home_dir, mock_bashrc):
        """Test detection of bash shell."""
        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                shell, rc_file = detect_shell()

        assert shell == "bash"
        assert rc_file.name == ".bashrc"

    def test_detect_zsh_from_env(self, mock_home_dir, mock_zshrc):
        """Test detection of zsh shell."""
        with patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                shell, rc_file = detect_shell()

        assert shell == "zsh"
        assert rc_file.name == ".zshrc"

    def test_detect_fish_from_env(self, mock_home_dir, mock_fish_config):
        """Test detection of fish shell."""
        with patch.dict(os.environ, {"SHELL": "/usr/bin/fish"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                shell, rc_file = detect_shell()

        assert shell == "fish"
        assert rc_file.name == "config.fish"

    def test_detect_bash_prefers_bashrc(self, mock_home_dir):
        """Test that bash prefers .bashrc over .bash_profile."""
        bashrc = mock_home_dir / ".bashrc"
        bash_profile = mock_home_dir / ".bash_profile"
        bashrc.write_text("# bashrc")
        bash_profile.write_text("# bash_profile")

        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                shell, rc_file = detect_shell()

        assert rc_file.name == ".bashrc"

    def test_detect_fallback_to_existing_rc(self, mock_home_dir, mock_zshrc):
        """Test fallback to existing RC file when shell unknown."""
        with patch.dict(os.environ, {"SHELL": "/bin/unknown"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                shell, rc_file = detect_shell()

        assert shell == "zsh"
        assert rc_file.name == ".zshrc"

    def test_detect_raises_when_no_shell(self, mock_home_dir):
        """Test that RuntimeError is raised when no shell found."""
        with patch.dict(os.environ, {"SHELL": "/bin/unknown"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                with pytest.raises(RuntimeError):
                    detect_shell()


# =============================================================================
# Tests for get_aliases_content
# =============================================================================


class TestGetAliasesContent:
    """Tests for get_aliases_content function."""

    def test_bash_content(self):
        """Test bash/zsh aliases content."""
        content = get_aliases_content("bash")
        assert MARKER_START in content
        assert MARKER_END in content
        assert BASH_ZSH_ALIASES in content

    def test_zsh_content(self):
        """Test zsh content (same as bash)."""
        content = get_aliases_content("zsh")
        assert MARKER_START in content
        assert MARKER_END in content
        assert BASH_ZSH_ALIASES in content

    def test_fish_content(self):
        """Test fish functions content."""
        content = get_aliases_content("fish")
        assert MARKER_START in content
        assert MARKER_END in content
        assert FISH_FUNCTIONS in content

    def test_unsupported_shell_raises(self):
        """Test that unsupported shell raises ValueError."""
        with pytest.raises(ValueError):
            get_aliases_content("powershell")

    def test_case_insensitive(self):
        """Test shell name is case insensitive."""
        content1 = get_aliases_content("BASH")
        content2 = get_aliases_content("bash")
        assert content1 == content2


# =============================================================================
# Tests for check_aliases_installed
# =============================================================================


class TestCheckAliasesInstalled:
    """Tests for check_aliases_installed function."""

    def test_not_installed(self, mock_bashrc):
        """Test when aliases are not installed."""
        assert check_aliases_installed(mock_bashrc) is False

    def test_installed(self, bashrc_with_aliases):
        """Test when aliases are installed."""
        assert check_aliases_installed(bashrc_with_aliases) is True

    def test_file_not_exists(self, mock_home_dir):
        """Test when RC file doesn't exist."""
        missing = mock_home_dir / ".bashrc"
        assert check_aliases_installed(missing) is False


# =============================================================================
# Tests for install_aliases
# =============================================================================


class TestInstallAliases:
    """Tests for install_aliases function."""

    def test_install_fresh(self, mock_home_dir, mock_bashrc):
        """Test fresh installation."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=mock_bashrc)

        assert code == 0
        assert "installed" in msg.lower()
        assert check_aliases_installed(mock_bashrc) is True

    def test_install_already_exists(self, mock_home_dir, bashrc_with_aliases):
        """Test installation when already installed."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=bashrc_with_aliases)

        assert code == 1
        assert "already installed" in msg.lower()

    def test_install_force_reinstall(self, mock_home_dir, bashrc_with_aliases):
        """Test force reinstallation."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=bashrc_with_aliases, force=True)

        assert code == 0
        assert "installed" in msg.lower()

        # Should still have exactly one set of markers
        content = bashrc_with_aliases.read_text()
        assert content.count(MARKER_START) == 1

    def test_install_dry_run(self, mock_home_dir, mock_bashrc):
        """Test dry run mode."""
        original_content = mock_bashrc.read_text()

        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=mock_bashrc, dry_run=True)

        assert code == 0
        assert "Would install" in msg
        # File should be unchanged
        assert mock_bashrc.read_text() == original_content

    def test_install_preserves_existing_content(self, mock_home_dir, mock_bashrc):
        """Test that installation preserves existing content."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            install_aliases(shell="bash", rc_file=mock_bashrc)

        content = mock_bashrc.read_text()
        assert "# Existing bashrc content" in content
        assert "export PATH=$PATH:/usr/local/bin" in content

    def test_install_creates_parent_dirs(self, mock_home_dir):
        """Test that installation creates parent directories."""
        fish_config = mock_home_dir / ".config" / "fish" / "config.fish"
        assert not fish_config.parent.exists()

        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="fish", rc_file=fish_config)

        assert code == 0
        assert fish_config.exists()

    def test_install_unsupported_shell(self, mock_home_dir, mock_bashrc):
        """Test installation with unsupported shell."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="powershell", rc_file=mock_bashrc)

        assert code == 1
        assert "Unsupported shell" in msg

    def test_install_auto_detect(self, mock_home_dir, mock_bashrc):
        """Test installation with auto-detection."""
        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                code, msg = install_aliases()

        assert code == 0

    def test_install_zsh(self, mock_home_dir, mock_zshrc):
        """Test installation for zsh."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="zsh", rc_file=mock_zshrc)

        assert code == 0
        assert check_aliases_installed(mock_zshrc) is True

    def test_install_fish(self, mock_home_dir, mock_fish_config):
        """Test installation for fish."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="fish", rc_file=mock_fish_config)

        assert code == 0
        assert check_aliases_installed(mock_fish_config) is True
        # Fish uses functions, not aliases
        content = mock_fish_config.read_text()
        assert "function ctx" in content


# =============================================================================
# Tests for uninstall_aliases
# =============================================================================


class TestUninstallAliases:
    """Tests for uninstall_aliases function."""

    def test_uninstall_success(self, mock_home_dir, bashrc_with_aliases):
        """Test successful uninstallation."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = uninstall_aliases(shell="bash", rc_file=bashrc_with_aliases)

        assert code == 0
        assert "removed" in msg.lower()
        assert check_aliases_installed(bashrc_with_aliases) is False

    def test_uninstall_not_installed(self, mock_home_dir, mock_bashrc):
        """Test uninstall when not installed."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = uninstall_aliases(shell="bash", rc_file=mock_bashrc)

        assert code == 1
        assert "not found" in msg.lower()

    def test_uninstall_preserves_other_content(self, mock_home_dir, bashrc_with_aliases):
        """Test that uninstall preserves other content."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            uninstall_aliases(shell="bash", rc_file=bashrc_with_aliases)

        content = bashrc_with_aliases.read_text()
        assert "# Existing content" in content
        assert "export EDITOR=vim" in content
        assert MARKER_START not in content

    def test_uninstall_dry_run(self, mock_home_dir, bashrc_with_aliases):
        """Test dry run mode."""
        original_content = bashrc_with_aliases.read_text()

        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = uninstall_aliases(shell="bash", rc_file=bashrc_with_aliases, dry_run=True)

        assert code == 0
        assert "Would remove" in msg
        # File should be unchanged
        assert bashrc_with_aliases.read_text() == original_content

    def test_uninstall_auto_detect(self, mock_home_dir, bashrc_with_aliases):
        """Test uninstall with auto-detection."""
        with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
            with patch.object(Path, "home", return_value=mock_home_dir):
                # Need to mock detect_shell to return our test file
                with patch("claude_ctx_py.shell_integration.detect_shell", return_value=("bash", bashrc_with_aliases)):
                    code, msg = uninstall_aliases()

        assert code == 0


# =============================================================================
# Tests for show_aliases
# =============================================================================


class TestShowAliases:
    """Tests for show_aliases function."""

    def test_show_aliases_content(self):
        """Test show_aliases returns helpful content."""
        result = show_aliases()

        assert "ctx" in result
        assert "ctx-light" in result
        assert "ctx-copy" in result
        assert "Installation" in result

    def test_show_aliases_is_string(self):
        """Test show_aliases returns string."""
        result = show_aliases()
        assert isinstance(result, str)


# =============================================================================
# Tests for marker constants
# =============================================================================


class TestMarkerConstants:
    """Tests for marker constants."""

    def test_markers_are_comments(self):
        """Test markers are shell comments."""
        assert MARKER_START.startswith("#")
        assert MARKER_END.startswith("#")

    def test_markers_are_distinct(self):
        """Test markers are different."""
        assert MARKER_START != MARKER_END

    def test_markers_contain_identifier(self):
        """Test markers contain identifiable text."""
        assert "cortex" in MARKER_START
        assert "cortex" in MARKER_END


# =============================================================================
# Integration tests
# =============================================================================


class TestInstallUninstallCycle:
    """Integration tests for install/uninstall cycle."""

    def test_full_cycle(self, mock_home_dir, mock_bashrc):
        """Test install then uninstall restores original state."""
        original = mock_bashrc.read_text()

        with patch.object(Path, "home", return_value=mock_home_dir):
            # Install
            code1, _ = install_aliases(shell="bash", rc_file=mock_bashrc)
            assert code1 == 0
            assert check_aliases_installed(mock_bashrc) is True

            # Uninstall
            code2, _ = uninstall_aliases(shell="bash", rc_file=mock_bashrc)
            assert code2 == 0
            assert check_aliases_installed(mock_bashrc) is False

        # Original content preserved
        final = mock_bashrc.read_text()
        assert "# Existing bashrc content" in final

    def test_multiple_installs_idempotent(self, mock_home_dir, mock_bashrc):
        """Test multiple force installs are idempotent."""
        with patch.object(Path, "home", return_value=mock_home_dir):
            install_aliases(shell="bash", rc_file=mock_bashrc)
            install_aliases(shell="bash", rc_file=mock_bashrc, force=True)
            install_aliases(shell="bash", rc_file=mock_bashrc, force=True)

        content = mock_bashrc.read_text()
        assert content.count(MARKER_START) == 1
        assert content.count(MARKER_END) == 1


# =============================================================================
# Edge case tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_install_creates_new_file(self, mock_home_dir):
        """Test installation creates RC file if missing."""
        new_bashrc = mock_home_dir / ".bashrc"
        assert not new_bashrc.exists()

        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=new_bashrc)

        assert code == 0
        assert new_bashrc.exists()
        assert check_aliases_installed(new_bashrc) is True

    def test_install_empty_file(self, mock_home_dir):
        """Test installation to empty RC file."""
        bashrc = mock_home_dir / ".bashrc"
        bashrc.write_text("")

        with patch.object(Path, "home", return_value=mock_home_dir):
            code, msg = install_aliases(shell="bash", rc_file=bashrc)

        assert code == 0
        assert check_aliases_installed(bashrc) is True

    def test_install_preserves_unicode(self, mock_home_dir):
        """Test installation preserves unicode content."""
        bashrc = mock_home_dir / ".bashrc"
        bashrc.write_text("# Comment: café résumé\nexport VAR='test'\n", encoding="utf-8")

        with patch.object(Path, "home", return_value=mock_home_dir):
            install_aliases(shell="bash", rc_file=bashrc)

        content = bashrc.read_text(encoding="utf-8")
        assert "café résumé" in content
        assert check_aliases_installed(bashrc) is True
