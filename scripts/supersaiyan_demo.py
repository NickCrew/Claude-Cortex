#!/usr/bin/env python3
"""Super Saiyan TUI Demo for cortex.

This demo showcases the enhanced TUI components with Super Saiyan styling.

Run with:
    python examples/supersaiyan_demo.py
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.binding import Binding

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_ctx_py.tui_supersaiyan import (
    SuperSaiyanCard,
    SuperSaiyanTable,
    SuperSaiyanButton,
    SuperSaiyanStatusBar,
    SuperSaiyanPanel,
    generate_sparkline,
)


class SuperSaiyanDemo(App):
    """Demo application showcasing Super Saiyan TUI components."""

    CSS = """
    Screen {
        background: #0a0e27;
    }

    Header {
        background: #3b82f6;
        color: white;
        text-style: bold;
    }

    .dashboard {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
        height: auto;
    }

    .content {
        padding: 1;
    }

    .button-group {
        layout: horizontal;
        height: auto;
        padding: 1;
    }

    Footer {
        background: #1a1f3a;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
    ]

    TITLE = "Super Saiyan Demo 🔥"

    def compose(self) -> ComposeResult:
        """Compose the demo UI."""
        yield Header(show_clock=True)

        # Dashboard cards with metrics
        with Container(classes="dashboard"):
            # Sample sparkline data
            data1 = [1, 2, 3, 5, 6, 8]
            data2 = [3, 4, 5, 6, 7, 8]
            data3 = [5, 6, 7, 8, 8, 8]

            yield SuperSaiyanCard(
                "Active Agents",
                "12",
                trend="+3",
                sparkline=generate_sparkline(data1),
            )
            yield SuperSaiyanCard(
                "Tasks Complete",
                "847",
                trend="+124",
                sparkline=generate_sparkline(data2),
            )
            yield SuperSaiyanCard(
                "Success Rate",
                "94%",
                trend="+2%",
                sparkline=generate_sparkline(data3),
            )

        # Content panel with table
        with SuperSaiyanPanel(classes="content"):
            table = SuperSaiyanTable()
            table.add_columns("Agent", "Status", "Progress", "Duration")

            # Add sample data
            table.add_status_row("code-reviewer", "active", 80, "2.5s")
            table.add_status_row("test-automator", "complete", 100, "3.2s")
            table.add_status_row("api-documenter", "running", 50, "1.8s")
            table.add_status_row("quality-engineer", "pending", 0, "0.0s")

            yield table

        # Action buttons
        with Container(classes="button-group"):
            yield SuperSaiyanButton("Activate Agent", classes="primary")
            yield SuperSaiyanButton("View Graph", variant="default")
            yield SuperSaiyanButton("Export", classes="success")
            yield SuperSaiyanButton("Deactivate", classes="danger")

        # Status bar
        status_bar = SuperSaiyanStatusBar()
        status_bar.agent_count = 12
        status_bar.active_tasks = 3
        status_bar.memory_usage = "45MB"
        yield status_bar

        yield Footer()

    def action_refresh(self) -> None:
        """Refresh action."""
        self.notify("Refreshing data...", severity="information", timeout=2)

    def action_help(self) -> None:
        """Show help."""
        self.notify(
            "Super Saiyan Demo - Press Q to quit, R to refresh",
            severity="information",
            timeout=3,
        )


def main():
    """Run the demo application."""
    app = SuperSaiyanDemo()
    app.run()


if __name__ == "__main__":
    main()
