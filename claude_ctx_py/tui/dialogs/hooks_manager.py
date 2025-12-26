"""Hooks Manager Dialog for viewing and installing hooks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static

from ...core.hooks import (
    HookDefinition,
    InstalledHook,
    HOOK_EVENTS,
    get_available_hooks,
    get_installed_hooks,
    install_hook,
    uninstall_hook,
)


class HooksManagerDialog(ModalScreen[Optional[str]]):
    """Dialog for managing Claude Code hooks."""

    CSS = """
    HooksManagerDialog {
        align: center middle;
    }

    HooksManagerDialog #dialog {
        width: 90%;
        max-width: 100;
        height: 85%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    HooksManagerDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    HooksManagerDialog #hooks-container {
        height: 1fr;
    }

    HooksManagerDialog #available-hooks {
        width: 1fr;
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface;
        padding: 1;
    }

    HooksManagerDialog #installed-hooks {
        width: 1fr;
        height: 1fr;
        border: solid $success-darken-2;
        background: $surface;
        padding: 1;
    }

    HooksManagerDialog .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    HooksManagerDialog #available-list {
        height: 1fr;
    }

    HooksManagerDialog #installed-list {
        height: 1fr;
    }

    HooksManagerDialog #hook-details {
        height: auto;
        max-height: 8;
        border: solid $primary-darken-3;
        background: $surface-darken-1;
        padding: 1;
        margin-top: 1;
    }

    HooksManagerDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    HooksManagerDialog #dialog-buttons Button {
        margin: 0 1;
    }

    HooksManagerDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("i", "install", "Install"),
        Binding("u", "uninstall", "Uninstall"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, plugin_dir: Optional[Path] = None) -> None:
        """Initialize the hooks manager.

        Args:
            plugin_dir: Plugin directory for finding available hooks
        """
        super().__init__()
        self.plugin_dir = plugin_dir
        self.available_hooks: List[HookDefinition] = []
        self.installed_hooks: List[InstalledHook] = []
        self.selected_hook: Optional[HookDefinition] = None

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Hooks Manager", id="dialog-title")

            with Horizontal(id="hooks-container"):
                with Container(id="available-hooks"):
                    yield Static("[bold]Available Hooks[/bold]", classes="section-title")
                    yield ListView(id="available-list")

                with Container(id="installed-hooks"):
                    yield Static("[bold]Installed Hooks[/bold]", classes="section-title")
                    yield ListView(id="installed-list")

            yield Static("", id="hook-details")

            yield Static(
                "[dim]i Install • u Uninstall • r Refresh • Esc Close[/dim]",
                id="dialog-hint",
            )

            with Horizontal(id="dialog-buttons"):
                yield Button("Install", variant="success", id="install")
                yield Button("Uninstall", variant="warning", id="uninstall")
                yield Button("Close", variant="default", id="close")

    def on_mount(self) -> None:
        """Load hooks when mounted."""
        self._load_hooks()

    def _load_hooks(self) -> None:
        """Load available and installed hooks."""
        try:
            self.available_hooks = get_available_hooks(self.plugin_dir)
        except Exception:
            self.available_hooks = []
        try:
            self.installed_hooks = get_installed_hooks()
        except Exception:
            self.installed_hooks = []
        self._update_lists()

    def _update_lists(self) -> None:
        """Update the hook lists."""
        # Update available hooks list
        try:
            available_list = self.query_one("#available-list", ListView)
            available_list.clear()

            if not self.available_hooks:
                available_list.append(ListItem(Label("[dim]No hooks found[/dim]")))
            else:
                for hook in self.available_hooks:
                    status = "[green]✓[/green] " if hook.is_installed else "[dim]○[/dim] "
                    label = f"{status}{hook.name} [dim]({hook.event})[/dim]"
                    item = ListItem(Label(label), id=f"avail-{self._sanitize_id(hook.name)}")
                    available_list.append(item)
        except Exception:
            pass

        # Update installed hooks list
        try:
            installed_list = self.query_one("#installed-list", ListView)
            installed_list.clear()

            if not self.installed_hooks:
                installed_list.append(ListItem(Label("[dim]No hooks installed[/dim]")))
            else:
                for inst_hook in self.installed_hooks:
                    # Extract hook name from command
                    cmd = inst_hook.command
                    name = cmd.split("/")[-1].replace(".py", "") if "/" in cmd else cmd
                    label = f"[green]●[/green] {name} [dim]({inst_hook.event})[/dim]"
                    item = ListItem(Label(label), id=f"inst-{self._sanitize_id(name)}")
                    installed_list.append(item)
        except Exception:
            pass

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as a widget ID."""
        return name.replace(".", "-").replace("_", "-").replace(" ", "-").lower()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection."""
        item_id = event.item.id or ""

        if item_id.startswith("avail-"):
            # Find the selected available hook
            hook_name = item_id.replace("avail-", "")
            for hook in self.available_hooks:
                if self._sanitize_id(hook.name) == hook_name:
                    self.selected_hook = hook
                    self._show_hook_details(hook)
                    break

    def _show_hook_details(self, hook: HookDefinition) -> None:
        """Show details for selected hook."""
        details = self.query_one("#hook-details", Static)

        status = "[green]Installed[/green]" if hook.is_installed else "[yellow]Not installed[/yellow]"
        text = f"""[bold]{hook.name}[/bold] · {status}
Event: [cyan]{hook.event}[/cyan]
{hook.description}
"""
        details.update(text)

    def action_install(self) -> None:
        """Install the selected hook."""
        if not self.selected_hook:
            return

        if self.selected_hook.is_installed:
            self.notify("Hook already installed", severity="warning", timeout=2)
            return

        success, msg = install_hook(self.selected_hook)
        if success:
            self.notify(msg, severity="information", timeout=2)
            self._load_hooks()
        else:
            self.notify(msg, severity="error", timeout=3)

    def action_uninstall(self) -> None:
        """Uninstall the selected hook."""
        if not self.selected_hook:
            return

        if not self.selected_hook.is_installed:
            self.notify("Hook not installed", severity="warning", timeout=2)
            return

        success, msg = uninstall_hook(self.selected_hook)
        if success:
            self.notify(msg, severity="information", timeout=2)
            self._load_hooks()
        else:
            self.notify(msg, severity="error", timeout=3)

    def action_refresh(self) -> None:
        """Refresh the hooks lists."""
        self._load_hooks()
        self.notify("Refreshed", severity="information", timeout=1)

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "install":
            self.action_install()
        elif event.button.id == "uninstall":
            self.action_uninstall()
        elif event.button.id == "close":
            self.action_close()
