"""First-run wizard for cortex CLI setup."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple, List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from . import installer
from . import shell_integration
from .core.base import _resolve_cortex_root


@dataclass
class WizardConfig:
    """Configuration collected during wizard execution."""

    target_dir: Path = field(default_factory=_resolve_cortex_root)
    install_completions: bool = True
    install_aliases: bool = True
    link_rules: bool = True
    detected_shell: str = ""
    shell_rc_path: Optional[Path] = None


def should_run_wizard() -> bool:
    """Check if the wizard should run.

    Returns True if:
    - ~/.cortex doesn't exist
    - CORTEX_SKIP_WIZARD env var is not set
    - Not running in a non-interactive environment (CI, etc.)
    """
    # Check skip env var
    if os.environ.get("CORTEX_SKIP_WIZARD"):
        return False

    # Check if stdin is a TTY (interactive terminal)
    if not sys.stdin.isatty():
        return False

    # Check if cortex root exists
    cortex_root = _resolve_cortex_root()
    return not cortex_root.exists()


def _show_welcome(console: Console) -> bool:
    """Display welcome screen and confirm continuation.

    Returns True if user wants to continue, False to abort.
    """
    welcome_text = Text()
    welcome_text.append("Cortex enhances Claude Code with:\n\n", style="")
    welcome_text.append("  • ", style="cyan")
    welcome_text.append("Reusable rules, modes, and principles\n")
    welcome_text.append("  • ", style="cyan")
    welcome_text.append("MCP server documentation\n")
    welcome_text.append("  • ", style="cyan")
    welcome_text.append("Skill definitions and workflows\n")
    welcome_text.append("  • ", style="cyan")
    welcome_text.append("Shell aliases for quick exports\n\n")
    welcome_text.append("This wizard will help you set up your environment.", style="dim")

    console.print()
    console.print(Panel(
        welcome_text,
        title="[bold cyan]Welcome to Claude Cortex[/bold cyan]",
        subtitle="First Run Setup",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()

    return Confirm.ask("Continue with setup?", default=True, console=console)


def _get_target_directory(console: Console) -> Path:
    """Prompt for target directory selection.

    Returns the selected target directory path.
    """
    default_path = _resolve_cortex_root()

    console.print()
    console.print("[bold]Installation Directory[/bold]")
    console.print("─" * 50)
    console.print(f"Default location: [cyan]{default_path}[/cyan]")
    console.print()

    use_default = Confirm.ask("Use default location?", default=True, console=console)

    if use_default:
        return default_path

    custom_path = Prompt.ask(
        "Enter custom path",
        default=str(default_path),
        console=console,
    )
    return Path(custom_path).expanduser().resolve()


def _get_shell_config(console: Console) -> Tuple[str, Optional[Path], bool, bool]:
    """Prompt for shell integration settings.

    Returns tuple of (shell_name, rc_path, install_completions, install_aliases).
    """
    console.print()
    console.print("[bold]Shell Integration[/bold]")
    console.print("─" * 50)

    # Try to detect shell
    try:
        detected_shell, rc_path = shell_integration.detect_shell()
        console.print(f"Detected shell: [cyan]{detected_shell}[/cyan] ([dim]{rc_path}[/dim])")
    except RuntimeError:
        console.print("[yellow]Could not auto-detect shell.[/yellow]")
        detected_shell = ""
        rc_path = None

    console.print()

    if detected_shell:
        install_completions = Confirm.ask(
            "Install shell completions? (tab completion for cortex commands)",
            default=True,
            console=console,
        )
        install_aliases = Confirm.ask(
            "Install shell aliases? (ctx, ctx-copy, ctx-light, etc.)",
            default=True,
            console=console,
        )
    else:
        console.print("[dim]Shell integration skipped - shell not detected.[/dim]")
        install_completions = False
        install_aliases = False

    return detected_shell, rc_path, install_completions, install_aliases


def _get_rule_linking_config(console: Console) -> bool:
    """Prompt for rule linking configuration.

    Returns True if rules should be symlinked to ~/.claude/rules/cortex/.
    """
    console.print()
    console.print("[bold]Rule Discovery[/bold]")
    console.print("─" * 50)
    console.print(
        "Cortex can symlink rules to [cyan]~/.claude/rules/cortex/[/cyan] so Claude\n"
        "Code automatically discovers them in any project."
    )
    console.print()

    return Confirm.ask("Enable automatic rule discovery?", default=True, console=console)


def _show_summary(console: Console, config: WizardConfig) -> bool:
    """Display configuration summary and confirm execution.

    Returns True if user confirms, False to abort.
    """
    console.print()
    console.print("[bold]Configuration Summary[/bold]")
    console.print("─" * 50)
    console.print()

    # Configuration table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Target directory", str(config.target_dir))

    if config.detected_shell:
        table.add_row("Shell", config.detected_shell)
        table.add_row(
            "Completions",
            "[green]Yes[/green]" if config.install_completions else "[dim]No[/dim]"
        )
        table.add_row(
            "Aliases",
            "[green]Yes[/green]" if config.install_aliases else "[dim]No[/dim]"
        )
    else:
        table.add_row("Shell integration", "[dim]Skipped (not detected)[/dim]")

    table.add_row(
        "Rule linking",
        "[green]~/.claude/rules/cortex/[/green]" if config.link_rules else "[dim]No[/dim]"
    )

    console.print(table)
    console.print()

    # Show what will be created
    console.print("[bold]The following will be created:[/bold]")
    console.print(f"  • {config.target_dir}/rules/")
    console.print(f"  • {config.target_dir}/flags/")
    console.print(f"  • {config.target_dir}/modes/")
    console.print(f"  • {config.target_dir}/principles/")
    console.print(f"  • {config.target_dir}/templates/")
    console.print(f"  • {config.target_dir}/cortex-config.json")
    console.print()

    return Confirm.ask("Proceed with installation?", default=True, console=console)


def _execute_installation(console: Console, config: WizardConfig) -> Tuple[int, List[str]]:
    """Execute the installation based on wizard configuration.

    Returns tuple of (exit_code, list of result messages).
    """
    results: List[str] = []
    exit_code = 0

    console.print()
    console.print("[bold]Installing Cortex[/bold]")
    console.print("─" * 50)

    # Run bootstrap
    code, message = installer.bootstrap(
        target_dir=config.target_dir,
        force=False,
        dry_run=False,
        link_rules=config.link_rules,
    )
    if code != 0:
        console.print(f"[red]✗[/red] Bootstrap failed: {message}")
        return code, [message]

    # Parse bootstrap results to show progress
    for line in message.split("\n"):
        if line.strip().startswith("✓"):
            console.print(f"[green]{line.strip()}[/green]")
            results.append(line.strip())
        elif line.strip().startswith("✗"):
            console.print(f"[red]{line.strip()}[/red]")
            results.append(line.strip())
            exit_code = 1

    # Install shell completions if requested
    if config.install_completions and config.detected_shell:
        code, message = installer.install_completions(
            shell=config.detected_shell,
            force=False,
            dry_run=False,
        )
        if code == 0:
            console.print(f"[green]✓ Installed {config.detected_shell} completions[/green]")
            results.append(f"Installed {config.detected_shell} completions")
        else:
            # Not a fatal error if completions fail
            console.print(f"[yellow]⚠ Completions: {message.split(chr(10))[0]}[/yellow]")

    # Install shell aliases if requested
    if config.install_aliases and config.detected_shell:
        code, message = shell_integration.install_aliases(
            shell=config.detected_shell,
            rc_file=config.shell_rc_path,
            force=False,
            dry_run=False,
        )
        if code == 0:
            console.print(f"[green]✓ Installed shell aliases to {config.shell_rc_path}[/green]")
            results.append(f"Installed aliases to {config.shell_rc_path}")
        else:
            # Not a fatal error if aliases fail
            console.print(f"[yellow]⚠ Aliases: {message.split(chr(10))[0]}[/yellow]")

    return exit_code, results


def _show_next_steps(console: Console, config: WizardConfig) -> None:
    """Display next steps after successful installation."""
    console.print()
    console.print(Panel(
        "[bold green]Installation complete![/bold green]\n\n"
        "[bold]Next steps:[/bold]\n\n"
        f"  1. Reload your shell: [cyan]source {config.shell_rc_path or '~/.zshrc'}[/cyan]\n"
        "  2. Launch TUI: [cyan]cortex tui[/cyan]\n"
        "  3. Start Claude with Cortex: [cyan]cortex start[/cyan]\n"
        "  4. Check status: [cyan]cortex status[/cyan]\n\n"
        "[dim]Run 'cortex --help' for more commands.[/dim]",
        title="[bold]Setup Complete[/bold]",
        border_style="green",
        padding=(1, 2),
    ))


def run_wizard(console: Optional[Console] = None) -> Tuple[int, str]:
    """Run the first-run wizard interactively.

    Args:
        console: Rich Console to use. Creates new one if None.

    Returns:
        Tuple of (exit_code, message).
    """
    if console is None:
        console = Console()

    try:
        # Step 1: Welcome
        if not _show_welcome(console):
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            return 1, "Setup cancelled by user"

        # Step 2: Target directory
        target_dir = _get_target_directory(console)

        # Step 3: Shell integration
        shell_name, rc_path, install_completions, install_aliases = _get_shell_config(console)

        # Step 4: Rule linking
        link_rules = _get_rule_linking_config(console)

        # Build config
        config = WizardConfig(
            target_dir=target_dir,
            install_completions=install_completions,
            install_aliases=install_aliases,
            link_rules=link_rules,
            detected_shell=shell_name,
            shell_rc_path=rc_path,
        )

        # Step 5: Summary and confirmation
        if not _show_summary(console, config):
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            return 1, "Setup cancelled by user"

        # Step 6: Execute
        exit_code, results = _execute_installation(console, config)

        if exit_code == 0:
            # Step 7: Next steps
            _show_next_steps(console, config)
            return 0, "Setup completed successfully"
        else:
            console.print("\n[red]Setup completed with errors.[/red]")
            return exit_code, "Setup completed with errors"

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Setup cancelled.[/yellow]")
        return 1, "Setup cancelled by user"
    except PermissionError as e:
        console.print(f"\n[red]Permission denied: {e}[/red]")
        return 1, f"Permission denied: {e}"
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return 1, f"Error: {e}"


def run_wizard_non_interactive(
    target_dir: Optional[Path] = None,
    link_rules: bool = True,
    install_completions: bool = False,
    install_aliases: bool = False,
) -> Tuple[int, str]:
    """Run wizard with defaults for non-interactive environments (CI, scripts).

    Args:
        target_dir: Override target directory (default: ~/.cortex)
        link_rules: Whether to symlink rules
        install_completions: Whether to install shell completions
        install_aliases: Whether to install shell aliases

    Returns:
        Tuple of (exit_code, message).
    """
    return installer.bootstrap(
        target_dir=target_dir,
        force=False,
        dry_run=False,
        link_rules=link_rules,
    )
