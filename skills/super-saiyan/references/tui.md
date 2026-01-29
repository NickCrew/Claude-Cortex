# Super Saiyan: TUI Reference

Visual excellence for terminal UIs using Textual, Ratatui, Bubbletea.

## Stack
- Python: `textual` + `rich`
- Rust: `ratatui` + `crossterm`
- Go: `bubbletea` + `lipgloss`

## Key Patterns

### Textual CSS
```css
Screen { background: #0a0e27; }

.card {
    border: tall cyan;
    background: #1a1f3a;
    padding: 1 2;
}

.card:hover {
    border: tall bright_cyan;
    background: #242945;
}

/* Animations */
.panel { opacity: 0; offset-y: 5; }
.panel.visible {
    opacity: 1; offset-y: 0;
    transition: opacity 300ms, offset-y 300ms ease_out;
}
```

### Rich Theme
```python
from rich.theme import Theme
theme = Theme({
    "primary": "bold bright_blue",
    "success": "bold bright_green",
    "error": "bold bright_red",
    "muted": "dim white",
})
```

### Progress & Status
```python
with console.status("[cyan]Loading...", spinner="dots"):
    do_work()

console.print("[green]✓[/green] Done")
console.print("[red]✗[/red] Failed")
```

### Data Tables
```python
table = Table(title="Status", border_style="bright_blue")
table.add_column("Agent", style="cyan")
table.add_column("Status", justify="center")
table.add_row("reviewer", "[green]●[/green] Active")
```

### Keyboard Bindings (Textual)
```python
BINDINGS = [
    Binding("q", "quit", "Quit"),
    Binding("ctrl+k", "palette", "Commands"),
]
```

## Checklist
- [ ] Rich colors (not just white/black)
- [ ] Smooth transitions
- [ ] Keyboard shortcuts with hints
- [ ] Tab navigation
- [ ] Status bar with live updates
- [ ] Instant response (<16ms)
- [ ] No flicker
