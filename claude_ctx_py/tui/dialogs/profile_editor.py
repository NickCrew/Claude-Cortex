"""Profile Editor Dialog for viewing and editing profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Label, Static, TabbedContent, TabPane

from ...core import _resolve_claude_dir
from ...core.agents import (
    BACKEND_AGENTS,
    BUILT_IN_PROFILES,
    DATA_AI_AGENTS,
    DEVOPS_AGENTS,
    DOCUMENTATION_AGENTS,
    DX_AGENTS,
    ESSENTIAL_AGENTS,
    FRONTEND_AGENTS,
    FULL_AGENTS,
    META_AGENTS,
    PRODUCT_AGENTS,
    QUALITY_AGENTS,
    WEB_DEV_AGENTS,
)


@dataclass
class ProfileConfig:
    """Configuration for a profile."""

    name: str
    is_built_in: bool
    agents: Set[str] = field(default_factory=set)
    modes: Set[str] = field(default_factory=set)
    rules: Set[str] = field(default_factory=set)


# Map built-in profile names to their agent sets
PROFILE_AGENTS = {
    "minimal": set(ESSENTIAL_AGENTS),
    "frontend": set(ESSENTIAL_AGENTS) | set(FRONTEND_AGENTS),
    "web-dev": set(ESSENTIAL_AGENTS) | set(WEB_DEV_AGENTS),
    "backend": set(ESSENTIAL_AGENTS) | set(BACKEND_AGENTS),
    "devops": set(ESSENTIAL_AGENTS) | set(DEVOPS_AGENTS),
    "documentation": set(ESSENTIAL_AGENTS) | set(DOCUMENTATION_AGENTS),
    "data-ai": set(ESSENTIAL_AGENTS) | set(DATA_AI_AGENTS),
    "quality": set(ESSENTIAL_AGENTS) | set(QUALITY_AGENTS),
    "meta": set(ESSENTIAL_AGENTS) | set(META_AGENTS),
    "developer-experience": set(ESSENTIAL_AGENTS) | set(DX_AGENTS),
    "product": set(ESSENTIAL_AGENTS) | set(PRODUCT_AGENTS),
    "full": set(ESSENTIAL_AGENTS) | set(FULL_AGENTS),
}

# Built-in profile modes
PROFILE_MODES = {
    "minimal": set(),
    "frontend": {"Task_Management"},
    "web-dev": {"Task_Management"},
    "backend": {"Task_Management"},
    "devops": {"Task_Management"},
    "documentation": {"Task_Management"},
    "data-ai": {"Task_Management"},
    "quality": {"Task_Management"},
    "meta": {"Task_Management"},
    "developer-experience": {"Task_Management"},
    "product": {"Task_Management"},
    "full": {"Task_Management"},
}

# Built-in profile rules
PROFILE_RULES = {
    "minimal": set(),
    "frontend": set(),
    "web-dev": {"quality-rules"},
    "backend": {"quality-rules"},
    "devops": set(),
    "documentation": set(),
    "data-ai": set(),
    "quality": {"quality-rules"},
    "meta": set(),
    "developer-experience": set(),
    "product": set(),
    "full": {"quality-rules"},
}


def get_available_agents(claude_dir: Path) -> List[str]:
    """Get list of available agent names."""
    agents_dir = claude_dir / "agents"
    agents = []
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.md")):
            if f.is_file() and not f.name.startswith("."):
                agents.append(f.stem)
    return agents


def get_available_modes(claude_dir: Path) -> List[str]:
    """Get list of available mode names."""
    modes_dir = claude_dir / "modes"
    modes = []
    if modes_dir.is_dir():
        for f in sorted(modes_dir.glob("*.md")):
            if f.is_file() and not f.name.startswith("."):
                modes.append(f.stem)
    return modes


def get_available_rules(claude_dir: Path) -> List[str]:
    """Get list of available rule names."""
    rules_dir = claude_dir / "rules"
    rules = []
    if rules_dir.is_dir():
        for f in sorted(rules_dir.glob("*.md")):
            if f.is_file() and not f.name.startswith("."):
                rules.append(f.stem)
    return rules


def parse_saved_profile(profile_path: Path) -> ProfileConfig:
    """Parse a saved .profile file."""
    content = profile_path.read_text(encoding="utf-8")
    config = ProfileConfig(name=profile_path.stem, is_built_in=False)

    for line in content.splitlines():
        if line.startswith("AGENTS=\""):
            agents_str = line.split("=\"", 1)[1].rstrip('"')
            for entry in agents_str.split():
                # Remove .md extension if present
                agent = entry.strip()
                if agent.endswith(".md"):
                    agent = agent[:-3]
                if agent:
                    config.agents.add(agent)
        elif line.startswith("MODES=\""):
            modes_str = line.split("=\"", 1)[1].rstrip('"')
            config.modes = {m.strip() for m in modes_str.split() if m.strip()}
        elif line.startswith("RULES=\""):
            rules_str = line.split("=\"", 1)[1].rstrip('"')
            config.rules = {r.strip() for r in rules_str.split() if r.strip()}

    return config


def get_builtin_profile_config(name: str) -> ProfileConfig:
    """Get configuration for a built-in profile."""
    return ProfileConfig(
        name=name,
        is_built_in=True,
        agents=PROFILE_AGENTS.get(name, set()),
        modes=PROFILE_MODES.get(name, set()),
        rules=PROFILE_RULES.get(name, set()),
    )


class ProfileEditorDialog(ModalScreen[Optional[ProfileConfig]]):
    """Dialog for viewing and editing profile configuration."""

    CSS = """
    ProfileEditorDialog {
        align: center middle;
    }

    ProfileEditorDialog #dialog {
        width: 90%;
        max-width: 110;
        height: 85%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    ProfileEditorDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    ProfileEditorDialog #profile-info {
        color: $text-muted;
        margin-bottom: 1;
    }

    ProfileEditorDialog TabbedContent {
        height: 1fr;
    }

    ProfileEditorDialog TabPane {
        padding: 1;
    }

    ProfileEditorDialog .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    ProfileEditorDialog .checkbox-item {
        margin-bottom: 0;
    }

    ProfileEditorDialog .checkbox-essential {
        color: $warning;
    }

    ProfileEditorDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    ProfileEditorDialog #dialog-buttons Button {
        margin: 0 1;
    }

    ProfileEditorDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "apply", "Apply"),
    ]

    def __init__(
        self,
        profile_name: str,
        profile_type: str,
        profile_path: Optional[str] = None,
    ) -> None:
        """Initialize the profile editor.

        Args:
            profile_name: Name of the profile
            profile_type: Either "built-in" or "saved"
            profile_path: Path to the .profile file (for saved profiles)
        """
        super().__init__()
        self.profile_name = profile_name
        self.profile_type = profile_type
        self.profile_path = Path(profile_path) if profile_path else None

        self.claude_dir = _resolve_claude_dir()

        # Load profile configuration
        if profile_type == "built-in":
            self.config = get_builtin_profile_config(profile_name)
        else:
            if self.profile_path and self.profile_path.exists():
                self.config = parse_saved_profile(self.profile_path)
            else:
                self.config = ProfileConfig(name=profile_name, is_built_in=False)

        # Get available items
        self.available_agents = get_available_agents(self.claude_dir)
        self.available_modes = get_available_modes(self.claude_dir)
        self.available_rules = get_available_rules(self.claude_dir)

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static(f"Profile: {self.profile_name}", id="dialog-title")

            type_label = "[cyan]Built-in[/cyan]" if self.profile_type == "built-in" else "[magenta]Saved[/magenta]"
            yield Static(
                f"Type: {type_label} | Edit selections below, then Apply",
                id="profile-info",
            )

            with TabbedContent():
                with TabPane("Agents", id="agents-tab"):
                    with VerticalScroll():
                        yield Static(
                            f"[bold]Select Agents[/bold] ({len(self.config.agents)} selected)",
                            classes="section-title",
                        )
                        for agent in self.available_agents:
                            is_essential = agent in ESSENTIAL_AGENTS
                            checked = agent in self.config.agents
                            label = f"{agent}"
                            if is_essential:
                                label += " [dim](essential)[/dim]"
                            yield Checkbox(
                                label,
                                value=checked,
                                id=f"agent-{self._sanitize_id(agent)}",
                                classes="checkbox-item" + (" checkbox-essential" if is_essential else ""),
                            )

                with TabPane("Modes", id="modes-tab"):
                    with VerticalScroll():
                        yield Static(
                            f"[bold]Select Modes[/bold] ({len(self.config.modes)} selected)",
                            classes="section-title",
                        )
                        for mode in self.available_modes:
                            checked = mode in self.config.modes
                            yield Checkbox(
                                mode,
                                value=checked,
                                id=f"mode-{self._sanitize_id(mode)}",
                                classes="checkbox-item",
                            )

                with TabPane("Rules", id="rules-tab"):
                    with VerticalScroll():
                        yield Static(
                            f"[bold]Select Rules[/bold] ({len(self.config.rules)} selected)",
                            classes="section-title",
                        )
                        for rule in self.available_rules:
                            checked = rule in self.config.rules
                            yield Checkbox(
                                rule,
                                value=checked,
                                id=f"rule-{self._sanitize_id(rule)}",
                                classes="checkbox-item",
                            )

            yield Static(
                "[dim]Tab between sections • Space to toggle • Enter to apply • Esc to cancel[/dim]",
                id="dialog-hint",
            )

            with Horizontal(id="dialog-buttons"):
                yield Button("Apply", variant="success", id="apply")
                yield Button("Cancel", variant="default", id="cancel")

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as a widget ID."""
        return name.replace(".", "-").replace("_", "-").replace(" ", "-").lower()

    def _collect_selections(self) -> ProfileConfig:
        """Collect current checkbox selections."""
        config = ProfileConfig(
            name=self.config.name,
            is_built_in=self.config.is_built_in,
        )

        # Collect agents
        for agent in self.available_agents:
            try:
                cb = self.query_one(f"#agent-{self._sanitize_id(agent)}", Checkbox)
                if cb.value:
                    config.agents.add(agent)
            except Exception:
                pass

        # Collect modes
        for mode in self.available_modes:
            try:
                cb = self.query_one(f"#mode-{self._sanitize_id(mode)}", Checkbox)
                if cb.value:
                    config.modes.add(mode)
            except Exception:
                pass

        # Collect rules
        for rule in self.available_rules:
            try:
                cb = self.query_one(f"#rule-{self._sanitize_id(rule)}", Checkbox)
                if cb.value:
                    config.rules.add(rule)
            except Exception:
                pass

        return config

    def action_apply(self) -> None:
        """Apply the profile with current selections."""
        config = self._collect_selections()
        self.dismiss(config)

    def action_cancel(self) -> None:
        """Cancel without applying."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "apply":
            self.action_apply()
        elif event.button.id == "cancel":
            self.action_cancel()
