"""Principles dialogs for TUI."""

from __future__ import annotations

from typing import Optional, TypedDict

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static, TextArea

from ...tui_icons import Icons


class PrincipleCreateData(TypedDict):
    name: str
    title: str
    content: str


class PrincipleCreateDialog(ModalScreen[Optional[PrincipleCreateData]]):
    """Dialog for creating a new principle snippet."""

    CSS = """
    PrincipleCreateDialog {
        align: center middle;
    }

    PrincipleCreateDialog #dialog {
        width: 80%;
        max-width: 100;
        height: auto;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    PrincipleCreateDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    PrincipleCreateDialog #dialog-hint {
        color: $text-muted;
        padding-bottom: 1;
    }

    PrincipleCreateDialog Input {
        margin-bottom: 1;
    }

    PrincipleCreateDialog TextArea {
        height: 10;
        margin-bottom: 1;
    }

    PrincipleCreateDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }

    PrincipleCreateDialog #dialog-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("ctrl+s", "submit", "Save"),
    ]

    def __init__(self, title: str = "New Principle"):
        super().__init__()
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.DOC} [bold]{self.dialog_title}[/bold]",
                    id="dialog-title",
                )
                yield Static(
                    "[dim]Create a principle snippet to guide Claude's behavior[/dim]",
                    id="dialog-hint",
                )
                yield Input(
                    placeholder="Filename (e.g., code-quality)",
                    id="principle-name",
                )
                yield Input(
                    placeholder="Title (e.g., Code Quality Standards)",
                    id="principle-title",
                )
                yield TextArea(
                    id="principle-content",
                )
                yield Static(
                    "[dim]Write the principle content above. "
                    "Markdown formatting is supported.[/dim]",
                    id="content-hint",
                )
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def on_mount(self) -> None:
        """Focus the name input on mount."""
        self.query_one("#principle-name", Input).focus()

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
        name = self.query_one("#principle-name", Input).value.strip()
        title = self.query_one("#principle-title", Input).value.strip()
        content = self.query_one("#principle-content", TextArea).text.strip()

        if not name:
            self.dismiss(None)
            return

        # Sanitize filename
        name = name.lower().replace(" ", "-")
        if name.endswith(".md"):
            name = name[:-3]

        self.dismiss(
            {
                "name": name,
                "title": title,
                "content": content,
            }
        )
