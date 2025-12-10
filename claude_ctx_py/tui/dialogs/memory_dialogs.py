"""Memory vault dialogs for TUI."""

from __future__ import annotations

from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ...tui_icons import Icons
from ..types import MemoryNote


class MemoryNoteDialog(ModalScreen[Optional[str]]):
    """Dialog showing memory note content."""

    CSS = """
    MemoryNoteDialog {
        align: center middle;
    }

    MemoryNoteDialog #dialog {
        width: 90%;
        max-width: 120;
        height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    MemoryNoteDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }

    MemoryNoteDialog #note-meta {
        padding: 1 0;
        color: $text-muted;
    }

    MemoryNoteDialog #note-content {
        height: 1fr;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $primary;
    }

    MemoryNoteDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        padding: 1 0;
    }

    MemoryNoteDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("O", "open", "Open in Editor"),
        Binding("D", "delete", "Delete"),
    ]

    def __init__(self, note: MemoryNote, content: str):
        """Initialize memory note dialog.

        Args:
            note: The memory note metadata
            content: The note content
        """
        super().__init__()
        self.note = note
        self.content = content

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        # Type icons
        type_icons = {
            "knowledge": "📚",
            "projects": "📁",
            "sessions": "📅",
            "fixes": "🔧",
        }
        icon = type_icons.get(self.note.note_type, "📄")

        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{icon} [bold]{self.note.title}[/bold]",
                    id="dialog-title",
                )

                # Metadata
                tags_text = ", ".join(self.note.tags) if self.note.tags else "none"
                yield Static(
                    f"[dim]Type:[/dim] {self.note.note_type}  "
                    f"[dim]Tags:[/dim] {tags_text}  "
                    f"[dim]Modified:[/dim] {self.note.modified.strftime('%Y-%m-%d %H:%M')}",
                    id="note-meta",
                )

                with VerticalScroll(id="note-content"):
                    # Render content (escape Rich markup)
                    escaped_content = self.content.replace("[", "\\[").replace("]", "\\]")
                    yield Static(escaped_content)

                yield Static(
                    "[dim][O] Open in Editor • [D] Delete • [esc] Close[/dim]",
                    id="dialog-hint",
                )

                with Horizontal(id="dialog-buttons"):
                    yield Button("Open", variant="primary", id="open")
                    yield Button("Delete", variant="error", id="delete")
                    yield Button("Close", variant="default", id="close")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss(None)

    def action_open(self) -> None:
        """Request open action."""
        self.dismiss("open")

    def action_delete(self) -> None:
        """Request delete action."""
        self.dismiss("delete")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close":
            self.dismiss(None)
        elif event.button.id == "open":
            self.dismiss("open")
        elif event.button.id == "delete":
            self.dismiss("delete")
