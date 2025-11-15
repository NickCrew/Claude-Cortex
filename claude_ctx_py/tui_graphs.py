"""Graph and timeline visualizations for TUI."""

from __future__ import annotations

from typing import Dict, List, Any
from .tui_icons import Icons


class DependencyGraph:
    """Visualize dependencies as a tree structure."""

    @staticmethod
    def create_tree_lines(
        root_name: str, dependencies: Dict[str, Any], max_depth: int = 3
    ) -> List[str]:
        """Create dependency tree visualization as text lines.

        Args:
            root_name: Name of the root node
            dependencies: Dictionary of dependencies
            max_depth: Maximum depth to traverse

        Returns:
            List of formatted tree lines
        """
        lines = [f"[bold cyan]{Icons.FOLDER} {root_name}[/bold cyan]"]
        DependencyGraph._add_dependency_lines(
            lines, dependencies, level=1, max_depth=max_depth
        )
        return lines

    @staticmethod
    def _add_dependency_lines(
        lines: List[str],
        deps: Dict[str, Any],
        level: int = 0,
        max_depth: int = 3,
        prefix: str = "",
    ) -> None:
        """Recursively add dependencies to the line list.

        Args:
            lines: List to append lines to
            deps: Dictionary of dependencies
            level: Current nesting level
            max_depth: Maximum depth to traverse
            prefix: Current line prefix for tree structure
        """
        if level >= max_depth or not deps:
            return

        items = list(deps.items())
        for idx, (name, children) in enumerate(items):
            is_last = idx == len(items) - 1

            # Tree connector
            connector = Icons.LAST_BRANCH if is_last else Icons.BRANCH

            # Icon based on type
            icon = Icons.FOLDER if children else Icons.FILE

            # Color based on level
            colors = ["cyan", "magenta", "green", "yellow", "blue"]
            color = colors[level % len(colors)]

            # Build line
            line = f"{prefix}{connector} [{color}]{icon} {name}[/{color}]"
            lines.append(line)

            # Recurse for children
            if children:
                new_prefix = prefix + (Icons.SPACE if is_last else f"{Icons.PIPE} ")
                DependencyGraph._add_dependency_lines(
                    lines, children, level + 1, max_depth, new_prefix
                )


class WorkflowTimeline:
    """Visual timeline for workflow execution."""

    @staticmethod
    def create_timeline(steps: List[Dict[str, Any]]) -> str:
        """Create a horizontal timeline with status indicators.

        Args:
            steps: List of step dictionaries with 'name' and 'status' keys

        Returns:
            Formatted timeline string
        """
        timeline_parts = []

        for idx, step in enumerate(steps):
            name = step.get("name", f"Step {idx + 1}")
            status = step.get("status", "pending")

            # Determine icon and color based on status
            if status == "completed":
                icon = f"[green]{Icons.SUCCESS}[/green]"
                name_style = f"[green]{name}[/green]"
            elif status == "running":
                icon = f"[yellow]{Icons.RUNNING}[/yellow]"
                name_style = f"[yellow]{name}[/yellow]"
            elif status == "error":
                icon = f"[red]{Icons.ERROR}[/red]"
                name_style = f"[red]{name}[/red]"
            else:
                icon = f"[dim]{Icons.READY}[/dim]"
                name_style = f"[dim]{name}[/dim]"

            # Build step display
            step_text = f"{icon} {name_style}"

            # Add connector arrow if not last step
            if idx < len(steps) - 1:
                step_text += f" [dim]{Icons.ARROW_RIGHT}[/dim]"

            timeline_parts.append(step_text)

        return " ".join(timeline_parts)

    @staticmethod
    def create_vertical_timeline(steps: List[Dict[str, Any]]) -> List[str]:
        """Create a vertical timeline suitable for narrow displays.

        Args:
            steps: List of step dictionaries with 'name' and 'status' keys

        Returns:
            List of formatted timeline lines
        """
        lines = []

        for idx, step in enumerate(steps):
            name = step.get("name", f"Step {idx + 1}")
            status = step.get("status", "pending")
            duration = step.get("duration", "")

            # Determine icon and color based on status
            if status == "completed":
                icon = f"[green]{Icons.SUCCESS}[/green]"
                name_style = f"[green]{name}[/green]"
            elif status == "running":
                icon = f"[yellow]{Icons.RUNNING}[/yellow]"
                name_style = f"[yellow bold]{name}[/yellow bold]"
            elif status == "error":
                icon = f"[red]{Icons.ERROR}[/red]"
                name_style = f"[red]{name}[/red]"
            else:
                icon = f"[dim]{Icons.READY}[/dim]"
                name_style = f"[dim]{name}[/dim]"

            # Build step line
            line = f"{icon} {name_style}"
            if duration:
                line += f" [dim]({duration})[/dim]"

            lines.append(line)

            # Add connector to next step if not last
            if idx < len(steps) - 1:
                lines.append(f"[dim]{Icons.PIPE}[/dim]")

        return lines


class StatsDisplay:
    """Display statistics in various formats."""

    @staticmethod
    def create_stats_bar(stats: Dict[str, Any]) -> str:
        """Create a horizontal stats bar with icons.

        Args:
            stats: Dictionary of statistics to display

        Returns:
            Formatted stats bar string
        """
        parts = []

        # Common stat types with icons
        if "total" in stats and stats["total"]:
            parts.append(f"[cyan]{stats['total']} total[/cyan]")

        if "active" in stats and stats["active"]:
            parts.append(f"[green]{Icons.SUCCESS} {stats['active']} active[/green]")

        if "pending" in stats and stats["pending"]:
            parts.append(f"[yellow]{Icons.READY} {stats['pending']} pending[/yellow]")

        if "errors" in stats and stats["errors"]:
            parts.append(f"[red]{Icons.ERROR} {stats['errors']} errors[/red]")

        if "warnings" in stats and stats["warnings"]:
            parts.append(
                f"[yellow]{Icons.WARNING} {stats['warnings']} warnings[/yellow]"
            )

        return (
            " [dim]│[/dim] ".join(parts) if parts else "[dim]No stats available[/dim]"
        )

    @staticmethod
    def create_key_value_grid(data: Dict[str, str], columns: int = 2) -> List[str]:
        """Create a grid layout of key-value pairs.

        Args:
            data: Dictionary of key-value pairs
            columns: Number of columns in the grid

        Returns:
            List of formatted grid lines
        """
        lines = []
        items = list(data.items())

        for i in range(0, len(items), columns):
            row_items = items[i : i + columns]
            row_parts = []

            for key, value in row_items:
                row_parts.append(f"[dim]{key}:[/dim] [cyan]{value}[/cyan]")

            lines.append(" [dim]│[/dim] ".join(row_parts))

        return lines
