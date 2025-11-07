"""Modal dialog system for TUI using Textual."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input
from textual.binding import Binding
from typing import Optional

from .tui_icons import Icons
from .tui_format import Format


class ConfirmDialog(ModalScreen[bool]):
    """Confirmation dialog modal."""

    BINDINGS = [
        Binding("y", "confirm_yes", "Yes"),
        Binding("n", "confirm_no", "No"),
        Binding("escape", "confirm_no", "Cancel"),
    ]

    def __init__(self, title: str, message: str, default: bool = False):
        """Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
            default: Default choice (True = Yes, False = No)
        """
        super().__init__()
        self.title = title
        self.message = message
        self.default = default

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.WARNING} [bold]{self.title}[/bold]", id="dialog-title")
                yield Static(self.message, id="dialog-message")
                with Container(id="dialog-buttons"):
                    yield Button("Yes", variant="success" if self.default else "default", id="yes")
                    yield Button("No", variant="error" if not self.default else "default", id="no")

    def action_confirm_yes(self) -> None:
        """Confirm with Yes."""
        self.dismiss(True)

    def action_confirm_no(self) -> None:
        """Confirm with No."""
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss(event.button.id == "yes")


class ErrorDialog(ModalScreen[None]):
    """Error dialog modal."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, message: str, details: str = ""):
        """Initialize error dialog.

        Args:
            title: Error title
            message: Error message
            details: Optional error details
        """
        super().__init__()
        self.title = title
        self.message = message
        self.details = details

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.ERROR} [bold red]{self.title}[/bold red]", id="dialog-title")
                yield Static(self.message, id="dialog-message")
                if self.details:
                    yield Static(f"[dim]{Format.truncate(self.details, 200)}[/dim]", id="dialog-details")
                yield Button("Close", variant="error", id="close")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss()


class InfoDialog(ModalScreen[None]):
    """Information dialog modal."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, message: str):
        """Initialize info dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.INFO} [bold blue]{self.title}[/bold blue]", id="dialog-title")
                yield Static(self.message, id="dialog-message")
                yield Button("OK", variant="primary", id="ok")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss()


class LoadingOverlay(ModalScreen[None]):
    """Loading overlay modal - non-dismissible."""

    def __init__(self, message: str = "Loading..."):
        """Initialize loading overlay.

        Args:
            message: Loading message
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the overlay."""
        with Container(id="loading-overlay"):
            yield Static(f"{Icons.RUNNING} [yellow]{self.message}[/yellow]", id="loading-message")
            yield Static("[dim]Please wait...[/dim]", id="loading-subtitle")

    # No bindings - loading overlay can't be dismissed by user


class TaskEditorDialog(ModalScreen[Optional[dict]]):
    """Dialog for creating or editing orchestration tasks."""

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    def __init__(self, title: str, defaults: Optional[dict] = None):
        super().__init__()
        self.title = title
        self.defaults = defaults or {}

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.CODE} [bold]{self.title}[/bold]", id="dialog-title")
                yield Input(value=self.defaults.get("name", ""), placeholder="Task name", id="task-name")
                yield Input(value=self.defaults.get("workstream", "primary"), placeholder="Workstream", id="task-workstream")
                yield Input(value=self.defaults.get("category", "general"), placeholder="Category (e.g. development)", id="task-category")
                yield Input(value=self.defaults.get("status", "pending"), placeholder="Status (pending/running/complete)", id="task-status")
                yield Input(value=str(self.defaults.get("progress", 0)), placeholder="Progress 0-100", id="task-progress")
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def action_close(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        name = self.query_one("#task-name", Input).value.strip()
        workstream = self.query_one("#task-workstream", Input).value.strip()
        category = self.query_one("#task-category", Input).value.strip()
        status = self.query_one("#task-status", Input).value.strip()
        progress = self.query_one("#task-progress", Input).value.strip()

        if not name:
            self.dismiss(None)
            return

        self.dismiss({
            "name": name,
            "workstream": workstream or "primary",
            "category": category or "general",
            "status": status or "pending",
            "progress": progress or "0",
        })


class PromptDialog(ModalScreen[Optional[str]]):
    """Simple prompt dialog to capture a single line of text."""

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    def __init__(self, title: str, prompt: str, *, placeholder: str = "", default: str = ""):
        super().__init__()
        self.title = title
        self.prompt = prompt
        self.placeholder = placeholder
        self.default = default

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.INFO} [bold]{self.title}[/bold]", id="dialog-title")
                yield Static(self.prompt, id="dialog-message")
                yield Input(value=self.default, placeholder=self.placeholder, id="prompt-input")
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def action_close(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        value = self.query_one("#prompt-input", Input).value.strip()
        self.dismiss(value or None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_submit()
        else:
            self.dismiss(None)


class TextViewerDialog(ModalScreen[None]):
    """Scrollable text viewer for long-form content (docs, snippets, logs)."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, body: str):
        super().__init__()
        self.title = title
        self.body = body

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.DOC} [bold]{self.title}[/bold]", id="dialog-title")
                yield Static(f"[dim]{Format.truncate(self.body, 4000)}[/dim]", id="dialog-message")
                yield Button("Close", variant="primary", id="close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
