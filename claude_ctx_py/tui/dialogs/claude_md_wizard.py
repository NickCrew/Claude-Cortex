"""CLAUDE.md Configuration Wizard Dialog."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Label, Static

from ...core import _resolve_claude_dir


@dataclass
class WizardConfig:
    """Configuration collected by the wizard."""
    core_files: Set[str] = field(default_factory=set)
    rules: Set[str] = field(default_factory=set)
    modes: Set[str] = field(default_factory=set)
    prompts: Set[str] = field(default_factory=set)
    mcp_docs: Set[str] = field(default_factory=set)


def discover_available_files(claude_dir: Path) -> Dict[str, List[str]]:
    """Discover available configuration files.

    Returns:
        Dict with keys: core, rules, modes, prompts, mcp_docs
    """
    result: Dict[str, List[str]] = {
        "core": [],
        "rules": [],
        "modes": [],
        "prompts": [],
        "mcp_docs": [],
    }
    rule_names: Set[str] = set()
    mode_names: Set[str] = set()

    # Core files
    for name in ["FLAGS.md", "PRINCIPLES.md", "RULES.md"]:
        if (claude_dir / name).exists():
            result["core"].append(name)

    # Rules (active + inactive)
    for rules_dir in [claude_dir / "rules", claude_dir / "inactive" / "rules"]:
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.md")):
                rule_names.add(f.name)

    # Modes (active + inactive)
    for modes_dir in [claude_dir / "modes", claude_dir / "inactive" / "modes"]:
        if modes_dir.exists():
            for f in sorted(modes_dir.glob("*.md")):
                if f.is_file():
                    mode_names.add(f.name)

    # Prompts (from subdirectories)
    prompts_dir = claude_dir / "prompts"
    if prompts_dir.exists():
        for category_dir in sorted(prompts_dir.iterdir()):
            if category_dir.is_dir() and not category_dir.name.startswith("."):
                for f in sorted(category_dir.glob("*.md")):
                    if f.is_file():
                        result["prompts"].append(f"{category_dir.name}/{f.stem}")

    # MCP docs
    mcp_docs_dir = claude_dir / "mcp" / "docs"
    if mcp_docs_dir.exists():
        for f in sorted(mcp_docs_dir.glob("*.md")):
            result["mcp_docs"].append(f.name)

    result["rules"] = sorted(rule_names)
    result["modes"] = sorted(mode_names)

    return result


def parse_current_claude_md(claude_dir: Path) -> WizardConfig:
    """Read current active state from filesystem (.active-* and live files)."""
    config = WizardConfig()

    # Core files present in CLAUDE dir are always included
    for name in ["FLAGS.md", "PRINCIPLES.md", "RULES.md"]:
        if (claude_dir / name).exists():
            config.core_files.add(name)

    # Rules: active dir and .active-rules tracker
    rules_dir = claude_dir / "rules"
    if rules_dir.exists():
        for f in sorted(rules_dir.glob("*.md")):
            config.rules.add(f.name)
    active_rules_file = claude_dir / ".active-rules"
    if active_rules_file.exists():
        for line in active_rules_file.read_text().splitlines():
            line = line.strip()
            if line:
                config.rules.add(line if line.endswith(".md") else f"{line}.md" if "." not in line else line)

    # Modes: active dir and .active-modes tracker
    modes_dir = claude_dir / "modes"
    if modes_dir.exists():
        for f in sorted(modes_dir.glob("*.md")):
            config.modes.add(f.name)
    active_modes_file = claude_dir / ".active-modes"
    if active_modes_file.exists():
        for line in active_modes_file.read_text().splitlines():
            line = line.strip()
            if line:
                config.modes.add(line if line.endswith(".md") else f"{line}.md" if "." not in line else line)

    # Prompts: from .active-prompts tracker
    active_prompts_file = claude_dir / ".active-prompts"
    if active_prompts_file.exists():
        for line in active_prompts_file.read_text().splitlines():
            line = line.strip()
            if line:
                config.prompts.add(line)

    # MCP docs: keep enabled list based on presence in mcp/docs
    mcp_docs_dir = claude_dir / "mcp" / "docs"
    if mcp_docs_dir.exists():
        for f in sorted(mcp_docs_dir.glob("*.md")):
            config.mcp_docs.add(f.name)

    return config


def generate_claude_md(config: WizardConfig) -> str:
    """Generate CLAUDE.md content from config.

    Args:
        config: The wizard configuration

    Returns:
        Generated CLAUDE.md content
    """
    lines = [
        "# Claude Framework Entry Point",
        "",
        "# Core Framework",
    ]

    # Core files (only include selected)
    for name in ["FLAGS.md", "PRINCIPLES.md", "RULES.md"]:
        if name in config.core_files:
            lines.append(f"@{name}")

    lines.extend(["", "# Rules"])
    for rule in sorted(config.rules):
        lines.append(f"@rules/{rule}")

    lines.extend(["", "# Behavioral Modes"])
    for mode in sorted(config.modes):
        lines.append(f"@modes/{mode}")

    if config.prompts:
        lines.extend(["", "# Prompt Library"])
        for prompt in sorted(config.prompts):
            lines.append(f"@prompts/{prompt}.md")

    lines.extend(["", "# MCP Documentation"])
    for doc in sorted(config.mcp_docs):
        lines.append(f"@mcp/docs/{doc}")

    lines.append("")
    return "\n".join(lines)


class ClaudeMdWizard(ModalScreen[Optional[WizardConfig]]):
    """Wizard dialog for configuring CLAUDE.md."""

    CSS = """
    ClaudeMdWizard {
        align: center middle;
    }

    ClaudeMdWizard #dialog {
        width: 85%;
        max-width: 100;
        height: 85%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    ClaudeMdWizard #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    ClaudeMdWizard #step-indicator {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    ClaudeMdWizard #step-content {
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface;
        padding: 1;
    }

    ClaudeMdWizard .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    ClaudeMdWizard .section-desc {
        color: $text-muted;
        margin-bottom: 1;
    }

    ClaudeMdWizard .checkbox-item {
        margin-bottom: 0;
    }

    ClaudeMdWizard #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    ClaudeMdWizard #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("left", "prev_step", "Previous"),
        Binding("right", "next_step", "Next"),
    ]

    STEPS = ["Core Framework", "Rules", "Modes", "Prompts", "MCP Documentation", "Review"]

    def __init__(self) -> None:
        super().__init__()
        self.claude_dir = _resolve_claude_dir()
        self.available = discover_available_files(self.claude_dir)
        self.config = parse_current_claude_md(self.claude_dir)
        self.current_step = 0

    def compose(self) -> ComposeResult:
        with Container(id="dialog", classes="visible"):
            yield Static("🔧 CLAUDE.md Configuration Wizard", id="dialog-title")
            yield Static(self._step_indicator(), id="step-indicator")

            with VerticalScroll(id="step-content"):
                yield from self._compose_step()

            yield Static(
                "[dim]← Previous • → Next • Space Toggle • Esc Cancel[/dim]",
                id="dialog-hint",
            )

            with Container(id="dialog-buttons"):
                yield Button("← Back", variant="default", id="back", disabled=True)
                yield Button("Next →", variant="primary", id="next")
                yield Button("Cancel", variant="default", id="cancel")

    def _step_indicator(self) -> str:
        """Generate step indicator text."""
        parts = []
        for i, step in enumerate(self.STEPS):
            if i == self.current_step:
                parts.append(f"[bold cyan]({i + 1}) {step}[/bold cyan]")
            elif i < self.current_step:
                parts.append(f"[green]✓ {step}[/green]")
            else:
                parts.append(f"[dim]{step}[/dim]")
        return " → ".join(parts)

    def _compose_step(self) -> ComposeResult:
        """Compose the current step's content."""
        if self.current_step == 0:
            yield from self._compose_core_step()
        elif self.current_step == 1:
            yield from self._compose_rules_step()
        elif self.current_step == 2:
            yield from self._compose_modes_step()
        elif self.current_step == 3:
            yield from self._compose_prompts_step()
        elif self.current_step == 4:
            yield from self._compose_mcp_step()
        elif self.current_step == 5:
            yield from self._compose_review_step()

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as a widget ID."""
        return name.replace(".", "-").replace("_", "-").lower()

    def _compose_core_step(self) -> ComposeResult:
        yield Static("[bold]Core Framework Files[/bold]", classes="section-title")
        yield Static(
            "Select the foundational framework files to include.",
            classes="section-desc",
        )

        for name in self.available["core"]:
            checked = name in self.config.core_files
            desc = {
                "FLAGS.md": "Behavioral flags and MCP server toggles",
                "PRINCIPLES.md": "Software engineering principles",
                "RULES.md": "Core behavioral rules",
            }.get(name, "")
            yield Checkbox(
                f"{name} - {desc}",
                value=checked,
                id=f"core-{self._sanitize_id(name)}",
                classes="checkbox-item",
            )

    def _compose_rules_step(self) -> ComposeResult:
        yield Static("[bold]Rules[/bold]", classes="section-title")
        yield Static(
            "Select which rule modules to enable.",
            classes="section-desc",
        )

        for name in self.available["rules"]:
            checked = name in self.config.rules
            display = name.replace(".md", "").replace("-", " ").title()
            yield Checkbox(
                display,
                value=checked,
                id=f"rule-{self._sanitize_id(name)}",
                classes="checkbox-item",
            )

    def _compose_modes_step(self) -> ComposeResult:
        yield Static("[bold]Behavioral Modes[/bold]", classes="section-title")
        yield Static(
            "Select behavioral modes to activate.",
            classes="section-desc",
        )

        for name in self.available["modes"]:
            checked = name in self.config.modes
            display = name.replace(".md", "").replace("_", " ")
            yield Checkbox(
                display,
                value=checked,
                id=f"mode-{self._sanitize_id(name)}",
                classes="checkbox-item",
            )

    def _compose_prompts_step(self) -> ComposeResult:
        yield Static("[bold]Prompt Library[/bold]", classes="section-title")
        yield Static(
            "Select prompts to inject into context.",
            classes="section-desc",
        )

        if not self.available["prompts"]:
            yield Static(
                "[dim]No prompts found. Create prompts in ~/.cortex/prompts/[/dim]",
                classes="section-desc",
            )
            return

        for slug in self.available["prompts"]:
            checked = slug in self.config.prompts
            # Format: category/name -> [category] Name
            if "/" in slug:
                category, name = slug.split("/", 1)
                display = f"[{category}] {name.replace('-', ' ').title()}"
            else:
                display = slug.replace("-", " ").title()
            yield Checkbox(
                display,
                value=checked,
                id=f"prompt-{self._sanitize_id(slug)}",
                classes="checkbox-item",
            )

    def _compose_mcp_step(self) -> ComposeResult:
        yield Static("[bold]MCP Documentation[/bold]", classes="section-title")
        yield Static(
            "Select MCP server documentation to include for Claude's reference.",
            classes="section-desc",
        )

        for name in self.available["mcp_docs"]:
            checked = name in self.config.mcp_docs
            display = name.replace(".md", "")
            yield Checkbox(
                display,
                value=checked,
                id=f"mcp-{self._sanitize_id(name)}",
                classes="checkbox-item",
            )

    def _compose_review_step(self) -> ComposeResult:
        yield Static("[bold]Review Configuration[/bold]", classes="section-title")
        yield Static(
            "Review your selections before saving.",
            classes="section-desc",
        )

        # Summary
        lines = []

        lines.append("[bold]Core Framework:[/bold]")
        if self.config.core_files:
            for f in sorted(self.config.core_files):
                lines.append(f"  [green]✓[/green] {f}")
        else:
            lines.append("  [dim]None selected[/dim]")

        lines.append("\n[bold]Rules:[/bold]")
        if self.config.rules:
            for f in sorted(self.config.rules):
                lines.append(f"  [green]✓[/green] {f}")
        else:
            lines.append("  [dim]None selected[/dim]")

        lines.append("\n[bold]Modes:[/bold]")
        if self.config.modes:
            for f in sorted(self.config.modes):
                lines.append(f"  [green]✓[/green] {f}")
        else:
            lines.append("  [dim]None selected[/dim]")

        lines.append("\n[bold]Prompts:[/bold]")
        if self.config.prompts:
            for f in sorted(self.config.prompts):
                lines.append(f"  [green]✓[/green] {f}")
        else:
            lines.append("  [dim]None selected[/dim]")

        lines.append("\n[bold]MCP Documentation:[/bold]")
        if self.config.mcp_docs:
            for f in sorted(self.config.mcp_docs):
                lines.append(f"  [green]✓[/green] {f}")
        else:
            lines.append("  [dim]None selected[/dim]")

        yield Static("\n".join(lines))

    def _collect_step_data(self) -> None:
        """Collect data from current step's checkboxes."""
        if self.current_step == 0:
            self.config.core_files = set()
            for name in self.available["core"]:
                try:
                    cb = self.query_one(f"#core-{self._sanitize_id(name)}", Checkbox)
                    if cb.value:
                        self.config.core_files.add(name)
                except Exception:
                    pass

        elif self.current_step == 1:
            self.config.rules = set()
            for name in self.available["rules"]:
                try:
                    cb = self.query_one(f"#rule-{self._sanitize_id(name)}", Checkbox)
                    if cb.value:
                        self.config.rules.add(name)
                except Exception:
                    pass

        elif self.current_step == 2:
            self.config.modes = set()
            for name in self.available["modes"]:
                try:
                    cb = self.query_one(f"#mode-{self._sanitize_id(name)}", Checkbox)
                    if cb.value:
                        self.config.modes.add(name)
                except Exception:
                    pass

        elif self.current_step == 3:
            self.config.prompts = set()
            for slug in self.available["prompts"]:
                try:
                    cb = self.query_one(f"#prompt-{self._sanitize_id(slug)}", Checkbox)
                    if cb.value:
                        self.config.prompts.add(slug)
                except Exception:
                    pass

        elif self.current_step == 4:
            self.config.mcp_docs = set()
            for name in self.available["mcp_docs"]:
                try:
                    cb = self.query_one(f"#mcp-{self._sanitize_id(name)}", Checkbox)
                    if cb.value:
                        self.config.mcp_docs.add(name)
                except Exception:
                    pass

    def _update_step(self) -> None:
        """Update the display for the current step."""
        # Update step indicator
        self.query_one("#step-indicator", Static).update(self._step_indicator())

        # Update content
        content = self.query_one("#step-content", VerticalScroll)
        content.remove_children()
        for widget in self._compose_step():
            content.mount(widget)

        # Update buttons
        back_btn = self.query_one("#back", Button)
        next_btn = self.query_one("#next", Button)

        back_btn.disabled = self.current_step == 0

        if self.current_step == len(self.STEPS) - 1:
            next_btn.label = "Save"
            next_btn.variant = "success"
        else:
            next_btn.label = "Next →"
            next_btn.variant = "primary"

    def action_prev_step(self) -> None:
        """Go to previous step."""
        if self.current_step > 0:
            self._collect_step_data()
            self.current_step -= 1
            self._update_step()

    def action_next_step(self) -> None:
        """Go to next step or save."""
        self._collect_step_data()

        if self.current_step < len(self.STEPS) - 1:
            self.current_step += 1
            self._update_step()
        else:
            # Save and exit
            self.dismiss(self.config)

    def action_cancel(self) -> None:
        """Cancel the wizard."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "back":
            self.action_prev_step()
        elif event.button.id == "next":
            self.action_next_step()
        elif event.button.id == "cancel":
            self.dismiss(None)
