"""Watch mode for real-time AI recommendations and auto-activation.

Monitors file changes and provides intelligent recommendations in real-time.
"""

from __future__ import annotations

import os
import time
import subprocess
import signal
import sys
import threading
from pathlib import Path
from types import FrameType
from typing import Any, Callable, Deque, Dict, List, Optional, Set
from datetime import datetime
from collections import deque

from .intelligence import IntelligentAgent, AgentRecommendation
from .core import _resolve_claude_dir, agent_activate, agent_deactivate


class WatchMode:
    """Watch mode for real-time AI recommendations."""

    def __init__(
        self,
        auto_activate: bool = True,
        notification_threshold: float = 0.7,
        check_interval: float = 2.0,
        notification_callback: Optional[Callable[[Dict[str, str]], None]] = None,
    ):
        """Initialize watch mode.

        Args:
            auto_activate: Auto-activate high-confidence recommendations
            notification_threshold: Confidence threshold for notifications
            check_interval: Seconds between checks
            notification_callback: Optional callback for notifications
        """
        self.auto_activate = auto_activate
        self.notification_threshold = notification_threshold
        self.check_interval = check_interval
        self.notification_callback = notification_callback

        # Initialize intelligent agent
        claude_dir = _resolve_claude_dir()
        self.intelligent_agent = IntelligentAgent(claude_dir / "intelligence")

        # Track state
        self.running = False
        self.directory = Path.cwd()
        self.last_check_time = time.time()
        self.last_git_head = self._get_git_head()
        self.last_recommendations: List[AgentRecommendation] = []
        self.activated_agents: Set[str] = set()
        self.notification_history: Deque[Dict[str, str]] = deque(maxlen=50)

        # Statistics
        self.checks_performed = 0
        self.recommendations_made = 0
        self.auto_activations = 0
        self.start_time = datetime.now()

        # Thread safety
        self._state_lock = threading.Lock()

    def stop(self) -> None:
        """Stop watch mode gracefully."""
        with self._state_lock:
            self.running = False

    def set_directory(self, directory: Path) -> None:
        """Set the directory to watch.

        Args:
            directory: Directory path to watch
        """
        with self._state_lock:
            self.directory = directory
            self.last_git_head = self._get_git_head()

    def change_directory(self, directory: Path) -> None:
        """Change the watched directory.

        Args:
            directory: New directory path to watch
        """
        with self._state_lock:
            old_dir = os.getcwd()
            try:
                os.chdir(directory)
                self.directory = directory
                self.last_git_head = self._get_git_head()
            except Exception:
                os.chdir(old_dir)
                raise

    def get_state(self) -> Dict[str, Any]:
        """Get current watch mode state.

        Returns:
            Dictionary with current state
        """
        with self._state_lock:
            return {
                "running": self.running,
                "directory": self.directory,
                "auto_activate": self.auto_activate,
                "threshold": self.notification_threshold,
                "interval": self.check_interval,
                "checks_performed": self.checks_performed,
                "recommendations_made": self.recommendations_made,
                "auto_activations": self.auto_activations,
                "started_at": self.start_time,
                "last_notification": self.notification_history[-1] if self.notification_history else None,
            }

    def _get_git_head(self) -> Optional[str]:
        """Get current git HEAD hash.

        Returns:
            HEAD hash or None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def _get_changed_files(self) -> List[Path]:
        """Get list of changed files from git.

        Returns:
            List of changed file paths
        """
        try:
            # Get unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Get staged changes
            staged = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                check=True,
            )

            all_files = set(result.stdout.split("\n") + staged.stdout.split("\n"))
            return [Path(f) for f in all_files if f.strip()]

        except Exception:
            return []

    def _print_banner(self) -> None:
        """Print watch mode banner."""
        print("\n" + "═" * 70)
        print("🤖 AI WATCH MODE - Real-time Intelligence")
        print("═" * 70)
        print(f"\n[{self._timestamp()}] Watch mode started")
        print(f"  Auto-activate: {'ON' if self.auto_activate else 'OFF'}")
        print(f"  Threshold: {self.notification_threshold * 100:.0f}% confidence")
        print(f"  Check interval: {self.check_interval}s")
        print("\n  Monitoring:")
        print("    • Git changes (commits, staged, unstaged)")
        print("    • File modifications")
        print("    • Context changes")
        print("\n  Press Ctrl+C to stop\n")
        print("─" * 70 + "\n")

    def _timestamp(self) -> str:
        """Get formatted timestamp.

        Returns:
            HH:MM:SS string
        """
        return datetime.now().strftime("%H:%M:%S")

    def _print_notification(
        self, icon: str, title: str, message: str, color: str = "white"
    ) -> None:
        """Print a notification.

        Args:
            icon: Emoji icon
            title: Notification title
            message: Notification message
            color: ANSI color name
        """
        timestamp = self._timestamp()

        # Store in history
        notification = {
            "timestamp": timestamp,
            "icon": icon,
            "title": title,
            "message": message,
        }
        self.notification_history.append(notification)

        # Call notification callback if provided
        if self.notification_callback:
            try:
                self.notification_callback(notification)
            except Exception:
                pass  # Don't let callback errors stop watch mode

        # Print with color
        color_codes = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "dim": "\033[2m",
        }

        reset = "\033[0m"
        color_code = color_codes.get(color, color_codes["white"])

        print(f"{color_code}[{timestamp}] {icon} {title}{reset}")
        if message:
            print(f"  {message}\n")

    def _analyze_context(self) -> bool:
        """Analyze current context and make recommendations.

        Returns:
            True if context changed
        """
        # Get changed files
        changed_files = self._get_changed_files()

        if not changed_files:
            return False

        # Analyze context
        context = self.intelligent_agent.analyze_context(changed_files)

        # Get recommendations
        recommendations = self.intelligent_agent.get_recommendations()

        # Check if recommendations changed significantly
        if self._recommendations_changed(recommendations):
            self.last_recommendations = recommendations
            self.recommendations_made += 1

            # Show recommendations
            self._show_recommendations(recommendations, context)

            # Auto-activate if enabled
            if self.auto_activate:
                self._handle_auto_activation(recommendations)

            return True

        return False

    def _recommendations_changed(self, new_recs: List[AgentRecommendation]) -> bool:
        """Check if recommendations changed significantly.

        Args:
            new_recs: New recommendations

        Returns:
            True if changed
        """
        if not self.last_recommendations:
            return bool(new_recs)

        # Get agent names
        old_agents = {r.agent_name for r in self.last_recommendations}
        new_agents = {r.agent_name for r in new_recs}

        # Check if different
        return old_agents != new_agents

    def _show_recommendations(
        self, recommendations: List[AgentRecommendation], context: Any
    ) -> None:
        """Display recommendations.

        Args:
            recommendations: List of recommendations
            context: Session context
        """
        if not recommendations:
            self._print_notification(
                "💤",
                "No recommendations",
                "Current context doesn't warrant any suggestions",
                "dim",
            )
            return

        # Context summary
        contexts = []
        if context.has_frontend:
            contexts.append("Frontend")
        if context.has_backend:
            contexts.append("Backend")
        if context.has_database:
            contexts.append("Database")
        if context.has_tests:
            contexts.append("Tests")
        if context.has_auth:
            contexts.append("Auth")
        if context.has_api:
            contexts.append("API")

        context_str = ", ".join(contexts) if contexts else "General"

        self._print_notification(
            "🔍",
            f"Context detected: {context_str}",
            f"{len(context.files_changed)} files changed",
            "cyan",
        )

        # Show top recommendations
        high_confidence = [
            r for r in recommendations if r.confidence >= self.notification_threshold
        ]

        if high_confidence:
            print(f"  💡 Recommendations:\n")
            for rec in high_confidence[:5]:
                # Urgency icon
                urgency_icons = {
                    "critical": "🔴",
                    "high": "🟡",
                    "medium": "🔵",
                    "low": "⚪",
                }
                icon = urgency_icons.get(rec.urgency, "⚪")

                # Auto badge
                auto_badge = " [AUTO]" if rec.auto_activate else ""

                print(f"     {icon} {rec.agent_name}{auto_badge}")
                print(f"        {rec.confidence * 100:.0f}% - {rec.reason}")

            print()

    def _handle_auto_activation(
        self, recommendations: List[AgentRecommendation]
    ) -> None:
        """Handle auto-activation of agents.

        Args:
            recommendations: List of recommendations
        """
        auto_agents = [
            r.agent_name
            for r in recommendations
            if r.auto_activate and r.agent_name not in self.activated_agents
        ]

        if not auto_agents:
            return

        self._print_notification(
            "⚡", f"Auto-activating {len(auto_agents)} agents...", "", "green"
        )

        for agent_name in auto_agents:
            try:
                exit_code, message = agent_activate(agent_name)
                if exit_code == 0:
                    self.activated_agents.add(agent_name)
                    self.auto_activations += 1
                    print(f"     ✓ {agent_name}")
                else:
                    print(f"     ✗ {agent_name}: Failed")
            except Exception as e:
                print(f"     ✗ {agent_name}: {str(e)}")

        print()

    def _check_for_changes(self) -> None:
        """Check for changes and analyze context."""
        with self._state_lock:
            self.checks_performed += 1

        # Check git HEAD changes (commits)
        current_head = self._get_git_head()
        if current_head != self.last_git_head:
            self._print_notification(
                "📝",
                "Git commit detected",
                f"HEAD: {current_head[:8] if current_head else 'unknown'}",
                "yellow",
            )
            self.last_git_head = current_head

        # Analyze context
        self._analyze_context()

    def _print_statistics(self) -> None:
        """Print watch mode statistics."""
        duration = datetime.now() - self.start_time
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)

        print("\n" + "─" * 70)
        print("📊 WATCH MODE STATISTICS")
        print("─" * 70)
        print(f"  Duration: {hours}h {minutes}m")
        print(f"  Checks performed: {self.checks_performed}")
        print(f"  Recommendations: {self.recommendations_made}")
        print(f"  Auto-activations: {self.auto_activations}")
        print(f"  Agents activated: {len(self.activated_agents)}")
        if self.activated_agents:
            print(f"    {', '.join(sorted(self.activated_agents))}")
        print("─" * 70 + "\n")

    def run(self) -> int:
        """Run watch mode.

        Returns:
            Exit code
        """
        # Set running state FIRST so TUI can see it immediately
        with self._state_lock:
            self.running = True

        # Setup signal handlers
        def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Print banner
        self._print_banner()

        # Initial analysis
        self._print_notification("🚀", "Performing initial analysis...", "", "cyan")
        self._analyze_context()

        # Main loop (running is already True)

        try:
            while True:
                with self._state_lock:
                    if not self.running:
                        break
                time.sleep(self.check_interval)
                self._check_for_changes()

        except KeyboardInterrupt:
            pass

        finally:
            # Cleanup
            self._print_notification("🛑", "Watch mode stopped", "", "yellow")
            self._print_statistics()

        return 0


def watch_main(
    auto_activate: bool = True,
    threshold: float = 0.7,
    interval: float = 2.0,
) -> int:
    """Main entry point for watch mode.

    Args:
        auto_activate: Enable auto-activation
        threshold: Confidence threshold for notifications
        interval: Check interval in seconds

    Returns:
        Exit code
    """
    watcher = WatchMode(
        auto_activate=auto_activate,
        notification_threshold=threshold,
        check_interval=interval,
    )

    return watcher.run()
