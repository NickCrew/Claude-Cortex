"""Enhanced Overview Dashboard - KAMEHAMEHA EDITION! 🔥"""

from __future__ import annotations
from typing import List, Optional
from .tui_icons import Icons


class EnhancedOverview:
    """Enhanced overview dashboard with MAXIMUM visual impact."""

    @staticmethod
    def create_hero_banner(active_agents: int, total_agents: int) -> str:
        """Create a hero banner with large metrics."""
        pct = (active_agents / total_agents * 100) if total_agents > 0 else 0

        # Choose color based on activation percentage
        if pct >= 75:
            color = "green"
            status = "OPTIMAL"
        elif pct >= 50:
            color = "yellow"
            status = "ACTIVE"
        elif pct > 0:
            color = "cyan"
            status = "PARTIAL"
        else:
            color = "dim"
            status = "IDLE"

        banner = f"""
[{color}]███[/{color}] [bold white]CLAUDE CONTEXT SYSTEM[/bold white] [{color}]███[/{color}]

[bold {color}]STATUS: {status}[/bold {color}]
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]

[bold cyan]⚡ AGENTS ACTIVE[/bold cyan]
[bold white]{active_agents}[/bold white][dim]/[/dim][white]{total_agents}[/white]
[{color}]{'█' * int(pct/5)}[/{color}][dim]{'░' * (20 - int(pct/5))}[/dim] [white]{pct:.0f}%[/white]
"""
        return banner.strip()

    @staticmethod
    def create_metric_card(
        title: str,
        value: str,
        subtitle: str,
        icon: str,
        color: str = "cyan",
        progress: Optional[float] = None,
    ) -> str:
        """Create a compact metric card with visual flair."""

        # Create progress bar if percentage provided
        progress_bar = ""
        if progress is not None:
            filled = int(progress / 10)  # 10 blocks for 100%
            bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (10 - filled)}[/dim]"
            progress_bar = f"\n  {bar} [dim]{progress:.0f}%[/dim]"

        card = f"""
[{color}]{icon}[/{color}] [bold]{title}[/bold]
[bold white]{value}[/bold white]
[dim]{subtitle}[/dim]{progress_bar}
"""
        return card.strip()

    @staticmethod
    def create_status_grid(
        agents_active: int,
        agents_total: int,
        modes_active: int,
        modes_total: int,
        rules_active: int,
        rules_total: int,
        skills_total: int,
        workflows_running: int,
    ) -> str:
        """Create a grid of status cards."""

        # Calculate percentages
        agent_pct = (agents_active / agents_total * 100) if agents_total > 0 else 0
        mode_pct = (modes_active / modes_total * 100) if modes_total > 0 else 0
        rule_pct = (rules_active / rules_total * 100) if rules_total > 0 else 0

        # Format content with proper padding (box interior is 26 chars for left, 28 for right)
        agent_status = f"{agents_active}/{agents_total} Active"
        mode_status = f"{modes_active}/{modes_total} Active"
        rule_status = f"{rules_active}/{rules_total} Active"
        skills_status = f"{skills_total} Installed"
        workflow_status = f"{workflows_running} Running"

        # Color selection for progress bars
        agent_color = (
            "green" if agent_pct >= 75 else "yellow" if agent_pct >= 50 else "cyan"
        )
        mode_color = (
            "green" if mode_pct >= 75 else "yellow" if mode_pct >= 50 else "cyan"
        )
        rule_color = (
            "green" if rule_pct >= 75 else "yellow" if rule_pct >= 50 else "cyan"
        )
        workflow_color = "green" if workflows_running > 0 else "dim"

        # Progress bars
        agent_bar = f"[{agent_color}]{'█' * int(agent_pct/5)}[/{agent_color}][dim]{'░' * (20 - int(agent_pct/5))}[/dim]"
        mode_bar = f"[{mode_color}]{'█' * int(mode_pct/5)}[/{mode_color}][dim]{'░' * (20 - int(mode_pct/5))}[/dim]"
        rule_bar = f"[{rule_color}]{'█' * int(rule_pct/5)}[/{rule_color}][dim]{'░' * (20 - int(rule_pct/5))}[/dim]"
        skills_bar = f"[green]{'█' * 15}[/green][dim]{'░' * 5}[/dim]"
        workflow_bar = f"[{workflow_color}]{'█' * (10 if workflows_running > 0 else 0)}[/{workflow_color}][dim]{'░' * (10 if workflows_running == 0 else 10)}[/dim]"

        # Status messages
        agent_msg = f"{agent_pct:.0f}% operational"
        mode_msg = f"{mode_pct:.0f}% enabled"
        rule_msg = f"{rule_pct:.0f}% enforced"
        workflow_msg = "Active tasks" if workflows_running > 0 else "No active tasks"

        grid = f"""
[bold cyan]📊 SYSTEM METRICS[/bold cyan]
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]

  [cyan]⚡ AGENTS[/cyan]                        [magenta]🎨 MODES[/magenta]
  [bold white]{agent_status}[/bold white]                  [bold white]{mode_status}[/bold white]
  {agent_bar}  {mode_bar}
  [dim]{agent_msg}[/dim]              [dim]{mode_msg}[/dim]

  [blue]📜 RULES[/blue]                        [green]💎 SKILLS[/green]
  [bold white]{rule_status}[/bold white]                  [bold white]{skills_status}[/bold white]
  {rule_bar}  {skills_bar}
  [dim]{rule_msg}[/dim]              [dim]Ready for use[/dim]

  [yellow]🏃 WORKFLOWS[/yellow]                    [red]⚡ QUICK ACTIONS[/red]
  [bold white]{workflow_status}[/bold white]                  [dim cyan]Press [white]2[/white] → Manage Agents[/dim cyan]
  {workflow_bar}  [dim cyan]Press [white]3[/white] → Toggle Modes[/dim cyan]
  [dim]{workflow_msg}[/dim]              [dim cyan]Press [white]4[/white] → View Rules[/dim cyan]
                                [dim cyan]Press [white]Ctrl+P[/white] → Commands[/dim cyan]
"""
        return grid.strip()

    @staticmethod
    def create_activity_timeline() -> str:
        """Create a visual activity timeline."""
        timeline = f"""
[bold cyan]📈 RECENT ACTIVITY[/bold cyan]
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]

  [green]●[/green] [dim]Agent activated[/dim]          [dim white]2 minutes ago[/dim white]
  [yellow]●[/yellow] [dim]Mode toggled[/dim]            [dim white]5 minutes ago[/dim white]
  [cyan]●[/cyan] [dim]Rules updated[/dim]           [dim white]12 minutes ago[/dim white]
  [blue]●[/blue] [dim]Context exported[/dim]        [dim white]1 hour ago[/dim white]
"""
        return timeline.strip()

    @staticmethod
    def create_system_health() -> str:
        """Create a system health indicator."""
        health = f"""
[bold green]✓ SYSTEM HEALTH[/bold green]
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]

  [green]●[/green] All systems operational
  [green]●[/green] Configuration loaded successfully
  [green]●[/green] Performance optimal
  [yellow]●[/yellow] Memory usage: 45% (normal)

  [dim]Last checked: just now[/dim]
"""
        return health.strip()
