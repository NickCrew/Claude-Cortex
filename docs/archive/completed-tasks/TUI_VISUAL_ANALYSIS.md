# Cortex TUI - Visual Implementation Analysis

## Current Architecture Overview

The TUI implementation consists of two distinct approaches working in parallel:

### 1. Rich-based TUI (`tui.py`) - PRIMARY IMPLEMENTATION

- **Framework**: Rich library for terminal rendering
- **Approach**: Manual state management with console-based rendering
- **Status**: Production-ready, feature-complete

### 2. Textual-based TUI (`tui_textual.py`) - EXPERIMENTAL

- **Framework**: Textual library (advanced terminal UI framework)
- **Approach**: Reactive component-based architecture
- **Status**: Minimal implementation (agents view only)

### 3. Extensions (`tui_extensions.py`)

- Profile management view (ProfileViewMixin)
- Context export view (ExportViewMixin)
- Setup wizard view (WizardViewMixin)

---

## Rich-Based TUI Visual Components

### Core Visual Architecture

#### Layout System

```
┌─────────────────────────────────────┐
│          HEADER (size=5)            │
│  "claude-ctx: [ViewName]"           │
│  "Press 1-9 for views, ? for help"  │
├─────────────────────────────────────┤
│                                     │
│         BODY (flexible)             │
│    (View-specific content)          │
│                                     │
├─────────────────────────────────────┤
│  FOOTER (size=4)                    │
│  Status, view, filter, connection   │
└─────────────────────────────────────┘
```

#### Component Hierarchy

- **Layout** (top-level container)
  - Header Panel
  - Body Panel (switches based on current view)
  - Footer Panel

---

## Color Schemes & Styling

### Current Color Palette

#### Primary Colors

- **Cyan** (`cyan`): Primary accent for names, links, highlights
- **Magenta** (`bold magenta`): Table headers
- **Green** (`bold green`): Active status, success states
- **Yellow** (`yellow`): Inactive status, warnings
- **Blue** (`bold blue`): Complete/finished states
- **Red** (`bold red`): Error states

#### Text Styles

- **Bold**: Headings, labels, important text
- **Dim**: Supplementary info, hints, timestamps
- **Reverse**: Selected row highlighting
- **Bold + Color**: Status badges (e.g., "Active", "Inactive")

### Status Color Mapping

```python
Status Colors:
- "active"    → bold green
- "inactive"  → yellow
- "running"   → bold green
- "complete"  → bold blue
- "pending"   → yellow
- "paused"    → cyan
- "error"     → bold red
```

---

## View Components & Visual Elements

### 1. Overview View

**Purpose**: Dashboard showing system status

**Visual Elements**:

- System Status section
  - Agents count: "5/10 active"
  - Modes count: "3/8 active"
  - Rules count: "5/12 active"
  - Skills count: "15 installed"
- Active Workflows section
- Quick Actions section (i, r, ?)

**Styling**:

- Headers: `bold yellow`
- Status indicators: `green`
- Navigation hints: `dim`
- Dividers: `━` characters with `dim` style

### 2. Agents View

**Purpose**: Browse and toggle agent statuses

**Components**:

- Agent List Table (expandable to details panel)
  - Selection indicator: `>` or empty
  - Name: `cyan` style
  - Status: Color-coded text (green/yellow)
  - Category: Standard text
  - Tier: Standard text
  - Requires: Dependencies list
  
**Features**:

- Selected row highlighted with `reverse` style
- Viewport scrolling (shows ~8 items max)
- Details panel (split view on Enter)
  - Name, Status, Category, Tier
  - Requirements and Recommendations

**Interactions**:

- Up/Down (↑/↓ or k/j): Navigate
- Space: Toggle agent activation
- Enter: Show/hide details
- /: Filter by name/category/tier

### 3. Modes View

**Purpose**: Browse and toggle behavioral modes

**Components**:

- Modes List Table
  - Selection indicator
  - Name: `cyan`
  - Status: Color-coded (green=active, yellow=inactive)
  - Description: Truncated to 80 chars

**Details Panel**:

- Name, Status, Description, File path

### 4. Rules View

**Purpose**: Browse and toggle execution rules

**Components**:

- Rules List Table
  - Selection indicator
  - Name: `cyan`
  - Status: Color-coded
  - Category: Tagged (workflow, quality, efficiency, security)
  - Description: Truncated to 60 chars

**Details Panel**:

- Name, Status, Category, Description, File path

### 5. Skills View

**Purpose**: Browse installed skills with metrics

**Components**:

- Skills List Table
  - Selection indicator
  - Name: `cyan`
  - Category: 15-char width
  - Uses: Right-aligned number
  - Last Used: Formatted timestamp
  - Tokens Saved: Right-aligned number

**Metrics View** (toggleable with 'm'):

- Activation Count
- Total Tokens Saved
- Average Tokens per use
- Success Rate (percentage)
- Last Activation timestamp

**Features**:

- Skill validation ('v' key)
- Metrics display ('m' key)
- Community browser stub ('c' key)

### 6. Workflows View

**Purpose**: Monitor and manage workflows

**Components**:

- Workflow List Table
  - Selection indicator
  - Name: `cyan`, 30-char width
  - Status: Color-coded text
  - Progress: Visual progress bar with percentage
    - Format: `[████████░░] 75%`
    - Uses block characters (█ filled, ░ empty)
  - Started: Elapsed time display
  - Description: Truncated

**Details Panel**:

- Workflow name, description, status
- Elapsed time
- Progress percentage
- Step list with indicators:
  - `→` for current step (bold green)
  - `✓` for completed steps (dim green)
  - `○` for pending steps (dim)

**Status Visualization**:

```
pending  → yellow
running  → bold green
paused   → cyan
complete → bold blue
error    → bold red
```

### 7. Orchestration View

**Purpose**: Show parallel execution status

**Layout**:

```
┌─────────────────────────────────────┐
│ Workstreams (size=15)               │
│ ASCII diagram showing parallel flow │
├─────────────────────────────────────┤
│ Active Agents Table (flexible)      │
│ [Agent-1] primary    | Progress     │
│ [Agent-2] quality    | Progress     │
├─────────────────────────────────────┤
│ Metrics Panel (size=8)              │
│ Parallel Efficiency: 87%            │
│ Overall Progress: 78%               │
│ Active Agents: 2/3                  │
└─────────────────────────────────────┘
```

**Agent Table Columns**:

- Agent: `cyan`, 20-char width
- Workstream: 15-char width
- Status: Color-coded
- Progress: 30-char progress bar

**Progress Bar Format**:

- Uses block characters: `█` (filled), `░` (empty)
- Shows percentage: `[██████████░░░░░░░░░░] 75%`

**Metrics Display**:

- Parallel Efficiency: `green`
- Overall Progress: `cyan`
- Estimated Completion: `magenta`

### 8. Profile View

**Purpose**: Manage reasoning profiles

**Components**:

- Profile List Table
  - Selection indicator
  - Profile: `cyan`
  - Type: Color-coded (`yellow` for built-in, `blue` for saved)
  - Description: 40-char width
  - Status: Active indicator

### 9. Export View

**Purpose**: Export context in various formats

**Components**:

- Export Options Checklist
  - Checkbox: `[x]` or `[ ]`
  - Options: core, rules, modes, agents, mcp_docs, skills
  - Selected option highlighted with `reverse`

- Format Selector
  - Displays: `[JSON]` (selected) vs `XML` vs `Markdown`

- Preview Section
  - Shows first 10 lines of export
  - Line count indicator for truncation

### 10. Help Panel

**Purpose**: Comprehensive keyboard reference

**Structure**:

```
═══════════════════════════════════════════════════════════
         CLAUDE CONTEXT TUI - KEYBOARD REFERENCE
═══════════════════════════════════════════════════════════

VIEWS (1-9)       │ NAVIGATION     │ ACTIONS
─────────────────────────────────────────────────────────
1  Overview       │ ↑/k  Up        │ Space  Toggle
2  Agents         │ ↓/j  Down      │ Enter  Details
...               │ PgUp Page up   │ /      Filter
─────────────────────────────────────────────────────────

CONTEXT-SPECIFIC KEYS (depend on current view)
─────────────────────────────────────────────────────────
Agents:      Space=toggle, Enter=details, /=filter
Modes:       Space=toggle, Enter=details, /=filter
...
```

**Styling**:

- Headers: `bold blue` and `bold cyan`
- Separators: `dim` dividing lines
- Content: Standard text

---

## Table Components

### Standard Table Structure

```python
Table(
    title="Table Name",
    show_header=True,
    header_style="bold magenta",
    show_lines=False,
    expand=True,
    title_style="bold cyan",
)
```

### Column Configuration Patterns

**Typical Column Setup**:

```python
table.add_column("", width=2, no_wrap=True)      # Selection indicator
table.add_column("Name", style="cyan", no_wrap=True)
table.add_column("Status", width=10, no_wrap=True)
table.add_column("Category", width=15, no_wrap=True)
table.add_column("Description", overflow="fold")  # Last column wraps
```

### Row Highlighting

- **Selected row**: `style="reverse"` (inverts colors)
- **Normal row**: `style=None`
- **Indicator**: `">"` for selected, `""` for unselected

### Text Styling in Cells

- Complex cells use Rich `Text` objects for multi-styled content
- Example:

  ```python
  status_text = Text("Active", style="bold green")
  table.add_row(indicator, name, status_text, category, tier)
  ```

---

## Panel Components

### Panel Structure

```python
Panel(
    content,           # Text, Table, Layout, etc.
    title="Title",
    subtitle="Controls",
    border_style="cyan",
    padding=(0, 1),    # (vertical, horizontal)
    expand=True,
)
```

### Common Panel Styles

- Details panels: `border_style="cyan"`
- Help panels: `border_style="yellow"`
- Status panels: `border_style="green"`
- Error panels: `border_style="red"`

---

## Progress Bar Visualization

### Block Character Progress Bars

**Format**: `[████████░░] 75%`

**Implementation**:

```python
bar_width = 10
filled = int((progress / 100) * bar_width)
progress_text = f"[{'█' * filled}{'░' * (bar_width - filled)}] {progress}%"
```

**Visual Examples**:

- 0%: `[░░░░░░░░░░] 0%`
- 25%: `[██░░░░░░░░] 25%`
- 50%: `[█████░░░░░░] 50%`
- 75%: `[███████░░░░] 75%`
- 100%: `[██████████] 100%`

---

## Filter UI

### Filter Entry Mode

**Status Message** during filtering:

```
"Filter: [accumulated_text]"
"Type to filter (Esc to cancel)..."
```

**Input Handling**:

- Backspace: Remove last character
- Printable chars: Add to filter
- Enter: Apply filter, reset selection
- Escape: Cancel, clear filter text

**Result Display**:

```
"Filter applied: 5 agents matched"
```

---

## Footer Status Bar

### Status Bar Layout

```
[View: Agents] Space=toggle, Enter=details, /=filter | Status: Agent activated | Filter: search_text | Showing 5/10 agents | [●] Connected
```

**Components**:

1. **View indicator**: `[View: ViewName]` in `bold cyan`
2. **Hint**: View-specific key hint in `dim`
3. **Status message**: User action feedback in `bold`
4. **Filter indicator**: Current filter text in `cyan`
5. **Count info**: Item count in `dim` (agents view only)
6. **Connection**: `[●]` in `green` + "Connected" in `dim`

---

## Visual Enhancement Opportunities

### Current Limitations

1. **Limited Theming**: Hard-coded color scheme, no user configuration
2. **No Dark/Light Mode Support**: Always uses terminal default theme
3. **Static Layouts**: No dynamic layout adjustment
4. **Basic Visual Feedback**: Limited animation/transition
5. **No Custom Styling**: No CSS/theme files for customization
6. **Sparse Information Density**: Could show more data per view

### Enhancement Areas

#### 1. Theme System

- Create theme configuration files
- Support light/dark mode auto-detection
- Allow user-defined color schemes
- Implement theme switching on-the-fly

#### 2. Advanced Visualizations

- Better progress indicators (percentage-based coloring)
- Trend indicators (up/down arrows with colors)
- Dependency graphs for agents
- Timeline views for workflows
- Heatmaps for skill usage

#### 3. Interactive Elements

- Modal dialogs for confirmations
- Progress spinners during loading
- Collapsible sections
- Sortable columns
- Inline editing for items

#### 4. Information Architecture

- Sidebar navigation
- Breadcrumb trails
- Tabs for multi-view sections
- Expandable tree views for hierarchies
- Card-based layouts

#### 5. Visual Polish

- Smooth transitions
- Loading animations
- Pulsing indicators for active items
- Gradient effects (if terminal supports)
- Icon support (if terminal supports Unicode)

#### 6. Accessibility

- High contrast mode
- Larger text option
- Reduce motion option
- Screen reader considerations

---

## Data Display Patterns

### Lists/Tables Pattern

- Selection indicator column
- Primary data column (styled)
- Status column (color-coded)
- Secondary info columns
- Last column with descriptions (wrappable)

### Details Pattern

- Label/Value pairs
- Bold labels for emphasis
- Status indicators with styles
- Nested information with indentation
- Path information in dim style

### Status Indicators Pattern

- Color-coded text labels
- Icon replacements (→, ✓, ○ for steps)
- Progress bars with percentages
- Elapsed time formatting
- Count displays (x/y format)

---

## Text Rendering Techniques

### Date/Time Formatting

- ISO format with timestamp: `dt.strftime("%Y-%m-%d %H:%M")`
- Elapsed time: `f"{hours}h {minutes}m ago"`
- Timestamps: `"%Y-%m-%d %H:%M:%S"`

### Number Formatting

- Token counts: Thousands separator with `:,` format
- Percentages: `f"{value:.1%}"` for decimals, `"{:.1f}%"` for manual
- Large numbers: Comma-separated or human-readable units

### Text Truncation

- Fixed-width columns: Truncate with `[:40]` + `"..."`
- Dynamic wrapping: Use `overflow="fold"` in table columns
- Description fields: Show first N chars then ellipsis

### Special Characters

- Selection indicator: `>` (chevron)
- Step indicators: `→` (current), `✓` (done), `○` (pending)
- Progress bars: `█` (filled), `░` (empty)
- Dividers: `━`, `─`, `═` (various weights)

---

## Navigation & Interaction Patterns

### View Switching (1-9 keys)

```
1 → overview
2 → agents
3 → modes
4 → rules
5 → skills
6 → workflows
7 → orchestrate
8 → profile
9 → export
```

### Movement Keys

```
↑/k/PgUp  → Move up / Page up
↓/j/PgDn  → Move down / Page down
Home      → Top of list
End       → Bottom of list
```

### Action Keys

```
Space     → Toggle current item (agent/mode/rule)
Enter     → Show/hide details panel
/         → Start filter mode
Esc       → Cancel filter / Clear details
?         → Toggle help
r         → Refresh current view
q         → Quit
```

### Context-Specific Keys

```
Agents:   v=validate (placeholder), Space=toggle, Enter=details
Skills:   v=validate, m=metrics, c=community
Modes:    Space=toggle, Enter=details
Rules:    Space=toggle, Enter=details
Workflows: Shift+R=run, Space=resume, s=stop (now wired)
```

---

## State Management

### ViewState Tracking

```python
@dataclass
class ViewState:
    selected_index: int = 0      # Currently selected item
    scroll_offset: int = 0       # Scroll position (reserved)
    filter_text: str = ""        # Current filter string
    show_details: bool = False   # Details panel visible
```

### TUIState Tracking

```python
@dataclass
class TUIState:
    current_view: str = "overview"           # Active view
    agents: List[AgentGraphNode] = []        # Loaded agents
    status_message: str = "..."              # Current status
    show_help: bool = False                  # Help visible
    view_states: Dict[str, ViewState] = {}   # Per-view state
    view_history: List[str] = []             # Navigation history
```

---

## Rendering Strategy

### Update Mechanism

- **Trigger**: State change detected
- **Condition**: `needs_update = True` set by key handler
- **Action**: `render()` called to clear and redraw entire layout
- **Performance**: Full screen refresh on each update (no incremental updates)

### Layout Reconstruction

```python
def create_layout(self) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="body"),
        Layout(name="footer", size=4),
    )
    layout["header"].update(self.create_header())
    layout["footer"].update(self.create_footer())
    
    # Route to view-specific renderer
    if self.state.current_view == "agents":
        if self.state.show_details:
            layout["body"].split_row(
                Layout(self.create_agent_table()),
                Layout(self.create_details_panel() or "", ratio=1),
            )
        else:
            layout["body"].update(self.create_agent_table())
```

---

## Component Reusability

### Mixins for View Composition

1. **ProfileViewMixin**: Profile management methods
2. **ExportViewMixin**: Export functionality
3. **WizardViewMixin**: Setup wizard views

### Shared Component Factory Methods

```python
create_header()              # Common header for all views
create_footer()              # Common footer for all views
create_help_panel()          # Comprehensive help
create_agent_table()         # Agent list table
create_agent_details_panel() # Agent details
create_modes_table()         # Modes table
create_mode_details_panel()  # Mode details
# ... and more
```

### Content Patterns

- **Panels**: Bordered content containers
- **Tables**: Tabular data display
- **Text**: Styled text with mixed formatting
- **Layouts**: Columnar/row-based arrangement

---

## Rich Library Usage

### Key Rich Components Used

1. **Console**: Main rendering interface
2. **Layout**: Grid-based layout system
3. **Panel**: Bordered container
4. **Table**: Data table with styling
5. **Text**: Rich text with inline styling
6. **Progress**: Progress bar (unused, could enhance)
7. **Live**: Live updating display (unused, could improve)

### Styling Capabilities Utilized

- Color names: cyan, magenta, green, yellow, blue, red, white, dim
- Style modifiers: bold, reverse, dim, italic, underline
- Style combinations: e.g., `"bold green"`, `"bold magenta"`

---

## Performance Characteristics

### Strengths

- Fast rendering with Rich library
- Minimal dependencies (Rich + PyYAML + Textual)
- Clean separation of state and rendering
- Efficient table rendering with built-in truncation

### Potential Issues

- Full-screen refresh on every state change (could optimize with Live)
- No incremental updates to specific regions
- File I/O on every view load (agents, modes, rules, skills)
- Repeated parsing of metadata for each render

### Optimization Opportunities

- Cache loaded data between renders
- Use Rich Live for incremental updates
- Implement lazy loading for large lists
- Add Progress bars for slow operations

---

## Summary of Visual Design

### Strengths

1. **Clean hierarchy**: Clear visual separation of concerns
2. **Consistent styling**: Unified color and layout patterns
3. **Good information density**: Fits lots of data in readable format
4. **Responsive navigation**: Quick view switching and item selection
5. **Helpful feedback**: Status messages and hints guide users

### Areas for Enhancement

1. **Theming**: No customizable color schemes
2. **Advanced visualization**: Limited to basic tables and text
3. **User experience**: No animations or transitions
4. **Accessibility**: No contrast modes or larger text options
5. **Documentation**: UI patterns not explicitly documented
