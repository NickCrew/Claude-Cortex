"""Memory vault dialogs for TUI."""

from __future__ import annotations

from typing import Optional, TypedDict

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ...tui_icons import Icons
from ..types import MemoryNote


class MemoryNoteCreateData(TypedDict):
    note_type: str
    title: str
    summary: str


class MemoryNoteCreateDialog(ModalScreen[Optional[MemoryNoteCreateData]]):
    """Dialog for creating a new memory note."""

    CSS = """
    MemoryNoteCreateDialog {
        align: center middle;
    }

    MemoryNoteCreateDialog #dialog {
        opacity: 1;
    }

    MemoryNoteCreateDialog #dialog-hint {
        color: $text-muted;
        padding-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    def __init__(self, title: str, *, default_type: str = "knowledge"):
        super().__init__()
        self.title = title
        self.default_type = default_type

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"🧠 [bold]{self.title}[/bold]", id="dialog-title"
                )
                yield Static(
                    "[dim]Types: knowledge, projects, sessions, fixes[/dim]",
                    id="dialog-hint",
                )
                yield Input(
                    value=self.default_type,
                    placeholder="Note type",
                    id="note-type",
                )
                yield Input(
                    placeholder="Title / topic",
                    id="note-title",
                )
                yield Input(
                    placeholder="Summary (optional)",
                    id="note-summary",
                )
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
        note_type = self.query_one("#note-type", Input).value.strip() or "knowledge"
        title = self.query_one("#note-title", Input).value.strip()
        summary = self.query_one("#note-summary", Input).value.strip()

        if not title:
            self.dismiss(None)
            return

        self.dismiss(
            {
                "note_type": note_type,
                "title": title,
                "summary": summary,
            }
        )


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
