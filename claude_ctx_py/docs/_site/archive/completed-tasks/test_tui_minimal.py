#!/usr/bin/env python3
"""Minimal test of TUI to debug issues."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container
from textual.binding import Binding
from textual.reactive import reactive


class MinimalTUI(App):
    """Minimal TUI to test basic functionality."""

    CSS = """
    Screen {
        background: $surface;
    }

    DataTable {
        height: 1fr;
    }

    #status-bar {
        height: 1;
        background: $boost;
        color: $text;
        padding: 0 1;
        border-top: solid $primary;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "test_status", "Test Status"),
    ]

    status_message: reactive[str] = reactive("Initial status message")

    def compose(self) -> ComposeResult:
        """Create widgets."""
        yield Header()
        yield Container(
            DataTable(id="main-table"),
            id="main-container"
        )
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Setup after mount."""
        # Add test data to table
        table = self.query_one(DataTable)
        table.add_column("Test Column")
        table.add_row("Test Row 1")
        table.add_row("Test Row 2")
        table.add_row("Test Row 3")

        # Update status bar
        self.update_status_bar()

    def watch_status_message(self, message: str) -> None:
        """Update status bar when message changes."""
        self.update_status_bar()

    def update_status_bar(self) -> None:
        """Update the status bar."""
        try:
            status_bar = self.query_one("#status-bar", Static)
            status_bar.update(f"Status: {self.status_message} | Memory: 25MB | CPU: 5%")
        except Exception as e:
            print(f"Error updating status bar: {e}")

    def action_test_status(self) -> None:
        """Test status bar update."""
        import random
        self.status_message = f"Updated at {random.randint(1, 100)}"


if __name__ == "__main__":
    app = MinimalTUI()
    app.run()
