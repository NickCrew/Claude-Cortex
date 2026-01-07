"""Tests for shell completion generation module.

This module tests the completions.py module which generates
shell completion scripts for bash, zsh, and fish shells.
"""

from __future__ import annotations

import pytest

from claude_ctx_py.completions import (
    generate_bash_completion,
    generate_fish_completion,
    generate_zsh_completion,
    get_completion_script,
    get_installation_instructions,
)


class TestGenerateBashCompletion:
    """Tests for bash completion script generation."""

    def test_returns_string(self):
        """Bash completion returns a string."""
        result = generate_bash_completion()
        assert isinstance(result, str)

    def test_contains_completion_function(self):
        """Bash completion contains the main completion function."""
        result = generate_bash_completion()
        assert "_claude_ctx_completion()" in result

    def test_contains_complete_command(self):
        """Bash completion registers the completion function."""
        result = generate_bash_completion()
        assert "complete -F _claude_ctx_completion cortex" in result

    def test_contains_top_level_commands(self):
        """Bash completion includes all top-level commands."""
        result = generate_bash_completion()
        expected_commands = [
            "mode",
            "agent",
            "rules",
            "principles",
            "skills",
            "mcp",
            "init",
            "setup",
            "profile",
            "workflow",
            "tui",
            "version",
            "completion",
            "install",
            "help",
            "doctor",
        ]
        for cmd in expected_commands:
            assert cmd in result, f"Missing command: {cmd}"

    def test_contains_mode_subcommands(self):
        """Bash completion includes mode subcommands."""
        result = generate_bash_completion()
        assert "mode_cmds=" in result
        assert "list" in result
        assert "activate" in result
        assert "deactivate" in result

    def test_contains_agent_subcommands(self):
        """Bash completion includes agent subcommands."""
        result = generate_bash_completion()
        assert "agent_cmds=" in result
        assert "deps" in result
        assert "graph" in result
        assert "validate" in result

    def test_contains_skills_subcommands(self):
        """Bash completion includes skills subcommands."""
        result = generate_bash_completion()
        assert "skills_cmds=" in result
        assert "analyze" in result
        assert "suggest" in result
        assert "metrics" in result
        assert "community" in result

    def test_contains_install_subcommands(self):
        """Bash completion includes install subcommands."""
        result = generate_bash_completion()
        assert "install_cmds=" in result
        assert "aliases" in result
        assert "completions" in result
        assert "manpage" in result


class TestGenerateZshCompletion:
    """Tests for zsh completion script generation."""

    def test_returns_string(self):
        """Zsh completion returns a string."""
        result = generate_zsh_completion()
        assert isinstance(result, str)

    def test_contains_compdef(self):
        """Zsh completion includes compdef directive."""
        result = generate_zsh_completion()
        assert "#compdef cortex" in result

    def test_contains_main_function(self):
        """Zsh completion contains the main function."""
        result = generate_zsh_completion()
        assert "_claude_ctx()" in result

    def test_contains_commands_array(self):
        """Zsh completion defines commands array."""
        result = generate_zsh_completion()
        assert "local -a commands" in result

    def test_contains_command_descriptions(self):
        """Zsh completion includes command descriptions."""
        result = generate_zsh_completion()
        assert "'mode:Mode management commands'" in result
        assert "'agent:Agent management commands'" in result
        assert "'tui:Launch terminal UI'" in result

    def test_contains_mode_commands_array(self):
        """Zsh completion defines mode subcommands."""
        result = generate_zsh_completion()
        assert "local -a mode_commands" in result
        assert "'list:List available modes'" in result
        assert "'activate:Activate one or more modes'" in result

    def test_contains_agent_commands_array(self):
        """Zsh completion defines agent subcommands."""
        result = generate_zsh_completion()
        assert "local -a agent_commands" in result
        assert "'deps:Show agent dependencies'" in result
        assert "'graph:Display dependency graph'" in result

    def test_contains_skills_commands_array(self):
        """Zsh completion defines skills subcommands."""
        result = generate_zsh_completion()
        assert "local -a skills_commands" in result
        assert "'analyze:Analyze text for skill suggestions'" in result
        assert "'community:Community skill commands'" in result

    def test_contains_mcp_commands_array(self):
        """Zsh completion defines mcp subcommands."""
        result = generate_zsh_completion()
        assert "local -a mcp_commands" in result
        assert "'diagnose:Diagnose server issues'" in result
        assert "'snippet:Generate config snippet'" in result

    def test_contains_install_commands_array(self):
        """Zsh completion defines install subcommands."""
        result = generate_zsh_completion()
        assert "local -a install_commands" in result
        assert "'manpage:Install manpages'" in result

    def test_uses_describe_function(self):
        """Zsh completion uses _describe for completion."""
        result = generate_zsh_completion()
        assert "_describe" in result


class TestGenerateFishCompletion:
    """Tests for fish completion script generation."""

    def test_returns_string(self):
        """Fish completion returns a string."""
        result = generate_fish_completion()
        assert isinstance(result, str)

    def test_contains_fish_comment(self):
        """Fish completion includes identifying comment."""
        result = generate_fish_completion()
        assert "# Fish completion for cortex" in result

    def test_uses_complete_command(self):
        """Fish completion uses the complete command."""
        result = generate_fish_completion()
        assert "complete -c cortex" in result

    def test_contains_top_level_commands(self):
        """Fish completion defines top-level commands."""
        result = generate_fish_completion()
        assert '-a "mode" -d "Mode management"' in result
        assert '-a "agent" -d "Agent management"' in result
        assert '-a "tui" -d "Launch terminal UI"' in result

    def test_uses_fish_use_subcommand(self):
        """Fish completion uses __fish_use_subcommand predicate."""
        result = generate_fish_completion()
        assert "__fish_use_subcommand" in result

    def test_uses_fish_seen_subcommand(self):
        """Fish completion uses __fish_seen_subcommand_from predicate."""
        result = generate_fish_completion()
        assert "__fish_seen_subcommand_from" in result

    def test_contains_mode_subcommands(self):
        """Fish completion includes mode subcommands."""
        result = generate_fish_completion()
        assert '__fish_seen_subcommand_from mode' in result
        assert '-a "list" -d "List available modes"' in result

    def test_contains_agent_subcommands(self):
        """Fish completion includes agent subcommands."""
        result = generate_fish_completion()
        assert '__fish_seen_subcommand_from agent' in result
        assert '-a "deps" -d "Show dependencies"' in result

    def test_contains_install_subcommands(self):
        """Fish completion includes install subcommands."""
        result = generate_fish_completion()
        assert '__fish_seen_subcommand_from install' in result
        assert '-a "manpage" -d "Install manpages"' in result

    def test_contains_completion_shells(self):
        """Fish completion includes shell options for completion command."""
        result = generate_fish_completion()
        assert '__fish_seen_subcommand_from completion' in result
        assert '-a "bash" -d "Bash completion"' in result
        assert '-a "zsh" -d "Zsh completion"' in result
        assert '-a "fish" -d "Fish completion"' in result


class TestGetCompletionScript:
    """Tests for get_completion_script function."""

    def test_returns_bash_completion(self):
        """get_completion_script returns bash completion for 'bash'."""
        result = get_completion_script("bash")
        assert "_claude_ctx_completion()" in result
        assert "complete -F" in result

    def test_returns_zsh_completion(self):
        """get_completion_script returns zsh completion for 'zsh'."""
        result = get_completion_script("zsh")
        assert "#compdef cortex" in result
        assert "_claude_ctx()" in result

    def test_returns_fish_completion(self):
        """get_completion_script returns fish completion for 'fish'."""
        result = get_completion_script("fish")
        assert "# Fish completion" in result
        assert "complete -c cortex" in result

    def test_case_insensitive_bash(self):
        """get_completion_script handles case-insensitive 'BASH'."""
        result = get_completion_script("BASH")
        assert "_claude_ctx_completion()" in result

    def test_case_insensitive_zsh(self):
        """get_completion_script handles case-insensitive 'ZSH'."""
        result = get_completion_script("ZSH")
        assert "#compdef cortex" in result

    def test_case_insensitive_fish(self):
        """get_completion_script handles case-insensitive 'FISH'."""
        result = get_completion_script("FISH")
        assert "# Fish completion" in result

    def test_mixed_case(self):
        """get_completion_script handles mixed case like 'BaSh'."""
        result = get_completion_script("BaSh")
        assert "_claude_ctx_completion()" in result

    def test_raises_for_unsupported_shell(self):
        """get_completion_script raises ValueError for unsupported shell."""
        with pytest.raises(ValueError) as exc_info:
            get_completion_script("powershell")
        assert "Unsupported shell: powershell" in str(exc_info.value)
        assert "bash, zsh, fish" in str(exc_info.value)

    def test_raises_for_empty_string(self):
        """get_completion_script raises ValueError for empty string."""
        with pytest.raises(ValueError) as exc_info:
            get_completion_script("")
        assert "Unsupported shell" in str(exc_info.value)

    def test_raises_for_invalid_shell(self):
        """get_completion_script raises ValueError for invalid shell name."""
        with pytest.raises(ValueError):
            get_completion_script("invalid_shell")


class TestGetInstallationInstructions:
    """Tests for get_installation_instructions function."""

    def test_returns_string_for_bash(self):
        """get_installation_instructions returns string for bash."""
        result = get_installation_instructions("bash")
        assert isinstance(result, str)

    def test_returns_string_for_zsh(self):
        """get_installation_instructions returns string for zsh."""
        result = get_installation_instructions("zsh")
        assert isinstance(result, str)

    def test_returns_string_for_fish(self):
        """get_installation_instructions returns string for fish."""
        result = get_installation_instructions("fish")
        assert isinstance(result, str)

    def test_bash_instructions_contain_paths(self):
        """Bash instructions contain installation paths."""
        result = get_installation_instructions("bash")
        assert "/etc/bash_completion.d/" in result
        assert "~/.bash_completion.d" in result
        assert "~/.bashrc" in result

    def test_bash_instructions_contain_options(self):
        """Bash instructions contain both system-wide and user options."""
        result = get_installation_instructions("bash")
        assert "System-wide" in result
        assert "User-specific" in result

    def test_zsh_instructions_contain_paths(self):
        """Zsh instructions contain installation paths."""
        result = get_installation_instructions("zsh")
        assert "~/.zsh/completions" in result
        assert "~/.zshrc" in result

    def test_zsh_instructions_contain_fpath(self):
        """Zsh instructions explain fpath setup."""
        result = get_installation_instructions("zsh")
        assert "fpath" in result
        assert "compinit" in result

    def test_fish_instructions_contain_paths(self):
        """Fish instructions contain installation paths."""
        result = get_installation_instructions("fish")
        assert "~/.config/fish/completions" in result
        assert "cortex.fish" in result

    def test_case_insensitive_bash(self):
        """get_installation_instructions handles case-insensitive 'BASH'."""
        result = get_installation_instructions("BASH")
        assert "Bash Completion" in result

    def test_case_insensitive_zsh(self):
        """get_installation_instructions handles case-insensitive 'ZSH'."""
        result = get_installation_instructions("ZSH")
        assert "Zsh Completion" in result

    def test_case_insensitive_fish(self):
        """get_installation_instructions handles case-insensitive 'FISH'."""
        result = get_installation_instructions("FISH")
        assert "Fish Completion" in result

    def test_unsupported_shell_returns_message(self):
        """get_installation_instructions returns message for unsupported shell."""
        result = get_installation_instructions("powershell")
        assert "No installation instructions for shell: powershell" in result

    def test_empty_shell_returns_message(self):
        """get_installation_instructions returns message for empty shell."""
        result = get_installation_instructions("")
        assert "No installation instructions for shell:" in result


class TestCompletionScriptConsistency:
    """Tests to ensure completion scripts are consistent with each other."""

    @pytest.fixture
    def all_completions(self):
        """Get all completion scripts."""
        return {
            "bash": generate_bash_completion(),
            "zsh": generate_zsh_completion(),
            "fish": generate_fish_completion(),
        }

    def test_all_shells_have_mode_command(self, all_completions):
        """All shells include mode command."""
        for shell, script in all_completions.items():
            assert "mode" in script, f"{shell} missing 'mode' command"

    def test_all_shells_have_agent_command(self, all_completions):
        """All shells include agent command."""
        for shell, script in all_completions.items():
            assert "agent" in script, f"{shell} missing 'agent' command"

    def test_all_shells_have_tui_command(self, all_completions):
        """All shells include tui command."""
        for shell, script in all_completions.items():
            assert "tui" in script, f"{shell} missing 'tui' command"

    def test_all_shells_have_skills_command(self, all_completions):
        """All shells include skills command."""
        for shell, script in all_completions.items():
            assert "skills" in script, f"{shell} missing 'skills' command"

    def test_all_shells_have_mcp_command(self, all_completions):
        """All shells include mcp command."""
        for shell, script in all_completions.items():
            assert "mcp" in script, f"{shell} missing 'mcp' command"

    def test_all_shells_have_workflow_command(self, all_completions):
        """All shells include workflow command."""
        for shell, script in all_completions.items():
            assert "workflow" in script, f"{shell} missing 'workflow' command"

    def test_all_shells_have_install_command(self, all_completions):
        """All shells include install command."""
        for shell, script in all_completions.items():
            assert "install" in script, f"{shell} missing 'install' command"

    def test_all_shells_have_doctor_command(self, all_completions):
        """All shells include doctor command."""
        for shell, script in all_completions.items():
            assert "doctor" in script, f"{shell} missing 'doctor' command"
