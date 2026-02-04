"""Codex skills management dialogs for TUI."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Static

from ...tui_icons import Icons


class BulkSkillOperationDialog(ModalScreen[Optional[Dict[str, List[str]]]]):
    """Dialog for bulk linking/unlinking skills by category."""

    CSS = """
    BulkSkillOperationDialog {
        align: center middle;
    }

    BulkSkillOperationDialog #dialog {
        width: 70;
        max-width: 90%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    BulkSkillOperationDialog #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    BulkSkillOperationDialog #category-list {
        height: auto;
        max-height: 40;
        padding: 1;
    }

    BulkSkillOperationDialog .category-row {
        padding: 0 0 1 0;
    }

    BulkSkillOperationDialog #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(
        self,
        categories: List[Tuple[str, str, int]],
        operation: Literal["link", "unlink"]
    ):
        """Initialize bulk operation dialog.

        Args:
            categories: List of (category_key, category_icon, skill_count) tuples
            operation: "link" or "unlink" operation type
        """
        super().__init__()
        self.categories = categories
        self.operation = operation
        self.selected: List[str] = []

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        operation_text = "Link" if self.operation == "link" else "Unlink"
        operation_verb = operation_text.lower()

        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{Icons.CODE} [bold]Bulk {operation_text} Skills[/bold]",
                    id="dialog-title",
                )

                yield Static(
                    f"[dim]Select categories to {operation_verb} all skills:[/dim]"
                )

                with VerticalScroll(id="category-list"):
                    for category_key, icon, count in self.categories:
                        yield Checkbox(
                            f"{icon} {category_key} ({count} skills)",
                            value=True,  # Pre-select all
                            id=f"bulk-{category_key}",
                            classes="category-row",
                        )

                yield Static(
                    f"[dim]Space to toggle • Enter to {operation_verb} • Esc to cancel[/dim]",
                    id="dialog-hint",
                )

                with Horizontal(id="dialog-buttons"):
                    yield Button(
                        f"{operation_text} Selected",
                        variant="primary",
                        id="confirm"
                    )
                    yield Button("Cancel", variant="default", id="cancel")

    def action_cancel(self) -> None:
        """Cancel the dialog."""
        self.dismiss(None)

    def action_confirm(self) -> None:
        """Confirm the operation."""
        selected: List[str] = []
        for category_key, _, _ in self.categories:
            try:
                checkbox = self.query_one(f"#bulk-{category_key}", Checkbox)
                if checkbox.value:
                    selected.append(category_key)
            except Exception:
                continue

        self.dismiss({self.operation: selected})

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "confirm":
            self.action_confirm()
        else:
            self.action_cancel()
