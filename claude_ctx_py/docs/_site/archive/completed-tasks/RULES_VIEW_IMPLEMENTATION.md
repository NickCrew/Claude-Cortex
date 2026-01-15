# Rules View Implementation for TUI

This document describes the complete implementation of the Rules view for the Textual-based TUI in `claude_ctx_py/tui_textual.py`.

## Changes Made

### 1. Added Imports (Lines 5-32)
```python
from dataclasses import dataclass  # Already added
from pathlib import Path  # Already added

from .core.rules import rules_activate, rules_deactivate  # Already added
from .core.base import _iter_md_files, _parse_active_entries  # Already added
```

### 2. Added RuleNode Dataclass (Lines 35-42)
```python
@dataclass
class RuleNode:
    """Represents a rule in the system."""
    name: str
    status: str  # "active" or "inactive"
    category: str
    description: str
    path: Path
```

### 3. Implemented load_rules() Method (Lines 250-292)
**Status**: ✅ COMPLETE

Replaces the placeholder at line 250. This method:
- Uses `_resolve_claude_dir()` to find the claude directory
- Loads active rules from `.active-rules` file
- Scans `rules/` directory for active rules files
- Scans `rules-disabled/` and `rules/disabled/` for inactive rules
- Parses each rule file using `_parse_rule_file()`
- Sorts rules by category and name
- Stores in `self.rules` list
- Updates status message with count

### 4. Implemented _parse_rule_file() Method (Lines 294-340)
**Status**: ✅ COMPLETE

Helper method that:
- Reads markdown file content
- Extracts display name from first `#` heading
- Extracts description from first `##` heading or first text line
- Determines category from filename patterns:
  - "workflow" → workflow
  - "quality" → quality
  - "parallel"/"execution" → execution
  - "efficiency" → efficiency
- Returns RuleNode object with all parsed data

### 5. Add show_rules_view() Method
**Status**: ⏳ PENDING - Needs to be added after `show_agents_view()`

Insert after line 568 (after show_agents_view method):

```python
def show_rules_view(self, table: DataTable) -> None:
    """Show rules table."""
    table.add_column("Name", key="name")
    table.add_column("Status", key="status")
    table.add_column("Category", key="category")
    table.add_column("Description", key="description")

    if not hasattr(self, 'rules') or not self.rules:
        table.add_row("No rules found", "", "", "")
        return

    for rule in self.rules:
        status_text = "Active" if rule.status == "active" else "Inactive"
        # Truncate description to fit table
        description = rule.description[:50] + "..." if len(rule.description) > 50 else rule.description
        table.add_row(
            rule.name,
            status_text,
            rule.category,
            description,
        )
```

### 6. Update update_view() Method
**Status**: ⏳ PENDING - Needs elif clause added

Find the `update_view()` method (around line 540) and add this elif clause in the chain:

```python
def update_view(self) -> None:
    """Update the table based on current view."""
    table = self.query_one(DataTable)
    table.clear(columns=True)

    if self.current_view == "agents":
        self.show_agents_view(table)
    elif self.current_view == "rules":  # ADD THIS
        self.show_rules_view(table)      # ADD THIS
    elif self.current_view == "overview":
        self.show_overview(table)
    elif self.current_view == "workflows":
        self.show_workflows_view(table)
    elif self.current_view == "orchestrate":
        self.show_orchestrate_view(table)
    else:
        table.add_column("Message")
        table.add_row(f"{self.current_view.title()} view coming soon")
```

### 7. Update action_toggle() Method
**Status**: ⏳ PENDING - Needs elif clause added

Find the `action_toggle()` method (around line 705) and add rules handling:

```python
def action_toggle(self) -> None:
    """Toggle selected item."""
    if self.current_view == "agents":
        # ... existing agent toggle code ...
    elif self.current_view == "rules":  # ADD THIS BLOCK
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)
            if row_key and len(row_key) > 0:
                rule_name = str(row_key[0])
                rule = next((r for r in self.rules if r.name == rule_name), None)
                if rule:
                    try:
                        if rule.status == "active":
                            message = rules_deactivate(rule.path.stem)
                        else:
                            message = rules_activate(rule.path.stem)

                        # Remove ANSI codes
                        import re
                        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
                        self.status_message = clean_message.split("\n")[0]

                        self.load_rules()
                        self.update_view()
                    except Exception as e:
                        self.status_message = f"Error: {e}"
```

### 8. Update action_refresh() Method
**Status**: ⏳ PENDING - Needs elif clause added

Find the `action_refresh()` method (around line 745) and add rules handling:

```python
def action_refresh(self) -> None:
    """Refresh current view."""
    if self.current_view == "agents":
        self.load_agents()
        self.update_view()
    elif self.current_view == "rules":  # ADD THIS
        self.load_rules()                 # ADD THIS
        self.update_view()                # ADD THIS
    elif self.current_view == "workflows":
        self.load_workflows()
        self.update_view()
    elif self.current_view == "orchestrate":
        self.load_agent_tasks()
        self.update_view()
    self.status_message = f"Refreshed {self.current_view}"
```

## Summary of Implementation

### Completed:
1. ✅ RuleNode dataclass defined
2. ✅ Required imports added
3. ✅ `load_rules()` method implemented
4. ✅ `_parse_rule_file()` helper method implemented
5. ✅ `load_rules()` called in `on_mount()`

### Pending (Manual Additions Needed):
1. ⏳ `show_rules_view()` method - Add after show_agents_view
2. ⏳ Update `update_view()` - Add elif for rules
3. ⏳ Update `action_toggle()` - Add rules toggle handling
4. ⏳ Update `action_refresh()` - Add rules refresh handling

## Testing Checklist

After completing the pending additions:

- [ ] Run TUI and press `4` to switch to Rules view
- [ ] Verify rules are displayed with correct columns
- [ ] Verify Active/Inactive status is shown correctly
- [ ] Press `Space` on a rule to toggle its status
- [ ] Verify status updates and view refreshes
- [ ] Press `r` to refresh the rules view
- [ ] Verify categories are correct (workflow, quality, execution, efficiency)
- [ ] Verify descriptions are extracted and truncated properly

## File Locations

- Main file: `/Users/nferguson/Developer/personal/claude-ctx-plugin/claude_ctx_py/tui_textual.py`
- Core rules functions: `/Users/nferguson/Developer/personal/claude-ctx-plugin/claude_ctx_py/core/rules.py`
- Base utilities: `/Users/nferguson/Developer/personal/claude-ctx-plugin/claude_ctx_py/core/base.py`

## Pattern Consistency

The Rules view follows the EXACT same pattern as the Agents view:

| Aspect | Agents View | Rules View |
|--------|-------------|------------|
| Data class | `AgentGraphNode` | `RuleNode` |
| Load method | `load_agents()` | `load_rules()` |
| Parse method | `_parse_agent_file()` | `_parse_rule_file()` |
| Show method | `show_agents_view()` | `show_rules_view()` |
| Storage | `self.agents` | `self.rules` |
| Activate function | `agent_activate()` | `rules_activate()` |
| Deactivate function | `agent_deactivate()` | `rules_deactivate()` |
| Columns | Name, Status, Category, Tier | Name, Status, Category, Description |
