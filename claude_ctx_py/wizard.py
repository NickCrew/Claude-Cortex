"""First-run wizard for cortex CLI setup."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from . import installer
from . import shell_integration
from .core.base import _resolve_cortex_root, _resolve_claude_dir
from .init_cmds import _detect_project_type, _recommend_profile, DetectionResult


class ExperienceLevel(Enum):
    """User experience level for adaptive wizard flow."""

    NEW = "new"  # Full explanations, all prompts
    EXPERIENCED = "experienced"  # Standard flow
    POWER_USER = "power_user"  # Minimal prompts, auto-defaults


# MCP Server definitions with installation info
# Note: claude-mem is a Claude Code plugin (install via /plugin), not an MCP server
MCP_SERVERS: Dict[str, Dict[str, object]] = {
    "context7": {
        "name": "Context7",
        "description": "Documentation lookup for libraries and frameworks",
        "url": "https://github.com/upstash/context7",
        "config": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
        },
        "default": True,
    },
    "mcp-memory": {
        "name": "MCP Memory",
        "description": "Knowledge graph memory across sessions",
        "url": "https://pypi.org/project/mcp-memory-py/",
        "config": {
            "command": "uvx",
            "args": ["--refresh", "--quiet", "mcp-memory-py"],
        },
        "default": True,
    },
    "basic-memory": {
        "name": "Basic Memory",
        "description": "Local-first personal knowledge management",
        "url": "https://github.com/basicmachines-co/basic-memory",
        "config": {
            "command": "uvx",
            "args": ["basic-memory", "mcp"],
        },
        "default": False,
    },
}


@dataclass
class OnboardingState:
    """Persisted onboarding completion state."""

    completed_at: Optional[str] = None
    experience_level: str = "new"
    profile_applied: str = "minimal"
    tui_tour_shown: bool = False
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Optional[str | bool]]:
        """Convert to dictionary for JSON serialization."""
        return {
            "completed_at": self.completed_at,
            "experience_level": self.experience_level,
            "profile_applied": self.profile_applied,
            "tui_tour_shown": self.tui_tour_shown,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str | bool]]) -> "OnboardingState":
        """Create from dictionary."""
        return cls(
            completed_at=str(data.get("completed_at")) if data.get("completed_at") else None,
            experience_level=str(data.get("experience_level", "new")),
            profile_applied=str(data.get("profile_applied", "minimal")),
            tui_tour_shown=bool(data.get("tui_tour_shown", False)),
            version=str(data.get("version", "1.0")),
        )


@dataclass
class WizardConfig:
    """Configuration collected during wizard execution."""

    target_dir: Path = field(default_factory=_resolve_cortex_root)
    install_completions: bool = True
    install_aliases: bool = True
    link_rules: bool = True
    detected_shell: str = ""
    shell_rc_path: Optional[Path] = None

    # New fields for enhanced wizard
    experience_level: ExperienceLevel = ExperienceLevel.NEW
    detected_language: Optional[str] = None
    detected_framework: Optional[str] = None
    recommended_profile: str = "minimal"
    selected_profile: str = "minimal"
    setup_mcp: bool = True
    selected_mcp_servers: List[str] = field(default_factory=lambda: ["context7", "mcp-memory"])
    setup_hooks: bool = True
    configure_settings: bool = True
    post_setup_action: str = "none"  # "tour", "flags", or "none"


def _get_onboarding_state_path() -> Path:
    """Get path to onboarding state file."""
    cortex_root = _resolve_cortex_root()
    return cortex_root / ".onboarding-state.json"


def _load_onboarding_state() -> Optional[OnboardingState]:
    """Load persisted onboarding state.

    Returns:
        OnboardingState if file exists and is valid, None otherwise.
    """
    state_path = _get_onboarding_state_path()
    if not state_path.exists():
        return None

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return OnboardingState.from_dict(data)
    except (json.JSONDecodeError, OSError):
        pass

    return None


def _save_onboarding_state(config: WizardConfig) -> bool:
    """Save onboarding state to file.

    Args:
        config: Wizard configuration to save state from.

    Returns:
        True if saved successfully, False otherwise.
    """
    state = OnboardingState(
        completed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        experience_level=config.experience_level.value,
        profile_applied=config.selected_profile,
        tui_tour_shown=False,  # Will be updated when tour runs
        version="1.0",
    )

    state_path = _get_onboarding_state_path()
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        return True
    except OSError:
        return False


def should_run_wizard() -> bool:
    """Check if the wizard should run.

    Returns True if:
    - ~/.cortex/cortex-config.json doesn't exist (not bootstrapped)
    - CORTEX_SKIP_WIZARD env var is not set
    - Not running in a non-interactive environment (CI, etc.)
    """
    # Check skip env var
    if os.environ.get("CORTEX_SKIP_WIZARD"):
        return False

    # Check if stdin is a TTY (interactive terminal)
    if not sys.stdin.isatty():
        return False

    # Check if cortex has been bootstrapped (config file exists)
    # Note: We check for config file, not just directory, because hooks
    # may create ~/.cortex/logs before the wizard runs
    cortex_root = _resolve_cortex_root()
    config_file = cortex_root / "cortex-config.json"
    return not config_file.exists()


def _show_welcome(console: Console, experience: ExperienceLevel) -> bool:
    """Display welcome screen and confirm continuation.

    Args:
        console: Rich Console to use.
        experience: User's experience level for adaptive content.

    Returns True if user wants to continue, False to abort.
    """
    welcome_text = Text()
    welcome_text.append("Cortex enhances Claude Code with:\n\n", style="")
    welcome_text.append("  * ", style="cyan")
    welcome_text.append("Reusable rules, modes, and principles\n")
    welcome_text.append("  * ", style="cyan")
    welcome_text.append("MCP server documentation\n")
    welcome_text.append("  * ", style="cyan")
    welcome_text.append("Skill definitions and workflows\n")
    welcome_text.append("  * ", style="cyan")
    welcome_text.append("Shell aliases for quick exports\n\n")

    if experience == ExperienceLevel.NEW:
        welcome_text.append(
            "This wizard will guide you through setting up your environment step by step.",
            style="dim",
        )
    else:
        welcome_text.append(
            "Let's get you set up quickly.", style="dim"
        )

    console.print()
    console.print(
        Panel(
            welcome_text,
            title="[bold cyan]Welcome to Claude Cortex[/bold cyan]",
            subtitle="First Run Setup",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    return Confirm.ask("Continue with setup?", default=True, console=console)


def _get_experience_level(console: Console) -> ExperienceLevel:
    """Prompt for user experience level.

    Args:
        console: Rich Console to use.

    Returns:
        Selected experience level.
    """
    console.print()
    console.print("[bold]How would you describe yourself?[/bold]")
    console.print("-" * 50)
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="cyan")
    table.add_column("Description")

    table.add_row("[1]", "New to Claude Code - show me everything")
    table.add_row("[2]", "Experienced - standard setup")
    table.add_row("[3]", "Power user - minimal prompts, auto-defaults")

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Select an option",
        choices=["1", "2", "3"],
        default="1",
        console=console,
    )

    mapping = {
        "1": ExperienceLevel.NEW,
        "2": ExperienceLevel.EXPERIENCED,
        "3": ExperienceLevel.POWER_USER,
    }
    return mapping[choice]


def _get_target_directory(console: Console, experience: ExperienceLevel) -> Path:
    """Prompt for target directory selection.

    Args:
        console: Rich Console to use.
        experience: User's experience level.

    Returns the selected target directory path.
    """
    default_path = _resolve_cortex_root()

    if experience == ExperienceLevel.POWER_USER:
        # Auto-accept default for power users
        console.print(f"[dim]Using default location: {default_path}[/dim]")
        return default_path

    console.print()
    console.print("[bold]Installation Directory[/bold]")
    console.print("-" * 50)
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


def _detect_project_and_recommend(
    console: Console, config: WizardConfig
) -> Tuple[DetectionResult, str]:
    """Detect project type and recommend a profile.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns:
        Tuple of (detection result, recommended profile name).
    """
    project_path = Path.cwd()

    if config.experience_level == ExperienceLevel.NEW:
        console.print()
        console.print("[bold]Project Detection[/bold]")
        console.print("-" * 50)
        console.print(
            f"Analyzing current directory: [cyan]{project_path}[/cyan]"
        )
        console.print()

    # Detect project type
    detection = _detect_project_type(project_path)

    # Update config with detection
    config.detected_language = detection.get("language")
    config.detected_framework = detection.get("framework")

    # Get recommended profile
    recommended = _map_detection_to_profile(detection)
    config.recommended_profile = recommended

    if config.experience_level == ExperienceLevel.NEW:
        if detection.get("language"):
            console.print(f"  [green]*[/green] Language: {detection['language']}")
        if detection.get("framework"):
            console.print(f"  [green]*[/green] Framework: {detection['framework']}")
        if detection.get("infrastructure"):
            console.print(f"  [green]*[/green] Infrastructure: {detection['infrastructure']}")
        if not detection.get("language") and not detection.get("framework"):
            console.print("  [dim]No specific project type detected[/dim]")
        console.print()
        console.print(f"Recommended profile: [bold cyan]{recommended}[/bold cyan]")

    return detection, recommended


def _map_detection_to_profile(detection: DetectionResult) -> str:
    """Map detected project characteristics to a profile.

    Args:
        detection: Project detection result.

    Returns:
        Recommended profile name.
    """
    language = detection.get("language")
    framework = detection.get("framework")
    infrastructure = detection.get("infrastructure")

    # Frontend frameworks
    if framework in {"react", "vue", "nextjs"}:
        return "frontend"

    # Backend frameworks
    if framework in {"django", "flask", "express"}:
        return "backend"

    # Infrastructure projects
    if infrastructure in {"terraform", "docker-compose"}:
        return "devops"

    # Language-based defaults
    if language == "typescript":
        return "frontend"
    if language == "python":
        return "backend"
    if language == "go" or language == "rust":
        return "backend"

    # Default
    return "minimal"


def _get_profile_selection(
    console: Console, config: WizardConfig, recommended: str
) -> str:
    """Let user confirm or change profile selection.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.
        recommended: Recommended profile name.

    Returns:
        Selected profile name.
    """
    # Import here to avoid circular imports
    from .core.agents import BUILT_IN_PROFILES

    if config.experience_level == ExperienceLevel.POWER_USER:
        console.print(f"[dim]Applying profile: {recommended}[/dim]")
        return recommended

    console.print()
    console.print("[bold]Profile Selection[/bold]")
    console.print("-" * 50)

    # Show profile options
    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column("#", style="cyan", width=3)
    table.add_column("Profile", style="bold")
    table.add_column("Description")

    profile_descriptions = {
        "minimal": "Essential agents only - lightweight setup",
        "frontend": "React, Vue, TypeScript, UI/UX focus",
        "web-dev": "Full-stack web development",
        "backend": "Python, Go, Rust backend development",
        "devops": "Infrastructure, CI/CD, Kubernetes",
        "documentation": "Technical writing and docs",
        "data-ai": "Data science, ML, AI development",
        "quality": "Testing, code review, security",
        "meta": "Agent development and tooling",
        "developer-experience": "DX optimization, automation",
        "product": "Product development workflow",
        "full": "All agents enabled - maximum capability",
    }

    for i, profile in enumerate(BUILT_IN_PROFILES, 1):
        marker = " *" if profile == recommended else ""
        desc = profile_descriptions.get(profile, "")
        table.add_row(str(i), f"{profile}{marker}", desc)

    console.print(table)
    console.print()
    console.print("[dim]* = recommended based on project detection[/dim]")
    console.print()

    # Find index of recommended profile
    try:
        default_idx = BUILT_IN_PROFILES.index(recommended) + 1
    except ValueError:
        default_idx = 1

    choice = Prompt.ask(
        "Select a profile",
        default=str(default_idx),
        console=console,
    )

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(BUILT_IN_PROFILES):
            return BUILT_IN_PROFILES[idx]
    except ValueError:
        # Try matching by name
        if choice.lower() in BUILT_IN_PROFILES:
            return choice.lower()

    return recommended


def _get_shell_config(
    console: Console, config: WizardConfig
) -> Tuple[str, Optional[Path], bool, bool]:
    """Prompt for shell integration settings.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns tuple of (shell_name, rc_path, install_completions, install_aliases).
    """
    if config.experience_level == ExperienceLevel.POWER_USER:
        # Auto-detect and enable all for power users
        try:
            detected_shell, rc_path = shell_integration.detect_shell()
            console.print(f"[dim]Auto-configured shell: {detected_shell}[/dim]")
            return detected_shell, rc_path, True, True
        except RuntimeError:
            return "", None, False, False

    console.print()
    console.print("[bold]Shell Integration[/bold]")
    console.print("-" * 50)

    # Try to detect shell
    try:
        detected_shell, rc_path = shell_integration.detect_shell()
        console.print(
            f"Detected shell: [cyan]{detected_shell}[/cyan] ([dim]{rc_path}[/dim])"
        )
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


def _get_rule_linking_config(console: Console, config: WizardConfig) -> bool:
    """Prompt for rule linking configuration.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns True if rules should be symlinked to ~/.claude/rules/cortex/.
    """
    if config.experience_level == ExperienceLevel.POWER_USER:
        console.print("[dim]Auto-enabled rule discovery[/dim]")
        return True

    console.print()
    console.print("[bold]Rule Discovery[/bold]")
    console.print("-" * 50)
    console.print(
        "Cortex can symlink rules to [cyan]~/.claude/rules/cortex/[/cyan] so Claude\n"
        "Code automatically discovers them in any project."
    )
    console.print()

    return Confirm.ask("Enable automatic rule discovery?", default=True, console=console)


def _prompt_mcp_servers(console: Console, config: WizardConfig) -> List[str]:
    """Prompt user to select MCP servers to enable.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns:
        List of selected MCP server IDs.
    """
    if config.experience_level == ExperienceLevel.POWER_USER:
        # Power users get defaults
        return [k for k, v in MCP_SERVERS.items() if v.get("default")]

    console.print()
    console.print("[bold]MCP Server Selection[/bold]")
    console.print("-" * 50)

    if config.experience_level == ExperienceLevel.NEW:
        console.print(
            "MCP (Model Context Protocol) servers extend Claude's capabilities.\n"
            "Select which servers to enable:\n"
        )

    # Display table of available servers
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Server", width=15)
    table.add_column("Description", width=45)
    table.add_column("Default", width=8)

    server_ids = list(MCP_SERVERS.keys())
    for i, server_id in enumerate(server_ids, 1):
        server = MCP_SERVERS[server_id]
        default_marker = "[green]✓[/green]" if server.get("default") else ""
        table.add_row(
            str(i),
            str(server["name"]),
            str(server["description"]),
            default_marker,
        )

    console.print(table)
    console.print()

    # Get default selections
    defaults = [str(i + 1) for i, sid in enumerate(server_ids) if MCP_SERVERS[sid].get("default")]
    default_str = ",".join(defaults) if defaults else "none"

    selection = Prompt.ask(
        "Enter server numbers to enable (comma-separated, or 'all'/'none')",
        default=default_str,
        console=console,
    )

    if selection.lower() == "all":
        return server_ids
    if selection.lower() == "none":
        return []

    selected: List[str] = []
    for part in selection.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(server_ids):
                selected.append(server_ids[idx])

    return selected


def _setup_claude_integration(
    console: Console, config: WizardConfig
) -> Tuple[bool, List[str], bool, bool]:
    """Setup Claude Code integration (MCP, hooks, settings).

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns:
        Tuple of (setup_mcp, selected_mcp_servers, setup_hooks, configure_settings).
    """
    if config.experience_level == ExperienceLevel.POWER_USER:
        console.print("[dim]Claude integration auto-configured[/dim]")
        defaults = [k for k, v in MCP_SERVERS.items() if v.get("default")]
        return True, defaults, True, True

    console.print()
    console.print("[bold]Claude Code Integration[/bold]")
    console.print("-" * 50)

    if config.experience_level == ExperienceLevel.NEW:
        console.print("Cortex can integrate with Claude Code via:")
        console.print("  * MCP servers for enhanced capabilities")
        console.print("  * Hooks for automated workflows")
        console.print("  * Settings for optimized defaults")
        console.print()

    setup_mcp = Confirm.ask(
        "Configure MCP servers?",
        default=True,
        console=console,
    )

    selected_mcp: List[str] = []
    if setup_mcp:
        selected_mcp = _prompt_mcp_servers(console, config)

    setup_hooks = Confirm.ask(
        "Show available hooks? (can be installed later via TUI)",
        default=True,
        console=console,
    )

    configure_settings = Confirm.ask(
        "Apply recommended settings?",
        default=True,
        console=console,
    )

    return setup_mcp, selected_mcp, setup_hooks, configure_settings


def _write_mcp_config(target_dir: Path, selected_servers: List[str]) -> None:
    """Write .mcp.json with selected servers.

    Args:
        target_dir: Directory to write config to.
        selected_servers: List of server IDs to include.
    """
    mcp_config: Dict[str, object] = {"mcpServers": {}}
    servers_dict: Dict[str, object] = {}

    for server_id in selected_servers:
        if server_id in MCP_SERVERS:
            servers_dict[server_id] = MCP_SERVERS[server_id]["config"]

    mcp_config["mcpServers"] = servers_dict

    mcp_path = target_dir / ".mcp.json"
    mcp_path.write_text(json.dumps(mcp_config, indent=2) + "\n", encoding="utf-8")


def _prompt_post_setup_action(console: Console, config: WizardConfig) -> str:
    """Offer post-setup actions at end of wizard.

    Args:
        console: Rich Console to use.
        config: Wizard configuration.

    Returns:
        One of: "tour", "flags", "none"
    """
    if config.experience_level == ExperienceLevel.POWER_USER:
        return "none"

    console.print()
    console.print("[bold]What's Next?[/bold]")
    console.print("-" * 50)
    console.print("Choose what to do after setup:\n")
    console.print("  [cyan]1[/cyan] Take a quick tour of the TUI")
    console.print("  [cyan]2[/cyan] Open the Flag Manager to customize flags")
    console.print("  [cyan]3[/cyan] Exit and start using Cortex")
    console.print()

    choice = Prompt.ask(
        "Enter choice",
        choices=["1", "2", "3"],
        default="1",
        console=console,
    )

    if choice == "1":
        return "tour"
    elif choice == "2":
        return "flags"
    return "none"


def _show_summary(console: Console, config: WizardConfig) -> bool:
    """Display configuration summary and confirm execution.

    Returns True if user confirms, False to abort.
    """
    console.print()
    console.print("[bold]Configuration Summary[/bold]")
    console.print("-" * 50)
    console.print()

    # Configuration table
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Target directory", str(config.target_dir))
    table.add_row("Experience level", config.experience_level.value)
    table.add_row("Selected profile", config.selected_profile)

    if config.detected_language:
        table.add_row("Detected language", config.detected_language)
    if config.detected_framework:
        table.add_row("Detected framework", config.detected_framework)

    if config.detected_shell:
        table.add_row("Shell", config.detected_shell)
        table.add_row(
            "Completions",
            "[green]Yes[/green]" if config.install_completions else "[dim]No[/dim]",
        )
        table.add_row(
            "Aliases",
            "[green]Yes[/green]" if config.install_aliases else "[dim]No[/dim]",
        )
    else:
        table.add_row("Shell integration", "[dim]Skipped (not detected)[/dim]")

    table.add_row(
        "Rule linking",
        "[green]~/.claude/rules/cortex/[/green]"
        if config.link_rules
        else "[dim]No[/dim]",
    )

    if config.setup_mcp and config.selected_mcp_servers:
        server_names = [MCP_SERVERS[s]["name"] for s in config.selected_mcp_servers if s in MCP_SERVERS]
        table.add_row("MCP servers", ", ".join(str(n) for n in server_names))
    else:
        table.add_row("MCP servers", "[dim]None[/dim]")
    table.add_row(
        "Hooks setup",
        "[green]Yes[/green]" if config.setup_hooks else "[dim]No[/dim]",
    )

    console.print(table)
    console.print()

    # Show what will be created
    console.print("[bold]The following will be created:[/bold]")
    console.print(f"  * {config.target_dir}/rules/")
    console.print(f"  * {config.target_dir}/flags/")
    console.print(f"  * {config.target_dir}/modes/")
    console.print(f"  * {config.target_dir}/principles/")
    console.print(f"  * {config.target_dir}/templates/")
    console.print(f"  * {config.target_dir}/cortex-config.json")
    console.print()

    return Confirm.ask("Proceed with installation?", default=True, console=console)


def _execute_installation(
    console: Console, config: WizardConfig
) -> Tuple[int, List[str]]:
    """Execute the installation based on wizard configuration.

    Returns tuple of (exit_code, list of result messages).
    """
    results: List[str] = []
    exit_code = 0

    console.print()
    console.print("[bold]Installing Cortex[/bold]")
    console.print("-" * 50)

    # Run bootstrap
    code, message = installer.bootstrap(
        target_dir=config.target_dir,
        force=False,
        dry_run=False,
        link_rules=config.link_rules,
    )
    if code != 0:
        console.print(f"[red]x[/red] Bootstrap failed: {message}")
        return code, [message]

    # Parse bootstrap results to show progress
    for line in message.split("\n"):
        if line.strip().startswith("*"):
            console.print(f"[green]{line.strip()}[/green]")
            results.append(line.strip())
        elif line.strip().startswith("x"):
            console.print(f"[red]{line.strip()}[/red]")
            results.append(line.strip())
            exit_code = 1

    # Apply selected profile
    if config.selected_profile != "minimal":
        try:
            from .core.profiles import profile_apply

            code, msg = profile_apply(config.selected_profile)
            if code == 0:
                console.print(
                    f"[green]* Applied profile: {config.selected_profile}[/green]"
                )
                results.append(f"Applied profile: {config.selected_profile}")
            else:
                console.print(f"[yellow]! Profile: {msg}[/yellow]")
        except ImportError:
            # profile_apply might not exist yet
            console.print(
                f"[dim]Profile '{config.selected_profile}' will be applied on first TUI launch[/dim]"
            )

    # Write MCP configuration if servers were selected
    if config.setup_mcp and config.selected_mcp_servers:
        try:
            _write_mcp_config(config.target_dir, config.selected_mcp_servers)
            server_count = len(config.selected_mcp_servers)
            console.print(f"[green]* Configured {server_count} MCP server(s)[/green]")
            results.append(f"Configured {server_count} MCP server(s)")
        except Exception as e:
            console.print(f"[yellow]! MCP config: {e}[/yellow]")

    # Install shell completions if requested
    if config.install_completions and config.detected_shell:
        code, message = installer.install_completions(
            shell=config.detected_shell,
            force=False,
            dry_run=False,
        )
        if code == 0:
            console.print(
                f"[green]* Installed {config.detected_shell} completions[/green]"
            )
            results.append(f"Installed {config.detected_shell} completions")
        else:
            # Not a fatal error if completions fail
            console.print(f"[yellow]! Completions: {message.split(chr(10))[0]}[/yellow]")

    # Install shell aliases if requested
    if config.install_aliases and config.detected_shell:
        code, message = shell_integration.install_aliases(
            shell=config.detected_shell,
            rc_file=config.shell_rc_path,
            force=False,
            dry_run=False,
        )
        if code == 0:
            console.print(
                f"[green]* Installed shell aliases to {config.shell_rc_path}[/green]"
            )
            results.append(f"Installed aliases to {config.shell_rc_path}")
        else:
            # Not a fatal error if aliases fail
            console.print(f"[yellow]! Aliases: {message.split(chr(10))[0]}[/yellow]")

    # Save onboarding state
    if _save_onboarding_state(config):
        console.print("[green]* Saved onboarding state[/green]")
    else:
        console.print("[yellow]! Could not save onboarding state[/yellow]")

    return exit_code, results


def _show_next_steps(console: Console, config: WizardConfig) -> None:
    """Display next steps after successful installation."""
    next_steps = Text()
    next_steps.append("[bold green]Installation complete![/bold green]\n\n")
    next_steps.append("[bold]Next steps:[/bold]\n\n")

    if config.shell_rc_path:
        next_steps.append(f"  1. Reload your shell: [cyan]source {config.shell_rc_path}[/cyan]\n")
    else:
        next_steps.append("  1. Open a new terminal to apply changes\n")

    next_steps.append("  2. Launch TUI: [cyan]cortex tui[/cyan]\n")
    next_steps.append("  3. Start Claude with Cortex: [cyan]cortex start[/cyan]\n")
    next_steps.append("  4. Check status: [cyan]cortex status[/cyan]\n\n")
    next_steps.append("[dim]Run 'cortex --help' for more commands.[/dim]")

    console.print()
    console.print(
        Panel(
            next_steps,
            title="[bold]Setup Complete[/bold]",
            border_style="green",
            padding=(1, 2),
        )
    )


def _launch_tui_tour(console: Console) -> None:
    """Launch the TUI with the tour flag.

    Args:
        console: Rich Console to use.
    """
    console.print()
    console.print("[cyan]Launching TUI tour...[/cyan]")
    console.print()

    try:
        # Launch cortex tui --tour
        subprocess.run(
            [sys.executable, "-m", "claude_ctx_py", "tui", "--tour"],
            check=False,
        )
    except Exception as e:
        console.print(f"[yellow]Could not launch TUI: {e}[/yellow]")
        console.print("You can start the tour later with: [cyan]cortex tui --tour[/cyan]")


def _launch_flag_manager(console: Console) -> None:
    """Launch the TUI and navigate to the Flag Manager view.

    Args:
        console: Rich Console to use.
    """
    console.print()
    console.print("[cyan]Launching Flag Manager...[/cyan]")
    console.print()

    try:
        # Launch cortex tui --view=flags
        subprocess.run(
            [sys.executable, "-m", "claude_ctx_py", "tui", "--view", "flags"],
            check=False,
        )
    except Exception as e:
        console.print(f"[yellow]Could not launch Flag Manager: {e}[/yellow]")
        console.print("You can open it later with: [cyan]cortex tui[/cyan] then press [cyan]F[/cyan]")


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
        # Step 1: Get experience level first
        experience = _get_experience_level(console)

        # Step 2: Welcome
        if not _show_welcome(console, experience):
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            return 1, "Setup cancelled by user"

        # Build initial config
        config = WizardConfig(experience_level=experience)

        # Step 3: Target directory
        config.target_dir = _get_target_directory(console, experience)

        # Step 4: Project detection and profile recommendation
        detection, recommended = _detect_project_and_recommend(console, config)

        # Step 5: Profile selection
        config.selected_profile = _get_profile_selection(console, config, recommended)

        # Step 6: Shell integration
        (
            config.detected_shell,
            config.shell_rc_path,
            config.install_completions,
            config.install_aliases,
        ) = _get_shell_config(console, config)

        # Step 7: Rule linking
        config.link_rules = _get_rule_linking_config(console, config)

        # Step 8: Claude integration (MCP, hooks, settings)
        config.setup_mcp, config.selected_mcp_servers, config.setup_hooks, config.configure_settings = (
            _setup_claude_integration(console, config)
        )

        # Step 9: Offer post-setup action
        config.post_setup_action = _prompt_post_setup_action(console, config)

        # Step 10: Summary and confirmation
        if not _show_summary(console, config):
            console.print("\n[yellow]Setup cancelled.[/yellow]")
            return 1, "Setup cancelled by user"

        # Step 11: Execute
        exit_code, results = _execute_installation(console, config)

        if exit_code == 0:
            # Step 12: Next steps
            _show_next_steps(console, config)

            # Step 13: Launch post-setup action if requested
            if config.post_setup_action == "tour":
                _launch_tui_tour(console)
            elif config.post_setup_action == "flags":
                _launch_flag_manager(console)

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
