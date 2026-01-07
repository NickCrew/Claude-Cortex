# Super Saiyan Mode: Terminal UI (TUI)

**Platform**: Terminal User Interfaces (Textual, Ratatui, Bubbletea, Blessed, Ink, etc.)

## TUI Philosophy

Terminal UIs have unique constraints and strengths:
- **Fast**: No browser overhead, instant response
- **Keyboard-first**: Power user paradise
- **Low resources**: Run anywhere, even over SSH
- **Professional**: Developer-friendly aesthetic
- **Accessible**: Screen reader friendly when done right

**Goal**: Make terminal UIs as polished as modern web apps

## Technology Stack

### Python (Textual + Rich)
```bash
pip install textual rich
```

### Rust (Ratatui)
```bash
cargo add ratatui crossterm
```

### Go (Bubbletea)
```bash
go get github.com/charmbracelet/bubbletea
```

### Node.js (Ink + React)
```bash
npm install ink react
```

## TUI Super Saiyan Features

### 1. Rich Color Schemes ✅

**Using Textual (Python):**
```python
# In your CSS (Textual)
Screen {
    background: $surface;
}

.card {
    background: linear-gradient(90deg, #1e3a8a 0%, #7c3aed 100%);
    border: tall $primary;
    padding: 1 2;
}

.card:hover {
    background: linear-gradient(90deg, #2563eb 0%, #8b5cf6 100%);
    border: tall $accent;
}

.success {
    color: $success;
    text-style: bold;
}

.error {
    color: $error;
    text-style: bold;
}
```

**Color Palette (Rich/ANSI):**
```python
from rich.console import Console
from rich.theme import Theme

supersaiyan_theme = Theme({
    "primary": "bold bright_blue",
    "secondary": "bold bright_magenta",
    "success": "bold bright_green",
    "warning": "bold bright_yellow",
    "error": "bold bright_red",
    "info": "bold bright_cyan",
    "muted": "dim white",
    "highlight": "reverse bright_cyan",
})

console = Console(theme=supersaiyan_theme)
```

### 2. Smooth Animations ✅

**Textual CSS Animations:**
```css
/* Fade in on mount */
.panel {
    opacity: 0;
}

.panel:focus {
    opacity: 1;
    transition: opacity 300ms;
}

/* Slide in from left */
.sidebar {
    offset-x: -30;
}

.sidebar.visible {
    offset-x: 0;
    transition: offset-x 300ms ease_out;
}

/* Scale on hover */
.button:hover {
    text-style: bold;
    background: $primary;
    transition: background 150ms;
}
```

**Rich Progress Animations:**
```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.live import Live
from rich.panel import Panel

with Progress(
    SpinnerColumn(spinner_name="dots"),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(complete_style="cyan", finished_style="green"),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
) as progress:
    task = progress.add_task("[cyan]Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
        time.sleep(0.05)
```

### 3. Status Indicators 🔥

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Animated spinner
with console.status("[bold cyan]Loading data...", spinner="dots"):
    # Do work
    time.sleep(2)

# Success indicator
console.print("[green]✓[/green] Task completed successfully")

# Error indicator
console.print("[red]✗[/red] Task failed")

# Warning indicator
console.print("[yellow]⚠[/yellow] Warning: Resource usage high")

# Info indicator
console.print("[cyan]ℹ[/cyan] Tip: Use --verbose for more details")
```

### 4. Beautiful Data Tables ✅

```python
from rich.table import Table
from rich.console import Console

table = Table(
    title="[bold cyan]Agent Status[/bold cyan]",
    show_header=True,
    header_style="bold magenta",
    border_style="bright_blue",
    title_style="bold cyan",
    padding=(0, 1),
)

table.add_column("Agent", style="cyan", no_wrap=True)
table.add_column("Status", justify="center")
table.add_column("Progress", justify="right")
table.add_column("Duration", justify="right", style="yellow")

table.add_row(
    "code-reviewer",
    "[green]●[/green] Active",
    "[cyan]████████░░[/cyan] 80%",
    "2.5s"
)
table.add_row(
    "test-automator",
    "[green]●[/green] Active",
    "[cyan]██████████[/cyan] 100%",
    "3.2s"
)
table.add_row(
    "api-documenter",
    "[yellow]●[/yellow] Running",
    "[cyan]█████░░░░░[/cyan] 50%",
    "1.8s"
)

console.print(table)
```

### 5. Dashboard Cards 📊

```python
from textual.widgets import Static
from textual.containers import Container
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

class MetricCard(Static):
    """Beautiful metric card with sparkline."""

    def __init__(self, title: str, value: str, trend: str, sparkline: str):
        content = Text()
        content.append(f"{title}\n", style="dim")
        content.append(f"{value}\n", style="bold cyan")
        content.append(f"{trend} ", style="green" if "+" in trend else "red")
        content.append(f"{sparkline}", style="bright_blue")

        panel = Panel(
            Align.center(content),
            border_style="bright_blue",
            padding=(1, 2),
        )
        super().__init__(panel)

# Usage:
card = MetricCard(
    title="Active Agents",
    value="12",
    trend="+23%",
    sparkline="▁▂▃▅▆█"
)
```

### 6. Command Palette 🎯

```python
from textual.app import App
from textual.widgets import Input, ListView, ListItem
from textual.binding import Binding

class CommandPalette(ListView):
    """Fuzzy searchable command palette (Cmd+K style)."""

    BINDINGS = [
        Binding("ctrl+k", "toggle_palette", "Command Palette", priority=True),
        Binding("escape", "close", "Close", show=False),
    ]

    commands = [
        ("activate-agent", "Activate an agent"),
        ("deactivate-agent", "Deactivate an agent"),
        ("view-graph", "View dependency graph"),
        ("export-context", "Export context"),
        ("search-agents", "Search agents"),
    ]

    def compose(self):
        yield Input(placeholder="Type to search...")
        for cmd, desc in self.commands:
            yield ListItem(f"{cmd} - {desc}")

    def action_toggle_palette(self):
        self.display = not self.display
```

### 7. Interactive Graphs 📈

```python
from plotille import Figure, scatter

# Terminal sparklines
def sparkline(data: List[float]) -> str:
    """Generate ASCII sparkline."""
    chars = "▁▂▃▄▅▆▇█"
    min_val, max_val = min(data), max(data)
    range_val = max_val - min_val or 1
    return "".join(
        chars[int((v - min_val) / range_val * (len(chars) - 1))]
        for v in data
    )

# Terminal charts
fig = Figure()
fig.width = 60
fig.height = 15
fig.set_x_limits(min_=0, max_=10)
fig.set_y_limits(min_=0, max_=10)
fig.color_mode = 'rgb'

fig.scatter([1, 2, 3, 4, 5], [1, 4, 9, 16, 25], lc='cyan', label='Progress')
print(fig.show(legend=True))
```

### 8. Keyboard Shortcuts with Visual Feedback 🎮

```python
from textual.app import App
from textual.binding import Binding
from textual.widgets import Footer

class SuperSaiyanTUI(App):
    """TUI with beautiful keyboard shortcuts."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("a", "activate", "Activate Agent"),
        Binding("d", "deactivate", "Deactivate Agent"),
        Binding("g", "graph", "View Graph"),
        Binding("?", "help", "Help"),
        Binding("ctrl+k", "palette", "Command Palette"),
        Binding("tab", "next_tab", "Next Tab", show=False),
        Binding("shift+tab", "prev_tab", "Previous Tab", show=False),
    ]

    def action_activate(self):
        self.notify("Activating agent...", severity="information")

    def action_graph(self):
        self.push_screen(GraphView())

    def notify(self, message: str, severity: str = "information"):
        """Show notification with style."""
        # Textual built-in notifications with style
        super().notify(message, severity=severity, timeout=3)
```

### 9. Smooth Panel Transitions 🎬

```python
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static

class SmoothPanel(Container):
    """Panel with smooth entrance animation."""

    DEFAULT_CSS = """
    SmoothPanel {
        opacity: 0;
        offset-y: 5;
    }

    SmoothPanel.visible {
        opacity: 1;
        offset-y: 0;
        transition: opacity 300ms, offset-y 300ms ease_out;
    }
    """

    def on_mount(self):
        # Trigger animation on mount
        self.add_class("visible")
```

### 10. Status Bar with Live Updates 📡

```python
from textual.widgets import Footer
from textual.reactive import reactive

class StatusBar(Footer):
    """Live updating status bar with colors."""

    agent_count = reactive(0)
    active_tasks = reactive(0)

    def render(self) -> str:
        return (
            f"[cyan]Agents:[/cyan] {self.agent_count} | "
            f"[green]Active:[/green] {self.active_tasks} | "
            f"[yellow]Memory:[/yellow] 45MB"
        )

    def watch_agent_count(self, new_count: int):
        """Update when agent count changes."""
        self.refresh()
```

## TUI Enhancement Checklist

✅ **Every TUI element should have:**

### Visual:
- [ ] Rich colors (not just white on black)
- [ ] Box drawing characters for borders
- [ ] Unicode symbols (✓, ✗, ⚠, ℹ, ●, ▸)
- [ ] Gradient effects where supported
- [ ] Consistent spacing and alignment
- [ ] Clear visual hierarchy

### Animation:
- [ ] Smooth transitions between screens
- [ ] Animated spinners during loading
- [ ] Progress bars with percentages
- [ ] Fade in/out effects (opacity)
- [ ] Slide transitions (offset)

### Interaction:
- [ ] Keyboard shortcuts with hints
- [ ] Tab navigation between elements
- [ ] Vim-style hjkl navigation (optional)
- [ ] Command palette (Ctrl+K)
- [ ] Context-sensitive help (?)
- [ ] Immediate visual feedback

### Information:
- [ ] Status bar with live updates
- [ ] Notifications/toasts for events
- [ ] Clear error messages
- [ ] Loading indicators
- [ ] Success confirmations

### Performance:
- [ ] Instant response (<16ms)
- [ ] No flicker or tearing
- [ ] Smooth scrolling
- [ ] Efficient redraws
- [ ] Low CPU usage

## Example: Complete Super Saiyan TUI

```python
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Button
from textual.binding import Binding
from rich.panel import Panel
from rich.table import Table

class SuperSaiyanTUI(App):
    """Complete Super Saiyan terminal interface."""

    CSS = """
    Screen {
        background: #0a0e27;
    }

    Header {
        background: linear-gradient(90deg, #1e3a8a 0%, #7c3aed 100%);
        color: white;
        text-style: bold;
    }

    .dashboard {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }

    .card {
        height: 100%;
        border: tall cyan;
        background: #1a1f3a;
        padding: 1 2;
        transition: border 200ms;
    }

    .card:hover {
        border: tall bright_cyan;
        background: #242945;
    }

    .card-title {
        color: cyan;
        text-style: bold;
    }

    .card-value {
        color: white;
        text-style: bold;
        text-align: center;
        content-align: center middle;
    }

    .table-container {
        border: solid bright_blue;
        padding: 1;
        margin: 1;
    }

    Button {
        margin: 1;
    }

    Button.primary {
        background: #2563eb;
        color: white;
        border: solid cyan;
    }

    Button.primary:hover {
        background: #3b82f6;
        text-style: bold;
    }

    Footer {
        background: #1a1f3a;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+k", "command_palette", "Commands"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Dashboard cards
        with Container(classes="dashboard"):
            yield MetricCard("Active Agents", "12", "+3", "▁▂▃▅▆█")
            yield MetricCard("Tasks Complete", "847", "+124", "▃▄▅▆▇█")
            yield MetricCard("Success Rate", "94%", "+2%", "▅▆▇██▇")

        # Data table
        yield DataTable()

        # Action buttons
        with Horizontal():
            yield Button("Activate Agent", variant="primary", classes="primary")
            yield Button("View Graph", variant="default")
            yield Button("Export", variant="default")

        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("Agent", "Status", "Progress", "Duration")
        table.add_row("code-reviewer", "● Active", "80%", "2.5s")
        table.add_row("test-automator", "● Active", "100%", "3.2s")
        table.add_row("api-documenter", "● Running", "50%", "1.8s")

    def action_refresh(self):
        self.notify("Refreshing data...", severity="information")

    def action_command_palette(self):
        self.notify("Command palette (Ctrl+K)", severity="information")

if __name__ == "__main__":
    SuperSaiyanTUI().run()
```

## TUI Color Palette

```python
# Super Saiyan TUI Colors (Textual variables)
$primary: #3b82f6;           # Blue
$secondary: #8b5cf6;         # Purple
$accent: #06b6d4;            # Cyan
$success: #10b981;           # Green
$warning: #f59e0b;           # Yellow
$error: #ef4444;             # Red
$info: #3b82f6;              # Blue
$surface: #0a0e27;           # Dark blue-gray
$surface-lighten-1: #1a1f3a; # Slightly lighter
$surface-lighten-2: #242945; # Even lighter
$text: #ffffff;              # White
$text-muted: #9ca3af;        # Gray
```

## Performance Optimization

### DO:
- ✅ Use reactive properties for auto-updates
- ✅ Batch UI updates
- ✅ Use `call_later()` for async operations
- ✅ Cache rendered content
- ✅ Use `auto_refresh=False` when not needed

### DON'T:
- ❌ Update UI in tight loops
- ❌ Render unnecessarily
- ❌ Block the main thread
- ❌ Use excessive animations
- ❌ Poll when you can use reactivity

## Accessibility (TUI)

✅ **Keyboard Navigation:**
- Tab/Shift+Tab between elements
- Arrow keys for lists/tables
- Enter to activate
- Escape to cancel
- ? for help

✅ **Screen Reader Support:**
- Use semantic widgets (Button, ListView, DataTable)
- Provide aria-style labels via Textual
- Clear focus indicators
- Logical reading order

✅ **Color Contrast:**
- Use bright variants for text
- Avoid color-only indicators
- Add symbols (✓, ✗) with colors
- Support high contrast themes

## Platform-Specific Tips

### Textual (Python):
- Use CSS for styling (familiar to web devs)
- Reactive properties for live updates
- Screens for navigation
- Workers for async tasks

### Ratatui (Rust):
- Extremely fast rendering
- Use crossterm for terminal manipulation
- Great for resource-constrained environments
- Type-safe widgets

### Bubbletea (Go):
- Elm architecture (Model-Update-View)
- Composable components
- Built-in bubbles (components)
- Great for CLI tools

### Ink (React):
- Use React components in terminal!
- Familiar to web developers
- Hot reloading during development
- npm ecosystem

## Testing TUI Visual Quality

```bash
# Test in different terminals:
- iTerm2 (Mac) - True color support
- Terminal.app (Mac) - Limited colors
- Windows Terminal - True color support
- Alacritty - Fast, true color
- Kitty - Advanced features
- tmux/screen - Multiplexer compatibility

# Test with:
- Light theme
- Dark theme
- High contrast mode
- Different font sizes
- Over SSH (latency)
```

## Summary

TUI Super Saiyan is about:
- 🎨 Rich colors and gradients
- ⚡ Smooth, subtle animations
- 🎯 Keyboard-first interactions
- 📊 Beautiful data visualization
- ✨ Professional polish
- 🚀 Blazing fast performance

Make terminal UIs that rival web apps! 🔥✨
