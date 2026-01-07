"""Asset management dialogs for TUI."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple, Literal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static, RadioSet, RadioButton, Checkbox

from ...tui_icons import Icons
from ...tui_format import Format
from ...core.asset_discovery import Asset, ClaudeDir, AssetCategory, InstallStatus


class TargetSelectorDialog(ModalScreen[Optional[Path]]):
    """Dialog for selecting installation target directory."""

    CSS = """
    TargetSelectorDialog {
        align: center middle;
    }

    TargetSelectorDialog #dialog {
        width: 70;
        max-width: 90%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    TargetSelectorDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    TargetSelectorDialog RadioSet {
        width: 100%;
        padding: 1;
    }

    TargetSelectorDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
    ]

    def __init__(self, directories: List[ClaudeDir], current: Optional[Path] = None):
        """Initialize target selector.

        Args:
            directories: List of available cortex directories
            current: Currently selected directory
        """
        super().__init__()
        self.directories = directories
        self.current = current

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{Icons.FOLDER} [bold]Select Installation Target[/bold]",
                    id="dialog-title",
                )

                with RadioSet(id="target-radio"):
                    for cd in self.directories:
                        # Format label with scope indicator
                        scope_color = {
                            "global": "cyan",
                            "project": "green",
                            "parent": "yellow",
                        }.get(cd.scope, "white")

                        label = f"[{scope_color}]{cd.path}[/{scope_color}] ({cd.scope})"
                        is_current = self.current and cd.path == self.current
                        yield RadioButton(label, value=bool(is_current))

                with Container(id="dialog-buttons"):
                    yield Button("Select", variant="primary", id="select")
                    yield Button("Cancel", variant="default", id="cancel")

    def action_cancel(self) -> None:
        """Cancel selection."""
        self.dismiss(None)

    def action_select(self) -> None:
        """Confirm selection."""
        radio_set = self.query_one("#target-radio", RadioSet)
        if radio_set.pressed_index is not None and radio_set.pressed_index < len(self.directories):
            self.dismiss(self.directories[radio_set.pressed_index].path)
        else:
            self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "select":
            self.action_select()
        else:
            self.action_cancel()


class AssetDetailDialog(ModalScreen[Optional[str]]):
    """Dialog showing asset details with install/uninstall options."""

    CSS = """
    AssetDetailDialog {
        align: center middle;
    }

    AssetDetailDialog #dialog {
        width: 80;
        max-width: 95%;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    AssetDetailDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }

    AssetDetailDialog #dialog-content {
        max-height: 50vh;
        padding: 1;
    }

    AssetDetailDialog .detail-row {
        padding: 0 0 1 0;
    }

    AssetDetailDialog .detail-label {
        color: $text-muted;
        width: 15;
    }

    AssetDetailDialog .detail-value {
        width: 1fr;
    }

    AssetDetailDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
        border-top: solid $primary;
    }

    AssetDetailDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        padding: 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("i", "install", "Install"),
        Binding("u", "uninstall", "Uninstall"),
        Binding("d", "diff", "View Diff"),
    ]

    def __init__(
        self,
        asset: Asset,
        status: InstallStatus,
        target_dir: Optional[Path] = None,
    ):
        """Initialize asset detail dialog.

        Args:
            asset: Asset to display
            status: Current installation status
            target_dir: Target installation directory
        """
        super().__init__()
        self.asset = asset
        self.status = status
        self.target_dir = target_dir

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        # Category icon
        category_icons = {
            AssetCategory.HOOKS: "📎",
            AssetCategory.COMMANDS: "📝",
            AssetCategory.AGENTS: "🤖",
            AssetCategory.SKILLS: "🎯",
            AssetCategory.MODES: "🎨",
            AssetCategory.WORKFLOWS: "🔄",
            AssetCategory.FLAGS: "🚩",
            AssetCategory.RULES: "🧭",
            AssetCategory.PROFILES: "👤",
            AssetCategory.SCENARIOS: "🎬",
            AssetCategory.TASKS: "✅",
            AssetCategory.SETTINGS: "⚙️",
        }
        icon = category_icons.get(self.asset.category, "📦")

        # Status formatting
        status_text = {
            InstallStatus.NOT_INSTALLED: "[dim]○ Not Installed[/dim]",
            InstallStatus.INSTALLED_SAME: "[green]● Installed[/green]",
            InstallStatus.INSTALLED_DIFFERENT: "[yellow]⚠ Installed (differs)[/yellow]",
            InstallStatus.INSTALLED_NEWER: "[cyan]● Installed (newer)[/cyan]",
            InstallStatus.INSTALLED_OLDER: "[yellow]● Installed (older)[/yellow]",
        }.get(self.status, "[dim]? Unknown[/dim]")

        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{icon} [bold]{self.asset.display_name}[/bold]",
                    id="dialog-title",
                )

                with VerticalScroll(id="dialog-content"):
                    # Category
                    yield Static(
                        f"[dim]Category:[/dim] {self.asset.category.value}",
                        classes="detail-row",
                    )

                    # Status
                    yield Static(
                        f"[dim]Status:[/dim] {status_text}",
                        classes="detail-row",
                    )

                    # Version
                    if self.asset.version:
                        yield Static(
                            f"[dim]Version:[/dim] {self.asset.version}",
                            classes="detail-row",
                        )

                    # Target
                    if self.target_dir:
                        yield Static(
                            f"[dim]Target:[/dim] {self.target_dir}",
                            classes="detail-row",
                        )

                    # Description
                    yield Static("")
                    yield Static("[dim]Description:[/dim]", classes="detail-row")
                    yield Static(
                        self.asset.description or "[dim]No description[/dim]",
                        classes="detail-row",
                    )

                    # Dependencies
                    if self.asset.dependencies:
                        yield Static("")
                        yield Static("[dim]Dependencies:[/dim]", classes="detail-row")
                        for dep in self.asset.dependencies:
                            yield Static(f"  • {dep}", classes="detail-row")

                    # Source path
                    yield Static("")
                    yield Static(
                        f"[dim]Source:[/dim] {self.asset.source_path}",
                        classes="detail-row",
                    )

                # Keyboard shortcuts hint
                if self.status == InstallStatus.NOT_INSTALLED:
                    hint = "[dim][i] Install • [esc] Close[/dim]"
                else:
                    hint = "[dim][i] Update • [u] Uninstall • [d] View Diff • [esc] Close[/dim]"
                yield Static(hint, id="dialog-hint")

                with Horizontal(id="dialog-buttons"):
                    # Show appropriate buttons based on status
                    if self.status == InstallStatus.NOT_INSTALLED:
                        yield Button("Install [i]", variant="success", id="install")
                    else:
                        yield Button("Update [i]", variant="primary", id="install")
                        yield Button("Uninstall [u]", variant="error", id="uninstall")
                        # Show diff button for any installed asset
                        diff_variant: Literal["default", "primary", "success", "warning", "error"] = "warning" if self.status == InstallStatus.INSTALLED_DIFFERENT else "default"
                        yield Button("View Diff [d]", variant=diff_variant, id="diff")

                    yield Button("Close [esc]", variant="default", id="close")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def action_install(self) -> None:
        """Request install action."""
        self.dismiss("install")

    def action_uninstall(self) -> None:
        """Request uninstall action."""
        self.dismiss("uninstall")

    def action_diff(self) -> None:
        """Request diff view."""
        self.dismiss("diff")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close":
            self.dismiss(None)
        elif event.button.id == "install":
            self.dismiss("install")
        elif event.button.id == "uninstall":
            self.dismiss("uninstall")
        elif event.button.id == "diff":
            self.dismiss("diff")


class DiffViewerDialog(ModalScreen[Optional[str]]):
    """Dialog for viewing diff between source and installed asset."""

    CSS = """
    DiffViewerDialog {
        align: center middle;
    }

    DiffViewerDialog #dialog {
        width: 90%;
        max-width: 120;
        height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $warning;
        opacity: 1;
    }

    DiffViewerDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    DiffViewerDialog #diff-content {
        height: 1fr;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }

    DiffViewerDialog .diff-add {
        color: $success;
    }

    DiffViewerDialog .diff-del {
        color: $error;
    }

    DiffViewerDialog .diff-info {
        color: $warning;
    }

    DiffViewerDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        padding: 1 0;
    }

    DiffViewerDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("a", "apply", "Apply Update"),
        Binding("k", "keep", "Keep Installed"),
    ]

    def __init__(self, asset_name: str, diff_text: str):
        """Initialize diff viewer.

        Args:
            asset_name: Name of the asset
            diff_text: Unified diff text
        """
        super().__init__()
        self.asset_name = asset_name
        self.diff_text = diff_text

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{Icons.DOC} [bold]Diff: {self.asset_name}[/bold]",
                    id="dialog-title",
                )

                with VerticalScroll(id="diff-content"):
                    # Colorize diff output
                    colored_diff = self._colorize_diff(self.diff_text)
                    yield Static(colored_diff, markup=True)

                yield Static(
                    "[dim]Use ↑/↓ to scroll • [a] Apply Update • [k] Keep Installed[/dim]",
                    id="dialog-hint",
                )

                with Horizontal(id="dialog-buttons"):
                    yield Button("Apply Update [a]", variant="success", id="apply")
                    yield Button("Keep Installed [k]", variant="default", id="keep")
                    yield Button("Close [esc]", variant="primary", id="close")

    def _colorize_diff(self, diff: str) -> str:
        """Colorize diff output for display."""
        lines = []
        for line in diff.split("\n"):
            if line.startswith("+++") or line.startswith("---"):
                lines.append(f"[bold]{self._escape(line)}[/bold]")
            elif line.startswith("@@"):
                lines.append(f"[cyan]{self._escape(line)}[/cyan]")
            elif line.startswith("+"):
                lines.append(f"[green]{self._escape(line)}[/green]")
            elif line.startswith("-"):
                lines.append(f"[red]{self._escape(line)}[/red]")
            else:
                lines.append(self._escape(line))
        return "\n".join(lines)

    def _escape(self, text: str) -> str:
        """Escape Rich markup characters."""
        return text.replace("[", "\\[").replace("]", "\\]")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def action_apply(self) -> None:
        """Apply the update."""
        self.dismiss("apply")

    def action_keep(self) -> None:
        """Keep installed version."""
        self.dismiss("keep")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "apply":
            self.dismiss("apply")
        elif event.button.id == "keep":
            self.dismiss("keep")
        else:
            self.dismiss(None)


class BulkInstallDialog(ModalScreen[Optional[List[str]]]):
    """Dialog for bulk installing assets by category."""

    CSS = """
    BulkInstallDialog {
        align: center middle;
    }

    BulkInstallDialog #dialog {
        width: 70;
        max-width: 90%;
        padding: 1 2;
        background: $surface;
        border: thick $success;
        opacity: 1;
    }

    BulkInstallDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    BulkInstallDialog #category-list {
        height: auto;
        max-height: 50vh;
        padding: 1;
    }

    BulkInstallDialog .category-row {
        padding: 0 0 1 0;
    }

    BulkInstallDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "install", "Install"),
        Binding("i", "install", "Install All"),
    ]

    def __init__(self, categories: List[Tuple[str, int]]):
        """Initialize bulk install dialog.

        Args:
            categories: List of (category_name, asset_count) tuples
        """
        super().__init__()
        self.categories = categories
        self.selected: List[str] = []

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        category_icons = {
            "hooks": "📎",
            "commands": "📝",
            "agents": "🤖",
            "skills": "🎯",
            "modes": "🎨",
            "workflows": "🔄",
            "rules": "🧭",
            "profiles": "👤",
            "scenarios": "🎬",
            "tasks": "✅",
            "flags": "🚩",
            "settings": "⚙️",
        }

        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{Icons.FOLDER} [bold]Bulk Install Assets[/bold]",
                    id="dialog-title",
                )

                yield Static(
                    "[dim]Select categories to install all available assets:[/dim]"
                )

                with VerticalScroll(id="category-list"):
                    for category, count in self.categories:
                        icon = category_icons.get(category, "📦")
                        yield Checkbox(
                            f"{icon} {category} ({count} assets)",
                            value=True,
                            id=f"bulk-{category}",
                            classes="category-row",
                        )

                yield Static(
                    "[dim]Space to toggle • [i] or Enter to install selected[/dim]",
                    id="dialog-hint",
                )

                with Horizontal(id="dialog-buttons"):
                    yield Button("Install Selected [i]", variant="success", id="install")
                    yield Button("Cancel [esc]", variant="default", id="cancel")

    def action_cancel(self) -> None:
        """Cancel installation."""
        self.dismiss(None)

    def action_install(self) -> None:
        """Confirm installation."""
        selected: List[str] = []
        for category, _ in self.categories:
            try:
                checkbox = self.query_one(f"#bulk-{category}", Checkbox)
            except Exception:
                continue
            if checkbox.value:
                selected.append(category)

        self.dismiss(selected)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "install":
            self.action_install()
        else:
            self.action_cancel()
