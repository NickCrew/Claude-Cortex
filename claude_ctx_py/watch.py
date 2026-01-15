"""Watch mode for real-time AI recommendations and auto-activation.

Monitors file changes and provides intelligent recommendations in real-time.
"""

from __future__ import annotations

import errno
import json
import os
import time
import subprocess
import signal
import sys
import threading
from pathlib import Path
from types import FrameType
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Iterable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

from .intelligence import IntelligentAgent, AgentRecommendation
from .launcher import DEFAULT_CONFIG_PATH
from .core import _resolve_claude_dir, _resolve_cortex_root, agent_activate


WATCH_DAEMON_ENV = "CORTEX_WATCH_DAEMON"
WATCH_PID_ENV = "CORTEX_WATCH_PID_PATH"
WATCH_LOG_ENV = "CORTEX_WATCH_LOG_PATH"
WATCH_LOG_DIRNAME = "logs"
WATCH_LOG_FILENAME = "watch.log"
WATCH_PID_FILENAME = "watch.pid"


@dataclass
class WatchDefaults:
    """Resolved watch mode defaults from config."""

    directories: Optional[List[Path]] = None
    auto_activate: Optional[bool] = None
    threshold: Optional[float] = None
    interval: Optional[float] = None
    warnings: List[str] = field(default_factory=list)


def _read_config(path: Path) -> tuple[Dict[str, Any], List[str]]:
    """Read cortex-config.json safely."""
    warnings: List[str] = []
    if not path.exists():
        return {}, warnings
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"Invalid JSON in {path}: {exc}")
        return {}, warnings
    if not isinstance(data, dict):
        warnings.append(f"Config {path} must be a JSON object.")
        return {}, warnings
    return data, warnings


def _parse_directory_list(value: Any, warnings: List[str]) -> Optional[List[Path]]:
    if value is None:
        return None
    entries: List[str] = []
    if isinstance(value, str):
        entries = [part.strip() for part in value.split(",") if part.strip()]
    elif isinstance(value, list):
        entries = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    else:
        warnings.append("Watch directories must be a list of strings or comma-separated string.")
        return None

    resolved: List[Path] = []
    seen: Set[Path] = set()
    invalid: List[str] = []
    for entry in entries:
        candidate = Path(os.path.expanduser(entry)).resolve(strict=False)
        if candidate in seen:
            continue
        seen.add(candidate)
        if not candidate.exists() or not candidate.is_dir():
            invalid.append(str(candidate))
            continue
        resolved.append(candidate)

    if invalid:
        warnings.append("Invalid watch directories in config: " + ", ".join(invalid))

    return resolved or None


def _parse_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return None


def _parse_float(value: Any, label: str, warnings: List[str]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            warnings.append(f"Invalid {label} value in config: {value}")
            return None
    warnings.append(f"Invalid {label} value in config: {value}")
    return None


def load_watch_defaults(config_path: Optional[Path] = None) -> WatchDefaults:
    """Load watch defaults from cortex-config.json."""
    path = config_path or DEFAULT_CONFIG_PATH
    config, warnings = _read_config(path)
    watch_config = config.get("watch")

    if watch_config is None:
        return WatchDefaults(warnings=warnings)
    if not isinstance(watch_config, dict):
        warnings.append("Config 'watch' must be a JSON object.")
        return WatchDefaults(warnings=warnings)

    directories = _parse_directory_list(
        watch_config.get("directories") or watch_config.get("dirs"),
        warnings,
    )
    auto_activate = _parse_bool(watch_config.get("auto_activate"))
    threshold = _parse_float(watch_config.get("threshold"), "threshold", warnings)
    interval = _parse_float(watch_config.get("interval"), "interval", warnings)

    if threshold is not None and not 0.0 <= threshold <= 1.0:
        warnings.append("Watch threshold must be between 0.0 and 1.0.")
        threshold = None
    if interval is not None and interval <= 0:
        warnings.append("Watch interval must be greater than 0.")
        interval = None

    return WatchDefaults(
        directories=directories,
        auto_activate=auto_activate,
        threshold=threshold,
        interval=interval,
        warnings=warnings,
    )


def _default_watch_pid_path() -> Path:
    return _resolve_cortex_root() / WATCH_PID_FILENAME


def _default_watch_log_path() -> Path:
    return _resolve_cortex_root() / WATCH_LOG_DIRNAME / WATCH_LOG_FILENAME


def _read_pid(path: Path) -> Optional[int]:
    try:
        raw = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw:
        return None
    try:
        pid = int(raw)
    except ValueError:
        return None
    return pid if pid > 0 else None


def _write_pid(path: Path, pid: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(pid), encoding="utf-8")


def _remove_pid(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def _is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        return True


def _cleanup_daemon_pid() -> None:
    pid_path_str = os.environ.get(WATCH_PID_ENV)
    if not pid_path_str:
        return
    pid_path = Path(pid_path_str)
    current_pid = os.getpid()
    recorded = _read_pid(pid_path)
    if recorded == current_pid:
        _remove_pid(pid_path)


def watch_daemon_status(pid_path: Optional[Path] = None) -> tuple[int, str]:
    path = pid_path or _default_watch_pid_path()
    pid = _read_pid(path)
    if not pid:
        return 1, "Watch daemon not running."
    if _is_process_running(pid):
        return 0, f"Watch daemon running (pid {pid})."
    _remove_pid(path)
    return 1, f"Watch daemon not running (stale pid {pid})."


def stop_watch_daemon(pid_path: Optional[Path] = None) -> tuple[int, str]:
    path = pid_path or _default_watch_pid_path()
    pid = _read_pid(path)
    if not pid:
        return 1, "No watch daemon PID file found."
    if not _is_process_running(pid):
        _remove_pid(path)
        return 1, f"Watch daemon not running (stale pid {pid})."
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        return 1, f"Failed to stop watch daemon (pid {pid}): {exc}."

    for _ in range(30):
        if not _is_process_running(pid):
            _remove_pid(path)
            return 0, "Watch daemon stopped."
        time.sleep(0.2)

    return 1, f"Watch daemon did not stop (pid {pid})."


def start_watch_daemon(
    *,
    auto_activate: bool,
    threshold: float,
    interval: float,
    directories: Optional[List[Path]] = None,
    pid_path: Optional[Path] = None,
    log_path: Optional[Path] = None,
) -> tuple[int, str]:
    if os.environ.get(WATCH_DAEMON_ENV) == "1":
        return 1, "Already running inside watch daemon environment."

    pid_path = pid_path or _default_watch_pid_path()
    log_path = log_path or _default_watch_log_path()

    existing_pid = _read_pid(pid_path)
    if existing_pid and _is_process_running(existing_pid):
        return 1, f"Watch daemon already running (pid {existing_pid})."

    _remove_pid(pid_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    args = [sys.executable, "-m", "claude_ctx_py.cli", "ai", "watch"]
    if not auto_activate:
        args.append("--no-auto-activate")
    args.extend(["--threshold", str(threshold)])
    args.extend(["--interval", str(interval)])
    if directories:
        for directory in directories:
            args.extend(["--dir", str(directory)])

    env = os.environ.copy()
    env[WATCH_DAEMON_ENV] = "1"
    env[WATCH_PID_ENV] = str(pid_path)
    env[WATCH_LOG_ENV] = str(log_path)

    with log_path.open("a", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            args,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.DEVNULL,
            env=env,
            start_new_session=True,
        )

    _write_pid(pid_path, process.pid)
    return 0, f"Watch daemon started (pid {process.pid}). Logs: {log_path}"


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
        self.directories: List[Path] = [Path.cwd()]
        self.directory = self.directories[0]
        self.last_check_time = time.time()
        self.last_git_heads: Dict[Path, Optional[str]] = {}
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
        self._refresh_git_heads()

    def stop(self) -> None:
        """Stop watch mode gracefully."""
        with self._state_lock:
            self.running = False

    def _normalize_directories(self, directories: Iterable[Path]) -> List[Path]:
        """Normalize and de-duplicate directories."""
        seen: Set[Path] = set()
        normalized: List[Path] = []
        for directory in directories:
            resolved = Path(os.path.expanduser(str(directory))).resolve(strict=False)
            if resolved in seen:
                continue
            seen.add(resolved)
            normalized.append(resolved)
        return normalized

    def _refresh_git_heads(self) -> None:
        """Refresh git head snapshots for all watched directories."""
        self.last_git_heads = {
            directory: self._get_git_head(directory) for directory in self.directories
        }

    def set_directories(self, directories: List[Path]) -> None:
        """Set the directories to watch.

        Args:
            directories: Directory paths to watch
        """
        with self._state_lock:
            normalized = self._normalize_directories(directories)
            if not normalized:
                normalized = [Path.cwd().resolve()]
            self.directories = normalized
            self.directory = normalized[0]
            self._refresh_git_heads()

    def set_directory(self, directory: Path) -> None:
        """Set the directory to watch.

        Args:
            directory: Directory path to watch
        """
        self.set_directories([directory])

    def change_directory(self, directory: Path) -> None:
        """Change the watched directory.

        Args:
            directory: New directory path to watch
        """
        with self._state_lock:
            old_dir = os.getcwd()
            try:
                os.chdir(directory)
                self.directories = [directory]
                self.directory = directory
                self.last_git_heads = {directory: self._get_git_head(directory)}
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
                "directories": list(self.directories),
                "auto_activate": self.auto_activate,
                "threshold": self.notification_threshold,
                "interval": self.check_interval,
                "checks_performed": self.checks_performed,
                "recommendations_made": self.recommendations_made,
                "auto_activations": self.auto_activations,
                "started_at": self.start_time,
                "last_notification": self.notification_history[-1] if self.notification_history else None,
            }

    def _get_git_head(self, directory: Path) -> Optional[str]:
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
                cwd=str(directory),
            )
            return result.stdout.strip()
        except Exception:
            return None

    def _get_changed_files_for_directory(self, directory: Path) -> List[Path]:
        """Get list of changed files from git for a directory."""
        try:
            # Get unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(directory),
            )

            # Get staged changes
            staged = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                check=True,
                cwd=str(directory),
            )

            all_files = set(result.stdout.split("\n") + staged.stdout.split("\n"))
            return [
                (directory / f).resolve()
                for f in all_files
                if f.strip()
            ]

        except Exception:
            return []

    def _get_changed_files(self) -> List[Path]:
        """Get list of changed files from git.

        Returns:
            List of changed file paths
        """
        files: List[Path] = []
        seen: Set[Path] = set()
        with self._state_lock:
            directories = list(self.directories)
        for directory in directories:
            for file_path in self._get_changed_files_for_directory(directory):
                if file_path in seen:
                    continue
                seen.add(file_path)
                files.append(file_path)
        return files

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
        if len(self.directories) == 1:
            print(f"    • Directory: {self.directories[0]}")
        else:
            print("    • Directories:")
            for directory in self.directories:
                print(f"      - {directory}")
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
        with self._state_lock:
            directories = list(self.directories)
        for directory in directories:
            current_head = self._get_git_head(directory)
            with self._state_lock:
                previous_head = self.last_git_heads.get(directory)
            if current_head != previous_head:
                head_display = current_head[:8] if current_head else "unknown"
                self._print_notification(
                    "📝",
                    "Git commit detected",
                    f"{directory}: HEAD {head_display}",
                    "yellow",
                )
                with self._state_lock:
                    self.last_git_heads[directory] = current_head

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
            _cleanup_daemon_pid()

        return 0


def watch_main(
    auto_activate: bool = True,
    threshold: float = 0.7,
    interval: float = 2.0,
    directories: Optional[List[Path]] = None,
) -> int:
    """Main entry point for watch mode.

    Args:
        auto_activate: Enable auto-activation
        threshold: Confidence threshold for notifications
        interval: Check interval in seconds
        directories: Optional list of directories to watch

    Returns:
        Exit code
    """
    watcher = WatchMode(
        auto_activate=auto_activate,
        notification_threshold=threshold,
        check_interval=interval,
    )
    if directories:
        watcher.set_directories(directories)

    return watcher.run()
