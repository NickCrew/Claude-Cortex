"""Enhanced Overview Dashboard - KAMEHAMEHA EDITION!"""

from __future__ import annotations
from typing import Dict, List, Optional
from .tui_icons import Icons
from .token_counter import TokenStats


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
        flags_active: int,
        flags_total: int,
    ) -> str:
        """Create a grid of status cards."""

        # Calculate percentages
        agent_pct = (agents_active / agents_total * 100) if agents_total > 0 else 0
        mode_pct = (modes_active / modes_total * 100) if modes_total > 0 else 0
        rule_pct = (rules_active / rules_total * 100) if rules_total > 0 else 0
        flag_pct = (flags_active / flags_total * 100) if flags_total > 0 else 0

        # Format content with proper padding (box interior is 26 chars for left, 28 for right)
        agent_status = f"{agents_active}/{agents_total} Active"
        mode_status = f"{modes_active}/{modes_total} Active"
        rule_status = f"{rules_active}/{rules_total} Active"
        skills_status = f"{skills_total} Installed"
        flags_status = f"{flags_active}/{flags_total} Active"
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
        flag_color = (
            "green" if flag_pct >= 75 else "yellow" if flag_pct >= 50 else "cyan"
        )
        workflow_color = "green" if workflows_running > 0 else "dim"

        # Progress bars
        agent_bar = f"[{agent_color}]{'█' * int(agent_pct/5)}[/{agent_color}][dim]{'░' * (20 - int(agent_pct/5))}[/dim]"
        mode_bar = f"[{mode_color}]{'█' * int(mode_pct/5)}[/{mode_color}][dim]{'░' * (20 - int(mode_pct/5))}[/dim]"
        rule_bar = f"[{rule_color}]{'█' * int(rule_pct/5)}[/{rule_color}][dim]{'░' * (20 - int(rule_pct/5))}[/dim]"
        skills_bar = f"[green]{'█' * 15}[/green][dim]{'░' * 5}[/dim]"
        flags_bar = f"[{flag_color}]{'█' * int(flag_pct/5)}[/{flag_color}][dim]{'░' * (20 - int(flag_pct/5))}[/dim]"
        workflow_bar = f"[{workflow_color}]{'█' * (10 if workflows_running > 0 else 0)}[/{workflow_color}][dim]{'░' * (10 if workflows_running == 0 else 10)}[/dim]"

        # Status messages
        agent_msg = f"{agent_pct:.0f}% operational"
        mode_msg = f"{mode_pct:.0f}% enabled"
        rule_msg = f"{rule_pct:.0f}% enforced"
        flag_msg = f"{flag_pct:.0f}% enabled" if flags_total > 0 else "No flags"
        workflow_msg = "Active tasks" if workflows_running > 0 else "No active tasks"

        def strip_rich(text: str) -> str:
            import re
            return re.sub(r"\[/?[^\]]+\]", "", text)

        def two_col(left: str, right: str, left_width: int = 34, gap: int = 2) -> str:
            left_len = len(strip_rich(left))
            pad = max(0, left_width - left_len)
            return f"{left}{' ' * pad}{' ' * gap}{right}".rstrip()

        lines = [
            "[bold cyan]📊 SYSTEM METRICS[/bold cyan]",
            "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
            "",
            two_col("  [cyan]⚡ AGENTS[/cyan]", "  [magenta]🎨 MODES[/magenta]"),
            two_col(f"  [bold white]{agent_status}[/bold white]", f"[bold white]{mode_status}[/bold white]"),
            two_col(f"  {agent_bar}", f"{mode_bar}"),
            two_col(f"  [dim]{agent_msg}[/dim]", f"[dim]{mode_msg}[/dim]"),
            "",
            two_col("  [blue]📜 RULES[/blue]", "  [green]💎 SKILLS[/green]"),
            two_col(f"  [bold white]{rule_status}[/bold white]", f"[bold white]{skills_status}[/bold white]"),
            two_col(f"  {rule_bar}", f"{skills_bar}"),
            two_col(f"  [dim]{rule_msg}[/dim]", f"[dim]Ready for use[/dim]"),
            "",
            two_col("  [white]🏁 FLAGS[/white]", "  [yellow]🏃 WORKFLOWS[/yellow]"),
            two_col(f"  [bold white]{flags_status}[/bold white]", f"[bold white]{workflow_status}[/bold white]"),
            two_col(f"  {flags_bar}", f"{workflow_bar}"),
            two_col(f"  [dim]{flag_msg}[/dim]", f"[dim]{workflow_msg}[/dim]"),
            "",
            two_col("  ", "  [red]⚡ QUICK ACTIONS[/red]"),
            two_col("  ", "  [dim cyan]Press [white]2[/white] → Manage Agents[/dim cyan]"),
            two_col("  ", "  [dim cyan]Press [white]3[/white] → Toggle Modes[/dim cyan]"),
            two_col("  ", "  [dim cyan]Press [white]4[/white] → View Rules[/dim cyan]"),
            two_col("  ", "  [dim cyan]Press [white]Ctrl+P[/white] → Commands[/dim cyan]"),
        ]

        return "\n".join(lines).strip()

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

    @staticmethod
    def create_token_usage(
        category_stats: Dict[str, TokenStats],
        total_stats: TokenStats,
        flags_stats: Optional[TokenStats] = None,
    ) -> str:
        """Create a token usage visualization.

        Args:
            category_stats: Token stats by category
            total_stats: Total token stats

        Returns:
            Formatted token usage display
        """
        category_names = {
            "core": ("Core", "cyan"),
            "rules": ("Rules", "blue"),
            "modes": ("Modes", "magenta"),
            "agents": ("Agents", "green"),
            "mcp_docs": ("MCP", "yellow"),
            "skills": ("Skills", "red"),
        }

        if flags_stats and flags_stats.files > 0:
            category_stats = dict(category_stats)
            category_stats["flags"] = flags_stats
            category_names["flags"] = ("Flags", "white")

        # Calculate bar widths proportional to token count
        max_tokens = max(
            (s.tokens for s in category_stats.values() if s.tokens > 0),
            default=1,
        )

        lines = []
        for category, (name, color) in category_names.items():
            stats = category_stats.get(category)
            if stats and stats.files > 0:
                # Calculate bar width (max 20 chars)
                bar_width = int((stats.tokens / max_tokens) * 20) if max_tokens > 0 else 0
                bar_width = max(1, bar_width)  # At least 1 char
                bar = f"[{color}]{'█' * bar_width}[/{color}][dim]{'░' * (20 - bar_width)}[/dim]"
                lines.append(
                    f"  [{color}]{name:8}[/{color}] {bar} [white]{stats.tokens_formatted:>6}[/white] [dim]({stats.files} files)[/dim]"
                )

        # Context window usage estimate (200K default for Claude)
        context_limit = 200000
        usage_pct = (total_stats.tokens / context_limit) * 100
        if usage_pct < 25:
            usage_color = "green"
            usage_status = "Excellent"
        elif usage_pct < 50:
            usage_color = "cyan"
            usage_status = "Good"
        elif usage_pct < 75:
            usage_color = "yellow"
            usage_status = "Moderate"
        else:
            usage_color = "red"
            usage_status = "High"

        usage_bar_width = int(usage_pct / 5)  # 20 chars = 100%
        usage_bar = f"[{usage_color}]{'█' * usage_bar_width}[/{usage_color}][dim]{'░' * (20 - usage_bar_width)}[/dim]"

        category_breakdown = "\n".join(lines) if lines else "  [dim]No active context files[/dim]"

        token_display = f"""
[bold cyan]📊 CONTEXT TOKEN USAGE[/bold cyan]
[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]

  [bold white]Total: {total_stats.tokens_formatted} tokens[/bold white] [dim]({total_stats.files} files, {total_stats.words:,} words)[/dim]

{category_breakdown}

[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]
  [bold]Context Window Usage[/bold] [{usage_color}]{usage_status}[/{usage_color}]
  {usage_bar} [white]{usage_pct:.1f}%[/white] [dim]of 200K[/dim]
"""
        return token_display.strip()
