"""Textual command providers for AgentTUI - SUPER SAIYAN EDITION! 🔥"""

from __future__ import annotations

from typing import AsyncIterator, Protocol, runtime_checkable

from textual.command import Hit, Provider
from .tui_icons import Icons

# Visual category markers
CATEGORY_AGENT = "⚡ AGENT"
CATEGORY_MODE = "🎨 MODE"
CATEGORY_RULE = "📜 RULE"
CATEGORY_VIEW = "👁️  VIEW"
CATEGORY_SYSTEM = "⚙️  SYSTEM"


@runtime_checkable
class _CommandApp(Protocol):
    current_view: str
    status_message: str

    def update_view(self) -> None:
        ...

    def load_scenarios(self) -> None:
        ...


class AgentCommandProvider(Provider):
    """Command provider for agent-related commands - SUPER SAIYAN MODE! ⚡"""

    async def discover(self) -> AsyncIterator[Hit]:
        """Show default commands with MAXIMUM VISUAL IMPACT!"""
        # Category: Agent Management
        yield Hit(
            1.0,
            f"[reverse][bold yellow]━━━ {CATEGORY_AGENT} MANAGEMENT ━━━━━━━━━━━━━━━━━━━[/bold yellow][/reverse]",
            lambda: None,
            help="[dim italic]Control and manage your AI agents[/dim italic]",
        )

    async def search(self, query: str) -> AsyncIterator[Hit]:
        """Search for agent commands with ULTRA styling!

        Args:
            query: The search query from the command palette

        Yields:
            Matching commands with MAXIMUM VISUAL FLAIR
        """
        matcher = self.matcher(query)

        # Define all agent commands with refined visual styling
        commands = [
            # ═══════════════════════════════════════════════════════
            # AGENT MANAGEMENT - Refined & Professional
            # ═══════════════════════════════════════════════════════
            (
                f"[cyan]🚀[/] [bold]Show Agents[/bold] [dim cyan]⚡[/dim cyan]",
                f"[dim]View and manage all agents [dim white]│[/dim white] Hotkey: [yellow]2[/yellow] [dim white]│[/dim white] Status: [green]●[/green] Active[/dim]",
                "show_agents",
                CATEGORY_AGENT,
            ),
            (
                f"[green]▶[/] [bold]Activate Agent[/bold] [dim green]✓[/dim green]",
                f"[dim]Power up an agent [dim white]│[/dim white] Action: [white]Space[/white] to toggle [dim white]│[/dim white] Target: Selected agent[/dim]",
                "activate_agent",
                CATEGORY_AGENT,
            ),
            (
                f"[red]■[/] [bold]Deactivate Agent[/bold] [dim red]✗[/dim red]",
                f"[dim]Power down an agent [dim white]│[/dim white] Action: [white]Space[/white] to toggle [dim white]│[/dim white] Safety: Confirmed[/dim]",
                "deactivate_agent",
                CATEGORY_AGENT,
            ),
            # ═══════════════════════════════════════════════════════
            # MODE MANAGEMENT - Behavioral Control
            # ═══════════════════════════════════════════════════════
            (
                f"[magenta]🎨[/] [bold]Show Modes[/bold] [dim magenta]◆[/dim magenta]",
                f"[dim]View behavioral modes [dim white]│[/dim white] Hotkey: [yellow]3[/yellow] [dim white]│[/dim white] Config: [dim yellow]⚙[/dim yellow] Live[/dim]",
                "show_modes",
                CATEGORY_MODE,
            ),
            (
                f"[yellow]⟳[/] [bold]Toggle Mode[/bold] [dim yellow]⚡[/dim yellow]",
                f"[dim]Switch mode state [dim white]│[/dim white] Action: [white]Space[/white] [dim white]│[/dim white] Effect: [cyan]Instant[/cyan][/dim]",
                "toggle_mode",
                CATEGORY_MODE,
            ),
            # ═══════════════════════════════════════════════════════
            # RULE MANAGEMENT - Policy Enforcement
            # ═══════════════════════════════════════════════════════
            (
                f"[blue]📜[/] [bold]Show Rules[/bold] [dim blue]⚖[/dim blue]",
                f"[dim]View rule modules [dim white]│[/dim white] Hotkey: [yellow]4[/yellow] [dim white]│[/dim white] Priority: [dim red]High[/dim red][/dim]",
                "show_rules",
                CATEGORY_RULE,
            ),
            (
                f"[yellow]⟳[/] [bold]Toggle Rule[/bold] [dim yellow]⚡[/dim yellow]",
                f"[dim]Modify rule state [dim white]│[/dim white] Action: [white]Space[/white] [dim white]│[/dim white] Scope: [cyan]Global[/cyan][/dim]",
                "toggle_rule",
                CATEGORY_RULE,
            ),
            # ═══════════════════════════════════════════════════════
            # SYSTEM VIEWS - Monitoring & Control
            # ═══════════════════════════════════════════════════════
            (
                f"[green]💎[/] [bold]Show Skills[/bold] [dim green]★[/dim green]",
                f"[dim]Browse skill library [dim white]│[/dim white] Hotkey: [yellow]5[/yellow] [dim white]│[/dim white] Count: [cyan]Available[/cyan][/dim]",
                "show_skills",
                CATEGORY_VIEW,
            ),
            (
                f"[blue]🗺[/] [bold]Show Scenarios[/bold] [dim blue]◎[/dim blue]",
                f"[dim]Review crisis scenarios [dim white]│[/dim white] Hotkey: [yellow]S[/yellow] [dim white]│[/dim white] Mode: [cyan]Plan[/cyan][/dim]",
                "show_scenarios",
                CATEGORY_VIEW,
            ),
            (
                f"[cyan]⚙[/] [bold]Show Workflows[/bold] [dim cyan]↻[/dim cyan]",
                f"[dim]Monitor workflows [dim white]│[/dim white] Hotkey: [yellow]6[/yellow] [dim white]│[/dim white] Status: [green]Running[/green][/dim]",
                "show_workflows",
                CATEGORY_VIEW,
            ),
            (
                f"[green]🌿[/] [bold]Show Worktrees[/bold] [dim green]⎇[/dim green]",
                f"[dim]Manage git worktrees [dim white]│[/dim white] Hotkey: [yellow]C[/yellow] [dim white]│[/dim white] Status: [cyan]Repo[/cyan][/dim]",
                "show_worktrees",
                CATEGORY_VIEW,
            ),
            (
                f"[magenta]🎯[/] [bold]Orchestrate[/bold] [dim magenta]◈[/dim magenta]",
                f"[dim]Task orchestration [dim white]│[/dim white] Hotkey: [yellow]7[/yellow] [dim white]│[/dim white] Mode: [dim yellow]Auto[/dim yellow][/dim]",
                "show_orchestrate",
                CATEGORY_VIEW,
            ),
            (
                f"[white]⌘[/] [bold]Show Slash Commands[/bold] [dim white]╱[/dim white]",
                f"[dim]Browse slash command catalog [dim white]│[/dim white] Hotkey: [white]/[/white][/dim]",
                "show_commands",
                CATEGORY_VIEW,
            ),
            # ═══════════════════════════════════════════════════════
            # SYSTEM OPERATIONS - Core Functions
            # ═══════════════════════════════════════════════════════
            (
                f"[yellow]📦[/] [bold]Export Context[/bold] [dim yellow]↓[/dim yellow]",
                f"[dim]Export configuration [dim white]│[/dim white] Format: [cyan]YAML/JSON[/cyan] [dim white]│[/dim white] Target: [blue]File[/blue][/dim]",
                "export_context",
                CATEGORY_SYSTEM,
            ),
        ]

        # Search and yield matching commands with category grouping
        current_category = None
        for name, help_text, action, category in commands:
            if match := matcher.match(name):
                # Add category separator if category changes
                if current_category != category and not query:
                    current_category = category
                    # Don't yield category headers in search results

                # Create proper closure for action
                def make_callback(act: str):
                    def callback() -> None:
                        self._run_command(act)
                    return callback

                yield Hit(
                    match,
                    matcher.highlight(name),
                    make_callback(action),
                    help=help_text,
                )

    def _run_command(self, action: str) -> None:
        """Execute a command action.

        Args:
            action: The action identifier
        """
        app_obj = getattr(self, "app", None)
        if not isinstance(app_obj, _CommandApp):
            return
        app = app_obj

        if action == "show_agents":
            app.current_view = "agents"
            app.update_view()
        elif action == "activate_agent":
            app.current_view = "agents"
            app.update_view()
            app.status_message = "Select an agent and press Space to activate"
        elif action == "deactivate_agent":
            app.current_view = "agents"
            app.update_view()
            app.status_message = "Select an agent and press Space to deactivate"
        elif action == "show_modes":
            app.current_view = "modes"
            app.update_view()
        elif action == "toggle_mode":
            app.current_view = "modes"
            app.update_view()
            app.status_message = "Select a mode and press Space to toggle"
        elif action == "show_rules":
            app.current_view = "rules"
            app.update_view()
        elif action == "toggle_rule":
            app.current_view = "rules"
            app.update_view()
            app.status_message = "Select a rule and press Space to toggle"
        elif action == "show_skills":
            app.current_view = "skills"
            app.update_view()
        elif action == "show_scenarios":
            app.current_view = "scenarios"
            app.load_scenarios()
            app.update_view()
        elif action == "show_workflows":
            app.current_view = "workflows"
            app.update_view()
        elif action == "show_worktrees":
            app.current_view = "worktrees"
            if hasattr(app, "load_worktrees"):
                app.load_worktrees()
            app.update_view()
        elif action == "show_orchestrate":
            app.current_view = "orchestrate"
            app.update_view()
        elif action == "show_commands":
            app.current_view = "commands"
            if hasattr(app, "load_slash_commands"):
                app.load_slash_commands()
            app.update_view()
        elif action == "export_context":
            app.current_view = "export"
            app.update_view()
