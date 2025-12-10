"""Backup Manager Dialog for creating and restoring backups."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, Static

from ...core.backup import (
    BackupInfo,
    create_backup,
    list_backups,
    restore_backup,
    delete_backup,
    get_backup_summary,
)


class BackupManagerDialog(ModalScreen[Optional[str]]):
    """Dialog for managing backups."""

    CSS = """
    BackupManagerDialog {
        align: center middle;
    }

    BackupManagerDialog #dialog {
        width: 85%;
        max-width: 90;
        height: 80%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    BackupManagerDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    BackupManagerDialog #backup-list-container {
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface;
        padding: 1;
    }

    BackupManagerDialog .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    BackupManagerDialog #backup-details {
        height: auto;
        max-height: 6;
        border: solid $primary-darken-3;
        background: $surface-darken-1;
        padding: 1;
        margin-top: 1;
    }

    BackupManagerDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    BackupManagerDialog #dialog-buttons Button {
        margin: 0 1;
    }

    BackupManagerDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("n", "new_backup", "New Backup"),
        Binding("r", "restore", "Restore"),
        Binding("d", "delete", "Delete"),
        Binding("f5", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.backups: List[BackupInfo] = []
        self.selected_backup: Optional[BackupInfo] = None

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("Backup Manager", id="dialog-title")

            with Container(id="backup-list-container"):
                yield Static("[bold]Available Backups[/bold]", classes="section-title")
                yield ListView(id="backup-list")

            yield Static("", id="backup-details")

            yield Static(
                "[dim]n New Backup • r Restore • d Delete • Esc Close[/dim]",
                id="dialog-hint",
            )

            with Horizontal(id="dialog-buttons"):
                yield Button("New Backup", variant="success", id="new")
                yield Button("Restore", variant="primary", id="restore")
                yield Button("Delete", variant="warning", id="delete")
                yield Button("Close", variant="default", id="close")

    def on_mount(self) -> None:
        """Load backups when mounted."""
        self._load_backups()

    def _load_backups(self) -> None:
        """Load available backups."""
        self.backups = list_backups()
        self._update_list()

    def _update_list(self) -> None:
        """Update the backup list."""
        backup_list = self.query_one("#backup-list", ListView)
        backup_list.clear()

        if not self.backups:
            backup_list.append(ListItem(Label("[dim]No backups available[/dim]")))
            return

        for backup in self.backups:
            created_str = backup.created.strftime("%Y-%m-%d %H:%M")
            label = f"[green]●[/green] {backup.name} [dim]({backup.size_human}) {created_str}[/dim]"
            item = ListItem(Label(label), id=f"backup-{self._sanitize_id(backup.name)}")
            backup_list.append(item)

    def _sanitize_id(self, name: str) -> str:
        """Sanitize a name for use as a widget ID."""
        return name.replace(".", "-").replace("_", "-").replace(" ", "-").lower()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection."""
        item_id = event.item.id or ""

        if item_id.startswith("backup-"):
            # Find the selected backup
            for backup in self.backups:
                if self._sanitize_id(backup.name) in item_id:
                    self.selected_backup = backup
                    self._show_backup_details(backup)
                    break

    def _show_backup_details(self, backup: BackupInfo) -> None:
        """Show details for selected backup."""
        details = self.query_one("#backup-details", Static)

        created_str = backup.created.strftime("%Y-%m-%d %H:%M:%S")
        text = f"""[bold]{backup.name}[/bold]
Created: {created_str}
Size: {backup.size_human}
Path: {backup.path}
"""
        details.update(text)

    def action_new_backup(self) -> None:
        """Create a new backup."""
        success, msg, _ = create_backup()
        if success:
            self.notify("Backup created", severity="information", timeout=2)
            self._load_backups()
        else:
            self.notify(msg, severity="error", timeout=3)

    def action_restore(self) -> None:
        """Restore from selected backup."""
        if not self.selected_backup:
            self.notify("Select a backup first", severity="warning", timeout=2)
            return

        success, msg = restore_backup(self.selected_backup)
        if success:
            self.notify("Backup restored", severity="information", timeout=2)
        else:
            self.notify(msg, severity="error", timeout=3)

    def action_delete(self) -> None:
        """Delete selected backup."""
        if not self.selected_backup:
            self.notify("Select a backup first", severity="warning", timeout=2)
            return

        success, msg = delete_backup(self.selected_backup)
        if success:
            self.notify("Backup deleted", severity="information", timeout=2)
            self.selected_backup = None
            self._load_backups()
        else:
            self.notify(msg, severity="error", timeout=3)

    def action_refresh(self) -> None:
        """Refresh the backup list."""
        self._load_backups()
        self.notify("Refreshed", severity="information", timeout=1)

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new":
            self.action_new_backup()
        elif event.button.id == "restore":
            self.action_restore()
        elif event.button.id == "delete":
            self.action_delete()
        elif event.button.id == "close":
            self.action_close()
