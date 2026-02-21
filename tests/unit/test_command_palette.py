"""Unit tests for command palette functionality.

Tests for the CommandPalette and CommandRegistry classes, including:
- Command registration and retrieval
- Fuzzy search matching algorithm
- Command palette filtering and display
"""

from __future__ import annotations

from typing import Dict, List

import pytest

from claude_ctx_py.tui_command_palette import CommandRegistry, CommandPalette


@pytest.mark.unit
@pytest.mark.fast
class TestCommandRegistry:
    """Tests for CommandRegistry class."""

    def test_register_single_command(self) -> None:
        """Test registering a single command."""
        registry = CommandRegistry()

        registry.register(
            name="Show Overview",
            description="Dashboard and metrics",
            action="view_overview",
        )

        commands = registry.get_all()
        assert len(commands) == 1
        assert commands[0]["name"] == "Show Overview"
        assert commands[0]["description"] == "Dashboard and metrics"
        assert commands[0]["action"] == "view_overview"

    def test_register_command_with_badge(self) -> None:
        """Test registering a command with a badge."""
        registry = CommandRegistry()

        registry.register(
            name="Show Agents",
            description="View and manage agents",
            action="view_agents",
            badge="core",
        )

        commands = registry.get_all()
        assert len(commands) == 1
        assert commands[0].get("badge") == "core"

    def test_register_batch_commands(self) -> None:
        """Test registering multiple commands at once."""
        registry = CommandRegistry()

        commands_to_register = [
            ("Show Overview", "Dashboard and metrics", "view_overview"),
            ("Show Agents", "View and manage agents", "view_agents", "core"),
            ("Show Rules", "View active rules", "view_rules", "policy"),
        ]

        registry.register_batch(commands_to_register)

        commands = registry.get_all()
        assert len(commands) == 3
        assert commands[0]["name"] == "Show Overview"
        assert commands[1].get("badge") == "core"
        assert commands[2].get("badge") == "policy"

    def test_clear_commands(self) -> None:
        """Test clearing all registered commands."""
        registry = CommandRegistry()

        registry.register(
            name="Show Overview",
            description="Dashboard",
            action="view_overview",
        )
        assert len(registry.get_all()) == 1

        registry.clear()
        assert len(registry.get_all()) == 0

    def test_get_all_returns_copy(self) -> None:
        """Test that get_all returns a copy, not a reference."""
        registry = CommandRegistry()

        registry.register(
            name="Show Overview",
            description="Dashboard",
            action="view_overview",
        )

        commands1 = registry.get_all()
        commands2 = registry.get_all()

        # Verify it's a copy by modifying one
        commands1.append({"name": "Test", "description": "Test", "action": "test"})

        # Original registry should be unchanged
        assert len(registry.get_all()) == 1
        assert commands2 != commands1


@pytest.mark.unit
@pytest.mark.fast
class TestCommandPaletteFuzzyMatch:
    """Tests for fuzzy matching algorithm in CommandPalette."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.palette = CommandPalette(
            commands=[
                {
                    "name": "Show Overview",
                    "description": "Dashboard",
                    "action": "view_overview",
                }
            ]
        )

    def test_exact_substring_match(self) -> None:
        """Test exact substring match scores highest."""
        score = self.palette._fuzzy_match("overview", "show overview")
        assert score > 0
        assert score > self.palette._fuzzy_match("so", "show overview")

    def test_fuzzy_character_matching(self) -> None:
        """Test fuzzy character-by-character matching."""
        # "so" matches "show overview" (s, o are present)
        score = self.palette._fuzzy_match("so", "show overview")
        assert score > 0

    def test_no_match(self) -> None:
        """Test that non-matching queries return 0."""
        score = self.palette._fuzzy_match("xyz", "show overview")
        assert score == 0

    def test_consecutive_characters_bonus(self) -> None:
        """Test that consecutive matches get a bonus."""
        # "show" is consecutive in "show overview"
        score1 = self.palette._fuzzy_match("show", "show overview")
        # "shw" is not fully consecutive
        score2 = self.palette._fuzzy_match("shw", "show overview")
        assert score1 > score2

    def test_case_insensitive_text_matching(self) -> None:
        """Test that fuzzy matching matches against lowercase text.

        Note: The fuzzy match function expects lowercase text (conversion
        happens in on_input_changed event handler). This test verifies that
        the algorithm works correctly with lowercase text.
        """
        score1 = self.palette._fuzzy_match("overview", "show overview")
        score2 = self.palette._fuzzy_match("overview", "SHOW OVERVIEW".lower())
        assert score1 == score2


@pytest.mark.unit
@pytest.mark.fast
class TestCommandPaletteFiltering:
    """Tests for command filtering in CommandPalette."""

    def setup_method(self) -> None:
        """Set up test fixtures with multiple commands."""
        commands = [
            {
                "name": "Show Overview",
                "description": "Dashboard",
                "action": "view_overview",
            },
            {
                "name": "Show Agents",
                "description": "View and manage agents",
                "action": "view_agents",
            },
            {
                "name": "Show Rules",
                "description": "View active rules",
                "action": "view_rules",
            },
        ]
        self.palette = CommandPalette(commands)

    def test_empty_query_returns_all_commands(self) -> None:
        """Test that empty query returns all commands."""
        self.palette.on_input_changed(
            type(
                "InputChanged",
                (),
                {"value": "", "input": type("Input", (), {"id": "palette-input"})()},
            )()
        )
        assert len(self.palette.filtered_commands) == 3

    def test_query_filters_commands(self) -> None:
        """Test that query filters commands by fuzzy match."""
        self.palette.on_input_changed(
            type(
                "InputChanged",
                (),
                {
                    "value": "agents",
                    "input": type("Input", (), {"id": "palette-input"})(),
                },
            )()
        )
        assert len(self.palette.filtered_commands) == 1
        assert self.palette.filtered_commands[0]["name"] == "Show Agents"

    def test_query_sorts_by_score(self) -> None:
        """Test that filtered commands are sorted by match score."""
        # Query that could match multiple commands
        self.palette.on_input_changed(
            type(
                "InputChanged",
                (),
                {"value": "show", "input": type("Input", (), {"id": "palette-input"})()},
            )()
        )
        # All three commands start with "Show"
        assert len(self.palette.filtered_commands) == 3
        # "Show" should be at the top due to exact substring match
        for cmd in self.palette.filtered_commands:
            assert cmd["name"].startswith("Show")

    def test_no_matching_commands(self) -> None:
        """Test behavior when query matches no commands."""
        self.palette.on_input_changed(
            type(
                "InputChanged",
                (),
                {
                    "value": "nonexistent",
                    "input": type("Input", (), {"id": "palette-input"})(),
                },
            )()
        )
        assert len(self.palette.filtered_commands) == 0


@pytest.mark.unit
@pytest.mark.fast
def test_command_palette_initialization() -> None:
    """Test CommandPalette initialization."""
    commands: List[Dict[str, str]] = [
        {
            "name": "Test Command",
            "description": "A test command",
            "action": "test_action",
        }
    ]

    palette = CommandPalette(commands)

    assert len(palette.commands) == 1
    assert len(palette.filtered_commands) == 1
    assert palette.selected_index == 0
