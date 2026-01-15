# TUI Workflows and Orchestrate Views - Integration Guide

## Quick Integration Steps

Since the tui.py file has been modified by linters, here's the manual integration approach:

### Step 1: Copy the new methods

The file `claude_ctx_py/tui_workflows_orchest.py` contains 5 new methods that need to be added to the `AgentTUI` class in `tui.py`.

Insert these methods after the `clear_filter()` method (around line 580):

1. `load_workflows()` - Loads workflow YAML files
2. `create_workflows_table()` - Renders workflows table
3. `create_workflow_details_panel()` - Shows workflow details
4. `load_agent_tasks()` - Loads orchestration tasks
5. `create_orchestrate_view()` - Renders orchestration dashboard

### Step 2: Add workflow action methods

Add these two new methods after the new methods from Step 1:

```python
def run_workflow(self) -> None:
    """Run the selected workflow."""
    workflows = self.load_workflows()
    if not workflows or self.state.selected_index >= len(workflows):
        self.state.status_message = "No workflow selected"
        return

    workflow = workflows[self.state.selected_index]

    try:
        exit_code, message = workflow_run(workflow.file_path.stem if workflow.file_path else workflow.name)

        # Clean ANSI codes from message
        import re
        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
        self.state.status_message = clean_message.split("\n")[0]

    except Exception as e:
        self.state.status_message = f"Error running workflow: {e}"

def resume_workflow(self) -> None:
    """Resume the paused workflow."""
    workflows = self.load_workflows()
    if not workflows or self.state.selected_index >= len(workflows):
        self.state.status_message = "No workflow selected"
        return

    workflow = workflows[self.state.selected_index]

    if workflow.status != "paused":
        self.state.status_message = "Workflow is not paused"
        return

    try:
        exit_code, message = workflow_resume()

        import re
        clean_message = re.sub(r"\x1b\[[0-9;]*m", "", message)
        self.state.status_message = clean_message.split("\n")[0]

    except Exception as e:
        self.state.status_message = f"Error resuming workflow: {e}"
```

### Step 3: Update create_layout() method

Find the `create_layout()` method and update the body rendering section to add workflow and orchestrate views:

```python
# Body rendering based on current view
if self.state.show_help:
    layout["body"].update(self.create_help_panel())
elif self.state.current_view == "workflows":
    if self.state.show_details:
        layout["body"].split_row(
            Layout(Panel(self.create_workflows_table(), title="Workflows")),
            Layout(self.create_workflow_details_panel() or "", ratio=1),
        )
    else:
        layout["body"].update(Panel(self.create_workflows_table(), title="Workflows"))
elif self.state.current_view == "orchestrate":
    layout["body"].update(self.create_orchestrate_view())
elif self.state.show_details:
    layout["body"].split_row(
        Layout(Panel(self.create_agent_table(), title="Agents")),
        Layout(self.create_details_panel() or "", ratio=1),
    )
else:
    layout["body"].update(Panel(self.create_agent_table(), title="Agents"))
```

### Step 4: Update run() method key handling

In the `run()` method, find the key handling section and add:

```python
# View switching
elif key == "6":
    self.state.current_view = "workflows"
    self.state.selected_index = 0
    self.state.show_details = False
elif key == "7":
    self.state.current_view = "orchestrate"
    self.state.show_details = False

# Modify existing 'r' and ' ' key handlers:
elif key == "r":
    if self.state.current_view == "workflows":
        self.run_workflow()
    else:
        self.load_agents()
elif key == " ":
    if self.state.current_view == "workflows":
        self.resume_workflow()
    else:
        self.toggle_agent()
elif key == "s":
    if self.state.current_view == "workflows":
        self.state.status_message = "Stop workflow not yet implemented"
```

### Step 5: Update create_help_panel() method

Add the new keybindings to the help panel:

```python
help_text.append("\nViews:\n", style="bold cyan")
help_text.append("  1-5     - Switch views\n")
help_text.append("  6       - Workflows view\n")
help_text.append("  7       - Orchestrate view\n")
help_text.append("\nActions (Workflows):\n", style="bold cyan")
help_text.append("  r       - Run selected workflow\n")
help_text.append("  Space   - Resume paused workflow\n")
help_text.append("  s       - Stop running workflow\n")
```

## Testing

1. Create test workflow directory:
```bash
mkdir -p ~/.claude/workflows
cp workflows/*.yaml ~/.claude/workflows/
```

2. Run TUI:
```bash
claude-ctx tui
```

3. Press `6` to view workflows

4. Press `7` to view orchestration dashboard

5. Press `?` to view help with new keybindings

## Files Modified

- `/Users/nferguson/Developer/personal/claude-ctx-plugin/claude_ctx_py/tui.py` - Main TUI file with new views

## Files Created

- `/Users/nferguson/Developer/personal/claude-ctx-plugin/claude_ctx_py/tui_workflows_orchest.py` - Temporary file with new methods
- `/Users/nferguson/Developer/personal/claude-ctx-plugin/IMPLEMENTATION_SUMMARY.md` - Detailed implementation documentation
- `/Users/nferguson/Developer/personal/claude-ctx-plugin/tui_workflows_integration.md` - This integration guide

## Clean up

After integration is complete, you can delete the temporary file:
```bash
rm claude_ctx_py/tui_workflows_orchest.py
```
