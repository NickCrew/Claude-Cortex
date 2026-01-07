"""Comprehensive tests for claude_ctx_py/tui_workflow_viz.py

Tests cover:
- WorkflowNode creation and methods
- WorkflowTimeline operations (add, get, calculate_levels)
- WorkflowTimeline rendering (timeline, Gantt chart)
- DependencyVisualizer (tree rendering, cycle detection)
- Edge cases (empty workflows, cycles, missing nodes)
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from claude_ctx_py.tui_workflow_viz import (
    DependencyVisualizer,
    WorkflowNode,
    WorkflowTimeline,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def basic_node():
    """Create a basic workflow node."""
    return WorkflowNode(
        node_id="task-1",
        name="Test Task",
        status="pending",
    )


@pytest.fixture
def completed_node():
    """Create a completed node with timing."""
    node = WorkflowNode(
        node_id="task-done",
        name="Completed Task",
        status="complete",
    )
    node.start_time = datetime(2025, 1, 5, 10, 0, 0)
    node.end_time = datetime(2025, 1, 5, 10, 5, 30)
    node.progress = 100.0
    return node


@pytest.fixture
def running_node():
    """Create a running node."""
    node = WorkflowNode(
        node_id="task-running",
        name="Running Task",
        status="running",
    )
    node.start_time = datetime(2025, 1, 5, 10, 0, 0)
    node.progress = 50.0
    return node


@pytest.fixture
def error_node():
    """Create an error node."""
    node = WorkflowNode(
        node_id="task-error",
        name="Error Task",
        status="error",
    )
    node.error_message = "Something went wrong"
    return node


@pytest.fixture
def simple_timeline():
    """Create a simple linear workflow."""
    nodes = [
        WorkflowNode("root", "Root Task", "complete"),
        WorkflowNode("child1", "Child 1", "running", dependencies=["root"]),
        WorkflowNode("child2", "Child 2", "pending", dependencies=["root"]),
        WorkflowNode("grandchild", "Grandchild", "pending", dependencies=["child1", "child2"]),
    ]
    return WorkflowTimeline(nodes)


@pytest.fixture
def timed_timeline():
    """Create a timeline with timing data."""
    base_time = datetime(2025, 1, 5, 9, 0, 0)

    node1 = WorkflowNode("task-1", "Task 1", "complete")
    node1.start_time = base_time
    node1.end_time = base_time + timedelta(minutes=10)
    node1.progress = 100.0

    node2 = WorkflowNode("task-2", "Task 2", "complete", dependencies=["task-1"])
    node2.start_time = base_time + timedelta(minutes=5)
    node2.end_time = base_time + timedelta(minutes=20)
    node2.progress = 100.0

    node3 = WorkflowNode("task-3", "Task 3", "running", dependencies=["task-1"])
    node3.start_time = base_time + timedelta(minutes=10)
    node3.progress = 60.0

    return WorkflowTimeline([node1, node2, node3])


@pytest.fixture
def cyclic_nodes():
    """Create nodes with circular dependencies."""
    return [
        WorkflowNode("a", "Node A", "pending", dependencies=["c"]),
        WorkflowNode("b", "Node B", "pending", dependencies=["a"]),
        WorkflowNode("c", "Node C", "pending", dependencies=["b"]),
    ]


# =============================================================================
# Tests for WorkflowNode
# =============================================================================


class TestWorkflowNode:
    """Tests for WorkflowNode class."""

    def test_create_basic_node(self, basic_node):
        """Test basic node creation."""
        assert basic_node.node_id == "task-1"
        assert basic_node.name == "Test Task"
        assert basic_node.status == "pending"
        assert basic_node.dependencies == []
        assert basic_node.progress == 0.0
        assert basic_node.start_time is None
        assert basic_node.end_time is None

    def test_create_node_with_dependencies(self):
        """Test node creation with dependencies."""
        node = WorkflowNode(
            "task-2",
            "Dependent Task",
            "pending",
            dependencies=["task-1", "task-0"],
        )
        assert node.dependencies == ["task-1", "task-0"]

    def test_get_duration_not_started(self, basic_node):
        """Test duration when not started."""
        assert basic_node.get_duration() is None

    def test_get_duration_completed(self, completed_node):
        """Test duration for completed node."""
        duration = completed_node.get_duration()
        assert duration == timedelta(minutes=5, seconds=30)

    def test_get_duration_running(self, running_node):
        """Test duration for running node (no end time)."""
        with patch("claude_ctx_py.tui_workflow_viz.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 5, 10, 10, 0)
            duration = running_node.get_duration()

        assert duration == timedelta(minutes=10)

    def test_get_status_icon_complete(self, completed_node):
        """Test status icon for complete."""
        icon = completed_node.get_status_icon()
        assert "green" in icon

    def test_get_status_icon_running(self, running_node):
        """Test status icon for running."""
        icon = running_node.get_status_icon()
        assert "yellow" in icon

    def test_get_status_icon_error(self, error_node):
        """Test status icon for error."""
        icon = error_node.get_status_icon()
        assert "red" in icon

    def test_get_status_icon_pending(self, basic_node):
        """Test status icon for pending."""
        icon = basic_node.get_status_icon()
        assert "dim" in icon

    def test_get_status_icon_blocked(self):
        """Test status icon for blocked."""
        node = WorkflowNode("blocked", "Blocked", "blocked")
        icon = node.get_status_icon()
        assert "dim" in icon


# =============================================================================
# Tests for WorkflowTimeline
# =============================================================================


class TestWorkflowTimeline:
    """Tests for WorkflowTimeline class."""

    def test_create_empty_timeline(self):
        """Test creating empty timeline."""
        timeline = WorkflowTimeline([])
        assert len(timeline.nodes) == 0

    def test_create_timeline_with_nodes(self, simple_timeline):
        """Test creating timeline with nodes."""
        assert len(simple_timeline.nodes) == 4
        assert "root" in simple_timeline.nodes
        assert "grandchild" in simple_timeline.nodes

    def test_add_node(self):
        """Test adding a node."""
        timeline = WorkflowTimeline([])
        node = WorkflowNode("new", "New Node", "pending")
        timeline.add_node(node)

        assert "new" in timeline.nodes
        assert timeline.nodes["new"] == node

    def test_add_node_replaces_existing(self, simple_timeline):
        """Test that adding node replaces existing."""
        new_node = WorkflowNode("root", "New Root", "running")
        simple_timeline.add_node(new_node)

        assert simple_timeline.nodes["root"].name == "New Root"
        assert simple_timeline.nodes["root"].status == "running"

    def test_get_node_exists(self, simple_timeline):
        """Test getting existing node."""
        node = simple_timeline.get_node("root")
        assert node is not None
        assert node.name == "Root Task"

    def test_get_node_not_exists(self, simple_timeline):
        """Test getting non-existent node."""
        node = simple_timeline.get_node("nonexistent")
        assert node is None

    def test_calculate_levels_simple(self, simple_timeline):
        """Test level calculation for simple timeline."""
        levels = simple_timeline.calculate_levels()

        assert levels["root"] == 0
        assert levels["child1"] == 1
        assert levels["child2"] == 1
        assert levels["grandchild"] == 2

    def test_calculate_levels_no_deps(self):
        """Test level calculation for nodes without deps."""
        nodes = [
            WorkflowNode("a", "A", "pending"),
            WorkflowNode("b", "B", "pending"),
        ]
        timeline = WorkflowTimeline(nodes)
        levels = timeline.calculate_levels()

        assert levels["a"] == 0
        assert levels["b"] == 0

    def test_calculate_levels_missing_dep(self):
        """Test level calculation with missing dependency."""
        nodes = [
            WorkflowNode("child", "Child", "pending", dependencies=["missing"]),
        ]
        timeline = WorkflowTimeline(nodes)
        levels = timeline.calculate_levels()

        # Should still calculate a level
        assert "child" in levels


class TestWorkflowTimelineRendering:
    """Tests for timeline rendering methods."""

    def test_render_timeline_simple(self, simple_timeline):
        """Test rendering simple timeline."""
        lines = simple_timeline.render_timeline()

        assert isinstance(lines, list)
        assert len(lines) > 0
        # Should contain node names
        output = "\n".join(lines)
        assert "Root Task" in output

    def test_render_timeline_empty(self):
        """Test rendering empty timeline."""
        timeline = WorkflowTimeline([])
        lines = timeline.render_timeline()
        assert isinstance(lines, list)

    def test_render_timeline_shows_levels(self, simple_timeline):
        """Test that timeline shows level information."""
        lines = simple_timeline.render_timeline()
        output = "\n".join(lines)

        assert "Level 0" in output
        assert "Level 1" in output

    def test_render_timeline_custom_width(self, simple_timeline):
        """Test timeline rendering with custom width."""
        lines = simple_timeline.render_timeline(width=40)
        assert isinstance(lines, list)

    def test_render_gantt_with_timing(self, timed_timeline):
        """Test Gantt chart rendering with timing data."""
        lines = timed_timeline.render_gantt_chart()

        assert isinstance(lines, list)
        assert len(lines) > 0
        output = "\n".join(lines)
        assert "Gantt" in output

    def test_render_gantt_no_timing(self, simple_timeline):
        """Test Gantt chart when no timing data."""
        lines = simple_timeline.render_gantt_chart()

        output = "\n".join(lines)
        assert "No workflow data" in output

    def test_render_gantt_shows_bars(self, timed_timeline):
        """Test that Gantt shows progress bars."""
        lines = timed_timeline.render_gantt_chart()
        output = "\n".join(lines)

        # Should contain bar characters
        assert "█" in output or "▓" in output or "░" in output

    def test_render_gantt_custom_width(self, timed_timeline):
        """Test Gantt chart with custom width."""
        lines = timed_timeline.render_gantt_chart(width=60)
        assert isinstance(lines, list)


class TestWorkflowTimelineSummary:
    """Tests for timeline summary."""

    def test_get_summary(self, simple_timeline):
        """Test getting workflow summary."""
        summary = simple_timeline.get_summary()

        assert summary["total"] == 4
        assert summary["complete"] == 1
        assert summary["running"] == 1
        assert summary["pending"] == 2
        assert summary["errors"] == 0

    def test_get_summary_empty(self):
        """Test summary for empty timeline."""
        timeline = WorkflowTimeline([])
        summary = timeline.get_summary()

        assert summary["total"] == 0
        assert summary["completion_pct"] == 0

    def test_get_summary_all_complete(self):
        """Test summary when all tasks complete."""
        nodes = [
            WorkflowNode("a", "A", "complete"),
            WorkflowNode("b", "B", "complete"),
        ]
        timeline = WorkflowTimeline(nodes)
        summary = timeline.get_summary()

        assert summary["completion_pct"] == 100

    def test_get_summary_with_duration(self, timed_timeline):
        """Test summary includes duration."""
        # Complete the running task to have all end times
        timed_timeline.nodes["task-3"].end_time = datetime(2025, 1, 5, 9, 30, 0)
        timed_timeline.nodes["task-3"].status = "complete"

        summary = timed_timeline.get_summary()
        assert summary["duration"] is not None


# =============================================================================
# Tests for DependencyVisualizer
# =============================================================================


class TestDependencyVisualizer:
    """Tests for DependencyVisualizer class."""

    def test_create_visualizer(self, simple_timeline):
        """Test creating dependency visualizer."""
        viz = DependencyVisualizer(list(simple_timeline.nodes.values()))
        assert len(viz.nodes) == 4

    def test_render_tree(self, simple_timeline):
        """Test rendering dependency tree."""
        viz = DependencyVisualizer(list(simple_timeline.nodes.values()))
        lines = viz.render_tree()

        assert isinstance(lines, list)
        assert len(lines) > 0
        output = "\n".join(lines)
        assert "Root Task" in output

    def test_render_tree_from_root(self, simple_timeline):
        """Test rendering tree from specific root."""
        viz = DependencyVisualizer(list(simple_timeline.nodes.values()))
        lines = viz.render_tree(root_id="root")

        output = "\n".join(lines)
        assert "Root Task" in output

    def test_render_tree_invalid_root(self, simple_timeline):
        """Test rendering tree with invalid root."""
        viz = DependencyVisualizer(list(simple_timeline.nodes.values()))
        lines = viz.render_tree(root_id="nonexistent")

        # Should return empty or minimal output
        assert isinstance(lines, list)

    def test_render_tree_empty(self):
        """Test rendering empty tree."""
        viz = DependencyVisualizer([])
        lines = viz.render_tree()

        output = "\n".join(lines)
        assert "No root nodes" in output

    def test_render_tree_no_roots(self, cyclic_nodes):
        """Test rendering when no root nodes (all have deps)."""
        viz = DependencyVisualizer(cyclic_nodes)
        lines = viz.render_tree()

        output = "\n".join(lines)
        assert "No root nodes" in output


class TestDependencyVisualizerCycleDetection:
    """Tests for cycle detection."""

    def test_detect_cycles_no_cycles(self, simple_timeline):
        """Test cycle detection finds no cycles in acyclic graph."""
        viz = DependencyVisualizer(list(simple_timeline.nodes.values()))
        cycles = viz.detect_cycles()

        assert cycles == []

    def test_detect_cycles_with_cycle(self, cyclic_nodes):
        """Test cycle detection finds cycles."""
        viz = DependencyVisualizer(cyclic_nodes)
        cycles = viz.detect_cycles()

        assert len(cycles) > 0

    def test_detect_cycles_self_loop(self):
        """Test detection of self-referential node."""
        node = WorkflowNode("self", "Self Ref", "pending", dependencies=["self"])
        viz = DependencyVisualizer([node])
        cycles = viz.detect_cycles()

        assert len(cycles) > 0

    def test_detect_cycles_empty(self):
        """Test cycle detection on empty graph."""
        viz = DependencyVisualizer([])
        cycles = viz.detect_cycles()

        assert cycles == []

    def test_detect_cycles_returns_node_ids(self, cyclic_nodes):
        """Test that cycles contain node IDs."""
        viz = DependencyVisualizer(cyclic_nodes)
        cycles = viz.detect_cycles()

        for cycle in cycles:
            assert isinstance(cycle, list)
            for node_id in cycle:
                assert isinstance(node_id, str)


# =============================================================================
# Edge case tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_node_with_empty_id(self):
        """Test node with empty ID."""
        node = WorkflowNode("", "Empty ID", "pending")
        assert node.node_id == ""

    def test_node_with_special_chars(self):
        """Test node with special characters in name."""
        node = WorkflowNode("special", "Task <>&\"'", "pending")
        icon = node.get_status_icon()
        assert isinstance(icon, str)

    def test_very_long_dependency_chain(self):
        """Test timeline with long linear chain."""
        nodes = []
        prev_id = None
        for i in range(50):
            deps = [prev_id] if prev_id else []
            node = WorkflowNode(f"task-{i}", f"Task {i}", "pending", dependencies=deps)
            nodes.append(node)
            prev_id = f"task-{i}"

        timeline = WorkflowTimeline(nodes)
        levels = timeline.calculate_levels()

        assert levels["task-0"] == 0
        assert levels["task-49"] == 49

    def test_wide_dependency_tree(self):
        """Test timeline with many parallel nodes."""
        root = WorkflowNode("root", "Root", "complete")
        children = [
            WorkflowNode(f"child-{i}", f"Child {i}", "pending", dependencies=["root"])
            for i in range(20)
        ]

        timeline = WorkflowTimeline([root] + children)
        levels = timeline.calculate_levels()

        assert levels["root"] == 0
        for i in range(20):
            assert levels[f"child-{i}"] == 1

    def test_diamond_dependency(self):
        """Test diamond-shaped dependency graph."""
        nodes = [
            WorkflowNode("root", "Root", "complete"),
            WorkflowNode("left", "Left", "complete", dependencies=["root"]),
            WorkflowNode("right", "Right", "complete", dependencies=["root"]),
            WorkflowNode("bottom", "Bottom", "pending", dependencies=["left", "right"]),
        ]

        timeline = WorkflowTimeline(nodes)
        levels = timeline.calculate_levels()

        assert levels["root"] == 0
        assert levels["left"] == 1
        assert levels["right"] == 1
        assert levels["bottom"] == 2

    def test_zero_duration_task(self):
        """Test task with instant completion."""
        node = WorkflowNode("instant", "Instant", "complete")
        timestamp = datetime(2025, 1, 5, 10, 0, 0)
        node.start_time = timestamp
        node.end_time = timestamp

        duration = node.get_duration()
        assert duration == timedelta(0)

    def test_gantt_zero_total_duration(self):
        """Test Gantt chart when total duration is zero."""
        node = WorkflowNode("instant", "Instant", "complete")
        timestamp = datetime(2025, 1, 5, 10, 0, 0)
        node.start_time = timestamp
        node.end_time = timestamp

        timeline = WorkflowTimeline([node])
        lines = timeline.render_gantt_chart()

        # Should not crash
        assert isinstance(lines, list)

    def test_node_with_progress_values(self):
        """Test node with various progress values."""
        for progress in [0, 25, 50, 75, 100]:
            node = WorkflowNode(f"p{progress}", f"Progress {progress}", "running")
            node.progress = float(progress)
            assert node.progress == progress
