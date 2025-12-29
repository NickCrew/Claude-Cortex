# Command Palette Guide 🎨

## Overview

The TUI now has a **beautiful, functional command palette** with visual styling and 11 custom commands for quick navigation and actions!

## How to Use

### Open Command Palette

Press **Ctrl+P** in the TUI to open the command palette.

> **New:** The palette now launches on its own worker, so it stays responsive even if other dialogs (task details, log viewers, etc.) are open. If Ctrl+P used to throw a `NoActiveWorker` error in older builds, that workflow is now fixed.

### Search for Commands

Type to search:
- **"agent"** → Shows agent management commands
- **"mode"** → Shows mode commands
- **"rule"** → Shows rule commands
- **"show"** → Shows all view commands
- **"toggle"** → Shows all toggle commands
- **"export"** → Shows context export command

### Navigate Results

- **↑/↓ arrows** → Move between commands
- **Enter** → Execute selected command
- **Escape** → Close palette

## Available Commands

### 🔧 Agent Management
- **💻 Show Agents** - View and manage agents (Press 2 or select)
- **▶️ Activate Agent** - Enable an agent (Goes to agent view, then Space)
- **⏹️ Deactivate Agent** - Disable an agent (Goes to agent view, then Space)

### 🎛️ Mode Management
- **🎨 Show Modes** - View active behavioral modes (Press 3 or select)
- **🔄 Toggle Mode** - Switch mode on/off (Goes to modes view, then Space)

### 📄 Rule Management
- **📋 Show Rules** - View active rule modules (Press 4 or select)
- **🔄 Toggle Rule** - Switch rule on/off (Goes to rules view, then Space)

### 🧩 Principles Management
- **📘 Show Principles** - View principles snippets (Press `p` or select)
- **🔄 Toggle Principle** - Switch snippet on/off (Goes to principles view, then Space)
- **🧱 Build Principles** - Rebuild `PRINCIPLES.md` from active snippets
- **📄 Open Principles** - View generated `PRINCIPLES.md`

### 📁 Other Views
- **💻 Show Skills** - Browse available skills (Press 5 or select)
- **🏃 Show Workflows** - View workflow execution (Press 6 or select)
- **🛰 Show MCP** - Manage MCP servers (Press 7 or select)
- **👤 Show Profiles** - Manage saved/built-in profiles (Press 8 or select)
- **📦 Show Export** - Configure context export (Press 9 or select)
- **🤖 Show AI Assistant** - Open AI assistant view (Press 0 or select)
- **🏃 Show Orchestrate** - View orchestration tasks (Press `o` or select)
- **📁 Export Context** - Export current context to file

### 🧠 Skill Intelligence
- **Skill Info** – Inspect metadata/frontmatter for the selected skill
- **Skill Versions** – Show available versions + compatibility notes
- **Skill Dependencies / Agents / Compose** – Visualize who depends on the skill and its compose tree
- **Skill Analyze / Suggest** – Feed free-form text or a project path to get skill recommendations
- **Skill Analytics / Report / Trending** – Pull the analytics dashboards, reports, and historical trends
- **Skill Metrics Reset** – Clear stored metrics after large refactors
- **Community Install / Validate / Rate / Search** – Work with the community catalog without leaving the TUI

## Visual Features

### Color-Coded Icons
- **Cyan** → View/Show commands
- **Green** → Activate/Enable actions
- **Red** → Deactivate/Disable actions
- **Yellow** → Toggle/Modify actions
- **Magenta** → Special views
- **Blue** → Documentation/Rules

### Rich Descriptions
Each command shows:
- **Bold title** → Command name
- **Dimmed text** → Description with helpful hints
- **Keyboard shortcuts** → Quick access keys

### Smart Matching
The search is fuzzy - type partial words and it finds matches:
- "ag" → Finds "Agent" commands
- "tog" → Finds "Toggle" commands
- "exp" → Finds "Export" command

## Technical Details

### Implementation Files
- `claude_ctx_py/tui_commands.py` → Command provider with visual styling
- `claude_ctx_py/tui_textual.py` → TUI with `COMMANDS` registration

### Key Learning
Textual uses `COMMANDS` (set), not `COMMAND_PROVIDERS` (list)!

```python
# Correct
COMMANDS = {AgentCommandProvider}

# Wrong
COMMAND_PROVIDERS = [AgentCommandProvider]
```

## Tips

1. **Quick navigation**: Press Ctrl+P and type first letters of what you want
2. **Learn shortcuts**: Command descriptions show keyboard shortcuts
3. **Visual cues**: Icon colors indicate action type (view, activate, toggle, etc.)
4. **Context help**: Descriptions explain what happens after selecting
5. **Safe reopening**: Because the palette runs in a dedicated worker, you can pop it open repeatedly—even while workflows are launching or logs are streaming—without destabilising the TUI.

## Example Workflows

### Activate an Agent
1. Press **Ctrl+P**
2. Type **"activate"**
3. Press **Enter**
4. In agents view, use arrows to select agent
5. Press **Space** to activate

### Toggle a Mode
1. Press **Ctrl+P**
2. Type **"toggle mode"**
3. Press **Enter**
4. In modes view, select mode
5. Press **Space** to toggle

### Export Context
1. Press **Ctrl+P**
2. Type **"export"**
3. Press **Enter**
4. Configure export options

Enjoy your enhanced TUI experience! 🎉
