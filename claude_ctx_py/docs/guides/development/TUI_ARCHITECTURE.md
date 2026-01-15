# TUI Architecture: Comprehensive Guide

**Version**: 1.0  
**Last Updated**: 2025-12-05  
**Status**: Current

---

## Table of Contents

1. [Overview](#overview)
2. [Package Structure](#package-structure)
3. [Architecture Patterns](#architecture-patterns)
4. [Core Components](#core-components)
5. [View System](#view-system)
6. [Styling System](#styling-system)
7. [Data Flow](#data-flow)
8. [Key Features](#key-features)
9. [Development Guide](#development-guide)
10. [Performance Optimization](#performance-optimization)

---

## Overview

### Purpose

The TUI (Terminal User Interface) provides an **interactive, keyboard-driven interface** for managing and exploring the cortex framework. It's built on the Textual framework and follows a modern reactive architecture.

### Key Characteristics

- **230KB Consolidated Application**: Single `main.py` with all views integrated
- **Package-Based Structure**: Proper Python package with organized submodules
- **Reactive State Management**: Textual's reactive properties for automatic UI updates
- **TCSS Styling**: External CSS-like styling for maintainability
- **Type-Safe**: Dedicated type definitions for all data models
- **Keyboard-First**: Fully navigable without mouse

### Technology Stack

```
Textual 0.47+  → TUI framework (reactive, CSS-like styling)
Rich 13.x      → Terminal formatting and rendering
Python 3.9+    → Runtime with dataclasses and type hints
```

---

## Package Structure

### Directory Organization

```
claude_ctx_py/tui/
├── __init__.py              # Package initialization
├── main.py                  # Main application (230KB)
├── types.py                 # Type definitions (2.3KB)
├── constants.py             # Global constants (2.3KB)
├── styles.tcss              # Textual CSS styles (4.5KB)
├── widgets.py               # Custom widgets (13KB)
│
├── screens/                 # View/screen definitions
│   ├── agents.py
│   ├── modes.py
│   ├── rules.py
│   ├── skills.py
│   ├── workflows.py
│   ├── scenarios.py
│   ├── profiles.py
│   ├── mcp.py
│   ├── ai_assistant.py
│   └── memory.py
│
├── widgets/                 # Reusable widget components
│   ├── data_table.py
│   ├── status_bar.py
│   └── notification.py
│
├── dialogs/                 # Modal dialogs
│   ├── rating.py            # Skill rating dialog
│   ├── confirm.py           # Confirmation dialog
│   └── input.py             # Text input dialog
│
└── layouts/                 # Layout components
    └── command_palette.py   # Fuzzy search command palette
```

### Key Files

**main.py** (230KB)

- Main `ClaudeCtxApp` class
- All view implementations
- Command palette integration
- Keyboard handling
- State management

**types.py** (2.3KB)

- `@dataclass` definitions for all data models
- `RuleNode`, `AgentTask`, `WorkflowInfo`, `ModeInfo`, etc.
- Type-safe data structures

**constants.py** (2.3KB)

- View titles and descriptions
- Key bindings configuration
- Profile descriptions
- Export categories

**styles.tcss** (4.5KB)

- Super Saiyan theme colors
- Component styling rules
- Dialog and overlay styles
- Animation definitions

---

## Architecture Patterns

### 1. Reactive State Management

Uses Textual's `Reactive` properties for automatic UI updates:

```python
from textual.reactive import Reactive

class ClaudeCtxApp(App):
    """Main TUI application."""
    
    # Reactive properties - UI updates automatically
    active_agents: Reactive[List[str]] = Reactive([])
    active_modes: Reactive[List[str]] = Reactive([])
    current_view: Reactive[str] = Reactive("overview")
    
    def watch_active_agents(self, new_value: List[str]) -> None:
        """Called automatically when active_agents changes."""
        self.notify(f"{len(new_value)} agents active")
        self.refresh_agent_view()
```

**Benefits**:

- ✅ No manual UI refresh calls
- ✅ Automatic change propagation
- ✅ Eliminates state synchronization bugs

### 2. Single-Page Application (SPA)

All views share the same window with view switching:

```python
def switch_to_view(self, view_name: str) -> None:
    """Switch to a different view."""
    self.current_view = view_name  # Triggers reactive update
    
    if view_name == "agents":
        self.load_agents_view()
    elif view_name == "modes":
        self.load_modes_view()
    # ... etc
```

### 3. Dependency Injection

Core modules injected into views:

```python
class AgentsView:
    def __init__(self, app: ClaudeCtxApp):
        self.app = app
        # Access core modules
        self.agent_mgr = app.core.agents
        self.skills_mgr = app.core.skills
```

### 4. Command Pattern

Actions abstracted as commands for keyboard and palette:

```python
COMMANDS = {
    "agents_list": ("List all agents", lambda: self.switch_to_view("agents")),
    "mode_activate": ("Activate mode", lambda: self.activate_selected_mode()),
    "export_agents": ("Export agents", lambda: self.export_view("agents")),
}
```

---

## Core Components

### 1. ClaudeCtxApp (Main Application)

**Location**: `tui/main.py`

The central application class that orchestrates all views and state:

```python
class ClaudeCtxApp(App):
    \"\"\"Main TUI application for cortex management.\"\"\"
    
    CSS_PATH = "styles.tcss"
    TITLE = "Cortex Manager"
    
    # Reactive state
    active_agents: Reactive[List[str]] = Reactive([])
    active_modes: Reactive[List[str]] = Reactive([])
    current_view: Reactive[str] = Reactive("overview")
    
    # Key bindings
    BINDINGS = [
        ("1", "view_overview", "Overview"),
        ("2", "view_agents", "Agents"),
        ("3", "view_modes", "Modes"),
        ("ctrl+p", "command_palette", "Command Palette"),
        ("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        \"\"\"Create child widgets.\"\"\"
        yield Header()
        yield Container(
            self.create_view_container(),
            id="main-container"
        )
        yield AdaptiveFooter()
    
    def on_mount(self) -> None:
        \"\"\"Initialize on startup.\"\"\"
        self.load_core_modules()
        self.load_initial_view()
        self.start_background_tasks()
```

**Responsibilities**:

- View coordination
- State management
- Keyboard routing
- Background task management
- Module initialization

### 2. Type System

**Location**: `tui/types.py`

Type-safe data models using `@dataclass`:

```python
@dataclass
class AgentTask:
    \"\"\"Represents an active agent task.\"\"\"
    agent_id: str
    agent_name: str
    workstream: str
    status: str  # "active", "completed", "failed"
    progress: int  # 0-100
    category: str = "general"
    started: Optional[float] = None
    completed: Optional[float] = None
    description: str = ""
    source_path: Optional[str] = None

@dataclass
class ModeInfo:
    \"\"\"Represents a behavioral mode.\"\"\"
    name: str
    status: str  # "active" or "inactive"
    purpose: str
    description: str
    path: Path

@dataclass
class MemoryNote:
    \"\"\"Represents a memory vault note.\"\"\"
    title: str
    note_type: str  # knowledge, projects, sessions, fixes
    path: str
    modified: datetime
    tags: List[str]
    snippet: str
```

**Benefits**:

- Type checking with mypy
- IDE autocomplete
- Self-documenting code
- Immutability by default

### 3. Constants System

**Location**: `tui/constants.py`

Centralized configuration:

```python
# View key bindings
PRIMARY_VIEW_BINDINGS = [
    ("1", "overview", "Overview"),
    ("2", "agents", "Agents"),
    ("3", "modes", "Modes"),
    ("4", "rules", "Rules"),
    ("5", "skills", "Skills"),
    ("6", "workflows", "Workflows"),
    ("7", "mcp", "MCP"),
    ("8", "profiles", "Profiles"),
    ("9", "export", "Export"),
    ("0", "ai_assistant", "AI Assistant"),
    ("A", "assets", "Assets"),
    ("M", "memory", "Memory"),
]

# View titles with icons
VIEW_TITLES = {
    "overview": f"{Icons.METRICS} Overview",
    "agents": f"{Icons.CODE} Agents",
    "modes": f"{Icons.FILTER} Modes",
    "skills": f"{Icons.CODE} Skills",
    "memory": "🧠 Memory Vault",
}

# Profile descriptions
PROFILE_DESCRIPTIONS = {
    "minimal": "Load minimal profile (essential agents only)",
    "frontend": "Load frontend profile (TypeScript + review)",
    "backend": "Load backend profile (Python + security)",
    "devops": "Load devops profile (infrastructure & deploy)",
}
```

---

## View System

### View Lifecycle

Each view follows a consistent lifecycle pattern:

```
1. Initialization  → __init__()
2. Composition     → compose()
3. Mounting        → on_mount()
4. Data Loading    → load_data()
5. UI Setup        → setup_ui()
6. Event Handling  → on_<event>()
7. Unmounting      → on_unmount()
```

### View Implementation Pattern

```python
class AgentsView(Container):
    \"\"\"Agents management view.\"\"\"
    
    def __init__(self, app: ClaudeCtxApp):
        super().__init__()
        self.app = app
        self.agents_data: List[Agent] = []
        self.table: Optional[DataTable] = None
    
    def compose(self) -> ComposeResult:
        \"\"\"Create child widgets.\"\"\"
        yield DataTable(id="agents-table")
        yield Static("Loading agents...", id="status")
    
    async def on_mount(self) -> None:
        \"\"\"Initialize on mount.\"\"\"
        # 1. Get reference to widgets
        self.table = self.query_one(DataTable)
        
        # 2. Load data
        await self.load_agents()
        
        # 3. Setup UI
        self.setup_table()
        
        # 4. Start refresh timer
        self.set_interval(5.0, self.refresh_data)
    
    async def load_agents(self) -> None:
        \"\"\"Load agents from core module.\"\"\"
        self.agents_data = await self.app.core.agents.list_all()
    
    def setup_table(self) -> None:
        \"\"\"Setup data table.\"\"\"
        self.table.add_columns(
            "Name", "Status", "Dependencies", "Category"
        )
        for agent in self.agents_data:
            self.table.add_row(
                agent.name,
                "✅" if agent.active else "⭕",
                ", ".join(agent.dependencies),
                agent.category
            )
    
    async def on_key(self, event: events.Key) -> None:
        \"\"\"Handle key presses.\"\"\"
        if event.key == "enter":
            await self.activate_selected()
        elif event.key == "d":
            await self.deactivate_selected()
        elif event.key == "i":
            await self.show_info()
```

### Primary Views

**1. Overview (Key: 1)**

- System metrics dashboard
- Active agents/modes/rules summary
- Quick stats

**2. Agents (Key: 2)**

- Agent list with status
- Activation/deactivation
- Dependency visualization
- Agent details

**3. Modes (Key: 3)**

- Mode list with status
- Mode activation
- Mode descriptions

**4. Rules (Key: 4)**

- Rule list with status
- Rule activation
- Rule categories

**5. Skills (Key: 5)**

- Skill catalog
- Rating system (Ctrl+R)
- Skill details
- Category filtering

**6. Workflows (Key: 6)**

- Workflow list
- Workflow execution
- Progress tracking

**7. MCP (Key: 7)**

- MCP server list
- Server status
- Server diagnostics
- Documentation viewer

**8. Profiles (Key: 8)**

- Profile templates
- Profile loading
- Quick profile switch

**9. Export (Key: 9)**

- Context export
- Category selection
- Clipboard integration

**0. AI Assistant (Key: 0)**

- AI recommendations
- Auto-activation
- Workflow predictions

**A. Assets (Key: A)**

- Asset manager
- Installation wizard
- Asset catalog

**M. Memory (Key: M)**

- Memory vault notes
- Note browser
- Search interface

---

## Styling System

### TCSS (Textual CSS)

**Location**: `tui/styles.tcss`

External stylesheet for all TUI components:

```tcss
/* Super Saiyan Mode Theme */
$primary: #3b82f6;       /* Blue */
$secondary: #8b5cf6;     /* Purple */
$accent: #06b6d4;        /* Cyan */
$success: #10b981;       /* Green */
$warning: #f59e0b;       /* Orange */
$error: #ef4444;         /* Red */
$surface: #050714;       /* Dark background */
$text: #f8fafc;          /* Light text */

/* DataTable Styling */
DataTable {
    height: 1fr;
    background: $surface-lighten-1;
    border: solid $primary;
    padding: 0 1;
}

DataTable > .datatable--header {
    background: $surface-lighten-2;
    color: $accent;
    text-style: bold;
}

DataTable:focus > .datatable--cursor {
    background: $primary;
    color: white;
    text-style: bold;
    border: heavy $accent;
}

/* Button Styling */
Button {
    background: $primary;
    color: white;
    border: solid $primary;
    text-style: bold;
}

Button:hover {
    background: $accent;
    border: solid $accent;
    transition: background 150ms, border 150ms;
}

/* Dialog Styling */
#dialog {
    align: center middle;
    width: 50%;
    background: $surface-lighten-1;
    border: thick $accent;
    padding: 1 2;
    opacity: 0;
}

#dialog.visible {
    opacity: 1;
    transition: opacity 250ms;
}
```

### Theme Customization

To customize the theme, edit `styles.tcss` color variables:

```tcss
/* Custom Theme Example */
$primary: #your-color;
$secondary: #your-color;
$accent: #your-color;
```

Changes are hot-reloaded when running in development mode.

---

## Data Flow

### Data Flow Architecture

```
┌──────────────────────────────────────────────────────────┐
│ User Input (Keyboard)                                     │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ Event Handlers (on_key, on_button_pressed)               │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ Action Methods (activate_agent, load_mode)               │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ Core Business Logic (core/agents.py, core/modes.py)      │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ File System / Database                                    │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ Reactive State Update (self.active_agents = new_list)    │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ watch_* Methods (watch_active_agents)                     │
└────────────────┬─────────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────────────┐
│ UI Refresh (table.refresh(), notify())                    │
└──────────────────────────────────────────────────────────┘
```

### Example: Activating an Agent

```python
# 1. User presses Enter on selected agent
async def on_key(self, event: events.Key) -> None:
    if event.key == "enter":
        # 2. Call action method
        await self.activate_selected_agent()

# 3. Action method interacts with core
async def activate_selected_agent(self) -> None:
    selected_row = self.table.cursor_row
    agent_name = self.agents_data[selected_row].name
    
    # 4. Call core business logic
    result = await self.app.core.agents.activate(agent_name)
    
    # 5. Update reactive state
    self.app.active_agents = result.active_agents
    
    # 6. Notification
    self.notify(f"Activated: {agent_name}")

# 7. Reactive watch updates UI
def watch_active_agents(self, new_value: List[str]) -> None:
    # 8. Refresh table to show new status
    self.refresh_agents_table()
```

---

## Key Features

### 1. Command Palette

**Trigger**: `Ctrl+P`

Fuzzy search across all TUI commands:

```python
class CommandPalette:
    \"\"\"Fuzzy search command palette.\"\"\"
    
    def compose(self) -> ComposeResult:
        yield Static("🔍 Command Palette", id="palette-title")
        yield Input(placeholder="Type to search...", id="palette-input")
        yield DataTable(id="palette-results")
        yield Static("Enter=Execute | Esc=Close", id="palette-help")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        \"\"\"Filter commands as user types.\"\"\"
        query = event.value.lower()
        matches = self.fuzzy_match(query, ALL_COMMANDS)
        self.update_results(matches)
    
    def fuzzy_match(self, query: str, commands: List[Command]) -> List[Command]:
        \"\"\"Simple fuzzy matching.\"\"\"
        return [
            cmd for cmd in commands
            if query in cmd.name.lower() or query in cmd.description.lower()
        ]
```

**Features**:

- Real-time filtering
- Keyboard navigation (↑/↓)
- Fuzzy matching on name and description
- Execute with Enter
- 50+ available commands

### 2. Adaptive Footer

Context-aware help display:

```python
class AdaptiveFooter(Static):
    \"\"\"Footer that shows context-specific keybindings.\"\"\"
    
    def update_for_view(self, view_name: str) -> None:
        \"\"\"Update help text for current view.\"\"\"
        bindings = VIEW_BINDINGS.get(view_name, [])
        help_text = " | ".join(
            f"{key}={desc}" for key, desc in bindings
        )
        self.update(help_text)
```

**Example Outputs**:

- Agents view: `Enter=Activate | d=Deactivate | i=Info | g=Graph`
- Skills view: `Enter=View | Ctrl+R=Rate | f=Filter`

### 3. Real-Time Notifications

Toast-style notifications:

```python
def notify(self, message: str, severity: str = "info") -> None:
    \"\"\"Show toast notification.\"\"\"
    styles = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red",
    }
    self.app.notify(
        message,
        title="Status",
        severity=severity,
        timeout=3.0
    )
```

### 4. Modal Dialogs

Reusable dialog system:

```python
# Confirmation dialog
result = await self.app.show_dialog(
    title="Confirm Action",
    message="Deactivate all agents?",
    buttons=["Yes", "No"]
)

# Input dialog
value = await self.app.show_input_dialog(
    title="Enter Name",
    placeholder="Mode name..."
)

# Rating dialog (skills)
rating = await self.app.show_rating_dialog(
    skill_name="api-design-patterns",
    current_rating=None
)
```

---

## Development Guide

### Adding a New View

**Step 1**: Define view key binding in `constants.py`:

```python
PRIMARY_VIEW_BINDINGS = [
    # ... existing bindings
    ("X", "myview", "My View"),
]

VIEW_TITLES = {
    # ... existing titles
    "myview": "🚀 My View",
}
```

**Step 2**: Implement view in `main.py`:

```python
def load_myview(self) -> None:
    \"\"\"Load my custom view.\"\"\"
    # Clear current view
    self.clear_view_container()
    
    # Create table
    table = DataTable()
    table.add_columns("Column 1", "Column 2")
    
    # Load data
    data = self.load_my_data()
    for item in data:
        table.add_row(item.col1, item.col2)
    
    # Add to container
    self.view_container.mount(table)
    
    # Update state
    self.current_view = "myview"
```

**Step 3**: Add key binding handler:

```python
def action_view_myview(self) -> None:
    \"\"\"Action to switch to myview.\"\"\"
    self.load_myview()
```

**Step 4**: Add to command palette:

```python
COMMANDS = {
    # ... existing commands
    "myview_open": ("Open My View", self.load_myview),
}
```

### Adding a Custom Widget

**Step 1**: Create widget class:

```python
from textual.widgets import Static
from rich.text import Text

class StatusIndicator(Static):
    \"\"\"Custom status indicator widget.\"\"\"
    
    def __init__(self, status: str):
        super().__init__()
        self.status = status
    
    def render(self) -> Text:
        \"\"\"Render the status indicator.\"\"\"
        icons = {
            "active": "✅",
            "inactive": "⭕",
            "error": "❌",
        }
        icon = icons.get(self.status, "❓")
        return Text(f"{icon} {self.status.title()}")
```

**Step 2**: Use in views:

```python
def compose(self) -> ComposeResult:
    yield StatusIndicator("active")
```

### Debugging Tips

**1. Enable Textual DevTools**:

```bash
$ textual console
# In another terminal
$ cortex tui
```

**2. Add Debug Logging**:

```python
from textual import log

log("Debug message:", variable)
log.info("Info message")
log.warning("Warning message")
log.error("Error message")
```

**3. Inspect Widget Tree**:

Press `Ctrl+\\` to toggle widget tree inspector.

---

## Performance Optimization

### Best Practices

**1. Lazy Loading**

Only load data when view is active:

```python
async def on_mount(self) -> None:
    if self.current_view == "agents":
        await self.load_agents()  # Load only when needed
```

**2. Debounced Search**

Debounce search input to reduce updates:

```python
from textual.timer import Timer

def on_input_changed(self, event: Input.Changed) -> None:
    # Cancel previous timer
    if hasattr(self, "_search_timer"):
        self._search_timer.stop()
    
    # Start new timer (300ms delay)
    self._search_timer = self.set_timer(
        0.3,
        lambda: self.perform_search(event.value)
    )
```

**3. Virtual Scrolling**

For large lists (>100 items), use pagination:

```python
PAGE_SIZE = 50

def load_page(self, page: int) -> None:
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    items = self.all_items[start:end]
    self.table.clear()
    for item in items:
        self.table.add_row(...)
```

**4. Efficient Redraws**

Update only changed cells:

```python
# ❌ Inefficient - rebuilds entire table
def update_table(self):
    self.table.clear()
    for item in self.items:
        self.table.add_row(...)

# ✅ Efficient - updates specific cell
def update_agent_status(self, agent_name: str, new_status: str):
    row_index = self.find_row_by_name(agent_name)
    self.table.update_cell(row_index, "status", new_status)
```

### Performance Metrics

| Operation | Target | Notes |
|-----------|--------|-------|
| View switch | <200ms | Includes data load |
| Table render (100 rows) | <100ms | Initial render |
| Search filter | <50ms | With debouncing |
| Keyboard response | <16ms | 60fps target |
| Memory usage | <50MB | With all views |

---

## Screenshots

Fresh screenshots available in `docs/assets/images/screenshots/december-2025/`:

- `agents-view.png` - Agents view
- `ai-assist-view.png` - AI assistant view
- `ai-watch-mode.png` - AI watch mode
- `asset-manager.png` - Asset manager
- `backup-manager.png` - Backup manager
- `cli-usage.png` - CLI usage
- `command-palette.png` - Command palette
- `config-wizard.png` - Setup wizard
- `export-view.png` - Export view
- `flags-view.png` - Flags explorer
- `galaxy-view.png` - Agent galaxy
- `hooks-manager.png` - Hooks manager
- `mcp-view.png` - MCP servers
- `memory-vault.png` - Memory vault
- `modes-view.png` - Modes view
- `principles-view.png` - Principles view
- `profiles-view.png` - Profiles view
- `scenarios-view.png` - Scenarios view
- `shortcuts-help.png` - Shortcuts/help overlay
- `skills-view.png` - Skills catalog
- `slash-commands-view.png` - Slash commands
- `workflows-view.png` - Workflows
- `worktrees-view.png` - Worktrees

---

## Related Documentation

- [TUI Navigation Summary](../tui/tui-navigation-summary.md)
- [TUI Keyboard Reference](../tui/tui-keyboard-reference.md)
- [TUI Entity Guide](../tui/tui-entity-guide.md)
- [TUI MCP View](../tui/tui-mcp-view.md)
- [Master Architecture Document](../../architecture/MASTER_ARCHITECTURE.md)

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-05 | Initial TUI architecture documentation | System Architect |

---

**Document Status**: ✅ Current  
**Maintainer**: Core Team
