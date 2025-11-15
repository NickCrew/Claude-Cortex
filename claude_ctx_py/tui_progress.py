"""Progress bar utilities for visual progress display in TUI."""

from __future__ import annotations

from typing import Sequence


class ProgressBar:
    """Enhanced progress bar with color gradients."""

    @staticmethod
    def simple_bar(value: float, total: float, width: int = 20) -> str:
        """Simple inline progress bar with gradient colors.

        Args:
            value: Current value
            total: Total value
            width: Width of the progress bar in characters

        Returns:
            Formatted progress bar string with percentage

        Examples:
            >>> ProgressBar.simple_bar(50, 100, 20)
            '[yellow]██████████[/yellow][dim]░░░░░░░░░░[/dim] 50%'
        """
        if total == 0:
            return f"[dim]{'░' * width}[/dim] 0%"

        pct = value / total
        filled = int(pct * width)
        empty = width - filled

        # Color gradient based on percentage
        if pct >= 0.9:
            color = "green"
        elif pct >= 0.7:
            color = "yellow"
        elif pct >= 0.5:
            color = "blue"
        else:
            color = "red"

        bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
        return f"{bar} {pct * 100:.0f}%"

    @staticmethod
    def compact_bar(value: float, total: float, width: int = 10) -> str:
        """Compact progress bar without percentage text.

        Args:
            value: Current value
            total: Total value
            width: Width of the progress bar in characters

        Returns:
            Formatted progress bar string

        Examples:
            >>> ProgressBar.compact_bar(75, 100, 10)
            '[green]███████[/green][dim]░░░[/dim]'
        """
        if total == 0:
            return f"[dim]{'░' * width}[/dim]"

        pct = value / total
        filled = int(pct * width)
        empty = width - filled

        # Color gradient based on percentage
        if pct >= 0.9:
            color = "green"
        elif pct >= 0.7:
            color = "yellow"
        elif pct >= 0.5:
            color = "blue"
        else:
            color = "red"

        return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"

    @staticmethod
    def status_bar(steps: Sequence[str], current_step: int) -> str:
        """Step-based progress indicator.

        Args:
            steps: List of step names
            current_step: Index of current step (0-based)

        Returns:
            Visual step indicator

        Examples:
            >>> ProgressBar.status_bar(['Init', 'Process', 'Complete'], 1)
            '[green]✓[/green] → [yellow]▶[/yellow] → [dim]○[/dim]'
        """
        from .tui_icons import Icons

        parts = []
        for idx, step in enumerate(steps):
            if idx < current_step:
                # Completed
                parts.append(f"[green]{Icons.SUCCESS}[/green]")
            elif idx == current_step:
                # Current
                parts.append(f"[yellow]{Icons.SELECTED}[/yellow]")
            else:
                # Pending
                parts.append(f"[dim]{Icons.READY}[/dim]")

        return " → ".join(parts)
