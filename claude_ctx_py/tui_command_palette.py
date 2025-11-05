"""Command palette with fuzzy search for quick navigation and actions."""

from __future__ import annotations

from typing import List, Dict, Callable, Optional, Tuple
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static, ListView, ListItem, Label
from textual.binding import Binding

from .tui_icons import Icons


class CommandPalette(ModalScreen[Optional[str]]):
    """Universal command palette with fuzzy search.

    Press Ctrl+P to open, type to search, Enter to execute.
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+p", "close", "Close"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    def __init__(self, commands: List[Dict[str, str]]):
        """Initialize command palette.

        Args:
            commands: List of command dicts with 'name', 'description', 'action' keys
        """
        super().__init__()
        self.commands = commands
        self.filtered_commands = commands.copy()
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        with Container(id="command-palette-container"):
            with Vertical():
                yield Static(f"{Icons.SEARCH} Command Palette", id="palette-title")
                yield Input(placeholder="Type to search commands...", id="palette-input")
                yield ListView(id="palette-results")
                yield Static(
                    f"[dim]{Icons.ARROW_UP}/{Icons.ARROW_DOWN} Navigate  {Icons.SUCCESS} Select  Esc Close[/dim]",
                    id="palette-help"
                )

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#palette-input", Input).focus()
        self._update_results()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        # Only process events from the palette input
        if event.input.id != "palette-input":
            return

        query = event.value.lower()

        if not query:
            self.filtered_commands = self.commands.copy()
        else:
            # Fuzzy search implementation
            self.filtered_commands = []
            for cmd in self.commands:
                score = self._fuzzy_match(query, cmd['name'].lower())
                if score > 0:
                    self.filtered_commands.append((score, cmd))

            # Sort by score (highest first)
            self.filtered_commands.sort(key=lambda x: x[0], reverse=True)
            self.filtered_commands = [cmd for score, cmd in self.filtered_commands]

        self.selected_index = 0
        self._update_results()

    def _fuzzy_match(self, query: str, text: str) -> int:
        """Fuzzy match scoring algorithm.

        Args:
            query: Search query
            text: Text to match against

        Returns:
            Match score (higher is better, 0 = no match)
        """
        if query in text:
            # Exact substring match gets high score
            return 1000 + (100 - len(text))

        # Character-by-character fuzzy matching
        score = 0
        query_idx = 0
        consecutive = 0

        for text_idx, char in enumerate(text):
            if query_idx < len(query) and char == query[query_idx]:
                score += 10 + (consecutive * 5)  # Bonus for consecutive matches
                query_idx += 1
                consecutive += 1
            else:
                consecutive = 0

        # If we matched all query characters, it's a valid match
        if query_idx == len(query):
            return score

        return 0

    def _update_results(self) -> None:
        """Update the results list view."""
        try:
            results = self.query_one("#palette-results", ListView)
            results.clear()

            if not self.filtered_commands:
                results.append(ListItem(Label("[dim]No commands found[/dim]")))
                results.refresh()
                return

            for idx, cmd in enumerate(self.filtered_commands[:10]):  # Show top 10
                name = cmd['name']
                description = cmd.get('description', '')

                # Highlight selected item
                if idx == self.selected_index:
                    label = f"[reverse]{Icons.ARROW_RIGHT} {name}[/reverse] [dim]{description}[/dim]"
                else:
                    label = f"  {name} [dim]{description}[/dim]"

                results.append(ListItem(Label(label)))

            # Force refresh the ListView
            results.refresh()
        except Exception:
            pass  # ListView not yet mounted

    def action_cursor_up(self) -> None:
        """Move cursor up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self._update_results()

    def action_cursor_down(self) -> None:
        """Move cursor down."""
        if self.selected_index < len(self.filtered_commands) - 1:
            self.selected_index += 1
            self._update_results()

    def action_select(self) -> None:
        """Select the current command."""
        if self.filtered_commands and self.selected_index < len(self.filtered_commands):
            selected = self.filtered_commands[self.selected_index]
            self.dismiss(selected['action'])
        else:
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the palette."""
        self.dismiss(None)


class CommandRegistry:
    """Registry for available commands in the TUI."""

    def __init__(self):
        """Initialize command registry."""
        self.commands: List[Dict[str, str]] = []

    def register(self, name: str, description: str, action: str) -> None:
        """Register a new command.

        Args:
            name: Command name (e.g., "Show Agents")
            description: Brief description
            action: Action identifier (e.g., "show_agents")
        """
        self.commands.append({
            'name': name,
            'description': description,
            'action': action
        })

    def register_batch(self, commands: List[Tuple[str, str, str]]) -> None:
        """Register multiple commands at once.

        Args:
            commands: List of (name, description, action) tuples
        """
        for name, description, action in commands:
            self.register(name, description, action)

    def get_all(self) -> List[Dict[str, str]]:
        """Get all registered commands.

        Returns:
            List of command dictionaries
        """
        return self.commands.copy()

    def clear(self) -> None:
        """Clear all registered commands."""
        self.commands.clear()


# Default command registry for TUI
DEFAULT_COMMANDS = [
    ("Show Agents", "View and manage agents", "show_agents"),
    ("Show Skills", "Browse available skills", "show_skills"),
    ("Show Modes", "View active modes", "show_modes"),
    ("Show Rules", "View active rules", "show_rules"),
    ("Show Workflows", "View workflow execution", "show_workflows"),
    ("Show Orchestrate", "View orchestration tasks", "show_orchestrate"),
    ("Activate Agent", "Activate a new agent", "activate_agent"),
    ("Deactivate Agent", "Deactivate an agent", "deactivate_agent"),
    ("Create Skill", "Create a new skill", "create_skill"),
    ("Toggle Mode", "Toggle a mode on/off", "toggle_mode"),
    ("Toggle Rule", "Toggle a rule on/off", "toggle_rule"),
    ("Export Context", "Export current context", "export_context"),
    ("Help", "Show help and documentation", "show_help"),
    ("Quit", "Exit the application", "quit"),
]
