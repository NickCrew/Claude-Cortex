"""Super Saiyan enhanced TUI components for cortex.

This module provides visually enhanced Textual widgets following Super Saiyan
design principles: accessibility first, performance always, delight users.
"""

from __future__ import annotations

from typing import Any

from textual.widgets import Static, DataTable, Button
from textual.containers import Container
from textual.reactive import reactive
from rich.panel import Panel
from rich.text import Text
from rich.table import Table as RichTable


class SuperSaiyanCard(Static):
    """Beautiful metric card with smooth animations and rich styling.

    Features:
    - Smooth fade-in animation on mount
    - Hover effects with color transitions
    - Gradient-style borders
    - Rich typography
    """

    DEFAULT_CSS = """
    SuperSaiyanCard {
        height: auto;
        border: tall $primary;
        background: $surface-lighten-1;
        padding: 1 2;
        opacity: 0;
        transition: opacity 300ms, border 200ms, background 200ms;
    }

    SuperSaiyanCard.mounted {
        opacity: 1;
    }

    SuperSaiyanCard:hover {
        border: tall $accent;
        background: $surface-lighten-2;
    }

    SuperSaiyanCard > .card-title {
        color: $accent;
        text-style: bold;
    }

    SuperSaiyanCard > .card-value {
        color: $text;
        text-style: bold;
        content-align: center middle;
    }

    SuperSaiyanCard > .card-trend {
        color: $success;
        text-style: italic;
    }
    """

    def __init__(
        self,
        title: str,
        value: str,
        trend: str | None = None,
        sparkline: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Super Saiyan card.

        Args:
            title: Card title
            value: Main value to display
            trend: Optional trend indicator (e.g., "+23%")
            sparkline: Optional sparkline (e.g., "▁▂▃▅▆█")
            **kwargs: Additional widget arguments
        """
        content = Text()
        content.append(f"{title}\n", style="dim cyan")
        content.append(f"{value}\n", style="bold white")

        if trend:
            style = "green" if "+" in trend else "red" if "-" in trend else "yellow"
            content.append(f"{trend} ", style=style)

        if sparkline:
            content.append(sparkline, style="bright_blue")

        panel = Panel(
            content,
            border_style="bright_blue",
            padding=(1, 2),
        )

        super().__init__(panel, **kwargs)

    def on_mount(self) -> None:
        """Trigger fade-in animation on mount."""
        self.add_class("mounted")


class SuperSaiyanTable(DataTable[Any]):
    """Enhanced DataTable with Super Saiyan styling.

    Features:
    - Color-coded status indicators
    - Smooth row highlighting
    - Progress bar visualization
    - Rich cell formatting
    """

    DEFAULT_CSS = """
    SuperSaiyanTable {
        border: solid $primary;
        background: $surface;
    }

    SuperSaiyanTable > .datatable--header {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    SuperSaiyanTable > .datatable--cursor {
        background: $accent 20%;
        color: $text;
    }

    SuperSaiyanTable:focus > .datatable--cursor {
        background: $accent 40%;
    }
    """

    def add_status_row(
        self,
        name: str,
        status: str,
        progress: int,
        duration: str,
    ) -> None:
        """Add a row with formatted status indicators.

        Args:
            name: Item name
            status: Status text ("active", "running", "complete", "error")
            progress: Progress percentage (0-100)
            duration: Duration string
        """
        # Status indicator with color
        status_map = {
            "active": "[green]●[/green] Active",
            "running": "[yellow]●[/yellow] Running",
            "complete": "[green]✓[/green] Complete",
            "error": "[red]✗[/red] Error",
            "pending": "[dim]○[/dim] Pending",
        }
        status_formatted = status_map.get(status.lower(), status)

        # Progress bar visualization
        filled = int(progress / 10)
        empty = 10 - filled
        progress_bar = f"[cyan]{'█' * filled}{'░' * empty}[/cyan] {progress}%"

        self.add_row(name, status_formatted, progress_bar, duration)


class SuperSaiyanButton(Button):
    """Enhanced button with Super Saiyan styling.

    Features:
    - Smooth hover effects
    - Press animations
    - Keyboard focus indicators
    - Rich variants (primary, success, danger)
    """

    DEFAULT_CSS = """
    SuperSaiyanButton {
        margin: 1;
        padding: 0 2;
        min-width: 16;
        transition: background 150ms, text-style 150ms;
    }

    SuperSaiyanButton.primary {
        background: $primary;
        color: $text;
        border: solid $primary;
    }

    SuperSaiyanButton.primary:hover {
        background: $primary-lighten-1;
        text-style: bold;
    }

    SuperSaiyanButton.success {
        background: $success;
        color: $text;
        border: solid $success;
    }

    SuperSaiyanButton.success:hover {
        background: $success-lighten-1;
        text-style: bold;
    }

    SuperSaiyanButton.danger {
        background: $error;
        color: $text;
        border: solid $error;
    }

    SuperSaiyanButton.danger:hover {
        background: $error-lighten-1;
        text-style: bold;
    }

    SuperSaiyanButton:focus {
        border: tall $accent;
        text-style: bold;
    }
    """


class SuperSaiyanStatusBar(Static):
    """Live-updating status bar with neon waveform feedback."""

    view = reactive("Agents")
    message = reactive("Initializing...")
    perf = reactive("")
    agent_active = reactive(0)
    agent_total = reactive(0)
    task_active = reactive(0)
    token_count = reactive("")
    wave_phase = reactive(0)

    _WAVE_FRAMES = (
        "≈~~~~",
        "~≈~~~",
        "~~≈~~",
        "~~~≈~",
        "~~≈~~",
        "~≈~~~",
    )

    DEFAULT_CSS = """
    SuperSaiyanStatusBar {
        height: 1;
        background: $surface-lighten-1;
        color: $text;
        padding: 0 2;
        border-top: tall $primary;
    }
    """

    def update_payload(
        self,
        *,
        view: str,
        message: str,
        perf: str,
        agent_active: int,
        agent_total: int,
        task_active: int,
        token_count: str = "",
    ) -> None:
        """Push new info into the status bar."""
        self.view = view
        self.message = message
        self.perf = perf
        self.agent_active = agent_active
        self.agent_total = agent_total
        self.task_active = task_active
        self.token_count = token_count
        self.wave_phase = (self.wave_phase + 1) % len(self._WAVE_FRAMES)

    def render(self) -> str:
        """Render status bar with live data."""
        agent_text = (
            f"[cyan]{self.agent_active}/{self.agent_total} agents"
            if self.agent_total
            else "[cyan]0 agents"
        )
        task_text = f"[green]{self.task_active} active tasks"
        token_text = f"[yellow]{self.token_count}[/yellow]" if self.token_count else ""
        wave = self._WAVE_FRAMES[self.wave_phase]

        parts = [f"[bold]{self.view}[/bold] {self.message}"]
        parts.append(agent_text)
        parts.append(task_text)
        if token_text:
            parts.append(token_text)
        if self.perf:
            parts.append(self.perf)
        parts.append(f"[magenta]{wave}[/magenta]")

        return " [dim]│[/dim] ".join(parts)

    def watch_view(self, _value: str) -> None:  # pragma: no cover - trivial
        self.refresh()

    watch_message = watch_view
    watch_perf = watch_view
    watch_agent_active = watch_view
    watch_agent_total = watch_view
    watch_task_active = watch_view
    watch_token_count = watch_view
    watch_wave_phase = watch_view


class SuperSaiyanPanel(Container):
    """Container with smooth entrance animation.

    Features:
    - Fade-in on mount
    - Slide-in effect
    - Hover effects
    - Smooth transitions
    """

    DEFAULT_CSS = """
    SuperSaiyanPanel {
        border: solid $primary;
        background: $surface-lighten-1;
        padding: 1;
        opacity: 0;
        offset-y: 5;
    }

    SuperSaiyanPanel.visible {
        opacity: 1;
        offset-y: 0;
        transition: opacity 300ms, offset-y 300ms;
    }

    SuperSaiyanPanel:hover {
        border: solid $accent;
    }
    """

    def on_mount(self) -> None:
        """Trigger entrance animation."""
        self.add_class("visible")


def generate_sparkline(data: list[float]) -> str:
    """Generate ASCII sparkline from data points.

    Args:
        data: List of numeric values

    Returns:
        Sparkline string using block characters
    """
    if not data:
        return ""

    chars = "▁▂▃▄▅▆▇█"
    min_val, max_val = min(data), max(data)
    range_val = max_val - min_val or 1

    return "".join(
        chars[int((v - min_val) / range_val * (len(chars) - 1))] for v in data
    )


def create_rich_table(
    title: str,
    columns: list[tuple[str, str]],
    rows: list[list[str]],
    border_style: str = "bright_blue",
) -> RichTable:
    """Create a Rich table with Super Saiyan styling.

    Args:
        title: Table title
        columns: List of (name, style) tuples
        rows: List of row data
        border_style: Border color style

    Returns:
        Styled Rich table
    """
    table = RichTable(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style=border_style,
        title_style="bold cyan",
        padding=(0, 1),
    )

    for name, style in columns:
        table.add_column(name, style=style)

    for row in rows:
        table.add_row(*row)

    return table


# Color palette for Super Saiyan TUI
SUPER_SAIYAN_THEME = {
    "primary": "#3b82f6",  # Blue
    "secondary": "#8b5cf6",  # Purple
    "accent": "#06b6d4",  # Cyan
    "success": "#10b981",  # Green
    "warning": "#f59e0b",  # Yellow
    "error": "#ef4444",  # Red
    "info": "#3b82f6",  # Blue
    "surface": "#0a0e27",  # Dark blue-gray
    "surface-lighten-1": "#1a1f3a",
    "surface-lighten-2": "#242945",
    "text": "#ffffff",  # White
    "text-muted": "#9ca3af",  # Gray
}
