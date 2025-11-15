"""Toast notification system for TUI."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any, Literal
from .tui_icons import Icons


NotificationType = Literal["success", "error", "info", "warning"]


class Toast:
    """Temporary notification system."""

    def __init__(self) -> None:
        """Initialize toast notification manager."""
        self.notifications: List[Dict[str, Any]] = []

    def success(self, message: str, duration: int = 3) -> None:
        """Show success notification.

        Args:
            message: Notification message
            duration: Duration in seconds
        """
        self._add_notification("success", message, duration)

    def error(self, message: str, duration: int = 5) -> None:
        """Show error notification.

        Args:
            message: Notification message
            duration: Duration in seconds
        """
        self._add_notification("error", message, duration)

    def info(self, message: str, duration: int = 3) -> None:
        """Show info notification.

        Args:
            message: Notification message
            duration: Duration in seconds
        """
        self._add_notification("info", message, duration)

    def warning(self, message: str, duration: int = 4) -> None:
        """Show warning notification.

        Args:
            message: Notification message
            duration: Duration in seconds
        """
        self._add_notification("warning", message, duration)

    def _add_notification(
        self, notif_type: NotificationType, message: str, duration: int
    ) -> None:
        """Add a notification to the queue.

        Args:
            notif_type: Type of notification
            message: Notification message
            duration: Duration in seconds
        """
        self.notifications.append(
            {
                "type": notif_type,
                "message": message,
                "created": datetime.now(),
                "expires": datetime.now() + timedelta(seconds=duration),
            }
        )

    def render(self, max_notifications: int = 3) -> List[str]:
        """Render active notifications as formatted strings.

        Args:
            max_notifications: Maximum number of notifications to show

        Returns:
            List of formatted notification strings
        """
        now = datetime.now()

        # Remove expired notifications
        self.notifications = [n for n in self.notifications if n["expires"] > now]

        # Render active notifications (most recent first)
        active = self.notifications[-max_notifications:]
        rendered = []

        for notif in active:
            formatted = self._format_notification(notif)
            rendered.append(formatted)

        return rendered

    def _format_notification(self, notif: Dict[str, Any]) -> str:
        """Format a single notification.

        Args:
            notif: Notification dictionary

        Returns:
            Formatted notification string
        """
        icon_map = {
            "success": (Icons.SUCCESS, "green"),
            "error": (Icons.ERROR, "red"),
            "info": (Icons.INFO, "blue"),
            "warning": (Icons.WARNING, "yellow"),
        }

        icon, color = icon_map.get(notif["type"], (Icons.INFO, "blue"))
        message = notif["message"]

        return f"[{color}]{icon}[/{color}] {message}"

    def has_active(self) -> bool:
        """Check if there are active notifications.

        Returns:
            True if there are active notifications
        """
        now = datetime.now()
        self.notifications = [n for n in self.notifications if n["expires"] > now]
        return len(self.notifications) > 0

    def clear(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()

    def count(self) -> int:
        """Get count of active notifications.

        Returns:
            Number of active notifications
        """
        now = datetime.now()
        self.notifications = [n for n in self.notifications if n["expires"] > now]
        return len(self.notifications)


class StatusMessage:
    """Persistent status message display."""

    def __init__(self) -> None:
        """Initialize status message manager."""
        self._message = ""
        self._message_type: NotificationType = "info"
        self._updated = datetime.now()

    def set(self, message: str, message_type: NotificationType = "info") -> None:
        """Set the status message.

        Args:
            message: Status message
            message_type: Type of message
        """
        self._message = message
        self._message_type = message_type
        self._updated = datetime.now()

    def clear(self) -> None:
        """Clear the status message."""
        self._message = ""
        self._updated = datetime.now()

    def get(self) -> str:
        """Get the formatted status message.

        Returns:
            Formatted status message string
        """
        if not self._message:
            return ""

        icon_map = {
            "success": (Icons.SUCCESS, "green"),
            "error": (Icons.ERROR, "red"),
            "info": (Icons.INFO, "blue"),
            "warning": (Icons.WARNING, "yellow"),
        }

        icon, color = icon_map.get(self._message_type, (Icons.INFO, "blue"))
        return f"[{color}]{icon}[/{color}] {self._message}"

    def has_message(self) -> bool:
        """Check if there is an active status message.

        Returns:
            True if there is a status message
        """
        return bool(self._message)

    def age(self) -> float:
        """Get age of current message in seconds.

        Returns:
            Age of message in seconds
        """
        return (datetime.now() - self._updated).total_seconds()
