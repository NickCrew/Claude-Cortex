"""Interactive workflow visualizer with timeline and dependency graph."""

from __future__ import annotations

from typing import Any, List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from .tui_icons import Icons
from .tui_format import Format
from .tui_progress import ProgressBar


class WorkflowNode:
    """Represents a node in the workflow graph."""

    def __init__(
        self,
        node_id: str,
        name: str,
        status: str = "pending",
        dependencies: Optional[List[str]] = None,
    ):
        """Initialize workflow node.

        Args:
            node_id: Unique node identifier
            name: Human-readable name
            status: Node status (pending, running, complete, error)
            dependencies: List of node IDs this depends on
        """
        self.node_id = node_id
        self.name = name
        self.status = status
        self.dependencies = dependencies or []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.progress: float = 0.0
        self.error_message: Optional[str] = None

    def get_duration(self) -> Optional[timedelta]:
        """Get node execution duration.

        Returns:
            Duration or None if not started/finished
        """
        if self.start_time is None:
            return None

        end = self.end_time or datetime.now()
        return end - self.start_time

    def get_status_icon(self) -> str:
        """Get colored status icon.

        Returns:
            Formatted status icon
        """
        if self.status == "complete":
            return f"[green]{Icons.SUCCESS}[/green]"
        elif self.status == "running":
            return f"[yellow]{Icons.RUNNING}[/yellow]"
        elif self.status == "error":
            return f"[red]{Icons.ERROR}[/red]"
        elif self.status == "blocked":
            return f"[dim]{Icons.BLOCKED}[/dim]"
        else:
            return f"[dim]{Icons.READY}[/dim]"


class WorkflowTimeline:
    """Interactive workflow timeline visualizer."""

    def __init__(self, nodes: List[WorkflowNode]):
        """Initialize workflow timeline.

        Args:
            nodes: List of workflow nodes
        """
        self.nodes = {node.node_id: node for node in nodes}
        self.execution_order: List[str] = []

    def add_node(self, node: WorkflowNode) -> None:
        """Add a node to the workflow.

        Args:
            node: Workflow node to add
        """
        self.nodes[node.node_id] = node

    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID.

        Args:
            node_id: Node identifier

        Returns:
            Workflow node or None
        """
        return self.nodes.get(node_id)

    def calculate_levels(self) -> Dict[str, int]:
        """Calculate dependency levels for timeline layout.

        Returns:
            Dictionary mapping node_id to level (0 = no deps, 1+ = has deps)
        """
        levels: Dict[str, int] = {}

        def get_level(node_id: str) -> int:
            if node_id in levels:
                return levels[node_id]

            node = self.nodes.get(node_id)
            if not node or not node.dependencies:
                levels[node_id] = 0
                return 0

            # Level is 1 + max level of dependencies
            dep_levels = [
                get_level(dep_id)
                for dep_id in node.dependencies
                if dep_id in self.nodes
            ]
            levels[node_id] = max(dep_levels, default=0) + 1
            return levels[node_id]

        # Calculate levels for all nodes
        for node_id in self.nodes:
            get_level(node_id)

        return levels

    def render_timeline(self, width: int = 80) -> List[str]:
        """Render workflow as a timeline.

        Args:
            width: Width of the timeline

        Returns:
            List of formatted timeline lines
        """
        lines = []
        levels = self.calculate_levels()

        # Group nodes by level
        nodes_by_level: Dict[int, List[str]] = {}
        for node_id, level in levels.items():
            if level not in nodes_by_level:
                nodes_by_level[level] = []
            nodes_by_level[level].append(node_id)

        # Render each level
        for level in sorted(nodes_by_level.keys()):
            lines.append(f"[dim]{'─' * width}[/dim]")
            lines.append(f"[bold]Level {level}[/bold]")
            lines.append("")

            for node_id in nodes_by_level[level]:
                node = self.nodes[node_id]
                lines.extend(self._render_node(node, width))
                lines.append("")

        return lines

    def _render_node(self, node: WorkflowNode, width: int = 80) -> List[str]:
        """Render a single node.

        Args:
            node: Workflow node
            width: Display width

        Returns:
            List of formatted lines
        """
        lines = []

        # Node header
        status_icon = node.get_status_icon()
        header = f"{status_icon} [bold]{node.name}[/bold] [dim]({node.node_id})[/dim]"
        lines.append(header)

        # Progress bar (if running or complete)
        if node.status in ("running", "complete"):
            progress = ProgressBar.simple_bar(node.progress, 100, width=30)
            lines.append(f"  {progress}")

        # Duration (if available)
        duration = node.get_duration()
        if duration is not None:
            duration_str = Format.duration(int(duration.total_seconds()))
            lines.append(f"  [dim]Duration: {duration_str}[/dim]")

        # Dependencies (if any)
        if node.dependencies:
            dep_names = []
            for dep_id in node.dependencies:
                dep_node = self.nodes.get(dep_id)
                if dep_node:
                    dep_status = dep_node.get_status_icon()
                    dep_names.append(f"{dep_status} {dep_node.name}")

            lines.append(f"  [dim]Depends on:[/dim]")
            for dep_name in dep_names:
                lines.append(f"    {Icons.ARROW_RIGHT} {dep_name}")

        # Error message (if any)
        if node.error_message:
            lines.append(f"  [red]{Icons.ERROR} {node.error_message}[/red]")

        return lines

    def render_gantt_chart(self, width: int = 80) -> List[str]:
        """Render workflow as a Gantt chart.

        Args:
            width: Width of the chart

        Returns:
            List of formatted chart lines
        """
        lines = []

        # Find time bounds
        start_times = [n.start_time for n in self.nodes.values() if n.start_time]
        end_times = [
            n.end_time or datetime.now() for n in self.nodes.values() if n.start_time
        ]

        if not start_times:
            return ["[dim]No workflow data available[/dim]"]

        workflow_start = min(start_times)
        workflow_end = max(end_times)
        total_duration = (workflow_end - workflow_start).total_seconds()

        if total_duration == 0:
            total_duration = 1  # Avoid division by zero

        # Header
        lines.append(f"[bold]Workflow Gantt Chart[/bold]")
        lines.append(f"[dim]Start: {workflow_start.strftime('%H:%M:%S')}[/dim]")
        lines.append(f"[dim]Duration: {Format.duration(int(total_duration))}[/dim]")
        lines.append("")

        # Chart width for bars
        bar_width = width - 30  # Leave room for labels

        # Render each node
        for node in self.nodes.values():
            if not node.start_time:
                continue

            # Calculate bar position and width
            start_offset = (node.start_time - workflow_start).total_seconds()
            start_pos = int((start_offset / total_duration) * bar_width)

            if node.end_time:
                duration = (node.end_time - node.start_time).total_seconds()
            else:
                duration = (datetime.now() - node.start_time).total_seconds()

            bar_length = max(1, int((duration / total_duration) * bar_width))

            # Create bar
            if node.status == "complete":
                bar_char = "█"
                bar_color = "green"
            elif node.status == "running":
                bar_char = "▓"
                bar_color = "yellow"
            elif node.status == "error":
                bar_char = "░"
                bar_color = "red"
            else:
                bar_char = "░"
                bar_color = "dim"

            # Format line
            label = Format.truncate(node.name, 25).ljust(25)
            padding = " " * start_pos
            bar = bar_char * bar_length

            line = f"{label} │{padding}[{bar_color}]{bar}[/{bar_color}]"
            lines.append(line)

        return lines

    def get_summary(self) -> Dict[str, Any]:
        """Get workflow execution summary.

        Returns:
            Summary dictionary
        """
        total = len(self.nodes)
        complete = sum(1 for n in self.nodes.values() if n.status == "complete")
        running = sum(1 for n in self.nodes.values() if n.status == "running")
        pending = sum(1 for n in self.nodes.values() if n.status == "pending")
        errors = sum(1 for n in self.nodes.values() if n.status == "error")

        # Calculate total duration
        start_times = [n.start_time for n in self.nodes.values() if n.start_time]
        end_times = [n.end_time for n in self.nodes.values() if n.end_time]

        total_duration = None
        if start_times and end_times:
            workflow_start = min(start_times)
            workflow_end = max(end_times)
            total_duration = (workflow_end - workflow_start).total_seconds()

        return {
            "total": total,
            "complete": complete,
            "running": running,
            "pending": pending,
            "errors": errors,
            "completion_pct": (complete / total * 100) if total > 0 else 0,
            "duration": total_duration,
        }


class DependencyVisualizer:
    """Visualize workflow dependencies as a tree/graph."""

    def __init__(self, nodes: List[WorkflowNode]):
        """Initialize dependency visualizer.

        Args:
            nodes: List of workflow nodes
        """
        self.nodes = {node.node_id: node for node in nodes}

    def render_tree(self, root_id: Optional[str] = None) -> List[str]:
        """Render dependency tree.

        Args:
            root_id: Starting node (None = show all roots)

        Returns:
            List of formatted tree lines
        """
        lines = []

        if root_id:
            # Render from specific root
            root = self.nodes.get(root_id)
            if root:
                lines.extend(self._render_subtree(root, "", is_last=True))
        else:
            # Find and render all roots (nodes with no dependencies)
            roots = [n for n in self.nodes.values() if not n.dependencies]

            if not roots:
                return ["[dim]No root nodes found[/dim]"]

            for idx, root in enumerate(roots):
                is_last = idx == len(roots) - 1
                lines.extend(self._render_subtree(root, "", is_last))

        return lines

    def _render_subtree(
        self, node: WorkflowNode, prefix: str, is_last: bool
    ) -> List[str]:
        """Recursively render a subtree.

        Args:
            node: Current node
            prefix: Line prefix for tree structure
            is_last: Whether this is the last sibling

        Returns:
            List of formatted lines
        """
        lines = []

        # Node connector
        connector = Icons.LAST_BRANCH if is_last else Icons.BRANCH

        # Node line
        status_icon = node.get_status_icon()
        node_line = f"{prefix}{connector} {status_icon} [bold]{node.name}[/bold]"
        lines.append(node_line)

        # Find dependents (nodes that depend on this one)
        dependents = [n for n in self.nodes.values() if node.node_id in n.dependencies]

        # Render dependents
        if dependents:
            new_prefix = prefix + (Icons.SPACE if is_last else f"{Icons.PIPE} ")

            for idx, dependent in enumerate(dependents):
                is_last_dependent = idx == len(dependents) - 1
                lines.extend(
                    self._render_subtree(dependent, new_prefix, is_last_dependent)
                )

        return lines

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in workflow.

        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        cycles = []
        visited: Set[str] = set()
        path: List[str] = []

        def dfs(node_id: str) -> None:
            if node_id in path:
                # Found a cycle
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for dep_id in node.dependencies:
                    if dep_id in self.nodes:
                        dfs(dep_id)

            path.pop()

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles
