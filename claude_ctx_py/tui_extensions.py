"""TUI extensions for profile, export, and wizard views."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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
    _resolve_claude_dir,
    _parse_active_entries,
)
from .core.context_export import export_context, collect_context_components
from .core.agents import agent_status
from .core.modes import mode_status
from .core.rules import rules_status


class ProfileViewMixin:
    """Mixin for profile view functionality."""

    def load_profiles(self) -> List[Dict[str, Any]]:
        """Load available profiles."""
        claude_dir = _resolve_claude_dir()
        profiles = []

        # Add built-in profiles
        for profile_name in BUILT_IN_PROFILES:
            profiles.append(
                {
                    "name": profile_name,
                    "type": "built-in",
                    "description": f"Built-in {profile_name} profile",
                    "active": False,  # TODO: Detect active profile
                }
            )

        # Add saved profiles
        profiles_dir = claude_dir / "profiles"
        if profiles_dir.is_dir():
            for profile_file in sorted(profiles_dir.glob("*.profile")):
                profile_name = profile_file.stem
                profiles.append(
                    {
                        "name": profile_name,
                        "type": "saved",
                        "description": "Custom saved profile",
                        "active": False,
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

    def __init__(self, *args, **kwargs):
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
        preview_lines = preview.split("\n")[:10]  # Show first 10 lines
        content.append("\n".join(preview_lines), style="dim")
        if len(preview.split("\n")) > 10:
            content.append(
                f"\n... ({len(preview.split('\n')) - 10} more lines)", style="dim"
            )

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

        preview = {"type": "claude-ctx-export", "format": "json", "components": {}}

        for category, files in components.items():
            if self.export_options.get(category, False):
                preview["components"][category] = list(files.keys())

        return json.dumps(preview, indent=2)

    def _generate_xml_preview(self) -> str:
        """Generate XML preview."""
        return """<?xml version="1.0"?>
<claude-ctx-export>
  <format>xml</format>
  <components>
    <!-- Component data will be here -->
  </components>
</claude-ctx-export>"""

    def _generate_markdown_preview(self) -> str:
        """Generate Markdown preview."""
        return """# Claude CTX Context Export

Exported from: ~/.claude

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
                Path(tempfile.gettempdir()) / f"claude-ctx-export.{self.export_format}"
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

    def copy_to_clipboard(self) -> None:
        """Copy export to clipboard."""
        # TODO: Implement clipboard support
        self.state.status_message = "Clipboard copy not yet implemented"


class WizardViewMixin:
    """Mixin for init wizard functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wizard_active = False
        self.wizard_step = 0
        self.wizard_selections = {}

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

        # TODO: Implement project type detection
        project_types = [
            "Web Development (Frontend/Backend)",
            "Backend API",
            "DevOps/Infrastructure",
            "Data Science/AI",
            "Documentation",
            "Other/Custom",
        ]

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
        content.append("Recommended agents based on project type:\n\n", style="dim")

        # TODO: Show recommended agents
        content.append("Agent selection coming soon...\n\n")

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

        content.append("Mode selection coming soon...\n\n")

        return Panel(content, title="Init Wizard - Modes", border_style="cyan")

    def _render_wizard_step4_rule_selection(self) -> Panel:
        """Render step 4: Rule selection."""
        content = Text()
        content.append(f"Step 4/5: Rule Selection\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        content.append("Rule selection coming soon...\n\n")

        return Panel(content, title="Init Wizard - Rules", border_style="cyan")

    def _render_wizard_step5_confirmation(self) -> Panel:
        """Render step 5: Confirmation."""
        content = Text()
        content.append(f"Step 5/5: Confirmation\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        content.append("Review your selections:\n\n", style="bold")
        content.append("Confirmation and apply coming soon...\n\n")

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
