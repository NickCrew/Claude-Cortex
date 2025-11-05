# TUI Visual Enhancement Plan
## Single Default Theme - Maximum Visual Impact

**Goal**: Transform the TUI into a polished, professional interface with excellent default visuals.

**No Theme System**: One beautiful default design that works everywhere.

---

## Phase 1: Foundation - Visual Utilities (2-3 hours)

### 1.1 Icon System
**File**: `claude_ctx_py/tui_icons.py` (new)

```python
class Icons:
    """Unicode icons for terminal UI - guaranteed compatibility"""

    # Status indicators
    SUCCESS = "✓"
    READY = "○"
    RUNNING = "⏳"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"

    # Navigation
    SELECTED = "▶"
    UNSELECTED = " "
    ARROW_RIGHT = "→"
    ARROW_DOWN = "↓"

    # File types
    FILE = "📄"
    FOLDER = "📁"
    CODE = "💻"
    TEST = "🧪"
    DOC = "📝"

    # Actions
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    REFRESH = "↻"
    SEARCH = "🔍"
    FILTER = "⚑"

    # Progress
    COMPLETE = "█"
    INCOMPLETE = "░"
    BULLET = "•"

    # Connectors (for trees/hierarchies)
    BRANCH = "├─"
    LAST_BRANCH = "└─"
    PIPE = "│"
    SPACE = "  "

class StatusIcon:
    """Smart status icon with color"""

    @staticmethod
    def active() -> str:
        return f"[green]{Icons.SUCCESS}[/green] Active"

    @staticmethod
    def inactive() -> str:
        return f"[dim]{Icons.READY}[/dim] Ready"

    @staticmethod
    def running() -> str:
        return f"[yellow]{Icons.RUNNING}[/yellow] Running"

    @staticmethod
    def error() -> str:
        return f"[red]{Icons.ERROR}[/red] Failed"

    @staticmethod
    def warning() -> str:
        return f"[yellow]{Icons.WARNING}[/yellow] Warning"
```

### 1.2 Formatting Utilities
**File**: `claude_ctx_py/tui_format.py` (new)

```python
from datetime import datetime, timedelta
from typing import Union

class Format:
    """Formatting utilities for better data display"""

    @staticmethod
    def number(n: Union[int, float]) -> str:
        """Format numbers with thousands separators"""
        if isinstance(n, float):
            return f"{n:,.2f}"
        return f"{n:,}"

    @staticmethod
    def bytes(size: int) -> str:
        """Human-readable byte sizes"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}PB"

    @staticmethod
    def percent(value: float, total: float) -> str:
        """Format percentage with color coding"""
        if total == 0:
            return "0%"

        pct = (value / total) * 100

        if pct >= 90:
            color = "green"
        elif pct >= 70:
            color = "yellow"
        else:
            color = "red"

        return f"[{color}]{pct:.0f}%[/{color}]"

    @staticmethod
    def time_ago(dt: datetime) -> str:
        """Relative time formatting (e.g., '2m ago', '3h ago')"""
        now = datetime.now()
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days}d ago"
        elif diff < timedelta(days=30):
            weeks = diff.days // 7
            return f"{weeks}w ago"
        else:
            months = diff.days // 30
            return f"{months}mo ago"

    @staticmethod
    def duration(seconds: float) -> str:
        """Format duration (e.g., '2m 30s', '1h 5m')"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s" if secs > 0 else f"{mins}m"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text with ellipsis"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def list_items(items: list, max_items: int = 3) -> str:
        """Format list with overflow indicator"""
        if len(items) <= max_items:
            return ", ".join(items)

        shown = items[:max_items]
        remaining = len(items) - max_items
        return f"{', '.join(shown)} [dim]+{remaining} more[/dim]"
```

### 1.3 Progress Bar Enhancement
**File**: `claude_ctx_py/tui_progress.py` (new)

```python
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.console import Console

class ProgressBar:
    """Enhanced progress bar with color gradients"""

    @staticmethod
    def create_bar(total: int, description: str = "Progress") -> Progress:
        """Create a beautiful progress bar"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )

    @staticmethod
    def simple_bar(value: float, total: float, width: int = 20) -> str:
        """Simple inline progress bar with gradient colors"""
        if total == 0:
            return f"[dim]{'░' * width}[/dim] 0%"

        pct = value / total
        filled = int(pct * width)
        empty = width - filled

        # Color gradient based on percentage
        if pct >= 0.9:
            color = "green"
        elif pct >= 0.7:
            color = "yellow"
        elif pct >= 0.5:
            color = "blue"
        else:
            color = "red"

        bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
        return f"{bar} {pct * 100:.0f}%"
```

---

## Phase 2: Core Visual Enhancements (3-4 hours)

### 2.1 Enhanced Table Rendering
**File**: `claude_ctx_py/tui.py` - Update table creation

**Changes**:
1. Add subtle row separators
2. Better column alignment
3. Icon integration
4. Smart truncation
5. Color-coded values

**Example - Agents Table**:
```python
def _create_agents_table(self) -> Table:
    """Enhanced agents table with icons and better formatting"""
    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        row_styles=["", "dim"],  # Alternating row styles
        padding=(0, 1),  # Better spacing
        expand=True
    )

    # Columns with better widths
    table.add_column("", width=1)  # Selection indicator
    table.add_column("Status", width=10)
    table.add_column("Name", ratio=2)
    table.add_column("Files", width=12, justify="right")
    table.add_column("Last Used", width=12, justify="right")

    for idx, agent in enumerate(self.state.agents):
        # Selection indicator
        indicator = Icons.SELECTED if idx == self.state.selected_index else Icons.UNSELECTED

        # Status with icon and color
        status = self._format_agent_status(agent)

        # Name with icon
        name = f"{Icons.CODE} [cyan]{agent.name}[/cyan]"

        # File count
        file_count = f"[dim]{Format.number(agent.file_count)} files[/dim]" if agent.file_count > 0 else "[dim]—[/dim]"

        # Last used
        last_used = Format.time_ago(agent.last_used) if agent.last_used else "[dim]never[/dim]"

        table.add_row(indicator, status, name, file_count, last_used)

    return table

def _format_agent_status(self, agent) -> str:
    """Format agent status with icon and color"""
    if agent.status == "active":
        return StatusIcon.active()
    elif agent.status == "running":
        return StatusIcon.running()
    elif agent.status == "error":
        return StatusIcon.error()
    else:
        return StatusIcon.inactive()
```

### 2.2 Better Header Design
**File**: `claude_ctx_py/tui.py` - Update header rendering

```python
def _create_header(self, title: str, subtitle: str = "") -> Panel:
    """Enhanced header with better visual hierarchy"""

    # Main title with icon
    title_text = f"[bold cyan]🔧 {title.upper()}[/bold cyan]"

    if subtitle:
        title_text += f"\n[dim]{subtitle}[/dim]"

    # Add stats bar if available
    if hasattr(self.state, 'stats'):
        stats = self._format_stats_bar()
        title_text += f"\n{stats}"

    return Panel(
        title_text,
        border_style="cyan",
        padding=(0, 2)
    )

def _format_stats_bar(self) -> str:
    """Quick stats bar in header"""
    stats = self.state.stats

    parts = []

    if stats.get('total'):
        parts.append(f"[cyan]{Format.number(stats['total'])} total[/cyan]")

    if stats.get('active'):
        parts.append(f"[green]{Icons.SUCCESS} {stats['active']} active[/green]")

    if stats.get('pending'):
        parts.append(f"[yellow]{Icons.READY} {stats['pending']} pending[/yellow]")

    if stats.get('errors'):
        parts.append(f"[red]{Icons.ERROR} {stats['errors']} errors[/red]")

    return " [dim]│[/dim] ".join(parts)
```

### 2.3 Enhanced Footer
**File**: `claude_ctx_py/tui.py` - Update footer

```python
def _create_footer(self) -> Panel:
    """Enhanced footer with better key hints"""

    # Organize keys by category
    navigation = "[cyan]↑↓[/cyan] Navigate [dim]│[/dim] [cyan]1-9[/cyan] Views"
    actions = "[green]Space[/green] Toggle [dim]│[/dim] [green]Enter[/green] Activate"
    system = "[yellow]R[/yellow] Refresh [dim]│[/dim] [red]Q[/red] Quit"

    footer_text = f"{navigation} [dim]│[/dim] {actions} [dim]│[/dim] {system}"

    return Panel(
        footer_text,
        border_style="cyan",
        padding=(0, 2)
    )
```

---

## Phase 3: Advanced Visualizations (4-5 hours)

### 3.1 Dependency Graph Visualization
**File**: `claude_ctx_py/tui_graphs.py` (new)

```python
from rich.tree import Tree
from rich.console import Console

class DependencyGraph:
    """Visualize dependencies as a tree"""

    @staticmethod
    def create_tree(root_name: str, dependencies: dict) -> Tree:
        """Create a dependency tree visualization"""
        tree = Tree(
            f"[bold cyan]{Icons.FOLDER} {root_name}[/bold cyan]",
            guide_style="cyan"
        )

        DependencyGraph._add_dependencies(tree, dependencies)

        return tree

    @staticmethod
    def _add_dependencies(tree: Tree, deps: dict, level: int = 0):
        """Recursively add dependencies"""
        for name, children in deps.items():
            # Icon based on type
            icon = Icons.FILE if not children else Icons.FOLDER

            # Color based on level
            colors = ["cyan", "magenta", "green", "yellow", "blue"]
            color = colors[level % len(colors)]

            node = tree.add(f"[{color}]{icon} {name}[/{color}]")

            if children:
                DependencyGraph._add_dependencies(node, children, level + 1)

class WorkflowTimeline:
    """Visual timeline for workflow execution"""

    @staticmethod
    def create_timeline(steps: list) -> str:
        """Create a horizontal timeline"""
        timeline = []

        for idx, step in enumerate(steps):
            # Determine icon and color based on status
            if step['status'] == 'completed':
                icon = f"[green]{Icons.SUCCESS}[/green]"
            elif step['status'] == 'running':
                icon = f"[yellow]{Icons.RUNNING}[/yellow]"
            elif step['status'] == 'error':
                icon = f"[red]{Icons.ERROR}[/red]"
            else:
                icon = f"[dim]{Icons.READY}[/dim]"

            # Step with connector
            step_text = f"{icon} {step['name']}"

            if idx < len(steps) - 1:
                step_text += f" [dim]{Icons.ARROW_RIGHT}[/dim]"

            timeline.append(step_text)

        return " ".join(timeline)
```

### 3.2 Modal Dialogs
**File**: `claude_ctx_py/tui_dialogs.py` (new)

```python
from rich.panel import Panel
from rich.align import Align

class Dialog:
    """Modal dialog system"""

    @staticmethod
    def confirm(title: str, message: str, default: bool = False) -> Panel:
        """Confirmation dialog"""

        icon = Icons.WARNING
        content = f"{icon} [bold]{title}[/bold]\n\n{message}\n\n"

        if default:
            content += "[green][ Yes ][/green]  [dim]No[/dim]"
        else:
            content += "[dim]Yes[/dim]  [red][ No ][/red]"

        content += "\n\n[dim]Y/N to choose, Enter to confirm[/dim]"

        return Panel(
            Align.center(content),
            title="Confirmation",
            border_style="yellow",
            padding=(1, 2)
        )

    @staticmethod
    def error(title: str, message: str, details: str = "") -> Panel:
        """Error dialog"""

        content = f"{Icons.ERROR} [bold red]{title}[/bold red]\n\n{message}"

        if details:
            content += f"\n\n[dim]{Format.truncate(details, 200)}[/dim]"

        content += "\n\n[dim]Press any key to continue[/dim]"

        return Panel(
            Align.center(content),
            title="Error",
            border_style="red",
            padding=(1, 2)
        )

    @staticmethod
    def loading(message: str) -> Panel:
        """Loading dialog with spinner"""

        content = f"{Icons.RUNNING} [yellow]{message}[/yellow]\n\n[dim]Please wait...[/dim]"

        return Panel(
            Align.center(content),
            title="Working",
            border_style="yellow",
            padding=(1, 2)
        )
```

### 3.3 Enhanced Progress Displays
**File**: Update views with inline progress

```python
def _create_workflow_progress(self, workflow) -> str:
    """Show workflow progress with visual bar"""

    completed = workflow.completed_steps
    total = workflow.total_steps

    # Progress bar
    bar = ProgressBar.simple_bar(completed, total, width=20)

    # Stats
    stats = f"{completed}/{total} steps"

    # Time estimate
    if workflow.estimated_remaining:
        time_left = Format.duration(workflow.estimated_remaining)
        stats += f" [dim]• {time_left} remaining[/dim]"

    return f"{bar}  {stats}"
```

---

## Phase 4: Interactive Enhancements (2-3 hours)

### 4.1 Loading States
**File**: `claude_ctx_py/tui.py` - Add loading indicators

```python
def show_loading(self, message: str = "Loading..."):
    """Show loading overlay"""
    self.state.loading = True
    self.state.loading_message = message
    self.render()

def hide_loading(self):
    """Hide loading overlay"""
    self.state.loading = False
    self.render()

def _render_with_loading(self, content):
    """Render content with optional loading overlay"""
    if self.state.loading:
        # Show semi-transparent loading dialog
        loading_dialog = Dialog.loading(self.state.loading_message)

        # Combine content with overlay
        # (implementation depends on Rich capabilities)
        pass

    return content
```

### 4.2 Toast Notifications
**File**: `claude_ctx_py/tui_notifications.py` (new)

```python
from rich.panel import Panel
from datetime import datetime, timedelta

class Toast:
    """Temporary notification system"""

    def __init__(self):
        self.notifications = []

    def success(self, message: str, duration: int = 3):
        """Show success notification"""
        self.notifications.append({
            'type': 'success',
            'message': message,
            'expires': datetime.now() + timedelta(seconds=duration)
        })

    def error(self, message: str, duration: int = 5):
        """Show error notification"""
        self.notifications.append({
            'type': 'error',
            'message': message,
            'expires': datetime.now() + timedelta(seconds=duration)
        })

    def info(self, message: str, duration: int = 3):
        """Show info notification"""
        self.notifications.append({
            'type': 'info',
            'message': message,
            'expires': datetime.now() + timedelta(seconds=duration)
        })

    def render(self) -> list:
        """Render active notifications"""
        now = datetime.now()

        # Remove expired
        self.notifications = [n for n in self.notifications if n['expires'] > now]

        # Render active
        panels = []
        for notif in self.notifications[-3:]:  # Show max 3
            icon_map = {
                'success': (Icons.SUCCESS, 'green'),
                'error': (Icons.ERROR, 'red'),
                'info': (Icons.INFO, 'blue')
            }
            icon, color = icon_map[notif['type']]

            content = f"[{color}]{icon}[/{color}] {notif['message']}"
            panels.append(Panel(content, border_style=color, padding=(0, 1)))

        return panels
```

### 4.3 Smooth Transitions
**File**: `claude_ctx_py/tui.py` - Add transition effects

```python
def transition_view(self, new_view: str):
    """Smooth transition between views"""
    # Flash current view
    self._flash_selection()

    # Update view
    self.state.current_view = new_view
    self.state.selected_index = 0

    # Show loading briefly
    self.show_loading(f"Loading {new_view}...")
    time.sleep(0.1)  # Brief pause for visual feedback
    self.hide_loading()

    # Render new view
    self.render()

def _flash_selection(self):
    """Brief visual feedback for selection"""
    # Could add a color flash or highlight
    pass
```

---

## Phase 5: View-Specific Enhancements (3-4 hours)

### 5.1 Overview View Enhancement
**Improvements**:
- Quick stats dashboard with icons
- Visual project health indicator
- Recent activity timeline
- Key metrics with progress bars

```python
def _create_overview_dashboard(self) -> Panel:
    """Enhanced overview with dashboard layout"""

    # Project health
    health = self._calculate_project_health()
    health_bar = ProgressBar.simple_bar(health, 100, width=30)
    health_display = f"[bold]Project Health:[/bold] {health_bar}"

    # Quick stats grid
    stats = [
        f"{Icons.CODE} [cyan]{Format.number(self.state.total_agents)}[/cyan] agents",
        f"{Icons.TEST} [green]{Format.number(self.state.active_workflows)}[/green] active workflows",
        f"{Icons.FILE} [magenta]{Format.number(self.state.total_files)}[/magenta] files tracked",
        f"{Icons.SUCCESS} [yellow]{self.state.last_success}[/yellow] last success"
    ]

    stats_display = " [dim]│[/dim] ".join(stats)

    # Recent activity
    activity_display = self._create_activity_timeline()

    content = f"{health_display}\n\n{stats_display}\n\n{activity_display}"

    return Panel(content, title="Dashboard", border_style="cyan")
```

### 5.2 Agents View Enhancement
**Improvements**:
- Agent status with visual indicators
- File count with color coding
- Last activity with relative time
- Quick action hints

### 5.3 Workflows View Enhancement
**Improvements**:
- Workflow timeline visualization
- Step-by-step progress
- Dependency graph
- Execution time estimates

```python
def _create_workflow_detail(self, workflow) -> Panel:
    """Enhanced workflow detail view"""

    # Timeline
    timeline = WorkflowTimeline.create_timeline(workflow.steps)

    # Progress
    progress = self._create_workflow_progress(workflow)

    # Dependencies
    if workflow.dependencies:
        dep_tree = DependencyGraph.create_tree(workflow.name, workflow.dependencies)

    # Execution stats
    stats = f"""
[bold]Execution Stats:[/bold]
├─ Started: {Format.time_ago(workflow.start_time)}
├─ Duration: {Format.duration(workflow.duration)}
├─ Steps: {workflow.completed_steps}/{workflow.total_steps}
└─ Status: {self._format_workflow_status(workflow)}
    """

    content = f"{timeline}\n\n{progress}\n\n{stats}"

    if workflow.dependencies:
        content += f"\n\n{dep_tree}"

    return Panel(content, title=f"Workflow: {workflow.name}", border_style="magenta")
```

### 5.4 Export View Enhancement
**Improvements**:
- Export format visualization
- File size estimates
- Preview of export structure
- Progress tracking for exports

---

## Phase 6: Polish & Testing (2-3 hours)

### 6.1 Consistency Pass
- [ ] All tables use same style
- [ ] All icons are consistent
- [ ] All status indicators match
- [ ] All formatting is uniform
- [ ] All colors follow palette

### 6.2 Performance Optimization
- [ ] Cache rendered components
- [ ] Lazy load expensive visualizations
- [ ] Debounce rapid redraws
- [ ] Profile render times

### 6.3 Terminal Compatibility
- [ ] Test on different terminals (iTerm, Terminal.app, Windows Terminal)
- [ ] Fallback for limited Unicode support
- [ ] Verify colors in different color schemes
- [ ] Check on different screen sizes

### 6.4 Edge Cases
- [ ] Empty states (no agents, no workflows, etc.)
- [ ] Error states
- [ ] Loading states
- [ ] Very long names/values
- [ ] Many items (pagination/scrolling)

---

## Implementation Order

### Week 1: Core Foundation (Days 1-2)
1. ✅ Create utility files (icons, formatting, progress)
2. ✅ Update table rendering across all views
3. ✅ Enhanced headers and footers
4. ✅ Status icons everywhere

### Week 1: Advanced Features (Days 3-4)
5. ✅ Dependency graphs
6. ✅ Timeline visualizations
7. ✅ Modal dialogs
8. ✅ Loading states

### Week 1: Polish (Day 5)
9. ✅ Interactive enhancements
10. ✅ Toast notifications
11. ✅ View-specific improvements
12. ✅ Testing and refinement

---

## Success Metrics

**Visual Quality**:
- [ ] Professional appearance
- [ ] Consistent design language
- [ ] Clear information hierarchy
- [ ] Easy to scan and understand

**User Experience**:
- [ ] Faster to find information
- [ ] More enjoyable to use
- [ ] Clear feedback for actions
- [ ] Helpful error messages

**Technical Quality**:
- [ ] No performance regression
- [ ] Terminal compatible
- [ ] Well-tested edge cases
- [ ] Maintainable code

---

## File Changes Summary

**New Files** (7):
- `claude_ctx_py/tui_icons.py` - Icon system
- `claude_ctx_py/tui_format.py` - Formatting utilities
- `claude_ctx_py/tui_progress.py` - Progress bars
- `claude_ctx_py/tui_graphs.py` - Visualizations
- `claude_ctx_py/tui_dialogs.py` - Modal dialogs
- `claude_ctx_py/tui_notifications.py` - Toast system
- `claude_ctx_py/tui_animations.py` - Transitions

**Modified Files** (3):
- `claude_ctx_py/tui.py` - Core rendering updates
- `claude_ctx_py/tui_extensions.py` - Extension updates
- `claude_ctx_py/cli.py` - Integration updates

---

## Color Palette (Default)

```python
COLORS = {
    'primary': 'cyan',           # Main accent color
    'secondary': 'magenta',      # Secondary accent
    'success': 'green',          # Success states
    'warning': 'yellow',         # Warning states
    'error': 'red',              # Error states
    'info': 'blue',              # Info states
    'text': 'white',             # Primary text
    'text_dim': 'bright_black',  # Secondary text
    'border': 'cyan',            # Borders and dividers
}
```

**Usage Guidelines**:
- **Cyan**: Navigation, headers, primary elements
- **Magenta**: Data tables, secondary headers
- **Green**: Success, active, positive metrics
- **Yellow**: Warnings, in-progress, caution
- **Red**: Errors, failures, critical issues
- **Blue**: Information, neutral states
- **Dim**: Secondary information, hints

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (utilities)
3. Iterate through phases
4. Test after each phase
5. Gather feedback and refine

Ready to implement?
