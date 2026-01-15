# Skills TUI Integration Guide

## Quick Start

Follow these steps to integrate the Skills view into the TUI:

### Step 1: Verify Imports (Already Done ✅)

The following imports have been added to `tui.py`:

```python
from .core import (
    # ... existing imports ...
    list_skills,
    skill_info,
    skill_validate,
    skill_community_list,
    skill_community_search,
    _extract_front_matter,
)
from .metrics import (
    get_all_metrics,
    get_skill_metrics,
)
```

### Step 2: Add Methods to AgentTUI Class

1. Open `/Users/nferguson/Developer/personal/cortex-plugin/claude_ctx_py/tui.py`

2. Find the AgentTUI class (around line 187)

3. Find a good insertion point after existing methods (after `get_filtered_agents()` or similar)

4. Copy ALL methods from `skills_tui_methods.py` and paste them into the AgentTUI class:
   - `load_skills()`
   - `get_filtered_skills()`
   - `create_skills_table()`
   - `create_skills_details_panel()`
   - `create_skills_metrics_panel()`
   - `create_community_skills_table()`
   - `validate_selected_skill()`
   - `toggle_skills_view_mode()`
   - `handle_skills_key()`

### Step 3: Initialize Skills in run() Method

Find the `run()` method (around line 542) and add skill loading:

```python
def run(self) -> int:
    """Run the TUI main loop."""
    try:
        # Load agents initially
        self.load_agents()

        # ADD THIS LINE:
        self.load_skills()  # <-- Load skills on startup

        with Live(
            self.create_layout(),
            # ... rest of method
```

### Step 4: Update create_layout() Method

Find the `create_layout()` method (around line 440) and add skills view handling.

Look for where views are handled (probably in the body layout section). Add:

```python
def create_layout(self) -> Layout:
    """Create the main layout."""
    layout = Layout()

    # Create main sections
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    # Add content to sections
    layout["header"].update(self.create_header())
    layout["footer"].update(self.create_footer())

    # Body content based on current view
    if self.state.show_help:
        layout["body"].update(self.create_help_panel())

    # ADD THIS SECTION:
    elif self.state.current_view == "skills":
        if self.state.skills_view_mode == "metrics":
            # Split view with metrics panel
            layout["body"].split_row(
                Layout(Panel(self.create_skills_table(), title="Skills")),
                Layout(self.create_skills_metrics_panel(), ratio=1),
            )
        elif self.state.skills_view_mode == "details" or self.state.show_details:
            # Split view with details panel
            layout["body"].split_row(
                Layout(Panel(self.create_skills_table(), title="Skills")),
                Layout(self.create_skills_details_panel() or "", ratio=1),
            )
        elif self.state.skills_view_mode == "community":
            # Community browser
            layout["body"].update(
                Panel(self.create_community_skills_table(), title="Community Skills")
            )
        else:
            # Default: local skills list
            layout["body"].update(Panel(self.create_skills_table(), title="Skills"))

    # ... rest of existing view handling (agents, workflows, etc.)
    elif self.state.show_details:
        layout["body"].split_row(
            Layout(Panel(self.create_agent_table(), title="Agents")),
            Layout(self.create_details_panel() or "", ratio=1),
        )
    else:
        layout["body"].update(Panel(self.create_agent_table(), title="Agents"))

    return layout
```

### Step 5: Add Key Handling for Skills View

In the `run()` method, find the main event loop and add skills key handling:

```python
while True:
    # Read key
    key = self.read_key()

    # Handle key presses
    if key == "q":
        break

    # ADD THIS SECTION:
    # View switching
    elif key == "5" and self.state.current_view != "skills":
        self.state.current_view = "skills"
        self.state.selected_index = 0
        self.state.status_message = "Skills view"

    # Skills view specific keys
    elif self.state.current_view == "skills":
        # Try skills-specific key handling first
        if not self.handle_skills_key(key):
            # Fall back to common navigation
            if key == "k" or key == "UP":
                self.move_up()
            elif key == "j" or key == "DOWN":
                self.move_down()
            elif key == "/":
                live.update(self.create_layout())
                self.start_filter()
            elif key == "\x1b":
                self.clear_filter()
                self.state.show_help = False
                self.state.show_details = False
                self.toggle_skills_view_mode("local")
            elif key == "?":
                self.toggle_help()
            elif key == "r":
                self.load_skills()

    # ... existing key handling for other views
    elif key == "k" or key == "UP":
        self.move_up()
    # ... etc

    # Update display
    live.update(self.create_layout())
```

### Step 6: Update Help Panel

Find the `create_help_panel()` method and add skills-specific help:

```python
def create_help_panel(self) -> Panel:
    """Create the help panel."""
    help_text = Text()

    # General navigation
    help_text.append("Navigation:\n", style="bold cyan")
    help_text.append("  1-9     - Switch views\n")
    help_text.append("  ?       - Toggle this help\n")
    help_text.append("  q       - Quit\n\n")

    # ADD THIS SECTION:
    if self.state.current_view == "skills":
        help_text.append("Skills View:\n", style="bold cyan")
        help_text.append("  ↑/k     - Move up\n")
        help_text.append("  ↓/j     - Move down\n")
        help_text.append("  Enter   - Toggle details panel\n")
        help_text.append("  v       - Validate skill\n")
        help_text.append("  m       - Toggle metrics panel\n")
        help_text.append("  c       - Community browser\n")
        help_text.append("  /       - Search/filter skills\n")
        help_text.append("  Esc     - Clear filter / Back to list\n")
        help_text.append("  r       - Reload skills\n")
    else:
        # Existing help text for other views
        help_text.append("Agent View:\n", style="bold cyan")
        help_text.append("  ↑/k     - Move up\n")
        help_text.append("  ↓/j     - Move down\n")
        help_text.append("  Space   - Toggle agent (activate/deactivate)\n")
        help_text.append("  Enter   - Show agent details\n")
        help_text.append("  /       - Search/filter agents\n")
        help_text.append("  Esc     - Clear filter\n")
        help_text.append("  r       - Reload agents\n")

    return Panel(help_text, title="Help", border_style="yellow")
```

### Step 7: Update move_up() and move_down()

These methods need to work with both agents and skills. Update them to be view-aware:

```python
def move_up(self) -> None:
    """Move selection up."""
    if self.state.current_view == "skills":
        filtered_items = self.get_filtered_skills()
    else:
        filtered_items = self.get_filtered_agents()

    if filtered_items and self.state.selected_index > 0:
        self.state.selected_index -= 1

def move_down(self) -> None:
    """Move selection down."""
    if self.state.current_view == "skills":
        filtered_items = self.get_filtered_skills()
    else:
        filtered_items = self.get_filtered_agents()

    if filtered_items and self.state.selected_index < len(filtered_items) - 1:
        self.state.selected_index += 1
```

### Step 8: Update Footer to Show Skill Counts

Find `create_footer()` and make it view-aware:

```python
def create_footer(self) -> Panel:
    """Create the footer with keybindings and status."""
    content = Text()

    # Status bar
    if self.state.status_message:
        content.append(self.state.status_message, style="bold")

    # Filter indicator
    if self.state.filter_text:
        content.append(" | ", style="dim")
        content.append(f"Filter: {self.state.filter_text}", style="cyan")

    # Item count (view-aware)
    if self.state.current_view == "skills":
        filtered_count = len(self.get_filtered_skills())
        total_count = len(self.state.skills)
        item_type = "skills"
    else:
        filtered_count = len(self.get_filtered_agents())
        total_count = len(self.state.agents)
        item_type = "agents"

    if self.state.filter_text and filtered_count != total_count:
        content.append(" | ", style="dim")
        content.append(
            f"Showing {filtered_count}/{total_count} {item_type}", style="dim"
        )

    return Panel(content, style="bold green", padding=(0, 1))
```

## Testing

### 1. Basic Functionality
```bash
python -m claude_ctx_py.tui
```

- Press `5` to enter skills view
- Use `j/k` to navigate
- Press `Enter` to see details
- Press `m` to see metrics
- Press `/` to filter
- Press `v` to validate
- Press `q` to quit

### 2. Verification Checklist

- [ ] Skills load on startup
- [ ] Table displays correctly
- [ ] Navigation works (up/down)
- [ ] Details panel shows when pressing Enter
- [ ] Metrics panel shows when pressing `m`
- [ ] Validation runs when pressing `v`
- [ ] Filter works correctly
- [ ] Escape returns to main list
- [ ] 'r' key reloads skills
- [ ] View switching (press `1` to go back to agents view)

### 3. Edge Cases

- [ ] No skills directory (shows appropriate message)
- [ ] Empty skills directory (shows "No skills found")
- [ ] Skills with no metrics (shows 0 values)
- [ ] Filter with no matches (shows "No skills found")
- [ ] Very long skill descriptions (truncates properly)

## Troubleshooting

### Import Errors
If you get import errors:
- Check that all imports are at the top of tui.py
- Verify metrics.py exists and exports get_all_metrics, get_skill_metrics
- Verify core/skills.py exports the necessary functions

### Skills Don't Load
- Check ~/.cortex/skills directory exists
- Verify SKILL.md files have valid frontmatter
- Check console for error messages
- Try running: `python -c "from claude_ctx_py.core import list_skills; print(list_skills())"`

### Table Doesn't Display
- Verify Rich library is installed: `pip install rich`
- Check that create_skills_table() is called in create_layout()
- Verify filtered_skills list is not empty

### Metrics Don't Show
- Check ~/.cortex/.metrics/skills/stats.json exists
- Verify metrics.py can be imported
- Try: `python -c "from claude_ctx_py.metrics import get_all_metrics; print(get_all_metrics())"`

## Rollback

If something goes wrong, you can rollback by:

1. Remove the added methods from AgentTUI class
2. Remove the skills import statements
3. Remove the SkillInfo dataclass
4. Remove skills field from TUIState
5. Remove skills initialization from __init__
6. Revert changes to create_layout(), run(), etc.

Git commands:
```bash
# See what changed
git diff claude_ctx_py/tui.py

# Discard changes
git checkout -- claude_ctx_py/tui.py
```

## Next Steps

After successful integration:

1. **Test thoroughly** with different skill sets
2. **Implement community browser** fully
3. **Add skill installation** from TUI
4. **Improve error handling** for edge cases
5. **Add more metrics views** (trending, ROI, etc.)
6. **Update documentation** with screenshots

## Support

For issues or questions:
- Check SKILLS_TUI_FINAL_SUMMARY.md for complete details
- Review skills_tui_methods.py for method implementations
- Check SKILLS_TUI_IMPLEMENTATION.md for design decisions
