"""Modal dialog system for TUI using Textual."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.binding import Binding

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
