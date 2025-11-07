"""Dashboard cards and sparkline visualizations for TUI."""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .tui_icons import Icons
from .tui_format import Format
from rich.text import Text


class Sparkline:
    """ASCII sparkline generator for mini graphs."""

    # Unicode block characters for sparklines
    BLOCKS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']

    @staticmethod
    def generate(data: List[float], width: int = 20, min_val: Optional[float] = None, max_val: Optional[float] = None) -> str:
        """Generate a sparkline from data points.

        Args:
            data: List of numeric values
            width: Width of the sparkline in characters
            min_val: Minimum value for scaling (auto-detect if None)
            max_val: Maximum value for scaling (auto-detect if None)

        Returns:
            Formatted sparkline string
        """
        if not data:
            return "▁" * width

        # Auto-detect min/max if not provided
        if min_val is None:
            min_val = min(data)
        if max_val is None:
            max_val = max(data)

        # Handle edge case where all values are the same
        if min_val == max_val:
            return Sparkline.BLOCKS[3] * width

        # Sample data to fit width
        if len(data) > width:
            step = len(data) / width
            sampled = [data[int(i * step)] for i in range(width)]
        else:
            sampled = data + [data[-1]] * (width - len(data))  # Pad if needed

        # Generate sparkline
        sparkline = []
        for value in sampled:
            # Normalize to 0-1 range
            normalized = (value - min_val) / (max_val - min_val)
            # Map to block character index
            block_idx = min(int(normalized * len(Sparkline.BLOCKS)), len(Sparkline.BLOCKS) - 1)
            sparkline.append(Sparkline.BLOCKS[block_idx])

        return ''.join(sparkline)

    @staticmethod
    def generate_with_trend(data: List[float], width: int = 20) -> str:
        """Generate sparkline with trend indicator and color.

        Args:
            data: List of numeric values
            width: Width of the sparkline

        Returns:
            Colored sparkline with trend indicator
        """
        if len(data) < 2:
            return f"[dim]{Sparkline.generate(data, width)}[/dim]"

        # Calculate trend
        recent_avg = sum(data[-3:]) / min(3, len(data))
        older_avg = sum(data[:3]) / min(3, len(data))
        trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0

        # Choose color based on trend
        if trend_pct > 5:
            color = "green"
            trend_icon = Icons.ARROW_UP
        elif trend_pct < -5:
            color = "red"
            trend_icon = Icons.ARROW_DOWN
        else:
            color = "yellow"
            trend_icon = "→"

        sparkline = Sparkline.generate(data, width)
        return f"[{color}]{trend_icon} {sparkline}[/{color}]"


class DashboardCard:
    """Dashboard card component for displaying stats with visual flair."""

    @staticmethod
    def create(
        title: str,
        value: str,
        subtitle: str = "",
        trend: Optional[float] = None,
        sparkline_data: Optional[List[float]] = None,
        icon: str = Icons.INFO,
        width: int = 30
    ) -> List[str]:
        """Create a dashboard card with stats and optional sparkline.

        Args:
            title: Card title
            value: Main value to display
            subtitle: Optional subtitle
            trend: Optional trend percentage
            sparkline_data: Optional data for sparkline
            icon: Icon to display
            width: Card width in characters

        Returns:
            List of formatted card lines
        """
        lines = []

        # Top border
        lines.append(f"╭{'─' * (width - 2)}╮")

        # Title row with icon
        title_text = f"{icon} {title}"
        padding = width - len(title_text) - 3
        lines.append(f"│ [bold]{title_text}[/bold]{' ' * padding}│")

        # Divider
        lines.append(f"├{'─' * (width - 2)}┤")

        # Value row
        value_padding = width - len(value) - 3
        lines.append(f"│ [cyan bold]{value}[/cyan bold]{' ' * value_padding}│")

        # Trend row (if provided)
        if trend is not None:
            if trend > 0:
                trend_text = f"[green]{Icons.ARROW_UP} +{trend:.1f}%[/green]"
            elif trend < 0:
                trend_text = f"[red]{Icons.ARROW_DOWN} {trend:.1f}%[/red]"
            else:
                trend_text = f"[dim]→ 0.0%[/dim]"

            # Calculate actual display length (without markup)
            clean_trend = f"+{trend:.1f}%" if trend > 0 else f"{trend:.1f}%"
            trend_padding = width - len(clean_trend) - 5
            lines.append(f"│ {trend_text}{' ' * trend_padding}│")

        # Subtitle row (if provided)
        if subtitle:
            sub_text = subtitle[:width - 4]
            sub_padding = width - len(sub_text) - 3
            lines.append(f"│ [dim]{sub_text}[/dim]{' ' * sub_padding}│")

        # Sparkline row (if provided)
        if sparkline_data:
            spark = Sparkline.generate(sparkline_data, width - 4)
            lines.append(f"│ {spark} │")

        # Bottom border
        lines.append(f"╰{'─' * (width - 2)}╯")

        return lines

    @staticmethod
    def create_compact(
        title: str,
        value: str,
        icon: str = Icons.INFO,
        color: str = "cyan"
    ) -> str:
        """Create a compact single-line dashboard card.

        Args:
            title: Card title
            value: Value to display
            icon: Icon
            color: Value color

        Returns:
            Formatted card string
        """
        return f"{icon} [bold]{title}[/bold] [{color}]{value}[/{color}]"


class DashboardGrid:
    """Layout manager for dashboard cards in a grid."""

    @staticmethod
    def _line_display_width(line: str) -> int:
        """Measure printable cell width of a markup line."""
        return Text.from_markup(line).cell_len

    @staticmethod
    def _card_width(card: List[str]) -> int:
        """Compute max printable width for a card."""
        if not card:
            return 0
        return max(DashboardGrid._line_display_width(line) for line in card)

    @staticmethod
    def _pad_line(line: str, width_diff: int) -> str:
        """Pad a single line to match width without breaking borders."""
        if width_diff <= 0:
            return line
        if line.endswith('│'):
            return f"{line[:-1]}{' ' * width_diff}│"
        return f"{line}{' ' * width_diff}"

    @staticmethod
    def create_row(cards: List[List[str]], spacing: int = 4) -> List[str]:
        """Create a horizontal row of cards.

        Args:
            cards: List of card line lists
            spacing: Spacing between cards

        Returns:
            List of combined lines
        """
        if not cards:
            return []

        # Find max height and width
        max_height = max(len(card) for card in cards)
        max_width = max(DashboardGrid._card_width(card) for card in cards)

        # Pad shorter cards and ensure equal width
        padded_cards = []
        for card in cards:
            if not card:
                continue

            new_card = []
            for line in card:
                line_width = DashboardGrid._line_display_width(line)
                width_diff = max(0, max_width - line_width)
                new_card.append(DashboardGrid._pad_line(line, width_diff))

            if len(new_card) < max_height:
                padding_lines = [' ' * max_width] * (max_height - len(new_card))
                new_card.extend(padding_lines)

            padded_cards.append(new_card)

        # Combine horizontally
        combined = []
        for row_idx in range(max_height):
            row_parts = []
            for card in padded_cards:
                if row_idx < len(card):
                    row_parts.append(card[row_idx])
                else:
                    row_parts.append(' ' * len(card[0]))

            combined.append((' ' * spacing).join(row_parts))

        return combined


class MetricsCollector:
    """Collects and tracks metrics over time for dashboard display."""

    def __init__(self, max_history: int = 50):
        """Initialize metrics collector.

        Args:
            max_history: Maximum number of data points to keep
        """
        self.max_history = max_history
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}

    def record(self, metric_name: str, value: float) -> None:
        """Record a metric value.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []

        self.metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.now()
        })

        # Trim to max history
        if len(self.metrics[metric_name]) > self.max_history:
            self.metrics[metric_name] = self.metrics[metric_name][-self.max_history:]

    def get_values(self, metric_name: str, count: Optional[int] = None) -> List[float]:
        """Get metric values.

        Args:
            metric_name: Name of the metric
            count: Number of recent values (None = all)

        Returns:
            List of metric values
        """
        if metric_name not in self.metrics:
            return []

        values = [m['value'] for m in self.metrics[metric_name]]

        if count is not None:
            return values[-count:]

        return values

    def get_trend(self, metric_name: str, window: int = 5) -> float:
        """Calculate trend percentage for a metric.

        Args:
            metric_name: Name of the metric
            window: Number of recent points to compare

        Returns:
            Trend percentage
        """
        values = self.get_values(metric_name)

        if len(values) < window * 2:
            return 0.0

        recent = sum(values[-window:]) / window
        older = sum(values[-window * 2:-window]) / window

        if older == 0:
            return 0.0

        return ((recent - older) / older) * 100

    def get_current(self, metric_name: str) -> Optional[float]:
        """Get most recent metric value.

        Args:
            metric_name: Name of the metric

        Returns:
            Most recent value or None
        """
        values = self.get_values(metric_name)
        return values[-1] if values else None

    def clear(self, metric_name: Optional[str] = None) -> None:
        """Clear metrics.

        Args:
            metric_name: Specific metric to clear (None = all)
        """
        if metric_name is None:
            self.metrics.clear()
        elif metric_name in self.metrics:
            self.metrics[metric_name].clear()
