#!/usr/bin/env python3
"""
Patch script to add Workflows and Orchestrate views to tui.py.
This script reads tui_workflows_orchest.py and integrates the methods into tui.py.
"""

import re
from pathlib import Path

def apply_patch():
    """Apply the workflows and orchestrate views patch."""

    tui_file = Path(__file__).parent / "claude_ctx_py" / "tui.py"
    methods_file = Path(__file__).parent / "claude_ctx_py" / "tui_workflows_orchest.py"

    if not tui_file.exists():
        print(f"Error: {tui_file} not found")
        return 1

    if not methods_file.exists():
        print(f"Error: {methods_file} not found")
        return 1

    # Read the current tui.py content
    with open(tui_file, 'r', encoding='utf-8') as f:
        tui_content = f.read()

    # Read the new methods
    with open(methods_file, 'r', encoding='utf-8') as f:
        methods_content = f.read()

    # Remove the first line (doc string header) and dedent
    methods_lines = methods_content.split('\n')[2:]  # Skip doc string
    methods_content = '\n'.join(methods_lines)

    # Step 1: Insert methods after clear_filter() method
    insert_pattern = r'(    def clear_filter\(self\) -> None:.*?\n        else:\n            self\.state\.status_message = "No filter active"\n\n)'

    if not re.search(insert_pattern, tui_content, re.DOTALL):
        print("Error: Could not find clear_filter method")
        return 1

    tui_content = re.sub(
        insert_pattern,
        r'\1' + methods_content + '\n',
        tui_content,
        flags=re.DOTALL
    )

    # Step 2: Add workflows and orchestrate views to create_layout()
    layout_pattern = r'(elif self\.state\.current_view == "export":\n            layout\["body"\]\.update\(self\.render_export_view\(\)\)\n)'

    workflows_orchestrate_routing = '''elif self.state.current_view == "workflows":
            if self.state.show_details:
                layout["body"].split_row(
                    Layout(Panel(self.create_workflows_table(), title="Workflows")),
                    Layout(self.create_workflow_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(Panel(self.create_workflows_table(), title="Workflows"))
        elif self.state.current_view == "orchestrate":
            layout["body"].update(self.create_orchestrate_view())
        '''

    tui_content = re.sub(
        layout_pattern,
        r'\1        ' + workflows_orchestrate_routing,
        tui_content
    )

    # Step 3: Add view switching to move_up() and move_down()
    move_up_pattern = r'(    def move_up\(self\) -> None:.*?elif self\.state\.current_view == "rules":.*?\n                self\.state\.selected_index -= 1\n)'

    workflows_move_up = '''        elif self.state.current_view == "workflows":
            workflows = self.load_workflows()
            if workflows and self.state.selected_index > 0:
                self.state.selected_index -= 1
'''

    if re.search(move_up_pattern, tui_content, re.DOTALL):
        tui_content = re.sub(
            move_up_pattern,
            r'\1' + workflows_move_up,
            tui_content,
            flags=re.DOTALL
        )

    move_down_pattern = r'(    def move_down\(self\) -> None:.*?elif self\.state\.current_view == "rules":.*?\n                self\.state\.selected_index \+= 1\n)'

    workflows_move_down = '''        elif self.state.current_view == "workflows":
            workflows = self.load_workflows()
            if workflows and self.state.selected_index < len(workflows) - 1:
                self.state.selected_index += 1
'''

    if re.search(move_down_pattern, tui_content, re.DOTALL):
        tui_content = re.sub(
            move_down_pattern,
            r'\1' + workflows_move_down,
            tui_content,
            flags=re.DOTALL
        )

    # Step 4: Update run() method key handling
    # Find the key handling section and add new keys
    key_pattern = r'(                elif key == "9":.*?\n                    self\.state\.selected_index = 0\n)'

    new_keys = '''                elif key == "6":
                    self.state.current_view = "workflows"
                    self.state.selected_index = 0
                    self.state.show_details = False
                elif key == "7":
                    self.state.current_view = "orchestrate"
                    self.state.show_details = False
'''

    if re.search(key_pattern, tui_content, re.DOTALL):
        tui_content = re.sub(
            key_pattern,
            r'\1' + new_keys,
            tui_content
        )

    # Modify 'r' key handler
    r_key_pattern = r'(                elif key == "r":)\n(                    self\.load_agents\(\))'
    r_key_replacement = r'''\1
                    if self.state.current_view == "workflows":
                        self.run_workflow()
                    else:
\2'''

    tui_content = re.sub(r_key_pattern, r_key_replacement, tui_content)

    # Modify space key handler
    space_pattern = r'(                elif key == " ":)\n(                    self\.toggle_agent\(\))'
    space_replacement = r'''\1
                    if self.state.current_view == "workflows":
                        self.resume_workflow()
                    else:
\2'''

    tui_content = re.sub(space_pattern, space_replacement, tui_content)

    # Add 's' key for stopping workflows
    s_key = '''                elif key == "s":
                    if self.state.current_view == "workflows":
                        self.state.status_message = "Stop workflow not yet implemented"
'''

    # Insert after space key handler
    space_insert_pattern = r'(                elif key == " ":.*?else:\n                        self\.toggle_agent\(\)\n)'

    if re.search(space_insert_pattern, tui_content, re.DOTALL):
        tui_content = re.sub(
            space_insert_pattern,
            r'\1' + s_key,
            tui_content,
            flags=re.DOTALL
        )

    # Step 5: Update help panel
    help_pattern = r'(help_text\.append\("  9       - Export view\\n"\))'

    help_addition = '''        help_text.append("  6       - Workflows view\\n")
        help_text.append("  7       - Orchestrate view\\n")
        help_text.append("\\nActions (Workflows):\\n", style="bold cyan")
        help_text.append("  r       - Run selected workflow\\n")
        help_text.append("  Space   - Resume paused workflow\\n")
        help_text.append("  s       - Stop running workflow\\n")
        help_text.append("\\nOther:\\n", style="bold cyan")
'''

    if re.search(help_pattern, tui_content):
        tui_content = re.sub(
            help_pattern,
            r'\1\n        ' + help_addition,
            tui_content
        )

    # Write the patched content
    backup_file = tui_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(tui_content)
    print(f"Created backup: {backup_file}")

    with open(tui_file, 'w', encoding='utf-8') as f:
        f.write(tui_content)
    print(f"Successfully patched: {tui_file}")

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(apply_patch())
