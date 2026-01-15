# 📋 Copy Definition Feature

The TUI now supports copying definitions of agents, modes, rules, skills, and commands directly to your clipboard.

## Usage

### Keyboard Shortcut
Press `y` when viewing any of these asset types to copy the selected item's definition to your clipboard.

### Supported Views

| View | What Gets Copied | Notes |
|------|------------------|-------|
| **Agents** | Complete agent markdown definition | Includes frontmatter, dependencies, instructions |
| **Modes** | Full mode configuration | Complete behavioral mode definition |
| **Rules** | Rule markdown content | All rule instructions and examples |
| **Skills** | Skill definition file (SKILL.md) | Complete skill documentation |
| **Commands** | Command with metadata header | Includes category, complexity, linked assets, and body |

## Examples

### Copy an Agent
1. Navigate to Agents view (`1` or click Agents)
2. Select an agent using arrow keys or `j`/`k`
3. Press `y` to copy
4. Notification confirms: ✓ Copied python-pro definition to clipboard

### Copy a Mode
1. Navigate to Modes view (`3`)
2. Select a mode
3. Press `y`
4. Definition is now in your clipboard

### Copy a Skill
1. Navigate to Skills view (`4`)
2. Select a skill
3. Press `y`
4. SKILL.md contents copied

## Clipboard Support

The feature attempts multiple clipboard methods:
- **pyperclip** library (if installed)
- **pbcopy** (macOS)
- **xclip** (Linux)

If clipboard access fails, you'll see an error notification.

## Use Cases

✅ **Share configurations** - Copy agent definitions to share with team members
✅ **Documentation** - Extract definitions for documentation purposes  
✅ **Backup** - Quick way to save a definition externally
✅ **Review** - Copy to external editor for detailed review
✅ **Compare** - Copy multiple definitions to compare side-by-side

## Related Features

- **View Definition** (`s` or Enter): View definition in TUI dialog
- **Edit Definition** (`Ctrl+E`): Open in external editor
- **Export Context** (`e` in Export view): Export entire context

## Troubleshooting

**"Failed to copy to clipboard"**
- Install pyperclip: `pip install pyperclip`
- macOS: Ensure Terminal has accessibility permissions
- Linux: Install xclip: `sudo apt-get install xclip`

**"Select an X to copy"**
- Make sure an item is selected in the current view
- Use arrow keys to highlight an item first
