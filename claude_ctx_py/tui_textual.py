"""Textual-based Terminal User Interface for claude-ctx."""

from __future__ import annotations

import json
import time
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable
from textual.reactive import reactive

from .core import (
    build_agent_graph,
    agent_activate,
    agent_deactivate,
    AgentGraphNode,
    _resolve_claude_dir,
    _iter_all_files,
    _is_disabled,
    _extract_agent_name,
    _read_agent_front_matter_lines,
    _parse_dependencies_from_front,
    _tokenize_front_matter,
    _extract_scalar_from_paths,
    _extract_front_matter,
)
from .core.rules import rules_activate, rules_deactivate
from .core.modes import mode_activate, mode_deactivate
from .core.base import _iter_md_files, _parse_active_entries
from .tui_icons import Icons, StatusIcon
from .tui_format import Format
from .tui_progress import ProgressBar
from .tui_command_palette import CommandPalette, CommandRegistry, DEFAULT_COMMANDS
from .tui_commands import AgentCommandProvider
from .tui_dashboard import DashboardCard, Sparkline, MetricsCollector
from .tui_performance import PerformanceMonitor
from .tui_workflow_viz import WorkflowNode, WorkflowTimeline, DependencyVisualizer
from .tui_overview_enhanced import EnhancedOverview
from .intelligence import IntelligentAgent, AgentRecommendation, WorkflowPrediction


@dataclass
class RuleNode:
    """Represents a rule in the system."""
    name: str
    status: str  # "active" or "inactive"
    category: str
    description: str
    path: Path


@dataclass
class AgentTask:
    """Represents an active agent task in the orchestration system."""
    agent_id: str
    agent_name: str
    workstream: str
    status: str
    progress: int
    started: Optional[float] = None
    completed: Optional[float] = None


@dataclass
class WorkflowInfo:
    """Information about a workflow."""
    name: str
    description: str
    status: str
    progress: int
    started: Optional[float]
    steps: List[str]
    current_step: Optional[str]
    file_path: Path


@dataclass
class ModeInfo:
    """Represents a behavioral mode in the system."""
    name: str
    status: str  # "active" or "inactive"
    purpose: str
    description: str
    path: Path


class AgentTUI(App):
    """Textual TUI for claude-ctx management."""

    CSS = """
    /* Super Saiyan Mode Colors 🔥 */
    $primary: #3b82f6;
    $secondary: #8b5cf6;
    $accent: #06b6d4;
    $success: #10b981;
    $warning: #f59e0b;
    $error: #ef4444;
    $surface: #0a0e27;
    $surface-lighten-1: #1a1f3a;
    $surface-lighten-2: #242945;

    Screen {
        background: $surface;
    }

    DataTable {
        height: 1fr;
        background: $surface-lighten-1;
        border: solid $primary;
        padding: 0 1;
    }

    DataTable > .datatable--header {
        background: $surface-lighten-2;
        color: $accent;
        text-style: bold;
    }

    DataTable > .datatable--cursor {
        background: $surface-lighten-2;
        color: $accent;
        text-style: bold;
    }

    DataTable:focus > .datatable--cursor {
        background: $surface-lighten-2;
        color: white;
        border-left: tall $accent;
    }

    Header {
        background: $surface-lighten-2;
        color: $accent;
        text-style: bold;
    }

    Footer {
        background: $surface-lighten-2;
    }

    #status-bar {
        height: 1;
        background: $surface-lighten-1;
        color: $text;
        padding: 0 1;
        border-top: solid $primary;
    }

    /* Command Palette Styles - Super Saiyan */
    #command-palette-container {
        align: center middle;
        width: 60%;
        height: auto;
        max-height: 80%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 0;
        offset-y: -5;
    }

    #command-palette-container.visible {
        opacity: 1;
        offset-y: 0;
        transition: opacity 300ms, offset-y 300ms out_cubic;
    }

    #palette-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #palette-input {
        margin-bottom: 1;
        background: $surface-lighten-2;
        border: solid $primary;
    }

    #palette-results {
        height: auto;
        max-height: 20;
        border: solid $primary;
        margin-bottom: 1;
        background: $surface;
    }

    #palette-help {
        text-align: center;
        margin-top: 1;
        color: $accent;
    }

    /* Dialog Styles - Super Saiyan */
    #dialog {
        align: center middle;
        width: 50%;
        height: auto;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 0;
    }

    #dialog.visible {
        opacity: 1;
        transition: opacity 250ms;
    }

    #dialog-title {
        text-align: center;
        margin-bottom: 1;
        color: $accent;
        text-style: bold;
    }

    #dialog-message {
        text-align: center;
        margin-bottom: 1;
    }

    #dialog-buttons {
        align: center middle;
        height: auto;
    }

    /* Loading Overlay Styles - Super Saiyan */
    #loading-overlay {
        align: center middle;
        width: 40%;
        height: auto;
        background: $surface-lighten-1;
        border: thick $warning;
        padding: 2 3;
        opacity: 0;
    }

    #loading-overlay.visible {
        opacity: 1;
        transition: opacity 200ms;
    }

    #loading-message {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: $warning;
    }

    #loading-subtitle {
        text-align: center;
        color: $accent;
    }

    /* Button Styles - Super Saiyan */
    Button {
        background: $primary;
        color: white;
        border: solid $primary;
        text-style: bold;
    }

    Button:hover {
        background: $accent;
        border: solid $accent;
        transition: background 150ms, border 150ms;
    }

    Button:focus {
        border: solid $warning;
    }
    """

    BINDINGS = [
        Binding("1", "view_overview", "Overview"),
        Binding("2", "view_agents", "Agents"),
        Binding("3", "view_modes", "Modes"),
        Binding("4", "view_rules", "Rules"),
        Binding("5", "view_skills", "Skills"),
        Binding("6", "view_workflows", "Workflows"),
        Binding("7", "view_orchestrate", "Orchestrate"),
        Binding("8", "view_ai_assistant", "AI Assistant", show=True),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("space", "toggle", "Toggle"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "auto_activate", "Auto-Activate"),
    ]

    # Register command provider for Textual's command palette
    # Textual looks for COMMANDS, not COMMAND_PROVIDERS!
    COMMANDS = {AgentCommandProvider}

    current_view: reactive[str] = reactive("agents")
    status_message: reactive[str] = reactive("Welcome to claude-ctx TUI")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        yield Container(
            DataTable(id="main-table"),
            id="main-container"
        )
        yield Static("Loading...", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load initial data when app starts."""
        # Initialize performance monitor and command registry
        self.performance_monitor = PerformanceMonitor()
        self.command_registry = CommandRegistry()
        self.command_registry.register_batch(DEFAULT_COMMANDS)
        self.metrics_collector = MetricsCollector()

        # Initialize intelligent agent for auto-activation and recommendations
        claude_dir = _resolve_claude_dir()
        self.intelligent_agent = IntelligentAgent(claude_dir / "intelligence")

        # Analyze context and get initial recommendations
        self.intelligent_agent.analyze_context()

        # Load data
        self.load_agents()
        self.load_rules()
        self.load_modes()
        self.load_skills()
        self.load_agent_tasks()
        self.load_workflows()
        self.update_view()

        # Start performance monitoring timer
        self.set_interval(1.0, self.update_performance_status)

        # Force initial status bar update
        self.watch_status_message(self.status_message)

        # Show AI recommendations if high confidence
        self._check_auto_activations()

    def watch_status_message(self, message: str) -> None:
        """Update status bar when message changes."""
        try:
            status_bar = self.query_one("#status-bar", Static)
            # Include performance metrics in status bar
            if hasattr(self, 'performance_monitor'):
                perf_status = self.performance_monitor.get_status_bar(compact=True)
                status_bar.update(f"[View: {self.current_view.title()}] {message} [dim]│[/dim] {perf_status}")
            else:
                status_bar.update(f"[View: {self.current_view.title()}] {message}")
        except Exception:
            pass  # Status bar not yet mounted

    def update_performance_status(self) -> None:
        """Update performance metrics in status bar (called by timer)."""
        # Trigger status message update to refresh performance metrics
        self.status_message = self.status_message  # Trigger reactive update

    def watch_current_view(self, view: str) -> None:
        """Update display when view changes."""
        self.update_view()

    def _validate_path(self, base_dir: Path, subpath: Path) -> Path:
        """
        Validate that a path stays within the base directory.

        Args:
            base_dir: The trusted base directory
            subpath: The path to validate (can be relative or absolute)

        Returns:
            Resolved canonical path

        Raises:
            ValueError: If path escapes base directory
        """
        base_resolved = base_dir.resolve()
        subpath_resolved = subpath.resolve()

        # Check if subpath is within base_dir
        try:
            subpath_resolved.relative_to(base_resolved)
        except ValueError:
            raise ValueError(f"Path traversal detected: {subpath} escapes {base_dir}")

        return subpath_resolved

    def _validate_workflow_schema(self, workflow_data: dict, file_path: Path) -> bool:
        """
        Validate that a workflow YAML has the expected structure.

        Args:
            workflow_data: Parsed YAML data
            file_path: Path to the workflow file (for error messages)

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(workflow_data, dict):
            return False

        # Optional fields (can be missing or wrong type without failing)
        # Just ensure they're the right type if present
        if "name" in workflow_data and not isinstance(workflow_data["name"], str):
            return False

        if "description" in workflow_data and not isinstance(workflow_data["description"], str):
            return False

        # Steps array is expected but can be empty
        if "steps" in workflow_data:
            if not isinstance(workflow_data["steps"], list):
                return False
            # Each step should be a dict with at least a name
            for step in workflow_data["steps"]:
                if not isinstance(step, dict):
                    return False

        return True

    def load_agents(self) -> None:
        """Load agents from the system."""
        try:
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

            self.agents = agents
            active_count = sum(1 for a in agents if a.status == "active")
            inactive_count = len(agents) - active_count
            self.status_message = f"Loaded {len(agents)} agents ({active_count} active, {inactive_count} inactive)"

        except Exception as e:
            self.status_message = f"Error loading agents: {e}"
            self.agents = []

    def _parse_agent_file(self, path, status: str):
        """Parse an agent file and return an AgentGraphNode."""
        try:
            lines = _read_agent_front_matter_lines(path)
            if not lines:
                return None

            name = _extract_agent_name(path, lines)
            tokens = _tokenize_front_matter(lines)

            category = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "category"),
                    ("category",),
                ),
            ) or "general"

            tier = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "tier", "id"),
                    ("tier", "id"),
                ),
            ) or "standard"

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
            return None

    def load_skills(self) -> None:
        """Load skills from the system."""
        try:
            skills = []
            claude_dir = _resolve_claude_dir()

            # Load skills from skills directory
            skills_dir = self._validate_path(claude_dir, claude_dir / "skills")
            if skills_dir.is_dir():
                for skill_path in sorted(skills_dir.iterdir()):
                    if not skill_path.is_dir():
                        continue

                    # Validate each skill subdirectory
                    skill_path = self._validate_path(claude_dir, skill_path)
                    skill_file = skill_path / "SKILL.md"
                    if not skill_file.is_file():
                        continue

                    skill_data = self._parse_skill_file(skill_file, claude_dir)
                    if skill_data:
                        skills.append(skill_data)

            # Sort by category then name
            skills.sort(key=lambda s: (s["category"].lower(), s["name"].lower()))

            self.skills = skills
            self.status_message = f"Loaded {len(skills)} skills"

        except Exception as e:
            self.status_message = f"Error loading skills: {e}"
            self.skills = []

    def _parse_skill_file(self, skill_file: Path, claude_dir: Path):
        """Parse a skill file and return skill data dictionary."""
        try:
            content = skill_file.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)

            if not front_matter:
                return None

            lines = front_matter.strip().splitlines()
            tokens = _tokenize_front_matter(lines)

            # Extract metadata
            name = _extract_scalar_from_paths(tokens, (("name",),)) or skill_file.parent.name
            description = _extract_scalar_from_paths(tokens, (("description",),)) or "No description"
            category = _extract_scalar_from_paths(tokens, (("category",),)) or "general"

            # Determine location (user vs project)
            # If skill is in user's home .claude dir, it's a user skill
            home_claude = Path.home() / ".claude"
            if home_claude in skill_file.parents:
                location = "user"
            else:
                location = "project"

            # Check if gitignored
            gitignored = self._is_gitignored(skill_file)
            status = "gitignored" if gitignored else "tracked"

            # Truncate description if too long
            max_desc_len = 80
            if len(description) > max_desc_len:
                description = description[:max_desc_len-3] + "..."

            return {
                "name": name,
                "description": description,
                "category": category,
                "location": location,
                "status": status,
                "path": str(skill_file),
            }
        except Exception:
            return None

    def _is_gitignored(self, path: Path) -> bool:
        """Check if a path is gitignored using git check-ignore."""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "check-ignore", "-q", str(path)],
                cwd=path.parent,
                capture_output=True,
            )
            # Return code 0 means the file is ignored
            return result.returncode == 0
        except Exception:
            # If git is not available or any error, assume not ignored
            return False

    def show_skills_view(self, table: DataTable) -> None:
        """Show skills table with enhanced colors (READ-ONLY)."""
        table.add_column("Name", key="name", width=25)
        table.add_column("Category", key="category", width=18)
        table.add_column("Location", key="location", width=12)
        table.add_column("Description", key="description")

        if not hasattr(self, 'skills') or not self.skills:
            table.add_row("[dim]No skills found[/dim]", "", "", "")
            return

        category_colors = {
            "api-design": "cyan",
            "security": "red",
            "performance": "yellow",
            "testing": "green",
            "architecture": "blue",
            "deployment": "magenta"
        }

        for skill in self.skills:
            # Color-coded name with icon
            name = f"[bold green]{Icons.CODE} {skill['name']}[/bold green]"

            # Color-coded category
            category = skill["category"]
            cat_color = category_colors.get(category.lower(), "white")
            category_text = f"[{cat_color}]{category}[/{cat_color}]"

            # Format location with status indicator
            location = skill["location"]
            if skill["status"] == "gitignored":
                location_text = f"[yellow]{location}[/yellow]"
            elif location == "user":
                location_text = f"[cyan]{location}[/cyan]"
            else:
                location_text = f"[dim]{location}[/dim]"

            # Truncate description - show more text
            description = f"[dim]{Format.truncate(skill['description'], 150)}[/dim]"

            table.add_row(
                name,
                category_text,
                location_text,
                description,
            )

    def load_agent_tasks(self) -> None:
        """Load active agent tasks for orchestration view."""
        tasks: List[AgentTask] = []
        try:
            claude_dir = _resolve_claude_dir()
            tasks_dir = self._validate_path(claude_dir, claude_dir / "tasks" / "current")

            # Check for active tasks file
            active_tasks_file = tasks_dir / "active_agents.json"
            if active_tasks_file.is_file():
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
            # No active tasks or error reading - use empty list
            pass

        self.agent_tasks = tasks

    def load_rules(self) -> None:
        """Load rules from the system."""
        try:
            rules = []
            claude_dir = _resolve_claude_dir()

            # Load active rules list
            active_rules_file = claude_dir / ".active-rules"
            active_rule_names = set(_parse_active_entries(active_rules_file))

            # Check active rules
            rules_dir = self._validate_path(claude_dir, claude_dir / "rules")
            if rules_dir.is_dir():
                for path in _iter_md_files(rules_dir):
                    if _is_disabled(path):
                        continue
                    node = self._parse_rule_file(path, "active" if path.stem in active_rule_names else "inactive")
                    if node:
                        rules.append(node)

            # Check disabled rules
            disabled_dirs = [
                self._validate_path(claude_dir, claude_dir / "rules-disabled"),
                self._validate_path(claude_dir, rules_dir / "disabled") if rules_dir.is_dir() else None,
            ]

            for disabled_dir in disabled_dirs:
                if disabled_dir and disabled_dir.is_dir():
                    for path in _iter_md_files(disabled_dir):
                        node = self._parse_rule_file(path, "inactive")
                        if node:
                            rules.append(node)

            # Sort by category and name
            rules.sort(key=lambda r: (r.category, r.name.lower()))

            self.rules = rules
            active_count = sum(1 for r in rules if r.status == "active")
            self.status_message = f"Loaded {len(rules)} rules ({active_count} active)"

        except Exception as e:
            self.status_message = f"Error loading rules: {e}"
            self.rules = []

    def _parse_rule_file(self, path: Path, status: str):
        """Parse a rule file and return a RuleNode."""
        try:
            name = path.stem

            # Read the file to extract description and category
            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Extract first heading as name if it exists
            display_name = name
            description = ""
            category = "general"

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("# "):
                    display_name = line[2:].strip()
                elif line.startswith("## ") and not description:
                    # Use first h2 as description
                    description = line[3:].strip()
                elif line and not line.startswith("#") and not description:
                    # Use first non-empty, non-heading line as description
                    description = line[:100]  # Limit length

                if display_name and description:
                    break

            # Determine category from filename or content
            if "workflow" in name.lower():
                category = "workflow"
            elif "quality" in name.lower():
                category = "quality"
            elif "parallel" in name.lower() or "execution" in name.lower():
                category = "execution"
            elif "efficiency" in name.lower():
                category = "efficiency"

            return RuleNode(
                name=display_name,
                status=status,
                category=category,
                description=description or "No description available",
                path=path,
            )
        except Exception:
            return None

    def load_modes(self) -> None:
        """Load behavioral modes from the system."""
        try:
            modes = []
            claude_dir = _resolve_claude_dir()

            # Load active modes from modes/ directory
            modes_dir = self._validate_path(claude_dir, claude_dir / "modes")
            if modes_dir.is_dir():
                for path in _iter_md_files(modes_dir):
                    if _is_disabled(path):
                        continue
                    node = self._parse_mode_file(path, "active")
                    if node:
                        modes.append(node)

            # Load inactive modes from modes/inactive/ directory
            if modes_dir.is_dir():
                inactive_dir = self._validate_path(claude_dir, modes_dir / "inactive")
                if inactive_dir.is_dir():
                    for path in _iter_md_files(inactive_dir):
                        node = self._parse_mode_file(path, "inactive")
                        if node:
                            modes.append(node)

            # Sort by status (active first) and then by name
            modes.sort(key=lambda m: (m.status != "active", m.name.lower()))

            self.modes = modes
            active_count = sum(1 for m in modes if m.status == "active")
            self.status_message = f"Loaded {len(modes)} modes ({active_count} active)"

        except Exception as e:
            self.status_message = f"Error loading modes: {e}"
            self.modes = []

    def _parse_mode_file(self, path: Path, status: str):
        """Parse a mode file and return a ModeInfo."""
        try:
            name = path.stem

            # Read the file to extract purpose and description
            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Extract mode information
            display_name = name
            purpose = ""
            description = ""

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("# "):
                    # Extract title (e.g., "# Task Management Mode" -> "Task Management")
                    title = line[2:].strip()
                    if title.endswith(" Mode"):
                        display_name = title[:-5]  # Remove " Mode" suffix
                    else:
                        display_name = title
                elif line.startswith("**Purpose**:"):
                    # Extract purpose
                    purpose = line.split("**Purpose**:")[1].strip()
                elif line.startswith("## ") and "Activation" not in line and not description:
                    # Use first non-activation h2 as description fallback
                    description = line[3:].strip()

            # Use purpose as description if available, otherwise use first description
            final_description = purpose if purpose else description
            if not final_description:
                # Fallback: use first non-empty, non-heading line
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("**"):
                        final_description = line[:80]  # Limit length
                        break

            return ModeInfo(
                name=display_name,
                status=status,
                purpose=purpose or "No purpose specified",
                description=final_description or "No description available",
                path=path,
            )
        except Exception:
            return None

    def load_workflows(self) -> None:
        """Load workflows from the workflows directory."""
        workflows: List[WorkflowInfo] = []
        try:
            claude_dir = _resolve_claude_dir()
            workflows_dir = self._validate_path(claude_dir, claude_dir / "workflows")
            tasks_dir = self._validate_path(claude_dir, claude_dir / "tasks" / "current")

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

                        # Validate YAML structure
                        if not self._validate_workflow_schema(workflow_data, workflow_file):
                            # Skip malformed workflows
                            continue

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
            self.status_message = f"Error loading workflows: {e}"

        self.workflows = workflows

    def update_view(self) -> None:
        """Update the table based on current view."""
        table = self.query_one(DataTable)
        table.clear(columns=True)

        if self.current_view == "agents":
            self.show_agents_view(table)
        elif self.current_view == "rules":
            self.show_rules_view(table)
        elif self.current_view == "modes":
            self.show_modes_view(table)
        elif self.current_view == "overview":
            self.show_overview(table)
        elif self.current_view == "skills":
            self.show_skills_view(table)
        elif self.current_view == "workflows":
            self.show_workflows_view(table)
        elif self.current_view == "orchestrate":
            self.show_orchestrate_view(table)
        elif self.current_view == "ai_assistant":
            self.show_ai_assistant_view(table)
        else:
            table.add_column("Message")
            table.add_row(f"{self.current_view.title()} view coming soon")

    def show_agents_view(self, table: DataTable) -> None:
        """Show agents table with enhanced colors and formatting."""
        table.add_column("Name", key="name", width=35)
        table.add_column("Status", key="status", width=12)
        table.add_column("Category", key="category", width=20)
        table.add_column("Tier", key="tier", width=15)

        if not hasattr(self, 'agents') or not self.agents:
            table.add_row("[dim]No agents found[/dim]", "", "", "")
            return

        # Color maps for categories and tiers
        category_colors = {
            "orchestration": "cyan",
            "analysis": "blue",
            "development": "green",
            "documentation": "yellow",
            "testing": "magenta",
            "quality": "red",
            "general": "white"
        }

        tier_colors = {
            "essential": "bold green",
            "standard": "cyan",
            "premium": "yellow",
            "experimental": "magenta"
        }

        for agent in self.agents:
            # Color-coded status with icon
            if agent.status == "active":
                status_text = f"[bold green]● ACTIVE[/bold green]"
            else:
                status_text = f"[dim]○ inactive[/dim]"

            # Color-coded name with icon
            if agent.status == "active":
                name = f"[bold]{Icons.CODE} {agent.name}[/bold]"
            else:
                name = f"[dim]{Icons.CODE} {agent.name}[/dim]"

            # Color-coded category
            cat_color = category_colors.get(agent.category.lower(), "white")
            category_text = f"[{cat_color}]{agent.category}[/{cat_color}]"

            # Color-coded tier
            tier_color = tier_colors.get(agent.tier.lower(), "white")
            tier_text = f"[{tier_color}]{agent.tier}[/{tier_color}]"

            table.add_row(
                name,
                status_text,
                category_text,
                tier_text,
            )


    def show_rules_view(self, table: DataTable) -> None:
        """Show rules table with enhanced colors."""
        table.add_column("Name", key="name", width=25)
        table.add_column("Status", key="status", width=12)
        table.add_column("Category", key="category", width=15)
        table.add_column("Description", key="description")

        if not hasattr(self, 'rules') or not self.rules:
            table.add_row("[dim]No rules found[/dim]", "", "", "")
            return

        category_colors = {
            "execution": "cyan",
            "quality": "green",
            "workflow": "yellow",
            "parallel": "magenta",
            "efficiency": "blue"
        }

        for rule in self.rules:
            # Color-coded status
            if rule.status == "active":
                status_text = f"[bold green]● ACTIVE[/bold green]"
                name = f"[bold]{Icons.DOC} {rule.name}[/bold]"
            else:
                status_text = f"[dim]○ inactive[/dim]"
                name = f"[dim]{Icons.DOC} {rule.name}[/dim]"

            # Color-coded category
            cat_color = category_colors.get(rule.category.lower(), "white")
            category_text = f"[{cat_color}]{rule.category}[/{cat_color}]"

            # Truncate description but show more characters
            description = f"[dim]{Format.truncate(rule.description, 120)}[/dim]"

            table.add_row(
                name,
                status_text,
                category_text,
                description,
            )

    def show_modes_view(self, table: DataTable) -> None:
        """Show modes table with enhanced colors."""
        table.add_column("Name", key="name", width=30)
        table.add_column("Status", key="status", width=12)
        table.add_column("Purpose", key="purpose")

        if not hasattr(self, 'modes') or not self.modes:
            table.add_row("[dim]No modes found[/dim]", "", "")
            return

        for mode in self.modes:
            # Color-coded status
            if mode.status == "active":
                status_text = f"[bold magenta]● ACTIVE[/bold magenta]"
                name = f"[bold magenta]{Icons.FILTER} {mode.name}[/bold magenta]"
            else:
                status_text = f"[dim]○ inactive[/dim]"
                name = f"[dim]{Icons.FILTER} {mode.name}[/dim]"

            # Show more of the purpose
            purpose = f"[dim italic]{Format.truncate(mode.purpose, 150)}[/dim italic]"

            table.add_row(
                name,
                status_text,
                purpose,
            )

    def show_overview(self, table: DataTable) -> None:
        """Show overview with KAMEHAMEHA-level dashboard! 🔥"""
        table.add_column("Dashboard", key="dashboard")

        # Collect stats
        active_agents = 0
        total_agents = 0
        if hasattr(self, 'agents'):
            active_agents = sum(1 for a in self.agents if a.status == "active")
            total_agents = len(self.agents)

        active_modes = 0
        total_modes = 0
        if hasattr(self, 'modes'):
            active_modes = sum(1 for m in self.modes if m.status == "active")
            total_modes = len(self.modes)

        active_rules = 0
        total_rules = 0
        if hasattr(self, 'rules'):
            active_rules = sum(1 for r in self.rules if r.status == "active")
            total_rules = len(self.rules)

        total_skills = len(self.skills) if hasattr(self, 'skills') else 0

        running_workflows = 0
        if hasattr(self, 'workflows'):
            running_workflows = sum(1 for w in self.workflows if w.status == "running")

        # Helper function to add multi-line content as separate rows
        def add_multiline(content: str):
            """Split multi-line content and add each line as a separate row."""
            for line in content.split('\n'):
                table.add_row(line)

        # 🔥 KAMEHAMEHA HERO BANNER 🔥
        hero = EnhancedOverview.create_hero_banner(active_agents, total_agents)
        add_multiline(hero)
        table.add_row("")

        # 📊 SYSTEM METRICS GRID
        metrics_grid = EnhancedOverview.create_status_grid(
            active_agents, total_agents,
            active_modes, total_modes,
            active_rules, total_rules,
            total_skills,
            running_workflows
        )
        add_multiline(metrics_grid)
        table.add_row("")

        # 📈 ACTIVITY TIMELINE
        timeline = EnhancedOverview.create_activity_timeline()
        add_multiline(timeline)
        table.add_row("")

        # ✓ SYSTEM HEALTH
        health = EnhancedOverview.create_system_health()
        add_multiline(health)

        # Add performance metrics if available
        if hasattr(self, 'performance_monitor'):
            table.add_row("")
            table.add_row("[bold cyan]⚡ Performance Monitor[/bold cyan]")
            perf_full = self.performance_monitor.get_status_bar(compact=False)
            table.add_row(perf_full)

    def show_workflows_view(self, table: DataTable) -> None:
        """Show workflows table."""
        table.add_column("Name", key="name")
        table.add_column("Status", key="status")
        table.add_column("Progress", key="progress")
        table.add_column("Started", key="started")
        table.add_column("Description", key="description")

        if not hasattr(self, 'workflows') or not self.workflows:
            table.add_row("No workflows found", "", "", "", "")
            return

        for workflow in self.workflows:
            # Use StatusIcon for better visual representation
            if workflow.status == "complete":
                status_text = StatusIcon.active()  # Reuse success icon
            elif workflow.status == "running":
                status_text = StatusIcon.running()
            elif workflow.status == "error":
                status_text = StatusIcon.error()
            else:
                status_text = StatusIcon.pending()

            # Use ProgressBar utility for consistent visualization
            progress_text = "-"
            if workflow.status in ("running", "paused", "complete"):
                progress_text = ProgressBar.simple_bar(workflow.progress, 100, width=10)

            # Use Format.time_ago if timestamp is datetime
            started_text = "-"
            if workflow.started:
                # Assuming started is a timestamp
                started_dt = datetime.fromtimestamp(workflow.started)
                started_text = Format.time_ago(started_dt)

            # Use Format.truncate for description
            description = Format.truncate(workflow.description, 40) if workflow.description else ""

            # Add icon to name
            name = f"{Icons.PLAY} {workflow.name}"

            table.add_row(
                name,
                status_text,
                progress_text,
                started_text,
                description,
            )

    def show_orchestrate_view(self, table: DataTable) -> None:
        """Show orchestration dashboard with active agents and metrics."""
        table.add_column("Agent", key="agent")
        table.add_column("Workstream", key="workstream")
        table.add_column("Status", key="status")
        table.add_column("Progress", key="progress")

        tasks = getattr(self, 'agent_tasks', [])

        if not tasks:
            # Show example/placeholder data with enhanced visuals
            table.add_row(
                f"{Icons.CODE} [Agent-1] Implementation",
                "primary",
                StatusIcon.running(),
                ProgressBar.simple_bar(75, 100, width=15),
            )
            table.add_row(
                f"{Icons.TEST} [Agent-2] Code Review",
                "quality",
                StatusIcon.active(),
                ProgressBar.simple_bar(100, 100, width=15),
            )
            table.add_row(
                f"{Icons.TEST} [Agent-3] Test Automation",
                "quality",
                StatusIcon.running(),
                ProgressBar.simple_bar(60, 100, width=15),
            )
            table.add_row(
                f"{Icons.DOC} [Agent-4] Documentation",
                "quality",
                StatusIcon.pending(),
                ProgressBar.simple_bar(0, 100, width=15),
            )

            # Add metrics section
            table.add_row("", "", "", "")
            table.add_row("METRICS:", "", "", "")
            table.add_row("Parallel Efficiency:", "87%", "", "")
            table.add_row("Overall Progress:", "78%", "", "")
            table.add_row("Active Agents:", "2/4", "", "")
            table.add_row("Estimated Completion:", "2m 30s", "", "")
        else:
            # Show real task data with enhanced visuals
            for task in tasks:
                # Use ProgressBar utility
                progress_bar = ProgressBar.simple_bar(task.progress, 100, width=15)

                # Use StatusIcon based on task status
                if task.status == "complete":
                    status_text = StatusIcon.active()
                elif task.status == "running":
                    status_text = StatusIcon.running()
                elif task.status == "error":
                    status_text = StatusIcon.error()
                else:
                    status_text = StatusIcon.pending()

                # Add icon to agent name
                agent_display = f"{Icons.CODE} [{task.agent_id}] {task.agent_name}"

                table.add_row(
                    agent_display,
                    task.workstream,
                    status_text,
                    progress_bar,
                )

            # Calculate and display metrics
            total_progress = sum(t.progress for t in tasks) // len(tasks) if tasks else 0
            running_count = sum(1 for t in tasks if t.status == "running")
            complete_count = sum(1 for t in tasks if t.status == "complete")
            parallel_efficiency = int((running_count / len(tasks)) * 100) if tasks else 0

            # Add metrics section
            table.add_row("", "", "", "")
            table.add_row("METRICS:", "", "", "")
            table.add_row("Parallel Efficiency:", f"{parallel_efficiency}%", "", "")
            table.add_row("Overall Progress:", f"{total_progress}%", "", "")
            table.add_row("Active Agents:", f"{running_count}/{len(tasks)}", "", "")
            table.add_row("Completed:", f"{complete_count}/{len(tasks)}", "", "")

            # Estimate completion time
            if running_count > 0 and total_progress > 0:
                estimated_minutes = int((100 - total_progress) * 0.5)
                table.add_row("Estimated Completion:", f"{estimated_minutes}m", "", "")

    def show_ai_assistant_view(self, table: DataTable) -> None:
        """Show AI assistant recommendations and predictions."""
        table.add_column("Type", key="type", width=20)
        table.add_column("Recommendation", key="recommendation", width=30)
        table.add_column("Confidence", key="confidence", width=12)
        table.add_column("Reason")

        if not hasattr(self, 'intelligent_agent'):
            table.add_row(
                "[dim]System[/dim]",
                "[yellow]AI Assistant not initialized[/yellow]",
                "",
                ""
            )
            return

        # Get recommendations
        recommendations = self.intelligent_agent.get_recommendations()

        # Show header
        table.add_row(
            "[bold cyan]🤖 INTELLIGENT RECOMMENDATIONS[/bold cyan]",
            "",
            "",
            ""
        )
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            ""
        )
        table.add_row("", "", "", "")

        if not recommendations:
            table.add_row(
                "[dim]Agent[/dim]",
                "[dim]No recommendations[/dim]",
                "",
                "[dim]Context analysis found no suggestions[/dim]"
            )
        else:
            # Show agent recommendations
            for rec in recommendations[:10]:  # Top 10
                # Color by urgency
                if rec.urgency == "critical":
                    urgency_color = "red"
                    urgency_icon = "🔴"
                elif rec.urgency == "high":
                    urgency_color = "yellow"
                    urgency_icon = "🟡"
                elif rec.urgency == "medium":
                    urgency_color = "cyan"
                    urgency_icon = "🔵"
                else:
                    urgency_color = "dim"
                    urgency_icon = "⚪"

                # Color by confidence
                confidence_pct = int(rec.confidence * 100)
                if rec.confidence >= 0.8:
                    confidence_text = f"[bold green]{confidence_pct}%[/bold green]"
                elif rec.confidence >= 0.6:
                    confidence_text = f"[yellow]{confidence_pct}%[/yellow]"
                else:
                    confidence_text = f"[dim]{confidence_pct}%[/dim]"

                # Auto-activate indicator
                auto_text = " [bold cyan]AUTO[/bold cyan]" if rec.auto_activate else ""

                table.add_row(
                    f"[{urgency_color}]{urgency_icon} Agent[/{urgency_color}]",
                    f"[bold]{rec.agent_name}[/bold]{auto_text}",
                    confidence_text,
                    f"[dim italic]{rec.reason}[/dim italic]"
                )

        # Show workflow prediction if available
        table.add_row("", "", "", "")
        table.add_row(
            "[bold magenta]🎯 WORKFLOW PREDICTION[/bold magenta]",
            "",
            "",
            ""
        )
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            ""
        )
        table.add_row("", "", "", "")

        workflow = self.intelligent_agent.predict_workflow()

        if workflow:
            confidence_pct = int(workflow.confidence * 100)
            success_pct = int(workflow.success_probability * 100)

            table.add_row(
                "[cyan]Workflow[/cyan]",
                f"[bold]{workflow.workflow_name}[/bold]",
                f"[green]{confidence_pct}%[/green]",
                f"[dim]Based on {workflow.based_on_pattern} pattern[/dim]"
            )

            table.add_row(
                "[cyan]Est. Duration[/cyan]",
                f"[yellow]{workflow.estimated_duration // 60}m {workflow.estimated_duration % 60}s[/yellow]",
                "",
                ""
            )

            table.add_row(
                "[cyan]Success Rate[/cyan]",
                f"[green]{success_pct}%[/green]",
                "",
                ""
            )

            table.add_row("", "", "", "")
            table.add_row(
                "[cyan]Agent Sequence:[/cyan]",
                "",
                "",
                ""
            )

            for i, agent in enumerate(workflow.agents_sequence, 1):
                table.add_row(
                    "",
                    f"[dim]{i}.[/dim] {Icons.CODE} {agent}",
                    "",
                    ""
                )
        else:
            table.add_row(
                "[dim]Workflow[/dim]",
                "[dim]Not enough data[/dim]",
                "",
                "[dim italic]Need 3+ similar sessions for prediction[/dim italic]"
            )

        # Show context info
        table.add_row("", "", "", "")
        table.add_row(
            "[bold yellow]📊 CONTEXT ANALYSIS[/bold yellow]",
            "",
            "",
            ""
        )
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            ""
        )
        table.add_row("", "", "", "")

        context = self.intelligent_agent.current_context
        if context:
            table.add_row(
                "[cyan]Files Changed[/cyan]",
                f"{len(context.files_changed)}",
                "",
                ""
            )

            # Show detected contexts
            contexts_detected = []
            if context.has_frontend:
                contexts_detected.append("[blue]Frontend[/blue]")
            if context.has_backend:
                contexts_detected.append("[green]Backend[/green]")
            if context.has_database:
                contexts_detected.append("[magenta]Database[/magenta]")
            if context.has_tests:
                contexts_detected.append("[yellow]Tests[/yellow]")
            if context.has_auth:
                contexts_detected.append("[red]Auth[/red]")
            if context.has_api:
                contexts_detected.append("[cyan]API[/cyan]")

            if contexts_detected:
                table.add_row(
                    "[cyan]Detected:[/cyan]",
                    ", ".join(contexts_detected),
                    "",
                    ""
                )

            # Show errors if any
            if context.errors_count > 0 or context.test_failures > 0:
                table.add_row(
                    "[red]Issues:[/red]",
                    f"[red]{context.errors_count} errors, {context.test_failures} test failures[/red]",
                    "",
                    ""
                )

        # Show actions
        table.add_row("", "", "", "")
        table.add_row(
            "[bold green]⚡ QUICK ACTIONS[/bold green]",
            "",
            "",
            ""
        )
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            ""
        )
        table.add_row("", "", "", "")
        table.add_row(
            "",
            "[dim cyan]Press [white]A[/white] → Auto-activate recommended agents[/dim cyan]",
            "",
            ""
        )
        table.add_row(
            "",
            "[dim cyan]Press [white]R[/white] → Refresh recommendations[/dim cyan]",
            "",
            ""
        )

    def action_view_overview(self) -> None:
        """Switch to overview."""
        self.current_view = "overview"
        self.status_message = "Switched to Overview"
        self.notify("📊 Overview", severity="information", timeout=1)

    def action_view_agents(self) -> None:
        """Switch to agents view."""
        self.current_view = "agents"
        self.status_message = "Switched to Agents"
        self.notify("🤖 Agents", severity="information", timeout=1)

    def action_view_modes(self) -> None:
        """Switch to modes view."""
        self.current_view = "modes"
        self.status_message = "Switched to Modes"
        self.notify("🎨 Modes", severity="information", timeout=1)

    def action_view_rules(self) -> None:
        """Switch to rules view."""
        self.current_view = "rules"
        self.status_message = "Switched to Rules"
        self.notify("📜 Rules", severity="information", timeout=1)

    def action_view_skills(self) -> None:
        """Switch to skills view."""
        self.current_view = "skills"
        self.status_message = "Switched to Skills"
        self.notify("💎 Skills", severity="information", timeout=1)

    def action_view_workflows(self) -> None:
        """Switch to workflows view."""
        self.current_view = "workflows"
        self.status_message = "Switched to Workflows"
        self.notify("🔄 Workflows", severity="information", timeout=1)

    def action_view_orchestrate(self) -> None:
        """Switch to orchestrate view."""
        self.current_view = "orchestrate"
        self.status_message = "Switched to Orchestrate"
        self.notify("🎯 Orchestrate", severity="information", timeout=1)

    def action_view_ai_assistant(self) -> None:
        """Switch to AI assistant view."""
        self.current_view = "ai_assistant"
        self.status_message = "Switched to AI Assistant"
        self.notify("🤖 AI Assistant", severity="information", timeout=1)
        # Refresh recommendations when entering view
        if hasattr(self, 'intelligent_agent'):
            self.intelligent_agent.analyze_context()

    def action_auto_activate(self) -> None:
        """Auto-activate recommended agents."""
        if not hasattr(self, 'intelligent_agent'):
            self.notify("AI Assistant not initialized", severity="error", timeout=2)
            return

        auto_agents = self.intelligent_agent.get_auto_activations()

        if not auto_agents:
            self.notify("No auto-activation recommendations", severity="information", timeout=2)
            return

        activated_count = 0
        for agent_name in auto_agents:
            try:
                exit_code, message = agent_activate(agent_name)
                if exit_code == 0:
                    self.intelligent_agent.mark_auto_activated(agent_name)
                    activated_count += 1
            except Exception:
                pass

        if activated_count > 0:
            self.notify(f"✓ Auto-activated {activated_count} agents", severity="success", timeout=3)
            self.load_agents()
            self.update_view()
        else:
            self.notify("Failed to auto-activate agents", severity="error", timeout=2)

    def _check_auto_activations(self) -> None:
        """Check for high-confidence auto-activations on startup."""
        if not hasattr(self, 'intelligent_agent'):
            return

        auto_agents = self.intelligent_agent.get_auto_activations()

        if auto_agents:
            agents_str = ", ".join(auto_agents[:3])
            if len(auto_agents) > 3:
                agents_str += f" +{len(auto_agents) - 3} more"

            self.notify(
                f"🤖 AI Suggestion: {agents_str} (Press 'A' to auto-activate)",
                severity="information",
                timeout=5
            )

    def action_toggle(self) -> None:
        """Toggle selected item."""
        if self.current_view == "agents":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                row_key = table.get_row_at(table.cursor_row)
                if row_key and len(row_key) > 0:
                    # Get plain text from first column (strip Rich markup and icons)
                    from rich.text import Text
                    raw_name = str(row_key[0])
                    # Use Rich to strip markup, then remove icon emoji
                    plain_text = Text.from_markup(raw_name).plain
                    # Remove the icon (first character if it's an emoji)
                    agent_name = plain_text.strip()
                    if agent_name and len(agent_name) > 0 and ord(agent_name[0]) > 127:
                        agent_name = agent_name[1:].strip()

                    agent = next((a for a in self.agents if a.name == agent_name), None)
                    if agent:
                        try:
                            if agent.status == "active":
                                exit_code, message = agent_deactivate(agent.name)
                            else:
                                exit_code, message = agent_activate(agent.name)

                            # Remove ANSI codes
                            import re
                            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                            self.status_message = clean_message.split("\n")[0]

                            if exit_code == 0:
                                if agent.status == "active":
                                    self.notify(f"✓ Deactivated {agent.name}", severity="success", timeout=2)
                                else:
                                    self.notify(f"✓ Activated {agent.name}", severity="success", timeout=2)
                                self.load_agents()
                                self.update_view()
                            else:
                                self.notify(f"✗ Failed to toggle {agent.name}", severity="error", timeout=3)
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(f"✗ Error: {str(e)[:50]}", severity="error", timeout=3)

        elif self.current_view == "rules":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                row_key = table.get_row_at(table.cursor_row)
                if row_key and len(row_key) > 0:
                    rule_name = str(row_key[0])
                    rule = next((r for r in self.rules if r.name == rule_name), None)
                    if rule:
                        try:
                            if rule.status == "active":
                                message = rules_deactivate(rule.path.stem)
                            else:
                                message = rules_activate(rule.path.stem)

                            # Remove ANSI codes
                            import re
                            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                            self.status_message = clean_message.split("\n")[0]

                            if rule.status == "active":
                                self.notify(f"✓ Deactivated {rule.name}", severity="success", timeout=2)
                            else:
                                self.notify(f"✓ Activated {rule.name}", severity="success", timeout=2)

                            self.load_rules()
                            self.update_view()
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(f"✗ Error: {str(e)[:50]}", severity="error", timeout=3)

        elif self.current_view == "modes":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                row_key = table.get_row_at(table.cursor_row)
                if row_key and len(row_key) > 0:
                    mode_name = str(row_key[0])
                    mode = next((m for m in self.modes if m.name == mode_name), None)
                    if mode:
                        try:
                            if mode.status == "active":
                                exit_code, message = mode_deactivate(mode.path.stem)
                            else:
                                exit_code, message = mode_activate(mode.path.stem)

                            # Remove ANSI codes
                            import re
                            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                            self.status_message = clean_message.split("\n")[0]

                            if exit_code == 0:
                                if mode.status == "active":
                                    self.notify(f"✓ Deactivated {mode.name}", severity="success", timeout=2)
                                else:
                                    self.notify(f"✓ Activated {mode.name}", severity="success", timeout=2)
                                self.load_modes()
                                self.update_view()
                            else:
                                self.notify(f"✗ Failed to toggle {mode.name}", severity="error", timeout=3)
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(f"✗ Error: {str(e)[:50]}", severity="error", timeout=3)

    def action_refresh(self) -> None:
        """Refresh current view."""
        if self.current_view == "agents":
            self.load_agents()
        elif self.current_view == "rules":
            self.load_rules()
        elif self.current_view == "modes":
            self.load_modes()
        elif self.current_view == "skills":
            self.load_skills()
        elif self.current_view == "workflows":
            self.load_workflows()
        elif self.current_view == "orchestrate":
            self.load_agent_tasks()

        self.update_view()
        self.status_message = f"Refreshed {self.current_view}"
        self.notify(f"🔄 Refreshed {self.current_view}", severity="information", timeout=1)

    def action_help(self) -> None:
        """Show help."""
        self.status_message = "Help: 1-7=Views, Ctrl+P=Commands, Space=Toggle, R=Refresh, Q=Quit"

    async def action_show_command_palette(self) -> None:
        """Show command palette for quick navigation."""
        commands = self.command_registry.get_all()
        result = await self.push_screen(CommandPalette(commands), wait_for_dismiss=True)

        if result:
            # Execute the selected command
            if result == "show_agents":
                self.action_view_agents()
            elif result == "show_skills":
                self.action_view_skills()
            elif result == "show_modes":
                self.action_view_modes()
            elif result == "show_rules":
                self.action_view_rules()
            elif result == "show_workflows":
                self.action_view_workflows()
            elif result == "show_orchestrate":
                self.action_view_orchestrate()
            elif result == "activate_agent":
                # Switch to agents view and show instruction
                self.action_view_agents()
                self.status_message = "Select an agent and press Space to activate"
            elif result == "deactivate_agent":
                # Switch to agents view and show instruction
                self.action_view_agents()
                self.status_message = "Select an agent and press Space to deactivate"
            elif result == "toggle_mode":
                # Switch to modes view
                self.action_view_modes()
                self.status_message = "Select a mode and press Space to toggle"
            elif result == "toggle_rule":
                # Switch to rules view
                self.action_view_rules()
                self.status_message = "Select a rule and press Space to toggle"
            elif result == "create_skill":
                self.status_message = "Skill creation wizard (not yet implemented)"
            elif result == "export_context":
                self.current_view = "export"
                self.update_view()
            elif result == "show_help":
                self.action_help()
            elif result == "refresh":
                self.action_refresh()
            elif result == "quit":
                self.exit()
            else:
                self.status_message = f"Command: {result} (not yet implemented)"


def main() -> int:
    """Entry point for the Textual TUI."""
    app = AgentTUI()
    app.run()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
