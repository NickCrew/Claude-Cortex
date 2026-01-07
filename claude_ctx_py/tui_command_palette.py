"""Command palette with fuzzy search for quick navigation and actions."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple, Union
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

    CSS = """
    CommandPalette {
        align: center middle;
    }

    CommandPalette #command-palette-container {
        width: 70%;
        height: auto;
        max-height: 80%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    CommandPalette #palette-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    CommandPalette #palette-input {
        margin-bottom: 1;
    }

    CommandPalette #palette-results {
        height: auto;
        max-height: 50vh;
        margin-bottom: 1;
    }

    CommandPalette #palette-help {
        text-align: center;
        color: $text-muted;
    }
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
        self._query = ""

    def compose(self) -> ComposeResult:
        """Compose the command palette."""
        with Container(id="command-palette-container"):
            with Vertical():
                yield Static(f"{Icons.SEARCH} Command Palette", id="palette-title")
                yield Input(placeholder="Summon anything…", id="palette-input")
                yield Static(
                    "[dim italic]Neon holo-panel ready. Type to filter, press Enter to fire.[/dim italic]",
                    id="palette-subtitle",
                )
                yield ListView(id="palette-results")
                yield Static(
                    f"[dim]{Icons.ARROW_UP}/{Icons.ARROW_DOWN} Navigate  {Icons.SUCCESS} Select  Esc Close[/dim]",
                    id="palette-help",
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
        self._query = query

        if not query:
            self.filtered_commands = self.commands.copy()
        else:
            # Fuzzy search implementation
            scored_commands: List[Tuple[int, Dict[str, str]]] = []
            for cmd in self.commands:
                score = self._fuzzy_match(query, cmd["name"].lower())
                if score > 0:
                    scored_commands.append((score, cmd))

            # Sort by score (highest first) and drop scores
            scored_commands.sort(key=lambda item: item[0], reverse=True)
            self.filtered_commands = [cmd for _, cmd in scored_commands]

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
                name = cmd["name"]
                description = cmd.get("description", "")
                badge = cmd.get("badge")
                name_text = self._highlight_query(name)
                desc_text = self._highlight_query(description)

                badge_text = f" [bold]{badge.upper()}[/bold]" if badge else ""
                if idx == self.selected_index:
                    label = f"[reverse]{Icons.ARROW_RIGHT} {name_text}{badge_text}[/reverse] [dim]{desc_text}[/dim]"
                else:
                    label = (
                        f"{Icons.SPACE} {name_text}{badge_text} [dim]{desc_text}[/dim]"
                    )

                results.append(ListItem(Label(label)))

            # Force refresh the ListView
            results.refresh()
        except Exception:
            pass  # ListView not yet mounted

    def _highlight_query(self, text: str) -> str:
        """Highlight query matches inside text using cyan accents."""
        if not self._query or not text:
            return text

        lower_text = text.lower()
        idx = lower_text.find(self._query)
        if idx == -1:
            return text

        end = idx + len(self._query)
        return f"{text[:idx]}[cyan]{text[idx:end]}[/cyan]{text[end:]}"

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
            self.dismiss(selected["action"])
        else:
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the palette."""
        self.dismiss(None)


CommandTuple = Union[Tuple[str, str, str], Tuple[str, str, str, str]]


class CommandRegistry:
    """Registry for available commands in the TUI."""

    def __init__(self) -> None:
        """Initialize command registry."""
        self.commands: List[Dict[str, str]] = []

    def register(
        self, name: str, description: str, action: str, badge: Optional[str] = None
    ) -> None:
        """Register a new command.

        Args:
            name: Command name (e.g., "Show Agents")
            description: Brief description
            action: Action identifier (e.g., "show_agents")
        """
        command = {"name": name, "description": description, "action": action}
        if badge:
            command["badge"] = badge
        self.commands.append(command)

    def register_batch(self, commands: Sequence[CommandTuple]) -> None:
        """Register multiple commands at once.

        Args:
            commands: List of (name, description, action) tuples
        """
        for entry in commands:
            if len(entry) == 4:
                name, description, action, badge = entry
                self.register(name, description, action, badge)
            else:
                name, description, action = entry
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
# NOTE: Action names must match actual action_* methods in main.py
DEFAULT_COMMANDS: List[CommandTuple] = [
    # View navigation (action_view_*)
    ("Show Overview", "Dashboard and metrics", "view_overview", "core"),
    ("Show Agents", "View and manage agents", "view_agents", "core"),
    ("Show Skills", "Browse available skills", "view_skills", "catalog"),
    ("Show Slash Commands", "Browse slash command library", "view_commands", "commands"),
    ("Show Modes", "View active modes", "view_modes", "context"),
    ("Show Rules", "View active rules", "view_rules", "policy"),
    ("Show Principles", "Manage principles snippets", "view_principles", "policy"),
    ("Build Principles", "Rebuild PRINCIPLES.md from snippets", "principles_build", "policy"),
    ("Open Principles", "View generated PRINCIPLES.md", "principles_open", "policy"),
    ("Show Workflows", "View workflow execution", "view_workflows", "ops"),
    ("Show Worktrees", "Manage git worktrees", "view_worktrees", "ops"),
    ("Show Scenarios", "View scenarios", "view_scenarios", "ops"),
    ("Show Orchestrate", "View orchestration tasks", "view_orchestrate", "ops"),
    ("Show MCP", "Manage MCP servers", "view_mcp", "infra"),
    ("Show Profiles", "Manage saved profiles", "view_profiles", "context"),
    ("Show Export", "Configure context export", "view_export", "utilities"),
    ("Show Tasks", "Manage task queue", "view_tasks", "tasks"),
    ("Show Assets", "Asset manager", "view_assets", "utilities"),
    ("Show Memory", "Memory vault", "view_memory", "context"),
    ("Galaxy View", "Visualize agent constellations", "view_galaxy", "viz"),
    ("Request Reviews", "Spawn review tasks from recommendations", "request_reviews", "ai"),
    ("Consult Gemini", "Ask Gemini for a second opinion", "consult_gemini", "ai"),
    ("Assign LLM Tasks", "Dispatch tasks to Gemini/OpenAI/Qwen", "assign_llm_tasks", "ai"),
    ("Design UI", "Generate distinctive UI components", "action_design_ui", "design"),
    ("RAG Ingest", "Ingest documents with context", "action_rag_ingest", "ops"),
    # Actions
    ("Toggle Selected", "Toggle current item", "toggle", "action"),
    ("Refresh", "Refresh current view", "refresh", "action"),
    ("Auto-Activate Recommended", "Trigger AI suggestions", "auto_activate", "ai"),
    ("Worktree Add", "Create a new worktree", "worktree_add", "ops"),
    ("Worktree Open", "Open selected worktree", "worktree_open", "ops"),
    ("Worktree Remove", "Remove selected worktree", "worktree_remove", "danger"),
    ("Worktree Prune", "Prune stale worktrees", "worktree_prune", "ops"),
    ("Worktree Base Dir", "Set worktree base directory", "worktree_set_base_dir", "ops"),
    # MCP actions
    ("MCP Browse & Install", "Install MCP server from registry", "mcp_browse_install", "infra"),
    ("MCP Add Server", "Add MCP server manually", "mcp_add", "infra"),
    ("MCP Test Server", "Test selected MCP server", "mcp_test_selected", "infra"),
    ("MCP Diagnose", "Diagnose all MCP servers", "mcp_diagnose", "infra"),
    # Profile actions
    ("Edit Profile", "View and edit selected profile", "profile_edit", "context"),
    ("Save Profile", "Save current config as profile", "profile_save_prompt", "context"),
    ("Delete Profile", "Delete selected profile", "profile_delete", "danger"),
    # Export actions
    ("Export Context", "Run export with current settings", "export_run", "utilities"),
    ("Copy to Clipboard", "Copy export to clipboard", "export_clipboard", "utilities"),
    # Configuration
    ("Configure CLAUDE.md", "Wizard to configure CLAUDE.md", "claude_md_wizard", "config"),
    ("Configure LLM Providers", "Set API keys for Gemini/OpenAI/Qwen", "llm_provider_settings", "config"),
    ("Manage Hooks", "Install and configure hooks", "hooks_manager", "config"),
    ("Backup Manager", "Create and restore backups", "backup_manager", "utilities"),
    # Help
    ("Help", "Show help and documentation", "help", "docs"),
    ("Quit", "Exit the application", "quit", "danger"),
    # Skill actions
    ("Skill Info", "Show metadata for selected skill", "skill_info", "skills"),
    ("Skill Versions", "Show available versions", "skill_versions", "skills"),
    ("Skill Dependencies", "Show dependency tree", "skill_deps", "skills"),
    ("Skill Agents", "Show agents using the skill", "skill_agents", "skills"),
    ("Skill Compose", "Show compose graph", "skill_compose", "skills"),
    ("Skill Analyze Text", "Analyze text to suggest skills", "skill_analyze", "ai"),
    ("Skill Suggest Project", "Suggest skills for current project", "skill_suggest", "ai"),
    ("Skill Analytics", "Show analytics dashboard", "skill_analytics", "metrics"),
    ("Skill Report", "Generate analytics report", "skill_report", "metrics"),
    ("Skill Trending", "Show trending skills", "skill_trending", "metrics"),
    ("Skill Metrics Reset", "Reset skill metrics", "skill_metrics_reset", "danger"),
    # Community skills
    ("Community Install Skill", "Install a community skill", "skill_community_install", "catalog"),
    ("Community Validate Skill", "Validate a community skill", "skill_community_validate", "catalog"),
    ("Community Rate Skill", "Rate a community skill", "skill_community_rate", "catalog"),
    ("Community Search", "Search community skills", "skill_community_search", "catalog"),
]
