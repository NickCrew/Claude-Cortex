# Super Saiyan: CLI Reference

Visual excellence for command-line interfaces using Click, Typer, Rich, etc.

## Stack
- Python: `click` + `rich` or `typer[all]`
- Rust: `clap` + `colored`
- Go: `cobra` + `lipgloss`

## Key Patterns

### Beautiful Output (Rich)
```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

console = Console()

# Progress
for item in track(items, description="Processing..."):
    process(item)

# Table
table = Table(title="Results", border_style="green")
table.add_column("Name", style="cyan")
table.add_column("Status")
table.add_row("api", "[green]✓[/green]")
console.print(table)
```

### Status Icons
```python
console.print("[green]✓[/green] Success")
console.print("[red]✗[/red] Failed")
console.print("[yellow]⚠[/yellow] Warning")
console.print("[cyan]ℹ[/cyan] Info")
```

### Error Messages
```python
from rich.panel import Panel
console.print(Panel(
    "[red]✗ Error:[/red] Connection failed\n\n[yellow]💡 Check DATABASE_URL[/yellow]",
    border_style="red"
))
```

### Interactive Prompts
```python
from rich.prompt import Prompt, Confirm
name = Prompt.ask("[cyan]Project name[/cyan]", default="my-project")
confirm = Confirm.ask("[cyan]Continue?[/cyan]", default=True)
```

## Checklist
- [ ] Colored output (TTY) / plain (piped)
- [ ] Progress indicators
- [ ] Clear success/error messages
- [ ] `--help` with examples
- [ ] Shell completions
- [ ] Fast startup (<100ms)
