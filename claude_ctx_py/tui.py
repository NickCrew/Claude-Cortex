"""Terminal User Interface for claude-ctx using Rich library."""

from __future__ import annotations

import sys
import termios
import tty
import time
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn

from .core import (
    build_agent_graph,
    agent_activate,
    agent_deactivate,
    AgentGraphNode,
    _resolve_claude_dir,
    _iter_all_files,
    _agent_basename,
    _is_disabled,
    _extract_agent_name,
    _read_agent_front_matter_lines,
    _parse_dependencies_from_front,
    _tokenize_front_matter,
    _extract_scalar_from_paths,
    workflow_list,
    workflow_status,
    workflow_run,
    workflow_resume,
)
from .tui_extensions import ProfileViewMixin, ExportViewMixin, WizardViewMixin
from .tui_mcp import MCPViewMixin


@dataclass
class ViewState:
    """State for a specific view."""

    selected_index: int = 0
    scroll_offset: int = 0
    filter_text: str = ""
    show_details: bool = False


@dataclass
class TUIState:
    """State management for the TUI."""

    # Current view (1-9)
    current_view: str = "overview"

    # Global state
    agents: List[AgentGraphNode] = field(default_factory=list)
    status_message: str = "Welcome to claude-ctx TUI"
    show_help: bool = False

    # Per-view state
    view_states: Dict[str, ViewState] = field(default_factory=dict)

    # Navigation history
    view_history: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize mutable default values."""
        if not self.view_states:
            self.view_states = {
                "overview": ViewState(),
                "agents": ViewState(),
                "modes": ViewState(),
                "rules": ViewState(),
                "skills": ViewState(),
                "workflows": ViewState(),
                "orchestrate": ViewState(),
                "mcp": ViewState(),
                "profile": ViewState(),
                "export": ViewState(),
            }

    @property
    def current_state(self) -> ViewState:
        """Get the current view's state."""
        return self.view_states[self.current_view]

    @property
    def selected_index(self) -> int:
        """Get selected index for current view."""
        return self.current_state.selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        """Set selected index for current view."""
        self.current_state.selected_index = value

    @property
    def filter_text(self) -> str:
        """Get filter text for current view."""
        return self.current_state.filter_text

    @filter_text.setter
    def filter_text(self, value: str) -> None:
        """Set filter text for current view."""
        self.current_state.filter_text = value

    @property
    def show_details(self) -> bool:
        """Get show_details for current view."""
        return self.current_state.show_details

    @show_details.setter
    def show_details(self, value: bool) -> None:
        """Set show_details for current view."""
        self.current_state.show_details = value


class AgentTUI(ProfileViewMixin, ExportViewMixin, WizardViewMixin, MCPViewMixin):
    """Terminal User Interface for claude-ctx management."""

    def __init__(self) -> None:
        self.console = Console()
        self.state = TUIState()
        self.original_terminal_settings: Optional[list] = None

        # Initialize mixin attributes
        self.export_options = {
            "agents": True,
            "modes": True,
            "rules": True,
            "skills": False,
            "workflows": False,
        }
        self.wizard_active = False
        self.wizard_step = 0
        self.wizard_selections = {}

    def render(self) -> None:
        """Render the entire layout once without Live to avoid flicker."""
        self.console.clear()
        self.console.print(self.create_layout())

    def load_agents(self) -> None:
        """Load agents from the system."""
        try:
            # Load agents from all directories
            agents = []
            seen_names = set()  # Track agent names to avoid duplicates
            claude_dir = _resolve_claude_dir()

            # Check active agents
            agents_dir = claude_dir / "agents"
            if agents_dir.is_dir():
                for path in _iter_all_files(agents_dir):
                    if not path.name.endswith(".md") or _is_disabled(path):
                        continue
                    node = self._parse_agent_file(path, "active")
                    if node and node.name not in seen_names:
                        agents.append(node)
                        seen_names.add(node.name)

            # Check disabled agents
            disabled_dirs = [
                claude_dir / "agents-disabled",
                agents_dir / "disabled" if agents_dir.is_dir() else None,
            ]

            for disabled_dir in disabled_dirs:
                if disabled_dir and disabled_dir.is_dir():
                    for path in _iter_all_files(disabled_dir):
                        if not path.name.endswith(".md"):
                            continue
                        node = self._parse_agent_file(path, "disabled")
                        if node and node.name not in seen_names:
                            agents.append(node)
                            seen_names.add(node.name)

            # Sort by category and name
            agents.sort(key=lambda a: (a.category, a.name.lower()))

            self.state.agents = agents
            if not self.state.agents:
                self.state.status_message = "No agents found"
            else:
                active_count = sum(1 for a in agents if a.status == "active")
                self.state.status_message = (
                    f"Loaded {len(self.state.agents)} agents "
                    f"({active_count} active, {len(agents) - active_count} inactive)"
                )
        except Exception as e:
            self.state.status_message = f"Error loading agents: {e}"
            self.state.agents = []

    # Skills Management Methods

    def load_skills(self) -> None:
        """Load skills from the system."""
        try:
            skills = []
            claude_dir = _resolve_claude_dir()
            skills_dir = claude_dir / "skills"

            if not skills_dir.is_dir():
                self.state.status_message = "No skills directory found"
                self.state.skills = []
                return

            # Load metrics
            try:
                metrics = get_all_metrics()
            except Exception:
                metrics = {}

            # Iterate through skill directories
            for skill_path in sorted(skills_dir.iterdir()):
                if not skill_path.is_dir():
                    continue

                skill_file = skill_path / "SKILL.md"
                if not skill_file.is_file():
                    continue

                skill_name = skill_path.name

                try:
                    # Read skill file
                    content = skill_file.read_text(encoding="utf-8")
                    front_matter = _extract_front_matter(content)

                    if front_matter:
                        lines = front_matter.strip().splitlines()
                        tokens = _tokenize_front_matter(lines)

                        description = _extract_scalar_from_paths(
                            tokens, (("description",),)
                        ) or "No description"

                        category = _extract_scalar_from_paths(
                            tokens, (("category",),)
                        ) or "general"
                    else:
                        description = "No description"
                        category = "general"

                    # Get metrics if available
                    skill_metrics = metrics.get(skill_name, {})
                    uses = skill_metrics.get("activation_count", 0)
                    last_used = skill_metrics.get("last_activated")
                    tokens_saved = skill_metrics.get("total_tokens_saved", 0)
                    success_rate = skill_metrics.get("success_rate", 0.0)

                    skills.append(
                        SkillInfo(
                            name=skill_name,
                            description=description,
                            category=category,
                            uses=uses,
                            last_used=last_used,
                            tokens_saved=tokens_saved,
                            success_rate=success_rate,
                            is_community=False,
                            installed=True,
                        )
                    )

                except Exception:
                    # Skip skills that fail to parse
                    continue

            # Sort by uses (most used first), then by name
            skills.sort(key=lambda s: (-s.uses, s.name.lower()))

            self.state.skills = skills
            self.state.status_message = f"Loaded {len(skills)} skills"

        except Exception as e:
            self.state.status_message = f"Error loading skills: {e}"
            self.state.skills = []


    def get_filtered_skills(self) -> List[SkillInfo]:
        """Get skills filtered by current filter text."""
        if not self.state.filter_text:
            return self.state.skills

        filter_lower = self.state.filter_text.lower()
        return [
            skill
            for skill in self.state.skills
            if filter_lower in skill.name.lower()
            or filter_lower in skill.description.lower()
            or filter_lower in skill.category.lower()
        ]


    def create_skills_table(self) -> Table:
        """Create the skills list table."""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", width=15, no_wrap=True)
        table.add_column("Uses", width=8, no_wrap=True, justify="right")
        table.add_column("Last Used", width=20, no_wrap=True)
        table.add_column("Tokens Saved", width=15, no_wrap=True, justify="right")

        filtered_skills = self.get_filtered_skills()

        if not filtered_skills:
            table.add_row("", "No skills found", "", "", "", "")
            return table

        for idx, skill in enumerate(filtered_skills):
            # Determine if this row is selected
            is_selected = idx == self.state.selected_index

            # Selection indicator
            indicator = ">" if is_selected else ""

            # Format last used date
            if skill.last_used:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(skill.last_used.replace("Z", "+00:00"))
                    last_used_str = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, AttributeError):
                    last_used_str = skill.last_used[:16]
            else:
                last_used_str = "Never"

            # Format tokens saved
            tokens_str = f"{skill.tokens_saved:,}" if skill.tokens_saved > 0 else "-"

            # Row style
            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                skill.name,
                skill.category,
                str(skill.uses),
                last_used_str,
                tokens_str,
                style=row_style,
            )

        return table


    def create_skills_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected skill."""
        if self.state.skills_view_mode != "details":
            return None

        filtered_skills = self.get_filtered_skills()
        if not filtered_skills or self.state.selected_index >= len(filtered_skills):
            return None

        skill = filtered_skills[self.state.selected_index]

        details = Text()
        details.append("Skill: ", style="bold")
        details.append(f"{skill.name}\n\n")

        details.append("Description:\n", style="bold")
        details.append(f"  {skill.description}\n\n")

        details.append("Category: ", style="bold")
        details.append(f"{skill.category}\n")

        details.append("Statistics:\n", style="bold")
        details.append(f"  Uses: {skill.uses}\n")
        details.append(f"  Tokens Saved: {skill.tokens_saved:,}\n")
        details.append(f"  Success Rate: {skill.success_rate:.1%}\n")
        details.append(f"  Last Used: {skill.last_used or 'Never'}\n")

        if skill.is_community:
            details.append("\nCommunity Info:\n", style="bold")
            details.append(f"  Author: {skill.author or 'Unknown'}\n")
            if skill.rating:
                stars = "★" * int(skill.rating) + "☆" * (5 - int(skill.rating))
                details.append(f"  Rating: {stars} ({skill.rating:.1f}/5)\n")
            details.append(f"  Installed: {'Yes' if skill.installed else 'No'}\n")

        return Panel(details, title="Skill Details", border_style="cyan")


    def create_skills_metrics_panel(self) -> Panel:
        """Create metrics panel for selected skill."""
        filtered_skills = self.get_filtered_skills()
        if not filtered_skills or self.state.selected_index >= len(filtered_skills):
            return Panel(
                Text("No skill selected", style="yellow"),
                title="Metrics",
                border_style="yellow"
            )

        skill = filtered_skills[self.state.selected_index]

        # Get detailed metrics
        try:
            skill_metrics = get_skill_metrics(skill.name)
            if not skill_metrics:
                return Panel(
                    Text(f"No metrics available for {skill.name}", style="yellow"),
                    title="Metrics",
                    border_style="yellow"
                )

            metrics_text = Text()
            metrics_text.append(f"Skill: {skill.name}\n\n", style="bold cyan")

            metrics_text.append("Usage Statistics:\n", style="bold")
            metrics_text.append(f"  Activation Count: {skill_metrics.get('activation_count', 0)}\n")
            metrics_text.append(f"  Total Tokens Saved: {skill_metrics.get('total_tokens_saved', 0):,}\n")
            metrics_text.append(f"  Average Tokens: {skill_metrics.get('avg_tokens', 0):,}\n")
            metrics_text.append(f"  Success Rate: {skill_metrics.get('success_rate', 0):.1%}\n\n")

            last_activated = skill_metrics.get("last_activated")
            if last_activated:
                metrics_text.append("Last Activation:\n", style="bold")
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_activated.replace("Z", "+00:00"))
                    metrics_text.append(f"  {dt.strftime('%Y-%m-%d %H:%M:%S')}\n")
                except (ValueError, AttributeError):
                    metrics_text.append(f"  {last_activated}\n")

            return Panel(metrics_text, title="Detailed Metrics", border_style="green")

        except Exception as e:
            return Panel(
                Text(f"Error loading metrics: {e}", style="red"),
                title="Metrics Error",
                border_style="red"
            )


    def create_community_skills_table(self) -> Table:
        """Create community skills browser table."""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Author", width=20, no_wrap=True)
        table.add_column("Rating", width=12, no_wrap=True)
        table.add_column("Status", width=12, no_wrap=True)
        table.add_column("Description", width=40)

        # This would need to fetch community skills
        # For now, show placeholder
        table.add_row("", "Loading...", "", "", "", "Community skills browser coming soon")

        return table


    def validate_selected_skill(self) -> None:
        """Validate the selected skill."""
        filtered_skills = self.get_filtered_skills()
        if not filtered_skills or self.state.selected_index >= len(filtered_skills):
            self.state.status_message = "No skill selected"
            return

        skill = filtered_skills[self.state.selected_index]

        try:
            # Call validation
            exit_code, message = skill_validate(skill.name)

            # Clean ANSI codes
            import re
            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)

            # Show first line in status
            self.state.status_message = clean_message.split("\n")[0]

            # If validation failed, could show full results in a panel
            # For now, just update status message

        except Exception as e:
            self.state.status_message = f"Validation error: {e}"


    def toggle_skills_view_mode(self, mode: str) -> None:
        """Switch between different skills view modes."""
        if mode in ["local", "community", "details", "metrics", "validate"]:
            self.state.skills_view_mode = mode
            self.state.status_message = f"Switched to {mode} view"
        else:
            self.state.status_message = f"Unknown view mode: {mode}"


    def handle_skills_key(self, key: str) -> bool:
        """Handle key presses specific to skills view.

        Returns True if key was handled, False otherwise.
        """
        if key == "v":
            self.validate_selected_skill()
            return True
        elif key == "m":
            if self.state.skills_view_mode == "metrics":
                self.toggle_skills_view_mode("local")
            else:
                self.toggle_skills_view_mode("metrics")
            return True
        elif key == "c":
            if self.state.skills_view_mode == "community":
                self.toggle_skills_view_mode("local")
            else:
                self.toggle_skills_view_mode("community")
                self.state.status_message = "Community skills browser not yet implemented"
            return True
        elif key == "\r" or key == "\n":
            # Toggle details mode
            if self.state.skills_view_mode == "details":
                self.toggle_skills_view_mode("local")
                self.state.show_details = False
            else:
                self.toggle_skills_view_mode("details")
                self.state.show_details = True
            return True

        return False  # Key not handled


    def _parse_agent_file(self, path: Path, status: str) -> Optional[AgentGraphNode]:
        """Parse an agent file and return an AgentGraphNode."""
        try:
            lines = _read_agent_front_matter_lines(path)
            if not lines:
                return None

            name = _extract_agent_name(path, lines)

            tokens = _tokenize_front_matter(lines)

            # Extract category (default to "general")
            category = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "category"),
                    ("category",),
                ),
            ) or "general"

            # Extract tier (default to "standard")
            tier = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "tier", "id"),
                    ("tier", "id"),
                ),
            ) or "standard"

            # Extract dependencies
            requires_raw, recommends_raw = _parse_dependencies_from_front(lines)
            requires = [item for item in requires_raw if item]
            recommends = [item for item in recommends_raw if item]

            return AgentGraphNode(
                name=name,
                slug=path.stem,
                category=category,
                tier=tier,
                status=status,
                requires=requires,
                recommends=recommends,
            )
        except Exception:
            # Skip agents that fail to parse
            return None

    def switch_view(self, view_name: str) -> None:
        """Switch to a different view."""
        if view_name in self.state.view_states:
            # Save current view to history
            if self.state.current_view != view_name:
                self.state.view_history.append(self.state.current_view)
                # Keep history to max 20 items
                if len(self.state.view_history) > 20:
                    self.state.view_history.pop(0)

            self.state.current_view = view_name
            self.state.show_help = False
            self.state.show_details = False
            self.state.status_message = f"Switched to {view_name.title()} view"

    def get_filtered_agents(self) -> List[AgentGraphNode]:
        """Get agents filtered by current filter text."""
        if not self.state.filter_text:
            return self.state.agents

        filter_lower = self.state.filter_text.lower()
        return [
            agent
            for agent in self.state.agents
            if filter_lower in agent.name.lower()
            or filter_lower in agent.category.lower()
            or filter_lower in agent.tier.lower()
        ]

    def create_header(self) -> Panel:
        """Create the header panel."""
        # Map view names to display names
        view_names = {
            "overview": "Overview",
            "agents": "Agents",
            "modes": "Modes",
            "rules": "Rules",
            "skills": "Skills",
            "workflows": "Workflows",
            "orchestrate": "Orchestrate",
            "profile": "Profile",
            "export": "Export",
        }

        view_display = view_names.get(self.state.current_view, self.state.current_view)
        title = Text(f"claude-ctx: {view_display}", style="bold cyan")
        subtitle = Text("Press 1-9 for views, '?' for help, 'q' to quit", style="dim")
        content = Text()
        content.append(title)
        content.append("\n")
        content.append(subtitle)

        return Panel(content, style="bold blue", padding=(0, 1))

    def create_overview_view(self) -> Panel:
        """Create the overview dashboard."""
        content = Text()

        content.append("Claude Context Overview\n", style="bold cyan")
        content.append("━" * 50 + "\n\n", style="dim")

        # System Status
        content.append("System Status:\n", style="bold yellow")

        # Agent stats
        active_agents = sum(1 for a in self.state.agents if a.status == "active")
        total_agents = len(self.state.agents)
        content.append(f"  Agents:    ", style="bold")
        content.append(f"{active_agents}/{total_agents} active  ", style="green")
        content.append("[Press 2 to manage]\n", style="dim")

        # Modes (placeholder)
        content.append(f"  Modes:     ", style="bold")
        content.append(f"3/8 active   ", style="green")
        content.append("[Press 3 to manage]\n", style="dim")

        # Rules (placeholder)
        content.append(f"  Rules:     ", style="bold")
        content.append(f"5/12 active  ", style="green")
        content.append("[Press 4 to manage]\n", style="dim")

        # Skills (placeholder)
        content.append(f"  Skills:    ", style="bold")
        content.append(f"15 installed ", style="cyan")
        content.append("[Press 5 to manage]\n\n", style="dim")

        # Active Workflows
        content.append("Active Workflows:\n", style="bold yellow")
        content.append("  • No active workflows\n", style="dim")
        content.append("  [Press 6 to manage workflows]\n\n", style="dim")

        # Quick Actions
        content.append("Quick Actions:\n", style="bold yellow")
        content.append("  i - Initialize new project\n")
        content.append("  r - Refresh all systems\n")
        content.append("  ? - Show help\n")

        return Panel(content, title="Overview", border_style="cyan", expand=True)

    def create_placeholder_view(self, view_name: str) -> Panel:
        """Create a placeholder for unimplemented views."""
        content = Text()
        content.append(f"{view_name.title()} View\n\n", style="bold cyan")
        content.append("This view is under construction.\n\n", style="yellow")
        content.append("Press 1-9 to switch views\n", style="dim")
        content.append("Press ? for help\n", style="dim")

        return Panel(content, title=view_name.title(), border_style="yellow")

    def create_agent_table(self) -> Table:
        """Create the agent list table."""
        table = Table(
            title="Agents",
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
            title_style="bold cyan",
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", width=10, no_wrap=True)
        table.add_column("Category", width=15, no_wrap=True)
        table.add_column("Tier", width=10, no_wrap=True)
        table.add_column("Requires", width=20)

        filtered_agents = self.get_filtered_agents()

        if not filtered_agents:
            table.add_row("", "No agents found", "", "", "", "")
            return table

        # Limit visible items to fit on screen (show ~8 items max)
        max_visible = 8
        total_agents = len(filtered_agents)
        selected = self.state.selected_index

        # Calculate window start and end
        if total_agents <= max_visible:
            start_idx = 0
            end_idx = total_agents
        else:
            # Center the selected item
            half_window = max_visible // 2
            start_idx = max(0, selected - half_window)
            end_idx = min(total_agents, start_idx + max_visible)
            # Adjust if we're near the end
            if end_idx == total_agents:
                start_idx = max(0, total_agents - max_visible)

        visible_agents = filtered_agents[start_idx:end_idx]

        for idx, agent in enumerate(visible_agents):
            actual_idx = start_idx + idx
            # Determine if this row is selected
            is_selected = actual_idx == self.state.selected_index

            # Selection indicator
            indicator = ">" if is_selected else ""

            # Status styling
            if agent.status == "active":
                status_text = Text("Active", style="bold green")
            else:
                status_text = Text("Inactive", style="yellow")

            # Format requires
            requires_text = ", ".join(agent.requires) if agent.requires else "-"

            # Row style
            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                agent.name,
                status_text,
                agent.category,
                agent.tier,
                requires_text,
                style=row_style,
            )

        return table

    def create_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected agent."""
        if not self.state.show_details:
            return None

        filtered_agents = self.get_filtered_agents()
        if not filtered_agents or self.state.selected_index >= len(filtered_agents):
            return None

        agent = filtered_agents[self.state.selected_index]

        details = Text()
        details.append(f"Name: ", style="bold")
        details.append(f"{agent.name}\n")

        details.append(f"Status: ", style="bold")
        status_style = "green" if agent.status == "active" else "yellow"
        details.append(f"{agent.status}\n", style=status_style)

        details.append(f"Category: ", style="bold")
        details.append(f"{agent.category}\n")

        details.append(f"Tier: ", style="bold")
        details.append(f"{agent.tier}\n")

        details.append(f"Requires: ", style="bold")
        requires = ", ".join(agent.requires) if agent.requires else "None"
        details.append(f"{requires}\n")

        details.append(f"Recommends: ", style="bold")
        recommends = ", ".join(agent.recommends) if agent.recommends else "None"
        details.append(f"{recommends}\n")

        return Panel(details, title="Agent Details", border_style="cyan")

    def create_help_panel(self) -> Panel:
        """Create the comprehensive help panel."""
        help_text = Text()

        # Header
        help_text.append("═" * 63 + "\n", style="bold blue")
        help_text.append("         CLAUDE CONTEXT TUI - KEYBOARD REFERENCE\n", style="bold cyan")
        help_text.append("═" * 63 + "\n\n", style="bold blue")

        # View Navigation
        help_text.append("VIEWS (1-9)       │ NAVIGATION     │ ACTIONS\n", style="bold yellow")
        help_text.append("─" * 63 + "\n", style="dim")
        help_text.append("1  Overview       │ ↑/k  Up        │ Space  Toggle\n")
        help_text.append("2  Agents         │ ↓/j  Down      │ Enter  Details\n")
        help_text.append("3  Modes          │ PgUp Page up   │ /      Filter\n")
        help_text.append("4  Rules          │ PgDn Page down │ r      Refresh\n")
        help_text.append("5  Skills         │ Home Top       │ i      Init\n")
        help_text.append("6  Workflows      │ End  Bottom    │ ?      Help\n")
        help_text.append("7  MCP Servers    │                │ q      Quit\n")
        help_text.append("8  Orchestrate    │                │\n")
        help_text.append("9  Profile        │                │\n")
        help_text.append("0  Export         │                │\n")
        help_text.append("─" * 63 + "\n\n", style="dim")

        # Context-Specific Keys
        help_text.append("CONTEXT-SPECIFIC KEYS (depend on current view)\n", style="bold yellow")
        help_text.append("─" * 63 + "\n", style="dim")
        help_text.append("Agents:      Space=toggle, Enter=details, /=filter\n")
        help_text.append("Modes:       Space=toggle, Enter=details, /=filter\n")
        help_text.append("Skills:      v=validate, m=metrics, c=community\n")
        help_text.append("Workflows:   r=run, Space=resume, s=stop\n")
        help_text.append("MCP:         t=test, d=docs, c=copy, v=validate, r=reload\n")
        help_text.append("Profile:     n=new, e=edit, d=delete\n")
        help_text.append("Export:      e=export, f=format, p=clipboard\n")
        help_text.append("─" * 63 + "\n", style="dim")

        return Panel(help_text, title="Help", border_style="yellow", padding=(1, 2))

    def create_footer(self) -> Panel:
        """Create the footer with status and view hints."""
        content = Text()

        # View-specific help hints
        view_hints = {
            "overview": "Press 1-9 to navigate to specific views",
            "agents": "Space=toggle, Enter=details, /=filter",
            "modes": "Space=toggle, Enter=details, /=filter",
            "rules": "Space=toggle, Enter=details, /=filter",
            "skills": "v=validate, m=metrics, c=community",
            "workflows": "r=run, Space=resume, s=stop",
            "mcp": "Enter=details, t=test, d=docs, c=copy, v=validate, r=reload",
            "orchestrate": "View parallel execution status",
            "profile": "n=new, e=edit, d=delete",
            "export": "e=export, f=format, p=clipboard",
        }

        # Current view indicator
        content.append(f"[View: {self.state.current_view.title()}] ", style="bold cyan")

        # View-specific hint
        hint = view_hints.get(self.state.current_view, "")
        if hint:
            content.append(hint, style="dim")
            content.append(" | ", style="dim")

        # Status message
        if self.state.status_message:
            content.append(f"Status: {self.state.status_message}", style="bold")

        # Filter indicator
        if self.state.filter_text:
            content.append(" | ", style="dim")
            content.append(f"Filter: {self.state.filter_text}", style="cyan")

        # Agent count (only in agents view)
        if self.state.current_view == "agents":
            filtered_count = len(self.get_filtered_agents())
            total_count = len(self.state.agents)
            if filtered_count > 0:
                content.append(" | ", style="dim")
                if self.state.filter_text and filtered_count != total_count:
                    content.append(f"Showing {filtered_count}/{total_count} agents", style="dim")
                else:
                    content.append(f"{self.state.selected_index + 1}/{filtered_count} agents", style="dim")

        # Connection indicator
        content.append(" | ", style="dim")
        content.append("[●] ", style="green")
        content.append("Connected", style="dim")

        return Panel(content, style="bold green", padding=(0, 1))

    def create_layout(self) -> Layout:
        """Create the main layout."""
        layout = Layout()

        # Create main sections with flexible sizing
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body"),
            Layout(name="footer", size=4),
        )

        # Add content to sections
        layout["header"].update(self.create_header())
        layout["footer"].update(self.create_footer())

        # Route to appropriate view
        if self.state.show_help:
            layout["body"].update(self.create_help_panel())
        elif self.state.current_view == "overview":
            layout["body"].update(self.create_overview_view())
        elif self.state.current_view == "profile":
            layout["body"].update(self.render_profile_view())
        elif self.state.current_view == "export":
            layout["body"].update(self.render_export_view())
        elif self.state.current_view == "workflows":
            if self.state.show_details:
                layout["body"].split_row(
                    Layout(self.create_workflows_table()),
                    Layout(self.create_workflow_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(self.create_workflows_table())
        elif self.state.current_view == "orchestrate":
            layout["body"].update(self.create_orchestrate_view())
        elif self.state.current_view == "mcp":
            layout["body"].update(self.render_mcp_view())
        elif self.state.current_view == "modes":
            if self.state.show_details:
                layout["body"].split_row(
                    Layout(self.create_modes_table()),
                    Layout(self.create_mode_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(self.create_modes_table())
        elif self.state.current_view == "rules":
            if self.state.show_details:
                layout["body"].split_row(
                    Layout(self.create_rules_table()),
                    Layout(self.create_rule_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(self.create_rules_table())
        elif hasattr(self, 'wizard_active') and self.wizard_active:
            layout["body"].update(self.render_wizard_view())
        elif self.state.current_view == "agents":
            if self.state.show_details:
                layout["body"].split_row(
                    Layout(self.create_agent_table()),
                    Layout(self.create_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(self.create_agent_table())
        else:
            # Fallback to overview if unknown view
            layout["body"].update(self.create_overview_view())

        return layout

    def move_up(self) -> None:
        """Move selection up."""
        if self.state.current_view == "agents":
            filtered_agents = self.get_filtered_agents()
            if filtered_agents and self.state.selected_index > 0:
                self.state.selected_index -= 1
        elif self.state.current_view == "modes":
            filtered_modes = self.get_filtered_modes()
            if filtered_modes and self.state.selected_index > 0:
                self.state.selected_index -= 1
        elif self.state.current_view == "rules":
            filtered_rules = self.get_filtered_rules()
            if filtered_rules and self.state.selected_index > 0:
                self.state.selected_index -= 1
        elif self.state.current_view == "workflows":
            workflows = self.load_workflows()
            if workflows and self.state.selected_index > 0:
                self.state.selected_index -= 1

    def move_down(self) -> None:
        """Move selection down."""
        if self.state.current_view == "agents":
            filtered_agents = self.get_filtered_agents()
            if filtered_agents and self.state.selected_index < len(filtered_agents) - 1:
                self.state.selected_index += 1
        elif self.state.current_view == "modes":
            filtered_modes = self.get_filtered_modes()
            if filtered_modes and self.state.selected_index < len(filtered_modes) - 1:
                self.state.selected_index += 1
        elif self.state.current_view == "rules":
            filtered_rules = self.get_filtered_rules()
            if filtered_rules and self.state.selected_index < len(filtered_rules) - 1:
                self.state.selected_index += 1
        elif self.state.current_view == "workflows":
            workflows = self.load_workflows()
            if workflows and self.state.selected_index < len(workflows) - 1:
                self.state.selected_index += 1

    def toggle_agent(self) -> None:
        """Toggle the selected agent's status."""
        if self.state.current_view != "agents":
            return

        filtered_agents = self.get_filtered_agents()
        if not filtered_agents or self.state.selected_index >= len(filtered_agents):
            self.state.status_message = "No agent selected"
            return

        agent = filtered_agents[self.state.selected_index]

        try:
            if agent.status == "active":
                exit_code, message = agent_deactivate(agent.name)
            else:
                exit_code, message = agent_activate(agent.name)

            # Parse the message and clean ANSI codes
            import re

            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
            self.state.status_message = clean_message.split("\n")[0]

            if exit_code == 0:
                # Reload agents to reflect changes
                self.load_agents()
                # Adjust selected index if needed
                new_filtered = self.get_filtered_agents()
                if self.state.selected_index >= len(new_filtered):
                    self.state.selected_index = max(0, len(new_filtered) - 1)

        except Exception as e:
            self.state.status_message = f"Error: {e}"

    def toggle_help(self) -> None:
        """Toggle help display."""
        self.state.show_help = not self.state.show_help
        if self.state.show_help:
            self.state.show_details = False

    def toggle_details(self) -> None:
        """Toggle details display."""
        self.state.show_details = not self.state.show_details
        if self.state.show_details:
            self.state.show_help = False

    def start_filter(self) -> None:
        """Start filter mode."""
        self.state.status_message = "Type to filter (Esc to cancel)..."

        # Read characters until Enter or Esc
        filter_chars: List[str] = []

        while True:
            char = self.read_key()

            if char == "\r" or char == "\n":  # Enter
                self.state.filter_text = "".join(filter_chars)
                self.state.selected_index = 0
                if self.state.current_view == "agents":
                    filtered_count = len(self.get_filtered_agents())
                    self.state.status_message = (
                        f"Filter applied: {filtered_count} agents matched"
                    )
                else:
                    self.state.status_message = "Filter applied"
                break
            elif char == "\x1b":  # Escape
                self.state.status_message = "Filter cancelled"
                break
            elif char == "\x7f":  # Backspace
                if filter_chars:
                    filter_chars.pop()
                    self.state.status_message = (
                        f"Filter: {''.join(filter_chars) or '(empty)'}"
                    )
            elif char and ord(char) >= 32:  # Printable character
                filter_chars.append(char)
                self.state.status_message = f"Filter: {''.join(filter_chars)}"

    def clear_filter(self) -> None:
        """Clear the current filter."""
        if self.state.filter_text:
            self.state.filter_text = ""
            self.state.selected_index = 0
            self.state.status_message = "Filter cleared"
        else:
            self.state.status_message = "No filter active"

    def load_workflows(self) -> List[WorkflowInfo]:
        """Load workflows from the workflows directory."""
        workflows: List[WorkflowInfo] = []
        try:
            claude_dir = _resolve_claude_dir()
            workflows_dir = claude_dir / "workflows"
            tasks_dir = claude_dir / "tasks" / "current"

            # Load active workflow status if exists
            active_workflow_file = tasks_dir / "active_workflow"
            active_workflow = None
            if active_workflow_file.is_file():
                active_workflow = active_workflow_file.read_text(encoding="utf-8").strip()

            if workflows_dir.is_dir():
                for workflow_file in sorted(workflows_dir.glob("*.yaml")):
                    if workflow_file.stem == "README":
                        continue

                    try:
                        content = workflow_file.read_text(encoding="utf-8")
                        workflow_data = yaml.safe_load(content)

                        name = workflow_data.get("name", workflow_file.stem)
                        description = workflow_data.get("description", "")
                        steps = [step.get("name", "") for step in workflow_data.get("steps", [])]

                        # Determine status
                        status = "pending"
                        progress = 0
                        started = None
                        current_step = None

                        if active_workflow == workflow_file.stem:
                            status_file = tasks_dir / "workflow_status"
                            if status_file.is_file():
                                status = status_file.read_text(encoding="utf-8").strip()

                            started_file = tasks_dir / "workflow_started"
                            if started_file.is_file():
                                started = float(started_file.read_text(encoding="utf-8").strip())

                            current_step_file = tasks_dir / "current_step"
                            if current_step_file.is_file():
                                current_step = current_step_file.read_text(encoding="utf-8").strip()

                            # Calculate progress based on current step
                            if current_step and steps:
                                try:
                                    step_index = steps.index(current_step)
                                    progress = int((step_index / len(steps)) * 100)
                                except ValueError:
                                    progress = 0

                        workflows.append(WorkflowInfo(
                            name=name,
                            description=description,
                            status=status,
                            progress=progress,
                            started=started,
                            steps=steps,
                            current_step=current_step,
                            file_path=workflow_file,
                        ))

                    except Exception:
                        # Skip malformed workflows
                        continue

        except Exception as e:
            self.state.status_message = f"Error loading workflows: {e}"

        return workflows

    def create_workflows_table(self) -> Table:
        """Create the workflows list table."""
        table = Table(
            title="Workflows",
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
            title_style="bold cyan",
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True, width=30)
        table.add_column("Status", width=12, no_wrap=True)
        table.add_column("Progress", width=12, no_wrap=True)
        table.add_column("Started", width=20, no_wrap=True)
        table.add_column("Description", width=40)

        workflows = self.load_workflows()

        if not workflows:
            table.add_row("", "No workflows found", "", "", "", "")
            return table

        for idx, workflow in enumerate(workflows):
            is_selected = idx == self.state.selected_index

            # Selection indicator
            indicator = ">" if is_selected else ""

            # Status styling
            status_styles = {
                "pending": "yellow",
                "running": "bold green",
                "paused": "cyan",
                "complete": "bold blue",
                "error": "bold red",
            }
            status_text = Text(workflow.status.title(), style=status_styles.get(workflow.status, "white"))

            # Progress bar
            progress_text = ""
            if workflow.status in ("running", "paused", "complete"):
                bar_width = 10
                filled = int((workflow.progress / 100) * bar_width)
                progress_text = f"[{'█' * filled}{'░' * (bar_width - filled)}] {workflow.progress}%"
            else:
                progress_text = "-"

            # Started time
            started_text = "-"
            if workflow.started:
                elapsed = int(time.time() - workflow.started)
                hours = elapsed // 3600
                minutes = (elapsed % 3600) // 60
                started_text = f"{hours}h {minutes}m ago"

            # Row style
            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                workflow.name,
                status_text,
                progress_text,
                started_text,
                workflow.description[:40],
                style=row_style,
            )

        return table

    def create_workflow_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected workflow."""
        if not self.state.show_details:
            return None

        workflows = self.load_workflows()
        if not workflows or self.state.selected_index >= len(workflows):
            return None

        workflow = workflows[self.state.selected_index]

        details = Text()
        details.append(f"Workflow: ", style="bold")
        details.append(f"{workflow.name}\n\n")

        details.append(f"Description: ", style="bold")
        details.append(f"{workflow.description}\n\n")

        details.append(f"Status: ", style="bold")
        status_styles = {
            "pending": "yellow",
            "running": "bold green",
            "paused": "cyan",
            "complete": "bold blue",
            "error": "bold red",
        }
        details.append(f"{workflow.status}\n\n", style=status_styles.get(workflow.status, "white"))

        if workflow.started:
            elapsed = int(time.time() - workflow.started)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            details.append(f"Started: ", style="bold")
            details.append(f"{hours}h {minutes}m ago\n\n")

        details.append(f"Progress: ", style="bold")
        details.append(f"{workflow.progress}%\n\n")

        if workflow.steps:
            details.append(f"Steps:\n", style="bold")
            for i, step in enumerate(workflow.steps):
                if workflow.current_step == step:
                    details.append(f"  → {step} ", style="bold green")
                    details.append("(current)\n")
                elif workflow.current_step and workflow.steps.index(workflow.current_step) > i:
                    details.append(f"  ✓ {step}\n", style="dim green")
                else:
                    details.append(f"  ○ {step}\n", style="dim")

        return Panel(details, title="Workflow Details", border_style="cyan")

    def load_agent_tasks(self) -> List[AgentTask]:
        """Load active agent tasks for orchestration view."""
        tasks: List[AgentTask] = []
        try:
            claude_dir = _resolve_claude_dir()
            tasks_dir = claude_dir / "tasks" / "current"

            # Check for active tasks file
            active_tasks_file = tasks_dir / "active_agents.json"
            if active_tasks_file.is_file():
                import json
                task_data = json.loads(active_tasks_file.read_text(encoding="utf-8"))

                for task_id, task_info in task_data.items():
                    tasks.append(AgentTask(
                        agent_id=task_id,
                        agent_name=task_info.get("name", task_id),
                        workstream=task_info.get("workstream", "primary"),
                        status=task_info.get("status", "pending"),
                        progress=task_info.get("progress", 0),
                        started=task_info.get("started"),
                        completed=task_info.get("completed"),
                    ))
        except Exception:
            # No active tasks or error reading
            pass

        return tasks

    def create_orchestrate_view(self) -> Layout:
        """Create the orchestration dashboard view."""
        layout = Layout()
        layout.split_column(
            Layout(name="workstreams", size=15),
            Layout(name="agents"),
            Layout(name="metrics", size=8),
        )

        # Workstreams panel
        workstreams_content = Text()
        workstreams_content.append("Orchestration Dashboard\n", style="bold cyan")
        workstreams_content.append("━" * 60 + "\n\n", style="cyan")

        workstreams_content.append("Workstream Layout:\n\n", style="bold yellow")
        workstreams_content.append("Primary               Quality (‖)\n", style="bold")
        workstreams_content.append("Implementation        • Code Review\n", style="dim")
        workstreams_content.append("████████████ 90%      • Tests\n\n", style="green")

        layout["workstreams"].update(Panel(workstreams_content, title="Workstreams"))

        # Active agents table
        agents_table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        agents_table.add_column("Agent", style="cyan", width=20)
        agents_table.add_column("Workstream", width=15)
        agents_table.add_column("Status", width=12)
        agents_table.add_column("Progress", width=30)

        tasks = self.load_agent_tasks()

        if not tasks:
            # Show example data if no active tasks
            agents_table.add_row(
                "[Agent-1] Implementation",
                "primary",
                Text("Running", style="bold green"),
                "[██████████░░░░░░░░░░] 75%",
            )
            agents_table.add_row(
                "[Agent-2] Code Review",
                "quality",
                Text("Complete", style="bold blue"),
                "[████████████████████] 100%",
            )
            agents_table.add_row(
                "[Agent-3] Test Automation",
                "quality",
                Text("Running", style="bold green"),
                "[████████████░░░░░░░░] 60%",
            )
        else:
            for task in tasks:
                status_styles = {
                    "pending": "yellow",
                    "running": "bold green",
                    "complete": "bold blue",
                    "error": "bold red",
                }

                status_text = Text(task.status.title(), style=status_styles.get(task.status, "white"))

                # Progress bar
                bar_width = 20
                filled = int((task.progress / 100) * bar_width)
                progress_bar = f"[{'█' * filled}{'░' * (bar_width - filled)}] {task.progress}%"

                agents_table.add_row(
                    f"[{task.agent_id}] {task.agent_name}",
                    task.workstream,
                    status_text,
                    progress_bar,
                )

        layout["agents"].update(Panel(agents_table, title="Active Agents"))

        # Metrics panel
        metrics_content = Text()
        metrics_content.append("Metrics:\n", style="bold yellow")

        # Calculate metrics
        if tasks:
            total_progress = sum(t.progress for t in tasks) // len(tasks) if tasks else 0
            running_count = sum(1 for t in tasks if t.status == "running")
            complete_count = sum(1 for t in tasks if t.status == "complete")
            parallel_efficiency = int((running_count / len(tasks)) * 100) if tasks else 0

            metrics_content.append(f"  Parallel Efficiency: ", style="bold")
            metrics_content.append(f"{parallel_efficiency}%\n", style="green")

            metrics_content.append(f"  Overall Progress: ", style="bold")
            metrics_content.append(f"{total_progress}%\n", style="cyan")

            metrics_content.append(f"  Active Agents: ", style="bold")
            metrics_content.append(f"{running_count}/{len(tasks)}\n", style="yellow")

            metrics_content.append(f"  Completed: ", style="bold")
            metrics_content.append(f"{complete_count}/{len(tasks)}\n", style="blue")

            # Estimate completion time
            if running_count > 0 and total_progress > 0:
                estimated_minutes = int((100 - total_progress) * 0.5)  # Rough estimate
                metrics_content.append(f"  Estimated Completion: ", style="bold")
                metrics_content.append(f"{estimated_minutes}m\n", style="magenta")
        else:
            metrics_content.append("  Parallel Efficiency: ", style="bold")
            metrics_content.append("87%\n", style="green")

            metrics_content.append(f"  Overall Progress: ", style="bold")
            metrics_content.append(f"78%\n", style="cyan")

            metrics_content.append(f"  Estimated Completion: ", style="bold")
            metrics_content.append(f"2m 30s\n", style="magenta")

        layout["metrics"].update(Panel(metrics_content, title="Orchestration Metrics"))

        return layout

    def read_key(self) -> str:
        """Read a single key from stdin (assumes terminal already in raw mode)."""
        try:
            key = sys.stdin.read(1)

            # Handle escape sequences
            if key == "\x1b":
                # Check if there's more input (non-blocking peek)
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    next_char = sys.stdin.read(1)

                    # ESC + [ sequences (arrow keys, function keys)
                    if next_char == "[":
                        third_char = sys.stdin.read(1)
                        if third_char == "A":
                            return "UP"
                        elif third_char == "B":
                            return "DOWN"
                        # Handle extended sequences like [1~, [2~, etc.
                        elif third_char.isdigit():
                            # Consume until ~
                            while True:
                                if select.select([sys.stdin], [], [], 0.01)[0]:
                                    ch = sys.stdin.read(1)
                                    if ch == "~":
                                        break
                                else:
                                    break
                            return ""  # Ignore function keys for now

                    # ESC + O sequences (function keys in some terminals)
                    elif next_char == "O":
                        # Consume the next character
                        if select.select([sys.stdin], [], [], 0.01)[0]:
                            sys.stdin.read(1)
                        return ""  # Ignore these sequences

                    # ESC + other character
                    else:
                        return key  # Return escape
                else:
                    # Standalone escape key
                    return key

            return key
        except Exception:
            return ""

    # Modes and Rules Management Methods

    def load_modes(self) -> List[ModeNode]:
        """Load modes from the system."""
        try:
            modes = []
            claude_dir = _resolve_claude_dir()
            modes_dir = claude_dir / "modes"
            inactive_dir = _mode_inactive_dir(claude_dir)

            # Load active modes
            if modes_dir.is_dir():
                for path in _iter_md_files(modes_dir):
                    if _is_disabled(path):
                        continue
                    description = self._extract_mode_description(path)
                    modes.append(ModeNode(
                        name=path.stem,
                        status="active",
                        description=description,
                        path=path
                    ))

            # Load inactive modes
            if inactive_dir.is_dir():
                for path in _iter_md_files(inactive_dir):
                    description = self._extract_mode_description(path)
                    modes.append(ModeNode(
                        name=path.stem,
                        status="inactive",
                        description=description,
                        path=path
                    ))

            # Sort by status (active first) then name
            modes.sort(key=lambda m: (m.status != "active", m.name.lower()))
            return modes

        except Exception as e:
            self.state.status_message = f"Error loading modes: {e}"
            return []

    def load_rules(self) -> List[RuleNode]:
        """Load rule modules from the system."""
        try:
            rules = []
            claude_dir = _resolve_claude_dir()
            rules_dir = claude_dir / "rules"
            active_rules_file = claude_dir / ".active-rules"

            # Get active rules
            active_rules = set(_parse_active_entries(active_rules_file))

            # Load all rule files
            if rules_dir.is_dir():
                for path in _iter_md_files(rules_dir):
                    if _is_disabled(path):
                        continue

                    rule_name = path.stem
                    status = "active" if rule_name in active_rules else "inactive"
                    category, description = self._extract_rule_info(path)

                    rules.append(RuleNode(
                        name=rule_name,
                        status=status,
                        category=category,
                        description=description,
                        path=path
                    ))

            # Sort by status (active first) then name
            rules.sort(key=lambda r: (r.status != "active", r.name.lower()))
            return rules

        except Exception as e:
            self.state.status_message = f"Error loading rules: {e}"
            return []

    def _extract_mode_description(self, path: Path) -> str:
        """Extract description from mode file."""
        try:
            content = path.read_text(encoding="utf-8")

            # Try to find **Purpose**: line
            purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+)', content)
            if purpose_match:
                return purpose_match.group(1).strip()

            # Try to find first non-header line
            lines = content.split('\n')
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('**'):
                    return stripped[:100]  # First 100 chars

            return "No description available"
        except Exception:
            return "Error reading description"

    def _extract_rule_info(self, path: Path) -> tuple[str, str]:
        """Extract category and description from rule file."""
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.split('\n')

            # Determine category from filename
            name = path.stem.lower()
            if 'workflow' in name:
                category = "workflow"
            elif 'quality' in name:
                category = "quality"
            elif 'efficiency' in name or 'parallel' in name:
                category = "efficiency"
            elif 'security' in name:
                category = "security"
            else:
                category = "general"

            # Extract first non-header line as description
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and len(stripped) > 10:
                    return category, stripped[:100]

            return category, "No description available"
        except Exception:
            return "general", "Error reading description"

    def get_filtered_modes(self) -> List[ModeNode]:
        """Get modes filtered by current filter text."""
        modes = getattr(self, '_cached_modes', [])
        if not modes:
            modes = self.load_modes()
            self._cached_modes = modes

        if not self.state.filter_text:
            return modes

        filter_lower = self.state.filter_text.lower()
        return [
            mode for mode in modes
            if filter_lower in mode.name.lower()
            or filter_lower in mode.description.lower()
        ]

    def get_filtered_rules(self) -> List[RuleNode]:
        """Get rules filtered by current filter text."""
        rules = getattr(self, '_cached_rules', [])
        if not rules:
            rules = self.load_rules()
            self._cached_rules = rules

        if not self.state.filter_text:
            return rules

        filter_lower = self.state.filter_text.lower()
        return [
            rule for rule in rules
            if filter_lower in rule.name.lower()
            or filter_lower in rule.category.lower()
            or filter_lower in rule.description.lower()
        ]

    def create_modes_table(self) -> Table:
        """Create the modes list table."""
        table = Table(
            title="Modes",
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
            title_style="bold cyan",
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True, min_width=20)
        table.add_column("Status", width=10, no_wrap=True)
        table.add_column("Description", overflow="fold")

        filtered_modes = self.get_filtered_modes()

        if not filtered_modes:
            table.add_row("", "No modes found", "", "")
            return table

        for idx, mode in enumerate(filtered_modes):
            is_selected = idx == self.state.selected_index
            indicator = ">" if is_selected else ""

            # Status styling
            if mode.status == "active":
                status_text = Text("Active", style="bold green")
            else:
                status_text = Text("Inactive", style="yellow")

            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                mode.name,
                status_text,
                mode.description[:80] + "..." if len(mode.description) > 80 else mode.description,
                style=row_style,
            )

        return table

    def create_rules_table(self) -> Table:
        """Create the rules list table."""
        table = Table(
            title="Rules",
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
            title_style="bold cyan",
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True, min_width=20)
        table.add_column("Status", width=10, no_wrap=True)
        table.add_column("Category", width=12, no_wrap=True)
        table.add_column("Description", overflow="fold")

        filtered_rules = self.get_filtered_rules()

        if not filtered_rules:
            table.add_row("", "No rules found", "", "", "")
            return table

        for idx, rule in enumerate(filtered_rules):
            is_selected = idx == self.state.selected_index
            indicator = ">" if is_selected else ""

            # Status styling
            if rule.status == "active":
                status_text = Text("Active", style="bold green")
            else:
                status_text = Text("Inactive", style="yellow")

            row_style = "reverse" if is_selected else None

            table.add_row(
                indicator,
                rule.name,
                status_text,
                rule.category,
                rule.description[:60] + "..." if len(rule.description) > 60 else rule.description,
                style=row_style,
            )

        return table

    def create_mode_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected mode."""
        if not self.state.show_details:
            return None

        filtered_modes = self.get_filtered_modes()
        if not filtered_modes or self.state.selected_index >= len(filtered_modes):
            return None

        mode = filtered_modes[self.state.selected_index]

        details = Text()
        details.append(f"Name: ", style="bold")
        details.append(f"{mode.name}\n")

        details.append(f"Status: ", style="bold")
        status_style = "green" if mode.status == "active" else "yellow"
        details.append(f"{mode.status}\n", style=status_style)

        details.append(f"\nDescription: ", style="bold")
        details.append(f"{mode.description}\n")

        if mode.path:
            details.append(f"\nPath: ", style="bold")
            details.append(f"{mode.path}\n", style="dim")

        return Panel(details, title="Mode Details", border_style="cyan")

    def create_rule_details_panel(self) -> Optional[Panel]:
        """Create the details panel for the selected rule."""
        if not self.state.show_details:
            return None

        filtered_rules = self.get_filtered_rules()
        if not filtered_rules or self.state.selected_index >= len(filtered_rules):
            return None

        rule = filtered_rules[self.state.selected_index]

        details = Text()
        details.append(f"Name: ", style="bold")
        details.append(f"{rule.name}\n")

        details.append(f"Status: ", style="bold")
        status_style = "green" if rule.status == "active" else "yellow"
        details.append(f"{rule.status}\n", style=status_style)

        details.append(f"Category: ", style="bold")
        details.append(f"{rule.category}\n")

        details.append(f"\nDescription: ", style="bold")
        details.append(f"{rule.description}\n")

        if rule.path:
            details.append(f"\nPath: ", style="bold")
            details.append(f"{rule.path}\n", style="dim")

        return Panel(details, title="Rule Details", border_style="cyan")

    def toggle_mode(self) -> None:
        """Toggle the selected mode's status."""
        filtered_modes = self.get_filtered_modes()
        if not filtered_modes or self.state.selected_index >= len(filtered_modes):
            self.state.status_message = "No mode selected"
            return

        mode = filtered_modes[self.state.selected_index]

        try:
            if mode.status == "active":
                exit_code, message = mode_deactivate(mode.name)
            else:
                exit_code, message = mode_activate(mode.name)

            # Clean ANSI codes from message
            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
            self.state.status_message = clean_message.split("\n")[0]

            if exit_code == 0:
                # Clear cache and reload
                self._cached_modes = []
                filtered_modes = self.get_filtered_modes()

                # Adjust selected index if needed
                if self.state.selected_index >= len(filtered_modes):
                    self.state.selected_index = max(0, len(filtered_modes) - 1)

        except Exception as e:
            self.state.status_message = f"Error: {e}"

    def toggle_rule(self) -> None:
        """Toggle the selected rule's status."""
        filtered_rules = self.get_filtered_rules()
        if not filtered_rules or self.state.selected_index >= len(filtered_rules):
            self.state.status_message = "No rule selected"
            return

        rule = filtered_rules[self.state.selected_index]

        try:
            if rule.status == "active":
                message = rules_deactivate(rule.name)
            else:
                message = rules_activate(rule.name)

            # Clean ANSI codes from message
            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
            self.state.status_message = clean_message.split("\n")[0]

            # Clear cache and reload
            self._cached_rules = []
            filtered_rules = self.get_filtered_rules()

            # Adjust selected index if needed
            if self.state.selected_index >= len(filtered_rules):
                self.state.selected_index = max(0, len(filtered_rules) - 1)

        except Exception as e:
            self.state.status_message = f"Error: {e}"

    def run(self) -> int:
        """Run the TUI main loop."""
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            # Set terminal to raw mode once
            tty.setraw(fd)

            # Load agents initially
            self.load_agents()

            # Initial render
            self.render()

            while True:
                # Read key
                key = self.read_key()

                # Track if state changed (needs update)
                needs_update = False

                # Handle view switching (1-9)
                if key == "1":
                    self.switch_view("overview")
                    needs_update = True
                elif key == "2":
                    self.switch_view("agents")
                    needs_update = True
                elif key == "3":
                    self.switch_view("modes")
                    needs_update = True
                elif key == "4":
                    self.switch_view("rules")
                    needs_update = True
                elif key == "5":
                    self.switch_view("skills")
                    needs_update = True
                elif key == "6":
                    self.switch_view("workflows")
                    needs_update = True
                elif key == "7":
                    self.switch_view("mcp")
                    needs_update = True
                elif key == "8":
                    self.switch_view("orchestrate")
                    needs_update = True
                elif key == "9":
                    self.switch_view("profile")
                    needs_update = True
                elif key == "0":
                    self.switch_view("export")
                    needs_update = True
                # Global navigation
                elif key == "q":
                    break
                elif key == "k" or key == "UP":
                    self.move_up()
                    needs_update = True
                elif key == "j" or key == "DOWN":
                    self.move_down()
                    needs_update = True
                elif key == " ":
                    if self.state.current_view == "agents":
                        self.toggle_agent()
                    elif self.state.current_view == "modes":
                        self.toggle_mode()
                    elif self.state.current_view == "rules":
                        self.toggle_rule()
                    needs_update = True
                elif key == "\r" or key == "\n":
                    self.toggle_details()
                    needs_update = True
                elif key == "/":
                    self.start_filter()
                    needs_update = True
                elif key == "\x1b":
                    self.clear_filter()
                    self.state.show_help = False
                    self.state.show_details = False
                    needs_update = True
                elif key == "?":
                    self.toggle_help()
                    needs_update = True
                elif key == "r":
                    if self.state.current_view == "agents":
                        self.load_agents()
                    elif self.state.current_view == "mcp":
                        self.handle_mcp_keys(key)
                    else:
                        self.state.status_message = f"Refreshing {self.state.current_view}..."
                    needs_update = True
                elif key in ["t", "d", "c", "v"] and self.state.current_view == "mcp":
                    self.handle_mcp_keys(key)
                    needs_update = True
                elif key == "i":
                    self.state.status_message = "Init wizard not yet implemented"
                    needs_update = True

                # Update display only when state actually changed
                if needs_update:
                    self.render()

            return 0

        except KeyboardInterrupt:
            return 0
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            return 1
        finally:
            # Always restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main() -> int:
    """Entry point for the TUI."""
    tui = AgentTUI()
    return tui.run()


if __name__ == "__main__":
    sys.exit(main())
