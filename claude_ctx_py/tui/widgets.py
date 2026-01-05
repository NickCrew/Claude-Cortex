"""Custom TUI widgets including responsive footer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from rich.console import RenderableType
from rich.text import Text
from textual import events
from textual.reactive import reactive
from textual.widget import Widget


@dataclass
class ShortcutDef:
    """Definition of a keyboard shortcut."""

    key: str
    label: str
    priority: int = 50  # Lower = higher priority (shown first)


# Shortcut definitions grouped by context
GLOBAL_SHORTCUTS: List[ShortcutDef] = [
    ShortcutDef("?", "Help", priority=1),
    ShortcutDef("q", "Quit", priority=2),
]

ACTION_SHORTCUTS: List[ShortcutDef] = [
    ShortcutDef("Space", "Toggle", priority=10),
    ShortcutDef("r", "Refresh", priority=11),
    ShortcutDef("^p", "Commands", priority=12),
]

# Compact view navigation - shown as a group
VIEW_NAV_SHORTCUT = ShortcutDef("1-0,A,M", "Views", priority=5)

# View-specific shortcuts
VIEW_SHORTCUTS: Dict[str, List[ShortcutDef]] = {
    "agents": [
        ShortcutDef("s", "Details", priority=20),
        ShortcutDef("v", "Validate", priority=21),
        ShortcutDef("^e", "Edit", priority=22),
    ],
    "skills": [
        ShortcutDef("s", "Details", priority=20),
        ShortcutDef("v", "Validate", priority=21),
        ShortcutDef("m", "Metrics", priority=22),
        ShortcutDef("d", "Docs", priority=23),
    ],
    "mcp": [
        ShortcutDef("B", "Browse/Install", priority=19),
        ShortcutDef("^t", "Test", priority=20),
        ShortcutDef("D", "Diagnose", priority=21),
        ShortcutDef("^a", "Add", priority=22),
        ShortcutDef("E", "Edit", priority=23),
        ShortcutDef("X", "Remove", priority=24),
    ],
    "profiles": [
        ShortcutDef("n", "Save", priority=20),
        ShortcutDef("D", "Delete", priority=21),
    ],
    "export": [
        ShortcutDef("f", "Format", priority=20),
        ShortcutDef("e", "Export", priority=21),
        ShortcutDef("x", "Copy", priority=22),
    ],
    "workflows": [
        ShortcutDef("R", "Run", priority=20),
        ShortcutDef("s", "Stop", priority=21),
    ],
    "scenarios": [
        ShortcutDef("R", "Run", priority=20),
        ShortcutDef("s", "Stop", priority=21),
        ShortcutDef("P", "Preview", priority=22),
        ShortcutDef("V", "Validate", priority=23),
    ],
    "tasks": [
        ShortcutDef("L", "Log", priority=20),
        ShortcutDef("O", "Open", priority=21),
    ],
    "assets": [
        ShortcutDef("i", "Install", priority=20),
        ShortcutDef("u", "Uninstall", priority=21),
        ShortcutDef("U", "Update All", priority=22),
        ShortcutDef("I", "Install All", priority=23),
        ShortcutDef("T", "Target", priority=24),
        ShortcutDef("d", "Diff", priority=25),
    ],
    "rules": [
        ShortcutDef("^e", "Edit", priority=20),
    ],
    "modes": [
        ShortcutDef("^e", "Edit", priority=20),
    ],
    "memory": [
        ShortcutDef("Enter", "View", priority=20),
        ShortcutDef("O", "Open", priority=21),
        ShortcutDef("D", "Delete", priority=22),
    ],
    "ai_assistant": [
        ShortcutDef("a", "Auto-Activate", priority=20),
        ShortcutDef("J", "Gemini", priority=21),
        ShortcutDef("K", "Assign LLMs", priority=22),
        ShortcutDef("Y", "Request Reviews", priority=23),
    ],
    "commands": [
        ShortcutDef("Enter", "View", priority=20),
        ShortcutDef("^e", "Edit", priority=21),
    ],
}

# Additional nav shortcuts (lower priority, shown if space)
EXTRA_NAV_SHORTCUTS: List[ShortcutDef] = [
    ShortcutDef("S", "Scenarios", priority=30),
    ShortcutDef("o", "Orchestrate", priority=31),
    ShortcutDef("Alt+g", "Galaxy", priority=32),
    ShortcutDef("t", "Tasks", priority=33),
    ShortcutDef("/", "Cmds", priority=34),
    ShortcutDef("gg/G", "Top/Bottom", priority=35),
    ShortcutDef("^b/^f", "Page", priority=36),
    ShortcutDef("^u/^d", "Half Page", priority=37),
]


class ResponsiveFooter(Widget):
    """A responsive footer that adapts to terminal width.

    Shows shortcuts in priority order, truncating gracefully when space is limited.
    Context-aware: shows relevant shortcuts for the current view.
    """

    DEFAULT_CSS = """
    ResponsiveFooter {
        dock: bottom;
        height: 1;
        background: $surface-lighten-2;
    }
    """

    current_view: reactive[str] = reactive("overview")

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ) -> None:
        """Initialize the responsive footer."""
        super().__init__(name=name, id=id, classes=classes)
        self._key_style = "bold reverse"
        self._label_style = "dim"
        self._separator = " "
        self._more_indicator = " [dim]?=more[/]"

    def _format_shortcut(self, shortcut: ShortcutDef) -> Text:
        """Format a single shortcut for display."""
        text = Text()
        text.append(f" {shortcut.key} ", style=self._key_style)
        text.append(f"{shortcut.label}", style=self._label_style)
        return text

    def _get_shortcuts_for_view(self, view: str) -> List[ShortcutDef]:
        """Get all applicable shortcuts for a view, sorted by priority."""
        shortcuts: List[ShortcutDef] = []

        # Global shortcuts (always)
        shortcuts.extend(GLOBAL_SHORTCUTS)

        # View navigation (compact)
        shortcuts.append(VIEW_NAV_SHORTCUT)

        # Action shortcuts
        shortcuts.extend(ACTION_SHORTCUTS)

        # View-specific shortcuts
        if view in VIEW_SHORTCUTS:
            shortcuts.extend(VIEW_SHORTCUTS[view])

        # Extra navigation (if space)
        shortcuts.extend(EXTRA_NAV_SHORTCUTS)

        # Sort by priority
        return sorted(shortcuts, key=lambda s: s.priority)

    def _shortcut_width(self, shortcut: ShortcutDef) -> int:
        """Calculate the display width of a shortcut."""
        # Format: " KEY LABEL " + separator
        return len(shortcut.key) + len(shortcut.label) + 4

    def render(self) -> RenderableType:
        """Render the footer with responsive shortcut display."""
        width = self.size.width
        if width <= 0:
            return Text("")

        shortcuts = self._get_shortcuts_for_view(self.current_view)

        result = Text()
        used_width = 0
        shown_count = 0
        more_width = len(" ?=more ")

        for shortcut in shortcuts:
            shortcut_width = self._shortcut_width(shortcut)
            remaining = width - used_width

            # Check if we have room for this shortcut
            # Reserve space for "?=more" indicator if not showing all
            need_more_indicator = shown_count < len(shortcuts) - 1
            min_remaining = shortcut_width + (more_width if need_more_indicator else 0)

            if remaining < min_remaining:
                # No more room - show indicator if we haven't shown everything
                if shown_count < len(shortcuts):
                    result.append(self._more_indicator)
                break

            # Add the shortcut
            if shown_count > 0:
                result.append(self._separator)
                used_width += len(self._separator)

            result.append_text(self._format_shortcut(shortcut))
            used_width += shortcut_width
            shown_count += 1

        return result

    def update_view(self, view: str) -> None:
        """Update the current view context."""
        self.current_view = view

    def watch_current_view(self, view: str) -> None:
        """React to view changes."""
        self.refresh()


class CompactFooter(Widget):
    """Ultra-compact footer for very narrow terminals.

    Shows only essential shortcuts in a minimal format.
    Falls back to this when width < 60 characters.
    """

    DEFAULT_CSS = """
    CompactFooter {
        dock: bottom;
        height: 1;
        background: $surface-lighten-2;
    }
    """

    current_view: reactive[str] = reactive("overview")

    def render(self) -> RenderableType:
        """Render ultra-compact footer."""
        width = self.size.width

        if width < 30:
            # Minimal: just help
            return Text(" [bold reverse] ? [/] Help")

        if width < 50:
            # Very compact
            return Text(
                " [bold reverse] ? [/]Help "
                "[bold reverse] q [/]Quit "
                "[bold reverse] 1-9 [/]Views"
            )

        # Compact with toggle
        return Text(
            " [bold reverse] ? [/]Help "
            "[bold reverse] q [/]Quit "
            "[bold reverse] Space [/]Toggle "
            "[bold reverse] 1-9 [/]Views"
        )


class AdaptiveFooter(Widget):
    """Adaptive footer that switches between responsive and compact modes.

    Automatically selects the best footer style based on terminal width.
    """

    DEFAULT_CSS = """
    AdaptiveFooter {
        dock: bottom;
        height: 1;
        background: $surface-lighten-2;
        color: $text-muted;
    }
    """

    current_view: reactive[str] = reactive("overview")
    _compact_threshold: int = 60

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
        compact_threshold: int = 60,
    ) -> None:
        """Initialize adaptive footer.

        Args:
            compact_threshold: Width below which to use ultra-compact mode
        """
        super().__init__(name=name, id=id, classes=classes)
        self._compact_threshold = compact_threshold
        self._key_style = "bold reverse"
        self._label_style = ""
        self._dim_style = "dim"

    def _format_shortcut(self, key: str, label: str) -> Text:
        """Format a single shortcut."""
        text = Text()
        text.append(f" {key} ", style=self._key_style)
        text.append(label, style=self._label_style)
        return text

    def _get_view_shortcuts(self, view: str) -> List[Tuple[str, str]]:
        """Get view-specific shortcuts as (key, label) tuples."""
        mapping = {
            "agents": [("s", "Details"), ("v", "Validate"), ("^e", "Edit")],
            "skills": [("s", "Details"), ("v", "Validate"), ("m", "Metrics"), ("d", "Docs")],
            "mcp": [("B", "Browse/Install"), ("^t", "Test"), ("D", "Diagnose"), ("^a", "Add")],
            "profiles": [("Spc", "Apply"), ("n", "Save"), ("D", "Delete")],
            "export": [("f", "Format"), ("e", "Export"), ("x", "Copy")],
            "workflows": [("R", "Run"), ("s", "Details")],
            "worktrees": [
                ("^n", "New"),
                ("^o", "Open"),
                ("^w", "Remove"),
                ("^k", "Prune"),
                ("B", "Base Dir"),
            ],
            "scenarios": [("R", "Run"), ("P", "Preview"), ("V", "Validate")],
            "tasks": [("a", "Add"), ("L", "Log"), ("O", "Open")],
            "assets": [("i", "Install"), ("u", "Uninstall"), ("U", "Update All"), ("I", "Install All")],
            "memory": [("Enter", "View"), ("O", "Open"), ("D", "Delete")],
            "modes": [("Spc", "Toggle"), ("^e", "Edit")],
            "rules": [("Spc", "Toggle"), ("^e", "Edit")],
            "principles": [
                ("Spc", "Toggle"),
                ("s", "Details"),
                ("c", "Build"),
                ("d", "Open"),
                ("^e", "Edit"),
            ],
            "ai_assistant": [("a", "Auto-Activate"), ("J", "Gemini"), ("Y", "Request Reviews")],
            "commands": [("Enter", "View"), ("^e", "Edit")],
        }
        return mapping.get(view, [])

    def render(self) -> RenderableType:
        """Render the adaptive footer."""
        width = self.size.width

        if width <= 0:
            return Text("")

        # Ultra-compact for very narrow terminals
        if width < 40:
            return Text(" [bold reverse] ? [/] Help  [bold reverse] q [/] Quit")

        if width < self._compact_threshold:
            return Text(
                " [bold reverse] ? [/]Help "
                "[bold reverse] q [/]Quit "
                "[bold reverse] Spc [/]Toggle "
                "[bold reverse] 1-9 [/]Nav"
            )

        # Build responsive footer
        result = Text()
        used = 0

        # Essential shortcuts (always show)
        essentials = [("?", "Help"), ("q", "Quit")]

        # Navigation hint
        nav = ("1-0,A,M", "Views")

        # Actions
        actions = [("Spc", "Toggle"), ("r", "Refresh")]

        # View-specific
        view_shortcuts = self._get_view_shortcuts(self.current_view)

        # Calculate what fits
        all_shortcuts = essentials + [nav] + actions + view_shortcuts

        for i, (key, label) in enumerate(all_shortcuts):
            shortcut_text = self._format_shortcut(key, label)
            shortcut_width = len(key) + len(label) + 4  # " KEY LABEL "

            # Reserve space for "?=more" if not last
            reserve = 8 if i < len(all_shortcuts) - 1 else 0

            if used + shortcut_width + reserve > width:
                # Add "more" indicator
                if used + 8 <= width:
                    result.append(" [dim]?=more[/]")
                break

            if used > 0:
                result.append(" ")
                used += 1

            result.append_text(shortcut_text)
            used += shortcut_width

        return result

    def update_view(self, view: str) -> None:
        """Update the current view context."""
        self.current_view = view

    def watch_current_view(self, view: str) -> None:
        """React to view changes."""
        self.refresh()

    def on_resize(self, event: events.Resize) -> None:
        """Refresh when terminal is resized."""
        self.refresh()
