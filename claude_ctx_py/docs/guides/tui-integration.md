# TUI Integration Guide

## Summary

This document describes the implementation of three new views for the cortex TUI:
1. **Profile View** (View #8) - Profile management
2. **Export View** (View #9) - Context export with format selection
3. **Init Wizard** (accessible via 'i' key) - Interactive project initialization

## Files Created

### 1. `claude_ctx_py/tui_extensions.py`
Contains three mixin classes:
- `ProfileViewMixin` - Profile management functionality
- `ExportViewMixin` - Context export functionality
- `WizardViewMixin` - Init wizard functionality

## Integration Steps

### Step 1: Add imports to `claude_ctx_py/tui.py`

Add to the imports section (after the existing .core imports):

```python
from .tui_extensions import ProfileViewMixin, ExportViewMixin, WizardViewMixin
```

### Step 2: Modify AgentTUI class definition

Change:
```python
class AgentTUI:
    """Terminal User Interface for agent management."""
```

To:
```python
class AgentTUI(ProfileViewMixin, ExportViewMixin, WizardViewMixin):
    """Terminal User Interface for agent management."""
```

### Step 3: Update create_layout method

Replace the `create_layout` method with:

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

    # Route to appropriate view
    if self.state.show_help:
        layout["body"].update(self.create_help_panel())
    elif self.state.current_view == "profile":
        layout["body"].update(self.render_profile_view())
    elif self.state.current_view == "export":
        layout["body"].update(self.render_export_view())
    elif self.wizard_active:
        layout["body"].update(self.render_wizard_view())
    elif self.state.show_details:
        layout["body"].split_row(
            Layout(Panel(self.create_agent_table(), title="Agents")),
            Layout(self.create_details_panel() or "", ratio=1),
        )
    else:
        layout["body"].update(Panel(self.create_agent_table(), title="Agents"))

    return layout
```

### Step 4: Update run method keyboard handling

In the `run` method, add key handlers after the existing ones (around line 617):

```python
elif key == "8":
    # Switch to profile view
    self.state.current_view = "profile"
    self.state.selected_index = 0
    self.state.status_message = "Profile view"
elif key == "9":
    # Switch to export view
    self.state.current_view = "export"
    self.state.selected_index = 0
    self.state.status_message = "Export view"
elif key == "i":
    # Start init wizard
    self.start_wizard()
elif key == "1":
    # Return to agents view
    self.state.current_view = "agents"
    self.state.selected_index = 0
    self.state.status_message = "Agents view"
```

### Step 5: Add view-specific key handling

After the existing key handling, add view-specific handlers:

```python
# View-specific key handling
if self.state.current_view == "profile":
    if key == "\r" or key == "\n":  # Enter
        self.apply_profile()
    elif key == "n":
        self.save_current_profile()
    elif key == "d":
        self.delete_profile()
    elif key == "s":
        self.save_current_profile()

elif self.state.current_view == "export":
    if key == " ":  # Space
        self.toggle_export_option()
    elif key == "f":
        self.cycle_export_format()
    elif key == "e":
        self.execute_export()
    elif key == "p":
        self.copy_to_clipboard()

elif self.wizard_active:
    if key == "\r" or key == "\n":  # Enter
        if self.wizard_step == 0:
            self.wizard_step = 1
        else:
            self.wizard_next_step()
    elif key == "\x7f":  # Backspace
        self.wizard_prev_step()
    elif key == "\x1b":  # Escape
        self.wizard_cancel()
```

### Step 6: Update help panel

Update the `create_help_panel` method to include new views:

```python
def create_help_panel(self) -> Panel:
    """Create the help panel."""
    help_text = Text()
    help_text.append("Views:\n", style="bold cyan")
    help_text.append("  1       - Agents view\n")
    help_text.append("  8       - Profile view\n")
    help_text.append("  9       - Export view\n")
    help_text.append("  i       - Init wizard\n")
    help_text.append("\n")
    help_text.append("Navigation:\n", style="bold cyan")
    help_text.append("  ↑/k     - Move up\n")
    help_text.append("  ↓/j     - Move down\n")
    help_text.append("  Space   - Toggle/Select\n")
    help_text.append("  Enter   - Confirm/Details\n")
    help_text.append("  /       - Search/filter\n")
    help_text.append("  Esc     - Clear/Cancel\n")
    help_text.append("  r       - Reload\n")
    help_text.append("  ?       - Toggle help\n")
    help_text.append("  q       - Quit\n")

    return Panel(help_text, title="Help", border_style="yellow")
```

## View-Specific Controls

### Profile View (View #8)
- `↑/↓` or `j/k` - Navigate profiles
- `Enter` - Apply selected profile
- `n` - Create new profile
- `s` - Save current configuration as profile
- `d` - Delete selected profile
- `r` - Reload profiles
- `1` - Return to agents view

### Export View (View #9)
- `↑/↓` or `j/k` - Navigate export options
- `Space` - Toggle export option
- `f` - Cycle through formats (JSON → XML → Markdown)
- `e` - Export to file
- `p` - Copy to clipboard
- `1` - Return to agents view

### Init Wizard (accessed via `i`)
- `Enter` - Next step / Confirm
- `Backspace` - Previous step
- `Esc` - Cancel wizard
- `Space` - Toggle selection (in selection steps)
- `↑/↓` or `j/k` - Navigate options

## Testing

After integration, test the following:

1. **Profile View**:
   ```bash
   cortex tui
   # Press 8 to switch to profile view
   # Press ↑/↓ to navigate profiles
   # Press Enter to apply a profile
   # Press 1 to return to agents view
   ```

2. **Export View**:
   ```bash
   cortex tui
   # Press 9 to switch to export view
   # Press Space to toggle options
   # Press f to change format
   # Press e to export
   # Press 1 to return
   ```

3. **Init Wizard**:
   ```bash
   cortex tui
   # Press i to start wizard
   # Press Enter to proceed through steps
   # Press Backspace to go back
   # Press Esc to cancel
   ```

## Implementation Status

- ✅ Profile View (View #8) - Core implementation complete
  - Profile listing implemented
  - Apply profile implemented
  - Save/delete profile stubs created (need full implementation)
- ✅ Export View (View #9) - Core implementation complete
  - Export options implemented
  - Format selection implemented
  - Preview generation implemented
  - Export execution implemented
  - Clipboard copy stub created (needs implementation)
- ✅ Init Wizard - Core structure complete
  - Multi-step wizard interface implemented
  - Step 1 (Project type) implemented
  - Steps 2-5 stubs created (need full implementation)
  - Navigation controls implemented

## Next Steps

1. Complete save/delete profile functionality
2. Implement clipboard support for export
3. Complete wizard steps 2-5 with full functionality
4. Add project type auto-detection
5. Add profile switching with confirmation dialog
6. Add export destination selection dialog
7. Persist wizard progress for resume capability
