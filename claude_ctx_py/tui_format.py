"""Formatting utilities for better data display in TUI."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence, Union


class Format:
    """Formatting utilities for better data display."""

    @staticmethod
    def number(n: Union[int, float]) -> str:
        """Format numbers with thousands separators.

        Args:
            n: Number to format

        Returns:
            Formatted number string

        Examples:
            >>> Format.number(1000)
            '1,000'
            >>> Format.number(1234.56)
            '1,234.56'
        """
        if isinstance(n, float):
            return f"{n:,.2f}"
        return f"{n:,}"

    @staticmethod
    def bytes(size: int) -> str:
        """Human-readable byte sizes.

        Args:
            size: Size in bytes

        Returns:
            Human-readable size string

        Examples:
            >>> Format.bytes(1024)
            '1.0KB'
            >>> Format.bytes(1048576)
            '1.0MB'
        """
        size_value = float(size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_value < 1024.0:
                return f"{size_value:.1f}{unit}"
            size_value /= 1024.0
        return f"{size_value:.1f}PB"

    @staticmethod
    def percent(value: float, total: float) -> str:
        """Format percentage with color coding.

        Args:
            value: Current value
            total: Total value

        Returns:
            Colored percentage string

        Examples:
            >>> Format.percent(90, 100)
            '[green]90%[/green]'
            >>> Format.percent(50, 100)
            '[red]50%[/red]'
        """
        if total == 0:
            return "0%"

        pct = (value / total) * 100

        if pct >= 90:
            color = "green"
        elif pct >= 70:
            color = "yellow"
        else:
            color = "red"

        return f"[{color}]{pct:.0f}%[/{color}]"

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Relative time formatting (e.g., '2m ago', '3h ago').

        Args:
            dt: Datetime to format

        Returns:
            Relative time string

        Examples:
            >>> Format.time_ago(datetime.now() - timedelta(minutes=5))
            '5m ago'
        """
        now = datetime.now()
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"{weeks}w ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"

    @staticmethod
    def duration(seconds: float) -> str:
        """Format duration (e.g., '2m 30s', '1h 5m').

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string

        Examples:
            >>> Format.duration(90)
            '1m 30s'
            >>> Format.duration(3665)
            '1h 1m'
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s" if secs > 0 else f"{mins}m"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text with ellipsis.

        Args:
            text: Text to truncate
            max_length: Maximum length including suffix
            suffix: Suffix to append if truncated

        Returns:
            Truncated text

        Examples:
            >>> Format.truncate("Hello World", 8)
            'Hello...'
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def list_items(items: Sequence[object], max_items: int = 3) -> str:
        """Format list with overflow indicator.

        Args:
            items: List of items to format
            max_items: Maximum items to show before overflow

        Returns:
            Formatted list string

        Examples:
            >>> Format.list_items(['a', 'b', 'c', 'd'], 2)
            'a, b [dim]+2 more[/dim]'
        """
        if len(items) <= max_items:
            return ", ".join(str(item) for item in items)

        shown = items[:max_items]
        remaining = len(items) - max_items
        return f"{', '.join(str(item) for item in shown)} [dim]+{remaining} more[/dim]"
