# Super Saiyan Mode: CLI Tools

**Platform**: Command-Line Interfaces (Click, Typer, Cobra, Clap, etc.)

## CLI Philosophy

CLIs are power tools:
- **Fast**: Sub-100ms startup preferred
- **Composable**: Work in pipes and scripts
- **Clear**: Excellent error messages
- **Beautiful**: Rich output when TTY, parseable when piped
- **Helpful**: Self-documenting with --help

**Goal**: Make CLI tools a joy to use

## Technology Stack

### Python (Click + Rich)
```bash
pip install click rich
```

### Python (Typer + Rich)
```bash
pip install typer[all] rich
```

### Rust (Clap + colored)
```bash
cargo add clap colored
```

### Go (Cobra + lipgloss)
```bash
go get github.com/spf13/cobra
go get github.com/charmbracelet/lipgloss
```

## CLI Super Saiyan Features

### 1. Beautiful Output with Rich (Python) 🎨

```python
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

console = Console()

@click.command()
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def deploy(verbose):
    """Deploy application with beautiful output."""

    # Header
    console.print(Panel.fit(
        "[bold cyan]Super Saiyan Deploy[/bold cyan]",
        border_style="bright_blue"
    ))

    # Progress with style
    for step in track(steps, description="[cyan]Deploying..."):
        process_step(step)

    # Results table
    table = Table(title="Deployment Summary", border_style="green")
    table.add_column("Service", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("URL", style="blue")

    table.add_row("API", "[green]✓[/green] Running", "https://api.example.com")
    table.add_row("Web", "[green]✓[/green] Running", "https://example.com")

    console.print(table)

    # Success message
    console.print("\n[bold green]✓[/bold green] Deployment successful!")
```

### 2. Progress Bars & Spinners ⏳

```python
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
    console=console,
) as progress:

    task1 = progress.add_task("[cyan]Building...", total=100)
    task2 = progress.add_task("[green]Testing...", total=100)
    task3 = progress.add_task("[yellow]Deploying...", total=100)

    # Simulate work
    while not progress.finished:
        progress.update(task1, advance=0.5)
        progress.update(task2, advance=0.3)
        progress.update(task3, advance=0.2)
        time.sleep(0.02)
```

### 3. Beautiful Error Messages 🚨

```python
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def error(message: str, suggestion: str = None):
    """Display beautiful error message."""

    content = Text()
    content.append("✗ Error: ", style="bold red")
    content.append(f"{message}\n", style="red")

    if suggestion:
        content.append("\n💡 Suggestion: ", style="bold yellow")
        content.append(suggestion, style="yellow")

    console.print(Panel(
        content,
        border_style="red",
        padding=(1, 2),
    ))

# Usage:
error(
    "Failed to connect to database",
    suggestion="Check your DATABASE_URL environment variable"
)
```

### 4. Status Updates with Icons ✨

```python
from rich.console import Console

console = Console()

# Different status types
console.print("[green]✓[/green] Successfully built project")
console.print("[red]✗[/red] Failed to run tests")
console.print("[yellow]⚠[/yellow] Warning: Using development database")
console.print("[cyan]ℹ[/cyan] Tip: Run with --verbose for details")
console.print("[blue]▸[/blue] Running command: npm install")
console.print("[magenta]⋯[/magenta] Waiting for user input...")
```

### 5. Interactive Prompts 🎯

```python
import typer
from rich.prompt import Prompt, Confirm
from rich.console import Console

console = Console()

def setup():
    """Interactive setup with beautiful prompts."""

    console.print("[bold cyan]Project Setup[/bold cyan]\n")

    # Text prompt
    project_name = Prompt.ask(
        "[cyan]Project name[/cyan]",
        default="my-project"
    )

    # Choice prompt
    framework = Prompt.ask(
        "[cyan]Framework[/cyan]",
        choices=["react", "vue", "svelte"],
        default="react"
    )

    # Confirmation
    use_typescript = Confirm.ask(
        "[cyan]Use TypeScript?[/cyan]",
        default=True
    )

    # Summary
    console.print(f"\n[bold]Creating project:[/bold]")
    console.print(f"  Name: [cyan]{project_name}[/cyan]")
    console.print(f"  Framework: [cyan]{framework}[/cyan]")
    console.print(f"  TypeScript: [cyan]{use_typescript}[/cyan]\n")
```

### 6. Structured Output (JSON/YAML) 📄

```python
import json
import yaml
from rich.console import Console
from rich.syntax import Syntax

console = Console()

def output_structured(data: dict, format: str = "pretty"):
    """Output data in various formats."""

    if format == "json":
        print(json.dumps(data, indent=2))
    elif format == "yaml":
        print(yaml.dump(data, default_flow_style=False))
    elif format == "pretty":
        # Rich formatted output
        for key, value in data.items():
            console.print(f"[cyan]{key}:[/cyan] {value}")
    else:
        # Syntax highlighted
        code = json.dumps(data, indent=2)
        syntax = Syntax(code, "json", theme="monokai", line_numbers=True)
        console.print(syntax)

# Usage with click option:
@click.command()
@click.option('--format', type=click.Choice(['json', 'yaml', 'pretty']), default='pretty')
def info(format):
    output_structured(get_info(), format=format)
```

### 7. Colorized Logs 📝

```python
from rich.logging import RichHandler
import logging

# Setup rich logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("app")

# Use it
log.info("Starting application")
log.warning("Resource usage high")
log.error("Failed to connect")
log.debug("Debug information")
```

### 8. Command Trees & Help Text 📚

```python
import typer
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from typing import Optional

app = typer.Typer(
    help="[bold cyan]Super Saiyan CLI[/bold cyan] - Beautiful command-line tool",
    rich_markup_mode="rich"
)

@app.command()
def deploy(
    environment: str = typer.Argument(
        ...,
        help="[cyan]Target environment:[/cyan] production, staging, development"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="[yellow]Enable verbose output[/yellow]"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="[yellow]Simulate deployment without changes[/yellow]"
    ),
):
    """
    [bold]Deploy application to target environment[/bold]

    [cyan]Examples:[/cyan]
      $ mycli deploy production
      $ mycli deploy staging --verbose
      $ mycli deploy production --dry-run
    """
    # Command implementation
    pass
```

### 9. Completion & Autocomplete ⌨️

```python
import typer
from typing import List

def complete_environment(incomplete: str) -> List[str]:
    """Autocomplete environments."""
    environments = ["production", "staging", "development", "test"]
    return [env for env in environments if env.startswith(incomplete)]

@app.command()
def deploy(
    environment: str = typer.Argument(
        ...,
        autocompletion=complete_environment
    )
):
    """Deploy with autocomplete support."""
    pass

# Shell completion setup:
# mycli --install-completion
```

### 10. Streaming Output 🌊

```python
from rich.live import Live
from rich.table import Table
import time

def stream_logs():
    """Stream logs with live updating table."""

    with Live(generate_table(), refresh_per_second=4) as live:
        for i in range(100):
            time.sleep(0.1)
            live.update(generate_table(i))

def generate_table(progress: int = 0):
    """Generate live updating table."""
    table = Table()
    table.add_column("Service")
    table.add_column("Status")
    table.add_column("Progress")

    table.add_row("API", "Running", f"{progress}%")
    table.add_row("Web", "Running", f"{progress}%")
    table.add_row("DB", "Healthy", "100%")

    return table
```

## CLI Enhancement Checklist

✅ **Every CLI should have:**

### Output:
- [ ] Colored output (when TTY)
- [ ] Plain output (when piped)
- [ ] Progress indicators for long operations
- [ ] Clear success/error messages
- [ ] Helpful error suggestions
- [ ] Structured output options (--json, --yaml)

### Usability:
- [ ] Excellent --help text
- [ ] Shell completions (bash/zsh/fish)
- [ ] Short and long options (-v, --verbose)
- [ ] Sensible defaults
- [ ] Dry-run mode for destructive operations
- [ ] Verbose mode for debugging

### Error Handling:
- [ ] Clear error messages
- [ ] Suggestions for common mistakes
- [ ] Non-zero exit codes on failure
- [ ] Validation before destructive actions
- [ ] Helpful "did you mean?" suggestions

### Performance:
- [ ] Fast startup (<100ms)
- [ ] Lazy loading of heavy dependencies
- [ ] Streaming output for large datasets
- [ ] Concurrent operations where possible
- [ ] Progress feedback for slow operations

### Documentation:
- [ ] README with examples
- [ ] Man page (optional but nice)
- [ ] --help with examples
- [ ] Inline help for subcommands
- [ ] Link to docs website

## Example: Complete Super Saiyan CLI

```python
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from typing import Optional

app = typer.Typer(rich_markup_mode="rich")
console = Console()

@app.command()
def agent(
    action: str = typer.Argument(
        ...,
        help="[cyan]Action:[/cyan] activate, deactivate, list"
    ),
    name: Optional[str] = typer.Argument(
        None,
        help="[cyan]Agent name[/cyan]"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="[yellow]Verbose output[/yellow]"
    ),
):
    """
    [bold cyan]Manage Claude agents[/bold cyan]

    [yellow]Examples:[/yellow]
      $ cortex agent list
      $ cortex agent activate code-reviewer
      $ cortex agent deactivate test-automator
    """

    if action == "list":
        # Beautiful table output
        table = Table(
            title="[bold cyan]Available Agents[/bold cyan]",
            border_style="bright_blue"
        )
        table.add_column("Agent", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Description", style="dim")

        agents = get_agents()
        for agent in agents:
            status = "[green]●[/green]" if agent.active else "[dim]○[/dim]"
            table.add_row(agent.name, status, agent.description)

        console.print(table)

    elif action == "activate":
        if not name:
            console.print("[red]✗[/red] Agent name required")
            raise typer.Exit(1)

        # Progress spinner
        with console.status(f"[cyan]Activating {name}..."):
            activate_agent(name)

        console.print(f"[green]✓[/green] Activated [cyan]{name}[/cyan]")

    elif action == "deactivate":
        if not name:
            console.print("[red]✗[/red] Agent name required")
            raise typer.Exit(1)

        console.print(f"[yellow]⚠[/yellow] Deactivating [cyan]{name}[/cyan]")
        deactivate_agent(name)
        console.print(f"[green]✓[/green] Deactivated [cyan]{name}[/cyan]")

if __name__ == "__main__":
    app()
```

## Platform-Specific Tips

### Python (Click):
- Simple, decorator-based
- Excellent testing support
- Large ecosystem

### Python (Typer):
- Type hints for validation
- Automatic help generation
- Rich integration built-in

### Rust (Clap):
- Fast, safe, compiled
- Automatic completions
- Great error messages

### Go (Cobra):
- Used by kubectl, hugo
- Subcommand trees
- Persistent flags

## Testing CLI Visual Quality

```bash
# Test output formats:
mycli --help                    # Help text
mycli command --json            # JSON output
mycli command | jq              # Piped (no colors)
mycli command > file            # Redirected (no colors)
mycli command 2>&1 | less       # Pager

# Test in different terminals:
- iTerm2 (Mac) - True color
- Terminal.app - 256 colors
- Windows Terminal - True color
- Over SSH - Latency test
```

## Summary

CLI Super Saiyan is about:
- 🎨 Colorful, structured output
- ⏳ Clear progress indicators
- 🚨 Beautiful error messages
- 📊 Rich data visualization
- ⚡ Fast, responsive commands
- 🎯 Excellent user experience

Make CLIs that users actually enjoy using! 🔥✨
