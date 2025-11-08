"""Textual-based Terminal User Interface for claude-ctx."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
import yaml
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, ContentSwitcher
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
    collect_context_components,
    export_context,
    init_profile,
    profile_save,
    _profile_reset,
    skill_validate,
    skill_metrics,
    skill_metrics_reset,
    skill_info,
    skill_versions,
    skill_deps,
    skill_agents,
    skill_compose,
    skill_analyze,
    skill_suggest,
    skill_report,
    skill_trending,
    skill_analytics,
    skill_community_list,
    skill_community_install,
    skill_community_validate,
    skill_community_rate,
    skill_community_search,
)
from .core.rules import rules_activate, rules_deactivate
from .core.modes import mode_activate, mode_deactivate
from .core.base import _iter_md_files, _parse_active_entries
from .core.mcp import (
    discover_servers,
    validate_server_config,
    generate_config_snippet,
    mcp_show,
    mcp_docs,
    mcp_test,
    mcp_diagnose,
    MCPServerInfo,
)
from .core.agents import BUILT_IN_PROFILES
from .tui_icons import Icons, StatusIcon
from .tui_format import Format
from .tui_progress import ProgressBar
from .tui_command_palette import CommandPalette, CommandRegistry, DEFAULT_COMMANDS
from .tui_commands import AgentCommandProvider
from .tui_dashboard import MetricsCollector
from .tui_performance import PerformanceMonitor
from .tui_workflow_viz import WorkflowNode, DependencyVisualizer
from .tui_overview_enhanced import EnhancedOverview
from .intelligence import IntelligentAgent, AgentRecommendation, WorkflowPrediction
from .tui_supersaiyan import SuperSaiyanStatusBar
from .tui_dialogs import TaskEditorDialog, ConfirmDialog, PromptDialog, TextViewerDialog


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
    category: str = "general"
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


PROFILE_DESCRIPTIONS: Dict[str, str] = {
    "minimal": "Load minimal profile (essential agents only)",
    "frontend": "Load frontend profile (TypeScript + review)",
    "web-dev": "Load web-dev profile (full-stack)",
    "backend": "Load backend profile (Python + security)",
    "devops": "Load devops profile (infrastructure & deploy)",
    "documentation": "Load documentation profile (writing focus)",
    "data-ai": "Load data/AI profile",
    "quality": "Load quality profile (QA + security)",
    "meta": "Load meta tooling profile",
    "developer-experience": "Load DX profile",
    "product": "Load product development profile",
    "full": "Load full profile (all agents)",
}

EXPORT_CATEGORIES = [
    ("core", "Core Framework", "FLAGS, PRINCIPLES, RULES"),
    ("rules", "Rules", "Active rule modules"),
    ("modes", "Modes", "Active behavioral modes"),
    ("agents", "Agents", "All available agents"),
    ("mcp_docs", "MCP Docs", "Model Context Protocol docs"),
    ("skills", "Skills", "Local skill definitions"),
]

DEFAULT_EXPORT_OPTIONS = {key: True for key, _label, _desc in EXPORT_CATEGORIES}

PRIMARY_VIEW_BINDINGS = [
    ("1", "overview", "Overview"),
    ("2", "agents", "Agents"),
    ("3", "modes", "Modes"),
    ("4", "rules", "Rules"),
    ("5", "skills", "Skills"),
    ("6", "workflows", "Workflows"),
    ("7", "mcp", "MCP"),
    ("8", "profiles", "Profiles"),
    ("9", "export", "Export"),
    ("0", "ai_assistant", "AI Assistant"),
]


class AgentTUI(App):
    """Textual TUI for claude-ctx management."""

    CATEGORY_PALETTE = {
        "orchestration": "cyan",
        "analysis": "blue",
        "development": "green",
        "documentation": "yellow",
        "testing": "magenta",
        "quality": "red",
        "general": "white",
        "ops": "bright_cyan",
        "ai": "bright_magenta",
    }

    CATEGORY_FALLBACK_COLORS = [
        "bright_blue",
        "bright_magenta",
        "bright_green",
        "bright_yellow",
        "deep_sky_blue1",
        "spring_green2",
        "light_salmon1",
        "plum1",
        "orange3",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.profiles: List[Dict[str, Optional[str]]] = []
        self.mcp_servers: List[MCPServerInfo] = []
        self.mcp_error: Optional[str] = None
        self.export_options: Dict[str, bool] = DEFAULT_EXPORT_OPTIONS.copy()
        self.export_agent_generic: bool = True
        self.export_row_meta: List[Tuple[str, Optional[str]]] = []

    CSS = """
    /* Super Saiyan Mode Colors 🔥 */
    $primary: #3b82f6;
    $secondary: #8b5cf6;
    $accent: #06b6d4;
    $success: #10b981;
    $warning: #f59e0b;
    $error: #ef4444;
    $surface: #050714;
    $surface-lighten-1: #111633;
    $surface-lighten-2: #1c2145;
    $text: #f8fafc;
    $text-muted: #94a3b8;

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
        background: $primary 40%;
        color: white;
        text-style: bold;
    }

    DataTable:focus > .datatable--cursor {
        background: $primary;
        color: white;
        text-style: bold;
        border: heavy $accent;
    }

    Header {
        background: $surface-lighten-2;
        color: $text;
        text-style: bold;
        border-bottom: tall $primary;
    }

    Footer {
        background: $surface-lighten-2;
        color: $text-muted;
    }

    #status-bar {
        height: auto;
    }

    /* Command Palette Styles - Super Saiyan */
    #command-palette-container {
        align: center middle;
        width: 70%;
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

    #palette-subtitle {
        text-align: center;
        color: $text-muted;
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

    #main-container {
        height: 1fr;
        padding: 1;
    }

    #view-switcher {
        height: 1fr;
    }

    #galaxy-view {
        height: 1fr;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $secondary;
    }

    #galaxy-layout {
        height: 1fr;
    }

    .galaxy-panel {
        border: dashed $secondary;
        padding: 1;
        height: 1fr;
    }

    #galaxy-graph {
        overflow: auto;
    }
    """

    BINDINGS = [
        *[Binding(key, f"view_{name}", label, show=True) for key, name, label in PRIMARY_VIEW_BINDINGS],
        Binding("o", "view_orchestrate", "Orchestrate", show=True),
        Binding("g", "view_galaxy", "Galaxy", show=True),
        Binding("t", "view_tasks", "Tasks", show=True),
        Binding("ctrl+p", "command_palette", "Commands", show=True),
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("space", "toggle", "Toggle"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "auto_activate", "Auto-Activate"),
        Binding("v", "validate_context", "Validate", show=False),
        Binding("m", "metrics_context", "Metrics", show=False),
        Binding("c", "context_action", "Action", show=False),
        Binding("d", "docs_context", "Docs", show=False),
        Binding("s", "details_context", "Details", show=False),
        Binding("ctrl+t", "mcp_test_selected", "Test", show=False),
        Binding("ctrl+d", "mcp_diagnose", "Diagnose", show=False),
        Binding("f", "export_cycle_format", "Format", show=False),
        Binding("e", "export_run", "Export", show=False),
        Binding("x", "export_clipboard", "Copy", show=False),
        Binding("n", "profile_save_prompt", "Save Profile", show=False),
        Binding("D", "profile_delete", "Delete Profile", show=False),
    ]

    # Register command provider for Textual's command palette
    # Textual looks for COMMANDS, not COMMAND_PROVIDERS!
    COMMANDS = {AgentCommandProvider}

    current_view: reactive[str] = reactive("agents")
    status_message: reactive[str] = reactive("Welcome to claude-ctx TUI")

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        with Container(id="main-container"):
            with ContentSwitcher(id="view-switcher"):
                yield DataTable(id="main-table")
                with Container(id="galaxy-view"):
                    yield Static("✦ Agent Galaxy ✦", id="galaxy-header")
                    with Horizontal(id="galaxy-layout"):
                        yield Static("", id="galaxy-stats", classes="galaxy-panel")
                        yield Static("", id="galaxy-graph", classes="galaxy-panel")
        yield SuperSaiyanStatusBar(id="status-bar")
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
        self.load_profiles()
        self.load_mcp_servers()
        self.update_view()

        # Start performance monitoring timer
        self.set_interval(1.0, self.update_performance_status)

        # Force initial status bar update
        self.watch_status_message(self.status_message)

        # Show AI recommendations if high confidence
        self._check_auto_activations()

    def watch_status_message(self, _message: str) -> None:
        """Update status bar when message changes."""
        self.refresh_status_bar()

    def update_performance_status(self) -> None:
        """Update performance metrics in status bar (called by timer)."""
        self.refresh_status_bar()

    def refresh_status_bar(self) -> None:
        """Push latest UI/metric info into the neon status bar."""
        try:
            status_bar = self.query_one(SuperSaiyanStatusBar)
        except Exception:
            return

        agents = getattr(self, 'agents', [])
        agent_total = len(agents)
        agent_active = sum(1 for a in agents if getattr(a, 'status', '') == "active")
        tasks = getattr(self, 'agent_tasks', [])
        task_active = sum(1 for t in tasks if getattr(t, 'status', '') == "running")
        perf_text = ""
        if hasattr(self, 'performance_monitor'):
            perf_text = self.performance_monitor.get_status_bar(compact=True)

        status_bar.update_payload(
            view=self.current_view.title(),
            message=self.status_message,
            perf=perf_text,
            agent_active=agent_active,
            agent_total=agent_total,
            task_active=task_active,
        )

    def watch_current_view(self, view: str) -> None:
        """Update display when view changes."""
        self.update_view()
        self.refresh_status_bar()

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

    def _table_cursor_index(self) -> Optional[int]:
        """Return the current row index in the main DataTable."""
        try:
            table = self.query_one("#main-table", DataTable)
        except Exception:
            return None
        return table.cursor_row

    def _selected_profile(self) -> Optional[Dict[str, Optional[str]]]:
        index = self._table_cursor_index()
        if index is None or not self.profiles:
            return None
        if index < 0 or index >= len(self.profiles):
            return None
        return self.profiles[index]

    def _selected_export_meta(self) -> Optional[Tuple[str, Optional[str]]]:
        index = self._table_cursor_index()
        if index is None:
            return None
        if index < 0 or index >= len(self.export_row_meta):
            return None
        return self.export_row_meta[index]

    def _selected_mcp_server(self) -> Optional[MCPServerInfo]:
        index = self._table_cursor_index()
        if index is None:
            return None
        servers = getattr(self, 'mcp_servers', [])
        if index < 0 or index >= len(servers):
            return None
        return servers[index]

    def _selected_skill(self) -> Optional[Dict[str, str]]:
        index = self._table_cursor_index()
        skills = getattr(self, 'skills', [])
        if index is None or not skills:
            return None
        if index < 0 or index >= len(skills):
            return None
        return skills[index]

    def _skill_slug(self, skill: Dict[str, str]) -> str:
        path_value = skill.get("path")
        if not path_value:
            return skill.get("name", "").replace(" ", "-")
        skill_path = Path(path_value)
        # SKILL.md lives inside the skill directory; use parent directory name
        if skill_path.name.lower() == "skill.md":
            return skill_path.parent.name
        return skill_path.stem

    async def _get_skill_slug(self, prompt_title: str = "Skill Name") -> Optional[str]:
        if self.current_view == "skills":
            skill = self._selected_skill()
            if skill:
                return self._skill_slug(skill)
        return await self._prompt_text(prompt_title, "Enter skill name", placeholder="e.g. observability/alerts")

    def _copy_to_clipboard(self, text: str) -> bool:
        """Attempt to copy text to the system clipboard."""
        try:
            import pyperclip  # type: ignore

            pyperclip.copy(text)
            return True
        except Exception:
            pass

        try:
            subprocess.run(["pbcopy"], check=True, input=text.encode("utf-8"))
            return True
        except Exception:
            pass

        try:
            if shutil.which("xclip"):
                subprocess.run(["xclip", "-selection", "clipboard"], check=True, input=text.encode("utf-8"))
                return True
        except Exception:
            pass

        return False

    def _apply_saved_profile(self, profile_path: Path) -> Tuple[int, str]:
        """Apply a saved .profile file by activating listed agents/modes/rules."""
        try:
            content = profile_path.read_text(encoding="utf-8")
        except Exception as exc:
            return 1, f"Failed to read profile: {exc}"

        agents = [Path(entry).stem for entry in self._extract_profile_list(content, "AGENTS")]
        modes = self._extract_profile_list(content, "MODES")
        rules = self._extract_profile_list(content, "RULES")

        exit_code, message = _profile_reset()
        messages = []
        if message:
            messages.append(message)
        if exit_code != 0:
            return exit_code, "\n".join(messages)

        for agent_name in filter(None, agents):
            exit_code, agent_message = agent_activate(agent_name)
            if agent_message:
                messages.append(agent_message)
            if exit_code != 0:
                return exit_code, "\n".join(messages)

        for mode_name in filter(None, modes):
            exit_code, mode_message = mode_activate(mode_name)
            if mode_message:
                messages.append(mode_message)
            if exit_code != 0 and (not mode_message or "already active" not in mode_message.lower()):
                return exit_code, "\n".join(messages)

        for rule_name in filter(None, rules):
            rule_message = rules_activate(rule_name)
            if rule_message:
                messages.append(rule_message)

        messages.append(f"[green]Applied profile from {profile_path.name}[/green]")
        return 0, "\n".join(messages)

    def _extract_profile_list(self, content: str, key: str) -> List[str]:
        """Extract a space-delimited list from profile metadata."""
        pattern = re.compile(rf'{key}="([^"]*)"')
        match = pattern.search(content)
        if not match:
            return []
        value = match.group(1)
        if not value:
            return []
        return [entry.strip() for entry in value.split() if entry.strip()]

    def _clean_ansi(self, text: str | None) -> str:
        """Remove ANSI escape codes for clean status messages."""
        if not text:
            return ""
        return re.sub(r"\x1b\[[0-9;]*m", "", text)

    async def _show_text_dialog(self, title: str, body: str) -> None:
        """Display multi-line text in a modal dialog."""
        if not body:
            return
        await self.push_screen(TextViewerDialog(title, body), wait_for_dismiss=True)

    async def _prompt_text(self, title: str, prompt: str, *, default: str = "", placeholder: str = "") -> Optional[str]:
        dialog = PromptDialog(title, prompt, default=default, placeholder=placeholder)
        value = await self.push_screen(dialog, wait_for_dismiss=True)
        if value is None:
            return None
        value = value.strip()
        return value or None

    async def _handle_skill_result(
        self,
        func,
        *,
        args: Optional[List[str]] = None,
        title: str,
        success: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        args = args or []
        try:
            exit_code, message = func(*args)
        except Exception as exc:
            self.notify(f"Skill command failed: {exc}", severity="error", timeout=3)
            return

        clean = self._clean_ansi(message)
        if clean:
            await self._show_text_dialog(title, clean)

        if exit_code == 0:
            if success:
                self.notify(success, severity="success", timeout=2)
        else:
            self.notify(error or f"{title} failed", severity="error", timeout=3)

    def load_agents(self) -> None:
        """Load agents from the system."""
        try:
            agents = []
            seen_names = set()  # Track agent names to avoid duplicates
            claude_dir = _resolve_claude_dir()
            self.agent_slug_lookup = {}
            self.agent_category_lookup = {}

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
            for agent in agents:
                variants = {
                    agent.name.lower(),
                    agent.slug.lower(),
                    agent.name.lower().replace(" ", "-"),
                    agent.name.lower().replace(" ", "_"),
                    agent.slug.lower().replace("_", "-"),
                    f"{agent.slug.lower()}.md",
                }
                for variant in variants:
                    self.agent_slug_lookup[variant] = agent.slug
                self.agent_category_lookup[agent.slug.lower()] = agent.category
                self.agent_category_lookup[agent.name.lower()] = agent.category
            active_count = sum(1 for a in agents if a.status == "active")
            inactive_count = len(agents) - active_count
            self.status_message = f"Loaded {len(agents)} agents ({active_count} active, {inactive_count} inactive)"
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record("agents_active", float(active_count))
            self.refresh_status_bar()

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

    def show_profiles_view(self, table: DataTable) -> None:
        """Render profile management view."""
        table.add_column("Profile", width=28)
        table.add_column("Type", width=12)
        table.add_column("Description")
        table.add_column("Updated", width=18)

        if not self.profiles:
            table.add_row("[dim]No profiles found[/dim]", "", "", "")
            return

        for profile in self.profiles:
            name = profile.get("name", "unknown")
            ptype = profile.get("type", "built-in")
            description = Format.truncate(profile.get("description", ""), 60)
            updated = profile.get("modified") or "-"
            icon = Icons.SUCCESS if ptype == "built-in" else Icons.DOC
            if ptype == "built-in":
                type_text = "[cyan]Built-in[/cyan]"
            else:
                type_text = "[magenta]Saved[/magenta]"

            table.add_row(
                f"{icon} {name}",
                type_text,
                f"[dim]{description}[/dim]" if description else "",
                updated,
            )

    def show_export_view(self, table: DataTable) -> None:
        """Render export configuration view."""
        table.add_column("Component", width=26)
        table.add_column("State", width=20)
        table.add_column("Details")

        self.export_row_meta = []
        try:
            components = collect_context_components()
        except Exception as exc:
            components = {}
            self.status_message = f"Export scan failed: {exc}"[:120]

        for key, label, description in EXPORT_CATEGORIES:
            enabled = self.export_options.get(key, True)
            count = len(components.get(key, {}))
            icon = Icons.SUCCESS if enabled else Icons.WARNING
            state = "[green]Included[/green]" if enabled else "[dim]Excluded[/dim]"
            state = f"{state} ({count} files)"

            table.add_row(
                f"{icon} {label}",
                state,
                Format.truncate(description or "", 60),
            )
            self.export_row_meta.append(("category", key))

        format_label = "Agent-generic" if self.export_agent_generic else "Claude-specific"
        format_color = "green" if self.export_agent_generic else "yellow"
        table.add_row(
            "Format",
            f"[{format_color}]{format_label}[/{format_color}]",
            "Toggle with 'f'",
        )
        self.export_row_meta.append(("format", "agent_generic"))

        summary = self._build_export_summary(components)
        table.add_row(
            "Summary",
            f"[dim]{summary}[/dim]",
            "Press 'e' to export, 'x' to copy",
        )
        self.export_row_meta.append(("summary", None))

    def _build_export_summary(self, components: Dict[str, Dict[str, Path]]) -> str:
        """Create a short summary string for enabled export categories."""
        enabled = []
        for key, label, _description in EXPORT_CATEGORIES:
            if not self.export_options.get(key, True):
                continue
            count = len(components.get(key, {}))
            enabled.append(f"{label} ({count})")

        if not enabled:
            return "No components selected"
        if len(enabled) <= 3:
            return ", ".join(enabled)
        return ", ".join(enabled[:3]) + ", …"

    def _export_exclude_categories(self) -> set[str]:
        """Return the set of categories to exclude when exporting."""
        return {key for key, enabled in self.export_options.items() if not enabled}

    def _default_export_path(self) -> Path:
        """Best-effort default export path."""
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop / "claude-ctx-export.md"
        return Path.cwd() / "claude-ctx-export.md"

    def load_agent_tasks(self) -> None:
        """Load active agent tasks for orchestration view."""
        tasks: List[AgentTask] = []
        try:
            tasks_dir = self._tasks_dir()

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
                        category=task_info.get("category", "general"),
                        started=task_info.get("started"),
                        completed=task_info.get("completed"),
                    ))
        except Exception:
            # No active tasks or error reading - use empty list
            pass

        tasks.sort(key=lambda t: t.agent_name.lower())
        self.agent_tasks = tasks
        self.refresh_status_bar()

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
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record("rules_active", float(active_count))

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
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record("modes_active", float(active_count))

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
        if hasattr(self, 'metrics_collector'):
            running = sum(1 for w in workflows if w.status == "running")
            self.metrics_collector.record("workflows_running", float(running))

    def load_profiles(self) -> None:
        """Load available profiles (built-in + saved)."""
        try:
            profiles: List[Dict[str, Optional[str]]] = []
            claude_dir = _resolve_claude_dir()

            for name in BUILT_IN_PROFILES:
                profiles.append({
                    "name": name,
                    "type": "built-in",
                    "description": PROFILE_DESCRIPTIONS.get(name, "Built-in profile"),
                    "path": None,
                    "modified": None,
                })

            profiles_dir = claude_dir / "profiles"
            if profiles_dir.is_dir():
                for profile_file in sorted(profiles_dir.glob("*.profile")):
                    modified_iso = None
                    try:
                        modified_iso = datetime.fromtimestamp(profile_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    except OSError:
                        modified_iso = None
                    profiles.append({
                        "name": profile_file.stem,
                        "type": "saved",
                        "description": "Saved profile snapshot",
                        "path": str(profile_file),
                        "modified": modified_iso,
                    })

            self.profiles = profiles
        except Exception as exc:
            self.profiles = []
            self.status_message = f"Error loading profiles: {exc}"[:160]

    def load_mcp_servers(self) -> None:
        """Load MCP server definitions."""
        try:
            success, servers, error = discover_servers()
            if success:
                self.mcp_servers = servers
                self.mcp_error = None
            else:
                self.mcp_servers = []
                self.mcp_error = error
        except Exception as exc:
            self.mcp_servers = []
            self.mcp_error = str(exc)

    def update_view(self) -> None:
        """Update the table based on current view."""
        switcher = self.query_one("#view-switcher", ContentSwitcher)
        table = self.query_one("#main-table", DataTable)
        table.clear(columns=True)

        if self.current_view == "galaxy":
            switcher.current = "galaxy-view"
            self.show_galaxy_view()
            return

        switcher.current = "main-table"

        if self.current_view == "overview":
            self.show_overview(table)
            return

        if self.current_view == "agents":
            self.show_agents_view(table)
        elif self.current_view == "rules":
            self.show_rules_view(table)
        elif self.current_view == "modes":
            self.show_modes_view(table)
        elif self.current_view == "skills":
            self.show_skills_view(table)
        elif self.current_view == "workflows":
            self.show_workflows_view(table)
        elif self.current_view == "orchestrate":
            self.show_orchestrate_view(table)
        elif self.current_view == "mcp":
            self.show_mcp_view(table)
        elif self.current_view == "profiles":
            self.show_profiles_view(table)
        elif self.current_view == "export":
            self.show_export_view(table)
        elif self.current_view == "ai_assistant":
            self.show_ai_assistant_view(table)
        elif self.current_view == "tasks":
            self.show_tasks_view(table)
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

            # Color-coded category via palette
            category_text = self._format_category(agent.category)

            # Color-coded tier
            tier_color = tier_colors.get(agent.tier.lower(), "white")
            tier_text = f"[{tier_color}]{agent.tier}[/{tier_color}]"

            table.add_row(
                name,
                status_text,
                category_text,
                tier_text,
            )

    def show_tasks_view(self, table: DataTable) -> None:
        """Show task management table."""
        table.add_column("Task", key="task", width=30)
        table.add_column("Category", key="category", width=16)
        table.add_column("Workstream", key="workstream", width=16)
        table.add_column("Status", key="status", width=12)
        table.add_column("Progress", key="progress", width=12)
        table.add_column("Started", key="started", width=18)

        tasks = getattr(self, 'agent_tasks', [])
        if not tasks:
            table.add_row("[dim]No tasks yet[/dim]", "", "", "", "", "")
            table.add_row("[dim]Press A to add a task[/dim]", "", "", "", "", "")
            return

        for task in tasks:
            status_icon = StatusIcon.running()
            if task.status == "complete":
                status_icon = StatusIcon.active()
            elif task.status == "error":
                status_icon = StatusIcon.error()
            elif task.status in ("pending", "paused"):
                status_icon = StatusIcon.pending()

            progress_bar = ProgressBar.simple_bar(task.progress, 100, width=12)

            started_text = "-"
            if task.started:
                started_dt = datetime.fromtimestamp(task.started)
                started_text = Format.time_ago(started_dt)

            table.add_row(
                f"{Icons.CODE} {task.agent_name}",
                self._format_category(task.category or task.workstream),
                task.workstream,
                status_icon,
                progress_bar,
                started_text,
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
        """Show overview with high-energy ASCII dashboard."""
        table.add_column("Dashboard", key="dashboard")

        active_agents = sum(1 for a in getattr(self, 'agents', []) if a.status == "active")
        total_agents = len(getattr(self, 'agents', []))
        active_modes = sum(1 for m in getattr(self, 'modes', []) if m.status == "active")
        total_modes = len(getattr(self, 'modes', []))
        active_rules = sum(1 for r in getattr(self, 'rules', []) if r.status == "active")
        total_rules = len(getattr(self, 'rules', []))
        total_skills = len(getattr(self, 'skills', []))
        running_workflows = sum(1 for w in getattr(self, 'workflows', []) if w.status == "running")

        def add_multiline(content: str):
            for line in content.split('\n'):
                table.add_row(line)

        hero = EnhancedOverview.create_hero_banner(active_agents, total_agents)
        add_multiline(hero)
        table.add_row("")

        metrics_grid = EnhancedOverview.create_status_grid(
            active_agents,
            total_agents,
            active_modes,
            total_modes,
            active_rules,
            total_rules,
            total_skills,
            running_workflows,
        )
        add_multiline(metrics_grid)
        table.add_row("")

        timeline = EnhancedOverview.create_activity_timeline()
        add_multiline(timeline)
        table.add_row("")

        health = EnhancedOverview.create_system_health()
        add_multiline(health)

        if hasattr(self, 'performance_monitor'):
            table.add_row("")
            table.add_row("[bold cyan]⚡ Performance Monitor[/bold cyan]")
            table.add_row(self.performance_monitor.get_status_bar(compact=False))

    def _normalize_agent_dependency(self, value: str) -> Optional[str]:
        if not value:
            return None
        key = value.strip().lower()
        if key.endswith(".md"):
            key = key[:-3]
        lookup = getattr(self, 'agent_slug_lookup', {})
        return lookup.get(key)

    def _tasks_dir(self) -> Path:
        claude_dir = _resolve_claude_dir()
        tasks_dir = claude_dir / "tasks" / "current"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return self._validate_path(claude_dir, tasks_dir)

    def _tasks_file_path(self) -> Path:
        return self._tasks_dir() / "active_agents.json"

    def _get_agent_category(self, identifier: Optional[str]) -> Optional[str]:
        if not identifier:
            return None
        lookup = getattr(self, 'agent_category_lookup', {})
        return lookup.get(identifier.lower())

    def _format_category(self, category: Optional[str]) -> str:
        if not category:
            return "[dim]unknown[/dim]"

        key = category.lower()
        palette = getattr(self, '_dynamic_category_palette', {})
        if key not in palette:
            base_color = self.CATEGORY_PALETTE.get(key)
            if base_color is None:
                fallback_index = getattr(self, '_fallback_category_index', 0)
                if self.CATEGORY_FALLBACK_COLORS:
                    base_color = self.CATEGORY_FALLBACK_COLORS[fallback_index % len(self.CATEGORY_FALLBACK_COLORS)]
                    self._fallback_category_index = fallback_index + 1
                else:
                    base_color = "white"
            palette[key] = base_color
            self._dynamic_category_palette = palette

        color = palette.get(key, "white")
        return f"[{color}]{category}[/{color}]"

    def _category_badges(self) -> List[str]:
        lookup = getattr(self, 'agent_category_lookup', {})
        categories = sorted(set(lookup.values())) if lookup else []
        if not categories:
            return ["[dim]n/a[/dim]"]
        return [self._format_category(cat) for cat in categories[:6]]

    def _generate_task_id(self, name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip('-') or "task"
        timestamp = int(time.time())
        return f"{base}-{timestamp}"

    def _save_tasks(self, tasks: List[AgentTask]) -> None:
        tasks_file = self._tasks_file_path()
        payload = {}
        for task in tasks:
            payload[task.agent_id] = {
                "name": task.agent_name,
                "workstream": task.workstream,
                "status": task.status,
                "progress": task.progress,
                "category": task.category,
                "started": task.started,
                "completed": task.completed,
            }
        tasks_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _upsert_task(self, agent_id: Optional[str], payload: dict) -> None:
        tasks = list(getattr(self, 'agent_tasks', []))
        name = payload.get("name", "").strip()
        if not name:
            raise ValueError("Task name is required")
        workstream = payload.get("workstream", "primary").strip() or "primary"
        status = payload.get("status", "pending").strip().lower() or "pending"
        category = payload.get("category", "general").strip() or "general"
        try:
            progress = int(payload.get("progress", 0))
        except (TypeError, ValueError):
            progress = 0
        progress = max(0, min(progress, 100))

        def adjust_times(existing: AgentTask) -> None:
            if status == "running" and not existing.started:
                existing.started = time.time()
            if status == "complete":
                if not existing.started:
                    existing.started = time.time()
                existing.completed = time.time()
            else:
                if status in ("pending", "paused"):
                    existing.completed = None

        if agent_id:
            updated = False
            for task in tasks:
                if task.agent_id == agent_id:
                    task.agent_name = name
                    task.workstream = workstream
                    task.status = status
                    task.progress = progress
                    task.category = category
                    adjust_times(task)
                    updated = True
                    break
            if not updated:
                tasks.append(AgentTask(
                    agent_id=agent_id,
                    agent_name=name,
                    workstream=workstream,
                    status=status,
                    progress=progress,
                    category=category,
                    started=time.time() if status in ("running", "complete") else None,
                    completed=time.time() if status == "complete" else None,
                ))
        else:
            new_id = self._generate_task_id(name)
            tasks.append(AgentTask(
                agent_id=new_id,
                agent_name=name,
                workstream=workstream,
                status=status,
                progress=progress,
                category=category,
                started=time.time() if status in ("running", "complete") else None,
                completed=time.time() if status == "complete" else None,
            ))

        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()

    def _remove_task(self, agent_id: str) -> None:
        tasks = [t for t in getattr(self, 'agent_tasks', []) if t.agent_id != agent_id]
        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()

    def _selected_task_index(self) -> Optional[int]:
        if self.current_view != "tasks":
            return None
        tasks = getattr(self, 'agent_tasks', [])
        if not tasks:
            return None
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            return None
        return min(table.cursor_row, len(tasks) - 1)

    def _build_agent_nodes(self) -> List[WorkflowNode]:
        agents = getattr(self, 'agents', [])
        if not agents:
            return []

        nodes: List[WorkflowNode] = []
        for agent in agents:
            node_id = agent.slug or agent.name.replace(" ", "-")
            dependencies = []
            for dep in getattr(agent, 'requires', []) or []:
                normalized = self._normalize_agent_dependency(dep)
                if normalized:
                    dependencies.append(normalized)
            node = WorkflowNode(
                node_id=node_id,
                name=agent.name,
                status="complete" if agent.status == "active" else "pending",
                dependencies=dependencies,
            )
            node.progress = 100 if agent.status == "active" else 0
            nodes.append(node)
        return nodes

    def _render_agent_constellation_preview(self, max_lines: int = 18) -> str:
        nodes = self._build_agent_nodes()
        if not nodes:
            return "[dim]Constellation data unavailable (no agents loaded)[/dim]"

        viz = DependencyVisualizer(nodes)
        tree_lines = viz.render_tree()
        preview = tree_lines[:max_lines]
        if len(tree_lines) > max_lines:
            preview.append("[dim]…expand with 9 to view full galaxy[/dim]")
        header = "[bold cyan]Agent Constellation[/bold cyan]\n[dim]────────────────────────────[/dim]"
        return "\n".join([header, *preview])

    def show_galaxy_view(self) -> None:
        header = self.query_one("#galaxy-header", Static)
        stats_widget = self.query_one("#galaxy-stats", Static)
        graph_widget = self.query_one("#galaxy-graph", Static)

        header.update("[bold magenta]🌌 Agent Galaxy[/bold magenta]")
        nodes = self._build_agent_nodes()

        if not nodes:
            stats_widget.update("[dim]Load agents to visualize dependencies[/dim]")
            graph_widget.update("[dim]No nodes available[/dim]")
            return

        viz = DependencyVisualizer(nodes)
        tree_lines = viz.render_tree()
        max_lines = 220
        if len(tree_lines) > max_lines:
            tree_lines = tree_lines[:max_lines] + ["[dim]…truncated[/dim]"]
        graph_widget.update("\n".join(tree_lines))

        active_agents = sum(1 for a in getattr(self, 'agents', []) if a.status == "active")
        dependency_edges = sum(len(node.dependencies) for node in nodes)
        stats_lines = [
            f"[cyan]Active:[/cyan] {active_agents}/{len(nodes)}",
            f"[cyan]Dependencies:[/cyan] {dependency_edges}",
            "[dim]Tip: Space toggles status in Agents view[/dim]",
            "[cyan]Categories:[/cyan] " + ", ".join(self._category_badges()),
        ]

        cycles = viz.detect_cycles()
        if cycles:
            stats_lines.append("[red]Cycles detected[/red]")
            for cycle in cycles[:3]:
                stats_lines.append(f"  • {' → '.join(cycle)}")
            if len(cycles) > 3:
                stats_lines.append(f"  • …+{len(cycles) - 3} more")
        else:
            stats_lines.append("[green]No dependency cycles detected[/green]")

        stats_widget.update("\n".join(stats_lines))

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
        table.add_column("Category", key="category", width=16)
        table.add_column("Workstream", key="workstream")
        table.add_column("Status", key="status")
        table.add_column("Progress", key="progress")

        tasks = getattr(self, 'agent_tasks', [])

        if not tasks:
            # Show example/placeholder data with enhanced visuals
            placeholder_rows = [
                (f"{Icons.CODE} [Agent-1] Implementation", "development", "primary", StatusIcon.running(), 75),
                (f"{Icons.TEST} [Agent-2] Code Review", "quality", "quality", StatusIcon.active(), 100),
                (f"{Icons.TEST} [Agent-3] Test Automation", "testing", "quality", StatusIcon.running(), 60),
                (f"{Icons.DOC} [Agent-4] Documentation", "documentation", "quality", StatusIcon.pending(), 0),
            ]
            for name, category, workstream, status_icon, progress in placeholder_rows:
                table.add_row(
                    name,
                    self._format_category(category),
                    workstream,
                    status_icon,
                    ProgressBar.simple_bar(progress, 100, width=15),
                )

            # Add metrics section
            table.add_row("", "", "", "", "")
            table.add_row("METRICS:", "", "", "", "")
            table.add_row("Parallel Efficiency:", "", "87%", "", "")
            table.add_row("Overall Progress:", "", "78%", "", "")
            table.add_row("Active Agents:", "", "2/4", "", "")
            table.add_row("Estimated Completion:", "", "2m 30s", "", "")
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

                category_guess = (
                    self._get_agent_category(task.agent_id)
                    or self._get_agent_category(task.agent_name)
                    or task.workstream
                )

                table.add_row(
                    agent_display,
                    self._format_category(category_guess),
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
            table.add_row("", "", "", "", "")
            table.add_row("METRICS:", "", "", "", "")
            table.add_row("Parallel Efficiency:", "", f"{parallel_efficiency}%", "", "")
            table.add_row("Overall Progress:", "", f"{total_progress}%", "", "")
            table.add_row("Active Agents:", "", f"{running_count}/{len(tasks)}", "", "")
            table.add_row("Completed:", "", f"{complete_count}/{len(tasks)}", "", "")

            # Estimate completion time
            if running_count > 0 and total_progress > 0:
                estimated_minutes = int((100 - total_progress) * 0.5)
                table.add_row("Estimated Completion:", "", f"{estimated_minutes}m", "", "")
            else:
                table.add_row("Estimated Completion:", "", "TBD", "", "")

    def show_mcp_view(self, table: DataTable) -> None:
        """Show MCP server overview with validation status."""
        table.add_column("Server", width=24)
        table.add_column("Command", width=30)
        table.add_column("Docs", width=6)
        table.add_column("Status", width=18)
        table.add_column("Notes")

        if self.mcp_error:
            table.add_row("[red]Error[/red]", Format.truncate(self.mcp_error, 40), "", "", "")
            return

        servers = getattr(self, 'mcp_servers', [])
        if not servers:
            table.add_row("[dim]No MCP servers configured[/dim]", "", "", "", "")
            return

        for server in servers:
            args = " ".join(server.args) if server.args else ""
            command_text = Format.truncate(f"{server.command} {args}".strip(), 30)
            docs_text = "[green]✓[/green]" if server.docs_path else "[dim]-[/dim]"

            try:
                is_valid, errors, warnings = validate_server_config(server.name)
            except Exception as exc:
                is_valid = False
                errors = [str(exc)]
                warnings = []

            if is_valid:
                status_text = "[green]Valid[/green]"
            else:
                status_text = f"[red]{len(errors)} issue(s)[/red]"
            if warnings:
                status_text += f" [yellow]{len(warnings)} warn[/yellow]"

            note = server.description or ""
            if errors:
                note = errors[0]
            elif warnings:
                note = warnings[0]

            table.add_row(
                f"{Icons.CODE} {server.name}",
                command_text,
                docs_text,
                status_text,
                Format.truncate(note, 60),
            )

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

    def action_view_mcp(self) -> None:
        """Switch to MCP servers view."""
        self.current_view = "mcp"
        self.load_mcp_servers()
        self.status_message = "Switched to MCP"
        self.notify("🛰 MCP Servers", severity="information", timeout=1)

    def action_view_profiles(self) -> None:
        """Switch to profiles view."""
        self.current_view = "profiles"
        self.load_profiles()
        self.status_message = "Switched to Profiles"
        self.notify("👤 Profiles", severity="information", timeout=1)

    def action_view_export(self) -> None:
        """Switch to export view."""
        self.current_view = "export"
        self.status_message = "Configure context export"
        self.notify("📤 Export", severity="information", timeout=1)

    def action_view_ai_assistant(self) -> None:
        """Switch to AI assistant view."""
        self.current_view = "ai_assistant"
        self.status_message = "Switched to AI Assistant"
        self.notify("🤖 AI Assistant", severity="information", timeout=1)
        # Refresh recommendations when entering view
        if hasattr(self, 'intelligent_agent'):
            self.intelligent_agent.analyze_context()

    def action_view_galaxy(self) -> None:
        """Switch to the agent galaxy visualization."""
        self.current_view = "galaxy"
        self.status_message = "Switched to Galaxy"
        self.notify("🌌 Galaxy", severity="information", timeout=1)

    def action_view_tasks(self) -> None:
        """Switch to tasks view."""
        self.current_view = "tasks"
        self.status_message = "Switched to Tasks"
        self.notify("🗂 Tasks", severity="information", timeout=1)

    def action_profile_apply(self) -> None:
        """Apply the selected profile."""
        if self.current_view != "profiles":
            return

        profile = self._selected_profile()
        if not profile:
            self.notify("Select a profile", severity="warning", timeout=2)
            return

        name = profile.get("name", "profile")
        try:
            if profile.get("type") == "built-in":
                exit_code, message = init_profile(name)
            else:
                path_str = profile.get("path")
                if not path_str:
                    self.notify("Profile file missing", severity="error", timeout=2)
                    return
                exit_code, message = self._apply_saved_profile(Path(path_str))
        except Exception as exc:
            self.notify(f"Failed: {exc}", severity="error", timeout=3)
            return

        clean = self._clean_ansi(message)
        if exit_code == 0:
            self.status_message = clean.split("\n")[0] if clean else f"Applied {name}"
            self.notify(f"✓ Applied {name}", severity="success", timeout=2)
            self.load_agents()
            self.load_modes()
            self.load_rules()
            self.load_profiles()
            self.update_view()
        else:
            self.status_message = clean or f"Failed to apply {name}"
            self.notify(self.status_message, severity="error", timeout=3)

    async def action_profile_save_prompt(self) -> None:
        """Prompt for a profile name and save current state."""
        if self.current_view != "profiles":
            self.action_view_profiles()

        dialog = PromptDialog("Save Profile", "Enter profile name", placeholder="team-alpha")
        name = await self.push_screen(dialog, wait_for_dismiss=True)
        if not name:
            return

        exit_code, message = profile_save(name.strip())
        clean = self._clean_ansi(message)
        if exit_code == 0:
            self.notify(clean or f"Saved profile {name}", severity="success", timeout=2)
            self.load_profiles()
            self.update_view()
        else:
            self.notify(clean or "Failed to save profile", severity="error", timeout=3)

    async def action_profile_delete(self) -> None:
        """Delete the selected saved profile."""
        if self.current_view != "profiles":
            return

        profile = self._selected_profile()
        if not profile or profile.get("type") != "saved":
            self.notify("Select a saved profile to delete", severity="warning", timeout=2)
            return

        confirm = await self.push_screen(
            ConfirmDialog("Delete Profile", f"Remove {profile.get('name', '')}?"),
            wait_for_dismiss=True,
        )
        if not confirm:
            return

        try:
            path_str = profile.get("path")
            if path_str:
                Path(path_str).unlink(missing_ok=True)
        except Exception as exc:
            self.notify(f"Failed to delete: {exc}", severity="error", timeout=3)
            return

        self.load_profiles()
        self.update_view()
        self.notify("Deleted profile", severity="information", timeout=2)

    async def action_skill_info(self) -> None:
        slug = await self._get_skill_slug("Skill Info")
        if not slug:
            return
        await self._handle_skill_result(
            skill_info,
            args=[slug],
            title=f"Skill Info · {slug}",
            success=f"Loaded info for {slug}",
        )

    async def action_skill_versions(self) -> None:
        slug = await self._get_skill_slug("Skill Versions")
        if not slug:
            return
        await self._handle_skill_result(
            skill_versions,
            args=[slug],
            title=f"Skill Versions · {slug}",
        )

    async def action_skill_deps(self) -> None:
        slug = await self._get_skill_slug("Skill Dependencies")
        if not slug:
            return
        await self._handle_skill_result(
            skill_deps,
            args=[slug],
            title=f"Skill Dependencies · {slug}",
        )

    async def action_skill_agents(self) -> None:
        slug = await self._get_skill_slug("Skill Agents")
        if not slug:
            return
        await self._handle_skill_result(
            skill_agents,
            args=[slug],
            title=f"Skill Agents · {slug}",
        )

    async def action_skill_compose(self) -> None:
        slug = await self._get_skill_slug("Skill Compose")
        if not slug:
            return
        await self._handle_skill_result(
            skill_compose,
            args=[slug],
            title=f"Skill Compose · {slug}",
        )

    async def action_skill_analyze(self) -> None:
        text = await self._prompt_text("Analyze Text", "Describe the work to analyze:")
        if not text:
            return
        await self._handle_skill_result(
            skill_analyze,
            args=[text],
            title="Skill Analyze",
        )

    async def action_skill_suggest(self) -> None:
        path = await self._prompt_text("Suggest Skills", "Project directory", default=".")
        if path is None:
            return
        await self._handle_skill_result(
            skill_suggest,
            args=[path],
            title=f"Skill Suggest · {path}",
        )

    async def action_skill_analytics(self) -> None:
        metric = await self._prompt_text(
            "Skill Analytics",
            "Metric (tokens/activations/success_rate/trending/roi/effectiveness, leave blank for dashboard)",
        )
        args = [metric] if metric else []
        await self._handle_skill_result(
            skill_analytics,
            args=args,
            title="Skill Analytics",
        )

    async def action_skill_report(self) -> None:
        fmt = await self._prompt_text("Skill Report", "Format (text/json/csv)", default="text")
        if fmt is None:
            return
        await self._handle_skill_result(
            skill_report,
            args=[fmt],
            title=f"Skill Report ({fmt})",
        )

    async def action_skill_trending(self) -> None:
        days_input = await self._prompt_text("Skill Trending", "Days to include", default="30")
        if days_input is None:
            return
        try:
            days = int(days_input)
        except ValueError:
            self.notify("Days must be a number", severity="error", timeout=2)
            return
        await self._handle_skill_result(
            skill_trending,
            args=[days],
            title=f"Trending Skills ({days}d)",
        )

    async def action_skill_metrics_reset(self) -> None:
        confirm = await self.push_screen(
            ConfirmDialog("Reset Skill Metrics", "Clear all recorded skill metrics?"),
            wait_for_dismiss=True,
        )
        if not confirm:
            return
        await self._handle_skill_result(
            skill_metrics_reset,
            title="Reset Skill Metrics",
            success="Skill metrics reset",
            error="Failed to reset metrics",
        )

    async def action_skill_community_install(self) -> None:
        name = await self._prompt_text("Community Install", "Skill name")
        if not name:
            return
        await self._handle_skill_result(
            skill_community_install,
            args=[name],
            title=f"Community Install · {name}",
            success=f"Installed {name}",
            error=f"Failed to install {name}",
        )

    async def action_skill_community_validate(self) -> None:
        name = await self._prompt_text("Community Validate", "Skill name")
        if not name:
            return
        await self._handle_skill_result(
            skill_community_validate,
            args=[name],
            title=f"Community Validate · {name}",
        )

    async def action_skill_community_rate(self) -> None:
        name = await self._prompt_text("Community Rate", "Skill name")
        if not name:
            return
        rating_input = await self._prompt_text("Community Rate", "Rating 1-5", default="5")
        if rating_input is None:
            return
        try:
            rating = int(rating_input)
        except ValueError:
            self.notify("Rating must be 1-5", severity="error", timeout=2)
            return
        await self._handle_skill_result(
            skill_community_rate,
            args=[name, rating],
            title=f"Community Rate · {name}",
            success=f"Rated {name} ({rating})",
        )

    async def action_skill_community_search(self) -> None:
        query = await self._prompt_text("Community Search", "Search query")
        if not query:
            return
        await self._handle_skill_result(
            skill_community_search,
            args=[query],
            title=f"Community Search · {query}",
        )

    async def action_skill_validate(self) -> None:
        """Validate the selected skill."""
        if self.current_view != "skills":
            self.action_view_skills()

        skill = self._selected_skill()
        if not skill:
            self.notify("Select a skill to validate", severity="warning", timeout=2)
            return

        slug = self._skill_slug(skill)
        try:
            exit_code, message = skill_validate(slug)
        except Exception as exc:
            self.notify(f"Validation failed: {exc}", severity="error", timeout=3)
            return

        clean = self._clean_ansi(message)
        if clean:
            await self._show_text_dialog(f"Skill Validation · {slug}", clean)

        if exit_code == 0:
            self.notify(f"✓ {slug} validated", severity="success", timeout=2)
        else:
            self.notify(f"Validation issues for {slug}", severity="error", timeout=3)

    async def action_skill_metrics(self) -> None:
        """Show metrics for the selected skill."""
        if self.current_view != "skills":
            self.action_view_skills()

        skill = self._selected_skill()
        if not skill:
            self.notify("Select a skill to view metrics", severity="warning", timeout=2)
            return

        slug = self._skill_slug(skill)
        try:
            exit_code, message = skill_metrics(slug)
        except Exception as exc:
            self.notify(f"Metrics error: {exc}", severity="error", timeout=3)
            return

        clean = self._clean_ansi(message)
        if clean:
            await self._show_text_dialog(f"Skill Metrics · {slug}", clean)

        if exit_code == 0:
            self.notify(f"Metrics loaded for {slug}", severity="information", timeout=2)
        else:
            self.notify(f"Metrics unavailable for {slug}", severity="warning", timeout=2)

    async def action_skill_community(self) -> None:
        """Show community skill listings."""
        try:
            exit_code, message = skill_community_list()
        except Exception as exc:
            self.notify(f"Community error: {exc}", severity="error", timeout=3)
            return

        clean = self._clean_ansi(message)
        if clean:
            await self._show_text_dialog("Community Skills", clean)

        if exit_code != 0:
            self.notify("No community skills found", severity="warning", timeout=2)

    async def action_validate_context(self) -> None:
        """Context-aware validate shortcut."""
        if self.current_view == "skills":
            await self.action_skill_validate()
        elif self.current_view == "mcp":
            self.action_mcp_validate()
        else:
            self.notify("Nothing to validate here", severity="warning", timeout=2)

    async def action_metrics_context(self) -> None:
        """Context-aware metrics shortcut."""
        if self.current_view == "skills":
            await self.action_skill_metrics()
        else:
            self.notify("Metrics not available in this view", severity="warning", timeout=2)

    async def action_context_action(self) -> None:
        """Context-aware action for the 'c' binding."""
        if self.current_view == "skills":
            await self.action_skill_community()
        elif self.current_view == "mcp":
            await self.action_mcp_snippet()
        else:
            self.notify("No contextual action", severity="warning", timeout=2)

    async def action_docs_context(self) -> None:
        """Context-aware docs shortcut."""
        if self.current_view == "mcp":
            await self.action_mcp_docs()
        else:
            self.notify("Docs not available in this view", severity="warning", timeout=2)

    async def action_details_context(self) -> None:
        """Context-aware details shortcut."""
        if self.current_view == "mcp":
            await self.action_mcp_details()
        else:
            self.notify("Details not available", severity="warning", timeout=2)

    def action_export_cycle_format(self) -> None:
        """Toggle between agent-generic and Claude-specific export formats."""
        if self.current_view != "export":
            self.action_view_export()
        self.export_agent_generic = not self.export_agent_generic
        mode = "Agent generic" if self.export_agent_generic else "Claude format"
        self.status_message = f"Format: {mode}"
        self.update_view()

    async def action_export_run(self) -> None:
        """Prompt for an export path and generate the context file."""
        if self.current_view != "export":
            self.action_view_export()

        default_path = str(self._default_export_path())
        dialog = PromptDialog("Export Context", "Write export to path", default=default_path)
        target = await self.push_screen(dialog, wait_for_dismiss=True)
        if not target:
            return

        output_path = Path(os.path.expanduser(target.strip()))
        exclude = self._export_exclude_categories()

        exit_code, message = export_context(
            output_path=output_path,
            exclude_categories=exclude,
            agent_generic=self.export_agent_generic,
        )
        clean = self._clean_ansi(message)
        if exit_code == 0:
            self.status_message = clean or f"Exported to {output_path}"
            self.notify(self.status_message, severity="success", timeout=2)
        else:
            self.status_message = clean or "Export failed"
            self.notify(self.status_message, severity="error", timeout=3)

    async def action_export_clipboard(self) -> None:
        """Generate export and copy it to the clipboard."""
        if self.current_view != "export":
            self.action_view_export()

        exclude = self._export_exclude_categories()
        tmp_path = Path(tempfile.gettempdir()) / "claude-ctx-export.md"
        exit_code, message = export_context(
            output_path=tmp_path,
            exclude_categories=exclude,
            agent_generic=self.export_agent_generic,
        )
        clean = self._clean_ansi(message)
        if exit_code != 0:
            self.notify(clean or "Export failed", severity="error", timeout=3)
            return

        try:
            content = tmp_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(f"Failed to read export: {exc}", severity="error", timeout=3)
            tmp_path.unlink(missing_ok=True)
            return

        tmp_path.unlink(missing_ok=True)

        if self._copy_to_clipboard(content):
            self.notify("Copied export to clipboard", severity="success", timeout=2)
        else:
            self.notify("Clipboard unavailable", severity="warning", timeout=3)

    def action_mcp_validate(self) -> None:
        """Validate the selected MCP server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return

        valid, errors, warnings = validate_server_config(server.name)
        if valid:
            note = "All checks passed"
            if warnings:
                note = warnings[0]
            self.notify(f"{server.name}: {note}", severity="success", timeout=2)
        else:
            self.notify(errors[0] if errors else "Validation failed", severity="error", timeout=3)

    async def action_mcp_details(self) -> None:
        """Show detailed information for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return

        exit_code, output = mcp_show(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return

        await self.push_screen(TextViewerDialog(f"MCP: {server.name}", output), wait_for_dismiss=True)

    async def action_mcp_docs(self) -> None:
        """Open MCP documentation for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return

        exit_code, output = mcp_docs(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return

        await self.push_screen(TextViewerDialog(f"Docs: {server.name}", output), wait_for_dismiss=True)

    async def action_mcp_snippet(self) -> None:
        """Generate config snippet for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return

        snippet = generate_config_snippet(server.name, server.command, args=server.args, env=server.env)
        await self.push_screen(TextViewerDialog(f"Snippet: {server.name}", snippet), wait_for_dismiss=True)
        if self._copy_to_clipboard(snippet):
            self.notify("Snippet copied", severity="success", timeout=2)
        else:
            self.notify("Snippet ready", severity="information", timeout=2)

    async def action_mcp_test_selected(self) -> None:
        """Run MCP test for selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return

        exit_code, output = mcp_test(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return
        await self.push_screen(TextViewerDialog(f"Test: {server.name}", output), wait_for_dismiss=True)

    async def action_mcp_diagnose(self) -> None:
        """Run diagnostics across all MCP servers."""
        exit_code, output = mcp_diagnose()
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return
        await self.push_screen(TextViewerDialog("MCP Diagnose", output), wait_for_dismiss=True)

    def action_auto_activate(self) -> None:
        """Auto-activate agents or add task when in Tasks view."""
        if self.current_view == "tasks":
            dialog = TaskEditorDialog("Add Task")
            self.push_screen(dialog, callback=self._handle_add_task)
            return

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

    def _handle_add_task(self, result: Optional[dict]) -> None:
        if not result:
            return
        try:
            self._upsert_task(None, result)
            self.current_view = "tasks"
            self.status_message = f"Created task {result.get('name', '')}"
            self.notify("✓ Task added", severity="success", timeout=2)
        except Exception as exc:
            self.notify(f"Failed to add task: {exc}", severity="error", timeout=3)

    def action_edit_task(self) -> None:
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task in Tasks view", severity="warning", timeout=2)
            return
        task = self.agent_tasks[index]
        dialog = TaskEditorDialog(
            "Edit Task",
            defaults={
                "name": task.agent_name,
                "workstream": task.workstream,
                "category": task.category,
                "status": task.status,
                "progress": task.progress,
            }
        )
        self.push_screen(
            dialog,
            callback=lambda result, agent_id=task.agent_id, label=task.agent_name: self._handle_edit_task(agent_id, label, result),
        )

    def _handle_edit_task(self, agent_id: str, label: str, result: Optional[dict]) -> None:
        if not result:
            return
        try:
            self._upsert_task(agent_id, result)
            self.status_message = f"Updated task {label}"
            self.notify("✓ Task updated", severity="success", timeout=2)
        except Exception as exc:
            self.notify(f"Failed to update task: {exc}", severity="error", timeout=3)

    def action_delete_task(self) -> None:
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task in Tasks view", severity="warning", timeout=2)
            return
        task = self.agent_tasks[index]
        dialog = ConfirmDialog("Delete Task", f"Remove {task.agent_name}?")
        self.push_screen(
            dialog,
            callback=lambda confirm, agent_id=task.agent_id, label=task.agent_name: self._handle_delete_task(agent_id, label, confirm),
        )

    def _handle_delete_task(self, agent_id: str, label: str, confirm: bool) -> None:
        if not confirm:
            return
        self._remove_task(agent_id)
        self.status_message = f"Deleted task {label}"
        self.notify("✓ Task deleted", severity="information", timeout=2)

    def action_toggle(self) -> None:
        """Toggle selected item."""
        if self.current_view == "profiles":
            self.action_profile_apply()
            return

        if self.current_view == "export":
            meta = self._selected_export_meta()
            if not meta:
                self.notify("Select an export option", severity="warning", timeout=2)
                return
            kind, key = meta
            if kind == "category" and key:
                self.export_options[key] = not self.export_options.get(key, True)
                state = "included" if self.export_options[key] else "excluded"
                self.status_message = f"{key} {state}"
                self.update_view()
            elif kind == "format":
                self.export_agent_generic = not self.export_agent_generic
                self.status_message = "Agent generic" if self.export_agent_generic else "Claude format"
                self.update_view()
            else:
                self.notify("Preview is read-only", severity="information", timeout=2)
            return

        if self.current_view == "agents":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                # Save current cursor position
                saved_cursor_row = table.cursor_row

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

                                # Restore cursor to same position (showing next agent)
                                table = self.query_one(DataTable)
                                if table.row_count > 0:
                                    # Keep at same index, or last row if we were at the end
                                    new_cursor_row = min(saved_cursor_row, table.row_count - 1)
                                    table.move_cursor(row=new_cursor_row)
                            else:
                                self.notify(f"✗ Failed to toggle {agent.name}", severity="error", timeout=3)
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(f"✗ Error: {str(e)[:50]}", severity="error", timeout=3)

        elif self.current_view == "rules":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                # Save current cursor position
                saved_cursor_row = table.cursor_row

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

                            # Restore cursor to same position (showing next rule)
                            table = self.query_one(DataTable)
                            if table.row_count > 0:
                                new_cursor_row = min(saved_cursor_row, table.row_count - 1)
                                table.move_cursor(row=new_cursor_row)
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(f"✗ Error: {str(e)[:50]}", severity="error", timeout=3)

        elif self.current_view == "modes":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                # Save current cursor position
                saved_cursor_row = table.cursor_row

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

                                # Restore cursor to same position (showing next mode)
                                table = self.query_one(DataTable)
                                if table.row_count > 0:
                                    new_cursor_row = min(saved_cursor_row, table.row_count - 1)
                                    table.move_cursor(row=new_cursor_row)
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
        elif self.current_view == "mcp":
            self.load_mcp_servers()
        elif self.current_view == "profiles":
            self.load_profiles()

        self.update_view()
        self.status_message = f"Refreshed {self.current_view}"
        self.notify(f"🔄 Refreshed {self.current_view}", severity="information", timeout=1)

    def action_help(self) -> None:
        """Show help."""
        self.status_message = (
            "Help: 1-6=Core views, 7=MCP, 8=Profiles, 9=Export, 0=AI, G=Galaxy, T=Tasks, Ctrl+P=Commands"
        )

    async def action_command_palette(self) -> None:
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
            elif result == "show_mcp":
                self.action_view_mcp()
            elif result == "show_profiles":
                self.action_view_profiles()
            elif result == "show_export":
                self.action_view_export()
            elif result == "show_tasks":
                self.action_view_tasks()
            elif result == "show_galaxy":
                self.action_view_galaxy()
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
            elif result == "add_task":
                await self.action_add_task()
            elif result == "edit_task":
                await self.action_edit_task()
            elif result == "delete_task":
                await self.action_delete_task()
            elif result == "export_context":
                self.current_view = "export"
                self.update_view()
            elif result == "show_help":
                self.action_help()
            elif result == "refresh":
                self.action_refresh()
            elif result == "auto_activate":
                await self.action_auto_activate()
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
