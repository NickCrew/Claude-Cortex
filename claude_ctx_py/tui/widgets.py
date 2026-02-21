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
    "export": [
        ShortcutDef("f", "Format", priority=20),
        ShortcutDef("e", "Export", priority=21),
        ShortcutDef("x", "Copy", priority=22),
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
    "settings": [
        ShortcutDef("i", "Install", priority=20),
        ShortcutDef("u", "Uninstall", priority=21),
        ShortcutDef("U", "Sync All", priority=22),
        ShortcutDef("Enter", "View", priority=23),
        ShortcutDef("^e", "Edit", priority=24),
    ],
}

# Additional nav shortcuts (lower priority, shown if space)
EXTRA_NAV_SHORTCUTS: List[ShortcutDef] = [
    ShortcutDef("6", "Tasks", priority=30),
    ShortcutDef("7", "Commands", priority=31),
    ShortcutDef("gg/G", "Top/Bottom", priority=32),
    ShortcutDef("^b/^f", "Page", priority=33),
    ShortcutDef("^u/^d", "Half Page", priority=34),
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

    Automatically selects the best footer style and height based on terminal width.
    Expands to 2-3 rows on small screens to show all shortcuts.
    """

    DEFAULT_CSS = """
    AdaptiveFooter {
        dock: bottom;
        height: auto;
        max-height: 3;
        background: $surface-lighten-2;
        color: $text-muted;
        padding: 0 1;
    }
    """

    current_view: reactive[str] = reactive("overview")
    _compact_threshold: int = 80
    _multirow_threshold: int = 60

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
            "overview": [("^p", "Palette")],
            "agents": [("s", "Details"), ("v", "Validate"), ("^e", "Edit")],
            "rules": [("Spc", "Toggle"), ("^e", "Edit")],
            "skills": [("s", "Details"), ("v", "Validate"), ("m", "Metrics")],
            "mcp": [("B", "Browse/Install"), ("^t", "Test"), ("D", "Diagnose"), ("^a", "Add")],
            "tasks": [("a", "Add"), ("L", "Log"), ("O", "Open"), ("K", "LLM Tasks")],
            "commands": [("Enter", "View"), ("^e", "Edit")],
            "export": [("f", "Format"), ("e", "Export"), ("x", "Copy")],
            "worktrees": [
                ("^n", "New"),
                ("^o", "Open"),
                ("^w", "Remove"),
                ("^k", "Prune"),
                ("B", "Base Dir"),
            ],
            "ai_assistant": [("a", "Auto-Activate"), ("J", "Gemini"), ("Y", "Reviews")],
            "watch_mode": [("Spc", "Toggle")],
            "assets": [("i", "Install"), ("u", "Uninstall"), ("U", "Update All"), ("I", "Install All")],
            "memory": [("Enter", "View"), ("O", "Open"), ("D", "Delete")],
            "settings": [("i", "Install"), ("u", "Uninstall"), ("U", "Sync All"), ("Enter", "View"), ("^e", "Edit")],
        }
        return mapping.get(view, [])

    def render(self) -> RenderableType:
        """Render the adaptive footer with multi-line support on small screens."""
        from rich.table import Table

        width = self.size.width

        if width <= 0:
            return Text("")

        # Ultra-compact for very narrow terminals (single line, essentials only)
        if width < 40:
            return Text(" [bold reverse] ? [/] Help  [bold reverse] q [/] Quit")

        # Compact mode for small screens (single line, minimal)
        if width < 50:
            return Text(
                " [bold reverse] ? [/]Help "
                "[bold reverse] q [/]Quit "
                "[bold reverse] 1-7 [/]Nav "
                "[bold reverse] 0 [/]Dash"
            )

        # Multi-row mode for 50-80 width
        if width < self._multirow_threshold:
            return self._render_multirow(width)

        # Full responsive footer for wide terminals
        return self._render_full(width)

    def _render_multirow(self, width: int) -> Text:
        """Render footer in multiple rows for better space usage."""
        lines: List[Text] = []

        # Row 1: Navigation + Essential actions
        row1 = Text(" ")
        essentials = [("?", "Help"), ("q", "Quit")]
        nav = ("1-7,0,C,E,w,A,M,F", "Views")

        for key, label in essentials + [nav]:
            row1.append_text(self._format_shortcut(key, label))
            row1.append(" ")

        lines.append(row1)

        # Row 2: View-specific + common actions
        row2 = Text(" ")
        actions = [("Spc", "Toggle"), ("r", "Refresh")]
        view_shortcuts = self._get_view_shortcuts(self.current_view)

        for key, label in actions + view_shortcuts:
            if len(row2.plain) + len(key) + len(label) + 6 > width:
                break
            row2.append_text(self._format_shortcut(key, label))
            row2.append(" ")

        lines.append(row2)

        # Combine lines with newlines
        result = Text()
        for i, line in enumerate(lines):
            result.append_text(line)
            if i < len(lines) - 1:
                result.append("\n")

        return result

    def _render_full(self, width: int) -> Text:
        """Render full responsive footer for wide terminals."""
        result = Text()
        used = 0

        # Essential shortcuts (always show)
        essentials = [("?", "Help"), ("q", "Quit")]

        # Navigation hint
        nav = ("1-7,0,C,E,w,A,M,F", "Views")

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


class QuickNav(Widget):
    """Header bar showing view navigation with labeled shortcuts.

    Shows all available views with their key bindings and labels.
    Current view is highlighted. Includes essential shortcuts (Help, Quit).
    """

    DEFAULT_CSS = """
    QuickNav {
        dock: top;
        height: auto;
        max-height: 2;
        background: $primary;
        color: $text;
        padding: 0 1;
        border-bottom: solid $accent;
    }
    """

    current_view: reactive[str] = reactive("overview")
    visible: reactive[bool] = reactive(True)

    # Map view names to (key, label) tuples
    VIEW_INFO = {
        "overview": ("1", "Overview"),
        "agents": ("2", "Agents"),
        "rules": ("3", "Rules"),
        "skills": ("4", "Skills"),
        "worktrees": ("C", "Worktrees"),
        "tasks": ("5", "Tasks"),
        "commands": ("6", "Commands"),
        "mcp": ("7", "MCP"),
        "export": ("E", "Export"),
        "ai_assistant": ("0", "Assistant"),
        "watch_mode": ("w", "Watch"),
        "assets": ("A", "Assets"),
        "memory": ("M", "Memory"),
        "codex_skills": ("X", "Codex"),
        "settings": ("F", "Settings"),
    }

    def render(self) -> RenderableType:
        """Render quick navigation header with view labels."""
        if not self.visible:
            return Text("")

        width = self.size.width
        if width <= 0:
            return Text("")

        # For very narrow terminals, show compact view
        if width < 80:
            return self._render_compact()

        # Build full nav bar
        result = Text()
        result.append("Views: ", style="dim")

        # Add view shortcuts with labels
        for view_name in [
            "overview", "agents", "rules", "skills", "worktrees",
            "tasks", "commands", "mcp", "export", "ai_assistant",
            "watch_mode", "assets", "memory", "codex_skills", "settings"
        ]:
            if view_name not in self.VIEW_INFO:
                continue

            key, label = self.VIEW_INFO[view_name]
            is_current = view_name == self.current_view

            # Format: [KEY]Label or [KEY] Label
            if is_current:
                result.append(f"[{key}]", style="bold reverse")
                result.append(f"{label}", style="bold reverse")
            else:
                result.append(f"[{key}]", style="")
                result.append(f"{label}", style="dim")

            result.append("  ")

        # Add separator and essential shortcuts
        result.append("│ ", style="dim")
        result.append("[?]", style="bold reverse")
        result.append("Help ", style="")
        result.append("[q]", style="bold reverse")
        result.append("Quit", style="")

        return result

    def _render_compact(self) -> Text:
        """Render compact version for narrow terminals (< 80 chars)."""
        result = Text()

        # Show current view prominently with label
        if self.current_view in self.VIEW_INFO:
            key, label = self.VIEW_INFO[self.current_view]
            result.append(f"Current: [{key}]{label} ", style="bold")

        # Quick nav hint
        result.append("│ ", style="dim")
        result.append("[1-7,0,C,E,w,A,M,X,F]", style="dim")
        result.append("Views ", style="dim")

        # Essential shortcuts
        result.append("[?]", style="bold reverse")
        result.append("Help ", style="")
        result.append("[q]", style="bold reverse")
        result.append("Quit", style="")

        return result

    def update_view(self, view: str) -> None:
        """Update the current view context."""
        self.current_view = view

    def watch_current_view(self, view: str) -> None:
        """React to view changes."""
        self.refresh()

    def toggle_visibility(self) -> None:
        """Toggle header visibility."""
        self.visible = not self.visible
        self.refresh()

    def on_resize(self, event: events.Resize) -> None:
        """Refresh when terminal is resized."""
        self.refresh()
