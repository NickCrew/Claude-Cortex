#!/usr/bin/env python3
"""Script to integrate the Skills view into tui.py."""

import re
from pathlib import Path


def integrate_skills_view():
    """Integrate the Skills view methods into tui.py."""

    tui_file = Path(__file__).parent / "claude_ctx_py" / "tui.py"
    skills_methods_file = Path(__file__).parent / "skills_tui_methods.py"

    if not tui_file.exists():
        print(f"Error: {tui_file} not found")
        return 1

    if not skills_methods_file.exists():
        print(f"Error: {skills_methods_file} not found")
        return 1

    # Read current content
    tui_content = tui_file.read_text()
    skills_content = skills_methods_file.read_text()

    # Extract methods from skills file (skip the docstring at top)
    # Remove first 4 lines (docstring) and get the rest
    skills_lines = skills_content.split('\n')[4:]
    skills_methods = '\n'.join(skills_lines)

    # Check if already integrated
    if "def load_skills(self)" in tui_content:
        print("- Skills methods already integrated")
    else:
        # Find a good insertion point (after load_agents method ends at line with self.state.agents = [])
        insert_pattern = r'(    def load_agents\(self\) -> None:.*?except Exception as e:.*?self\.state\.agents = \[\]\n\n)'

        if re.search(insert_pattern, tui_content, re.DOTALL):
            def add_skills_methods(match):
                return match.group(1) + '    # Skills Management Methods\n' + skills_methods + '\n\n'

            tui_content = re.sub(
                insert_pattern,
                add_skills_methods,
                tui_content,
                flags=re.DOTALL
            )
            print("✓ Added skills methods to AgentTUI class")
        else:
            print("Error: Could not find insertion point after load_agents()")
            print("Trying to find nearest method boundary...")
            # Try alternative: insert after _parse_agent_file method
            alt_pattern = r'(    def _parse_agent_file\(self.*?\n)\n(    def )'
            if re.search(alt_pattern, tui_content, re.DOTALL):
                def add_skills_methods_alt(match):
                    return match.group(1) + '\n    # Skills Management Methods\n' + skills_methods + '\n\n' + match.group(2)

                # Insert before the next method
                tui_content = re.sub(
                    alt_pattern,
                    add_skills_methods_alt,
                    tui_content,
                    flags=re.DOTALL
                )
                print("✓ Added skills methods after _parse_agent_file")
            else:
                return 1

    # Add skills imports
    if "list_skills" not in tui_content:
        # Add to the existing core imports
        import_pattern = r'(from \.core import \([\s\S]+?)(\))'
        import_addition = """    list_skills,
    skill_info,
    skill_validate,
    skill_community_list,
    skill_community_search,
    _extract_front_matter,
"""
        tui_content = re.sub(import_pattern, r'\1' + import_addition + r'\2', tui_content)
        print("✓ Added skills imports")
    else:
        print("- Skills imports already present")

    # Add metrics import
    if "from .metrics import" not in tui_content:
        # Find the last import line and add after it
        import_section_end = tui_content.find('\n\n@dataclass')
        if import_section_end > 0:
            before_imports = tui_content[:import_section_end]
            after_imports = tui_content[import_section_end:]
            tui_content = before_imports + "\nfrom .metrics import get_all_metrics, get_skill_metrics\n" + after_imports
            print("✓ Added metrics imports")
    else:
        print("- Metrics imports already present")

    # Add skills view to create_layout
    if '"skills"' not in tui_content:
        # Find the orchestrate view section and add skills after it
        layout_pattern = r'(elif self\.state\.current_view == "orchestrate":\n            layout\["body"\]\.update\(self\.create_orchestrate_view\(\)\))'

        skills_layout = '''
        elif self.state.current_view == "skills":
            if hasattr(self, 'community_mode') and self.community_mode:
                layout["body"].update(Panel(self.create_community_skills_table(), title="Community Skills"))
            elif self.state.show_details:
                layout["body"].split_row(
                    Layout(Panel(self.create_skills_table(), title="Skills")),
                    Layout(self.create_skills_details_panel() or "", ratio=1),
                )
            else:
                layout["body"].update(Panel(self.create_skills_table(), title="Skills"))'''

        tui_content = re.sub(
            layout_pattern,
            r'\1' + skills_layout,
            tui_content
        )
        print("✓ Added skills view to create_layout()")
    else:
        print("- Skills view already in create_layout()")

    # Add skills loading to run() method
    if "self.load_skills()" not in tui_content:
        run_pattern = r'(def run\(self\) -> int:.*?self\.load_agents\(\)\n)'
        skills_init = "        self.load_skills()\n        self.community_mode = False  # Track if in community browser\n"

        tui_content = re.sub(
            run_pattern,
            r'\1' + skills_init,
            tui_content,
            flags=re.DOTALL
        )
        print("✓ Added skills loading to run() method")
    else:
        print("- Skills loading already in run() method")

    # Add view switching key (5)
    if 'key == "5"' not in tui_content:
        view_switch_pattern = r'(elif key == "4":.*?self\.state\.status_message = "[^"]*")'
        skills_switch = '''
                    elif key == "5":
                        # Switch to skills view
                        self.state.current_view = "skills"
                        self.state.selected_index = 0
                        self.community_mode = False
                        self.state.status_message = "Skills view"'''

        tui_content = re.sub(
            view_switch_pattern,
            r'\1' + skills_switch,
            tui_content,
            flags=re.DOTALL
        )
        print("✓ Added skills view switch key (5)")
    else:
        print("- Skills view switch key already present")

    # Add skills navigation to move_up() and move_down()
    if 'current_view == "skills"' not in tui_content:
        # Add to move_up
        move_up_pattern = r'(def move_up\(self\) -> None:.*?elif self\.state\.current_view == "workflows":.*?\n                self\.state\.selected_index -= 1\n)'
        skills_move_up = '''        elif self.state.current_view == "skills":
            if hasattr(self, 'community_mode') and self.community_mode:
                if self.state.selected_index > 0:
                    self.state.selected_index -= 1
            else:
                filtered_skills = self.get_filtered_skills()
                if filtered_skills and self.state.selected_index > 0:
                    self.state.selected_index -= 1
'''

        tui_content = re.sub(
            move_up_pattern,
            r'\1' + skills_move_up,
            tui_content,
            flags=re.DOTALL
        )

        # Add to move_down
        move_down_pattern = r'(def move_down\(self\) -> None:.*?elif self\.state\.current_view == "workflows":.*?\n                self\.state\.selected_index \+= 1\n)'
        skills_move_down = '''        elif self.state.current_view == "skills":
            if hasattr(self, 'community_mode') and self.community_mode:
                # Get community skills count
                pass  # Will be implemented
            else:
                filtered_skills = self.get_filtered_skills()
                if filtered_skills and self.state.selected_index < len(filtered_skills) - 1:
                    self.state.selected_index += 1
'''

        tui_content = re.sub(
            move_down_pattern,
            r'\1' + skills_move_down,
            tui_content,
            flags=re.DOTALL
        )
        print("✓ Added skills navigation to move_up() and move_down()")
    else:
        print("- Skills navigation already present")

    # Write the modified content back
    tui_file.write_text(tui_content)
    print(f"\n✓ Successfully integrated Skills view into {tui_file}")
    print("\nSkills view features:")
    print("  - Press '5' to switch to skills view")
    print("  - Press 'c' to browse community skills")
    print("  - Press 'v' to validate selected skill")
    print("  - Press 'm' to view skill metrics")

    return 0


if __name__ == "__main__":
    exit(integrate_skills_view())
