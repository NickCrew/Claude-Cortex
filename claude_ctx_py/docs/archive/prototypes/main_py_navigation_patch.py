"""
Patch for claude_ctx_py/tui/main.py - Navigation Stack Integration

This file shows the exact code additions needed to integrate navigation providers.
Copy/paste these sections into main.py at the indicated line numbers.
"""

# ============================================================================
# SECTION 1: Imports (Add after line 138)
# ============================================================================
# Location: After "from ..tui_commands import AgentCommandProvider"

from ..tui_navigation_providers import (
    NavigationProvider,
    ViewNavigationProvider,
    ItemJumpProvider,
)


# ============================================================================
# SECTION 2: Command Registration (Replace line 325)
# ============================================================================
# Location: Line ~325, replace:
#   COMMANDS = {AgentCommandProvider}
# With:

COMMANDS = {
    AgentCommandProvider,
    NavigationProvider,      # Back/forward/recent views
    ViewNavigationProvider,  # Enhanced view switching
    ItemJumpProvider,        # Cross-view item search
}


# ============================================================================
# SECTION 3: Navigation State Variables (Add after line 327)
# ============================================================================
# Location: After "current_view: reactive[str] = reactive("agents")"

# Navigation stack for browser-like back/forward support
navigation_stack: list[str] = []
navigation_index: int = 0
_navigating_history: bool = False  # Flag to prevent stack updates during history nav


# ============================================================================
# SECTION 4: Keybindings (Add to BINDINGS list around line 250-320)
# ============================================================================
# Location: In the BINDINGS list, add these entries:

Binding("backspace", "navigate_back", "Back", priority=True, show=False),
Binding("left", "navigate_back_if_allowed", "Back", show=False),
Binding("right", "navigate_forward_if_allowed", "Forward", show=False),


# ============================================================================
# SECTION 5: Updated watch_current_view (Replace around line 500)
# ============================================================================
# Location: Replace the entire watch_current_view method

def watch_current_view(self, old_view: str, new_view: str) -> None:
    """Handle view changes and update navigation stack.

    Args:
        old_view: Previous view name
        new_view: New view name
    """
    # Update navigation stack (browser-like history)
    # Only add if this is a new navigation (not back/forward)
    if not self._navigating_history:
        # Truncate forward history when navigating to new view
        self.navigation_stack = self.navigation_stack[:self.navigation_index + 1]
        self.navigation_stack.append(new_view)
        self.navigation_index = len(self.navigation_stack) - 1

        # Limit stack size to prevent memory issues
        max_history = 50
        if len(self.navigation_stack) > max_history:
            overflow = len(self.navigation_stack) - max_history
            self.navigation_stack = self.navigation_stack[overflow:]
            self.navigation_index -= overflow

    # Existing view update logic
    self.update_view()
    footer = self.query_one(AdaptiveFooter)
    footer.update_view(new_view)
    self.refresh_status_bar()
    self.refresh(layout=True)


# ============================================================================
# SECTION 6: Navigation Helper Methods (Add anywhere after class definition)
# ============================================================================
# Location: Add these methods to the CtxTUI class (around line 4000+)

def navigate_back(self) -> None:
    """Navigate to previous view in history."""
    if self.navigation_index > 0:
        self._navigating_history = True
        self.navigation_index -= 1
        new_view = self.navigation_stack[self.navigation_index]
        self.current_view = new_view
        self._navigating_history = False
        from .tui_icons import Icons
        self.notify(f"{Icons.ARROW_LEFT} Back to {new_view}", severity="information")

def navigate_forward(self) -> None:
    """Navigate to next view in history."""
    if self.navigation_index < len(self.navigation_stack) - 1:
        self._navigating_history = True
        self.navigation_index += 1
        new_view = self.navigation_stack[self.navigation_index]
        self.current_view = new_view
        self._navigating_history = False
        from .tui_icons import Icons
        self.notify(f"Forward {Icons.ARROW_RIGHT} {new_view}", severity="information")

def can_go_back(self) -> bool:
    """Check if back navigation is available.

    Returns:
        True if there is navigation history to go back to
    """
    return self.navigation_index > 0

def can_go_forward(self) -> bool:
    """Check if forward navigation is available.

    Returns:
        True if there is forward navigation history
    """
    return self.navigation_index < len(self.navigation_stack) - 1

def select_item_by_name(self, item_name: str) -> None:
    """Select an item by name in the current view's DataTable.

    This enables cross-view navigation via the command palette.

    Args:
        item_name: Name of the item to select
    """
    try:
        table = self.query_one("#main-table", DataTable)

        # Search for the item in the table
        for row_idx, row_key in enumerate(table.rows):
            row_data = table.get_row(row_key)
            # First column typically contains the name
            if row_data and str(row_data[0]) == item_name:
                table.cursor_row = row_idx
                table.scroll_to_row(row_idx)
                self.notify(f"Selected {item_name}", severity="information")
                return

        # Item not found in current view
        self.notify(f"Item '{item_name}' not found in {self.current_view}", severity="warning")

    except Exception as e:
        self.notify(f"Error selecting item: {e}", severity="error")


# ============================================================================
# SECTION 7: Keybinding Actions (Add after other action methods)
# ============================================================================
# Location: Add these action methods (around line 4000+)

def action_navigate_back(self) -> None:
    """Navigate to previous view (Backspace key)."""
    if self.can_go_back():
        self.navigate_back()
    else:
        self.notify("No navigation history", severity="information")

def action_navigate_back_if_allowed(self) -> None:
    """Navigate back with left arrow (only if not in flags view).

    This prevents conflicts with horizontal navigation in flags explorer.
    """
    # Don't interfere with flags navigation
    if self.current_view not in ("flags", "flag_manager"):
        if self.can_go_back():
            self.navigate_back()

def action_navigate_forward_if_allowed(self) -> None:
    """Navigate forward with right arrow (only if not in flags view).

    This prevents conflicts with horizontal navigation in flags explorer.
    """
    # Don't interfere with flags navigation
    if self.current_view not in ("flags", "flag_manager"):
        if self.can_go_forward():
            self.navigate_forward()


# ============================================================================
# SECTION 8: Initialize Navigation Stack (Modify on_mount, line ~412)
# ============================================================================
# Location: In on_mount() method, add after performance_monitor initialization

def on_mount(self) -> None:
    """Load initial data when app starts."""
    # ... existing initialization code ...

    # Initialize performance monitor and command registry
    self.performance_monitor = PerformanceMonitor()
    self.command_registry = CommandRegistry()
    self.command_registry.register_batch(DEFAULT_COMMANDS)

    # NEW: Initialize navigation stack with current view
    self.navigation_stack = [self.current_view]
    self.navigation_index = 0
    self._navigating_history = False

    # ... rest of on_mount code ...


# ============================================================================
# OPTIONAL: Use Native Command Palette (Replace action_command_palette)
# ============================================================================
# Location: Line ~7023, replace or comment out:

# OPTION A: Comment out to use Textual's native palette (Ctrl+P auto-handled)
# def action_command_palette(self) -> None:
#     """Show the command palette."""
#     self.run_worker(self._open_command_palette(), exclusive=True)

# OPTION B: Add separate keybinding for native palette (keep custom as Ctrl+P)
def action_native_command_palette(self) -> None:
    """Show Textual's native command palette."""
    # Call parent class method to open native palette
    super().action_command_palette()

# Then add to BINDINGS:
# Binding("ctrl+shift+p", "native_command_palette", "Native Palette", show=False),


# ============================================================================
# SUMMARY OF CHANGES
# ============================================================================
"""
Changes Summary:
1. ✅ Import navigation providers (3 new imports)
2. ✅ Register providers in COMMANDS (add 3 providers)
3. ✅ Add navigation state variables (3 variables)
4. ✅ Add keybindings (3 bindings for back/forward)
5. ✅ Update watch_current_view (add stack management)
6. ✅ Add navigation methods (5 new methods)
7. ✅ Add keybinding actions (3 action methods)
8. ✅ Initialize navigation stack in on_mount (3 lines)

Total new code: ~150 lines
Total modified code: ~20 lines

Result: Full navigation stack + native command palette integration!
"""


# ============================================================================
# TESTING CHECKLIST
# ============================================================================
"""
After applying this patch, test:

1. ✅ Press Ctrl+P → Should open command palette (native or custom)
2. ✅ Type "back" → Should show back command if history exists
3. ✅ Navigate: 2 → 5 → 6 → Backspace → Should go back to view 5
4. ✅ Press → → Should go forward to view 6
5. ✅ Type "agent" in palette → Should show agents and individual agents
6. ✅ Type "recent" → Should show recently visited views
7. ✅ Search for skill name → Should jump to that skill when selected
8. ✅ Navigation stack limited to 50 entries (check after 60+ navigations)
"""
