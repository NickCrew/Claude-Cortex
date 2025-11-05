#!/usr/bin/env python3
"""Script to integrate the new TUI views into the main TUI file."""

import re
from pathlib import Path


def integrate_tui_views():
    """Integrate the new TUI views."""
    tui_file = Path(__file__).parent / "claude_ctx_py" / "tui.py"

    # Read current content
    content = tui_file.read_text()

    # 1. Add imports
    import_pattern = r"(from \.core import \([^)]+\))"
    import_addition = """\n from .tui_extensions import ProfileViewMixin, ExportViewMixin, WizardViewMixin"""

    if "tui_extensions" not in content:
        content = re.sub(import_pattern, r"\1" + import_addition, content)
        print("✓ Added tui_extensions imports")
    else:
        print("- tui_extensions imports already present")

    # 2. Modify class definition
    class_pattern = r"class AgentTUI:"
    class_replacement = "class AgentTUI(ProfileViewMixin, ExportViewMixin, WizardViewMixin):"

    if "ProfileViewMixin" not in content:
        content = content.replace(class_pattern, class_replacement)
        print("✓ Updated AgentTUI class to use mixins")
    else:
        print("- AgentTUI class already uses mixins")

    # 3. Update create_layout method
    layout_method = '''    def create_layout(self) -> Layout:
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
        elif hasattr(self, 'wizard_active') and self.wizard_active:
            layout["body"].update(self.render_wizard_view())
        elif self.state.show_details:
            layout["body"].split_row(
                Layout(Panel(self.create_agent_table(), title="Agents")),
                Layout(self.create_details_panel() or "", ratio=1),
            )
        else:
            layout["body"].update(Panel(self.create_agent_table(), title="Agents"))

        return layout'''

    if "render_profile_view" not in content:
        # Find and replace the create_layout method
        layout_pattern = r"    def create_layout\(self\) -> Layout:.*?return layout"
        content = re.sub(layout_pattern, layout_method, content, flags=re.DOTALL)
        print("✓ Updated create_layout method")
    else:
        print("- create_layout method already updated")

    # 4. Add view switching keys in run method
    view_switching = '''
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
                        if hasattr(self, 'start_wizard'):
                            self.start_wizard()
                    elif key == "1":
                        # Return to agents view
                        self.state.current_view = "agents"
                        self.state.selected_index = 0
                        self.state.status_message = "Agents view"

                    # View-specific key handling
                    if self.state.current_view == "profile":
                        if key == "\\r" or key == "\\n":  # Enter
                            if hasattr(self, 'apply_profile'):
                                self.apply_profile()
                        elif key == "n":
                            if hasattr(self, 'save_current_profile'):
                                self.save_current_profile()
                        elif key == "d":
                            if hasattr(self, 'delete_profile'):
                                self.delete_profile()
                        elif key == "s":
                            if hasattr(self, 'save_current_profile'):
                                self.save_current_profile()

                    elif self.state.current_view == "export":
                        if key == " ":  # Space
                            if hasattr(self, 'toggle_export_option'):
                                self.toggle_export_option()
                        elif key == "f":
                            if hasattr(self, 'cycle_export_format'):
                                self.cycle_export_format()
                        elif key == "e":
                            if hasattr(self, 'execute_export'):
                                self.execute_export()
                        elif key == "p":
                            if hasattr(self, 'copy_to_clipboard'):
                                self.copy_to_clipboard()

                    elif hasattr(self, 'wizard_active') and self.wizard_active:
                        if key == "\\r" or key == "\\n":  # Enter
                            if hasattr(self, 'wizard_next_step'):
                                self.wizard_next_step()
                        elif key == "\\x7f":  # Backspace
                            if hasattr(self, 'wizard_prev_step'):
                                self.wizard_prev_step()
                        elif key == "\\x1b":  # Escape
                            if hasattr(self, 'wizard_cancel'):
                                self.wizard_cancel()
'''

    # Find the position to insert view switching (after the 'r' key handler)
    if 'key == "8"' not in content:
        reload_pattern = r"(elif key == \"r\":\s+self\.load_agents\(\))"
        content = re.sub(reload_pattern, r"\1" + view_switching, content)
        print("✓ Added view switching and handling keys")
    else:
        print("- View switching keys already present")

    # 5. Update help panel
    help_method = '''    def create_help_panel(self) -> Panel:
        """Create the help panel."""
        help_text = Text()
        help_text.append("Views:\\n", style="bold cyan")
        help_text.append("  1       - Agents view\\n")
        help_text.append("  8       - Profile view\\n")
        help_text.append("  9       - Export view\\n")
        help_text.append("  i       - Init wizard\\n")
        help_text.append("\\n")
        help_text.append("Navigation:\\n", style="bold cyan")
        help_text.append("  ↑/k     - Move up\\n")
        help_text.append("  ↓/j     - Move down\\n")
        help_text.append("  Space   - Toggle/Select\\n")
        help_text.append("  Enter   - Confirm/Details\\n")
        help_text.append("  /       - Search/filter\\n")
        help_text.append("  Esc     - Clear/Cancel\\n")
        help_text.append("  r       - Reload\\n")
        help_text.append("  ?       - Toggle help\\n")
        help_text.append("  q       - Quit\\n")

        return Panel(help_text, title="Help", border_style="yellow")'''

    if "Profile view" not in content or "Export view" not in content:
        help_pattern = r"    def create_help_panel\(self\) -> Panel:.*?return Panel\(help_text, title=\"Help\", border_style=\"yellow\"\)"
        content = re.sub(help_pattern, help_method, content, flags=re.DOTALL)
        print("✓ Updated help panel")
    else:
        print("- Help panel already updated")

    # Write the modified content
    tui_file.write_text(content)
    print(f"\n✓ Successfully integrated new TUI views into {tui_file}")
    print("\nNext steps:")
    print("1. Test the TUI: claude-ctx tui")
    print("2. Press '8' for profile view")
    print("3. Press '9' for export view")
    print("4. Press 'i' for init wizard")
    print("5. Press '?' for help")


if __name__ == "__main__":
    try:
        integrate_tui_views()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
