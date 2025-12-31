"""Performance monitoring and system metrics for TUI."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime, timedelta
from .tui_icons import Icons
from .tui_format import Format


class SystemMetrics:
    """System performance metrics collector."""

    def __init__(self) -> None:
        """Initialize system metrics collector."""
        self.start_time = time.time()
        self._last_check = time.time()
        self._check_interval = 1.0  # seconds

    def get_uptime(self) -> str:
        """Get application uptime.

        Returns:
            Formatted uptime string
        """
        elapsed = time.time() - self.start_time
        return Format.duration(int(elapsed))

    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information.

        Returns:
            Dictionary with memory stats
        """
        try:
            import psutil

            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()

            return {
                "rss": mem_info.rss,  # Resident Set Size
                "rss_formatted": Format.bytes(mem_info.rss),
                "percent": process.memory_percent(),
            }
        except ImportError:
            # Fallback if psutil not available
            return {
                "rss": 0,
                "rss_formatted": "N/A",
                "percent": 0.0,
            }

    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage.

        Returns:
            CPU usage percentage
        """
        try:
            import psutil

            process = psutil.Process(os.getpid())
            # Get CPU percent with interval for accuracy
            return float(process.cpu_percent(interval=0.1))
        except ImportError:
            return 0.0

    def get_thread_count(self) -> int:
        """Get number of active threads.

        Returns:
            Thread count
        """
        try:
            import psutil

            process = psutil.Process(os.getpid())
            return int(process.num_threads())
        except ImportError:
            import threading

            return threading.active_count()

    def should_update(self) -> bool:
        """Check if metrics should be updated based on interval.

        Returns:
            True if should update
        """
        now = time.time()
        if now - self._last_check >= self._check_interval:
            self._last_check = now
            return True
        return False


class PerformanceMonitor:
    """Performance monitor for TUI status bar."""

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.metrics = SystemMetrics()
        self._cached_display = ""
        self._last_update = time.time()

    def get_status_bar(self, compact: bool = False) -> str:
        """Get performance status bar text.

        Args:
            compact: Use compact display format

        Returns:
            Formatted status bar string
        """
        # Update if interval has passed OR if we don't have cached data
        if self.metrics.should_update() or not self._cached_display:
            if compact:
                self._cached_display = self._get_compact_display()
            else:
                self._cached_display = self._get_full_display()

        return self._cached_display

    def _get_full_display(self) -> str:
        """Get full performance display.

        Returns:
            Formatted performance string
        """
        parts = []

        # Uptime
        uptime = self.metrics.get_uptime()
        parts.append(f"{Icons.RUNNING} {uptime}")

        # Memory
        mem = self.metrics.get_memory_usage()
        mem_color = self._get_mem_color(mem["percent"])
        parts.append(
            f"[{mem_color}]{Icons.METRICS} {mem['rss_formatted']}[/{mem_color}]"
        )

        # CPU
        cpu = self.metrics.get_cpu_usage()
        cpu_color = self._get_cpu_color(cpu)
        parts.append(f"[{cpu_color}]CPU {cpu:.1f}%[/{cpu_color}]")

        # Threads
        threads = self.metrics.get_thread_count()
        parts.append(f"[dim]{Icons.BRANCH} {threads} threads[/dim]")

        return " [dim]│[/dim] ".join(parts)

    def _get_compact_display(self) -> str:
        """Get compact performance display.

        Returns:
            Formatted compact string
        """
        mem = self.metrics.get_memory_usage()
        cpu = self.metrics.get_cpu_usage()

        mem_color = self._get_mem_color(mem["percent"])
        cpu_color = self._get_cpu_color(cpu)

        return f"[{mem_color}]{mem['rss_formatted']}[/{mem_color}] [{cpu_color}]{cpu:.0f}%[/{cpu_color}]"

    def _get_mem_color(self, percent: float) -> str:
        """Get color based on memory usage.

        Args:
            percent: Memory usage percentage

        Returns:
            Color name
        """
        if percent > 80:
            return "red"
        elif percent > 60:
            return "yellow"
        else:
            return "green"

    def _get_cpu_color(self, percent: float) -> str:
        """Get color based on CPU usage.

        Args:
            percent: CPU usage percentage

        Returns:
            Color name
        """
        if percent > 80:
            return "red"
        elif percent > 50:
            return "yellow"
        else:
            return "green"


class TaskRecord(TypedDict, total=False):
    name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    status: str


class TaskPerformanceTracker:
    """Track performance of individual tasks and agents."""

    def __init__(self) -> None:
        """Initialize task performance tracker."""
        self.tasks: Dict[str, TaskRecord] = {}

    def start_task(self, task_id: str, task_name: str) -> None:
        """Start tracking a task.

        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
        """
        self.tasks[task_id] = {
            "name": task_name,
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "status": "running",
        }

    def end_task(self, task_id: str, status: str = "complete") -> None:
        """End tracking a task.

        Args:
            task_id: Task identifier
            status: Final status (complete, error, cancelled)
        """
        record = self.tasks.get(task_id)
        if record is None:
            return

        end_time = time.time()
        start_time = record.get("start_time", end_time)
        record["end_time"] = end_time
        record["duration"] = float(end_time - start_time)
        record["status"] = status

    def get_task_duration(self, task_id: str) -> Optional[float]:
        """Get task duration.

        Args:
            task_id: Task identifier

        Returns:
            Duration in seconds or None
        """
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]

        duration = task.get("duration")
        if isinstance(duration, (int, float)):
            return float(duration)

        end_time = task.get("end_time")
        start_time = task.get("start_time")
        if end_time is None and isinstance(start_time, (int, float)):
            return float(time.time() - start_time)

        if isinstance(end_time, (int, float)) and isinstance(start_time, (int, float)):
            return float(end_time - start_time)

        return None

    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """Get list of currently running tasks.

        Returns:
            List of running task dictionaries
        """
        return [
            {
                "id": task_id,
                "name": task["name"],
                "duration": time.time()
                - float(task.get("start_time", time.time())),
            }
            for task_id, task in self.tasks.items()
            if task["status"] == "running"
        ]

    def get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get list of completed tasks.

        Returns:
            List of completed task dictionaries
        """
        return [
            {
                "id": task_id,
                "name": task["name"],
                "duration": task["duration"],
                "status": task["status"],
            }
            for task_id, task in self.tasks.items()
            if task["status"] != "running"
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary.

        Returns:
            Summary dictionary
        """
        completed = self.get_completed_tasks()
        running = self.get_running_tasks()

        duration_values = [
            float(t["duration"])
            for t in completed
            if isinstance(t.get("duration"), (int, float))
        ]
        total_time = sum(duration_values)
        avg_time = total_time / len(duration_values) if duration_values else 0.0

        return {
            "total_tasks": len(self.tasks),
            "running": len(running),
            "completed": len([t for t in completed if t["status"] == "complete"]),
            "failed": len([t for t in completed if t["status"] == "error"]),
            "total_time": total_time,
            "avg_time": avg_time,
        }

    def clear_completed(self) -> None:
        """Clear completed tasks from tracking."""
        self.tasks = {
            task_id: task
            for task_id, task in self.tasks.items()
            if task["status"] == "running"
        }


class PerformanceAlert:
    """Alert system for performance issues."""

    def __init__(self) -> None:
        """Initialize performance alert system."""
        self.alerts: List[str] = []
        self.thresholds = {
            "memory_percent": 85.0,
            "cpu_percent": 90.0,
            "task_duration": 300.0,  # 5 minutes
        }

    def check_metrics(self, metrics: SystemMetrics) -> List[str]:
        """Check metrics against thresholds and generate alerts.

        Args:
            metrics: System metrics instance

        Returns:
            List of alert messages
        """
        alerts = []

        # Check memory
        mem = metrics.get_memory_usage()
        if mem["percent"] > self.thresholds["memory_percent"]:
            alerts.append(f"{Icons.WARNING} High memory usage: {mem['percent']:.1f}%")

        # Check CPU
        cpu = metrics.get_cpu_usage()
        if cpu > self.thresholds["cpu_percent"]:
            alerts.append(f"{Icons.WARNING} High CPU usage: {cpu:.1f}%")

        return alerts

    def set_threshold(self, metric: str, value: float) -> None:
        """Set alert threshold for a metric.

        Args:
            metric: Metric name
            value: Threshold value
        """
        if metric in self.thresholds:
            self.thresholds[metric] = value
