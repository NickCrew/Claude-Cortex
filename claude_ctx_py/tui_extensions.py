"""TUI extensions for profile, export, and wizard views."""

from __future__ import annotations

import json
import subprocess
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Set

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .core.base import _parse_active_entries, _resolve_claude_dir, _run_detect_project_type
from .core.asset_discovery import discover_plugin_assets
from .core.profiles import (
    profile_list,
    profile_save,
    profile_minimal,
    profile_backend,
    profile_frontend,
    profile_web_dev,
    profile_devops,
    profile_documentation,
    profile_data_ai,
    profile_quality,
    profile_meta,
    profile_developer_experience,
    profile_product,
    profile_full,
    init_wizard as core_init_wizard,
    BUILT_IN_PROFILES,
    _get_current_active_state,
    _get_profile_state,
)
from .core.context_export import export_context, collect_context_components
from .core.agents import (
    agent_status,
    agent_activate,
    ESSENTIAL_AGENTS,
    FRONTEND_AGENTS,
    WEB_DEV_AGENTS,
    BACKEND_AGENTS,
    DEVOPS_AGENTS,
    DOCUMENTATION_AGENTS,
    DATA_AI_AGENTS,
    QUALITY_AGENTS,
    META_AGENTS,
    DX_AGENTS,
    PRODUCT_AGENTS,
    FULL_AGENTS,
)
from .core.modes import mode_status, mode_activate
from .core.rules import rules_status, rules_activate


class ProfileViewMixin:
    """Mixin for profile view functionality."""

    state: Any
    load_agents: Callable[[], None]

    def _get_profile_state_from_name(self, profile_name: str, claude_dir: Path, is_built_in: bool) -> Tuple[Set[str], Set[str], Set[str]]:
        """Helper to get the expected active state (agents, modes, rules) for a given profile name.

        Args:
            profile_name: The name of the profile.
            claude_dir: The root claude directory.
            is_built_in: True if it's a built-in profile, False for saved.

        Returns:
            A tuple of sets: (active_agents, active_modes, active_rules) for the profile.
        """
        if is_built_in:
            # Temporarily apply the profile to get its active state without modifying the actual system
            # This is a bit hacky, but avoids duplicating the profile loading logic.
            # A better long-term solution might be to have a 'dry_run' mode for profile loaders.
            # For now, we'll simulate the state.
            active_agents: Set[str] = set()
            active_modes: Set[str] = set()
            active_rules: Set[str] = set()

            # Map profile names to their expected active components (as defined in profiles.py)
            # This requires duplicating some logic from profiles.py, but avoids actually activating them.
            if profile_name == "minimal":
                from .core.agents import ESSENTIAL_AGENTS
                active_agents = set(ESSENTIAL_AGENTS)
            elif profile_name == "backend":
                from .core.agents import ESSENTIAL_AGENTS, BACKEND_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + BACKEND_AGENTS)
                active_modes = {"Task_Management"}
                active_rules = {"quality-rules"}
            elif profile_name == "frontend":
                from .core.agents import ESSENTIAL_AGENTS, FRONTEND_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + FRONTEND_AGENTS)
                active_modes = {"Task_Management"}
                active_rules = {"quality-rules"}
            elif profile_name == "web-dev":
                from .core.agents import ESSENTIAL_AGENTS, WEB_DEV_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + WEB_DEV_AGENTS)
                active_modes = {"Task_Management"}
                active_rules = {"quality-rules"}
            elif profile_name == "devops":
                from .core.agents import ESSENTIAL_AGENTS, DEVOPS_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + DEVOPS_AGENTS)
                active_modes = {"Orchestration"}
                active_rules = {"workflow-rules"}
            elif profile_name == "documentation":
                from .core.agents import ESSENTIAL_AGENTS, DOCUMENTATION_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + DOCUMENTATION_AGENTS)
            elif profile_name == "data-ai":
                from .core.agents import ESSENTIAL_AGENTS, DATA_AI_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + DATA_AI_AGENTS)
            elif profile_name == "quality":
                from .core.agents import ESSENTIAL_AGENTS, QUALITY_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + QUALITY_AGENTS)
                active_rules = {"quality-gate-rules", "quality-rules"}
            elif profile_name == "meta":
                from .core.agents import ESSENTIAL_AGENTS, META_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + META_AGENTS)
            elif profile_name == "developer-experience":
                from .core.agents import ESSENTIAL_AGENTS, DX_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + DX_AGENTS)
            elif profile_name == "product":
                from .core.agents import ESSENTIAL_AGENTS, PRODUCT_AGENTS
                active_agents = set(ESSENTIAL_AGENTS + PRODUCT_AGENTS)
            elif profile_name == "full":
                from .core.agents import FULL_AGENTS
                active_agents = set(FULL_AGENTS)
                active_modes = {"Super_Saiyan", "Orchestration", "Parallel_Orchestration", "Task_Management", "Token_Efficiency"}
                active_rules = {"quality-rules", "workflow-rules", "git-rules", "efficiency-rules", "quality-gate-rules"}

            return active_agents, active_modes, active_rules
        else:
            # For saved profiles, parse the .profile file directly
            profile_file = claude_dir / "profiles" / f"{profile_name}.profile"
            if profile_file.is_file():
                return _get_profile_state(profile_file)
            return set(), set(), set()

    def load_profiles(self) -> List[Dict[str, Any]]:
        """Load available profiles."""
        claude_dir = _resolve_claude_dir()
        profiles = []

        current_active_agents, current_active_modes, current_active_rules = _get_current_active_state(claude_dir)

        # Add built-in profiles
        for profile_name in BUILT_IN_PROFILES:
            profile_agents, profile_modes, profile_rules = self._get_profile_state_from_name(profile_name, claude_dir, is_built_in=True)
            is_active = (
                current_active_agents == profile_agents and
                current_active_modes == profile_modes and
                current_active_rules == profile_rules
            )
            profiles.append(
                {
                    "name": profile_name,
                    "type": "built-in",
                    "description": f"Built-in {profile_name} profile",
                    "active": is_active,
                }
            )

        # Add saved profiles
        profiles_dir = claude_dir / "profiles"
        if profiles_dir.is_dir():
            for profile_file in sorted(profiles_dir.glob("*.profile")):
                profile_name = profile_file.stem
                profile_agents, profile_modes, profile_rules = _get_profile_state(profile_file)
                is_active = (
                    current_active_agents == profile_agents and
                    current_active_modes == profile_modes and
                    current_active_rules == profile_rules
                )
                profiles.append(
                    {
                        "name": profile_name,
                        "type": "saved",
                        "description": "Custom saved profile",
                        "active": is_active,
                    }
                )

        return profiles

    def render_profile_view(self) -> Panel:
        """Render the profile management view."""
        # Load profiles
        profiles = self.load_profiles()

        # Create profiles table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Profile", style="cyan", no_wrap=True)
        table.add_column("Type", width=12, no_wrap=True)
        table.add_column("Description", width=40)
        table.add_column("Status", width=10, no_wrap=True)

        if not profiles:
            table.add_row("", "No profiles found", "", "", "")
        else:
            for idx, profile in enumerate(profiles):
                is_selected = idx == self.state.selected_index
                indicator = ">" if is_selected else ""

                # Status indicator
                status_text = (
                    Text("Active", style="bold green")
                    if profile["active"]
                    else Text("", style="dim")
                )

                # Type styling
                type_style = "yellow" if profile["type"] == "built-in" else "blue"
                type_text = Text(profile["type"], style=type_style)

                # Row style
                row_style = "reverse" if is_selected else None

                table.add_row(
                    indicator,
                    profile["name"],
                    type_text,
                    profile["description"],
                    status_text,
                    style=row_style,
                )

        # Add controls hint
        controls = Text()
        controls.append("\nControls: ", style="bold")
        controls.append("Enter", style="cyan")
        controls.append("=Apply  ", style="dim")
        controls.append("n", style="cyan")
        controls.append("=New  ", style="dim")
        controls.append("s", style="cyan")
        controls.append("=Save  ", style="dim")
        controls.append("d", style="cyan")
        controls.append("=Delete  ", style="dim")
        controls.append("r", style="cyan")
        controls.append("=Reload", style="dim")

        return Panel(
            table,
            title="Profile Management",
            subtitle=controls,
            border_style="cyan",
        )

    def apply_profile(self) -> None:
        """Apply the selected profile."""
        profiles = self.load_profiles()
        if not profiles or self.state.selected_index >= len(profiles):
            self.state.status_message = "No profile selected"
            return

        profile = profiles[self.state.selected_index]
        profile_name = profile["name"]

        # Map profile names to functions
        profile_loaders = {
            "minimal": profile_minimal,
            "backend": profile_backend,
            "frontend": profile_frontend,
            "web-dev": profile_web_dev,
            "devops": profile_devops,
            "documentation": profile_documentation,
            "data-ai": profile_data_ai,
            "quality": profile_quality,
            "meta": profile_meta,
            "developer-experience": profile_developer_experience,
            "product": profile_product,
            "full": profile_full,
        }

        loader = profile_loaders.get(profile_name)
        if loader:
            try:
                exit_code, message = loader()
                # Clean ANSI codes
                import re

                clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                self.state.status_message = clean_message.split("\n")[0]
                if exit_code == 0:
                    self.load_agents()
            except Exception as e:
                self.state.status_message = f"Error applying profile: {e}"
        else:
            self.state.status_message = f"Profile '{profile_name}' not implemented"

    def save_current_profile(self) -> None:
        """Save current configuration as a profile."""
        # TODO: Implement profile name prompt
        self.state.status_message = "Profile save not yet implemented in TUI"

    def delete_profile(self) -> None:
        """Delete the selected profile."""
        profiles = self.load_profiles()
        if not profiles or self.state.selected_index >= len(profiles):
            self.state.status_message = "No profile selected"
            return

        profile = profiles[self.state.selected_index]
        if profile["type"] == "built-in":
            self.state.status_message = "Cannot delete built-in profiles"
            return

        # TODO: Implement profile deletion with confirmation
        self.state.status_message = "Profile deletion not yet implemented in TUI"


class ExportViewMixin:
    """Mixin for export view functionality."""

    state: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.export_options = {
            "core": True,
            "rules": True,
            "modes": True,
            "agents": True,
            "mcp_docs": False,
            "skills": False,
        }
        self.export_format = "json"
        self.export_preview = ""

    def render_export_view(self) -> Panel:
        """Render the context export view."""
        content = Text()

        # Title
        content.append("Context Export\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        # Export options
        content.append("Export Options:\n", style="bold")
        options = [
            ("core", "Core Framework"),
            ("rules", "Active Rules"),
            ("modes", "Active Modes"),
            ("agents", "Active Agents"),
            ("mcp_docs", "MCP Documentation"),
            ("skills", "Skills"),
        ]

        for idx, (key, label) in enumerate(options):
            is_selected = idx == self.state.selected_index
            checkbox = "[x]" if self.export_options[key] else "[ ]"
            prefix = "> " if is_selected else "  "
            content.append(
                f"{prefix}{checkbox} {label}\n",
                style="reverse" if is_selected else None,
            )

        content.append("\n")

        # Format selection
        content.append(f"Format: ", style="bold")
        formats = ["JSON", "XML", "Markdown"]
        format_display = " | ".join(
            f"[{fmt}]" if fmt.lower() == self.export_format else fmt for fmt in formats
        )
        content.append(f"{format_display}\n\n", style="cyan")

        # Preview section
        content.append("Preview:\n", style="bold")
        content.append("─" * 60 + "\n", style="dim")

        # Generate preview
        preview = self.generate_export_preview()
        preview_lines_all = preview.splitlines()
        preview_lines = preview_lines_all[:10]  # Show first 10 lines
        content.append("\n".join(preview_lines), style="dim")
        if len(preview_lines_all) > 10:
            remaining = len(preview_lines_all) - 10
            content.append(f"\n... ({remaining} more lines)", style="dim")

        content.append("\n\n")

        # Controls
        controls = Text()
        controls.append("Controls: ", style="bold")
        controls.append("Space", style="cyan")
        controls.append("=Toggle  ", style="dim")
        controls.append("f", style="cyan")
        controls.append("=Format  ", style="dim")
        controls.append("e", style="cyan")
        controls.append("=Export  ", style="dim")
        controls.append("p", style="cyan")
        controls.append("=Clipboard", style="dim")

        return Panel(
            content, title="Context Export", subtitle=controls, border_style="cyan"
        )

    def generate_export_preview(self) -> str:
        """Generate a preview of the export."""
        if self.export_format == "json":
            return self._generate_json_preview()
        elif self.export_format == "xml":
            return self._generate_xml_preview()
        else:  # markdown
            return self._generate_markdown_preview()

    def _generate_json_preview(self) -> str:
        """Generate JSON preview."""
        claude_dir = _resolve_claude_dir()
        components = collect_context_components(claude_dir)

        preview: Dict[str, Any] = {
            "type": "cortex-export",
            "format": "json",
            "components": {},
        }
        selected_components: Dict[str, List[str]] = preview["components"]

        for category, files in components.items():
            if self.export_options.get(category, False):
                selected_components[category] = list(files.keys())

        return json.dumps(preview, indent=2)

    def _generate_xml_preview(self) -> str:
        """Generate XML preview."""
        return """<?xml version="1.0"?>
<cortex-export>
  <format>xml</format>
  <components>
    <!-- Component data will be here -->
  </components>
</cortex-export>"""

    def _generate_markdown_preview(self) -> str:
        """Generate Markdown preview."""
        return """# Cortex Context Export

Exported from: ~/.cortex

---

## Core Framework
..."""

    def toggle_export_option(self) -> None:
        """Toggle the selected export option."""
        options = list(self.export_options.keys())
        if self.state.selected_index < len(options):
            key = options[self.state.selected_index]
            self.export_options[key] = not self.export_options[key]
            self.state.status_message = f"Toggled {key}: {self.export_options[key]}"

    def cycle_export_format(self) -> None:
        """Cycle through export formats."""
        formats = ["json", "xml", "markdown"]
        current_idx = formats.index(self.export_format)
        self.export_format = formats[(current_idx + 1) % len(formats)]
        self.state.status_message = f"Export format: {self.export_format.upper()}"

    def execute_export(self) -> None:
        """Execute the export to file."""
        try:
            # Build exclude categories
            exclude_categories = {
                key for key, enabled in self.export_options.items() if not enabled
            }

            # Generate output path
            import tempfile

            output_path = (
                Path(tempfile.gettempdir()) / f"cortex-export.{self.export_format}"
            )

            # TODO: Support format parameter in export_context
            exit_code, message = export_context(
                output_path,
                exclude_categories=exclude_categories,
            )

            # Clean ANSI codes
            import re

            clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
            self.state.status_message = clean_message.split("\n")[0]
        except Exception as e:
            self.state.status_message = f"Export error: {e}"

    def export_copy_to_clipboard(self) -> None:
        """Copy export to clipboard."""
        try:
            content_to_copy = self.generate_export_preview()
            subprocess.run(
                ["pbcopy"],
                input=content_to_copy.encode("utf-8"),
                check=True,
                capture_output=True,
            )
            self.state.status_message = "Export copied to clipboard"
        except FileNotFoundError:
            self.state.status_message = "Error: 'pbcopy' command not found. Clipboard functionality requires macOS."
        except subprocess.CalledProcessError as e:
            self.state.status_message = f"Error copying to clipboard: {e.stderr.decode().strip()}"
        except Exception as e:
            self.state.status_message = f"An unexpected error occurred: {e}"


class WizardViewMixin:
    """Mixin for init wizard functionality."""

    state: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.wizard_active = False
        self.wizard_step = 0
        self.wizard_selections: Dict[str, Any] = {}

    def action_wizard_toggle(self) -> None:
        """Toggle selection of current item in wizard."""
        if not self.wizard_active:
            return

        if self.wizard_step == 1:
            # Agents
            assets = discover_plugin_assets()
            agents = sorted(assets.get("agents", []), key=lambda a: a.name)
            if 0 <= self.state.selected_index < len(agents):
                agent_name = agents[self.state.selected_index].name
                if "agents" not in self.wizard_selections:
                    self.wizard_selections["agents"] = set()
                
                if agent_name in self.wizard_selections["agents"]:
                    self.wizard_selections["agents"].remove(agent_name)
                else:
                    self.wizard_selections["agents"].add(agent_name)
                self.state.status_message = f"Toggled agent: {agent_name}"

        elif self.wizard_step == 2:
            # Modes
            assets = discover_plugin_assets()
            modes = sorted(assets.get("modes", []), key=lambda m: m.name)
            if 0 <= self.state.selected_index < len(modes):
                mode_name = modes[self.state.selected_index].name
                if "modes" not in self.wizard_selections:
                    self.wizard_selections["modes"] = set()
                
                if mode_name in self.wizard_selections["modes"]:
                    self.wizard_selections["modes"].remove(mode_name)
                else:
                    self.wizard_selections["modes"].add(mode_name)
                self.state.status_message = f"Toggled mode: {mode_name}"

        elif self.wizard_step == 3:
            # Rules
            assets = discover_plugin_assets()
            rules = sorted(assets.get("rules", []), key=lambda r: r.name)
            if 0 <= self.state.selected_index < len(rules):
                rule_name = rules[self.state.selected_index].name
                if "rules" not in self.wizard_selections:
                    self.wizard_selections["rules"] = set()
                
                if rule_name in self.wizard_selections["rules"]:
                    self.wizard_selections["rules"].remove(rule_name)
                else:
                    self.wizard_selections["rules"].add(rule_name)
                self.state.status_message = f"Toggled rule: {rule_name}"

    def action_wizard_next(self) -> None:
        """Advance to next wizard step."""
        if not self.wizard_active:
            self.start_wizard()
            return

        if self.wizard_step == 0:
            # Project Type selection
            project_types = [
                "Web Development (Frontend/Backend)",
                "Backend API",
                "DevOps/Infrastructure",
                "Data Science/AI",
                "Documentation",
                "Other/Custom",
            ]
            if 0 <= self.state.selected_index < len(project_types):
                self.wizard_selections["project_type"] = project_types[self.state.selected_index]
            self.wizard_next_step()
        elif self.wizard_step == 4:
            # Confirmation step - Apply!
            self._apply_wizard_configuration()
            self.wizard_step += 1 # Move to complete
        else:
            self.wizard_next_step()

    def action_wizard_prev(self) -> None:
        """Go back to previous wizard step."""
        if self.wizard_active:
            self.wizard_prev_step()

    def _apply_wizard_configuration(self) -> None:
        """Actually apply the selections made in the wizard."""
        try:
            # 1. Reset/Apply base profile
            ptype = self.wizard_selections.get("project_type", "")
            if "Web" in ptype:
                profile_web_dev()
            elif "Backend" in ptype:
                profile_backend()
            elif "DevOps" in ptype:
                profile_devops()
            elif "Data" in ptype:
                profile_data_ai()
            elif "Documentation" in ptype:
                profile_documentation()
            else:
                profile_minimal()

            # 2. Activate specific agents
            for agent in self.wizard_selections.get("agents", []):
                agent_activate(agent)

            # 3. Activate specific modes
            for mode in self.wizard_selections.get("modes", []):
                mode_activate(mode)

            # 4. Activate specific rules
            for rule in self.wizard_selections.get("rules", []):
                rules_activate(rule)

            self.state.status_message = "Configuration applied successfully!"
        except Exception as e:
            self.state.status_message = f"Error applying configuration: {e}"

    def render_wizard_view(self) -> Panel:
        """Render the init wizard view."""
        if not self.wizard_active:
            return self._render_wizard_start()

        wizard_steps = [
            self._render_wizard_step1_project_type,
            self._render_wizard_step2_agent_selection,
            self._render_wizard_step3_mode_selection,
            self._render_wizard_step4_rule_selection,
            self._render_wizard_step5_confirmation,
        ]

        if self.wizard_step < len(wizard_steps):
            return wizard_steps[self.wizard_step]()
        else:
            return self._render_wizard_complete()

    def _render_wizard_start(self) -> Panel:
        """Render wizard start screen."""
        content = Text()
        content.append("Init Wizard\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")
        content.append(
            "This wizard will help you initialize your project configuration.\n\n"
        )
        content.append("Press ", style="dim")
        content.append("Enter", style="cyan")
        content.append(" to start, or ", style="dim")
        content.append("Esc", style="cyan")
        content.append(" to cancel.", style="dim")

        return Panel(content, title="Init Wizard", border_style="cyan")

    def _render_wizard_step1_project_type(self) -> Panel:
        """Render step 1: Project type detection."""
        content = Text()
        content.append(f"Step 1/5: Project Type\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        # Detect project type
        claude_dir = _resolve_claude_dir()
        detected_type = ""
        try:
            message = _run_detect_project_type(claude_dir)
            if message:
                # Message format: "Detected project type: <type>"
                match = re.search(r"Detected project type: (.*)", message)
                if match:
                    detected_type = match.group(1).strip()
        except Exception:
            # Ignore errors for detection, fall back to no detection
            pass

        project_types = [
            "Web Development (Frontend/Backend)",
            "Backend API",
            "DevOps/Infrastructure",
            "Data Science/AI",
            "Documentation",
            "Other/Custom",
        ]

        if detected_type and detected_type != "Unknown":
            content.append(f"Detected: [b yellow]{detected_type}[/b yellow]\n\n")
            # Pre-select the detected type if it's in our list
            try:
                self.state.selected_index = project_types.index(detected_type)
            except ValueError:
                # If detected type is not in our list, don't pre-select
                pass
        else:
            content.append("Select your project type:\n\n")

        for idx, ptype in enumerate(project_types):
            is_selected = idx == self.state.selected_index
            prefix = "> " if is_selected else "  "
            content.append(
                f"{prefix}{ptype}\n", style="reverse" if is_selected else None
            )

        content.append("\n")
        content.append("Enter", style="cyan")
        content.append("=Select  ", style="dim")
        content.append("Backspace", style="cyan")
        content.append("=Back  ", style="dim")
        content.append("Esc", style="cyan")
        content.append("=Cancel", style="dim")

        return Panel(content, title="Init Wizard - Project Type", border_style="cyan")

    def _render_wizard_step2_agent_selection(self) -> Panel:
        """Render step 2: Agent selection."""
        content = Text()
        content.append(f"Step 2/5: Agent Selection\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")
        content.append("Select additional agents to activate:\n\n")

        assets = discover_plugin_assets()
        agents = sorted(assets.get("agents", []), key=lambda a: a.name)

        # Get pre-selected agents based on project type if not already set
        if "agents" not in self.wizard_selections:
            # Simple heuristic mapping
            ptype = self.wizard_selections.get("project_type", "")
            preselected = set(ESSENTIAL_AGENTS)
            if "Web" in ptype:
                preselected.update(WEB_DEV_AGENTS)
            elif "Backend" in ptype:
                preselected.update(BACKEND_AGENTS)
            elif "DevOps" in ptype:
                preselected.update(DEVOPS_AGENTS)
            elif "Data" in ptype:
                preselected.update(DATA_AI_AGENTS)
            elif "Documentation" in ptype:
                preselected.update(DOCUMENTATION_AGENTS)
            self.wizard_selections["agents"] = preselected

        selected_agents = self.wizard_selections.get("agents", set())

        # Paginate if needed (simple display for now)
        start_idx = getattr(self, "_agent_page_start", 0)
        page_size = 15
        
        display_agents = agents[start_idx:start_idx+page_size]

        for idx, agent in enumerate(display_agents):
            abs_idx = start_idx + idx
            is_cursor = abs_idx == self.state.selected_index
            is_selected = agent.name in selected_agents
            
            checkbox = "[x]" if is_selected else "[ ]"
            prefix = "> " if is_cursor else "  "
            
            style = "reverse" if is_cursor else None
            desc = agent.description[:50] + "..." if len(agent.description) > 50 else agent.description
            
            content.append(f"{prefix}{checkbox} {agent.name.ljust(25)} - {desc}\n", style=style)

        if len(agents) > page_size:
            content.append(f"\n[dim]Showing {start_idx+1}-{min(start_idx+page_size, len(agents))} of {len(agents)}. Use Up/Down to scroll.[/dim]\n")

        content.append("\n")
        content.append("Space", style="cyan")
        content.append("=Toggle  ", style="dim")
        content.append("Enter", style="cyan")
        content.append("=Next  ", style="dim")
        content.append("Backspace", style="cyan")
        content.append("=Back  ", style="dim")

        return Panel(content, title="Init Wizard - Agents", border_style="cyan")

    def _render_wizard_step3_mode_selection(self) -> Panel:
        """Render step 3: Mode selection."""
        content = Text()
        content.append(f"Step 3/5: Mode Selection\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")
        content.append("Select behavioral modes to activate:\n\n")

        assets = discover_plugin_assets()
        modes = sorted(assets.get("modes", []), key=lambda m: m.name)

        if "modes" not in self.wizard_selections:
            self.wizard_selections["modes"] = set()

        selected_modes = self.wizard_selections["modes"]

        for idx, mode in enumerate(modes):
            is_cursor = idx == self.state.selected_index
            is_selected = mode.name in selected_modes
            
            checkbox = "[x]" if is_selected else "[ ]"
            prefix = "> " if is_cursor else "  "
            style = "reverse" if is_cursor else None
            
            content.append(f"{prefix}{checkbox} {mode.name.ljust(25)} - {mode.description}\n", style=style)

        content.append("\n")
        content.append("Space", style="cyan")
        content.append("=Toggle  ", style="dim")
        content.append("Enter", style="cyan")
        content.append("=Next  ", style="dim")
        content.append("Backspace", style="cyan")
        content.append("=Back  ", style="dim")

        return Panel(content, title="Init Wizard - Modes", border_style="cyan")

    def _render_wizard_step4_rule_selection(self) -> Panel:
        """Render step 4: Rule selection."""
        content = Text()
        content.append(f"Step 4/5: Rule Selection\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")
        content.append("Select rule modules to enforce:\n\n")

        assets = discover_plugin_assets()
        rules = sorted(assets.get("rules", []), key=lambda r: r.name)

        if "rules" not in self.wizard_selections:
            self.wizard_selections["rules"] = set()

        selected_rules = self.wizard_selections["rules"]

        for idx, rule in enumerate(rules):
            is_cursor = idx == self.state.selected_index
            is_selected = rule.name in selected_rules
            
            checkbox = "[x]" if is_selected else "[ ]"
            prefix = "> " if is_cursor else "  "
            style = "reverse" if is_cursor else None
            
            content.append(f"{prefix}{checkbox} {rule.name.ljust(25)} - {rule.description}\n", style=style)

        content.append("\n")
        content.append("Space", style="cyan")
        content.append("=Toggle  ", style="dim")
        content.append("Enter", style="cyan")
        content.append("=Next  ", style="dim")
        content.append("Backspace", style="cyan")
        content.append("=Back  ", style="dim")

        return Panel(content, title="Init Wizard - Rules", border_style="cyan")

    def _render_wizard_step5_confirmation(self) -> Panel:
        """Render step 5: Confirmation."""
        content = Text()
        content.append(f"Step 5/5: Confirmation\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        content.append("Review your selections:\n\n", style="bold")
        
        ptype = self.wizard_selections.get("project_type", "Unknown")
        content.append(f"Project Type: [yellow]{ptype}[/yellow]\n\n")
        
        agents = self.wizard_selections.get("agents", set())
        content.append(f"Agents ({len(agents)}):\n", style="bold")
        if agents:
            content.append(f"[dim]{', '.join(sorted(agents))}[/dim]\n\n")
        else:
            content.append("[dim]None selected[/dim]\n\n")
            
        modes = self.wizard_selections.get("modes", set())
        content.append(f"Modes ({len(modes)}):\n", style="bold")
        if modes:
            content.append(f"[dim]{', '.join(sorted(modes))}[/dim]\n\n")
        else:
            content.append("[dim]None selected[/dim]\n\n")
            
        rules = self.wizard_selections.get("rules", set())
        content.append(f"Rules ({len(rules)}):\n", style="bold")
        if rules:
            content.append(f"[dim]{', '.join(sorted(rules))}[/dim]\n\n")
        else:
            content.append("[dim]None selected[/dim]\n\n")

        content.append("Enter", style="cyan")
        content.append("=Apply Configuration  ", style="dim")
        content.append("Backspace", style="cyan")
        content.append("=Back  ", style="dim")

        return Panel(content, title="Init Wizard - Confirm", border_style="cyan")

    def _render_wizard_complete(self) -> Panel:
        """Render wizard completion."""
        content = Text()
        content.append("Wizard Complete!\n", style="bold green")
        content.append("─" * 60 + "\n\n", style="dim")

        content.append("Your project has been initialized successfully.\n\n")
        content.append("Press any key to return to main view.", style="dim")

        return Panel(content, title="Init Wizard - Complete", border_style="green")

    def start_wizard(self) -> None:
        """Start the init wizard."""
        self.wizard_active = True
        self.wizard_step = 0
        self.wizard_selections = {}
        self.state.selected_index = 0
        self.state.status_message = "Init wizard started"

    def wizard_next_step(self) -> None:
        """Move to next wizard step."""
        if self.wizard_step < 5:
            self.wizard_step += 1
            self.state.selected_index = 0
            self.state.status_message = f"Step {self.wizard_step + 1}/5"

    def wizard_prev_step(self) -> None:
        """Move to previous wizard step."""
        if self.wizard_step > 0:
            self.wizard_step -= 1
            self.state.selected_index = 0
            self.state.status_message = f"Step {self.wizard_step + 1}/5"

    def wizard_cancel(self) -> None:
        """Cancel the wizard."""
        self.wizard_active = False
        self.wizard_step = 0
        self.wizard_selections = {}
        self.state.current_view = "overview"
        self.state.status_message = "Wizard cancelled"
