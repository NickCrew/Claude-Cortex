"""Textual-based Terminal User Interface for cortex."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
import yaml
import re
import sys
import asyncio
import shlex
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePath
from typing import Any, Callable, ClassVar, Dict, List, Optional, Sequence, Set, Tuple, TypedDict

from textual.app import App, ComposeResult, SuspendNotSupported
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual import events
from textual.widgets import ContentSwitcher, DataTable, Header, Input, Static

from .widgets import AdaptiveFooter
from ..tui_extensions import ProfileViewMixin, ExportViewMixin, WizardViewMixin

AnyDataTable = DataTable[Any]
from textual.reactive import reactive

ASSET_CATEGORY_ORDER = [
    "hooks",
    "commands",
    "agents",
    "skills",
    "modes",
    "prompts",
    "workflows",
    "flags",
    "rules",
    "profiles",
    "scenarios",
    "tasks",
    "settings",
]

from .types import (
    RuleNode, AgentTask, WorkflowInfo, ModeInfo, MCPDocInfo, ScenarioInfo, ScenarioRuntimeState,
    AssetInfo, MemoryNote, WatchModeState, PrincipleSnippet, PromptInfo,
)
from .constants import (
    PROFILE_DESCRIPTIONS, EXPORT_CATEGORIES, DEFAULT_EXPORT_OPTIONS,
    PRIMARY_VIEW_BINDINGS, VIEW_TITLES
)

from ..core import (
    build_agent_graph,
    agent_activate,
    agent_deactivate,
    AgentGraphNode,
    _resolve_claude_dir,
    _resolve_cortex_root,
    _iter_all_files,
    _is_disabled,
    _extract_agent_name,
    _read_agent_front_matter_lines,
    _parse_dependencies_from_front,
    _tokenize_front_matter,
    _extract_scalar_from_paths,
    _extract_front_matter,
    _ensure_scenarios_dir,
    _scenario_lock_basename,
    _parse_scenario_metadata,
    collect_context_components,
    export_context,
    init_profile,
    init_wizard,
    init_minimal,
    profile_save,
    _profile_reset,
    scenario_preview,
    scenario_run,
    scenario_validate,
    scenario_status,
    scenario_stop,
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
    skill_rate,
    skill_community_list,
    skill_community_install,
    skill_community_validate,
    skill_community_rate,
    skill_community_search,
    skill_recommend,
    workflow_stop,
    WorktreeInfo,
    worktree_discover,
    worktree_default_path,
    worktree_get_base_dir,
    worktree_set_base_dir,
    worktree_clear_base_dir,
    worktree_add,
    worktree_remove,
    worktree_prune,
    _parse_claude_md_refs,
    _inactive_dir_candidates,
    _inactive_category_dir,
    _write_active_entries,
)
from ..core.rules import rules_activate, rules_deactivate
from ..core.principles import (
    principles_activate,
    principles_deactivate,
    principles_build,
)
from ..core.modes import (
    mode_activate,
    mode_deactivate,
    mode_activate_intelligent,
    mode_deactivate_intelligent,
)
from ..core.base import (
    _iter_md_files,
    _parse_active_entries,
    _strip_ansi_codes,
    _ensure_claude_structure,
    _find_missing_template_files,
    _ensure_template_files,
)
from ..core.migration import migrate_to_file_activation
from ..core.doctor import doctor_run
from ..core.mcp import (
    discover_servers,
    validate_server_config,
    generate_config_snippet,
    mcp_show,
    mcp_docs,
    mcp_test,
    mcp_diagnose,
    add_mcp_server,
    remove_mcp_server,
    update_mcp_server,
    MCPServerInfo,
    list_doc_only_servers,
    # MCP docs activation
    mcp_activate,
    mcp_deactivate,
)
from ..core.agents import BUILT_IN_PROFILES
from ..core.asset_discovery import (
    Asset, ClaudeDir, AssetCategory, InstallStatus,
    discover_plugin_assets, find_claude_directories, check_installation_status,
)
from ..core.asset_installer import install_asset, uninstall_asset, get_asset_diff
from ..core.hooks import detect_settings_files, get_settings_path, get_settings_scope
from .dialogs import (
    TargetSelectorDialog,
    AssetDetailDialog,
    DiffViewerDialog,
    BulkInstallDialog,
    MCPBrowseDialog,
    MCPInstallDialog,
    ClaudeMdWizard,
    WizardConfig,
    generate_claude_md,
    ProfileEditorDialog,
    ProfileConfig,
    HooksManagerDialog,
    BackupManagerDialog,
    LLMProviderSettingsDialog,
)
from ..core.mcp_installer import install_and_configure
from ..core.mcp_registry import get_server
from ..core import _resolve_claude_dir
from ..tui_icons import Icons, StatusIcon
from ..tui_format import Format
from ..tui_progress import ProgressBar
from ..tui_command_palette import CommandPalette, CommandRegistry, DEFAULT_COMMANDS
from ..tui_commands import AgentCommandProvider
from ..tui_dashboard import MetricsCollector
from ..tui_performance import PerformanceMonitor
from ..tui_workflow_viz import WorkflowNode, DependencyVisualizer
from ..tui_overview_enhanced import EnhancedOverview
from ..token_counter import get_active_context_tokens, count_category_tokens, count_file_tokens, TokenStats
from ..intelligence import (
    AgentRecommendation,
    IntelligentAgent,
    SessionContext,
    WorkflowPrediction,
)
from ..tui_supersaiyan import SuperSaiyanStatusBar
from ..tui_dialogs import (
    MCPServerData,
    MCPServerDialog,
    TaskEditorData,
    TaskEditorDialog,
    ConfirmDialog,
    HelpDialog,
    PromptDialog,
    TextViewerDialog,
)
from ..tui_log_viewer import LogViewerScreen
from ..skill_rating import SkillRatingCollector, SkillQualityMetrics
from ..skill_rating_prompts import SkillRatingPromptManager
from ..slash_commands import SlashCommandInfo, scan_slash_commands
from ..watch import WatchMode
import threading





class AgentTUI(App[None], ProfileViewMixin, ExportViewMixin, WizardViewMixin):
    """Textual TUI for cortex management."""

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

    def __init__(
        self,
        *,
        theme_path: Optional[Path] = None,
        **kwargs: Any,
    ) -> None:
        resolved_theme = self._resolve_theme_path(theme_path)
        css_path: list[str | PurePath] | None = None
        if resolved_theme is not None:
            css_path = []
            base_css = self.CSS_PATH
            if base_css:
                if isinstance(base_css, list):
                    css_path.extend(base_css)
                elif isinstance(base_css, (str, PurePath)):
                    css_path.append(base_css)
            css_path.append(resolved_theme)

        super().__init__(css_path=css_path, **kwargs)
        self.theme_path = resolved_theme
        self.claude_home: Path = _resolve_claude_dir()
        self.agents: List[AgentGraphNode] = []
        self.rules: List[RuleNode] = []
        self.modes: List[ModeInfo] = []
        self.principles: List[PrincipleSnippet] = []
        self.workflows: List[WorkflowInfo] = []
        self.worktrees: List[WorktreeInfo] = []
        self.worktree_repo_root: Optional[Path] = None
        self.worktree_error: Optional[str] = None
        self.worktree_base_dir: Optional[Path] = None
        self.worktree_base_source: Optional[str] = None
        self.profiles: List[Dict[str, Optional[str]]] = []
        self.mcp_servers: List[MCPServerInfo] = []
        self.mcp_docs: List[MCPDocInfo] = []
        self.prompts: List[PromptInfo] = []
        self.mcp_error: Optional[str] = None
        self.export_options: Dict[str, bool] = DEFAULT_EXPORT_OPTIONS.copy()
        self.export_agent_generic: bool = True
        self.export_row_meta: List[Tuple[str, Optional[str]]] = []
        self.scenarios: List[ScenarioInfo] = []
        self.skills: List[Dict[str, Any]] = []
        self.slash_commands: List[SlashCommandInfo] = []
        self.skill_rating_collector: Optional[SkillRatingCollector] = None
        self.skill_rating_error: Optional[str] = None
        self.skill_prompt_manager: Optional[SkillRatingPromptManager] = None
        self._tasks_state_signature: Optional[str] = None
        # Asset manager state
        self.available_assets: Dict[str, List[Asset]] = {}
        self.claude_directories: List[ClaudeDir] = []
        self.selected_target_dir: Optional[Path] = None
        # Memory vault state
        self.memory_notes: List[MemoryNote] = []
        # Watch mode state
        self.watch_mode_instance: Optional[WatchMode] = None
        self.watch_mode_thread: Optional[threading.Thread] = None
        # Flags explorer state
        self.current_flag_category = "all"  # Track selected flag category
        self.flag_categories = ["all"]
        # Track which categories are enabled (all enabled by default, except "all" which is special)
        self.flag_categories_enabled: Dict[str, bool] = {}
        # Flag manager state
        self.flag_files: List[Dict[str, Any]] = []
        self.selected_flag_index = 0
        self.selected_index = 0
        self.state = self
        self.wizard_active = False
        self.wizard_step = 0
        # Vi-style navigation state
        self._vi_g_pending = False
        self._vi_g_deadline = 0.0

    @staticmethod
    def _resolve_theme_path(theme_path: Optional[Path]) -> Optional[Path]:
        if theme_path is not None:
            return theme_path

        env_path = os.environ.get("CORTEX_TUI_THEME") or os.environ.get(
            "CLAUDE_TUI_THEME"
        )
        if env_path:
            candidate = Path(env_path).expanduser()
            if candidate.is_file():
                return candidate
            return None

        claude_dir = _resolve_claude_dir()
        candidates = [
            claude_dir / "tui" / "theme.tcss",
            claude_dir / "tui-theme.tcss",
        ]
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    CSS_PATH: ClassVar[str | PurePath | list[str | PurePath] | None] = "styles.tcss"
    # Bindings registered for key handling; display handled by AdaptiveFooter
    BINDINGS = [
        *[
            Binding(key, f"view_{name}", label, show=False)
            for key, name, label in PRIMARY_VIEW_BINDINGS
        ],
        Binding("S", "view_scenarios", "Scenarios", show=False),
        Binding("o", "view_orchestrate", "Orchestrate", show=False),
        Binding("alt+g", "view_galaxy", "Galaxy", show=False),
        Binding("ctrl+g", "view_flag_manager", "Flag Mgr", show=False),
        Binding("t", "view_tasks", "Tasks", show=False),
        Binding("/", "view_commands", "Slash Cmds", show=False),
        Binding("ctrl+p", "command_palette", "Commands", show=False),
        Binding("q", "quit", "Quit", show=False),
        Binding("?", "help", "Help", show=False),
        Binding("space", "toggle", "Toggle", show=False),
        Binding("r", "refresh", "Refresh", show=False),
        Binding("ctrl+r", "skill_rate_selected", "Rate Skill", show=False),
        Binding("a", "auto_activate", "Auto-Activate", show=False),
        Binding("J", "consult_gemini", "Consult Gemini", show=False),
        Binding("K", "assign_llm_tasks", "Assign LLM Tasks", show=False),
        Binding("Y", "request_reviews", "Request Reviews", show=False),
        Binding("s", "details_context", "Details", show=False),
        Binding("v", "validate_context", "Validate", show=False),
        Binding("m", "metrics_context", "Metrics", show=False),
        Binding("c", "context_action", "Actions", show=False),
        Binding("d", "docs_context", "Docs", show=False),
        Binding("ctrl+e", "edit_item", "Edit", show=False),
        Binding("ctrl+t", "mcp_test_selected", "Test", show=False),
        Binding("ctrl+a", "mcp_add", "Add MCP", show=False),
        Binding("B", "context_browse_or_base", "Browse/Base", show=False),
        Binding("E", "mcp_edit", "Edit MCP", show=False),
        Binding("X", "mcp_remove", "Remove MCP", show=False),
        Binding("f", "export_cycle_format", "Format", show=False),
        Binding("e", "export_run", "Export", show=False),
        Binding("x", "export_clipboard", "Copy", show=False),
        # Worktree bindings
        Binding("ctrl+n", "worktree_add", "New Worktree", show=False),
        Binding("ctrl+o", "worktree_open", "Open Worktree", show=False),
        Binding("ctrl+w", "worktree_remove", "Remove Worktree", show=False),
        Binding("ctrl+k", "worktree_prune", "Prune Worktrees", show=False),
        Binding("y", "copy_definition", "Copy Definition", show=False),
        Binding("n", "profile_save_prompt", "Save Profile", show=False),
        Binding("D", "context_delete", "Delete/Diagnose", show=False),
        Binding("P", "scenario_preview", "Preview", show=False),
        Binding("R", "run_selected", "Run", show=False),
        Binding("s", "stop_selected", "Stop", show=False),
        Binding("V", "scenario_validate_selected", "Validate Scenario", show=False),
        Binding("H", "scenario_status_history", "Scenario Status", show=False),
        Binding("L", "task_open_source", "Open Log", show=False),
        Binding("O", "task_open_external", "Open File", show=False),
        # Asset Manager bindings
        Binding("i", "asset_install", "Install", show=False),
        Binding("u", "asset_uninstall", "Uninstall", show=False),
        Binding("T", "asset_change_target", "Target", show=False),
        Binding("I", "asset_bulk_install", "Bulk Install", show=False),
        Binding("U", "asset_update_all", "Update All", show=False),
        Binding("enter", "asset_details", "Details", show=False),
        # Memory Vault bindings
        Binding("enter", "memory_view_note", "View", show=False),
        Binding("N", "memory_new_note", "New Note", show=False),
        Binding("O", "memory_open_note", "Open", show=False),
        # Agent bindings
        Binding("enter", "agent_view", "View Agent", show=False),
        # Profile bindings
        Binding("enter", "profile_edit", "View/Edit Profile", show=False),
        # Setup Tools bindings (profiles view)
        Binding("I", "setup_init_wizard", "Init Wizard", show=False),
        Binding("m", "setup_init_minimal", "Init Minimal", show=False),
        Binding("M", "setup_migration", "Migration", show=False),
        Binding("c", "setup_health_check", "Health Check", show=False),
        # CLAUDE.md Wizard
        Binding("W", "claude_md_wizard", "Configure CLAUDE.md", show=False),
        # Hooks Manager
        Binding("h", "hooks_manager", "Manage Hooks", show=False),
        # Backup Manager
        Binding("b", "backup_manager", "Backup Manager", show=False),
        # Vi-style navigation
        Binding("j", "cursor_down", "Cursor Down", show=False),
        Binding("k", "cursor_up", "Cursor Up", show=False),
        Binding("G", "cursor_bottom", "Bottom", show=False),
        Binding("ctrl+b", "page_up", "Page Up", show=False),
        Binding("ctrl+f", "page_down", "Page Down", show=False),
        Binding("ctrl+u", "half_page_up", "Half Page Up", show=False),
        Binding("ctrl+d", "half_page_down", "Half Page Down", show=False),
        # Watch Mode bindings
        Binding("d", "watch_change_directory", "Change Dir", show=False),
        Binding("t", "watch_adjust_threshold", "Adjust Threshold", show=False),
        Binding("i", "watch_adjust_interval", "Adjust Interval", show=False),
    ]

    # Register command provider for Textual's command palette
    # Textual looks for COMMANDS, not COMMAND_PROVIDERS!
    COMMANDS = {AgentCommandProvider}

    current_view: reactive[str] = reactive("agents")
    status_message: reactive[str] = reactive("Welcome to cortex TUI")

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
        yield AdaptiveFooter(id="adaptive-footer")

    def _selected_agent(self) -> Optional[AgentGraphNode]:
        index = self._table_cursor_index()
        agents = self.agents
        if index is None or not agents:
            return None
        if index < 0 or index >= len(agents):
            return None
        return agents[index]

    def action_edit_item(self) -> None:
        """Open the selected item's source file in the default editor."""
        file_path: Optional[Path] = None
        item_name: Optional[str] = None

        if self.current_view == "agents":
            agent = self._selected_agent()
            if agent:
                file_path = agent.path
                item_name = agent.name
        elif self.current_view == "rules":
            # Assuming a _selected_rule() helper or direct access
            index = self._table_cursor_index()
            if index is not None and 0 <= index < len(self.rules):
                rule = self.rules[index]
                file_path = rule.path
                item_name = rule.name
        elif self.current_view == "modes":
            # Assuming a _selected_mode() helper or direct access
            index = self._table_cursor_index()
            if index is not None and 0 <= index < len(self.modes):
                mode = self.modes[index]
                file_path = mode.path
                item_name = mode.name
        elif self.current_view == "prompts":
            index = self._table_cursor_index()
            if index is not None and 0 <= index < len(self.prompts):
                prompt = self.prompts[index]
                file_path = prompt.path
                item_name = prompt.name
        elif self.current_view == "principles":
            index = self._table_cursor_index()
            if index is not None and 0 <= index < len(self.principles):
                snippet = self.principles[index]
                file_path = snippet.path
                item_name = snippet.name
        elif self.current_view == "skills":
            skill = self._selected_skill()
            if skill and "path" in skill:
                file_path = Path(skill["path"])
                item_name = skill["name"]
        elif self.current_view == "commands":
            command = self._selected_command()
            if command:
                file_path = command.path
                item_name = command.command

        if file_path and item_name:
            try:
                # Use a cross-platform way to open the file
                if sys.platform == "darwin":
                    subprocess.Popen(["open", str(file_path)])
                elif sys.platform == "win32":
                    os.startfile(str(file_path))
                else:  # linux and other UNIX
                    editor = os.environ.get("EDITOR", "vi")
                    # This runs in the background and doesn't block the TUI
                    subprocess.Popen([editor, str(file_path)])
                self.status_message = f"Opening {item_name}..."
            except Exception as e:
                self.status_message = f"Error opening file: {e}"
        else:
            self.status_message = "No editable item selected."

    def on_unmount(self) -> None:
        """Clean up resources when app exits."""
        # Stop watch mode gracefully
        if self.watch_mode_instance and self.watch_mode_instance.running:
            self.watch_mode_instance.stop()
            if self.watch_mode_thread:
                self.watch_mode_thread.join(timeout=5.0)

    def on_mount(self) -> None:
        """Load initial data when app starts."""
        # Initialize performance monitor and command registry
        self.performance_monitor = PerformanceMonitor()
        self.command_registry = CommandRegistry()
        self.command_registry.register_batch(DEFAULT_COMMANDS)
        self.metrics_collector = MetricsCollector()

        # Initialize intelligent agent for auto-activation and recommendations
        claude_dir = _resolve_claude_dir()
        self.claude_home = claude_dir
        self.intelligent_agent = IntelligentAgent(claude_dir / "intelligence")

        # Analyze context and get initial recommendations
        self.intelligent_agent.analyze_context()

        # Load data
        self.load_agents()
        self.load_rules()
        self.load_modes()
        self.load_principles()
        self.load_skills()
        self.load_slash_commands()
        self.load_agent_tasks()
        self.load_workflows()
        self.load_worktrees()
        self.load_scenarios()
        self.load_profiles()
        self.load_mcp_servers()
        self.update_view()

        # Start performance monitoring timer
        self.set_interval(1.0, self.update_performance_status)
        self.set_interval(2.0, self._poll_tasks_file_changes)

        # Force initial status bar update
        self.watch_status_message(self.status_message)

        # Show AI recommendations if high confidence
        self._check_auto_activations()

        # Schedule background check for pending prompts
        self.call_after_refresh(self._post_startup_checks)

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

        agents = getattr(self, "agents", [])
        agent_total = len(agents)
        agent_active = sum(1 for a in agents if getattr(a, "status", "") == "active")
        tasks = getattr(self, "agent_tasks", [])
        task_active = sum(1 for t in tasks if getattr(t, "status", "") == "running")
        perf_text = ""
        if hasattr(self, "performance_monitor"):
            perf_text = self.performance_monitor.get_status_bar(compact=True)

        # Get token count (cached to avoid repeated file reads)
        token_text = ""
        try:
            if not hasattr(self, "_token_cache") or (time.time() - getattr(self, "_token_cache_time", 0)) > 30:
                _, total_stats = get_active_context_tokens()
                self._token_cache = total_stats.tokens_formatted
                self._token_cache_time = time.time()
            token_text = self._token_cache
        except Exception:
            pass

        status_bar.update_payload(
            view=self.current_view.title(),
            message=self.status_message,
            perf=perf_text,
            agent_active=agent_active,
            agent_total=agent_total,
            task_active=task_active,
            token_count=token_text,
        )

    def watch_current_view(self, view: str) -> None:
        """Update display when view changes."""
        self.update_view()
        self.refresh_status_bar()

        # Dynamically update footer bindings based on context
        view_bindings = {
            "agents": {"toggle", "details_context", "validate_context", "edit_item", "copy_definition"},
            "rules": {"toggle", "edit_item", "copy_definition"},
            "modes": {"toggle", "edit_item", "copy_definition"},
            "principles": {
                "toggle",
                "edit_item",
                "copy_definition",
                "details_context",
                "context_action",
                "docs_context",
            },
            "skills": {
                "details_context",
                "validate_context",
                "metrics_context",
                "docs_context",
                "context_action",
                "edit_item",
                "copy_definition",
            },
            "commands": {"details_context", "edit_item", "copy_definition"},
            "mcp": {
                "details_context",
                "docs_context",
                "mcp_test_selected",
                "mcp_diagnose",
                "mcp_add",
                "mcp_edit",
                "mcp_remove",
            },
            "profiles": {"toggle", "profile_save_prompt", "profile_delete", "setup_init_wizard", "setup_init_minimal", "setup_migration", "setup_health_check"},
            "export": {"toggle", "export_cycle_format", "export_run", "export_clipboard"},
            "workflows": {"run_selected", "stop_selected"},
            "worktrees": {
                "worktree_add",
                "worktree_open",
                "worktree_remove",
                "worktree_prune",
                "worktree_set_base_dir",
                "details_context",
            },
            "scenarios": {"scenario_preview", "run_selected", "stop_selected"},
            "ai_assistant": {
                "auto_activate",
                "consult_gemini",
                "request_reviews",
                "assign_llm_tasks",
            },
            "watch_mode": {"toggle", "watch_change_directory", "watch_toggle_auto", "watch_adjust_threshold", "watch_adjust_interval"},
            "tasks": {"details_context", "edit_item", "task_open_source", "task_open_external"},
        }

        # Get the set of keys to show for the current view, default to empty set
        keys_to_show = view_bindings.get(self.current_view, set())

        # Update the adaptive footer with current view context
        try:
            footer = self.query_one("#adaptive-footer", AdaptiveFooter)
            footer.update_view(view)
        except Exception:
            pass  # Footer not yet mounted

        self.refresh(layout=True)

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

    def _validate_workflow_schema(self, workflow_data: Any, file_path: Path) -> bool:
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

        if "description" in workflow_data and not isinstance(
            workflow_data["description"], str
        ):
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

    def _parse_iso_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse ISO8601 timestamps produced by scenario state files."""
        if not value:
            return None
        normalized = value.strip()
        if not normalized:
            return None
        try:
            if normalized.endswith("Z"):
                normalized = normalized[:-1] + "+00:00"
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            return dt
        except Exception:
            return None

    def _main_table(self) -> Optional[DataTable[Any]]:
        """Return the main DataTable widget if available."""
        try:
            return self.query_one("#main-table", DataTable)
        except Exception:
            return None

    def _table_cursor_index(self) -> Optional[int]:
        """Return the current row index in the main DataTable."""
        table = self._main_table()
        return table.cursor_row if table else None

    def _restore_main_table_cursor(self, saved_cursor_row: Optional[int]) -> None:
        """Restore the cursor position in the main table after a refresh."""
        if saved_cursor_row is None:
            return
        table = self._main_table()
        if not table:
            return
        if table.row_count <= 0:
            return
        table.move_cursor(row=min(saved_cursor_row, table.row_count - 1))

    def _wizard_max_index(self) -> int:
        """Return max selectable index for the init wizard."""
        if not self.wizard_active:
            return 0
        if self.wizard_step == 0:
            return 5
        if self.wizard_step == 1:
            assets = discover_plugin_assets()
            return max(0, len(assets.get("agents", [])) - 1)
        if self.wizard_step == 2:
            assets = discover_plugin_assets()
            return max(0, len(assets.get("modes", [])) - 1)
        if self.wizard_step == 3:
            assets = discover_plugin_assets()
            return max(0, len(assets.get("rules", [])) - 1)
        return 0

    def _wizard_set_index(self, index: int) -> None:
        """Set wizard selection index with bounds checking."""
        if not self.wizard_active:
            return
        max_idx = self._wizard_max_index()
        new_idx = max(0, min(index, max_idx))
        if new_idx != self.state.selected_index:
            self.state.selected_index = new_idx
            self.update_view()

    def _wizard_move_by(self, delta: int) -> None:
        """Move wizard selection by delta with bounds checking."""
        if not self.wizard_active:
            return
        self._wizard_set_index(self.state.selected_index + delta)

    def _wizard_half_page_delta(self) -> int:
        """Compute half-page jump for the wizard selection."""
        max_idx = self._wizard_max_index()
        if max_idx <= 0:
            return 1
        return max(1, (max_idx + 1) // 2)

    def _table_page_delta(self, table: DataTable[Any], row_index: int, direction: str) -> int:
        """Compute a page-sized row delta for the given table."""
        if table.row_count <= 1:
            return 0
        try:
            height = table.size.height - (table.header_height if table.show_header else 0)
        except Exception:
            height = 0

        rows_to_scroll = 0
        if height > 0:
            try:
                ordered_rows = table.ordered_rows
            except Exception:
                ordered_rows = []
            if ordered_rows:
                row_index = max(0, min(row_index, len(ordered_rows) - 1))
                offset = 0
                if direction == "up":
                    rows_iter = ordered_rows[: row_index + 1]
                else:
                    rows_iter = ordered_rows[row_index:]
                for ordered_row in rows_iter:
                    offset += ordered_row.height
                    if offset > height:
                        break
                    rows_to_scroll += 1

        if rows_to_scroll <= 0:
            rows_to_scroll = min(10, table.row_count)

        return max(1, rows_to_scroll - 1)

    def _table_page_move(self, direction: str, *, half: bool = False) -> None:
        """Move the main table cursor by a page (or half-page)."""
        table = self._main_table()
        if not table or table.row_count <= 0:
            return
        row_index = table.cursor_row if table.cursor_row is not None else 0
        delta = self._table_page_delta(table, row_index, direction)
        if delta <= 0:
            return
        if half:
            delta = max(1, delta // 2)
        if direction == "up":
            new_row = row_index - delta
        else:
            new_row = row_index + delta
        new_row = max(0, min(new_row, table.row_count - 1))
        table.move_cursor(row=new_row)

    def _flag_manager_set_index(self, index: int) -> None:
        """Set flag manager selection with bounds checking."""
        if self.current_view != "flag_manager":
            return
        if not self.flag_files:
            return
        new_idx = max(0, min(index, len(self.flag_files) - 1))
        if new_idx != self.selected_flag_index:
            self.selected_flag_index = new_idx
            self.update_view()

    def _flag_manager_page_move(self, direction: str, *, half: bool = False) -> None:
        """Move flag manager selection by a page (or half-page)."""
        if self.current_view != "flag_manager" or not self.flag_files:
            return
        delta = 1
        table = self._main_table()
        if table and table.row_count > 0:
            row_offset = 2
            row_index = min(table.row_count - 1, row_offset + self.selected_flag_index)
            delta = self._table_page_delta(table, row_index, direction)
        if half:
            delta = max(1, delta // 2)
        if direction == "up":
            self._flag_manager_set_index(self.selected_flag_index - delta)
        else:
            self._flag_manager_set_index(self.selected_flag_index + delta)

    def _text_input_focused(self) -> bool:
        """Return True if a text input widget currently has focus."""
        focused = self.focused
        return isinstance(focused, Input)

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
        servers = self.mcp_servers
        if index < 0 or index >= len(servers):
            return None
        return servers[index]

    def _selected_worktree(self) -> Optional[WorktreeInfo]:
        index = self._table_cursor_index()
        if index is None or not self.worktrees:
            return None
        if index < 0 or index >= len(self.worktrees):
            return None
        return self.worktrees[index]

    def _selected_skill(self) -> Optional[Dict[str, Any]]:
        index = self._table_cursor_index()
        skills = self.skills
        if index is None or not skills:
            return None
        if index < 0 or index >= len(skills):
            return None
        return skills[index]

    def _selected_command(self) -> Optional[SlashCommandInfo]:
        index = self._table_cursor_index()
        commands = self.slash_commands
        if index is None or not commands:
            return None
        if index < 0 or index >= len(commands):
            return None
        return commands[index]

    def _normalize_slug(self, value: str) -> str:
        """Normalize a slug for comparison (lowercase, no .md, POSIX separators)."""
        candidate = value.strip().replace("\\", "/")
        if candidate.endswith(".md"):
            candidate = candidate[:-3]
        return candidate.lower()

    def _relative_slug(self, path: Path, base_dir: Path) -> str:
        """Compute normalized slug for a file relative to a base directory."""
        try:
            relative = path.relative_to(base_dir)
        except ValueError:
            relative = path
        return self._normalize_slug(relative.as_posix())

    def _active_rule_slugs(self, claude_dir: Path) -> Set[str]:
        """Return active rule slugs from .active-rules and live files."""
        active = {
            self._normalize_slug(entry)
            for entry in _parse_active_entries(claude_dir / ".active-rules")
        }
        rules_dir = claude_dir / "rules"
        for path in _iter_md_files(rules_dir):
            active.add(self._relative_slug(path, rules_dir))
        return active

    def _active_mode_slugs(self, claude_dir: Path) -> Set[str]:
        """Return active mode slugs from .active-modes file only."""
        return {
            self._normalize_slug(entry)
            for entry in _parse_active_entries(claude_dir / ".active-modes")
        }

    def _ensure_configured_mcp(self, server: MCPServerInfo, action: str) -> bool:
        """Ensure an MCP server is configured before running certain actions."""
        if getattr(server, "doc_only", False):
            self.notify(
                f"{server.name} is not configured. Use 'Add MCP' to install before {action}.",
                severity="warning",
                timeout=3,
            )
            return False
        return True

    def _selected_workflow(self) -> Optional[WorkflowInfo]:
        index = self._table_cursor_index()
        workflows = self.workflows
        if index is None or not workflows:
            return None
        if index < 0 or index >= len(workflows):
            return None
        return workflows[index]

    def _selected_scenario(self) -> Optional[ScenarioInfo]:
        index = self._table_cursor_index()
        scenarios = self.scenarios
        if index is None or not scenarios:
            return None
        if index < 0 or index >= len(scenarios):
            return None
        return scenarios[index]

    def _format_command_stack(self, command: SlashCommandInfo) -> str:
        """Summarize linked assets for a slash command."""
        sections: List[str] = []
        if command.agents:
            sections.append(
                "[cyan]Agents:[/cyan] "
                + Format.truncate(Format.list_items(command.agents, 2), 40)
            )
        if command.personas:
            sections.append(
                "[magenta]Personas:[/magenta] "
                + Format.truncate(Format.list_items(command.personas, 2), 40)
            )
        if command.mcp_servers:
            sections.append(
                "[yellow]MCP:[/yellow] "
                + Format.truncate(Format.list_items(command.mcp_servers, 2), 40)
            )

        if not sections:
            return "[dim]—[/dim]"
        return "  |  ".join(sections)

    def _skill_slug(self, skill: Dict[str, Any]) -> str:
        path_value = skill.get("path")
        if not path_value:
            name_value = str(skill.get("name", ""))
            return name_value.replace(" ", "-")
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
        return await self._prompt_text(
            prompt_title, "Enter skill name", placeholder="e.g. observability/alerts"
        )

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
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    check=True,
                    input=text.encode("utf-8"),
                )
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

        agents = [
            Path(entry).stem for entry in self._extract_profile_list(content, "AGENTS")
        ]
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
            if exit_code != 0 and (
                not mode_message or "already active" not in mode_message.lower()
            ):
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

    async def _prompt_text(
        self, title: str, prompt: str, *, default: str = "", placeholder: str = ""
    ) -> Optional[str]:
        dialog = PromptDialog(title, prompt, default=default, placeholder=placeholder)
        value = await self.push_screen(dialog, wait_for_dismiss=True)
        if value is None:
            return None
        value = value.strip()
        return value or None

    async def _handle_skill_result(
        self,
        func: Callable[..., Tuple[int, str]],
        *,
        args: Optional[Sequence[str]] = None,
        title: str,
        success: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        args = list(args or [])
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
                self.notify(success, severity="information", timeout=2)
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
            for disabled_dir in _inactive_dir_candidates(claude_dir, "agents"):
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
            if hasattr(self, "metrics_collector"):
                self.metrics_collector.record("agents_active", float(active_count))
            self.refresh_status_bar()

        except Exception as e:
            self.status_message = f"Error loading agents: {e}"
            self.agents = []

    def _parse_agent_file(self, path: Path, status: str) -> Optional[AgentGraphNode]:
        """Parse an agent file and return an AgentGraphNode."""
        try:
            lines = _read_agent_front_matter_lines(path)
            if not lines:
                return None

            name = _extract_agent_name(path, lines)
            tokens = _tokenize_front_matter(lines)

            category = (
                _extract_scalar_from_paths(
                    tokens,
                    (
                        ("metadata", "category"),
                        ("category",),
                    ),
                )
                or "general"
            )

            tier = (
                _extract_scalar_from_paths(
                    tokens,
                    (
                        ("metadata", "tier", "id"),
                        ("tier", "id"),
                    ),
                )
                or "standard"
            )

            requires_raw, recommends_raw = _parse_dependencies_from_front(lines)
            requires = [item for item in requires_raw if item]
            recommends = [item for item in recommends_raw if item]

            return AgentGraphNode(
                name=name,
                slug=path.stem,
                path=path,
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

            self._attach_skill_ratings(skills)
            self.skills = skills
            if self.skill_rating_error:
                self.status_message = (
                    f"Loaded {len(skills)} skills (ratings offline)"
                )
            else:
                self.status_message = f"Loaded {len(skills)} skills"

        except Exception as e:
            self.status_message = f"Error loading skills: {e}"
            self.skills = []

    def load_slash_commands(self) -> None:
        """Load slash command metadata from the commands directory."""
        try:
            claude_dir = _resolve_claude_dir()
            commands_dir = self._validate_path(claude_dir, claude_dir / "commands")
        except ValueError:
            claude_dir = _resolve_claude_dir()
            commands_dir = claude_dir / "commands"

        if not commands_dir.exists():
            self.slash_commands = []
            self.status_message = "Commands directory not found"
            return

        try:
            commands = scan_slash_commands(commands_dir, home_dir=claude_dir)
        except Exception as exc:
            self.slash_commands = []
            self.status_message = f"Error loading slash commands: {exc}"[:160]
            return

        self.slash_commands = commands
        namespace_count = len({cmd.namespace for cmd in commands})
        if commands:
            self.status_message = (
                f"Loaded {len(commands)} slash commands"
                if namespace_count <= 1
                else f"Loaded {len(commands)} slash commands across {namespace_count} namespaces"
            )
        else:
            self.status_message = "No slash commands found"

    def _parse_skill_file(
        self, skill_file: Path, claude_dir: Path
    ) -> Optional[Dict[str, Any]]:
        """Parse a skill file and return skill data dictionary."""
        try:
            content = skill_file.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)

            if not front_matter:
                return None

            lines = front_matter.strip().splitlines()
            tokens = _tokenize_front_matter(lines)

            # Extract metadata
            name = (
                _extract_scalar_from_paths(tokens, (("name",),))
                or skill_file.parent.name
            )
            description = (
                _extract_scalar_from_paths(tokens, (("description",),))
                or "No description"
            )
            category = _extract_scalar_from_paths(tokens, (("category",),)) or "general"

            # Determine location (user vs project)
            # If skill is in user's home cortex dir, it's a user skill
            home_claude = _resolve_cortex_root()
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
                description = description[: max_desc_len - 3] + "..."

            return {
                "name": name,
                "slug": skill_file.parent.name,
                "description": description,
                "category": category,
                "location": location,
                "status": status,
                "path": str(skill_file),
                "rating_metrics": None,
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

    def _get_skill_rating_collector(self) -> Optional[SkillRatingCollector]:
        """Instantiate (or return cached) rating collector."""
        if self.skill_rating_collector is not None:
            return self.skill_rating_collector

        try:
            self.skill_rating_collector = SkillRatingCollector()
            self.skill_rating_error = None
        except Exception as exc:
            # Surface error but don't crash the skills view
            self.skill_rating_collector = None
            self.skill_rating_error = str(exc)
        return self.skill_rating_collector

    def _get_skill_prompt_manager(self) -> Optional[SkillRatingPromptManager]:
        """Lazy-load the prompt manager used for auto-rating nudges."""
        if isinstance(self.skill_prompt_manager, SkillRatingPromptManager):
            return self.skill_prompt_manager

        try:
            self.skill_prompt_manager = SkillRatingPromptManager()
        except Exception as exc:
            # Surface one-time status so the user understands why prompts are missing
            self.status_message = f"Rating prompts unavailable: {exc}"[:120]
            self.skill_prompt_manager = None
        return self.skill_prompt_manager

    def _attach_skill_ratings(self, skills: List[Dict[str, Any]]) -> None:
        """Populate rating metrics for every known skill (if available)."""
        collector = self._get_skill_rating_collector()
        if not collector:
            for skill in skills:
                skill["rating_metrics"] = None
            return

        for skill in skills:
            slug = skill.get("slug") or self._skill_slug(skill)
            try:
                metrics = collector.get_skill_score(slug)
            except Exception as exc:
                self.skill_rating_error = str(exc)
                metrics = None
            skill["rating_metrics"] = metrics

    def _format_skill_rating(self, skill: Dict[str, Any]) -> str:
        """Return a human-friendly rating summary for the table."""
        metrics = skill.get("rating_metrics")
        if isinstance(metrics, SkillQualityMetrics):
            total_text = f"{metrics.total_ratings} rating"
            if metrics.total_ratings != 1:
                total_text += "s"
            helpful_text = f"{int(metrics.helpful_percentage)}% helpful"
            return (
                f"[gold1]{metrics.star_display()}[/gold1]\n"
                f"[dim]{total_text} · {helpful_text}[/dim]"
            )

        if self.skill_rating_error:
            summary = self.skill_rating_error.splitlines()[0][:48]
            return f"[red]Unavailable[/red]\n[dim]{summary}[/dim]"

        return "[dim]No ratings yet[/dim]"

    async def _post_startup_checks(self) -> None:
        """Run startup prompts after the UI has mounted."""
        await self._maybe_prompt_for_missing_templates()
        await self._maybe_prompt_for_skill_ratings()

    async def _maybe_prompt_for_missing_templates(self) -> None:
        """Offer to initialize missing template files in CLAUDE_PLUGIN_ROOT."""
        explicit_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if not explicit_root:
            return

        target_root = Path(explicit_root).expanduser()
        if not target_root.exists():
            return

        missing = _find_missing_template_files(target_root)
        if not missing:
            return

        preview = ", ".join(str(path) for path in missing[:5])
        if len(missing) > 5:
            preview += f" (+{len(missing) - 5} more)"

        dialog = ConfirmDialog(
            "Initialize Templates",
            "Template files are missing from CLAUDE_PLUGIN_ROOT:\n"
            f"{target_root}\n\n"
            f"Missing: {preview}\n\n"
            "Initialize missing templates and launch the Init Wizard?",
            default=True,
        )
        confirm = await self.push_screen(dialog, wait_for_dismiss=True)
        if not confirm:
            self.notify(
                "Templates missing. Run Init Wizard from Profiles when ready.",
                severity="warning",
                timeout=4,
            )
            return

        created = _ensure_template_files(target_root)
        if created:
            self.notify(
                f"Initialized {len(created)} template files",
                severity="information",
                timeout=3,
            )
        else:
            self.notify(
                "Templates already present",
                severity="information",
                timeout=2,
            )

        await self._run_init_wizard()

    async def _maybe_prompt_for_skill_ratings(self) -> None:
        """Surface auto-prompts for recently used skills."""
        manager = self._get_skill_prompt_manager()
        if not manager:
            return

        try:
            prompts = manager.detect_due_prompts(limit=3)
        except Exception as exc:
            self.status_message = f"Unable to check rating prompts: {exc}"[:120]
            return

        for prompt in prompts:
            manager.mark_prompted(prompt.skill)
            reason = prompt.reason
            dialog = ConfirmDialog(
                "Rate Skill",
                f"{prompt.skill}\n{reason}\n\nWould you like to rate this skill now?",
            )
            confirm = await self.push_screen(dialog, wait_for_dismiss=True)
            if not confirm:
                continue

            await self._rate_skill_interactive(prompt.skill, prompt.skill)

    def show_skills_view(self, table: DataTable[Any]) -> None:
        """Show skills table with enhanced colors (READ-ONLY)."""
        table.add_column("Name", key="name", width=25)
        table.add_column("Rating", key="rating", width=18)
        table.add_column("Category", key="category", width=15)
        table.add_column("Location", key="location", width=10)
        table.add_column("Description", key="description")

        if not hasattr(self, "skills") or not self.skills:
            table.add_row("[dim]No skills found[/dim]", "", "", "", "")
            return

        category_colors = {
            "api-design": "cyan",
            "security": "red",
            "performance": "yellow",
            "testing": "green",
            "architecture": "blue",
            "deployment": "magenta",
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

            # Truncate description - show more text, escape Rich markup
            desc_text = Format.truncate(skill['description'], 150).replace("[", "\\[")
            description = f"[dim]{desc_text}[/dim]"

            rating_text = self._format_skill_rating(skill)

            table.add_row(
                name,
                rating_text,
                category_text,
                location_text,
                description,
            )

    def show_commands_view(self, table: AnyDataTable) -> None:
        """Render slash command catalog."""
        table.add_column("Command", width=32)
        table.add_column("Category", width=16)
        table.add_column("Complexity", width=12)
        table.add_column("Stack", width=32)
        table.add_column("Description")

        commands = getattr(self, "slash_commands", [])
        if not commands:
            table.add_row("[dim]No slash commands found[/dim]", "", "", "", "")
            return

        category_colors: Dict[str, str] = {}
        fallback_colors = self.CATEGORY_FALLBACK_COLORS

        complexity_palette = {
            "basic": "green",
            "standard": "cyan",
            "advanced": "magenta",
            "expert": "yellow",
            "over9000": "bright_magenta",
        }

        for cmd in commands:
            icon = Icons.CODE if cmd.location == "user" else Icons.DOC
            icon_color = "cyan" if cmd.location == "user" else "magenta"
            command_text = (
                f"[{icon_color}]{icon}[/{icon_color}] /{cmd.namespace}:{cmd.name}"
            )

            cat_key = cmd.category.lower()
            color = category_colors.get(cat_key)
            if not color:
                color = self.CATEGORY_PALETTE.get(cat_key)
                if not color:
                    color = fallback_colors[len(category_colors) % len(fallback_colors)]
                category_colors[cat_key] = color
            category_text = f"[{color}]{cmd.category.title()}[/{color}]"

            comp_color = complexity_palette.get(cmd.complexity.lower(), "white")
            complexity_text = f"[{comp_color}]{cmd.complexity.title()}[/{comp_color}]"

            stack_text = self._format_command_stack(cmd)
            desc_text = Format.truncate(cmd.description, 110).replace("[", "\\[")
            description = f"[dim]{desc_text}[/dim]"

            table.add_row(
                command_text,
                category_text,
                complexity_text,
                stack_text,
                description,
            )

    def _render_profiles_table(self, table: DataTable[Any]) -> None:
        """Render profile management view with setup tools."""
        table.add_column("Item", width=28)
        table.add_column("Type", width=12)
        table.add_column("Description")
        table.add_column("Action", width=18)

        # Setup Tools Section
        table.add_row(
            "[bold cyan]━━━ Setup Tools ━━━[/bold cyan]",
            "",
            "[dim]Press key to run[/dim]",
            "",
        )
        table.add_row(
            f"{Icons.PLAY} Init Wizard",
            "[yellow]Setup[/yellow]",
            "Interactive project initialization wizard",
            "[dim]Shift+I[/dim]",
        )
        table.add_row(
            f"{Icons.SUCCESS} Init Minimal",
            "[yellow]Setup[/yellow]",
            "Quick minimal configuration setup",
            "[dim]m[/dim]",
        )
        table.add_row(
            f"{Icons.SYNC} Migration",
            "[yellow]Setup[/yellow]",
            "Migrate from comment-based to file-based activation",
            "[dim]Shift+M[/dim]",
        )
        table.add_row(
            f"{Icons.TEST} Health Check",
            "[yellow]Setup[/yellow]",
            "Run diagnostics and verify directory structure",
            "[dim]c[/dim]",
        )
        table.add_row(
            "[bold cyan]━━━ Profiles ━━━[/bold cyan]",
            "",
            "[dim]Enter to apply, n to save new[/dim]",
            "",
        )

        if not self.profiles:
            table.add_row("[dim]No profiles found[/dim]", "", "", "")
            return

        for profile in self.profiles:
            name = profile.get("name", "unknown")
            ptype = profile.get("type", "built-in")
            description_value = profile.get("description") or ""
            description = Format.truncate(description_value, 60)
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

    def _render_export_table(self, table: DataTable[Any]) -> None:
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
            files = components.get(key, {})
            count = len(files)
            # Calculate token count for this category
            try:
                stats = count_category_tokens(files)
                token_str = f", {stats.tokens_formatted} tokens"
            except Exception:
                token_str = ""

            icon = Icons.SUCCESS if enabled else Icons.WARNING
            state = "[green]Included[/green]" if enabled else "[dim]Excluded[/dim]"
            state = f"{state} ({count} files{token_str})"

            table.add_row(
                f"{icon} {label}",
                state,
                Format.truncate(description or "", 60),
            )
            self.export_row_meta.append(("category", key))

        format_label = (
            "Agent-generic" if self.export_agent_generic else "Claude-specific"
        )
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
        from ..token_counter import TokenStats

        enabled = []
        total_stats = TokenStats(files=0, chars=0, words=0, tokens=0)

        for key, label, _description in EXPORT_CATEGORIES:
            if not self.export_options.get(key, True):
                continue
            files = components.get(key, {})
            count = len(files)
            enabled.append(f"{label} ({count})")
            try:
                stats = count_category_tokens(files)
                total_stats = total_stats + stats
            except Exception:
                pass

        if not enabled:
            return "No components selected"

        summary_parts = enabled[:3] if len(enabled) > 3 else enabled
        summary = ", ".join(summary_parts)
        if len(enabled) > 3:
            summary += ", …"

        # Add total token count
        if total_stats.tokens > 0:
            summary += f" | {total_stats.tokens_formatted} total"

        return summary

    def _export_exclude_categories(self) -> set[str]:
        """Return the set of categories to exclude when exporting."""
        return {key for key, enabled in self.export_options.items() if not enabled}

    def _default_export_path(self) -> Path:
        """Best-effort default export path."""
        desktop = Path.home() / "Desktop"
        if desktop.exists():
            return desktop / "cortex-export.md"
        return Path.cwd() / "cortex-export.md"

    def load_agent_tasks(self) -> None:
        """Load active agent tasks for orchestration view."""
        tasks: List[AgentTask] = []
        tasks_dir: Optional[Path] = None
        try:
            tasks_dir = self._tasks_dir()

            # Check for active tasks file
            active_tasks_file = tasks_dir / "active_agents.json"
            if active_tasks_file.is_file():
                task_data = json.loads(active_tasks_file.read_text(encoding="utf-8"))

                for task_id, task_info in task_data.items():
                    tasks.append(
                        AgentTask(
                            agent_id=task_id,
                            agent_name=task_info.get("name", task_id),
                            workstream=task_info.get("workstream", "primary"),
                            status=task_info.get("status", "pending"),
                            progress=task_info.get("progress", 0),
                            category=task_info.get("category", "general"),
                            started=task_info.get("started"),
                            completed=task_info.get("completed"),
                            description=task_info.get("description", ""),
                            raw_notes=task_info.get("raw_notes", ""),
                            source_path=task_info.get("source_path"),
                        )
                    )
        except Exception:
            # No active tasks or error reading - use empty list
            tasks_dir = tasks_dir or None

        if not tasks and tasks_dir is not None:
            tasks = self._build_workflow_task_fallback(tasks_dir)

        tasks.sort(key=lambda t: t.agent_name.lower())
        self.agent_tasks = tasks
        if tasks_dir is not None:
            self._tasks_state_signature = self._compute_tasks_state_signature(tasks_dir)
        else:
            self._tasks_state_signature = self._project_agent_signature()
        self.refresh_status_bar()

    def load_rules(self) -> None:
        """Load rules from the system."""
        try:
            rules: List[RuleNode] = []
            claude_dir = _resolve_claude_dir()
            active_rule_slugs = self._active_rule_slugs(claude_dir)

            # Check active rules
            rules_dir = self._validate_path(claude_dir, claude_dir / "rules")
            if rules_dir.is_dir():
                for path in _iter_md_files(rules_dir):
                    if _is_disabled(path):
                        continue
                    slug = self._relative_slug(path, rules_dir)
                    status = "active" if slug in active_rule_slugs else "inactive"
                    node = self._parse_rule_file(
                        path,
                        status,
                    )
                    if node:
                        rules.append(node)

            # Check disabled rules
            for disabled_dir in _inactive_dir_candidates(claude_dir, "rules"):
                valid_dir = self._validate_path(claude_dir, disabled_dir)
                if valid_dir.is_dir():
                    for path in _iter_md_files(valid_dir):
                        slug = self._relative_slug(path, valid_dir)
                        status = "active" if slug in active_rule_slugs else "inactive"
                        node = self._parse_rule_file(path, status)
                        if node:
                            rules.append(node)

            # Sort by category and name
            rules.sort(key=lambda r: (r.category, r.name.lower()))

            self.rules = rules
            active_count = sum(1 for r in rules if r.status == "active")
            self.status_message = f"Loaded {len(rules)} rules ({active_count} active)"
            if hasattr(self, "metrics_collector"):
                self.metrics_collector.record("rules_active", float(active_count))

        except Exception as e:
            self.status_message = f"Error loading rules: {e}"
            self.rules = []

    def load_principles(self) -> None:
        """Load principles snippets from the system."""
        try:
            principles: List[PrincipleSnippet] = []
            claude_dir = _resolve_claude_dir()
            principles_dir = self._validate_path(claude_dir, claude_dir / "principles")

            active_entries = _parse_active_entries(claude_dir / ".active-principles")
            active_names = {
                entry[:-3] if entry.endswith(".md") else entry
                for entry in active_entries
            }

            if not active_names and principles_dir.is_dir():
                active_names = {path.stem for path in _iter_md_files(principles_dir)}

            if principles_dir.is_dir():
                for path in _iter_md_files(principles_dir):
                    status = "active" if path.stem in active_names else "inactive"
                    node = self._parse_principle_file(path, status)
                    if node:
                        principles.append(node)

            self.principles = principles
            active_count = sum(1 for p in principles if p.status == "active")
            self.status_message = (
                f"Loaded {len(principles)} principles ({active_count} active)"
            )
            if hasattr(self, "metrics_collector"):
                self.metrics_collector.record(
                    "principles_active",
                    float(active_count),
                )
        except Exception as e:
            self.status_message = f"Error loading principles: {e}"
            self.principles = []

    def _parse_principle_file(
        self,
        path: Path,
        status: str,
    ) -> Optional[PrincipleSnippet]:
        """Parse a principles snippet file into a PrincipleSnippet."""
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()

            title = path.stem
            description = ""
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith("<!--"):
                    continue
                if stripped.startswith("#"):
                    if title == path.stem:
                        title = stripped.lstrip("#").strip()
                    continue
                description = stripped
                break

            if not description:
                description = title

            return PrincipleSnippet(
                name=path.stem,
                status=status,
                title=title,
                description=description,
                path=path,
            )
        except Exception:
            return None

    def _parse_rule_file(self, path: Path, status: str) -> Optional[RuleNode]:
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
            modes: List[ModeInfo] = []
            claude_dir = _resolve_claude_dir()
            active_mode_slugs = self._active_mode_slugs(claude_dir)

            # Load active modes from modes/ directory
            modes_dir = self._validate_path(claude_dir, claude_dir / "modes")
            if modes_dir.is_dir():
                for path in _iter_md_files(modes_dir):
                    if _is_disabled(path):
                        continue
                    slug = self._relative_slug(path, modes_dir)
                    status = "active" if slug in active_mode_slugs else "inactive"
                    node = self._parse_mode_file(path, status)
                    if node:
                        modes.append(node)

            # Load inactive modes from inactive/modes/ directory (legacy dirs supported)
            for inactive_dir in _inactive_dir_candidates(claude_dir, "modes"):
                valid_dir = self._validate_path(claude_dir, inactive_dir)
                if valid_dir.is_dir():
                    for path in _iter_md_files(valid_dir):
                        slug = self._relative_slug(path, valid_dir)
                        status = "active" if slug in active_mode_slugs else "inactive"
                        node = self._parse_mode_file(path, status)
                        if node:
                            modes.append(node)

            # Sort by status (active first) and then by name
            modes.sort(key=lambda m: (m.status != "active", m.name.lower()))

            self.modes = modes
            active_count = sum(1 for m in modes if m.status == "active")
            self.status_message = f"Loaded {len(modes)} modes ({active_count} active)"

            # Debug logging
            print(f"[DEBUG] load_modes: Loaded {len(modes)} modes")
            for mode in modes:
                print(f"[DEBUG]   - {mode.name} ({mode.status}): {mode.purpose[:50]}...")

            if hasattr(self, "metrics_collector"):
                self.metrics_collector.record("modes_active", float(active_count))

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.status_message = f"Error loading modes: {e}"
            self.modes = []
            # Log full traceback for debugging
            print(f"[DEBUG] Mode loading error:\n{error_detail}")

    def _parse_mode_file(self, path: Path, status: str) -> Optional[ModeInfo]:
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
            subtitle = ""

            found_title = False
            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("# ") and not found_title:
                    # Extract title (e.g., "# Task Management Mode" -> "Task Management")
                    # Only use the FIRST h1 heading
                    title = line[2:].strip()
                    if title.endswith(" Mode"):
                        display_name = title[:-5]  # Remove " Mode" suffix
                    else:
                        display_name = title
                    found_title = True
                elif line.startswith("**Purpose**:"):
                    # Extract purpose
                    purpose = line.split("**Purpose**:")[1].strip()
                elif not subtitle and line.startswith("**") and not line.startswith("**Purpose**") and ":" not in line:
                    # Extract subtitle/tagline (e.g., "**Universal Visual Excellence Mode**")
                    subtitle = line.replace("**", "").strip()
                elif (
                    line.startswith("## ")
                    and "Activation" not in line
                    and not description
                ):
                    # Use first non-activation h2 as description fallback
                    description = line[3:].strip()

            # Build final purpose: prefer explicit Purpose, then subtitle, then description
            if not purpose:
                purpose = subtitle or description

            # Use purpose as description if available, otherwise use first description
            final_description = purpose if purpose else description
            if not final_description:
                # Fallback: use first non-empty, non-heading, non-bold line
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#") and not line.startswith("**") and not line.startswith(">"):
                        final_description = line[:100]  # Limit length
                        break

            return ModeInfo(
                name=display_name,
                status=status,
                purpose=purpose or final_description or "Behavioral mode",
                description=final_description or "No description available",
                path=path,
            )
        except Exception as e:
            # Return a placeholder instead of None so user can see something went wrong
            return ModeInfo(
                name=path.stem,
                status=status,
                purpose=f"Error parsing mode: {str(e)[:50]}",
                description="Failed to parse mode file",
                path=path,
            )

    def load_prompts(self) -> None:
        """Load prompts from the prompt library."""
        try:
            from ..core.prompts import discover_prompts as core_discover_prompts

            core_prompts = core_discover_prompts()

            # Convert core PromptInfo to TUI PromptInfo
            prompts: List[PromptInfo] = []
            for cp in core_prompts:
                prompts.append(PromptInfo(
                    name=cp.name,
                    slug=cp.slug,
                    status=cp.status,
                    category=cp.category,
                    description=cp.description,
                    tokens=cp.tokens,
                    path=cp.path,
                ))

            # Sort by status (active first), then by category, then by name
            prompts.sort(key=lambda p: (p.status != "active", p.category.lower(), p.name.lower()))

            self.prompts = prompts
            active_count = sum(1 for p in prompts if p.status == "active")
            self.status_message = f"Loaded {len(prompts)} prompts ({active_count} active)"

            if hasattr(self, "metrics_collector"):
                self.metrics_collector.record("prompts_active", float(active_count))

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.status_message = f"Error loading prompts: {e}"
            self.prompts = []
            print(f"[DEBUG] Prompt loading error:\n{error_detail}")

    def load_workflows(self) -> None:
        """Load workflows from the workflows directory."""
        workflows: List[WorkflowInfo] = []
        try:
            claude_dir = _resolve_claude_dir()
            workflows_dir = self._validate_path(claude_dir, claude_dir / "workflows")
            tasks_dir = self._validate_path(
                claude_dir, claude_dir / "tasks" / "current"
            )

            # Load active workflow status if exists
            active_workflow_file = tasks_dir / "active_workflow"
            active_workflow = None
            if active_workflow_file.is_file():
                active_workflow = active_workflow_file.read_text(
                    encoding="utf-8"
                ).strip()

            if workflows_dir.is_dir():
                for workflow_file in sorted(workflows_dir.glob("*.yaml")):
                    if workflow_file.stem == "README":
                        continue

                    try:
                        content = workflow_file.read_text(encoding="utf-8")
                        workflow_data = yaml.safe_load(content)

                        # Validate YAML structure
                        if not self._validate_workflow_schema(
                            workflow_data, workflow_file
                        ):
                            # Skip malformed workflows
                            continue

                        name = workflow_data.get("name", workflow_file.stem)
                        description = workflow_data.get("description", "")
                        steps = [
                            step.get("name", "")
                            for step in workflow_data.get("steps", [])
                        ]

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
                                started = float(
                                    started_file.read_text(encoding="utf-8").strip()
                                )

                            current_step_file = tasks_dir / "current_step"
                            if current_step_file.is_file():
                                current_step = current_step_file.read_text(
                                    encoding="utf-8"
                                ).strip()

                            # Calculate progress based on current step
                            if current_step and steps:
                                try:
                                    step_index = steps.index(current_step)
                                    progress = int((step_index / len(steps)) * 100)
                                except ValueError:
                                    progress = 0

                        workflows.append(
                            WorkflowInfo(
                                name=name,
                                description=description,
                                status=status,
                                progress=progress,
                                started=started,
                                steps=steps,
                                current_step=current_step,
                                file_path=workflow_file,
                            )
                        )

                    except Exception:
                        # Skip malformed workflows
                        continue

        except Exception as e:
            self.status_message = f"Error loading workflows: {e}"

        self.workflows = workflows
        if hasattr(self, "metrics_collector"):
            running = sum(1 for w in workflows if w.status == "running")
            self.metrics_collector.record("workflows_running", float(running))

    def load_worktrees(self) -> None:
        """Load git worktrees for the current repository."""
        try:
            repo_root, worktrees, error = worktree_discover()
            self.worktrees = worktrees
            self.worktree_repo_root = repo_root
            self.worktree_error = error
            base_dir, base_source, base_error = worktree_get_base_dir()
            self.worktree_base_dir = base_dir
            self.worktree_base_source = base_source
            if error:
                self.status_message = f"Worktrees: {error}"
            elif base_error:
                self.status_message = f"Worktrees: {base_error}"
            else:
                base_hint = ""
                if base_dir:
                    base_hint = f" (base: {base_dir}"
                    if base_source:
                        base_hint += f" · {base_source}"
                    base_hint += ")"
                self.status_message = f"Loaded {len(worktrees)} worktrees{base_hint}"
        except Exception as e:
            self.worktrees = []
            self.worktree_repo_root = None
            self.worktree_error = f"Failed to load worktrees: {e}"
            self.worktree_base_dir = None
            self.worktree_base_source = None
            self.status_message = self.worktree_error

    def load_scenarios(self) -> None:
        """Load scenario metadata and runtime state."""
        scenarios: List[ScenarioInfo] = []
        try:
            claude_dir = _resolve_claude_dir()
            scenarios_dir, state_dir, lock_dir = _ensure_scenarios_dir(claude_dir)
            scenarios_dir = self._validate_path(claude_dir, scenarios_dir)
            state_dir = self._validate_path(claude_dir, state_dir)
            lock_dir = self._validate_path(claude_dir, lock_dir)

            # Cache latest state per scenario (by modification time)
            state_cache: Dict[str, ScenarioRuntimeState] = {}
            state_files = []
            for state_file in state_dir.glob("*.json"):
                try:
                    mtime = state_file.stat().st_mtime
                except OSError:
                    mtime = 0
                state_files.append((mtime, state_file))
            for _mtime, state_file in sorted(state_files, key=lambda x: x[0], reverse=True):
                try:
                    data = json.loads(state_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                scenario_name = str(data.get("scenario") or state_file.stem)
                if scenario_name in state_cache:
                    continue
                state_cache[scenario_name] = {
                    "status": str(data.get("status", "pending")),
                    "started": self._parse_iso_datetime(data.get("started")),
                    "completed": self._parse_iso_datetime(data.get("completed")),
                }

            lock_map: Dict[str, Optional[str]] = {}
            for lock_file in lock_dir.glob("*.lock"):
                try:
                    exec_id = lock_file.read_text(encoding="utf-8").strip() or None
                except OSError:
                    exec_id = None
                lock_map[lock_file.stem] = exec_id

            for scenario_file in sorted(scenarios_dir.glob("*.yaml")):
                if scenario_file.stem == "README":
                    continue

                code, metadata, error_msg = _parse_scenario_metadata(scenario_file)
                if code != 0 or metadata is None:
                    scenarios.append(
                        ScenarioInfo(
                            name=scenario_file.stem,
                            description=error_msg or "Invalid scenario definition",
                            priority="-",
                            scenario_type="invalid",
                            phase_names=[],
                            agents=[],
                            profiles=[],
                            status="invalid",
                            started_at=None,
                            completed_at=None,
                            lock_holder=None,
                            file_path=scenario_file,
                            error=error_msg or "Invalid scenario definition",
                        )
                    )
                    continue

                phase_names = [phase.name for phase in metadata.phases]
                agents: List[str] = []
                profiles: List[str] = []
                for phase in metadata.phases:
                    for agent in phase.agents:
                        if agent not in agents:
                            agents.append(agent)
                    for profile in phase.profiles:
                        if profile not in profiles:
                            profiles.append(profile)

                state_entry = state_cache.get(metadata.name)
                if state_entry is not None:
                    status = state_entry["status"]
                    started_at = state_entry["started"]
                    completed_at = state_entry["completed"]
                else:
                    status = "pending"
                    started_at = None
                    completed_at = None

                lock_key = _scenario_lock_basename(metadata.name)
                lock_holder = lock_map.get(lock_key)
                if lock_holder is not None:
                    status = "running"

                scenarios.append(
                    ScenarioInfo(
                        name=metadata.name,
                        description=metadata.description,
                        priority=metadata.priority,
                        scenario_type=metadata.scenario_type,
                        phase_names=phase_names,
                        agents=agents,
                        profiles=profiles,
                        status=status,
                        started_at=started_at,
                        completed_at=completed_at,
                        lock_holder=lock_holder,
                        file_path=scenario_file,
                    )
                )

        except Exception as exc:  # pragma: no cover - defensive guard
            self.scenarios = []
            self.status_message = f"Error loading scenarios: {exc}"[:160]
            return

        self.scenarios = scenarios
        if hasattr(self, "metrics_collector"):
            self.metrics_collector.record("scenarios_total", float(len(scenarios)))
            running = sum(1 for s in scenarios if s.status == "running")
            self.metrics_collector.record("scenarios_running", float(running))

    def load_profiles(self) -> List[Dict[str, Optional[str]]]:
        """Load available profiles (built-in + saved)."""
        try:
            profiles: List[Dict[str, Optional[str]]] = []
            claude_dir = _resolve_claude_dir()

            for name in BUILT_IN_PROFILES:
                profiles.append(
                    {
                        "name": name,
                        "type": "built-in",
                        "description": PROFILE_DESCRIPTIONS.get(
                            name, "Built-in profile"
                        ),
                        "path": None,
                        "modified": None,
                    }
                )

            profiles_dir = claude_dir / "profiles"
            if profiles_dir.is_dir():
                for profile_file in sorted(profiles_dir.glob("*.profile")):
                    modified_iso = None
                    try:
                        modified_iso = datetime.fromtimestamp(
                            profile_file.stat().st_mtime
                        ).strftime("%Y-%m-%d %H:%M")
                    except OSError:
                        modified_iso = None
                    profiles.append(
                        {
                            "name": profile_file.stem,
                            "type": "saved",
                            "description": "Saved profile snapshot",
                            "path": str(profile_file),
                            "modified": modified_iso,
                        }
                    )

            self.profiles = profiles
            return profiles
        except Exception as exc:
            self.profiles = []
            self.status_message = f"Error loading profiles: {exc}"[:160]
            return []

    def load_mcp_servers(self) -> None:
        """Load MCP server definitions."""
        try:
            success, servers, error = discover_servers()
            if success:
                claude_dir = _resolve_claude_dir()
                doc_only = list_doc_only_servers(
                    {server.name for server in servers}, claude_dir
                )
                combined = servers + doc_only
                combined.sort(key=lambda s: (getattr(s, "doc_only", False), s.name.lower()))
                self.mcp_servers = combined
                self.mcp_error = None
                doc_note = (
                    f" + {len(doc_only)} docs"
                    if doc_only
                    else ""
                )
                self.status_message = f"Loaded {len(servers)} MCP server(s){doc_note}"
            else:
                self.mcp_servers = []
                self.mcp_error = error
                self.status_message = f"Error loading MCP servers: {error}"
        except Exception as exc:
            self.mcp_servers = []
            self.mcp_error = str(exc)
            self.status_message = f"Failed to load MCP servers: {exc}"

    def load_mcp_docs(self) -> None:
        """Load MCP docs from mcp/docs/ with their activation status."""
        try:
            docs: List[MCPDocInfo] = []
            claude_dir = _resolve_claude_dir()
            mcp_docs_dir = claude_dir / "mcp" / "docs"

            # Get active docs from .active-mcp
            active_docs = set(_parse_active_entries(claude_dir / ".active-mcp"))

            if mcp_docs_dir.is_dir():
                for path in _iter_md_files(mcp_docs_dir):
                    name = path.stem
                    status = "active" if name in active_docs else "inactive"

                    # Read description from first paragraph
                    try:
                        content = path.read_text(encoding="utf-8")
                        lines = content.split("\n")
                        description = ""
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                description = line[:100]
                                break
                    except Exception:
                        description = ""

                    docs.append(MCPDocInfo(
                        name=name,
                        status=status,
                        description=description,
                        path=path,
                    ))

            # Sort: active first, then by name
            docs.sort(key=lambda d: (d.status != "active", d.name.lower()))
            self.mcp_docs = docs

            active_count = sum(1 for d in docs if d.status == "active")
            self.status_message = f"Loaded {len(docs)} MCP docs ({active_count} active)"

        except Exception as e:
            self.mcp_docs = []
            self.status_message = f"Error loading MCP docs: {e}"

    def load_assets(self) -> None:
        """Load available assets from the plugin."""
        try:
            self.available_assets = discover_plugin_assets()
            self.claude_directories = find_claude_directories(Path.cwd())

            # Set default target dir (respect explicit scope overrides)
            if self.selected_target_dir is None:
                explicit_scope = os.environ.get("CORTEX_SCOPE")
                explicit_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
                preferred = _resolve_claude_dir() if (explicit_scope or explicit_root) else None
                if preferred is not None:
                    for cd in self.claude_directories:
                        if cd.path.resolve() == preferred.resolve():
                            self.selected_target_dir = cd.path
                            break
                    if self.selected_target_dir is None:
                        self.selected_target_dir = preferred

                if self.selected_target_dir is None:
                    for cd in self.claude_directories:
                        if cd.scope == "global":
                            self.selected_target_dir = cd.path
                            break
                    if self.selected_target_dir is None and self.claude_directories:
                        self.selected_target_dir = self.claude_directories[0].path

            total = sum(len(assets) for assets in self.available_assets.values())
            active_settings = get_settings_path()
            settings_scope = get_settings_scope(active_settings)
            self.status_message = (
                f"Loaded {total} assets from plugin | settings: {settings_scope} "
                f"({active_settings})"
            )
        except Exception as e:
            self.available_assets = {}
            self.claude_directories = []
            self.status_message = f"Failed to load assets: {e}"

    def load_memory_notes(self) -> None:
        """Load notes from the memory vault."""
        try:
            from ..memory import list_notes, get_vault_stats, NoteType

            notes: List[MemoryNote] = []
            for note_type_enum in NoteType:
                note_list = list_notes(note_type_enum, recent=50)
                note_type = note_type_enum.value
                for n in note_list:
                    notes.append(MemoryNote(
                        title=n.get("name", "Untitled"),
                        note_type=note_type,
                        path=str(n.get("path", "")),
                        modified=n.get("modified", datetime.now()),
                        tags=n.get("tags", []),
                        snippet=n.get("snippet", "")[:100],
                    ))

            # Sort by modified date, newest first
            notes.sort(key=lambda n: n.modified, reverse=True)
            self.memory_notes = notes

            stats = get_vault_stats()
            total = stats.get("total_notes", len(notes))
            self.status_message = f"Loaded {total} memory notes"
        except Exception as e:
            self.memory_notes = []
            self.status_message = f"Failed to load memory: {e}"

    def update_view(self) -> None:
        """Update the table based on current view."""
        switcher = self.query_one("#view-switcher", ContentSwitcher)
        table = self.query_one("#main-table", DataTable)
        table.clear(columns=True)
        self._apply_view_title(table, self.current_view)

        if self.current_view == "galaxy":
            switcher.current = "galaxy-view"
            self.show_galaxy_view()
            return

        switcher.current = "main-table"

        if self.wizard_active:
            # When wizard is active, we don't use the DataTable, we use a Static panel
            # but we can also just overlay it. For now, let's update a dedicated wizard area or overview.
            # However, looking at the mixin, it returns a Panel. 
            # We'll update the switcher to a wizard-view if it exists, or just hijack overview.
            table.add_column("Wizard")
            # This is a bit of a hack to render the Panel into the table area
            # In a real Textual app we'd use a proper Screen or View
            table.add_row(self.render_wizard_view())
            return

        if self.current_view == "overview":
            self.show_overview(table)
            return

        if self.current_view == "agents":
            self.show_agents_view(table)
        elif self.current_view == "principles":
            self.show_principles_view(table)
        elif self.current_view == "rules":
            self.show_rules_view(table)
        elif self.current_view == "modes":
            self.show_modes_view(table)
        elif self.current_view == "prompts":
            self.show_prompts_view(table)
        elif self.current_view == "skills":
            self.show_skills_view(table)
        elif self.current_view == "commands":
            self.show_commands_view(table)
        elif self.current_view == "workflows":
            self.show_workflows_view(table)
        elif self.current_view == "worktrees":
            self.show_worktrees_view(table)
        elif self.current_view == "scenarios":
            self.show_scenarios_view(table)
        elif self.current_view == "orchestrate":
            self.show_orchestrate_view(table)
        elif self.current_view == "mcp":
            self.show_mcp_view(table)
        elif self.current_view == "profiles":
            self._render_profiles_table(table)
        elif self.current_view == "export":
            self._render_export_table(table)
        elif self.current_view == "ai_assistant":
            self.show_ai_assistant_view(table)
        elif self.current_view == "flags":
            self.show_flags_view(table)
        elif self.current_view == "flag_manager":
            self.show_flag_manager_view(table)
        elif self.current_view == "tasks":
            self.show_tasks_view(table)
        elif self.current_view == "assets":
            self.show_assets_view(table)
        elif self.current_view == "memory":
            self.show_memory_view(table)
        elif self.current_view == "watch_mode":
            self._render_watch_mode_view()
        else:
            table.add_column("Message")
            table.add_row(f"{self.current_view.title()} view coming soon")

    def _apply_view_title(self, table: AnyDataTable, view: str) -> None:
        """Set border title on the main data table for the active view."""
        title = VIEW_TITLES.get(view, view.replace("_", " ").title())
        try:
            table.border_title = title
        except Exception:
            pass

    def show_agents_view(self, table: AnyDataTable) -> None:
        """Show agents table with enhanced colors and formatting."""
        table.add_column("Name", key="name", width=35)
        table.add_column("Status", key="status", width=12)
        table.add_column("Category", key="category", width=20)
        table.add_column("Tier", key="tier", width=15)

        if not hasattr(self, "agents") or not self.agents:
            table.add_row("[dim]No agents found[/dim]", "", "", "")
            return

        tier_colors = {
            "essential": "bold green",
            "standard": "cyan",
            "premium": "yellow",
            "experimental": "magenta",
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

    def show_tasks_view(self, table: AnyDataTable) -> None:
        """Show task management table."""
        table.add_column("Task", key="task", width=30)
        table.add_column("Category", key="category", width=16)
        table.add_column("Workstream", key="workstream", width=16)
        table.add_column("Status", key="status", width=12)
        table.add_column("Progress", key="progress", width=12)
        table.add_column("Started", key="started", width=18)
        table.add_column("Details", key="details", width=48)

        tasks = getattr(self, "agent_tasks", [])
        if not tasks:
            table.add_row("[dim]No tasks yet[/dim]", "", "", "", "", "", "")
            table.add_row("[dim]Press A to add a task[/dim]", "", "", "", "", "", "")
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

            details_text = (
                Format.truncate(task.description, 90)
                if task.description
                else "[dim]No details[/dim]"
            )

            table.add_row(
                f"{Icons.CODE} {task.agent_name}",
                self._format_category(task.category or task.workstream),
                task.workstream,
                status_icon,
                progress_bar,
                started_text,
                details_text,
            )

    def show_flags_view(self, table: AnyDataTable) -> None:
        """Show flags explorer with categories and descriptions."""
        # Parse flag definitions from flags/
        flags_data = self._parse_flags_md()

        # Refresh categories dynamically based on discovered flags
        if flags_data:
            self._refresh_flag_categories(flags_data)

        if not flags_data:
            table.add_column("Message")
            table.add_row("[dim]No flags found[/dim]")
            table.add_row("[dim]Check flags/ directory or FLAGS.md references[/dim]")
            return

        # Category colors
        category_colors = {
            "Mode Activation": "cyan",
            "MCP Server": "magenta",
            "Thinking Budget": "yellow",
            "Analysis Depth": "green",
            "Auto-Escalation": "red",
            "Execution Control": "blue",
            "Output Optimization": "white",
            "Visual Excellence": "bold magenta",
        }

        # Filter by category and enabled state
        if self.current_flag_category != "all":
            # Show specific category (regardless of enabled state when viewing it directly)
            filtered_flags = [f for f in flags_data if f["category"] == self.current_flag_category]
        else:
            # In "All" view, only show flags from enabled categories
            filtered_flags = [
                f for f in flags_data
                if self.flag_categories_enabled.get(f["category"], True)
            ]

        # Add header row showing category navigation
        table.add_column("Flag", key="flag", width=32)
        table.add_column("Category", key="category", width=20)
        table.add_column("Trigger/Purpose", key="trigger", width=50)
        table.add_column("Behavior", key="behavior", width=45)

        # Add category selector as first row
        category_display = self._format_flag_categories(category_colors)
        enabled_count = sum(1 for enabled in self.flag_categories_enabled.values() if enabled)
        table.add_row(
            f"[bold]Category:[/bold]",
            category_display,
            f"[dim]← → navigate | [space] toggle[/dim]",
            f"[dim]Showing {len(filtered_flags)}/{len(flags_data)} flags ({enabled_count} categories enabled)[/dim]",
        )

        # Add separator
        table.add_row("─" * 30, "─" * 18, "─" * 48, "─" * 43)

        if not filtered_flags:
            table.add_row("[dim]No flags in this category[/dim]", "", "", "")
            return

        for flag_info in filtered_flags:
            flag_name = flag_info["name"]
            category = flag_info["category"]
            trigger = flag_info["trigger"]
            behavior = flag_info["behavior"]

            # Color-coded category
            cat_color = category_colors.get(category, "white")
            category_text = f"[{cat_color}]{category}[/{cat_color}]"

            # Format flag name
            flag_text = f"[bold cyan]{flag_name}[/bold cyan]"

            # Truncate long descriptions
            trigger_text = Format.truncate(trigger, 90)
            behavior_text = Format.truncate(behavior, 85)

            table.add_row(
                flag_text,
                category_text,
                f"[dim]{trigger_text}[/dim]",
                behavior_text,
            )

    def _format_flag_categories(self, category_colors: Dict[str, str]) -> str:
        """Format category selector with current selection highlighted."""
        parts = []
        for i, cat in enumerate(self.flag_categories):
            if cat == "all":
                display = "All"
                color = "white"
            else:
                display = cat
                color = category_colors.get(cat, "white")
                # Add enabled/disabled indicator
                is_enabled = self.flag_categories_enabled.get(cat, True)
                indicator = "✓" if is_enabled else "✗"
                display = f"{indicator} {display}"

            if cat == self.current_flag_category:
                # Highlight current category
                parts.append(f"[bold {color} on black]▸ {display} ◂[/bold {color} on black]")
            else:
                if cat != "all" and not self.flag_categories_enabled.get(cat, True):
                    # Dim disabled categories
                    parts.append(f"[dim strikethrough]{display}[/dim strikethrough]")
                else:
                    parts.append(f"[dim]{display}[/dim]")

        return " | ".join(parts)

    def _refresh_flag_categories(self, flags_data: List[Dict[str, str]]) -> None:
        """Update categories list based on parsed flags."""
        categories = sorted({f["category"] for f in flags_data if f.get("category")})
        self.flag_categories = ["all"] + categories

        enabled_map: Dict[str, bool] = {}
        for cat in categories:
            enabled_map[cat] = self.flag_categories_enabled.get(cat, True)
        self.flag_categories_enabled = enabled_map

        if self.current_flag_category not in self.flag_categories:
            self.current_flag_category = "all"

    def _parse_flags_md(self) -> List[Dict[str, str]]:
        """Parse flag files from flags/ (or resolve @flags references in FLAGS.md)."""
        base_dir = self._flag_manager_base_dir()
        claude_dir = base_dir
        possible_flags_md: List[Path] = []
        if claude_dir:
            possible_flags_md.append(claude_dir / "FLAGS.md")
            possible_flags_md.append(claude_dir.parent / "FLAGS.md")
        if Path.cwd() not in (claude_dir, claude_dir.parent):
            possible_flags_md.append(Path.cwd() / "FLAGS.md")
        flags_md_path = next((p for p in possible_flags_md if p.exists()), None)

        possible_flags_dirs: List[Path] = []
        if claude_dir:
            possible_flags_dirs.append(claude_dir / "flags")
            possible_flags_dirs.append(claude_dir.parent / "flags")
        if Path.cwd() not in (claude_dir, claude_dir.parent):
            possible_flags_dirs.append(Path.cwd() / "flags")
        flags_dir = next((p for p in possible_flags_dirs if p.exists()), None)

        flag_files: List[Path] = []
        if flags_dir and flags_dir.exists():
            flag_files = sorted(flags_dir.glob("*.md"))
        elif flags_md_path and flags_md_path.exists():
            candidate_dir = flags_md_path.parent / "flags"
            if candidate_dir.exists():
                flag_files = sorted(candidate_dir.glob("*.md"))

        if not flag_files and flags_md_path and flags_md_path.exists():
            # Fallback for legacy monolithic FLAGS.md
            try:
                content = flags_md_path.read_text(encoding="utf-8")
            except Exception:
                return []
            return self._parse_legacy_flags_md(content)

        flags: List[Dict[str, str]] = []
        for flag_file in flag_files:
            try:
                content = flag_file.read_text(encoding="utf-8")
            except Exception:
                continue

            category = ""
            for line in content.splitlines():
                if line.startswith("# "):
                    category = line[2:].strip()
                    break
            if category.endswith(" Flags"):
                category = category.replace(" Flags", "").strip()
            if not category:
                category = flag_file.stem.replace("-", " ").title()

            lines = content.split("\n")
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith("**--"):
                    flag_match = line.split("**")[1] if "**" in line else ""
                    flag_name = flag_match.strip()

                    trigger = ""
                    behavior = ""
                    j = i + 1

                    while j < len(lines) and not lines[j].strip().startswith("**--"):
                        subline = lines[j].strip()
                        if subline.startswith("- Trigger:"):
                            trigger = subline.replace("- Trigger:", "").strip()
                        elif subline.startswith("- Behavior:"):
                            behavior = subline.replace("- Behavior:", "").strip()
                        elif subline.startswith("- Purpose:"):
                            trigger = subline.replace("- Purpose:", "").strip()
                        j += 1

                    if flag_name:
                        flags.append({
                            "name": flag_name,
                            "category": category,
                            "trigger": trigger or "See documentation",
                            "behavior": behavior or "See documentation",
                        })

                    i = j
                    continue

                i += 1

        return flags

    def _parse_legacy_flags_md(self, content: str) -> List[Dict[str, str]]:
        """Parse legacy monolithic FLAGS.md content."""
        flags: List[Dict[str, str]] = []
        current_category = ""
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if line.startswith("## ") and "Flags" in line:
                current_category = line[3:].replace(" Flags", "").strip()
                i += 1
                continue

            if line.startswith("**--"):
                flag_match = line.split("**")[1] if "**" in line else ""
                flag_name = flag_match.strip()

                trigger = ""
                behavior = ""
                j = i + 1

                while j < len(lines) and not lines[j].startswith("**--") and not lines[j].startswith("## "):
                    subline = lines[j].strip()
                    if subline.startswith("- Trigger:"):
                        trigger = subline.replace("- Trigger:", "").strip()
                    elif subline.startswith("- Behavior:"):
                        behavior = subline.replace("- Behavior:", "").strip()
                    elif subline.startswith("- Purpose:"):
                        trigger = subline.replace("- Purpose:", "").strip()
                    j += 1

                if flag_name:
                    flags.append({
                        "name": flag_name,
                        "category": current_category,
                        "trigger": trigger or "See documentation",
                        "behavior": behavior or "See documentation",
                    })

                i = j
                continue

            i += 1

        return flags

    def show_principles_view(self, table: AnyDataTable) -> None:
        """Show principles snippets view."""
        table.add_column("Snippet", key="name", width=24)
        table.add_column("Status", key="status", width=12)
        table.add_column("Summary", key="summary")
        table.add_column("Source", key="source", width=36)

        if not hasattr(self, "principles") or not self.principles:
            table.add_row("[dim]No principles found[/dim]", "", "", "")
            table.add_row(
                "[dim]Add snippets under principles/[/dim]",
                "",
                "",
                "",
            )
            return

        claude_dir = _resolve_claude_dir()

        def _relpath(path: Path) -> str:
            try:
                return path.relative_to(claude_dir).as_posix()
            except ValueError:
                return path.as_posix()

        for snippet in self.principles:
            if snippet.status == "active":
                status_text = "[bold green]● ACTIVE[/bold green]"
                name = f"[bold]{Icons.DOC} {snippet.name}[/bold]"
            else:
                status_text = "[dim]○ inactive[/dim]"
                name = f"[dim]{Icons.DOC} {snippet.name}[/dim]"

            summary_parts = [snippet.title] if snippet.title else []
            if snippet.description and snippet.description != snippet.title:
                summary_parts.append(snippet.description)
            summary_text = " — ".join(summary_parts) if summary_parts else "Snippet"
            summary_text = Format.truncate(summary_text, 140).replace("[", "\\[")
            summary = f"[dim]{summary_text}[/dim]"
            source = f"[dim]{Format.truncate(_relpath(snippet.path), 60)}[/dim]"

            table.add_row(name, status_text, summary, source)

    def show_rules_view(self, table: AnyDataTable) -> None:
        """Show rules table with enhanced colors."""
        table.add_column("Name", key="name", width=25)
        table.add_column("Status", key="status", width=12)
        table.add_column("Category", key="category", width=15)
        table.add_column("Description", key="description")
        table.add_column("Source", key="source", width=36)

        if not hasattr(self, "rules") or not self.rules:
            table.add_row("[dim]No rules found[/dim]", "", "", "", "")
            return

        category_colors = {
            "execution": "cyan",
            "quality": "green",
            "workflow": "yellow",
            "parallel": "magenta",
            "efficiency": "blue",
        }

        claude_dir = _resolve_claude_dir()
        def _relpath(path: Path) -> str:
            try:
                return path.relative_to(claude_dir).as_posix()
            except ValueError:
                return path.as_posix()

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

            # Truncate description but show more characters - escape Rich markup
            desc_text = Format.truncate(rule.description, 120).replace("[", "\\[")
            description = f"[dim]{desc_text}[/dim]"

            source = f"[dim]{Format.truncate(_relpath(rule.path), 60)}[/dim]"

            table.add_row(
                name,
                status_text,
                category_text,
                description,
                source,
            )

    def show_modes_view(self, table: AnyDataTable) -> None:
        """Show modes table with enhanced colors."""
        table.add_column("Name", key="name", width=30)
        table.add_column("Status", key="status", width=12)
        table.add_column("Purpose", key="purpose")
        table.add_column("Source", key="source", width=36)

        # Debug logging
        has_modes_attr = hasattr(self, "modes")
        modes_value = getattr(self, "modes", None)
        modes_count = len(modes_value) if modes_value else 0
        print(f"[DEBUG] show_modes_view: has_attr={has_modes_attr}, modes={modes_value is not None}, count={modes_count}")

        if not hasattr(self, "modes") or not self.modes:
            table.add_row("[dim]No modes found[/dim]", "", "", "")
            return

        claude_dir = _resolve_claude_dir()
        def _relpath(path: Path) -> str:
            try:
                return path.relative_to(claude_dir).as_posix()
            except ValueError:
                return path.as_posix()

        for mode in self.modes:
            # Color-coded status (match rules view styling)
            if mode.status == "active":
                status_text = f"[bold green]● ACTIVE[/bold green]"
                name = f"[bold]{Icons.FILTER} {mode.name}[/bold]"
            else:
                status_text = f"[dim]○ inactive[/dim]"
                name = f"[dim]{Icons.FILTER} {mode.name}[/dim]"

            # Show more of the purpose - escape Rich markup characters
            purpose_text = Format.truncate(mode.purpose, 150).replace("[", "\\[")
            purpose = f"[dim italic]{purpose_text}[/dim italic]"

            source = f"[dim]{Format.truncate(_relpath(mode.path), 60)}[/dim]"

            table.add_row(
                name,
                status_text,
                purpose,
                source,
            )

    def show_prompts_view(self, table: AnyDataTable) -> None:
        """Show prompts table with categories and status."""
        table.add_column("Name", key="name", width=25)
        table.add_column("Category", key="category", width=15)
        table.add_column("Tokens", key="tokens", width=10)
        table.add_column("Status", key="status", width=12)
        table.add_column("Description", key="description")

        if not hasattr(self, "prompts") or not self.prompts:
            table.add_row(
                "[dim]No prompts found[/dim]",
                "",
                "",
                "",
                "[dim]Create prompts in ~/.cortex/prompts/[/dim]",
            )
            return

        for prompt in self.prompts:
            # Color-coded status
            if prompt.status == "active":
                status_text = f"[bold green]● ACTIVE[/bold green]"
                name = f"[bold]{Icons.DOCUMENT} {prompt.name}[/bold]"
            else:
                status_text = f"[dim]○ inactive[/dim]"
                name = f"[dim]{Icons.DOCUMENT} {prompt.name}[/dim]"

            category = f"[cyan]{prompt.category}[/cyan]" if prompt.category else "[dim]—[/dim]"
            tokens = f"[dim]~{prompt.tokens}[/dim]" if prompt.tokens else "[dim]—[/dim]"
            description = Format.truncate(prompt.description, 60).replace("[", "\\[")

            table.add_row(
                name,
                category,
                tokens,
                status_text,
                f"[dim italic]{description}[/dim italic]",
            )

    def show_overview(self, table: AnyDataTable) -> None:
        """Show overview with high-energy ASCII dashboard."""
        table.add_column("Dashboard", key="dashboard")

        active_agents = sum(
            1 for a in getattr(self, "agents", []) if a.status == "active"
        )
        total_agents = len(getattr(self, "agents", []))
        active_modes = sum(
            1 for m in getattr(self, "modes", []) if m.status == "active"
        )
        total_modes = len(getattr(self, "modes", []))
        active_rules = sum(
            1 for r in getattr(self, "rules", []) if r.status == "active"
        )
        total_rules = len(getattr(self, "rules", []))
        total_skills = len(getattr(self, "skills", []))
        running_workflows = sum(
            1 for w in getattr(self, "workflows", []) if w.status == "running"
        )
        flags_active, flags_total, flags_stats = self._get_flags_summary()

        def add_multiline(content: str) -> None:
            for line in content.split("\n"):
                table.add_row(line)

        hero = EnhancedOverview.create_hero_banner(active_agents, total_agents)
        add_multiline(hero)
        claude_home = getattr(self, "claude_home", _resolve_claude_dir())
        table.add_row(f"[bold cyan]Claude directory[/bold cyan]: [dim]{claude_home}[/dim]")
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
            flags_active,
            flags_total,
        )
        add_multiline(metrics_grid)
        table.add_row("")

        timeline = EnhancedOverview.create_activity_timeline()
        add_multiline(timeline)
        table.add_row("")

        health = EnhancedOverview.create_system_health()
        add_multiline(health)

        if hasattr(self, "performance_monitor"):
            table.add_row("")
            table.add_row("[bold cyan]⚡ Performance Monitor[/bold cyan]")
            table.add_row(self.performance_monitor.get_status_bar(compact=False))

        # Token usage section
        try:
            category_stats, total_stats = get_active_context_tokens()
            table.add_row("")
            combined_total = total_stats + flags_stats
            token_display = EnhancedOverview.create_token_usage(
                category_stats,
                combined_total,
                flags_stats=flags_stats,
            )
            add_multiline(token_display)
        except Exception:
            pass  # Silently skip if token counting fails

    def _get_flags_summary(self) -> tuple[int, int, TokenStats]:
        """Get active/total flag counts and token stats for active flags."""
        claude_dir = _resolve_claude_dir()
        flags_dir = claude_dir / "flags"
        flags_md = claude_dir / "FLAGS.md"

        total_flags = len(list(flags_dir.glob("*.md"))) if flags_dir.exists() else 0
        active_flags: set[str] = set()

        if flags_md.exists():
            try:
                content = flags_md.read_text(encoding="utf-8")
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("@flags/"):
                        name = stripped.replace("@flags/", "").strip()
                        if name:
                            active_flags.add(name)
            except OSError:
                pass

        stats = TokenStats(files=0, chars=0, words=0, tokens=0)
        for name in active_flags:
            if not name.endswith(".md"):
                filename = f"{name}.md"
            else:
                filename = name
            path = flags_dir / filename
            if path.exists():
                stats = stats + count_file_tokens(path)

        return len(active_flags), total_flags, stats

    def _normalize_agent_dependency(self, value: str) -> Optional[str]:
        if not value:
            return None
        key = value.strip().lower()
        if key.endswith(".md"):
            key = key[:-3]
        lookup = getattr(self, "agent_slug_lookup", {})
        return lookup.get(key)

    def _tasks_dir(self) -> Path:
        """Locate the most relevant tasks/current directory.

        Preference order:
        1) Explicit override via CLAUDE_TASKS_HOME (if set)
        2) Primary resolved Claude directory (plugin or ~/.cortex)
        3) Project-local .claude next to the current working directory

        The newest directory that already exists and contains any task files
        (active_agents.json, active_workflow, workflow_status, workflow_started)
        wins. If none exist, we create the primary directory under the resolved Claude directory.
        """

        def candidates() -> list[Path]:
            roots: list[Path] = []
            env_root = os.environ.get("CLAUDE_TASKS_HOME")
            if env_root:
                roots.append(Path(env_root).expanduser())
            roots.append(_resolve_claude_dir())
            roots.append(Path.cwd() / ".claude")
            seen: set[Path] = set()
            uniq: list[Path] = []
            for root in roots:
                if root in seen:
                    continue
                seen.add(root)
                uniq.append(root)
            return [root / "tasks" / "current" for root in uniq]

        task_files = {
            "active_agents.json",
            "active_workflow",
            "workflow_status",
            "workflow_started",
        }

        viable: list[tuple[float, Path]] = []
        for candidate in candidates():
            try:
                validated = self._validate_path(candidate.parents[1], candidate)
            except Exception:
                continue
            if validated.exists():
                try:
                    if any((validated / name).exists() for name in task_files):
                        mtime = max(
                            (validated / name).stat().st_mtime
                            for name in task_files
                            if (validated / name).exists()
                        )
                    else:
                        mtime = validated.stat().st_mtime
                    viable.append((mtime, validated))
                except OSError:
                    continue

        if viable:
            # newest wins
            viable.sort(key=lambda t: t[0], reverse=True)
            return viable[0][1]

        # fallback: create primary under resolved Claude directory
        primary = _resolve_claude_dir() / "tasks" / "current"
        primary.mkdir(parents=True, exist_ok=True)
        return self._validate_path(primary.parents[1], primary)

    def _tasks_file_path(self) -> Path:
        return self._tasks_dir() / "active_agents.json"

    def _build_workflow_task_fallback(self, tasks_dir: Path) -> List[AgentTask]:
        """Generate synthetic tasks from workflow + active project sessions."""
        fallback: List[AgentTask] = []
        active_file = tasks_dir / "active_workflow"
        workflow_name = ""
        if active_file.is_file():
            try:
                workflow_name = active_file.read_text(encoding="utf-8").strip()
            except OSError:
                workflow_name = ""

        workflow_name = workflow_name or "Active Workflow"
        status_file = tasks_dir / "workflow_status"
        try:
            status_raw = status_file.read_text(encoding="utf-8").strip()
        except OSError:
            status_raw = ""

        status_normalized = (status_raw or "running").lower()
        if status_normalized in {"done", "completed"}:
            status_normalized = "complete"

        started_file = tasks_dir / "workflow_started"
        started: Optional[float] = None
        if started_file.is_file():
            try:
                started = float(started_file.read_text(encoding="utf-8").strip())
            except ValueError:
                started = None

        current_step_file = tasks_dir / "current_step"
        try:
            current_step = current_step_file.read_text(encoding="utf-8").strip()
        except OSError:
            current_step = ""

        progress_lookup = {
            "pending": 5,
            "running": 45,
            "paused": 30,
            "complete": 100,
            "error": 0,
        }
        progress = progress_lookup.get(status_normalized, 10)
        display_name = workflow_name
        if current_step:
            display_name = f"{workflow_name} · {current_step}"

        description_bits = [f"Status: {status_normalized.title()}"]
        if current_step:
            description_bits.append(f"Current step: {current_step}")
        if started:
            started_dt = datetime.fromtimestamp(started)
            description_bits.append(f"Started {Format.time_ago(started_dt)}")
        description_text = " • ".join(description_bits)

        fallback.append(
            AgentTask(
                agent_id=f"workflow::{workflow_name.lower().replace(' ', '-')}",
                agent_name=display_name,
                workstream="workflow",
                status=status_normalized,
                progress=progress,
                category="workflow",
                started=started,
                completed=None,
                description=description_text,
                raw_notes=f"Workflow file: {tasks_dir}",
                source_path=str(tasks_dir / "workflow_status"),
            )
        )

        project_tasks = self._collect_project_agent_tasks()
        seen_ids = {task.agent_id for task in fallback}
        for task in project_tasks:
            if task.agent_id in seen_ids:
                continue
            fallback.append(task)
            seen_ids.add(task.agent_id)
        return fallback

    def _collect_project_agent_tasks(self) -> List[AgentTask]:
        """Read recent agent launch logs to synthesize tasks for active projects."""
        claude_dir = _resolve_claude_dir()
        projects_root = claude_dir / "projects"
        if not projects_root.is_dir():
            return []

        agent_files: List[Path] = []
        for project_dir in projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            agent_files.extend(sorted(project_dir.glob("agent-*.jsonl")))

        now = time.time()
        # Sort by modification time (newest first) and limit to avoid heavy parsing
        agent_files = sorted(
            (path for path in agent_files if path.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        tasks: List[AgentTask] = []
        max_files = 40
        max_age_seconds = 24 * 3600
        for path in agent_files[:max_files]:
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if now - mtime > max_age_seconds:
                continue
            try:
                raw = path.read_text(encoding="utf-8").strip()
                if not raw:
                    continue
                record = json.loads(raw)
            except Exception:
                continue

            text_blocks: List[str] = []
            message = record.get("message", {})
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    text_blocks.append(block.get("text", ""))
            if not text_blocks:
                continue
            full_text = "\n".join(text_blocks)
            if "Workstreams" not in full_text:
                continue

            project_tasks = self._parse_workstream_sections(
                full_text, path, record, mtime
            )
            tasks.extend(project_tasks)
            if len(tasks) >= 12:
                break
        return tasks

    def _parse_workstream_sections(
        self, text: str, agent_file: Path, record: Dict[str, Any], mtime: float
    ) -> List[AgentTask]:
        """Extract structured tasks from rich workstream summaries."""
        tasks: List[AgentTask] = []
        workstream_pattern = re.compile(
            r"###\s+\d+\.\s+\*\*(.+?)\*\*\s*\(([^)]+)\)", re.IGNORECASE
        )
        matches = list(workstream_pattern.finditer(text))
        if not matches:
            return tasks

        cwd = record.get("cwd") or record.get("message", {}).get("cwd", "")
        project_name = Path(cwd).name if cwd else "project"

        for idx, match in enumerate(matches):
            name = match.group(1).strip()
            agent_label = match.group(2).strip()
            next_start = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            section_body = text[match.end() : next_start]
            raw_section = section_body.strip()
            description_lines = []
            for line in section_body.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("###"):
                    break
                if stripped.startswith("-") or stripped.startswith("•"):
                    description_lines.append(stripped.lstrip("-• "))
            if description_lines:
                description = "; ".join(description_lines)
            else:
                paragraph_lines = [
                    line.strip()
                    for line in section_body.splitlines()
                    if line.strip() and not line.strip().startswith("###")
                ]
                description = " ".join(paragraph_lines[:2])
            if cwd:
                description = (description + f" • Path: {cwd}").strip()
            description = description.strip()

            heading_meta = f"{name} {agent_label}".lower()
            status = "running"
            if "after" in heading_meta or "pending" in heading_meta:
                status = "pending"

            progress = 60 if status == "running" else 15
            agent_slug = re.sub(r"[^a-z0-9]+", "-", f"{agent_label}-{name}".lower()).strip("-")
            agent_id = f"project::{agent_file.stem}::{agent_slug or 'agent'}"

            tasks.append(
                AgentTask(
                    agent_id=agent_id,
                    agent_name=name,
                    workstream=project_name,
                    status=status,
                    progress=progress,
                    category="workflow",
                    started=mtime if status == "running" else None,
                    completed=None,
                    description=description,
                    raw_notes=raw_section,
                    source_path=str(agent_file),
                )
            )
        return tasks

    def _project_agent_signature(self) -> str:
        claude_dir = _resolve_claude_dir()
        projects_root = claude_dir / "projects"
        if not projects_root.is_dir():
            return "no-projects"

        now = time.time()
        max_age_seconds = 24 * 3600
        records: List[str] = []
        for project_dir in projects_root.iterdir():
            if not project_dir.is_dir():
                continue
            for agent_file in project_dir.glob("agent-*.jsonl"):
                try:
                    mtime = agent_file.stat().st_mtime
                except OSError:
                    continue
                if now - mtime > max_age_seconds:
                    continue
                records.append(f"{project_dir.name}/{agent_file.name}:{mtime}")

        if not records:
            return "no-active-project-agents"

        records.sort()
        return "|".join(records)


    def _compute_tasks_state_signature(self, tasks_dir: Path) -> str:
        """Return a signature tracking relevant workflow/task files."""
        anchors = [
            "active_agents.json",
            "active_workflow",
            "workflow_status",
            "workflow_started",
            "current_step",
        ]
        parts: List[str] = []
        for name in anchors:
            path = tasks_dir / name
            if path.is_file():
                try:
                    parts.append(f"{name}:{path.stat().st_mtime}")
                except OSError:
                    parts.append(f"{name}:err")
            else:
                parts.append(f"{name}:missing")
        parts.append(self._project_agent_signature())
        return "|".join(parts)

    def _poll_tasks_file_changes(self) -> None:
        """Reload tasks when task/workflow state files change on disk."""
        tasks_dir = self._tasks_dir()
        signature = self._compute_tasks_state_signature(tasks_dir)
        if signature == self._tasks_state_signature:
            return

        self.load_agent_tasks()
        if self.current_view in {"tasks", "orchestrate"}:
            self.update_view()

    def _get_agent_category(self, identifier: Optional[str]) -> Optional[str]:
        if not identifier:
            return None
        lookup = getattr(self, "agent_category_lookup", {})
        return lookup.get(identifier.lower())

    def _format_category(self, category: Optional[str]) -> str:
        if not category:
            return "[dim]unknown[/dim]"

        key = category.lower()
        palette = getattr(self, "_dynamic_category_palette", {})
        if key not in palette:
            base_color = self.CATEGORY_PALETTE.get(key)
            if base_color is None:
                fallback_index = getattr(self, "_fallback_category_index", 0)
                if self.CATEGORY_FALLBACK_COLORS:
                    base_color = self.CATEGORY_FALLBACK_COLORS[
                        fallback_index % len(self.CATEGORY_FALLBACK_COLORS)
                    ]
                    self._fallback_category_index = fallback_index + 1
                else:
                    base_color = "white"
            palette[key] = base_color
            self._dynamic_category_palette = palette

        color = palette.get(key, "white")
        return f"[{color}]{category}[/{color}]"

    def _category_badges(self) -> List[str]:
        lookup = getattr(self, "agent_category_lookup", {})
        categories = sorted(set(lookup.values())) if lookup else []
        if not categories:
            return ["[dim]n/a[/dim]"]
        return [self._format_category(cat) for cat in categories[:6]]

    def _generate_task_id(self, name: str) -> str:
        base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "task"
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
                "description": task.description,
                "raw_notes": task.raw_notes,
                "source_path": task.source_path,
            }
        tasks_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _upsert_task(self, agent_id: Optional[str], payload: Dict[str, Any]) -> None:
        tasks = list(getattr(self, "agent_tasks", []))
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
        description = payload.get("description", "") or ""
        description = description.strip()
        raw_notes = payload.get("raw_notes", "") or description

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
                    task.description = description
                    task.raw_notes = raw_notes
                    adjust_times(task)
                    updated = True
                    break
            if not updated:
                tasks.append(
                AgentTask(
                    agent_id=agent_id,
                    agent_name=name,
                    workstream=workstream,
                    status=status,
                    progress=progress,
                    category=category,
                    started=(
                        time.time() if status in ("running", "complete") else None
                    ),
                    completed=time.time() if status == "complete" else None,
                    description=description,
                    raw_notes=raw_notes,
                )
            )
        else:
            new_id = self._generate_task_id(name)
            tasks.append(
                AgentTask(
                    agent_id=new_id,
                    agent_name=name,
                    workstream=workstream,
                    status=status,
                    progress=progress,
                    category=category,
                    started=time.time() if status in ("running", "complete") else None,
                    completed=time.time() if status == "complete" else None,
                    description=description,
                    raw_notes=raw_notes,
                )
            )

        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()

    def _remove_task(self, agent_id: str) -> None:
        tasks = [t for t in getattr(self, "agent_tasks", []) if t.agent_id != agent_id]
        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()

    def _selected_task_index(self) -> Optional[int]:
        if self.current_view != "tasks":
            return None
        tasks = getattr(self, "agent_tasks", [])
        if not tasks:
            return None
        table = self.query_one(DataTable)
        row_value = getattr(table, "cursor_row", None)
        if not isinstance(row_value, int):
            return None
        return min(row_value, len(tasks) - 1)

    def _build_agent_nodes(self) -> List[WorkflowNode]:
        agents = getattr(self, "agents", [])
        if not agents:
            return []

        nodes: List[WorkflowNode] = []
        for agent in agents:
            node_id = agent.slug or agent.name.replace(" ", "-")
            dependencies = []
            for dep in getattr(agent, "requires", []) or []:
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

        active_agents = sum(
            1 for a in getattr(self, "agents", []) if a.status == "active"
        )
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

    def show_workflows_view(self, table: AnyDataTable) -> None:
        """Show workflows table."""
        table.add_column("Name", key="name")
        table.add_column("Status", key="status")
        table.add_column("Progress", key="progress")
        table.add_column("Started", key="started")
        table.add_column("Description", key="description")

        if not hasattr(self, "workflows") or not self.workflows:
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
            description = (
                Format.truncate(workflow.description, 40)
                if workflow.description
                else ""
            )

            # Add icon to name
            name = f"{Icons.PLAY} {workflow.name}"

            table.add_row(
                name,
                status_text,
                progress_text,
                started_text,
                description,
            )

    def show_worktrees_view(self, table: AnyDataTable) -> None:
        """Show git worktrees table."""
        table.add_column("Branch", key="branch", width=24)
        table.add_column("Status", key="status", width=14)
        table.add_column("Path", key="path", width=48)
        table.add_column("HEAD", key="head", width=10)

        if self.worktree_error:
            table.add_row(f"[dim]{self.worktree_error}[/dim]", "", "", "")
            return

        if not hasattr(self, "worktrees") or not self.worktrees:
            table.add_row("[dim]No worktrees found[/dim]", "", "", "")
            return

        repo_root = self.worktree_repo_root

        for worktree in self.worktrees:
            branch = worktree.branch or "detached"
            if worktree.is_main:
                branch = f"[bold]{branch}[/bold] [dim](main)[/dim]"
            elif worktree.branch:
                branch = f"{branch}"
            else:
                branch = f"[dim]{branch}[/dim]"

            status_parts: List[str] = []
            if worktree.detached:
                status_parts.append("detached")
            if worktree.locked:
                status_parts.append("locked")
            if worktree.prunable:
                status_parts.append("prunable")
            status_label = ", ".join(status_parts) if status_parts else "clean"
            status_color = "yellow" if status_parts else "green"
            status = f"[{status_color}]{status_label}[/{status_color}]"

            path_display: str = str(worktree.path)
            if repo_root:
                try:
                    path_display = str(
                        worktree.path.resolve().relative_to(repo_root.resolve())
                    )
                except Exception:
                    path_display = str(worktree.path)

            head = worktree.head[:8] if worktree.head else "-"

            table.add_row(branch, status, path_display, head)

    def show_scenarios_view(self, table: AnyDataTable) -> None:
        """Show scenario catalog."""
        table.add_column("Scenario", key="scenario", width=32)
        table.add_column("Status", key="status", width=14)
        table.add_column("Priority", key="priority", width=12)
        table.add_column("Phases", key="phases", width=18)
        table.add_column("Agents", key="agents", width=24)
        table.add_column("Last Run", key="last_run", width=14)
        table.add_column("Description", key="description")

        scenarios = getattr(self, "scenarios", [])
        if not scenarios:
            table.add_row("[dim]No scenarios found[/dim]", "", "", "", "", "", "")
            table.add_row(
                "[dim]Add YAML files under ~/.cortex/scenarios[/dim]",
                "",
                "",
                "",
                "",
                "",
                "",
            )
            return

        priority_colors = {
            "critical": "red",
            "high": "yellow",
            "medium": "green",
            "normal": "green",
            "low": "cyan",
        }

        for scenario in scenarios:
            icon = Icons.PLAY if scenario.status != "invalid" else Icons.WARNING
            name = f"{icon} {scenario.name}"

            status_key = (scenario.status or "pending").lower()
            if status_key == "running":
                status_text = StatusIcon.running()
            elif status_key in ("completed", "complete", "success"):
                status_text = StatusIcon.active()
            elif status_key in ("failed", "error"):
                status_text = StatusIcon.error()
            elif status_key == "invalid":
                status_text = StatusIcon.warning()
            else:
                status_text = StatusIcon.pending()

            priority_color = priority_colors.get(scenario.priority.lower(), "white")
            priority_text = (
                f"[{priority_color}]{scenario.priority}[/{priority_color}]"
                if scenario.priority and scenario.priority != "-"
                else "[dim]-[/dim]"
            )

            phases_preview = (
                Format.list_items(scenario.phase_names, max_items=2)
                if scenario.phase_names
                else "-"
            )
            phases_text = f"{len(scenario.phase_names)} | {phases_preview}" if scenario.phase_names else "0"

            agents_text = (
                Format.list_items(scenario.agents, max_items=3)
                if scenario.agents
                else "-"
            )

            last_run_text = "-"
            if scenario.completed_at:
                last_run_text = Format.time_ago(scenario.completed_at)
            elif scenario.started_at:
                last_run_text = Format.time_ago(scenario.started_at)

            description = scenario.description or scenario.error or ""
            description = Format.truncate(description, 60) if description else ""

            table.add_row(
                name,
                status_text,
                priority_text,
                phases_text,
                agents_text,
                last_run_text,
                description,
            )

    def show_orchestrate_view(self, table: AnyDataTable) -> None:
        """Show orchestration dashboard with active agents and metrics."""
        table.add_column("Agent", key="agent")
        table.add_column("Category", key="category", width=16)
        table.add_column("Workstream", key="workstream")
        table.add_column("Status", key="status")
        table.add_column("Progress", key="progress")

        tasks = getattr(self, "agent_tasks", [])

        if not tasks:
            # Show example/placeholder data with enhanced visuals
            placeholder_rows = [
                (
                    f"{Icons.CODE} [Agent-1] Implementation",
                    "development",
                    "primary",
                    StatusIcon.running(),
                    75,
                ),
                (
                    f"{Icons.TEST} [Agent-2] Code Review",
                    "quality",
                    "quality",
                    StatusIcon.active(),
                    100,
                ),
                (
                    f"{Icons.TEST} [Agent-3] Test Automation",
                    "testing",
                    "quality",
                    StatusIcon.running(),
                    60,
                ),
                (
                    f"{Icons.DOC} [Agent-4] Documentation",
                    "documentation",
                    "quality",
                    StatusIcon.pending(),
                    0,
                ),
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
            total_progress = (
                sum(t.progress for t in tasks) // len(tasks) if tasks else 0
            )
            running_count = sum(1 for t in tasks if t.status == "running")
            complete_count = sum(1 for t in tasks if t.status == "complete")
            parallel_efficiency = (
                int((running_count / len(tasks)) * 100) if tasks else 0
            )

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
                table.add_row(
                    "Estimated Completion:", "", f"{estimated_minutes}m", "", ""
                )
            else:
                table.add_row("Estimated Completion:", "", "TBD", "", "")

    def show_mcp_view(self, table: AnyDataTable) -> None:
        """Show MCP server overview with validation status and MCP docs."""
        table.add_column("Name", width=24)
        table.add_column("Type", width=10)
        table.add_column("Status", width=12)
        table.add_column("Details", width=30)
        table.add_column("Notes")

        # Show MCP Docs section first (these control CLAUDE.md inclusion)
        mcp_docs = getattr(self, "mcp_docs", [])
        if mcp_docs:
            table.add_row(
                "[bold cyan]📚 MCP Documentation[/bold cyan]",
                "",
                "",
                "[dim]Controls CLAUDE.md inclusion[/dim]",
                "[dim]Space=Toggle[/dim]",
            )
            for doc in mcp_docs:
                if doc.status == "active":
                    status_text = "[bold green]● ACTIVE[/bold green]"
                    name = f"[bold]{Icons.DOC} {doc.name}[/bold]"
                else:
                    status_text = "[dim]○ inactive[/dim]"
                    name = f"[dim]{Icons.DOC} {doc.name}[/dim]"

                table.add_row(
                    name,
                    "[cyan]doc[/cyan]",
                    status_text,
                    Format.truncate(doc.description, 30),
                    "",
                )

            # Separator
            table.add_row("", "", "", "", "")

        # Show MCP Servers section
        if self.mcp_error:
            table.add_row(
                "[red]Error[/red]", "", "", Format.truncate(self.mcp_error, 40), ""
            )
            return

        servers = getattr(self, "mcp_servers", [])
        if servers:
            table.add_row(
                "[bold cyan]🛰 MCP Servers[/bold cyan]",
                "",
                "",
                "[dim]Claude Desktop configuration[/dim]",
                "",
            )
            for server in servers:
                args = " ".join(server.args) if server.args else ""

                if getattr(server, "doc_only", False):
                    details_text = "[dim]Not configured[/dim]"
                    status_text = "[yellow]Docs only[/yellow]"
                    note = server.description or "Add via 'Add MCP'"
                else:
                    details_text = Format.truncate(
                        f"{server.command} {args}".strip(), 30
                    )
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
                    "[magenta]server[/magenta]",
                    status_text,
                    details_text,
                    Format.truncate(note, 40),
                )
        elif not mcp_docs:
            table.add_row("[dim]No MCP servers or docs found[/dim]", "", "", "", "")

    def _split_review_recommendations(
        self, recommendations: List[AgentRecommendation]
    ) -> tuple[List[AgentRecommendation], List[AgentRecommendation]]:
        """Split recommendations into review vs non-review groups."""
        review_agents = {
            "architect-review",
            "code-reviewer",
            "database-optimizer",
            "performance-engineer",
            "quality-engineer",
            "react-specialist",
            "security-auditor",
            "sql-pro",
            "typescript-pro",
            "ui-ux-designer",
        }

        def is_review_rec(rec: AgentRecommendation) -> bool:
            return rec.agent_name in review_agents or "review" in rec.reason.lower()

        review_recs = [rec for rec in recommendations if is_review_rec(rec)]
        other_recs = [rec for rec in recommendations if not is_review_rec(rec)]
        return review_recs, other_recs

    def _resolve_agent_slug(self, name: str) -> str:
        """Resolve a display name to an agent slug if possible."""
        raw = name.strip()
        if not raw:
            return raw
        lookup = getattr(self, "agent_slug_lookup", {})
        if not lookup:
            self.load_agents()
            lookup = getattr(self, "agent_slug_lookup", {})

        key = raw.lower()
        if key in lookup:
            return lookup[key]
        key = key.replace(" ", "-")
        return lookup.get(key, raw)

    def _is_agent_active(self, slug_or_name: str) -> bool:
        agents = getattr(self, "agents", [])
        needle = slug_or_name.lower()
        for agent in agents:
            if agent.slug.lower() == needle or agent.name.lower() == needle:
                return agent.status == "active"
        return False

    def _ensure_agent_active(self, slug_or_name: str) -> bool:
        """Activate agent if inactive. Returns True if active after call."""
        if self._is_agent_active(slug_or_name):
            return True
        exit_code, message = agent_activate(slug_or_name)
        if exit_code != 0:
            clean = self._clean_ansi(message)
            self.notify(
                clean or f"Failed to activate {slug_or_name}",
                severity="error",
                timeout=3,
            )
            return False
        self.load_agents()
        return self._is_agent_active(slug_or_name)

    def _review_output_dir(self) -> Path:
        """Create a timestamped output directory for review runs."""
        tasks_dir = self._tasks_dir()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = tasks_dir / "review-outputs" / stamp
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _llm_output_dir(self) -> Path:
        """Create a timestamped output directory for LLM consult runs."""
        tasks_dir = self._tasks_dir()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_dir = tasks_dir / "llm-outputs" / stamp
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _llm_consult_script_path(self) -> Optional[Path]:
        script_path = (
            Path(__file__).resolve().parents[2]
            / "skills"
            / "multi-llm-consult"
            / "scripts"
            / "consult_llm.py"
        )
        if script_path.exists():
            return script_path
        return None

    def _summarize_prompt(self, prompt: str, max_len: int = 120) -> str:
        cleaned = " ".join(prompt.strip().split())
        if len(cleaned) > max_len:
            return cleaned[: max_len - 1] + "…"
        return cleaned

    def _build_review_prompt(
        self,
        agent_name: str,
        rec: AgentRecommendation,
        context: Optional[SessionContext],
        diff_text: Optional[str] = None,
    ) -> str:
        """Build a review prompt tailored to the recommendation/context."""
        lines = [
            f"You are the {agent_name} reviewer.",
            f"Review the current repository changes. Focus on: {rec.reason}.",
            "Use git diff and inspect relevant files.",
            "Return: Strengths, Issues (Critical/Important/Minor), Fixes, and Approval status.",
        ]

        files_changed: List[str] = []
        if context and getattr(context, "files_changed", None):
            files_changed = list(context.files_changed)

        if files_changed:
            lines.append("")
            lines.append("Changed files:")
            max_files = 30
            for path in files_changed[:max_files]:
                lines.append(f"- {path}")
            if len(files_changed) > max_files:
                lines.append(f"... and {len(files_changed) - max_files} more")

        if diff_text:
            lines.append("")
            lines.append("Git diff (truncated):")
            lines.append("```")
            lines.append(diff_text)
            lines.append("```")

        return "\n".join(lines)

    def _get_git_diff(self, max_chars: int = 40000) -> Optional[str]:
        """Return a combined git diff (staged + unstaged), truncated."""
        try:
            probe = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=False,
                capture_output=True,
                text=True,
            )
            if probe.returncode != 0:
                return None
        except Exception:
            return None

        def run_diff(args: List[str]) -> str:
            result = subprocess.run(
                ["git", "diff", *args],
                check=False,
                capture_output=True,
                text=True,
            )
            return result.stdout or ""

        unstaged = run_diff(["--stat=0"])
        staged = run_diff(["--cached", "--stat=0"])
        if not unstaged and not staged:
            unstaged = run_diff([])
            staged = run_diff(["--cached"])
        else:
            unstaged = run_diff([])
            staged = run_diff(["--cached"])

        combined = []
        if unstaged.strip():
            combined.append("# Unstaged diff")
            combined.append(unstaged.strip())
        if staged.strip():
            combined.append("# Staged diff")
            combined.append(staged.strip())
        if not combined:
            return None

        text = "\n\n".join(combined)
        if len(text) > max_chars:
            return text[:max_chars] + "\n...[truncated]"
        return text

    def _update_review_task_status(
        self,
        task_id: str,
        *,
        status: str,
        progress: int,
        source_path: Optional[Path] = None,
        note: Optional[str] = None,
    ) -> None:
        tasks_file = self._tasks_file_path()
        if not tasks_file.exists():
            return

        try:
            payload = json.loads(tasks_file.read_text(encoding="utf-8"))
        except Exception:
            return

        task = payload.get(task_id)
        if not isinstance(task, dict):
            return

        task["status"] = status
        task["progress"] = progress
        if status in {"running"} and not task.get("started"):
            task["started"] = time.time()
        if status in {"complete", "error"}:
            task["completed"] = time.time()

        if source_path is not None:
            task["source_path"] = str(source_path)

        if note:
            existing_notes = task.get("raw_notes") or task.get("description") or ""
            combined = f"{existing_notes}\n{note}".strip()
            task["raw_notes"] = combined
            if not task.get("description"):
                task["description"] = note

        tasks_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _spawn_review_cli_task(
        self,
        *,
        task_id: str,
        agent_name: str,
        prompt: str,
        output_path: Path,
    ) -> None:
        """Run a Claude CLI review for a single agent and update task status."""
        error_path = output_path.with_suffix(".err.txt")

        def runner() -> None:
            cmd = [
                "claude",
                "--agent",
                agent_name,
                "--print",
                "--output-format",
                "text",
                prompt,
            ]
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with output_path.open("w", encoding="utf-8") as out, error_path.open(
                    "w", encoding="utf-8"
                ) as err:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=str(Path.cwd()),
                        stdout=out,
                        stderr=err,
                        text=True,
                    )
                    rc = proc.wait()
            except FileNotFoundError:
                error_path.write_text("Claude CLI not found.", encoding="utf-8")
                self._update_review_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"CLI not found. See {error_path.name}.",
                )
                return
            except Exception as exc:
                error_path.write_text(str(exc), encoding="utf-8")
                self._update_review_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"Review failed. See {error_path.name}.",
                )
                return

            if rc == 0:
                self._update_review_task_status(
                    task_id,
                    status="complete",
                    progress=100,
                    source_path=output_path,
                )
            else:
                self._update_review_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"Review exited with code {rc}. See {error_path.name}.",
                )

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    def _update_llm_task_status(
        self,
        task_id: str,
        *,
        status: str,
        progress: int,
        source_path: Optional[Path] = None,
        note: Optional[str] = None,
    ) -> None:
        tasks_file = self._tasks_file_path()
        if not tasks_file.exists():
            return

        try:
            payload = json.loads(tasks_file.read_text(encoding="utf-8"))
        except Exception:
            return

        task = payload.get(task_id)
        if not isinstance(task, dict):
            return

        task["status"] = status
        task["progress"] = progress
        if status in {"running"} and not task.get("started"):
            task["started"] = time.time()
        if status in {"complete", "error"}:
            task["completed"] = time.time()

        if source_path is not None:
            task["source_path"] = str(source_path)

        if note:
            existing_notes = task.get("raw_notes") or task.get("description") or ""
            combined = f"{existing_notes}\n{note}".strip()
            task["raw_notes"] = combined
            if not task.get("description"):
                task["description"] = note

        tasks_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _spawn_llm_consult_task(
        self,
        *,
        task_id: str,
        provider_key: str,
        purpose: str,
        prompt: str,
        output_path: Path,
        script_path: Path,
        context_file: Optional[Path],
    ) -> None:
        """Run a multi-LLM consult script and update task status."""
        error_path = output_path.with_suffix(".err.txt")

        def runner() -> None:
            cmd = [
                sys.executable,
                str(script_path),
                "--provider",
                provider_key,
                "--purpose",
                purpose,
                "--prompt",
                prompt,
            ]
            if context_file is not None:
                cmd += ["--context-file", str(context_file)]

            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with output_path.open("w", encoding="utf-8") as out, error_path.open(
                    "w", encoding="utf-8"
                ) as err:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=str(Path.cwd()),
                        stdout=out,
                        stderr=err,
                        text=True,
                    )
                    rc = proc.wait()
            except FileNotFoundError:
                error_path.write_text("LLM consult script not found.", encoding="utf-8")
                self._update_llm_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"Consult script not found. See {error_path.name}.",
                )
                return
            except Exception as exc:
                error_path.write_text(str(exc), encoding="utf-8")
                self._update_llm_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"LLM consult failed. See {error_path.name}.",
                )
                return

            if rc == 0:
                self._update_llm_task_status(
                    task_id,
                    status="complete",
                    progress=100,
                    source_path=output_path,
                )
            else:
                self._update_llm_task_status(
                    task_id,
                    status="error",
                    progress=0,
                    source_path=output_path,
                    note=f"LLM consult exited with code {rc}. See {error_path.name}.",
                )

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

    def show_ai_assistant_view(self, table: AnyDataTable) -> None:
        """Show AI assistant recommendations and predictions."""
        table.add_column("Type", key="type", width=14)
        table.add_column("Recommendation", key="recommendation", width=30)
        table.add_column("Conf", key="confidence", width=6)
        table.add_column("Reason", width=45)

        if not hasattr(self, "intelligent_agent"):
            table.add_row(
                "[dim]System[/dim]",
                "[yellow]AI Assistant not initialized[/yellow]",
                "",
                "",
            )
            return

        # Get recommendations
        agent_recommendations = self.intelligent_agent.get_recommendations()

        # Show header
        table.add_row(
            "[bold cyan]🤖 AI Recommendations[/bold cyan]", "", "", ""
        )
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            "",
        )
        table.add_row("", "", "", "")

        if not agent_recommendations:
            table.add_row(
                "[dim]Agent[/dim]",
                "[dim]No recommendations[/dim]",
                "",
                "[dim]Context analysis found no suggestions[/dim]",
            )
        else:
            top_recs = agent_recommendations[:10]
            review_recs, other_recs = self._split_review_recommendations(top_recs)

            if review_recs:
                table.add_row(
                    "[bold cyan]Review Requests[/bold cyan]",
                    f"[dim]{len(review_recs)} reviewers[/dim]",
                    "",
                    "",
                )

            # Show review recommendations
            for rec in review_recs:
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
                    f"[{urgency_color}]{urgency_icon} Review[/{urgency_color}]",
                    f"[bold]{rec.agent_name}[/bold]{auto_text}",
                    confidence_text,
                    f"[dim italic]{rec.reason}[/dim italic]",
                )

            if other_recs:
                table.add_row("", "", "", "")
                table.add_row(
                    "[bold cyan]Other Suggestions[/bold cyan]",
                    f"[dim]{len(other_recs)} items[/dim]",
                    "",
                    "",
                )

            # Show non-review recommendations
            for rec in other_recs:
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
                    f"[dim italic]{rec.reason}[/dim italic]",
                )

        # Show deactivation recommendations
        table.add_row("", "", "", "")
        table.add_row("[bold orange1]⚠ Deactivation Suggestions[/bold orange1]", "", "", "")
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            "",
        )
        table.add_row("", "", "", "")

        # Get active agents from profiles
        active_agents = []
        if hasattr(self, "profiles_manager") and self.profiles_manager:
            active_agents = self.profiles_manager.get_active_agents()

        if active_agents:
            deactivation_recs = self.intelligent_agent.get_deactivation_recommendations(
                active_agents
            )

            if not deactivation_recs:
                table.add_row(
                    "[dim]Agent[/dim]",
                    "[dim]No deactivation needed[/dim]",
                    "",
                    "[dim]All active agents are relevant to current context[/dim]",
                )
            else:
                # Show deactivation recommendations
                for drec in deactivation_recs[:5]:  # Top 5
                    # Color by urgency
                    if drec.urgency == "high":
                        urgency_color = "orange1"
                        urgency_icon = "🔸"
                    elif drec.urgency == "medium":
                        urgency_color = "yellow"
                        urgency_icon = "🔹"
                    else:
                        urgency_color = "dim"
                        urgency_icon = "⚪"

                    # Color by confidence
                    confidence_pct = int(drec.confidence * 100)
                    if drec.confidence >= 0.8:
                        confidence_text = f"[bold orange1]{confidence_pct}%[/bold orange1]"
                    elif drec.confidence >= 0.6:
                        confidence_text = f"[yellow]{confidence_pct}%[/yellow]"
                    else:
                        confidence_text = f"[dim]{confidence_pct}%[/dim]"

                    # Auto-deactivate indicator
                    auto_text = (
                        " [bold orange1]AUTO[/bold orange1]"
                        if drec.auto_deactivate
                        else ""
                    )

                    # Resource impact indicator
                    resource_text = ""
                    if drec.resource_impact == "high":
                        resource_text = " [red]⚡HIGH[/red]"
                    elif drec.resource_impact == "medium":
                        resource_text = " [yellow]⚡MED[/yellow]"

                    table.add_row(
                        f"[{urgency_color}]{urgency_icon} Agent[/{urgency_color}]",
                        f"[bold]{drec.agent_name}[/bold]{auto_text}{resource_text}",
                        confidence_text,
                        f"[dim italic]{drec.reason}[/dim italic]",
                    )
        else:
            table.add_row(
                "[dim]Agent[/dim]",
                "[dim]No active agents[/dim]",
                "",
                "[dim]Activate agents to see deactivation suggestions[/dim]",
            )

        # Show skill recommendations
        table.add_row("", "", "", "")
        table.add_row("[bold green]✨ Skills[/bold green]", "", "", "")
        table.add_row(
            "[dim]━━━━━━━━━━[/dim]",
            "",
            "",
            "",
        )
        table.add_row("", "", "", "")

        # Get skill recommendations using the recommender directly
        try:
            from .. import skill_recommender

            # Create context from current project
            cwd = Path.cwd()
            python_files = list(cwd.glob("**/*.py"))[:20]

            context = SessionContext(
                files_changed=[str(f.relative_to(cwd)) for f in python_files] if python_files else [],
                file_types={f.suffix for f in python_files} if python_files else set(),
                directories={str(f.parent.relative_to(cwd)) for f in python_files} if python_files else set(),
                has_tests=any('test' in str(f) for f in python_files) if python_files else False,
                has_auth=any('auth' in str(f) for f in python_files) if python_files else False,
                has_api=any('api' in str(f) for f in python_files) if python_files else False,
                has_frontend=(cwd / 'src').exists() or (cwd / 'frontend').exists(),
                has_backend=(cwd / 'backend').exists() or (cwd / 'server').exists(),
                has_database=any('db' in str(f) or 'database' in str(f) for f in python_files) if python_files else False,
                errors_count=0,
                test_failures=0,
                build_failures=0,
                session_start=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
                active_agents=[],
                active_modes=[],
                active_rules=[],
            )

            recommender = skill_recommender.SkillRecommender()
            skill_recommendations = recommender.recommend_for_context(context)

            if skill_recommendations:
                # Show top 5 skill recommendations
                for skill_rec in skill_recommendations[:5]:
                    confidence_pct = int(skill_rec.confidence * 100)

                    # Color by confidence
                    if skill_rec.confidence >= 0.8:
                        confidence_text = f"[bold green]{confidence_pct}%[/bold green]"
                        skill_icon = "✓"
                        skill_color = "green"
                    elif skill_rec.confidence >= 0.6:
                        confidence_text = f"[yellow]{confidence_pct}%[/yellow]"
                        skill_icon = "•"
                        skill_color = "yellow"
                    else:
                        confidence_text = f"[dim]{confidence_pct}%[/dim]"
                        skill_icon = "○"
                        skill_color = "dim"

                    # Auto-activate indicator
                    auto_text = (
                        " [bold cyan]AUTO[/bold cyan]"
                        if skill_rec.auto_activate
                        else ""
                    )

                    table.add_row(
                        f"[{skill_color}]{skill_icon} Skill[/{skill_color}]",
                        f"[bold]{skill_rec.skill_name}[/bold]{auto_text}",
                        confidence_text,
                        f"[dim italic]{skill_rec.reason}[/dim italic]",
                    )
            else:
                table.add_row(
                    "[dim]Skills[/dim]",
                    "[dim]No recommendations[/dim]",
                    "",
                    "[dim]Skills will be recommended based on project context[/dim]",
                )
        except Exception as e:
            table.add_row(
                "[dim]Skills[/dim]",
                f"[red]Error: {str(e)[:30]}[/red]",
                "",
                f"[dim]{type(e).__name__}[/dim]",
            )

        # Show workflow prediction if available
        table.add_row("", "", "", "")
        table.add_row("[bold magenta]🎯 WORKFLOW PREDICTION[/bold magenta]", "", "", "")
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            "",
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
                f"[dim]Based on {workflow.based_on_pattern} pattern[/dim]",
            )

            table.add_row(
                "[cyan]Est. Duration[/cyan]",
                f"[yellow]{workflow.estimated_duration // 60}m {workflow.estimated_duration % 60}s[/yellow]",
                "",
                "",
            )

            table.add_row(
                "[cyan]Success Rate[/cyan]", f"[green]{success_pct}%[/green]", "", ""
            )

            table.add_row("", "", "", "")
            table.add_row("[cyan]Agent Sequence:[/cyan]", "", "", "")

            for i, agent in enumerate(workflow.agents_sequence, 1):
                table.add_row("", f"[dim]{i}.[/dim] {Icons.CODE} {agent}", "", "")
        else:
            table.add_row(
                "[dim]Workflow[/dim]",
                "[dim]Not enough data[/dim]",
                "",
                "[dim italic]Need 3+ similar sessions for prediction[/dim italic]",
            )

        # Show context info
        table.add_row("", "", "", "")
        table.add_row("[bold yellow]📊 CONTEXT ANALYSIS[/bold yellow]", "", "", "")
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            "",
        )
        table.add_row("", "", "", "")

        session_context: Optional[SessionContext] = (
            self.intelligent_agent.current_context
        )
        if session_context:
            table.add_row(
                "[cyan]Files Changed[/cyan]",
                f"{len(session_context.files_changed)}",
                "",
                "",
            )

            # Show detected contexts
            contexts_detected = []
            if session_context.has_frontend:
                contexts_detected.append("[blue]Frontend[/blue]")
            if session_context.has_backend:
                contexts_detected.append("[green]Backend[/green]")
            if session_context.has_database:
                contexts_detected.append("[magenta]Database[/magenta]")
            if session_context.has_tests:
                contexts_detected.append("[yellow]Tests[/yellow]")
            if session_context.has_auth:
                contexts_detected.append("[red]Auth[/red]")
            if session_context.has_api:
                contexts_detected.append("[cyan]API[/cyan]")

            if contexts_detected:
                table.add_row(
                    "[cyan]Detected:[/cyan]", ", ".join(contexts_detected), "", ""
                )

            # Show errors if any
            if (
                session_context.errors_count > 0
                or session_context.test_failures > 0
            ):
                table.add_row(
                    "[red]Issues:[/red]",
                    f"[red]{session_context.errors_count} errors, {session_context.test_failures} test failures[/red]",
                    "",
                    "",
                )

        # Show actions
        table.add_row("", "", "", "")
        table.add_row("[bold green]⚡ QUICK ACTIONS[/bold green]", "", "", "")
        table.add_row(
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            "",
            "",
        )
        table.add_row("", "", "", "")
        table.add_row(
            "",
            "[dim cyan]Press [white]A[/white] → Auto-activate recommended agents[/dim cyan]",
            "",
            "",
        )
        table.add_row(
            "",
            "[dim cyan]Press [white]G[/white] → Consult Gemini[/dim cyan]",
            "",
            "",
        )
        table.add_row(
            "",
            "[dim cyan]Press [white]K[/white] → Assign LLM tasks[/dim cyan]",
            "",
            "",
        )
        table.add_row(
            "",
            "[dim cyan]Press [white]Y[/white] → Request review tasks[/dim cyan]",
            "",
            "",
        )
        table.add_row(
            "",
            "[dim cyan]Press [white]r[/white] → Refresh recommendations[/dim cyan]",
            "",
            "",
        )

    def show_assets_view(self, table: AnyDataTable) -> None:
        """Show available assets for installation."""
        table.add_column("Category", key="category", width=12)
        table.add_column("Name", key="name", width=30)
        table.add_column("Status", key="status", width=15)
        table.add_column("Description", key="description")

        if not self.available_assets:
            table.add_row("[dim]No assets found[/dim]", "", "", "")
            table.add_row(
                "", "[dim]Press r to refresh[/dim]", "", ""
            )
            return

        # Show target directory info
        target_text = str(self.selected_target_dir) if self.selected_target_dir else "Not set"
        table.add_row(
            "[bold cyan]Target[/bold cyan]",
            f"[dim]{target_text}[/dim]",
            "",
            "[dim]Press [white]T[/white] to change target[/dim]",
        )
        table.add_row("", "", "", "")

        # Category colors and icons
        category_config = {
            "hooks": ("📎", "cyan"),
            "commands": ("📝", "green"),
            "agents": ("🤖", "blue"),
            "skills": ("🎯", "yellow"),
            "modes": ("🎨", "magenta"),
            "workflows": ("🔄", "white"),
            "flags": ("🚩", "red"),
            "rules": ("🧭", "bright_blue"),
            "profiles": ("👤", "bright_green"),
            "scenarios": ("🎬", "bright_magenta"),
            "tasks": ("✅", "bright_yellow"),
            "settings": ("⚙️", "bright_cyan"),
        }

        # Render assets by category
        for category_name in ASSET_CATEGORY_ORDER:
            assets = self.available_assets.get(category_name, [])
            if not assets:
                continue

            icon, color = category_config.get(category_name, ("📦", "white"))

            for asset in assets:
                # Check installation status
                if self.selected_target_dir:
                    status = check_installation_status(asset, self.selected_target_dir)
                    if status == InstallStatus.INSTALLED_SAME:
                        status_text = "[green]● Installed[/green]"
                    elif status == InstallStatus.INSTALLED_DIFFERENT:
                        status_text = "[yellow]⚠ Differs[/yellow]"
                    else:
                        status_text = "[dim]○ Available[/dim]"
                else:
                    status_text = "[dim]? Unknown[/dim]"

                # Format name with namespace for commands
                if asset.namespace:
                    name_text = f"{icon} {asset.namespace}:{asset.name}"
                else:
                    name_text = f"{icon} {asset.name}"

                # Truncate description
                desc = Format.truncate(asset.description, 60).replace("[", "\\[")

                table.add_row(
                    f"[{color}]{category_name}[/{color}]",
                    name_text,
                    status_text,
                    f"[dim]{desc}[/dim]",
                )

    def show_memory_view(self, table: AnyDataTable) -> None:
        """Show memory vault notes."""
        table.add_column("Type", key="type", width=12)
        table.add_column("Title", key="title", width=35)
        table.add_column("Modified", key="modified", width=12)
        table.add_column("Tags", key="tags")

        if not self.memory_notes:
            table.add_row("[dim]No notes found[/dim]", "", "", "")
            table.add_row(
                "", "[dim]Use /memory:remember to create notes[/dim]", "", ""
            )
            return

        # Type icons and colors
        type_config = {
            "knowledge": ("📚", "cyan"),
            "projects": ("📁", "green"),
            "sessions": ("📅", "yellow"),
            "fixes": ("🔧", "magenta"),
        }

        for note in self.memory_notes:
            icon, color = type_config.get(note.note_type, ("📄", "white"))

            # Format modified time
            now = datetime.now()
            diff = now - note.modified
            if diff.days > 0:
                modified_text = f"{diff.days}d ago"
            elif diff.seconds >= 3600:
                modified_text = f"{diff.seconds // 3600}h ago"
            elif diff.seconds >= 60:
                modified_text = f"{diff.seconds // 60}m ago"
            else:
                modified_text = "just now"

            # Format tags
            tags_text = " ".join(f"[dim]#{t}[/dim]" for t in note.tags[:3])
            if len(note.tags) > 3:
                tags_text += f" [dim]+{len(note.tags) - 3}[/dim]"

            table.add_row(
                f"[{color}]{icon} {note.note_type}[/{color}]",
                f"{note.title}",
                f"[dim]{modified_text}[/dim]",
                tags_text,
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

    def action_view_principles(self) -> None:
        """Switch to principles view."""
        self.current_view = "principles"
        self.load_principles()
        self.status_message = "Switched to Principles"
        self.notify(f"{Icons.DOC} Principles", severity="information", timeout=1)

    def action_view_skills(self) -> None:
        """Switch to skills view."""
        self.current_view = "skills"
        self.status_message = "Switched to Skills"
        self.notify("💎 Skills", severity="information", timeout=1)

    def action_view_commands(self) -> None:
        """Switch to slash commands view."""
        self.current_view = "commands"
        self.load_slash_commands()
        self.status_message = "Switched to Slash Commands"
        self.notify("⌘ Slash Commands", severity="information", timeout=1)

    def action_view_workflows(self) -> None:
        """Switch to workflows view."""
        self.current_view = "workflows"
        self.status_message = "Switched to Workflows"
        self.notify("🔄 Workflows", severity="information", timeout=1)

    def action_view_worktrees(self) -> None:
        """Switch to worktrees view."""
        self.current_view = "worktrees"
        self.load_worktrees()
        self.status_message = "Switched to Worktrees"
        self.notify("🌿 Worktrees", severity="information", timeout=1)

    def action_view_scenarios(self) -> None:
        """Switch to scenarios view."""
        self.current_view = "scenarios"
        self.load_scenarios()
        self.status_message = "Switched to Scenarios"
        self.notify("🗺 Scenarios", severity="information", timeout=1)

    def action_view_orchestrate(self) -> None:
        """Switch to orchestrate view."""
        self.current_view = "orchestrate"
        self.status_message = "Switched to Orchestrate"
        self.notify("🎯 Orchestrate", severity="information", timeout=1)

    def action_view_mcp(self) -> None:
        """Switch to MCP servers view."""
        self.current_view = "mcp"
        self.load_mcp_servers()
        self.load_mcp_docs()
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
        if hasattr(self, "intelligent_agent"):
            self.intelligent_agent.analyze_context()

    def action_view_assets(self) -> None:
        """Switch to assets view."""
        self.load_assets()
        self.current_view = "assets"
        self.status_message = "Switched to Asset Manager"
        self.notify("📦 Asset Manager", severity="information", timeout=1)

    def action_view_memory(self) -> None:
        """Switch to memory view."""
        self.load_memory_notes()
        self.current_view = "memory"
        self.status_message = "Switched to Memory Vault"
        self.notify("🧠 Memory Vault", severity="information", timeout=1)

    def action_view_watch_mode(self) -> None:
        """Switch to watch mode view."""
        self.current_view = "watch_mode"
        self.status_message = "Switched to Watch Mode"
        self.notify("🔍 Watch Mode", severity="information", timeout=1)

    def action_view_flags(self) -> None:
        """Switch to flags explorer view."""
        self.current_view = "flags"
        self.status_message = "Switched to Flag Explorer"
        self.notify("🚩 Flag Explorer", severity="information", timeout=1)

    def action_cursor_up(self) -> None:
        """Navigate up in lists."""
        if self.wizard_active:
            self._wizard_move_by(-1)
            return
        if self.current_view == "flag_manager":
            self.action_flag_manager_prev()
            return
        table = self._main_table()
        if table:
            table.action_cursor_up()

    def action_cursor_down(self) -> None:
        """Navigate down in lists."""
        if self.wizard_active:
            self._wizard_move_by(1)
            return
        if self.current_view == "flag_manager":
            self.action_flag_manager_next()
            return
        table = self._main_table()
        if table:
            table.action_cursor_down()

    def action_cursor_top(self) -> None:
        """Jump to the top of the current list."""
        if self.wizard_active:
            self._wizard_set_index(0)
            return
        if self.current_view == "flag_manager":
            self._flag_manager_set_index(0)
            return
        table = self._main_table()
        if table and table.row_count > 0:
            table.move_cursor(row=0)

    def action_cursor_bottom(self) -> None:
        """Jump to the bottom of the current list."""
        if self.wizard_active:
            self._wizard_set_index(self._wizard_max_index())
            return
        if self.current_view == "flag_manager":
            if self.flag_files:
                self._flag_manager_set_index(len(self.flag_files) - 1)
            return
        table = self._main_table()
        if table and table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)

    def action_page_up(self) -> None:
        """Move up by one page."""
        if self.wizard_active:
            self._wizard_set_index(0)
            return
        if self.current_view == "flag_manager":
            self._flag_manager_page_move("up")
            return
        self._table_page_move("up")

    def action_page_down(self) -> None:
        """Move down by one page."""
        if self.wizard_active:
            self._wizard_set_index(self._wizard_max_index())
            return
        if self.current_view == "flag_manager":
            self._flag_manager_page_move("down")
            return
        self._table_page_move("down")

    def action_half_page_up(self) -> None:
        """Move up by half a page."""
        if self.wizard_active:
            self._wizard_move_by(self._wizard_half_page_delta() * -1)
            return
        if self.current_view == "flag_manager":
            self._flag_manager_page_move("up", half=True)
            return
        self._table_page_move("up", half=True)

    def action_half_page_down(self) -> None:
        """Move down by half a page."""
        if self.wizard_active:
            self._wizard_move_by(self._wizard_half_page_delta())
            return
        if self.current_view == "flag_manager":
            self._flag_manager_page_move("down", half=True)
            return
        self._table_page_move("down", half=True)

    # ─────────────────────────────────────────────────────────────────────
    # Flags Explorer Actions
    # ─────────────────────────────────────────────────────────────────────

    async def on_key(self, event: events.Key) -> None:
        """Handle key presses for global navigation."""
        if self.wizard_active:
            if event.key == "space":
                self.action_wizard_toggle()
                self.update_view()
                event.prevent_default()
                event.stop()
            elif event.key == "enter":
                self.action_wizard_next()
                self.update_view()
                event.prevent_default()
                event.stop()
            elif event.key == "backspace":
                self.action_wizard_prev()
                self.update_view()
                event.prevent_default()
                event.stop()
            elif event.key == "escape":
                self.wizard_cancel()
                self.update_view()
                event.prevent_default()
                event.stop()
            elif event.key == "up":
                self.action_cursor_up()
                self.update_view()
                event.prevent_default()
                event.stop()
            elif event.key == "down":
                self.action_cursor_down()
                self.update_view()
                event.prevent_default()
                event.stop()
            return

        if self.current_view == "flags":
            if event.key == "left":
                self.action_flag_category_prev()
                event.prevent_default()
                event.stop()
            elif event.key == "right":
                self.action_flag_category_next()
                event.prevent_default()
                event.stop()
            elif event.key == "space":
                self.action_flag_category_toggle()
                event.prevent_default()
                event.stop()
        elif self.current_view == "flag_manager":
            if event.key == "up":
                self.action_flag_manager_prev()
                event.prevent_default()
                event.stop()
            elif event.key == "down":
                self.action_flag_manager_next()
                event.prevent_default()
                event.stop()
            elif event.key == "space":
                self.action_flag_manager_toggle()
                event.prevent_default()
                event.stop()

        if self._text_input_focused():
            return

        if event.key == "g":
            now = time.monotonic()
            if self._vi_g_pending and now <= self._vi_g_deadline:
                self._vi_g_pending = False
                self.action_cursor_top()
            else:
                self._vi_g_pending = True
                self._vi_g_deadline = now + 0.5
            event.prevent_default()
            event.stop()
            return

        if self._vi_g_pending:
            self._vi_g_pending = False

    def action_flag_category_next(self) -> None:
        """Navigate to next flag category."""
        if self.current_view != "flags":
            return
        current_idx = self.flag_categories.index(self.current_flag_category)
        next_idx = (current_idx + 1) % len(self.flag_categories)
        self.current_flag_category = self.flag_categories[next_idx]
        self.update_view()
        category_name = "All Flags" if self.current_flag_category == "all" else self.current_flag_category
        self.status_message = f"Category: {category_name}"

    def action_flag_category_prev(self) -> None:
        """Navigate to previous flag category."""
        if self.current_view != "flags":
            return
        current_idx = self.flag_categories.index(self.current_flag_category)
        prev_idx = (current_idx - 1) % len(self.flag_categories)
        self.current_flag_category = self.flag_categories[prev_idx]
        self.update_view()
        category_name = "All Flags" if self.current_flag_category == "all" else self.current_flag_category
        self.status_message = f"Category: {category_name}"

    def action_flag_category_toggle(self) -> None:
        """Toggle the current flag category on/off."""
        if self.current_view != "flags":
            return

        # Can't toggle "all" category
        if self.current_flag_category == "all":
            self.notify("Cannot toggle 'All' view - toggle individual categories instead", severity="warning", timeout=2)
            return

        # Toggle the current category
        current_state = self.flag_categories_enabled.get(self.current_flag_category, True)
        self.flag_categories_enabled[self.current_flag_category] = not current_state

        new_state = "enabled" if not current_state else "disabled"
        self.update_view()
        self.notify(f"{self.current_flag_category}: {new_state}", severity="information", timeout=2)
        self.status_message = f"{self.current_flag_category}: {new_state}"

    # ─────────────────────────────────────────────────────────────────────
    # Flag Manager Actions
    # ─────────────────────────────────────────────────────────────────────

    def action_view_flag_manager(self) -> None:
        """Switch to flag manager view."""
        self.current_view = "flag_manager"
        self.flag_files = self._load_flag_files_metadata()
        self.selected_flag_index = 0
        self.status_message = "Switched to Flag Manager (Ctrl+G)"
        self.notify("⚙️ Flag Manager", severity="information", timeout=1)

    def show_flag_manager_view(self, table: AnyDataTable) -> None:
        """Show flag manager view for enabling/disabling flag categories."""
        if not self.flag_files:
            self.flag_files = self._load_flag_files_metadata()

        if not self.flag_files:
            table.add_column("Message")
            table.add_row("[dim]No flag files found[/dim]")
            table.add_row("[dim]Check flags/ directory[/dim]")
            return

        # Calculate totals
        total_tokens = sum(f["tokens"] for f in self.flag_files)
        active_tokens = sum(f["tokens"] for f in self.flag_files if f["active"])
        inactive_tokens = total_tokens - active_tokens
        savings_pct = (inactive_tokens / total_tokens * 100) if total_tokens > 0 else 0

        # Add columns
        table.add_column("Status", key="status", width=8)
        table.add_column("Flag Category", key="category", width=30)
        table.add_column("Tokens", key="tokens", width=10)
        table.add_column("File", key="file", width=35)

        # Add header with token summary
        table.add_row(
            "[bold]Summary[/bold]",
            f"[bold cyan]{len([f for f in self.flag_files if f['active']])}/{len(self.flag_files)} active[/bold cyan]",
            f"[bold yellow]{active_tokens}/{total_tokens}[/bold yellow]",
            f"[dim]Saving {savings_pct:.0f}% tokens ({inactive_tokens} tokens)[/dim]",
        )
        table.add_row("─" * 6, "─" * 28, "─" * 8, "─" * 33)

        # Add flag files
        for i, flag_file in enumerate(self.flag_files):
            is_selected = (i == self.selected_flag_index)
            active = flag_file["active"]
            category = flag_file["category"]
            tokens = flag_file["tokens"]
            filename = flag_file["filename"]

            # Status indicator
            if active:
                status = "[green]✓ ON[/green]"
            else:
                status = "[dim]✗ OFF[/dim]"

            # Category text with selection highlight
            if is_selected:
                category_text = f"[bold cyan on black]▸ {category}[/bold cyan on black]"
            else:
                if active:
                    category_text = f"[white]{category}[/white]"
                else:
                    category_text = f"[dim]{category}[/dim]"

            # Tokens
            if active:
                tokens_text = f"[yellow]{tokens}[/yellow]"
            else:
                tokens_text = f"[dim]{tokens}[/dim]"

            # Filename
            if active:
                file_text = f"[dim]{filename}[/dim]"
            else:
                file_text = f"[dim strikethrough]{filename}[/dim strikethrough]"

            table.add_row(status, category_text, tokens_text, file_text)

        # Add footer with instructions
        table.add_row("", "", "", "")
        table.add_row(
            "[dim]Controls:[/dim]",
            "[dim]↑↓ Select[/dim]",
            "[dim]Space Toggle[/dim]",
            "[dim]Changes saved to FLAGS.md[/dim]",
        )

    def _flag_manager_base_dir(self) -> Path:
        """Resolve the base directory for flags (prefer selected target)."""
        if self.selected_target_dir and self.selected_target_dir.exists():
            return self.selected_target_dir
        explicit_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        explicit_scope = os.environ.get("CORTEX_SCOPE")
        if explicit_root or explicit_scope:
            return _resolve_claude_dir()
        return _resolve_cortex_root()

    def _load_flag_files_metadata(self) -> List[Dict[str, Any]]:
        """Load metadata about all flag files and their active status."""
        flag_files = []

        claude_home = self._flag_manager_base_dir()
        flags_dir = claude_home / "flags"
        flags_md_path = claude_home / "FLAGS.md"

        if not flags_dir.exists():
            return []

        # Parse FLAGS.md to see which flags are active
        active_flags = set()
        if flags_md_path.exists():
            try:
                with open(flags_md_path, "r", encoding="utf-8") as f:
                    for line in f:
                        stripped = line.strip()
                        if stripped.startswith("@flags/"):
                            filename = stripped.replace("@flags/", "").strip()
                            if filename:
                                active_flags.add(filename)
            except OSError:
                pass

        # Scan all .md files in flags directory
        for flag_file in sorted(flags_dir.glob("*.md")):
            filename = flag_file.name

            # Parse the file to extract category name and token count
            category_name = filename.replace(".md", "").replace("-", " ").title()
            tokens = 100  # Default

            with open(flag_file, "r") as f:
                content = f.read()
                # Extract category name from first heading
                first_heading = None
                for line in content.split("\n"):
                    if line.startswith("# "):
                        first_heading = line[2:].strip()
                        break
                if first_heading:
                    category_name = first_heading

                # Extract token count from "**Estimated tokens: ~XXX**"
                import re
                token_match = re.search(r"\*\*Estimated tokens:\s*~?(\d+)\*\*", content)
                if token_match:
                    tokens = int(token_match.group(1))

            flag_files.append({
                "category": category_name,
                "filename": filename,
                "path": str(flag_file),
                "tokens": tokens,
                "active": filename in active_flags,
            })

        return flag_files

    def _toggle_flag_in_flags_md(self, filename: str) -> bool:
        """Toggle a flag file in FLAGS.md by adding/removing its reference."""
        claude_home = self._flag_manager_base_dir()
        flags_md_path = claude_home / "FLAGS.md"

        lines: List[str] = []
        if flags_md_path.exists():
            try:
                lines = flags_md_path.read_text(encoding="utf-8").splitlines(keepends=True)
            except OSError:
                return False

        active_line = f"@flags/{filename}"
        modified = False
        new_lines: List[str] = []
        found_active = False
        found_commented = False

        for line in lines:
            stripped = line.strip()
            if stripped == active_line:
                found_active = True
                modified = True
                continue
            if stripped.startswith("<!-- @flags/") and stripped.endswith("-->"):
                commented_name = stripped.replace("<!-- @flags/", "").replace(" -->", "").strip()
                if commented_name == filename:
                    found_commented = True
                    modified = True
                    continue
            new_lines.append(line)

        if found_active:
            # Disabled by removing the line.
            pass
        else:
            if found_commented:
                # Replace legacy commented entry with active reference.
                new_lines.append(f"{active_line}\n")
            else:
                new_lines.append(f"{active_line}\n")
            modified = True

        if not modified:
            return False

        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] = f"{new_lines[-1]}\n"

        try:
            flags_md_path.write_text("".join(new_lines), encoding="utf-8")
        except OSError:
            return False

        return True

    def action_flag_manager_next(self) -> None:
        """Navigate to next flag in manager."""
        if self.current_view != "flag_manager" or not self.flag_files:
            return
        self.selected_flag_index = (self.selected_flag_index + 1) % len(self.flag_files)
        self.update_view()

    def action_flag_manager_prev(self) -> None:
        """Navigate to previous flag in manager."""
        if self.current_view != "flag_manager" or not self.flag_files:
            return
        self.selected_flag_index = (self.selected_flag_index - 1) % len(self.flag_files)
        self.update_view()

    def action_flag_manager_toggle(self) -> None:
        """Toggle the selected flag on/off."""
        if self.current_view != "flag_manager" or not self.flag_files:
            return

        if 0 <= self.selected_flag_index < len(self.flag_files):
            flag = self.flag_files[self.selected_flag_index]
            success = self._toggle_flag_in_flags_md(flag["filename"])

            if success:
                # Reload flag files to reflect changes
                self.flag_files = self._load_flag_files_metadata()
                new_state = "enabled" if flag["active"] == False else "disabled"
                self.update_view()
                self.notify(f"{flag['category']}: {new_state} in FLAGS.md", severity="information", timeout=2)
                self.status_message = f"{flag['category']}: {new_state}"
            else:
                self.notify("Failed to toggle flag in FLAGS.md", severity="error", timeout=2)

    # ─────────────────────────────────────────────────────────────────────
    # Watch Mode Actions
    # ─────────────────────────────────────────────────────────────────────

    def _get_watch_directory(self) -> Path:
        """Get the current watch directory."""
        if self.watch_mode_instance:
            return self.watch_mode_instance.directory
        return Path.cwd()

    def _get_watch_mode_state(self) -> WatchModeState:
        """Get current watch mode state for display."""
        if self.watch_mode_instance:
            state = self.watch_mode_instance.get_state()
            last_notif = state.get("last_notification")
            last_notif_str = None
            if last_notif:
                last_notif_str = f"{last_notif.get('icon', '')} {last_notif.get('title', '')} - {last_notif.get('message', '')}"
            return WatchModeState(
                running=state.get("running", False),
                directory=state.get("directory", Path.cwd()),
                auto_activate=state.get("auto_activate", True),
                threshold=state.get("threshold", 0.7),
                interval=state.get("interval", 2.0),
                checks_performed=state.get("checks_performed", 0),
                recommendations_made=state.get("recommendations_made", 0),
                auto_activations=state.get("auto_activations", 0),
                started_at=state.get("started_at"),
                last_notification=last_notif_str,
            )
        return WatchModeState(
            running=False,
            directory=Path.cwd(),
            auto_activate=True,
            threshold=0.7,
            interval=2.0,
            checks_performed=0,
            recommendations_made=0,
            auto_activations=0,
            started_at=None,
            last_notification=None,
        )

    def _handle_watch_notification(self, notification: Dict[str, str]) -> None:
        """Handle watch mode notifications in TUI."""
        icon = notification.get("icon", "🔔")
        title = notification.get("title", "Watch Mode")
        message = notification.get("message", "")
        # Show as TUI notification
        self.notify(f"{icon} {title}: {message}", timeout=5)
        # Update status message
        self.status_message = f"Watch: {title}"
        # Refresh view if on watch_mode
        if self.current_view == "watch_mode":
            self.update_view()

    def action_watch_start(self) -> None:
        """Start watch mode in background thread."""
        if self.watch_mode_instance and self.watch_mode_instance.running:
            self.notify("Watch mode already running", severity="warning", timeout=2)
            return
        # Initialize WatchMode with current or selected directory
        directory = self._get_watch_directory()
        self.watch_mode_instance = WatchMode(
            auto_activate=True,
            notification_threshold=0.7,
            check_interval=2.0,
            notification_callback=self._handle_watch_notification
        )
        self.watch_mode_instance.set_directory(directory)
        # Run in background thread
        self.watch_mode_thread = threading.Thread(
            target=self.watch_mode_instance.run,
            daemon=True
        )
        self.watch_mode_thread.start()
        self.notify("✅ Watch mode started", severity="information", timeout=2)
        # Immediate update
        self.update_view()
        # Schedule another update after brief delay to ensure thread has set running=True
        self.set_timer(0.1, self.update_view)

    def action_watch_stop(self) -> None:
        """Stop watch mode gracefully."""
        if not self.watch_mode_instance or not self.watch_mode_instance.running:
            self.notify("Watch mode not running", severity="warning", timeout=2)
            return
        self.watch_mode_instance.stop()
        if self.watch_mode_thread:
            self.watch_mode_thread.join(timeout=5.0)
        self.notify("⏹ Watch mode stopped", severity="information", timeout=2)
        self.update_view()

    async def action_watch_change_directory(self) -> None:
        """Prompt for new directory to watch."""
        current_dir = str(self._get_watch_directory())
        dialog = PromptDialog(
            "Change Watch Directory",
            "Enter directory path to watch",
            default=current_dir
        )
        result = await self.push_screen(dialog, wait_for_dismiss=True)
        if not result:
            return
        new_dir = Path(os.path.expanduser(result.strip()))
        if not new_dir.exists() or not new_dir.is_dir():
            self.notify("Invalid directory", severity="error", timeout=2)
            return
        if self.watch_mode_instance:
            try:
                self.watch_mode_instance.change_directory(new_dir)
                self.notify(f"📁 Directory changed to {new_dir.name}", severity="information", timeout=2)
            except Exception as e:
                self.notify(f"Failed to change directory: {e}", severity="error", timeout=3)
        self.update_view()

    def action_watch_toggle_auto(self) -> None:
        """Toggle auto-activation on/off."""
        if not self.watch_mode_instance:
            self.notify("Watch mode not initialized", severity="warning", timeout=2)
            return
        self.watch_mode_instance.auto_activate = not self.watch_mode_instance.auto_activate
        status = "enabled" if self.watch_mode_instance.auto_activate else "disabled"
        self.notify(f"Auto-activation {status}", severity="information", timeout=2)
        self.update_view()

    async def action_watch_adjust_threshold(self) -> None:
        """Adjust confidence threshold."""
        current = "0.7"
        if self.watch_mode_instance:
            current = str(self.watch_mode_instance.notification_threshold)
        dialog = PromptDialog(
            "Adjust Threshold",
            "Enter confidence threshold (0.0-1.0)",
            default=current
        )
        result = await self.push_screen(dialog, wait_for_dismiss=True)
        if not result:
            return
        try:
            threshold = float(result)
            if not 0.0 <= threshold <= 1.0:
                raise ValueError()
            if self.watch_mode_instance:
                self.watch_mode_instance.notification_threshold = threshold
            self.notify(f"🎯 Threshold set to {threshold:.0%}", severity="information", timeout=2)
            self.update_view()
        except ValueError:
            self.notify("Invalid threshold (must be 0.0-1.0)", severity="error", timeout=2)

    async def action_watch_adjust_interval(self) -> None:
        """Adjust check interval."""
        current = "2.0"
        if self.watch_mode_instance:
            current = str(self.watch_mode_instance.check_interval)
        dialog = PromptDialog(
            "Adjust Interval",
            "Enter check interval in seconds",
            default=current
        )
        result = await self.push_screen(dialog, wait_for_dismiss=True)
        if not result:
            return
        try:
            interval = float(result)
            if interval < 0.5:
                raise ValueError("Interval must be at least 0.5s")
            if self.watch_mode_instance:
                self.watch_mode_instance.check_interval = interval
            self.notify(f"⏱ Interval set to {interval}s", severity="information", timeout=2)
            self.update_view()
        except ValueError as e:
            self.notify(f"Invalid interval: {e}", severity="error", timeout=2)

    def _render_watch_mode_view(self) -> None:
        """Render watch mode control panel."""
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_column("Setting", width=22)
        table.add_column("Value", width=48)
        table.add_column("Action", width=20)
        # Get current state
        state = self._get_watch_mode_state()
        # Status row
        status_icon = "🟢 Running" if state.running else "🔴 Stopped"
        status_action = "[space] Stop" if state.running else "[space] Start"
        table.add_row("▶ Status", status_icon, status_action)
        # Directory row
        table.add_row("📁 Directory", str(state.directory), "[d] Change")
        # Settings rows
        auto_icon = "✅ ON" if state.auto_activate else "❌ OFF"
        table.add_row("🤖 Auto-activate", auto_icon, "[a] Toggle")
        table.add_row("🎯 Threshold", f"{state.threshold:.0%}", "[t] Adjust")
        table.add_row("⏱ Interval", f"{state.interval}s", "[i] Adjust")
        # Statistics rows
        table.add_row("", "", "")
        table.add_row("[bold]📊 Statistics[/bold]", "", "")
        table.add_row("🔍 Checks", str(state.checks_performed), "")
        table.add_row("💡 Recommendations", str(state.recommendations_made), "")
        table.add_row("⚡ Auto-activations", str(state.auto_activations), "")
        # Runtime info
        if state.started_at:
            duration = datetime.now() - state.started_at
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            table.add_row("⏰ Duration", f"{hours}h {minutes}m", "")
        # Last notification
        if state.last_notification:
            notif_text = Format.truncate(state.last_notification, 60)
            table.add_row("🔔 Last Event", f"[dim]{notif_text}[/dim]", "")
        self.status_message = f"Watch Mode - {status_icon}"

    # ─────────────────────────────────────────────────────────────────────
    # Asset Manager Actions
    # ─────────────────────────────────────────────────────────────────────

    def _get_selected_asset(self) -> Optional[Asset]:
        """Get the currently selected asset from the table."""
        if self.current_view != "assets":
            return None

        table = self.query_one("#main-table", DataTable)

        # Skip header rows (target info row and blank row)
        row_idx = table.cursor_row
        if row_idx < 2:  # Header rows
            return None

        # Flatten assets list
        all_assets: List[Asset] = []
        for category in ASSET_CATEGORY_ORDER:
            all_assets.extend(self.available_assets.get(category, []))

        asset_idx = row_idx - 2  # Adjust for header rows
        if 0 <= asset_idx < len(all_assets):
            return all_assets[asset_idx]
        return None

    def action_asset_change_target(self) -> None:
        """Change the installation target directory."""
        if self.current_view != "assets":
            return

        if not self.claude_directories:
            self.notify("No cortex directories found", severity="warning", timeout=2)
            return

        dialog = TargetSelectorDialog(self.claude_directories, self.selected_target_dir)
        self.push_screen(dialog, callback=self._handle_target_change)

    def _handle_target_change(self, result: Optional[Path]) -> None:
        """Handle target directory change callback."""
        try:
            if result:
                self.selected_target_dir = result
                self.status_message = f"Target: {result}"
                self.notify(f"Target set to {result}", severity="information", timeout=2)
                self.update_view()
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    def action_asset_details(self) -> None:
        """Show details for the selected asset (Enter key)."""
        if self.current_view != "assets":
            return
        self._show_asset_details()

    def action_asset_install(self) -> None:
        """Install the selected asset."""
        if self.current_view != "assets":
            return
        self._show_asset_details()

    def _show_asset_details(self) -> None:
        """Show asset detail dialog with install/uninstall/diff options."""
        asset = self._get_selected_asset()
        if not asset:
            self.notify("No asset selected", severity="warning", timeout=2)
            return

        if not self.selected_target_dir:
            self.notify("Select a target directory first (press T)", severity="warning", timeout=2)
            return

        # Check status
        status = check_installation_status(asset, self.selected_target_dir)

        # Store current asset for callback
        self._current_asset = asset

        # Show detail dialog with callback
        dialog = AssetDetailDialog(asset, status, self.selected_target_dir)
        self.push_screen(dialog, callback=self._handle_asset_detail_action)

    def _handle_asset_detail_action(self, action: Optional[str]) -> None:
        """Handle action from asset detail dialog."""
        try:
            if not action or not hasattr(self, "_current_asset"):
                return
            if not self.selected_target_dir:
                return
            saved_cursor_row = self._table_cursor_index()
            asset = self._current_asset

            if action == "install":
                exit_code, message = install_asset(asset, self.selected_target_dir)
                if exit_code == 0:
                    self.notify(f"✓ Installed {asset.display_name}", severity="information", timeout=2)
                else:
                    self.notify(f"Failed: {message}", severity="error", timeout=3)
                self.update_view()
                self._restore_main_table_cursor(saved_cursor_row)
            elif action == "uninstall":
                self._uninstall_asset_sync(asset)
            elif action == "diff":
                self._show_asset_diff_sync(asset)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    def _uninstall_asset_sync(self, asset: Asset) -> None:
        """Uninstall an asset with confirmation (sync version)."""
        if not self.selected_target_dir:
            self.notify("Select a target directory first", severity="warning", timeout=2)
            return

        # Store asset for callback
        self._uninstall_asset_pending = asset

        # Show confirm dialog with callback
        dialog = ConfirmDialog(
            "Uninstall Asset",
            f"Uninstall {asset.display_name} from {self.selected_target_dir}?",
        )
        self.push_screen(dialog, callback=self._handle_uninstall_confirm)

    def _handle_uninstall_confirm(self, confirmed: Optional[bool]) -> None:
        """Handle uninstall confirmation callback."""
        try:
            if not confirmed or not hasattr(self, "_uninstall_asset_pending"):
                return
            if not self.selected_target_dir:
                return

            saved_cursor_row = self._table_cursor_index()
            asset = self._uninstall_asset_pending
            exit_code, message = uninstall_asset(
                asset.category.value, asset.name, self.selected_target_dir
            )
            if exit_code == 0:
                self.notify(f"✓ Uninstalled {asset.display_name}", severity="information", timeout=2)
            else:
                self.notify(f"Failed: {message}", severity="error", timeout=3)
            self.update_view()
            self._restore_main_table_cursor(saved_cursor_row)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    def _show_asset_diff_sync(self, asset: Asset) -> None:
        """Show diff between source and installed asset (sync version)."""
        if not self.selected_target_dir:
            self.notify("Select a target directory first", severity="warning", timeout=2)
            return

        diff_text = get_asset_diff(asset, self.selected_target_dir)
        if not diff_text:
            self.notify("No differences found (or not installed)", severity="information", timeout=2)
            return

        # Store asset for callback
        self._diff_asset_pending = asset

        dialog = DiffViewerDialog(asset.display_name, diff_text)
        self.push_screen(dialog, callback=self._handle_diff_action)

    def _handle_diff_action(self, action: Optional[str]) -> None:
        """Handle diff viewer action callback."""
        try:
            if action != "apply" or not hasattr(self, "_diff_asset_pending"):
                return
            if not self.selected_target_dir:
                return

            saved_cursor_row = self._table_cursor_index()
            asset = self._diff_asset_pending
            exit_code, message = install_asset(asset, self.selected_target_dir)
            if exit_code == 0:
                self.notify(f"✓ Updated {asset.display_name}", severity="information", timeout=2)
            else:
                self.notify(f"Failed: {message}", severity="error", timeout=3)
            self.update_view()
            self._restore_main_table_cursor(saved_cursor_row)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    def action_asset_uninstall(self) -> None:
        """Uninstall the selected asset."""
        if self.current_view != "assets":
            return

        asset = self._get_selected_asset()
        if not asset:
            self.notify("No asset selected", severity="warning", timeout=2)
            return

        self._uninstall_asset_sync(asset)

    def action_asset_diff(self) -> None:
        """Show diff for the selected asset."""
        if self.current_view != "assets":
            return

        asset = self._get_selected_asset()
        if not asset:
            self.notify("No asset selected", severity="warning", timeout=2)
            return

        self._show_asset_diff_sync(asset)

    def action_asset_bulk_install(self) -> None:
        """Bulk install assets by category."""
        if self.current_view != "assets":
            return

        if not self.selected_target_dir:
            self.notify("Select a target directory first (press T)", severity="warning", timeout=2)
            return

        # Gather category counts (only not-installed assets)
        categories: List[Tuple[str, int]] = []
        for cat_name in ASSET_CATEGORY_ORDER:
            assets = self.available_assets.get(cat_name, [])
            not_installed = [
                a for a in assets
                if check_installation_status(a, self.selected_target_dir) == InstallStatus.NOT_INSTALLED
            ]
            if not_installed:
                categories.append((cat_name, len(not_installed)))

        if not categories:
            self.notify("All assets are already installed", severity="information", timeout=2)
            return

        dialog = BulkInstallDialog(categories)
        self.push_screen(dialog, callback=self._handle_bulk_install)

    def _handle_bulk_install(self, selected: Optional[List[str]]) -> None:
        """Handle bulk install dialog callback."""
        try:
            if not selected:
                self.notify("No categories selected", severity="warning", timeout=2)
                return
            if not self.selected_target_dir:
                return

            saved_cursor_row = self._table_cursor_index()
            installed_count = 0
            failed_count = 0

            for cat_name in selected:
                assets = self.available_assets.get(cat_name, [])
                for asset in assets:
                    if check_installation_status(asset, self.selected_target_dir) == InstallStatus.NOT_INSTALLED:
                        exit_code, _ = install_asset(asset, self.selected_target_dir)
                        if exit_code == 0:
                            installed_count += 1
                        else:
                            failed_count += 1

            if failed_count == 0:
                self.notify(f"✓ Installed {installed_count} assets", severity="information", timeout=2)
            else:
                self.notify(
                    f"Installed {installed_count}, failed {failed_count}",
                    severity="warning",
                    timeout=3,
                )
            self.update_view()
            self._restore_main_table_cursor(saved_cursor_row)
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    def action_asset_update_all(self) -> None:
        """Update all assets that differ from source."""
        if self.current_view != "assets":
            return

        if not self.selected_target_dir:
            self.notify("Select a target directory first (press T)", severity="warning", timeout=2)
            return

        # Find all assets that need updating (differ from source)
        assets_to_update: List[Asset] = []
        for cat_name in ASSET_CATEGORY_ORDER:
            assets = self.available_assets.get(cat_name, [])
            for asset in assets:
                status = check_installation_status(asset, self.selected_target_dir)
                if status in (InstallStatus.INSTALLED_DIFFERENT, InstallStatus.INSTALLED_OLDER):
                    assets_to_update.append(asset)

        if not assets_to_update:
            self.notify("All installed assets are up to date", severity="information", timeout=2)
            return

        # Show confirmation dialog
        self._assets_to_update = assets_to_update
        self._update_all_assets_pending = True
        dialog = ConfirmDialog(
            "Update All Assets",
            f"Update {len(assets_to_update)} asset(s) to latest version?",
        )
        self.push_screen(dialog, callback=self._handle_update_all_confirm)

    def _handle_update_all_confirm(self, confirmed: Optional[bool]) -> None:
        """Handle update all confirmation callback."""
        try:
            if not confirmed or not hasattr(self, "_assets_to_update"):
                return
            if not self.selected_target_dir:
                return

            saved_cursor_row = self._table_cursor_index()
            assets = self._assets_to_update
            updated_count = 0
            failed_count = 0

            for asset in assets:
                exit_code, _ = install_asset(asset, self.selected_target_dir)
                if exit_code == 0:
                    updated_count += 1
                else:
                    failed_count += 1

            if failed_count == 0:
                self.notify(f"✓ Updated {updated_count} assets", severity="information", timeout=2)
            else:
                self.notify(
                    f"Updated {updated_count}, failed {failed_count}",
                    severity="warning",
                    timeout=3,
                )
            self.update_view()
            self._restore_main_table_cursor(saved_cursor_row)
            if hasattr(self, "_update_all_assets_pending"):
                delattr(self, "_update_all_assets_pending")
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=5)

    # ─────────────────────────────────────────────────────────────────────────
    # Memory Vault Actions
    # ─────────────────────────────────────────────────────────────────────────

    def _normalize_memory_note_type(self, raw: str) -> Optional[str]:
        """Normalize memory note type input."""
        note_type = raw.strip().lower()
        aliases = {
            "knowledge": "knowledge",
            "project": "projects",
            "projects": "projects",
            "session": "sessions",
            "sessions": "sessions",
            "fix": "fixes",
            "fixes": "fixes",
        }
        return aliases.get(note_type)

    def action_memory_new_note(self) -> None:
        """Create a new memory note."""
        if self.current_view != "memory":
            self.action_view_memory()

        from .dialogs import MemoryNoteCreateDialog

        dialog = MemoryNoteCreateDialog("New Memory Note")
        self.push_screen(dialog, callback=self._handle_memory_note_create)

    def _handle_memory_note_create(self, result: Optional[dict[str, str]]) -> None:
        if not result:
            return

        note_type_raw = result.get("note_type", "")
        title = result.get("title", "").strip()
        summary = result.get("summary", "").strip()

        if not title:
            self.notify("Note title is required", severity="warning", timeout=2)
            return

        note_type = self._normalize_memory_note_type(note_type_raw)
        if not note_type:
            self.notify(
                "Invalid note type. Use: knowledge, projects, sessions, fixes",
                severity="error",
                timeout=3,
            )
            return

        from ..memory import memory_remember, memory_project, memory_capture, memory_fix

        try:
            if note_type == "knowledge":
                text = summary or "Captured via TUI"
                exit_code, message = memory_remember(text=text, topic=title)
            elif note_type == "projects":
                exit_code, message = memory_project(
                    name=title,
                    purpose=summary or None,
                    path=None,
                    related=None,
                    update=False,
                )
            elif note_type == "sessions":
                session_summary = summary or "Session captured via TUI"
                exit_code, message = memory_capture(
                    title=title,
                    summary=session_summary,
                    quick=True,
                )
            else:
                problem = summary or "Issue documented via TUI"
                exit_code, message = memory_fix(
                    title=title,
                    problem=problem,
                )
        except Exception as exc:
            self.notify(
                f"Failed to create memory note: {exc}",
                severity="error",
                timeout=3,
            )
            return

        clean = self._clean_ansi(message)
        if exit_code == 0:
            self.notify(clean or "Created memory note", severity="information", timeout=2)
            self.load_memory_notes()
            self.update_view()
        else:
            self.notify(clean or "Failed to create memory note", severity="error", timeout=3)

    def _get_selected_memory_note(self) -> Optional[MemoryNote]:
        """Get the currently selected memory note from the table."""
        if self.current_view != "memory":
            return None

        table = self.query_one("#main-table", DataTable)

        row_idx = table.cursor_row
        if row_idx < 0 or row_idx >= len(self.memory_notes):
            return None

        return self.memory_notes[row_idx]

    def action_memory_view_note(self) -> None:
        """View the selected memory note."""
        if self.current_view != "memory":
            return

        note = self._get_selected_memory_note()
        if not note:
            self.notify("No note selected", severity="warning", timeout=2)
            return

        # Read the note content
        try:
            from ..memory import read_note, NoteType
            note_type = NoteType(note.note_type)
            content = read_note(note_type, note.title)
            if content:
                # Show in a detail dialog
                self._show_memory_note_dialog(note, content)
            else:
                self.notify("Could not read note", severity="error", timeout=2)
        except Exception as e:
            self.notify(f"Error reading note: {e}", severity="error", timeout=3)

    def _show_memory_note_dialog(self, note: MemoryNote, content: str) -> None:
        """Show a dialog with memory note content."""
        from .dialogs import MemoryNoteDialog
        self._current_memory_note = note
        dialog = MemoryNoteDialog(note, content)
        self.push_screen(dialog, callback=self._handle_memory_note_action)

    def _handle_memory_note_action(self, action: Optional[str]) -> None:
        """Handle action from memory note dialog."""
        if not action or not hasattr(self, "_current_memory_note"):
            return

        note = self._current_memory_note

        if action == "open":
            try:
                import subprocess
                import os
                editor = os.environ.get("EDITOR", "open" if os.name == "darwin" else "xdg-open")
                subprocess.Popen([editor, note.path])
                self.notify(f"Opened {note.title}", severity="information", timeout=2)
            except Exception as e:
                self.notify(f"Error opening note: {e}", severity="error", timeout=3)
        elif action == "delete":
            self._memory_note_to_delete = note
            dialog = ConfirmDialog(
                "Delete Note",
                f"Delete '{note.title}'? This cannot be undone.",
            )
            self.push_screen(dialog, callback=self._handle_memory_delete_confirm)

    def action_memory_open_note(self) -> None:
        """Open the selected memory note in external editor."""
        if self.current_view != "memory":
            return

        note = self._get_selected_memory_note()
        if not note:
            self.notify("No note selected", severity="warning", timeout=2)
            return

        try:
            import subprocess
            import os

            editor = os.environ.get("EDITOR", "open" if os.name == "darwin" else "xdg-open")
            subprocess.Popen([editor, note.path])
            self.notify(f"Opened {note.title}", severity="information", timeout=2)
        except Exception as e:
            self.notify(f"Error opening note: {e}", severity="error", timeout=3)

    def action_memory_delete_note(self) -> None:
        """Delete the selected memory note."""
        if self.current_view != "memory":
            return

        note = self._get_selected_memory_note()
        if not note:
            self.notify("No note selected", severity="warning", timeout=2)
            return

        # Store note for callback
        self._memory_note_to_delete = note

        dialog = ConfirmDialog(
            "Delete Note",
            f"Delete '{note.title}'? This cannot be undone.",
        )
        self.push_screen(dialog, callback=self._handle_memory_delete_confirm)

    def _handle_memory_delete_confirm(self, confirmed: Optional[bool]) -> None:
        """Handle note deletion confirmation callback."""
        try:
            if not confirmed or not hasattr(self, "_memory_note_pending"):
                return

            saved_cursor_row = self._table_cursor_index()
            note = self._memory_note_pending
            path = Path(note.path)

            if path.exists():
                path.unlink()
                self.notify(f"✓ Deleted {note.title}", severity="information", timeout=2)
                self.load_memory_notes()
                self.update_view()
            else:
                self.notify("Note file not found", severity="warning", timeout=2)
        except Exception as e:
            self.notify(f"Error deleting note: {e}", severity="error", timeout=5)

    async def action_run_selected(self) -> None:
        """Run the highlighted item in workflows or scenarios view."""
        if self.current_view == "workflows":
            await self._run_selected_workflow()
            return
        if self.current_view == "scenarios":
            await self.action_scenario_run_auto()
            return
        self.notify(
            "Run action is only available in Workflows or Scenarios views",
            severity="warning",
            timeout=2,
        )

    async def action_stop_selected(self) -> None:
        """Stop the highlighted workflow or scenario."""
        if self.current_view == "workflows":
            await self._stop_selected_workflow()
            return
        if self.current_view == "scenarios":
            await self._stop_selected_scenario()
            return
        self.notify(
            "Stop action is only available in Workflows or Scenarios views",
            severity="warning",
            timeout=2,
        )

    async def action_scenario_preview(self) -> None:
        """Preview the selected scenario definition."""
        if self.current_view != "scenarios":
            return
        scenario = self._selected_scenario()
        if not scenario:
            self.notify("Select a scenario to preview", severity="warning", timeout=2)
            return
        exit_code, message = scenario_preview(scenario.file_path.stem)
        cleaned = _strip_ansi_codes(message or "")
        if exit_code != 0:
            self.status_message = cleaned.split("\n")[0][:160]
            self.notify(
                f"✗ Failed to preview {scenario.name}",
                severity="error",
                timeout=3,
            )
            return

        await self.push_screen(
            TextViewerDialog(f"Scenario Preview: {scenario.name}", cleaned)
        )
        self.status_message = f"Previewed {scenario.name}"

    def action_principles_build(self) -> None:
        """Rebuild PRINCIPLES.md from active snippets."""
        if self.current_view != "principles":
            self.action_view_principles()

        exit_code, message = principles_build()
        clean = self._clean_ansi(message)
        if clean:
            self.status_message = clean.split("\n")[0]

        if exit_code == 0:
            self.notify("✓ Principles rebuilt", severity="information", timeout=2)
            self.load_principles()
            self.update_view()
        else:
            self.notify(clean or "Build failed", severity="error", timeout=3)

    async def action_scenario_run_auto(self) -> None:
        """Run the selected scenario in automatic mode."""
        if self.current_view != "scenarios":
            return
        scenario = self._selected_scenario()
        if not scenario:
            self.notify("Select a scenario to run", severity="warning", timeout=2)
            return
        if scenario.status == "invalid":
            self.notify(
                f"Cannot run invalid scenario '{scenario.name}'",
                severity="error",
                timeout=3,
            )
            return
        if scenario.lock_holder:
            self.notify(
                f"Scenario '{scenario.name}' already running",
                severity="warning",
                timeout=2,
            )
            return

        confirm = await self.push_screen(
            ConfirmDialog(
                "Run Scenario",
                f"Execute scenario '{scenario.name}' in automatic mode?",
                default=True,
            ),
            wait_for_dismiss=True,
        )
        if confirm is not True:
            self.status_message = "Scenario run cancelled"
            return

        self.status_message = f"Running scenario: {scenario.name}"
        
        python_executable = sys.executable
        command = [python_executable, "-m", "claude_ctx_py.cli", "orchestrate", "run", scenario.file_path.stem, "--auto"]

        await self.app.push_screen(LogViewerScreen(command, title=f"Running Scenario: {scenario.name}"))
        
        self.notify(
            f"Scenario '{scenario.name}' finished.",
            severity="information",
            timeout=3,
        )
        self.load_scenarios()
        self.update_view()

    async def _run_selected_workflow(self) -> None:
        """Run the highlighted workflow and stream output in a log viewer."""
        workflow = self._selected_workflow()
        if not workflow:
            self.notify("Select a workflow to run", severity="warning", timeout=2)
            return

        workflow_name = workflow.file_path.stem if workflow.file_path else workflow.name
        self.status_message = f"Running workflow: {workflow.name}"

        python_executable = sys.executable
        command = [
            python_executable,
            "-m",
            "claude_ctx_py.cli",
            "workflow",
            "run",
            workflow_name,
        ]

        await self.app.push_screen(
            LogViewerScreen(command, title=f"Running Workflow: {workflow.name}")
        )

        self.notify(
            f"Workflow '{workflow.name}' finished.",
            severity="information",
            timeout=3,
        )
        self.load_workflows()
        self.load_agent_tasks()
        self.update_view()

    async def _stop_selected_workflow(self) -> None:
        workflow = self._selected_workflow()
        if not workflow:
            self.notify("Select a workflow to stop", severity="warning", timeout=2)
            return

        workflow_name = workflow.file_path.stem if workflow.file_path else workflow.name
        exit_code, message = workflow_stop(workflow_name)
        clean = self._clean_ansi(message)

        if exit_code == 0:
            self.notify(clean or f"Stopped {workflow.name}", severity="information", timeout=2)
            self.status_message = clean or f"Stopped {workflow.name}"
        else:
            self.notify(clean or "Failed to stop workflow", severity="error", timeout=3)
            self.status_message = clean or f"Failed to stop {workflow.name}"

        self.load_workflows()
        self.load_agent_tasks()
        self.update_view()

    async def _stop_selected_scenario(self) -> None:
        scenario = self._selected_scenario()
        if not scenario:
            self.notify("Select a scenario to stop", severity="warning", timeout=2)
            return

        scenario_name = scenario.file_path.stem if scenario.file_path else scenario.name
        exit_code, message = scenario_stop(scenario_name)
        clean = self._clean_ansi(message)

        if exit_code == 0:
            self.notify(clean or f"Stopped {scenario.name}", severity="information", timeout=2)
            self.status_message = clean or f"Stopped {scenario.name}"
        else:
            self.notify(clean or "Failed to stop scenario", severity="error", timeout=3)
            self.status_message = clean or f"Failed to stop {scenario.name}"

        self.load_scenarios()
        self.update_view()

    async def action_scenario_validate_selected(self) -> None:
        """Validate the selected scenario against the schema."""
        if self.current_view != "scenarios":
            return
        scenario = self._selected_scenario()
        if not scenario:
            self.notify("Select a scenario to validate", severity="warning", timeout=2)
            return

        exit_code, message = scenario_validate(scenario.file_path.stem)
        cleaned = _strip_ansi_codes(message or "")
        await self.push_screen(
            TextViewerDialog(f"Scenario Validation: {scenario.name}", cleaned)
        )

        if exit_code == 0:
            self.notify(
                f"Scenario '{scenario.name}' is valid",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Validated {scenario.name}"
        else:
            self.notify(
                f"Scenario '{scenario.name}' failed validation",
                severity="error",
                timeout=3,
            )
            self.status_message = f"Validation errors for {scenario.name}"

    async def action_scenario_status_history(self) -> None:
        """Show scenario locks and recent executions."""
        report = scenario_status()
        cleaned = _strip_ansi_codes(report or "No scenario executions logged yet.")
        await self.push_screen(TextViewerDialog("Scenario Status", cleaned))
        self.status_message = "Scenario status displayed"

    def action_view_galaxy(self) -> None:
        """Switch to the agent galaxy visualization."""
        self.current_view = "galaxy"
        self.status_message = "Switched to Galaxy"
        self.notify("🌌 Galaxy", severity="information", timeout=1)

    def action_view_tasks(self) -> None:
        """Switch to tasks view."""
        self.load_agent_tasks()
        self.current_view = "tasks"
        self.status_message = "Switched to Tasks"
        self.notify("🗂 Tasks", severity="information", timeout=1)

    def action_agent_view(self) -> None:
        """View the selected agent's definition (Enter key in agents view)."""
        if self.current_view != "agents":
            return
        # Delegate to the existing details context action
        self.run_worker(self._show_selected_agent_definition(), exclusive=True)

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
            self.notify(f"✓ Applied {name}", severity="information", timeout=2)
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

        dialog = PromptDialog(
            "Save Profile", "Enter profile name", placeholder="team-alpha"
        )
        name = await self.push_screen(dialog, wait_for_dismiss=True)
        if not name:
            return

        exit_code, message = profile_save(name.strip())
        clean = self._clean_ansi(message)
        if exit_code == 0:
            self.notify(clean or f"Saved profile {name}", severity="information", timeout=2)
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
            self.notify(
                "Select a saved profile to delete", severity="warning", timeout=2
            )
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

    def action_profile_edit(self) -> None:
        """Open the profile editor dialog."""
        if self.current_view != "profiles":
            return

        profile = self._selected_profile()
        if not profile:
            self.notify("Select a profile first", severity="warning", timeout=2)
            return

        name = profile.get("name") or ""
        ptype = profile.get("type") or "built-in"
        path_str = profile.get("path")

        dialog = ProfileEditorDialog(name, ptype, path_str)
        self.push_screen(dialog, callback=self._handle_profile_edit_result)

    def _handle_profile_edit_result(self, config: Optional[ProfileConfig]) -> None:
        """Handle the result from the profile editor dialog."""
        if not config:
            return

        # Apply the edited profile configuration
        try:
            # First reset to minimal
            exit_code, message = _profile_reset()
            if exit_code != 0:
                self.notify(f"Reset failed: {self._clean_ansi(message)}", severity="error", timeout=3)
                return

            # Activate selected agents
            for agent_name in config.agents:
                exit_code, msg = agent_activate(agent_name)
                if exit_code != 0 and "already active" not in (msg or "").lower():
                    self.notify(f"Agent {agent_name}: {self._clean_ansi(msg)}", severity="warning", timeout=2)

            # Activate selected modes
            for mode_name in config.modes:
                exit_code, msg = mode_activate(mode_name)
                if exit_code != 0 and "already active" not in (msg or "").lower():
                    self.notify(f"Mode {mode_name}: {self._clean_ansi(msg)}", severity="warning", timeout=2)

            # Activate selected rules
            for rule_name in config.rules:
                rules_activate(rule_name)

            # Reload all views
            self.load_agents()
            self.load_modes()
            self.load_rules()
            self.load_profiles()
            self.update_view()

            self.status_message = f"Applied profile: {config.name}"
            self.notify(f"Applied profile: {config.name}", severity="information", timeout=2)

        except Exception as exc:
            self.notify(f"Failed to apply: {exc}", severity="error", timeout=3)

    # ─────────────────────────────────────────────────────────────────────────
    # Setup Tools Actions (profiles view)
    # ─────────────────────────────────────────────────────────────────────────

    async def _run_init_wizard(self) -> None:
        """Run the interactive initialization wizard."""
        self.notify("Starting Init Wizard...", severity="information", timeout=2)

        try:
            exit_code, message = init_wizard(cwd=Path.cwd())
            clean_msg = self._clean_ansi(message)

            if exit_code == 0:
                self.notify("Init Wizard completed", severity="information", timeout=3)
                # Reload all data
                self.load_agents()
                self.load_modes()
                self.load_rules()
                self.load_profiles()
                self.update_view()
            else:
                self.notify("Wizard cancelled or failed", severity="warning", timeout=3)

            await self._show_text_dialog("Init Wizard Result", clean_msg)

        except Exception as exc:
            self.notify(f"Init Wizard failed: {exc}", severity="error", timeout=3)

    async def action_setup_init_wizard(self) -> None:
        """Launch the interactive initialization wizard."""
        if self.current_view != "profiles":
            return

        await self._run_init_wizard()

    async def action_setup_init_minimal(self) -> None:
        """Apply minimal configuration quickly."""
        if self.current_view != "profiles":
            return

        confirm = await self.push_screen(
            ConfirmDialog(
                "Init Minimal",
                "Apply minimal configuration? This will reset to essential agents only."
            ),
            wait_for_dismiss=True,
        )
        if not confirm:
            return

        try:
            exit_code, message = init_minimal()
            clean_msg = self._clean_ansi(message)

            if exit_code == 0:
                self.notify("Minimal configuration applied", severity="information", timeout=3)
                # Reload all data
                self.load_agents()
                self.load_modes()
                self.load_rules()
                self.load_profiles()
                self.update_view()
            else:
                self.notify(f"Init failed: {clean_msg[:100]}", severity="error", timeout=3)

            # Show full output
            await self._show_text_dialog("Init Minimal Result", clean_msg)

        except Exception as exc:
            self.notify(f"Init Minimal failed: {exc}", severity="error", timeout=3)

    async def action_setup_migration(self) -> None:
        """Migrate from comment-based to file-based activation."""
        if self.current_view != "profiles":
            return

        confirm = await self.push_screen(
            ConfirmDialog(
                "Run Migration",
                "Migrate CLAUDE.md from comment-based to file-based activation?\n"
                "This will update rules and modes to use the new system."
            ),
            wait_for_dismiss=True,
        )
        if not confirm:
            return

        try:
            exit_code, message = migrate_to_file_activation()
            clean_msg = self._clean_ansi(message)

            if exit_code == 0:
                self.notify("Migration completed successfully", severity="information", timeout=3)
            else:
                self.notify("Migration completed with warnings", severity="warning", timeout=3)

            # Reload all data
            self.load_agents()
            self.load_modes()
            self.load_rules()
            self.load_profiles()
            self.update_view()

            # Show full output
            await self._show_text_dialog("Migration Result", clean_msg)

        except Exception as exc:
            self.notify(f"Migration failed: {exc}", severity="error", timeout=3)

    async def action_setup_health_check(self) -> None:
        """Run diagnostics and verify directory structure."""
        if self.current_view != "profiles":
            return

        self.notify("Running health check...", severity="information", timeout=2)

        try:
            claude_dir = _resolve_claude_dir()

            # First ensure structure exists
            created = _ensure_claude_structure(claude_dir)

            # Then run doctor diagnostics
            exit_code, doctor_msg = doctor_run(fix=False)
            clean_doctor = self._clean_ansi(doctor_msg)

            # Build report
            report_lines = ["[bold cyan]Directory Structure[/bold cyan]"]
            if created:
                report_lines.append(f"Created {len(created)} missing directories/files:")
                for path in created[:10]:
                    report_lines.append(f"  • {Path(path).name}")
                if len(created) > 10:
                    report_lines.append(f"  ... and {len(created) - 10} more")
            else:
                report_lines.append("All directories and files present ✓")

            report_lines.append("")
            report_lines.append("[bold cyan]Diagnostics[/bold cyan]")
            report_lines.append(clean_doctor)

            if exit_code == 0 and not created:
                self.notify("Health check passed", severity="information", timeout=3)
            elif created:
                self.notify(f"Fixed {len(created)} missing items", severity="information", timeout=3)
            else:
                self.notify("Health check found issues", severity="warning", timeout=3)

            # Show full report
            await self._show_text_dialog("Health Check Report", "\n".join(report_lines))

        except Exception as exc:
            self.notify(f"Health check failed: {exc}", severity="error", timeout=3)

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
        path = await self._prompt_text(
            "Suggest Skills", "Project directory", default="."
        )
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
        fmt = await self._prompt_text(
            "Skill Report", "Format (text/json/csv)", default="text"
        )
        if fmt is None:
            return
        await self._handle_skill_result(
            skill_report,
            args=[fmt],
            title=f"Skill Report ({fmt})",
        )

    async def action_skill_trending(self) -> None:
        days_input = await self._prompt_text(
            "Skill Trending", "Days to include", default="30"
        )
        if days_input is None:
            return
        try:
            days = int(days_input)
        except ValueError:
            self.notify("Days must be a number", severity="error", timeout=2)
            return
        await self._handle_skill_result(
            skill_trending,
            args=[str(days)],
            title=f"Trending Skills ({days}d)",
        )

    async def _rate_skill_interactive(
        self, skill_slug: str, display_name: Optional[str] = None
    ) -> bool:
        """Shared rating flow used by manual and auto prompts."""

        label = display_name or skill_slug
        title = f"Rate Skill · {label}"

        stars_input = await self._prompt_text(
            title,
            f"Stars 1-5 for {label}",
            default="5",
        )
        if stars_input is None:
            return False
        try:
            stars = int(stars_input)
        except ValueError:
            self.notify(
                "Rating must be a number between 1-5",
                severity="error",
                timeout=2,
            )
            return False
        if stars < 1 or stars > 5:
            self.notify(
                "Rating must be between 1 and 5 stars",
                severity="error",
                timeout=2,
            )
            return False

        helpful_input = await self._prompt_text(
            "Was it helpful?",
            "y/n",
            default="y",
        )
        if helpful_input is None:
            return False

        succeeded_input = await self._prompt_text(
            "Did the task succeed?",
            "y/n",
            default="y",
        )
        if succeeded_input is None:
            return False

        review = await self._prompt_text(
            "Optional Review",
            "Share a short review (Enter to skip)",
            default="",
        )
        if review is None:
            return False

        helpful_value = (helpful_input or "y").strip().lower() not in {"n", "no"}
        succeeded_value = (succeeded_input or "y").strip().lower() not in {
            "n",
            "no",
        }
        review_value = review.strip() or None

        try:
            exit_code, output = skill_rate(
                skill_slug,
                stars=stars,
                helpful=helpful_value,
                task_succeeded=succeeded_value,
                review=review_value,
            )
        except Exception as exc:
            self.notify(f"Rating failed: {exc}", severity="error", timeout=3)
            return False

        cleaned = self._clean_ansi(output)
        if cleaned:
            await self._show_text_dialog(f"Skill Rating · {label}", cleaned)

        if exit_code == 0:
            self.notify(f"Thanks for rating {label}", severity="information", timeout=2)
            # Refresh cached metrics so the table reflects new data
            self.skill_rating_collector = None
            self.skill_prompt_manager = None  # ensure future prompts see new state
            self.load_skills()
            self.update_view()
            manager = self._get_skill_prompt_manager()
            if manager:
                manager.mark_rated(skill_slug)
            return True

        self.notify(
            f"Unable to rate {label}", severity="error", timeout=3
        )
        return False

    async def action_skill_rate_selected(self) -> None:
        """Collect a rating for the highlighted skill."""
        if self.current_view != "skills":
            self.action_view_skills()

        skill = self._selected_skill()
        if not skill:
            self.notify("Select a skill to rate", severity="warning", timeout=2)
            return

        slug = self._skill_slug(skill)
        await self._rate_skill_interactive(slug, skill.get("name", slug))

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
        rating_input = await self._prompt_text(
            "Community Rate", "Rating 1-5", default="5"
        )
        if rating_input is None:
            return
        try:
            rating = int(rating_input)
        except ValueError:
            self.notify("Rating must be 1-5", severity="error", timeout=2)
            return
        await self._handle_skill_result(
            skill_community_rate,
            args=[name, str(rating)],
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
            self.notify(f"✓ {slug} validated", severity="information", timeout=2)
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
            self.notify(
                f"Metrics unavailable for {slug}", severity="warning", timeout=2
            )

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
            self.notify(
                "Metrics not available in this view", severity="warning", timeout=2
            )

    async def action_context_action(self) -> None:
        """Context-aware action for the 'c' binding."""
        if self.current_view == "skills":
            await self.action_skill_community()
        elif self.current_view == "mcp":
            await self.action_mcp_snippet()
        elif self.current_view == "principles":
            self.action_principles_build()
        else:
            self.notify("No contextual action", severity="warning", timeout=2)

    async def action_docs_context(self) -> None:
        """Context-aware docs shortcut."""
        if self.current_view == "mcp":
            await self.action_mcp_docs()
        elif self.current_view == "principles":
            self.action_principles_open()
        else:
            self.notify(
                "Docs not available in this view", severity="warning", timeout=2
            )

    async def action_details_context(self) -> None:
        """Context-aware details shortcut."""
        if self.current_view == "agents":
            # Running in a worker ensures push_screen wait semantics work reliably
            self.run_worker(self._show_selected_agent_definition(), exclusive=True)
            return
        elif self.current_view == "principles":
            self.run_worker(self._show_selected_principle_definition(), exclusive=True)
            return
        elif self.current_view == "mcp":
            await self.action_mcp_details()
        elif self.current_view == "tasks":
            self.run_worker(self._show_task_details(), exclusive=True)
            return
        elif self.current_view == "commands":
            self.run_worker(self._show_selected_command_definition(), exclusive=True)
            return
        elif self.current_view == "worktrees":
            worktree = self._selected_worktree()
            if not worktree:
                self.notify("Select a worktree to view details", severity="warning", timeout=2)
                return
            lines = [
                f"Path: {worktree.path}",
                f"Branch: {worktree.branch or 'detached'}",
                f"HEAD: {worktree.head or 'unknown'}",
                f"Main: {'yes' if worktree.is_main else 'no'}",
                f"Locked: {'yes' if worktree.locked else 'no'}",
                f"Prunable: {'yes' if worktree.prunable else 'no'}",
            ]
            if worktree.lock_reason:
                lines.append(f"Lock reason: {worktree.lock_reason}")
            if worktree.prune_reason:
                lines.append(f"Prune reason: {worktree.prune_reason}")
            self.run_worker(
                self._show_text_dialog("Worktree Details", "\n".join(lines)),
                exclusive=True,
            )
            return
        else:
            self.notify("Details not available", severity="warning", timeout=2)

    async def _show_selected_principle_definition(self) -> None:
        """Open the selected principles snippet for review."""
        index = self._table_cursor_index()
        if index is None or not self.principles:
            self.notify(
                "Select a principles snippet to view details",
                severity="warning",
                timeout=2,
            )
            return
        if index < 0 or index >= len(self.principles):
            return

        snippet = self.principles[index]
        try:
            claude_dir = _resolve_claude_dir()
            snippet_path = self._validate_path(claude_dir, snippet.path)
        except ValueError:
            snippet_path = snippet.path

        try:
            body = snippet_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to load {snippet.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        meta_lines = [
            f"Snippet : {snippet.name}",
            f"Title   : {snippet.title}",
            f"Status  : {snippet.status}",
            f"Path    : {snippet.path}",
            "",
        ]
        meta_lines.append(body)
        await self._show_text_dialog(
            f"Principles Snippet · {snippet.name}",
            "\n".join(meta_lines),
        )
        self.status_message = f"Viewing principles snippet {snippet.name}"
        self.refresh_status_bar()

    def action_principles_open(self) -> None:
        """Open the generated PRINCIPLES.md for review."""
        self.run_worker(self._show_principles_output(), exclusive=True)

    async def _show_principles_output(self) -> None:
        if self.current_view != "principles":
            self.action_view_principles()

        claude_dir = _resolve_claude_dir()
        principles_path = claude_dir / "PRINCIPLES.md"

        if not principles_path.is_file():
            exit_code, message = principles_build()
            clean = self._clean_ansi(message)
            if exit_code != 0:
                self.notify(
                    clean or "Failed to build PRINCIPLES.md",
                    severity="error",
                    timeout=3,
                )
                return
            self.notify("✓ Built PRINCIPLES.md", severity="information", timeout=2)

        try:
            body = principles_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read PRINCIPLES.md: {exc}",
                severity="error",
                timeout=3,
            )
            return

        await self._show_text_dialog("PRINCIPLES.md", body)
        self.status_message = "Viewing PRINCIPLES.md"
        self.refresh_status_bar()

    async def _show_selected_agent_definition(self) -> None:
        """Open the full agent definition for the selected agent."""
        agent = self._selected_agent()
        if not agent:
            self.notify(
                "Select an agent to view its definition",
                severity="warning",
                timeout=2,
            )
            return

        try:
            claude_dir = _resolve_claude_dir()
            agent_path = self._validate_path(claude_dir, agent.path)
        except ValueError:
            agent_path = agent.path

        try:
            definition = agent_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to load {agent.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        await self._show_text_dialog(f"{agent.name} Definition", definition)
        self.status_message = f"Viewing definition for {agent.name}"
        self.refresh_status_bar()

    async def _show_selected_command_definition(self) -> None:
        """Open the selected slash command for review."""
        command = self._selected_command()
        if not command:
            self.notify(
                "Select a slash command to view details",
                severity="warning",
                timeout=2,
            )
            return

        try:
            claude_dir = _resolve_claude_dir()
            command_path = self._validate_path(claude_dir, command.path)
        except ValueError:
            command_path = command.path

        try:
            body = command_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to load {command.command}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        meta_lines = [
            f"Command : {command.command}",
            f"Category: {command.category}",
            f"Complexity: {command.complexity}",
            f"Agents  : {', '.join(command.agents) if command.agents else '—'}",
            f"Personas: {', '.join(command.personas) if command.personas else '—'}",
            f"MCP     : {', '.join(command.mcp_servers) if command.mcp_servers else '—'}",
            f"Path    : {command.path}",
            "",
        ]
        meta_lines.append(body)
        await self._show_text_dialog(f"{command.command} Definition", "\n".join(meta_lines))
        self.status_message = f"Viewing slash command {command.command}"
        self.refresh_status_bar()

    async def action_copy_definition(self) -> None:
        """Copy the definition of the selected item to clipboard."""
        try:
            if self.current_view == "agents":
                await self._copy_agent_definition()
            elif self.current_view == "modes":
                await self._copy_mode_definition()
            elif self.current_view == "principles":
                await self._copy_principle_definition()
            elif self.current_view == "rules":
                await self._copy_rule_definition()
            elif self.current_view == "skills":
                await self._copy_skill_definition()
            elif self.current_view == "commands":
                await self._copy_command_definition()
            else:
                self.notify(
                    "Copy not available in this view",
                    severity="warning",
                    timeout=2,
                )
        except Exception as exc:
            self.notify(
                f"Copy failed: {exc}",
                severity="error",
                timeout=3,
            )

    async def _copy_agent_definition(self) -> None:
        """Copy the selected agent's definition to clipboard."""
        agent = self._selected_agent()
        if not agent:
            self.notify(
                "Select an agent to copy",
                severity="warning",
                timeout=2,
            )
            return

        try:
            claude_dir = _resolve_claude_dir()
            agent_path = self._validate_path(claude_dir, agent.path)
        except ValueError:
            agent_path = agent.path

        try:
            definition = agent_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {agent.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        if self._copy_to_clipboard(definition):
            self.notify(
                f"✓ Copied {agent.name} definition to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {agent.name} definition"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _copy_mode_definition(self) -> None:
        """Copy the selected mode's definition to clipboard."""
        index = self._table_cursor_index()
        if index is None or not self.modes:
            self.notify(
                "Select a mode to copy",
                severity="warning",
                timeout=2,
            )
            return

        if index < 0 or index >= len(self.modes):
            return

        mode = self.modes[index]
        try:
            claude_dir = _resolve_claude_dir()
            mode_path = self._validate_path(claude_dir, mode.path)
        except ValueError:
            mode_path = mode.path

        try:
            definition = mode_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {mode.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        if self._copy_to_clipboard(definition):
            self.notify(
                f"✓ Copied {mode.name} mode to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {mode.name} mode"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _copy_principle_definition(self) -> None:
        """Copy the selected principles snippet to clipboard."""
        index = self._table_cursor_index()
        if index is None or not self.principles:
            self.notify(
                "Select a principles snippet to copy",
                severity="warning",
                timeout=2,
            )
            return

        if index < 0 or index >= len(self.principles):
            return

        snippet = self.principles[index]
        try:
            claude_dir = _resolve_claude_dir()
            snippet_path = self._validate_path(claude_dir, snippet.path)
        except ValueError:
            snippet_path = snippet.path

        try:
            definition = snippet_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {snippet.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        if self._copy_to_clipboard(definition):
            self.notify(
                f"✓ Copied {snippet.name} snippet to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {snippet.name} snippet"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _copy_rule_definition(self) -> None:
        """Copy the selected rule's definition to clipboard."""
        index = self._table_cursor_index()
        if index is None or not self.rules:
            self.notify(
                "Select a rule to copy",
                severity="warning",
                timeout=2,
            )
            return

        if index < 0 or index >= len(self.rules):
            return

        rule = self.rules[index]
        try:
            claude_dir = _resolve_claude_dir()
            rule_path = self._validate_path(claude_dir, rule.path)
        except ValueError:
            rule_path = rule.path

        try:
            definition = rule_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {rule.name}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        if self._copy_to_clipboard(definition):
            self.notify(
                f"✓ Copied {rule.name} rule to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {rule.name} rule"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _copy_skill_definition(self) -> None:
        """Copy the selected skill's definition to clipboard."""
        skill = self._selected_skill()
        if not skill:
            self.notify(
                "Select a skill to copy",
                severity="warning",
                timeout=2,
            )
            return

        skill_path = Path(skill["path"])
        try:
            definition = skill_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {skill['name']}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        if self._copy_to_clipboard(definition):
            self.notify(
                f"✓ Copied {skill['name']} skill to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {skill['name']} skill"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _copy_command_definition(self) -> None:
        """Copy the selected command's definition to clipboard."""
        command = self._selected_command()
        if not command:
            self.notify(
                "Select a command to copy",
                severity="warning",
                timeout=2,
            )
            return

        try:
            claude_dir = _resolve_claude_dir()
            command_path = self._validate_path(claude_dir, command.path)
        except ValueError:
            command_path = command.path

        try:
            body = command_path.read_text(encoding="utf-8")
        except Exception as exc:
            self.notify(
                f"Failed to read {command.command}: {exc}",
                severity="error",
                timeout=3,
            )
            return

        # Build a formatted version with metadata
        meta_lines = [
            f"Command: {command.command}",
            f"Category: {command.category}",
            f"Complexity: {command.complexity}",
            f"Agents: {', '.join(command.agents) if command.agents else '—'}",
            f"Personas: {', '.join(command.personas) if command.personas else '—'}",
            f"MCP Servers: {', '.join(command.mcp_servers) if command.mcp_servers else '—'}",
            "",
            body,
        ]
        full_definition = "\n".join(meta_lines)

        if self._copy_to_clipboard(full_definition):
            self.notify(
                f"✓ Copied {command.command} to clipboard",
                severity="information",
                timeout=2,
            )
            self.status_message = f"Copied {command.command}"
        else:
            self.notify(
                "Failed to copy to clipboard",
                severity="error",
                timeout=3,
            )

    async def _show_task_details(self) -> None:
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task to view details", severity="warning", timeout=2)
            return
        tasks = getattr(self, "agent_tasks", [])
        if not tasks or index >= len(tasks):
            self.notify("No task details available", severity="warning", timeout=2)
            return
        task = tasks[index]
        lines = [
            f"Task: {task.agent_name}",
            f"Workstream: {task.workstream}",
            f"Category: {task.category}",
            f"Status: {task.status.title()}",
            f"Progress: {task.progress}%",
        ]
        if task.started:
            started_dt = datetime.fromtimestamp(task.started)
            lines.append(f"Started: {started_dt.isoformat(timespec='seconds')}")
        if task.completed:
            completed_dt = datetime.fromtimestamp(task.completed)
            lines.append(f"Completed: {completed_dt.isoformat(timespec='seconds')}")
        if task.source_path:
            lines.append(
                f"Source log: {task.source_path} (press L to stream, O to open externally)"
            )
        lines.append("")
        summary = task.description or "No summary captured for this task."
        lines.append("Summary:")
        lines.append(summary)
        if task.raw_notes:
            lines.append("")
            lines.append("Raw Notes:")
            lines.append(task.raw_notes)
        await self._show_text_dialog(f"Task · {task.agent_name}", "\n".join(lines))
        self.status_message = f"Viewing details for {task.agent_name}"
        self.refresh_status_bar()

    async def action_task_open_source(self) -> None:
        """Stream the underlying log file for the selected task."""
        if self.current_view != "tasks":
            self.notify("Switch to Tasks view to open logs", severity="warning", timeout=2)
            return
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task to open its log", severity="warning", timeout=2)
            return
        tasks = getattr(self, "agent_tasks", [])
        if not tasks or index >= len(tasks):
            self.notify("No task selected", severity="warning", timeout=2)
            return
        task = tasks[index]
        if not task.source_path:
            self.notify("Task has no associated log", severity="warning", timeout=2)
            return

        path = Path(task.source_path)
        try:
            claude_dir = _resolve_claude_dir()
            path = self._validate_path(claude_dir, path)
        except ValueError:
            path = Path(task.source_path)

        if not path.exists():
            self.notify("Log file missing", severity="error", timeout=2)
            return

        command = ["tail", "-n", "200", "-f", str(path)]
        self.run_worker(
            self._open_task_log(command, task.agent_name), exclusive=True
        )

    async def _open_task_log(self, command: List[str], label: str) -> None:
        await self.push_screen(
            LogViewerScreen(command, title=f"Task Log · {label}"),
            wait_for_dismiss=True,
        )
        self.status_message = f"Streaming log for {label}"
        self.refresh_status_bar()

    async def action_task_open_external(self) -> None:
        """Open the task log in the system viewer/editor."""
        if self.current_view != "tasks":
            self.notify("Switch to Tasks view to open logs", severity="warning", timeout=2)
            return
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task to open its log", severity="warning", timeout=2)
            return
        tasks = getattr(self, "agent_tasks", [])
        if not tasks or index >= len(tasks):
            self.notify("No task selected", severity="warning", timeout=2)
            return
        task = tasks[index]
        if not task.source_path:
            self.notify("Task has no associated log", severity="warning", timeout=2)
            return

        path = Path(task.source_path)
        try:
            claude_dir = _resolve_claude_dir()
            path = self._validate_path(claude_dir, path)
        except ValueError:
            path = Path(task.source_path)

        if not path.exists():
            self.notify("Log file missing", severity="error", timeout=2)
            return

        opened = self._open_path_external(path)
        if opened:
            self.status_message = f"Opened {path.name}"
            self.notify("Opened log in system viewer", severity="information", timeout=2)
        else:
            self.notify("Failed to open log", severity="error", timeout=2)

    def _open_path_external(self, path: Path) -> bool:
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            elif sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", str(path)])
            elif sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                return False
            return True
        except Exception:
            return False

    async def action_worktree_add(self) -> None:
        """Create a new git worktree."""
        if self.current_view != "worktrees":
            self.action_view_worktrees()

        branch = await self._prompt_text("New Worktree", "Branch name")
        if not branch:
            return

        default_path, _error = worktree_default_path(branch)
        path_value: Optional[str] = None
        if default_path:
            prompt = "Target path (optional)"
            path_input = await self._prompt_text(
                "Worktree Path",
                prompt,
                default=str(default_path),
            )
            if path_input is None:
                return
            try:
                if Path(path_input).expanduser().resolve() != default_path.resolve():
                    path_value = path_input
            except Exception:
                path_value = path_input
        else:
            path_input = await self._prompt_text(
                "Worktree Path", "Target path (optional)"
            )
            if path_input is None:
                return
            path_value = path_input or None

        exit_code, message = worktree_add(branch, path=path_value)
        clean = self._clean_ansi(message)
        if exit_code != 0:
            self.notify(clean or "Failed to add worktree", severity="error", timeout=3)
            return

        self.notify(clean or "Worktree created", severity="information", timeout=3)
        self.load_worktrees()
        self.update_view()

    async def action_worktree_open(self) -> None:
        """Open the selected worktree in the system file manager."""
        if self.current_view != "worktrees":
            self.action_view_worktrees()

        worktree = self._selected_worktree()
        if not worktree:
            self.notify("Select a worktree first", severity="warning", timeout=2)
            return

        opened = self._open_path_external(worktree.path)
        if opened:
            self.status_message = f"Opened {worktree.path}"
            self.notify("Opened worktree", severity="information", timeout=2)
        else:
            self.notify("Failed to open worktree", severity="error", timeout=2)

    async def action_worktree_remove(self) -> None:
        """Remove the selected worktree."""
        if self.current_view != "worktrees":
            self.action_view_worktrees()

        worktree = self._selected_worktree()
        if not worktree:
            self.notify("Select a worktree first", severity="warning", timeout=2)
            return
        if worktree.is_main:
            self.notify("Cannot remove the main worktree", severity="warning", timeout=2)
            return

        confirm = await self.push_screen(
            ConfirmDialog("Remove Worktree", f"Remove {worktree.path}?"),
            wait_for_dismiss=True,
        )
        if not confirm:
            return

        exit_code, message = worktree_remove(str(worktree.path))
        clean = self._clean_ansi(message)
        if exit_code != 0:
            self.notify(clean or "Failed to remove worktree", severity="error", timeout=3)
            return

        self.notify(clean or "Worktree removed", severity="information", timeout=2)
        self.load_worktrees()
        self.update_view()

    async def action_worktree_prune(self) -> None:
        """Prune stale worktrees."""
        if self.current_view != "worktrees":
            self.action_view_worktrees()

        confirm = await self.push_screen(
            ConfirmDialog("Prune Worktrees", "Prune stale worktrees?"),
            wait_for_dismiss=True,
        )
        if not confirm:
            return

        exit_code, message = worktree_prune()
        clean = self._clean_ansi(message)
        if exit_code != 0:
            self.notify(clean or "Failed to prune worktrees", severity="error", timeout=3)
            return

        if clean:
            await self._show_text_dialog("Worktree Prune", clean)
        self.load_worktrees()
        self.update_view()

    async def action_worktree_set_base_dir(self) -> None:
        """Set or clear the worktree base directory."""
        if self.current_view != "worktrees":
            self.action_view_worktrees()

        current_dir = self.worktree_base_dir
        prompt = "Base directory (enter '-' to clear)"
        default_value = str(current_dir) if current_dir else ""
        value = await self._prompt_text(
            "Worktree Base Directory",
            prompt,
            default=default_value,
        )
        if value is None:
            return

        if value.strip() == "-":
            exit_code, message = worktree_clear_base_dir()
        else:
            exit_code, message = worktree_set_base_dir(value)

        clean = self._clean_ansi(message)
        if exit_code != 0:
            self.notify(clean or "Failed to update base directory", severity="error", timeout=3)
            return

        self.notify(clean or "Base directory updated", severity="information", timeout=2)
        self.load_worktrees()
        self.update_view()

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
        dialog = PromptDialog(
            "Export Context", "Write export to path", default=default_path
        )
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
            self.notify(self.status_message, severity="information", timeout=2)
        else:
            self.status_message = clean or "Export failed"
            self.notify(self.status_message, severity="error", timeout=3)

    async def action_export_clipboard(self) -> None:
        """Generate export and copy it to the clipboard."""
        if self.current_view != "export":
            self.action_view_export()

        exclude = self._export_exclude_categories()
        tmp_path = Path(tempfile.gettempdir()) / "cortex-export.md"
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
            self.notify("Copied export to clipboard", severity="information", timeout=2)
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
        if not self._ensure_configured_mcp(server, "validating"):
            return

        valid, errors, warnings = validate_server_config(server.name)
        if valid:
            note = "All checks passed"
            if warnings:
                note = warnings[0]
            self.notify(f"{server.name}: {note}", severity="information", timeout=2)
        else:
            self.notify(
                errors[0] if errors else "Validation failed",
                severity="error",
                timeout=3,
            )

    async def action_mcp_details(self) -> None:
        """Show detailed information for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return
        if not self._ensure_configured_mcp(server, "viewing details"):
            return

        exit_code, output = mcp_show(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return

        await self.push_screen(
            TextViewerDialog(f"MCP: {server.name}", output), wait_for_dismiss=True
        )

    async def action_mcp_docs(self) -> None:
        """Open MCP documentation for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return
        if getattr(server, "doc_only", False):
            if server.docs_path and server.docs_path.exists():
                try:
                    content = server.docs_path.read_text(encoding="utf-8")
                except OSError as exc:
                    self.notify(
                        f"Failed to read docs: {exc}", severity="error", timeout=3
                    )
                    return
                await self.push_screen(
                    TextViewerDialog(f"Docs: {server.name}", content),
                    wait_for_dismiss=True,
                )
            else:
                self.notify(
                    "Documentation file missing", severity="warning", timeout=2
                )
            return
        exit_code, output = mcp_docs(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return

        await self.push_screen(
            TextViewerDialog(f"Docs: {server.name}", output), wait_for_dismiss=True
        )

    async def action_mcp_snippet(self) -> None:
        """Generate config snippet for the selected server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return
        if not self._ensure_configured_mcp(server, "generating a config snippet"):
            return

        snippet = generate_config_snippet(
            server.name, server.command, args=server.args, env=server.env
        )
        await self.push_screen(
            TextViewerDialog(f"Snippet: {server.name}", snippet), wait_for_dismiss=True
        )
        if self._copy_to_clipboard(snippet):
            self.notify("Snippet copied", severity="information", timeout=2)
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
        if not self._ensure_configured_mcp(server, "testing"):
            return

        exit_code, output = mcp_test(server.name)
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return
        await self.push_screen(
            TextViewerDialog(f"Test: {server.name}", output), wait_for_dismiss=True
        )

    async def action_context_delete(self) -> None:
        """Contextual delete/diagnose handler for D."""
        if self.current_view == "mcp":
            await self.action_mcp_diagnose()
            return
        if self.current_view == "profiles":
            await self.action_profile_delete()
            return
        if self.current_view == "memory":
            self.action_memory_delete_note()
            return

    async def action_context_browse_or_base(self) -> None:
        """Contextual MCP browse or worktree base dir handler for B."""
        if self.current_view == "worktrees":
            await self.action_worktree_set_base_dir()
            return
        self.action_mcp_browse_install()

    async def action_mcp_diagnose(self) -> None:
        """Run diagnostics across all MCP servers."""
        exit_code, output = mcp_diagnose()
        if exit_code != 0:
            self.notify(output, severity="error", timeout=3)
            return
        await self.push_screen(
            TextViewerDialog("MCP Diagnose", output), wait_for_dismiss=True
        )

    async def action_mcp_add(self) -> None:
        """Add a new MCP server."""
        dialog = MCPServerDialog("Add MCP Server")
        result = await self.push_screen(dialog, wait_for_dismiss=True)

        if result:
            success, message = add_mcp_server(
                name=result["name"],
                command=result["command"],
                args=result.get("args", []),
                description=result.get("description", ""),
            )
            if success:
                self.notify(message, severity="information", timeout=2)
                self.load_mcp_servers()
                self.update_view()
            else:
                self.notify(message, severity="error", timeout=3)

    def action_mcp_browse_install(self) -> None:
        """Browse and install MCP servers from registry."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        # Step 1: Browse and select a server
        browse_dialog = MCPBrowseDialog()
        self.push_screen(browse_dialog, callback=self._handle_mcp_browse_result)

    def _handle_mcp_browse_result(self, server_name: Optional[str]) -> None:
        """Handle result from MCP browse dialog."""
        if not server_name:
            return

        # Step 2: Configure and install
        install_dialog = MCPInstallDialog(server_name)
        self.push_screen(install_dialog, callback=self._handle_mcp_install_result)

    def _handle_mcp_install_result(self, config: Optional[Dict[str, Any]]) -> None:
        """Handle result from MCP install dialog."""
        if not config:
            return

        # Step 3: Perform installation
        server = get_server(config["server_name"])
        if not server:
            self.notify(f"Server not found", severity="error", timeout=3)
            return

        self.notify(f"Installing {server.name}...", severity="information", timeout=2)

        result = install_and_configure(
            server=server,
            env_values=config.get("env_values", {}),
        )

        if result.success:
            message = f"✓ {server.name} installed and configured"
            if result.warnings:
                message += f" ({len(result.warnings)} warnings)"
            self.notify(message, severity="information", timeout=3)
            self.load_mcp_servers()
            self.update_view()
        else:
            self.notify(f"Failed: {result.message}", severity="error", timeout=4)

    async def action_mcp_edit(self) -> None:
        """Edit the selected MCP server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return
        if not self._ensure_configured_mcp(server, "editing"):
            return

        # Prepare defaults for dialog
        defaults: MCPServerData = {
            "name": server.name,
            "command": server.command,
            "args": list(server.args),
            "description": server.description or "",
        }

        dialog = MCPServerDialog(f"Edit MCP Server: {server.name}", defaults=defaults)
        result = await self.push_screen(dialog, wait_for_dismiss=True)

        if result:
            success, message = update_mcp_server(
                name=result["name"],
                command=result["command"],
                args=result.get("args", []),
                description=result.get("description", ""),
            )
            if success:
                self.notify(message, severity="information", timeout=2)
                self.load_mcp_servers()
                self.update_view()
            else:
                self.notify(message, severity="error", timeout=3)

    async def action_mcp_remove(self) -> None:
        """Remove the selected MCP server."""
        if self.current_view != "mcp":
            self.action_view_mcp()

        server = self._selected_mcp_server()
        if not server:
            self.notify("Select an MCP server", severity="warning", timeout=2)
            return
        if not self._ensure_configured_mcp(server, "removing"):
            return

        # Confirm deletion
        confirmed = await self.push_screen(
            ConfirmDialog(
                f"Remove MCP server '{server.name}'?",
                "This will remove the server from your Claude Desktop configuration.",
            ),
            wait_for_dismiss=True,
        )

        if confirmed:
            success, message = remove_mcp_server(server.name)
            if success:
                self.notify(message, severity="information", timeout=2)
                self.load_mcp_servers()
                self.update_view()
            else:
                self.notify(message, severity="error", timeout=3)

    def action_auto_activate(self) -> None:
        """Auto-activate agents or add task when in Tasks view."""
        if self.current_view == "tasks":
            dialog = TaskEditorDialog("Add Task")
            self.push_screen(dialog, callback=self._handle_add_task)
            return

        if not hasattr(self, "intelligent_agent"):
            self.notify("AI Assistant not initialized", severity="error", timeout=2)
            return

        auto_agents = self.intelligent_agent.get_auto_activations()

        if not auto_agents:
            self.notify(
                "No auto-activation recommendations", severity="information", timeout=2
            )
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
            self.notify(
                f"✓ Auto-activated {activated_count} agents",
                severity="information",
                timeout=3,
            )
            self.load_agents()
            self.update_view()
        else:
            self.notify("Failed to auto-activate agents", severity="error", timeout=2)

    async def action_design_ui(self) -> None:
        """Trigger the Design UI flow."""
        prompt = await self._prompt_text(
            "Design UI", 
            "Describe the UI component you want to build:",
            placeholder="e.g. A Solarpunk renewable energy dashboard"
        )
        if not prompt:
            return

        # Activate the skill and trigger the command
        # In a real implementation, this might spawn a task or just notify the user
        self.notify(f"🎨 Designing UI: {prompt}", severity="information", timeout=3)
        # Note: In the TUI we don't have a direct 'chat' to send /design:ui to,
        # but we can log the intent or spawn an LLM task.
        await self.action_assign_llm_tasks(
            purpose=f"Design UI: {prompt}",
            prompt=f"Use /design:ui {prompt}",
            diff_text=None
        )

    async def action_rag_ingest(self) -> None:
        """Trigger the RAG Ingestion flow."""
        path_str = await self._prompt_text(
            "RAG Ingest", 
            "Enter file or directory path to ingest:",
            default="."
        )
        if not path_str:
            return

        self.notify(f"📂 Ingesting {path_str} with contextual awareness...", severity="information")
        
        # We'll run this in a thread to avoid blocking the TUI
        def do_ingest():
            try:
                from ..core import rag
                ingester = rag.ContextualIngester()
                path = Path(path_str)
                if path.is_file():
                    ingester.ingest_file(path)
                elif path.is_dir():
                    for file_path in path.rglob("*"):
                        if file_path.is_file() and file_path.suffix in [".md", ".txt", ".py", ".js", ".ts"]:
                            ingester.ingest_file(file_path)
                self.call_from_thread(self.notify, "✓ Ingestion complete", severity="information")
            except Exception as e:
                self.call_from_thread(self.notify, f"✗ Ingestion failed: {e}", severity="error")

        threading.Thread(target=do_ingest, daemon=True).start()

    def action_request_reviews(self) -> None:
        """Spawn review tasks from AI recommendations."""
        if not hasattr(self, "intelligent_agent"):
            self.notify("AI Assistant not initialized", severity="error", timeout=2)
            return

        self.intelligent_agent.analyze_context()
        recommendations = self.intelligent_agent.get_recommendations()
        if not recommendations:
            self.notify("No recommendations to request", severity="warning", timeout=2)
            return

        review_recs, _ = self._split_review_recommendations(recommendations)
        if not review_recs:
            self.notify("No review recommendations found", severity="warning", timeout=2)
            return

        review_recs = review_recs[:10]
        cli_available = shutil.which("claude") is not None
        output_dir = self._review_output_dir() if cli_available else None
        context = getattr(self.intelligent_agent, "current_context", None)
        diff_text = self._get_git_diff()
        if diff_text and output_dir is not None:
            try:
                (output_dir / "diff.txt").write_text(diff_text, encoding="utf-8")
            except Exception as exc:
                self.notify(
                    f"Failed to write diff.txt: {exc}",
                    severity="warning",
                    timeout=3,
                )

        tasks = list(getattr(self, "agent_tasks", []))
        existing_open = {
            t.agent_name.lower()
            for t in tasks
            if t.category == "review" and t.status in {"pending", "running"}
        }

        created = 0
        spawn_specs: List[Tuple[str, str, str, Path]] = []
        for rec in review_recs:
            agent_name = rec.agent_name.strip()
            if not agent_name:
                continue
            agent_slug = self._resolve_agent_slug(agent_name)
            if agent_slug.lower() in existing_open:
                continue

            if not self._ensure_agent_active(agent_slug):
                continue

            confidence_pct = int(rec.confidence * 100)
            description = f"{rec.reason} (confidence {confidence_pct}%)"
            slug = re.sub(r"[^a-z0-9]+", "-", agent_slug.lower()).strip("-") or "review"
            output_path = (
                output_dir / f"{slug}.txt" if output_dir is not None else None
            )
            status = "running" if cli_available else "pending"
            started = time.time() if cli_available else None
            task_id = self._generate_task_id(f"review-{agent_slug}")
            tasks.append(
                AgentTask(
                    agent_id=task_id,
                    agent_name=agent_slug,
                    workstream="reviews",
                    status=status,
                    progress=0,
                    category="review",
                    started=started,
                    completed=None,
                    description=description,
                    raw_notes=description,
                    source_path=str(output_path) if output_path is not None else None,
                )
            )
            if cli_available and output_path is not None:
                prompt = self._build_review_prompt(agent_slug, rec, context, diff_text)
                spawn_specs.append((task_id, agent_slug, prompt, output_path))
            existing_open.add(agent_slug.lower())
            created += 1

        if created == 0:
            self.notify("Review tasks already requested", severity="information", timeout=2)
            return

        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()
        self.status_message = f"Requested {created} review task(s)"
        self.notify(
            f"✓ Requested {created} review task(s)",
            severity="information",
            timeout=2,
        )

        if not cli_available:
            self.notify(
                "Claude CLI not found. Tasks queued without execution.",
                severity="warning",
                timeout=3,
            )
            return

        for task_id, agent_name, prompt, output_path in spawn_specs:
            self._spawn_review_cli_task(
                task_id=task_id,
                agent_name=agent_name,
                prompt=prompt,
                output_path=output_path,
            )

    def action_assign_llm_tasks(self) -> None:
        """Spawn LLM consult tasks for Gemini/OpenAI/Qwen."""
        self.run_worker(self._assign_llm_tasks_flow(), exclusive=True)

    async def _assign_llm_tasks_flow(self) -> None:
        purpose = await self._prompt_text(
            "Assign LLM Tasks",
            "Purpose (second-opinion | plan | review | delegate)",
            default="second-opinion",
            placeholder="second-opinion",
        )
        if not purpose:
            return

        prompt = ""
        editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"
        tmp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".md", mode="w", encoding="utf-8"
            ) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(
                    "# LLM Task Prompt\n"
                    "# Write the prompt below. Lines starting with '#' are ignored.\n\n"
                )
            editor_cmd = shlex.split(editor)
            if not editor_cmd:
                editor_cmd = ["vi"]
            try:
                with self.suspend():
                    subprocess.run([*editor_cmd, str(tmp_path)], check=False)
            except SuspendNotSupported:
                raise RuntimeError("Terminal suspend is not supported") from None
            raw = tmp_path.read_text(encoding="utf-8")
            prompt_lines = [
                line for line in raw.splitlines() if not line.strip().startswith("#")
            ]
            prompt = "\n".join(prompt_lines).strip()
        except Exception as exc:
            self.notify(
                f"Failed to open editor: {exc}. Using inline prompt.",
                severity="warning",
                timeout=3,
            )
            prompt = await self._prompt_text(
                "Assign LLM Tasks",
                "Prompt for LLMs",
                placeholder="What should the other LLMs do?",
            )
            if not prompt:
                return
        finally:
            try:
                if tmp_path and tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass

        if not prompt:
            use_inline = bool(
                await self.push_screen(
                    ConfirmDialog(
                        "Assign LLM Tasks",
                        "Prompt is empty. Use inline prompt instead?",
                    ),
                    wait_for_dismiss=True,
                )
            )
            if not use_inline:
                return
            prompt = await self._prompt_text(
                "Assign LLM Tasks",
                "Prompt for LLMs",
                placeholder="What should the other LLMs do?",
            )
            if not prompt:
                return

        diff_text = self._get_git_diff()
        include_diff = False
        if diff_text:
            include_diff = bool(
                await self.push_screen(
                    ConfirmDialog(
                        "Include git diff?",
                        "Attach the current git diff to all LLM tasks?",
                    ),
                    wait_for_dismiss=True,
                )
            )

        self._queue_llm_tasks(
            purpose.strip(),
            prompt.strip(),
            diff_text if include_diff else None,
        )

    def _queue_llm_tasks(
        self, purpose: str, prompt: str, diff_text: Optional[str]
    ) -> None:
        providers = [
            ("Gemini", "gemini"),
            ("OpenAI", "openai"),
            ("Qwen", "qwen"),
        ]

        script_path = self._llm_consult_script_path()
        script_available = script_path is not None
        output_dir = self._llm_output_dir() if script_available else None

        context_file: Optional[Path] = None
        if diff_text and output_dir is not None:
            context_file = output_dir / "diff.txt"
            try:
                context_file.write_text(diff_text, encoding="utf-8")
            except Exception as exc:
                self.notify(
                    f"Failed to write diff.txt: {exc}",
                    severity="warning",
                    timeout=3,
                )
                context_file = None

        tasks = list(getattr(self, "agent_tasks", []))
        existing_open = {
            t.agent_name.lower()
            for t in tasks
            if t.category == "llm" and t.status in {"pending", "running"}
        }

        summary = self._summarize_prompt(prompt)
        description = f"{purpose}: {summary}" if summary else purpose

        created = 0
        spawn_specs: List[Tuple[str, str, str, str, Path, Optional[Path]]] = []
        for display_name, provider_key in providers:
            if display_name.lower() in existing_open:
                continue

            output_path = (
                output_dir / f"{provider_key}.txt" if output_dir is not None else None
            )
            status = "running" if script_available and output_path is not None else "pending"
            started = time.time() if status == "running" else None
            task_id = self._generate_task_id(f"llm-{provider_key}")

            tasks.append(
                AgentTask(
                    agent_id=task_id,
                    agent_name=display_name,
                    workstream="llm",
                    status=status,
                    progress=0,
                    category="llm",
                    started=started,
                    completed=None,
                    description=description,
                    raw_notes=prompt,
                    source_path=str(output_path) if output_path is not None else None,
                )
            )
            if script_available and output_path is not None and script_path is not None:
                spawn_specs.append(
                    (
                        task_id,
                        provider_key,
                        purpose,
                        prompt,
                        output_path,
                        context_file,
                    )
                )
            existing_open.add(display_name.lower())
            created += 1

        if created == 0:
            self.notify("LLM tasks already requested", severity="information", timeout=2)
            return

        self._save_tasks(tasks)
        self.load_agent_tasks()
        self.update_view()
        self.status_message = f"Requested {created} LLM task(s)"
        self.notify(
            f"✓ Requested {created} LLM task(s)",
            severity="information",
            timeout=2,
        )

        if not script_available or script_path is None:
            self.notify(
                "LLM consult script missing. Tasks queued without execution.",
                severity="warning",
                timeout=3,
            )
            return

        for task_id, provider_key, purpose, prompt, output_path, context_file in spawn_specs:
            self._spawn_llm_consult_task(
                task_id=task_id,
                provider_key=provider_key,
                purpose=purpose,
                prompt=prompt,
                output_path=output_path,
                script_path=script_path,
                context_file=context_file,
            )

    def action_consult_gemini(self) -> None:
        """Consult Gemini with a user-provided prompt."""
        self.run_worker(self._consult_gemini_flow(), exclusive=True)

    async def _consult_gemini_flow(self) -> None:
        purpose = await self._prompt_text(
            "Gemini Consult",
            "Purpose (second-opinion | plan | review | delegate)",
            default="second-opinion",
            placeholder="second-opinion",
        )
        if not purpose:
            return

        prompt = ""
        editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vi"
        tmp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".md", mode="w", encoding="utf-8"
            ) as tmp:
                tmp_path = Path(tmp.name)
                tmp.write(
                    "# Gemini Consult Prompt\n"
                    "# Write the prompt below. Lines starting with '#' are ignored.\n\n"
                )
            editor_cmd = shlex.split(editor)
            if not editor_cmd:
                editor_cmd = ["vi"]
            try:
                with self.suspend():
                    subprocess.run([*editor_cmd, str(tmp_path)], check=False)
            except SuspendNotSupported:
                raise RuntimeError("Terminal suspend is not supported") from None
            raw = tmp_path.read_text(encoding="utf-8")
            prompt_lines = [
                line for line in raw.splitlines() if not line.strip().startswith("#")
            ]
            prompt = "\n".join(prompt_lines).strip()
        except Exception as exc:
            self.notify(
                f"Failed to open editor: {exc}. Using inline prompt.",
                severity="warning",
                timeout=3,
            )
            prompt = await self._prompt_text(
                "Gemini Consult",
                "Prompt for Gemini",
                placeholder="What should Gemini evaluate?",
            )
            if not prompt:
                return
        finally:
            try:
                if tmp_path and tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass

        if not prompt:
            use_inline = bool(
                await self.push_screen(
                    ConfirmDialog(
                        "Gemini Consult",
                        "Prompt is empty. Use inline prompt instead?",
                    ),
                    wait_for_dismiss=True,
                )
            )
            if not use_inline:
                return
            prompt = await self._prompt_text(
                "Gemini Consult",
                "Prompt for Gemini",
                placeholder="What should Gemini evaluate?",
            )
            if not prompt:
                return

        diff_text = self._get_git_diff()
        include_diff = False
        if diff_text:
            include_diff = bool(
                await self.push_screen(
                    ConfirmDialog(
                        "Include git diff?",
                        "Attach the current git diff as context for Gemini?",
                    ),
                    wait_for_dismiss=True,
                )
            )

        await self._run_gemini_consult(
            purpose.strip(),
            prompt.strip(),
            diff_text if include_diff else None,
        )

    async def _run_gemini_consult(
        self, purpose: str, prompt: str, diff_text: Optional[str]
    ) -> None:
        script_path = self._llm_consult_script_path()
        if script_path is None:
            self.notify(
                "Gemini consult script missing: skills/multi-llm-consult/scripts/consult_llm.py",
                severity="error",
                timeout=3,
            )
            return

        temp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        context_file: Optional[Path] = None
        if diff_text:
            temp_dir = tempfile.TemporaryDirectory()
            context_file = Path(temp_dir.name) / "diff.txt"
            try:
                context_file.write_text(diff_text, encoding="utf-8")
            except Exception as exc:
                self.notify(f"Failed to write diff context: {exc}", severity="warning", timeout=3)
                context_file = None

        cmd = [
            sys.executable,
            str(script_path),
            "--provider",
            "gemini",
            "--purpose",
            purpose,
            "--prompt",
            prompt,
        ]
        if context_file is not None:
            cmd += ["--context-file", str(context_file)]

        self.notify("Consulting Gemini...", severity="information", timeout=2)

        def runner() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )

        result = await asyncio.to_thread(runner)
        if temp_dir is not None:
            temp_dir.cleanup()

        output = (result.stdout or "").strip()
        errors = (result.stderr or "").strip()
        if result.returncode != 0:
            message = errors or output or "Gemini consult failed"
            await self._show_text_dialog("Gemini Consult Error", message)
            self.notify("Gemini consult failed", severity="error", timeout=3)
            return

        if not output:
            output = "Gemini returned no output."
        await self._show_text_dialog("Gemini Consult", output)

    def _check_auto_activations(self) -> None:
        """Check for high-confidence auto-activations on startup."""
        if not hasattr(self, "intelligent_agent"):
            return

        auto_agents = self.intelligent_agent.get_auto_activations()

        if auto_agents:
            agents_str = ", ".join(auto_agents[:3])
            if len(auto_agents) > 3:
                agents_str += f" +{len(auto_agents) - 3} more"

            self.notify(
                f"🤖 AI Suggestion: {agents_str} (Press 'A' to auto-activate)",
                severity="information",
                timeout=5,
            )

    def _handle_add_task(self, result: Optional[TaskEditorData]) -> None:
        if not result:
            return
        try:
            payload = dict(result)
            payload.setdefault("raw_notes", payload.get("description", ""))
            self._upsert_task(None, payload)
            self.current_view = "tasks"
            self.status_message = f"Created task {result.get('name', '')}"
            self.notify("✓ Task added", severity="information", timeout=2)
        except Exception as exc:
            self.notify(f"Failed to add task: {exc}", severity="error", timeout=3)

    def action_edit_task(self) -> None:
        index = self._selected_task_index()
        if index is None:
            self.notify("Select a task in Tasks view", severity="warning", timeout=2)
            return
        task = self.agent_tasks[index]
        defaults: TaskEditorData = {
            "name": task.agent_name,
            "workstream": task.workstream,
            "category": task.category,
            "status": task.status,
            "progress": str(task.progress),
            "description": task.description,
            "raw_notes": task.raw_notes,
        }
        dialog = TaskEditorDialog("Edit Task", defaults=defaults)
        self.push_screen(
            dialog,
            callback=lambda result, agent_id=task.agent_id, label=task.agent_name: self._handle_edit_task(
                agent_id, label, result
            ),
        )

    def _handle_edit_task(
        self, agent_id: str, label: str, result: Optional[TaskEditorData]
    ) -> None:
        if not result:
            return
        try:
            payload = dict(result)
            payload["raw_notes"] = result.get("raw_notes", "")
            self._upsert_task(agent_id, payload)
            self.status_message = f"Updated task {label}"
            self.notify("✓ Task updated", severity="information", timeout=2)
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
            callback=lambda confirm, agent_id=task.agent_id, label=task.agent_name: self._handle_delete_task(
                agent_id, label, confirm
            ),
        )

    def _handle_delete_task(self, agent_id: str, label: str, confirm: bool) -> None:
        if not confirm:
            return
        self._remove_task(agent_id)
        self.status_message = f"Deleted task {label}"
        self.notify("✓ Task deleted", severity="information", timeout=2)

    def action_toggle(self) -> None:  # type: ignore[override]
        """Toggle selected item."""
        if self.wizard_active:
            self.action_wizard_toggle()
            return

        if self.current_view == "flags":
            self.action_flag_category_toggle()
            return

        if self.current_view == "flag_manager":
            self.action_flag_manager_toggle()
            return

        if self.current_view == "profiles":
            self.action_profile_apply()
            return

        if self.current_view == "watch_mode":
            # Toggle watch mode start/stop
            if self.watch_mode_instance and self.watch_mode_instance.running:
                self.action_watch_stop()
            else:
                self.action_watch_start()
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
                self.status_message = (
                    "Agent generic" if self.export_agent_generic else "Claude format"
                )
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
                                    self.notify(
                                        f"✓ Deactivated {agent.name}",
                                        severity="information",
                                        timeout=2,
                                    )
                                else:
                                    self.notify(
                                        f"✓ Activated {agent.name}",
                                        severity="information",
                                        timeout=2,
                                    )
                                self.load_agents()
                                self.update_view()

                                # Restore cursor to same position (showing next agent)
                                table = self.query_one(DataTable)
                                if table.row_count > 0:
                                    # Keep at same index, or last row if we were at the end
                                    new_cursor_row = min(
                                        saved_cursor_row, table.row_count - 1
                                    )
                                    table.move_cursor(row=new_cursor_row)
                            else:
                                self.notify(
                                    f"✗ Failed to toggle {agent.name}",
                                    severity="error",
                                    timeout=3,
                                )
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(
                                f"✗ Error: {str(e)[:50]}", severity="error", timeout=3
                            )

        elif self.current_view == "rules":
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
                    rule_name = plain_text.strip()
                    if rule_name and len(rule_name) > 0 and ord(rule_name[0]) > 127:
                        rule_name = rule_name[1:].strip()

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
                                self.notify(
                                    f"✓ Deactivated {rule.name}",
                                    severity="information",
                                    timeout=2,
                                )
                            else:
                                self.notify(
                                    f"✓ Activated {rule.name}",
                                    severity="information",
                                    timeout=2,
                                )

                            self.load_rules()
                            self.update_view()

                            # Restore cursor to same position (showing next rule)
                            table = self.query_one(DataTable)
                            if table.row_count > 0:
                                new_cursor_row = min(
                                    saved_cursor_row, table.row_count - 1
                                )
                                table.move_cursor(row=new_cursor_row)
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(
                                f"✗ Error: {str(e)[:50]}", severity="error", timeout=3
                            )

        elif self.current_view == "modes":
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
                    mode_name = plain_text.strip()
                    if mode_name and len(mode_name) > 0 and ord(mode_name[0]) > 127:
                        mode_name = mode_name[1:].strip()

                    mode = next((m for m in self.modes if m.name == mode_name), None)
                    if mode:
                        try:
                            if mode.status == "active":
                                # Use intelligent deactivation
                                exit_code, message, affected_modes = mode_deactivate_intelligent(
                                    mode.path.stem
                                )
                            else:
                                # Use intelligent activation
                                exit_code, message, deactivated_modes = mode_activate_intelligent(
                                    mode.path.stem
                                )

                            # Remove ANSI codes
                            import re

                            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                            self.status_message = clean_message.split("\n")[0]

                            if exit_code == 0:
                                if mode.status == "active":
                                    # Deactivation successful
                                    notify_msg = f"✓ Deactivated {mode.name}"
                                    if affected_modes:
                                        notify_msg += f" (affects: {', '.join(affected_modes)})"
                                    self.notify(
                                        notify_msg,
                                        severity="warning"
                                        if affected_modes
                                        else "information",
                                        timeout=3 if affected_modes else 2,
                                    )
                                else:
                                    # Activation successful
                                    notify_msg = f"✓ Activated {mode.name}"
                                    if deactivated_modes:
                                        notify_msg += f" (auto-deactivated: {', '.join(deactivated_modes)})"
                                    self.notify(
                                        notify_msg,
                                        severity="information",
                                        timeout=3 if deactivated_modes else 2,
                                    )
                                self.load_modes()
                                self.update_view()

                                # Restore cursor to same position (showing next mode)
                                table = self.query_one(DataTable)
                                if table.row_count > 0:
                                    new_cursor_row = min(
                                        saved_cursor_row, table.row_count - 1
                                    )
                                    table.move_cursor(row=new_cursor_row)
                            else:
                                # Show error message
                                self.notify(
                                    f"✗ {clean_message}",
                                    severity="error",
                                    timeout=5,
                                )
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(
                                f"✗ Error: {str(e)[:50]}", severity="error", timeout=3
                            )

        elif self.current_view == "prompts":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                saved_cursor_row = table.cursor_row
                index = table.cursor_row
                if 0 <= index < len(self.prompts):
                    prompt = self.prompts[index]
                    try:
                        from ..core.prompts import prompt_activate, prompt_deactivate

                        if prompt.status == "active":
                            exit_code, message = prompt_deactivate(prompt.slug)
                        else:
                            exit_code, message = prompt_activate(prompt.slug)

                        # Remove ANSI codes
                        import re
                        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                        self.status_message = clean_message.split("\n")[0]

                        if exit_code == 0:
                            if prompt.status == "active":
                                self.notify(
                                    f"✓ Deactivated prompt: {prompt.slug}",
                                    severity="information",
                                    timeout=2,
                                )
                            else:
                                self.notify(
                                    f"✓ Activated prompt: {prompt.slug}",
                                    severity="information",
                                    timeout=2,
                                )
                            self.load_prompts()
                            self.update_view()

                            # Restore cursor position
                            table = self.query_one(DataTable)
                            if table.row_count > 0:
                                new_cursor_row = min(saved_cursor_row, table.row_count - 1)
                                table.move_cursor(row=new_cursor_row)
                        else:
                            self.notify(
                                f"✗ {clean_message}",
                                severity="error",
                                timeout=5,
                            )
                    except Exception as e:
                        self.status_message = f"Error: {e}"
                        self.notify(
                            f"✗ Error: {str(e)[:50]}", severity="error", timeout=3
                        )

        elif self.current_view == "principles":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                saved_cursor_row = table.cursor_row
                row_key = table.get_row_at(table.cursor_row)
                if row_key and len(row_key) > 0:
                    from rich.text import Text

                    raw_name = str(row_key[0])
                    plain_text = Text.from_markup(raw_name).plain
                    snippet_name = plain_text.strip()
                    if (
                        snippet_name
                        and len(snippet_name) > 0
                        and ord(snippet_name[0]) > 127
                    ):
                        snippet_name = snippet_name[1:].strip()

                    snippet = next(
                        (p for p in self.principles if p.name == snippet_name),
                        None,
                    )
                    if snippet:
                        try:
                            if snippet.status == "active":
                                exit_code, message = principles_deactivate(
                                    snippet.path.stem
                                )
                            else:
                                exit_code, message = principles_activate(
                                    snippet.path.stem
                                )

                            import re

                            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                            self.status_message = clean_message.split("\n")[0]

                            if exit_code == 0:
                                if snippet.status == "active":
                                    self.notify(
                                        f"✓ Deactivated {snippet.name}",
                                        severity="information",
                                        timeout=2,
                                    )
                                else:
                                    self.notify(
                                        f"✓ Activated {snippet.name}",
                                        severity="information",
                                        timeout=2,
                                    )
                                self.load_principles()
                                self.update_view()

                                table = self.query_one(DataTable)
                                if table.row_count > 0:
                                    new_cursor_row = min(
                                        saved_cursor_row, table.row_count - 1
                                    )
                                    table.move_cursor(row=new_cursor_row)
                            else:
                                self.notify(
                                    f"✗ {clean_message}",
                                    severity="error",
                                    timeout=3,
                                )
                        except Exception as e:
                            self.status_message = f"Error: {e}"
                            self.notify(
                                f"✗ Error: {str(e)[:50]}",
                                severity="error",
                                timeout=3,
                            )

        elif self.current_view == "mcp":
            table = self.query_one(DataTable)
            if table.cursor_row is not None:
                saved_cursor_row = table.cursor_row
                row_key = table.get_row_at(table.cursor_row)

                if row_key and len(row_key) > 0:
                    from rich.text import Text

                    raw_name = str(row_key[0])
                    plain_text = Text.from_markup(raw_name).plain
                    item_name = plain_text.strip()
                    # Remove icon emoji if present
                    if item_name and len(item_name) > 0 and ord(item_name[0]) > 127:
                        item_name = item_name[1:].strip()

                    # Check if it's an MCP doc (type column = "doc")
                    type_col = str(row_key[1]) if len(row_key) > 1 else ""
                    type_text = Text.from_markup(type_col).plain.strip()

                    if type_text == "doc":
                        doc = next((d for d in self.mcp_docs if d.name == item_name), None)
                        if doc:
                            try:
                                import re
                                if doc.status == "active":
                                    exit_code, message = mcp_deactivate(doc.name)
                                else:
                                    exit_code, message = mcp_activate(doc.name)

                                clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                                self.status_message = clean_message.split("\n")[0]

                                if exit_code == 0:
                                    if doc.status == "active":
                                        self.notify(
                                            f"✓ Deactivated {doc.name}",
                                            severity="warning",
                                            timeout=2,
                                        )
                                    else:
                                        self.notify(
                                            f"✓ Activated {doc.name}",
                                            severity="information",
                                            timeout=2,
                                        )
                                    self.load_mcp_docs()
                                    self.update_view()

                                    table = self.query_one(DataTable)
                                    if table.row_count > 0:
                                        new_cursor_row = min(
                                            saved_cursor_row, table.row_count - 1
                                        )
                                        table.move_cursor(row=new_cursor_row)
                                else:
                                    self.notify(
                                        f"✗ {clean_message}",
                                        severity="error",
                                        timeout=5,
                                    )
                            except Exception as e:
                                self.status_message = f"Error: {e}"
                                self.notify(
                                    f"✗ Error: {str(e)[:50]}", severity="error", timeout=3
                                )

    def action_refresh(self) -> None:
        """Refresh current view."""
        if self.current_view == "agents":
            self.load_agents()
        elif self.current_view == "principles":
            self.load_principles()
        elif self.current_view == "rules":
            self.load_rules()
        elif self.current_view == "modes":
            self.load_modes()
        elif self.current_view == "prompts":
            self.load_prompts()
        elif self.current_view == "skills":
            self.load_skills()
        elif self.current_view == "commands":
            self.load_slash_commands()
        elif self.current_view == "workflows":
            self.load_workflows()
        elif self.current_view == "worktrees":
            self.load_worktrees()
        elif self.current_view == "scenarios":
            self.load_scenarios()
        elif self.current_view == "orchestrate":
            self.load_agent_tasks()
        elif self.current_view == "tasks":
            self.load_agent_tasks()
        elif self.current_view == "mcp":
            self.load_mcp_servers()
            self.load_mcp_docs()
        elif self.current_view == "profiles":
            self.load_profiles()

        self.update_view()
        self.status_message = f"Refreshed {self.current_view}"
        self.notify(
            f"🔄 Refreshed {self.current_view}", severity="information", timeout=1
        )

    def action_help(self) -> None:
        """Show comprehensive keyboard shortcuts help."""
        self.push_screen(HelpDialog(current_view=self.current_view))

    def action_claude_md_wizard(self) -> None:
        """Open the CLAUDE.md configuration wizard."""
        wizard = ClaudeMdWizard()
        self.push_screen(wizard, callback=self._handle_claude_md_wizard_result)

    def _handle_claude_md_wizard_result(self, config: Optional[WizardConfig]) -> None:
        """Handle result from CLAUDE.md wizard."""
        if config is None:
            return

        # Generate CLAUDE.md content
        content = generate_claude_md(config)

        # Write to file
        claude_dir = _resolve_claude_dir()
        claude_md_path = claude_dir / "CLAUDE.md"

        def _sync_components(category: str, desired: Set[str]) -> None:
            """Ensure filesystem matches desired active set for a category."""
            active_dir = claude_dir / category
            inactive_dir = _inactive_category_dir(claude_dir, category)
            active_dir.mkdir(parents=True, exist_ok=True)
            inactive_dir.mkdir(parents=True, exist_ok=True)

            # Deactivate anything not desired
            for path in list(active_dir.glob("*.md")):
                if path.stem not in desired:
                    target = inactive_dir / path.name
                    if target.exists():
                        target.unlink()
                    path.rename(target)

            # Activate desired items (promote from inactive if present)
            for name in desired:
                active_path = active_dir / name
                inactive_path = inactive_dir / name
                if active_path.exists():
                    continue
                if inactive_path.exists():
                    inactive_path.rename(active_path)

            # Update tracking file
            _write_active_entries(claude_dir / f".active-{category}", [n for n in desired])

        try:
            # Backup existing file
            if claude_md_path.exists():
                backup_path = claude_dir / "CLAUDE.md.backup"
                backup_path.write_text(claude_md_path.read_text())

            # Write new content
            claude_md_path.write_text(content)

            # Sync rules and modes on disk to match wizard selection
            _sync_components("rules", {r.removesuffix(".md") for r in config.rules})
            _sync_components("modes", {m.removesuffix(".md") for m in config.modes})

            self.notify(
                f"✓ CLAUDE.md updated ({len(config.core_files)} core, "
                f"{len(config.rules)} rules, {len(config.modes)} modes, "
                f"{len(config.mcp_docs)} MCP docs)",
                severity="information",
                timeout=4,
            )
        except Exception as e:
            self.notify(f"Failed to write CLAUDE.md: {e}", severity="error", timeout=5)

    def action_hooks_manager(self) -> None:
        """Open the hooks manager dialog."""
        # Find plugin directory for available hooks
        import claude_ctx_py
        plugin_dir = Path(claude_ctx_py.__file__).parent.parent

        dialog = HooksManagerDialog(plugin_dir)
        self.push_screen(dialog, callback=self._handle_hooks_manager_result)

    def _handle_hooks_manager_result(self, result: Optional[str]) -> None:
        """Handle result from hooks manager."""
        if result:
            self.notify(result, severity="information", timeout=2)

    def action_backup_manager(self) -> None:
        """Open the backup manager dialog."""
        dialog = BackupManagerDialog()
        self.push_screen(dialog, callback=self._handle_backup_manager_result)

    def _handle_backup_manager_result(self, result: Optional[str]) -> None:
        """Handle result from backup manager."""
        if result:
            self.notify(result, severity="information", timeout=2)

    def action_llm_provider_settings(self) -> None:
        """Open the LLM provider settings dialog."""
        dialog = LLMProviderSettingsDialog()
        self.push_screen(dialog, callback=self._handle_llm_provider_settings_result)

    def _handle_llm_provider_settings_result(self, saved: Optional[bool]) -> None:
        """Handle result from provider settings dialog."""
        if saved:
            self.notify("LLM provider settings saved", severity="information", timeout=2)

    def action_command_palette(self) -> None:
        """Show the command palette."""
        self.run_worker(self._open_command_palette(), exclusive=True)

    async def _open_command_palette(self) -> None:
        await self.push_screen(
            CommandPalette(self.command_registry.commands),
            self._on_command_selected,
        )

    def _on_command_selected(self, command_action: Optional[str]) -> None:
        """Handle command selection from palette.

        Args:
            command_action: The action identifier of the selected command, or None if dismissed
        """
        if command_action:
            # Execute the action by name
            try:
                action_method = getattr(self, f"action_{command_action}", None)
                if action_method and callable(action_method):
                    action_method()
                else:
                    self.notify(
                        f"Unknown command action: {command_action}",
                        severity="warning",
                        timeout=3
                    )
            except Exception as e:
                self.notify(
                    f"Error executing command: {e}",
                    severity="error",
                    timeout=5
                )


def main(theme_path: Optional[Path] = None) -> int:
    """Entry point for the Textual TUI."""
    resolved_theme: Optional[Path] = None
    if theme_path is not None:
        resolved_theme = Path(theme_path).expanduser()
        if not resolved_theme.is_file():
            print(f"Theme file not found: {resolved_theme}")
            return 1

    app = AgentTUI(theme_path=resolved_theme)
    app.run()
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
