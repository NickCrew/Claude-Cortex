"""Textual command providers for AgentTUI - SUPER SAIYAN EDITION! 🔥"""

from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, Optional, runtime_checkable, Callable

from textual.command import Hit, Provider
from .tui_icons import Icons

# Visual category markers
CATEGORY_AGENT = "⚡ AGENT"
CATEGORY_MODE = "🎨 MODE"
CATEGORY_RULE = "📜 RULE"
CATEGORY_VIEW = "👁️  VIEW"
CATEGORY_CONFIG = "⚙️  CONFIG"
CATEGORY_TOOLS = "🛠️  TOOLS"
CATEGORY_SYSTEM = "💻 SYSTEM"


@runtime_checkable
class _CommandApp(Protocol):
    current_view: str
    status_message: str

    def update_view(self) -> None:
        ...

    def load_scenarios(self) -> None:
        ...

    def load_worktrees(self) -> None:
        ...

    def load_slash_commands(self) -> None:
        ...

    def push_screen(self, screen: Any, callback: Optional[Callable[[Any], None]] = None) -> None:
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
            (
                f"[magenta]✦[/] [bold]Agent Galaxy[/bold] [dim magenta]🌌[/dim magenta]",
                f"[dim]Visualize agent dependencies [dim white]│[/dim white] Hotkey: [yellow]g[/yellow][/dim]",
                "show_galaxy",
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
            (
                f"[cyan]📖[/] [bold]Show Principles[/bold] [dim cyan]📜[/dim cyan]",
                f"[dim]View guidance principles [dim white]│[/dim white] Hotkey: [yellow]p[/yellow][/dim]",
                "show_principles",
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
            (
                f"[yellow]📝[/] [bold]Show Tasks[/bold] [dim yellow]✅[/dim yellow]",
                f"[dim]View active agent tasks [dim white]│[/dim white] Hotkey: [yellow]t[/yellow][/dim]",
                "show_tasks",
                CATEGORY_VIEW,
            ),
            # ═══════════════════════════════════════════════════════
            # AI & INTELLIGENCE
            # ═══════════════════════════════════════════════════════
            (
                f"[bright_magenta]🤖[/] [bold]AI Assistant[/bold] [dim bright_magenta]✨[/dim bright_magenta]",
                f"[dim]Get AI recommendations [dim white]│[/dim white] Hotkey: [yellow]0[/yellow][/dim]",
                "show_ai_assistant",
                CATEGORY_VIEW,
            ),
            (
                f"[bright_magenta]📝[/] [bold]Request Reviews[/bold] [dim bright_magenta]⚑[/dim bright_magenta]",
                f"[dim]Spawn review tasks from recommendations [dim white]│[/dim white] Hotkey: [yellow]Y[/yellow][/dim]",
                "request_reviews",
                CATEGORY_VIEW,
            ),
            (
                f"[bright_magenta]✨[/] [bold]Consult Gemini[/bold] [dim bright_magenta]◆[/dim bright_magenta]",
                f"[dim]Ask Gemini for a second opinion [dim white]│[/dim white] Hotkey: [yellow]G[/yellow][/dim]",
                "consult_gemini",
                CATEGORY_VIEW,
            ),
            (
                f"[bright_magenta]🧠[/] [bold]Assign LLM Tasks[/bold] [dim bright_magenta]◆[/dim bright_magenta]",
                f"[dim]Dispatch tasks to Gemini/OpenAI/Qwen [dim white]│[/dim white] Hotkey: [yellow]K[/yellow][/dim]",
                "assign_llm_tasks",
                CATEGORY_VIEW,
            ),
            (
                f"[cyan]👁️[/] [bold]Watch Mode[/bold] [dim cyan]🔍[/dim cyan]",
                f"[dim]Monitor repo changes [dim white]│[/dim white] Hotkey: [yellow]w[/yellow][/dim]",
                "show_watch_mode",
                CATEGORY_VIEW,
            ),
            # ═══════════════════════════════════════════════════════
            # CONFIGURATION & ASSETS
            # ═══════════════════════════════════════════════════════
            (
                f"[yellow]🚩[/] [bold]Flag Explorer[/bold] [dim yellow]⚐[/dim yellow]",
                f"[dim]Browse behavior flags [dim white]│[/dim white] Hotkey: [yellow]F[/yellow][/dim]",
                "show_flags",
                CATEGORY_CONFIG,
            ),
            (
                f"[bright_blue]⚙️[/] [bold]Flag Manager[/bold] [dim bright_blue]🛠[/dim bright_blue]",
                f"[dim]Manage flag files [dim white]│[/dim white] Hotkey: [yellow]Ctrl+G[/yellow][/dim]",
                "show_flag_manager",
                CATEGORY_CONFIG,
            ),
            (
                f"[green]📦[/] [bold]Asset Manager[/bold] [dim green]↓[/dim green]",
                f"[dim]Install plugin assets [dim white]│[/dim white] Hotkey: [yellow]A[/yellow][/dim]",
                "show_assets",
                CATEGORY_CONFIG,
            ),
            (
                f"[blue]👤[/] [bold]Profiles[/bold] [dim blue]👥[/dim blue]",
                f"[dim]Switch config profiles [dim white]│[/dim white] Hotkey: [yellow]8[/yellow][/dim]",
                "show_profiles",
                CATEGORY_CONFIG,
            ),
            # ═══════════════════════════════════════════════════════
            # TOOLS & UTILITIES
            # ═══════════════════════════════════════════════════════
            (
                f"[bright_magenta]🧠[/] [bold]Memory Vault[/bold] [dim bright_magenta]✦[/dim bright_magenta]",
                f"[dim]Browse memory notes [dim white]│[/dim white] Hotkey: [magenta]M[/magenta] or [magenta]Ctrl+M[/magenta][/dim]",
                "show_memory",
                CATEGORY_TOOLS,
            ),
            (
                f"[cyan]🔌[/] [bold]MCP Servers[/bold] [dim cyan]⚡[/dim cyan]",
                f"[dim]Manage MCP integrations [dim white]│[/dim white] Hotkey: [yellow]7[/yellow][/dim]",
                "show_mcp",
                CATEGORY_TOOLS,
            ),
            (
                f"[blue]📎[/] [bold]Hooks Manager[/bold] [dim blue]⚓[/dim blue]",
                f"[dim]Configure automation hooks [dim white]│[/dim white] Hotkey: [yellow]h[/yellow][/dim]",
                "show_hooks",
                CATEGORY_TOOLS,
            ),
            (
                f"[yellow]💾[/] [bold]Backup Manager[/bold] [dim yellow]📥[/dim yellow]",
                f"[dim]Snapshot context state [dim white]│[/dim white] Hotkey: [yellow]b[/yellow][/dim]",
                "show_backups",
                CATEGORY_TOOLS,
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
            (
                f"[green]🧙[/] [bold]Init Wizard[/bold] [dim green]✨[/dim green]",
                f"[dim]Start project setup [dim white]│[/dim white] Hotkey: [white]I[/white] (in Profiles)[/dim]",
                "run_init_wizard",
                CATEGORY_SYSTEM,
            ),
            (
                f"[cyan]🩺[/] [bold]Health Check[/bold] [dim cyan]✚[/dim cyan]",
                f"[dim]Run doctor diagnostics [dim white]│[/dim white] Hotkey: [white]c[/white] (in Profiles)[/dim]",
                "run_health_check",
                CATEGORY_SYSTEM,
            ),
            (
                f"[blue]🔄[/] [bold]Setup Migration[/bold] [dim blue]⟳[/dim blue]",
                f"[dim]Migrate activation files [dim white]│[/dim white] Hotkey: [white]M[/white] (in Profiles)[/dim]",
                "run_migration",
                CATEGORY_SYSTEM,
            ),
            (
                f"[white]❓[/] [bold]Help[/bold] [dim white]ℹ[/dim white]",
                f"[dim]Show keyboard shortcuts [dim white]│[/dim white] Hotkey: [yellow]?[/yellow][/dim]",
                "show_help",
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
                def make_callback(act: str) -> Callable[[], None]:
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
        elif action == "show_galaxy":
            app.current_view = "galaxy"
            app.update_view()
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
        elif action == "show_principles":
            app.current_view = "principles"
            app.update_view()
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
        elif action == "show_tasks":
            app.current_view = "tasks"
            app.update_view()
        elif action == "show_ai_assistant":
            app.current_view = "ai_assistant"
            app.update_view()
        elif action == "request_reviews":
            if hasattr(app, "action_request_reviews"):
                getattr(app, "action_request_reviews")()
        elif action == "consult_gemini":
            if hasattr(app, "action_consult_gemini"):
                getattr(app, "action_consult_gemini")()
        elif action == "assign_llm_tasks":
            if hasattr(app, "action_assign_llm_tasks"):
                getattr(app, "action_assign_llm_tasks")()
        elif action == "show_watch_mode":
            app.current_view = "watch_mode"
            app.update_view()
        elif action == "show_flags":
            app.current_view = "flags"
            app.update_view()
        elif action == "show_flag_manager":
            app.current_view = "flag_manager"
            app.update_view()
        elif action == "show_assets":
            app.current_view = "assets"
            app.update_view()
        elif action == "show_profiles":
            app.current_view = "profiles"
            app.update_view()
        elif action == "show_mcp":
            app.current_view = "mcp"
            app.update_view()
        elif action == "show_hooks":
            if hasattr(app, "action_hooks_manager"):
                getattr(app, "action_hooks_manager")()
        elif action == "show_backups":
            if hasattr(app, "action_backup_manager"):
                getattr(app, "action_backup_manager")()
        elif action == "export_context":
            app.current_view = "export"
            app.update_view()
        elif action == "show_memory":
            if hasattr(app, "push_screen"):
                try:
                    from .tui_memory import MemoryScreen
                    # app is typed as _CommandApp but at runtime it is the App instance
                    # We need to ignore type checking for this dynamic call
                    getattr(app, "push_screen")(MemoryScreen())
                except ImportError:
                    # Fallback to standard memory view if dedicated screen is missing
                    app.current_view = "memory"
                    app.update_view()
                except Exception as e:
                    app.status_message = f"Error opening memory: {e}"
        elif action == "run_init_wizard":
            if hasattr(app, "action_setup_init_wizard"):
                getattr(app, "action_setup_init_wizard")()
        elif action == "run_health_check":
            if hasattr(app, "action_setup_health_check"):
                getattr(app, "action_setup_health_check")()
        elif action == "run_migration":
            if hasattr(app, "action_setup_migration"):
                getattr(app, "action_setup_migration")()
        elif action == "show_help":
            if hasattr(app, "action_help"):
                getattr(app, "action_help")()
