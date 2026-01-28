"""Command-line interface for cortex-py."""

from __future__ import annotations

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Iterable, List, cast, Dict, Any, Callable

from . import core
from .core.migration import migrate_to_file_activation, migrate_commands_layout
from .messages import RESTART_REQUIRED_MESSAGE


def _enable_argcomplete(parser: argparse.ArgumentParser) -> None:
    """Integrate argcomplete if it is available."""

    try:  # pragma: no cover - optional dependency
        import argcomplete
    except ImportError:  # pragma: no cover
        return

    argcomplete.autocomplete(parser)


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


_ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_PATTERN.sub("", text)


def _message_indicates_change(message: str) -> bool:
    clean = _strip_ansi(message or "")
    for line in clean.splitlines():
        line = line.strip().lower()
        if line.startswith("activated ") or line.startswith("deactivated "):
            return True
    return False


def _restart_notice() -> str:
    return RESTART_REQUIRED_MESSAGE


def _build_agent_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    agent_parser = subparsers.add_parser("agent", help="Agent commands")
    agent_sub = agent_parser.add_subparsers(dest="agent_command")
    agent_sub.add_parser("list", help="List available agents")
    agent_sub.add_parser("status", help="Show active agents")
    agent_activate = agent_sub.add_parser(
        "activate", help="Activate one or more agents"
    )
    agent_activate.add_argument("agents", nargs="+", help="Agent name(s) (without .md)")
    agent_deactivate = agent_sub.add_parser(
        "deactivate", help="Deactivate one or more agents"
    )
    agent_deactivate.add_argument(
        "agents", nargs="+", help="Agent name(s) (without .md)"
    )
    agent_deactivate.add_argument(
        "--force",
        action="store_true",
        help="Override dependency checks",
    )
    agent_deps_parser = agent_sub.add_parser(
        "deps", help="Show dependency information for an agent"
    )
    agent_deps_parser.add_argument("agent", help="Agent name (without .md)")
    agent_graph = agent_sub.add_parser(
        "graph", help="Display dependency graph for agents"
    )
    agent_graph.add_argument(
        "--export",
        dest="export",
        metavar="PATH",
        help="Write dependency map to the given path",
    )
    agent_validate_parser = agent_sub.add_parser(
        "validate", help="Validate agent metadata against schema"
    )
    agent_validate_parser.add_argument(
        "--all",
        dest="include_all",
        action="store_true",
        help="Validate all active and disabled agents",
    )
    agent_validate_parser.add_argument(
        "agents",
        nargs="*",
        help="Agent names or paths to validate",
    )


def _build_rules_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    rules_parser = subparsers.add_parser("rules", help="Rule commands")
    rules_sub = rules_parser.add_subparsers(dest="rules_command")
    rules_sub.add_parser("list", help="List available rules")
    rules_sub.add_parser("status", help="Show active rule modules")
    rules_activate = rules_sub.add_parser(
        "activate", help="Activate one or more rule modules"
    )
    rules_activate.add_argument("rules", nargs="+", help="Rule name(s) (without .md)")
    rules_deactivate = rules_sub.add_parser(
        "deactivate", help="Deactivate one or more rule modules"
    )
    rules_deactivate.add_argument("rules", nargs="+", help="Rule name(s) (without .md)")


def _build_hooks_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    hooks_parser = subparsers.add_parser("hooks", help="Hook commands")
    hooks_sub = hooks_parser.add_subparsers(dest="hooks_command")
    hooks_validate = hooks_sub.add_parser(
        "validate", help="Validate hooks.json configuration"
    )
    hooks_validate.add_argument(
        "--path",
        type=Path,
        help="Path to hooks.json (defaults to plugin root hooks/hooks.json)",
    )


def _build_setup_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    setup_parser = subparsers.add_parser("setup", help="Setup and migration commands")
    setup_sub = setup_parser.add_subparsers(dest="setup_command")
    setup_sub.add_parser(
        "migrate",
        help="Migrate CLAUDE.md comment-based activation to file-based rules/modes",
    )
    migrate_cmds = setup_sub.add_parser(
        "migrate-commands",
        help="Flatten legacy commands/ namespaces into a single directory",
    )
    migrate_cmds.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned moves without changing files",
    )
    migrate_cmds.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing targets (backs up overwritten files)",
    )


def _build_skills_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    skills_parser = subparsers.add_parser("skills", help="Skill commands")
    skills_sub = skills_parser.add_subparsers(dest="skills_command")
    skills_sub.add_parser("list", help="List available skills")
    skills_info_parser = skills_sub.add_parser("info", help="Show skill details")
    skills_info_parser.add_argument("skill", help="Skill name")
    skills_validate_parser = skills_sub.add_parser(
        "validate", help="Validate skill metadata"
    )
    skills_validate_parser.add_argument(
        "skills",
        nargs="*",
        help="Skill names to validate (default: all)",
    )
    skills_validate_parser.add_argument(
        "--all",
        dest="validate_all",
        action="store_true",
        help="Validate all skills",
    )
    skills_analyze_parser = skills_sub.add_parser(
        "analyze", help="Analyze text and suggest matching skills"
    )
    skills_analyze_parser.add_argument(
        "text",
        help="Text to analyze for skill keywords",
    )
    skills_suggest_parser = skills_sub.add_parser(
        "suggest", help="Suggest skills based on project context"
    )
    skills_suggest_parser.add_argument(
        "--project-dir",
        dest="suggest_project_dir",
        default=".",
        help="Project directory to analyze (default: current directory)",
    )
    skills_metrics_parser = skills_sub.add_parser(
        "metrics", help="Show skill usage metrics"
    )
    skills_metrics_parser.add_argument(
        "skill",
        nargs="?",
        help="Skill name (optional - shows all if omitted)",
    )
    skills_metrics_parser.add_argument(
        "--reset",
        dest="metrics_reset",
        action="store_true",
        help="Reset all metrics",
    )
    skills_deps_parser = skills_sub.add_parser(
        "deps", help="Show which agents use a skill"
    )
    skills_deps_parser.add_argument("skill", help="Skill name")
    skills_agents_parser = skills_sub.add_parser(
        "agents", help="Show which agents use a skill (alias for deps)"
    )
    skills_agents_parser.add_argument("skill", help="Skill name")
    skills_compose_parser = skills_sub.add_parser(
        "compose", help="Show dependency tree for a skill"
    )
    skills_compose_parser.add_argument("skill", help="Skill name")
    skills_versions_parser = skills_sub.add_parser(
        "versions", help="Show version information for a skill"
    )
    skills_versions_parser.add_argument("skill", help="Skill name")
    skills_analytics_parser = skills_sub.add_parser(
        "analytics", help="Show skill effectiveness analytics"
    )
    skills_analytics_parser.add_argument(
        "--metric",
        dest="analytics_metric",
        choices=[
            "trending",
            "roi",
            "effectiveness",
            "tokens",
            "activations",
            "success_rate",
        ],
        help="Specific metric to display",
    )
    skills_report_parser = skills_sub.add_parser(
        "report", help="Generate comprehensive analytics report"
    )
    skills_report_parser.add_argument(
        "--format",
        dest="report_format",
        choices=["text", "json", "csv"],
        default="text",
        help="Report output format (default: text)",
    )
    skills_trending_parser = skills_sub.add_parser(
        "trending", help="Show trending skills over time"
    )
    skills_trending_parser.add_argument(
        "--days",
        dest="trending_days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    skills_recommend_parser = skills_sub.add_parser(
        "recommend", help="Get AI-powered skill recommendations"
    )
    skills_feedback_parser = skills_sub.add_parser(
        "feedback", help="Provide feedback on skill recommendations"
    )
    skills_feedback_parser.add_argument("skill", help="Skill name")
    skills_feedback_parser.add_argument(
        "rating",
        choices=["helpful", "not-helpful"],
        help="Was the recommendation helpful?",
    )
    skills_feedback_parser.add_argument(
        "--comment",
        dest="feedback_comment",
        help="Optional comment explaining your feedback",
    )
    # Rating commands
    skills_rate_parser = skills_sub.add_parser(
        "rate", help="Rate a skill with stars and optional review"
    )
    skills_rate_parser.add_argument("skill", help="Skill name to rate")
    skills_rate_parser.add_argument(
        "--stars",
        dest="stars",
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5],
        help="Star rating (1-5)",
    )
    skills_rate_parser.add_argument(
        "--helpful",
        dest="helpful",
        action="store_true",
        default=True,
        help="Mark as helpful (default: True)",
    )
    skills_rate_parser.add_argument(
        "--not-helpful",
        dest="not_helpful",
        action="store_true",
        help="Mark as not helpful",
    )
    skills_rate_parser.add_argument(
        "--succeeded",
        dest="task_succeeded",
        action="store_true",
        default=True,
        help="Task succeeded with this skill (default: True)",
    )
    skills_rate_parser.add_argument(
        "--failed",
        dest="task_failed",
        action="store_true",
        help="Task failed despite using this skill",
    )
    skills_rate_parser.add_argument(
        "--review",
        dest="review",
        help="Optional written review",
    )
    skills_ratings_parser = skills_sub.add_parser(
        "ratings", help="Show ratings and reviews for a skill"
    )
    skills_ratings_parser.add_argument("skill", help="Skill name")
    skills_top_rated_parser = skills_sub.add_parser(
        "top-rated", help="Show top-rated skills"
    )
    skills_top_rated_parser.add_argument(
        "--category",
        dest="top_rated_category",
        help="Optional category filter",
    )
    skills_top_rated_parser.add_argument(
        "--limit",
        dest="top_rated_limit",
        type=int,
        default=10,
        help="Maximum number of skills to show (default: 10)",
    )
    skills_export_ratings_parser = skills_sub.add_parser(
        "export-ratings", help="Export skill ratings data"
    )
    skills_export_ratings_parser.add_argument(
        "--skill",
        dest="export_skill",
        help="Optional skill name to filter by (exports all if not specified)",
    )
    skills_export_ratings_parser.add_argument(
        "--format",
        dest="export_format",
        choices=["json", "csv"],
        default="json",
        help="Export format (default: json)",
    )
    skills_community_parser = skills_sub.add_parser(
        "community", help="Community skill commands"
    )
    community_sub = skills_community_parser.add_subparsers(dest="community_command")
    community_list_parser = community_sub.add_parser(
        "list", help="List community skills"
    )
    community_list_parser.add_argument(
        "--tag",
        dest="community_list_tag",
        help="Filter by tag",
    )
    community_list_parser.add_argument(
        "--search",
        dest="community_list_search",
        help="Search query",
    )
    community_list_parser.add_argument(
        "--verified",
        dest="community_list_verified",
        action="store_true",
        help="Show only verified skills",
    )
    community_list_parser.add_argument(
        "--sort",
        dest="community_list_sort",
        help="Sort field (e.g., name, rating, downloads)",
    )
    community_install_parser = community_sub.add_parser(
        "install", help="Install a community skill"
    )
    community_install_parser.add_argument(
        "skill",
        help="Skill name to install",
    )
    community_validate_parser = community_sub.add_parser(
        "validate", help="Validate a community skill"
    )
    community_validate_parser.add_argument(
        "skill",
        help="Skill name to validate",
    )
    community_rate_parser = community_sub.add_parser(
        "rate", help="Rate a community skill"
    )
    community_rate_parser.add_argument(
        "skill",
        help="Skill name to rate",
    )
    community_rate_parser.add_argument(
        "--rating",
        dest="community_rating",
        type=int,
        required=True,
        help="Rating value (1-5)",
    )
    community_search_parser = community_sub.add_parser(
        "search", help="Search community skills"
    )
    community_search_parser.add_argument(
        "query",
        help="Search query",
    )
    community_search_parser.add_argument(
        "--tags",
        dest="community_search_tags",
        nargs="*",
        help="Filter by tags",
    )


def _build_mcp_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    mcp_parser = subparsers.add_parser("mcp", help="MCP server commands")
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command")
    mcp_sub.add_parser("list", help="List all MCP servers with status")
    mcp_sub.add_parser("list-docs", help="List MCP docs with activation status")
    mcp_sub.add_parser("status", help="Show active MCP docs")
    mcp_activate_parser = mcp_sub.add_parser("activate", help="Activate MCP doc(s) in CLAUDE.md")
    mcp_activate_parser.add_argument("docs", nargs="+", help="MCP doc name(s) (without .md)")
    mcp_deactivate_parser = mcp_sub.add_parser("deactivate", help="Deactivate MCP doc(s) from CLAUDE.md")
    mcp_deactivate_parser.add_argument("docs", nargs="+", help="MCP doc name(s) (without .md)")
    mcp_show_parser = mcp_sub.add_parser("show", help="Show detailed server info")
    mcp_show_parser.add_argument("server", help="Server name")
    mcp_docs_parser = mcp_sub.add_parser("docs", help="Display server documentation")
    mcp_docs_parser.add_argument("server", help="Server name")
    mcp_test_parser = mcp_sub.add_parser("test", help="Test server configuration")
    mcp_test_parser.add_argument("server", help="Server name")
    mcp_sub.add_parser("diagnose", help="Diagnose all server issues")
    mcp_snippet_parser = mcp_sub.add_parser("snippet", help="Generate config snippet")
    mcp_snippet_parser.add_argument("server", help="Server name")


def _build_init_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    init_parser = subparsers.add_parser("init", help="Initialization commands")
    init_parser.add_argument(
        "--interactive",
        "-i",
        dest="init_interactive",
        action="store_true",
        help="Run initialization wizard",
    )
    init_parser.add_argument(
        "--resume",
        dest="init_resume_flag",
        action="store_true",
        help="Resume the last initialization session",
    )
    init_sub = init_parser.add_subparsers(dest="init_command")

    init_detect = init_sub.add_parser(
        "detect",
        help="Detect project context and refresh init cache",
    )
    init_detect.add_argument(
        "path",
        nargs="?",
        help="Target project directory (defaults to current working directory)",
    )

    init_sub.add_parser(
        "minimal",
        help="Apply minimal defaults via the init system",
    )

    init_profile = init_sub.add_parser(
        "profile",
        help="Capture profile selection for init",
    )
    init_profile.add_argument(
        "name",
        nargs="?",
        help="Profile name to activate",
    )

    init_status = init_sub.add_parser(
        "status",
        help="Show stored init state for a project",
    )
    init_status.add_argument(
        "target",
        nargs="?",
        help="Project path or slug",
    )
    init_status.add_argument(
        "--json",
        action="store_true",
        help="Emit detection JSON instead of summary output",
    )

    init_reset = init_sub.add_parser("reset", help="Clear init state for a project")
    init_reset.add_argument(
        "target",
        nargs="?",
        help="Project path or slug (defaults to current working directory)",
    )

    init_resume = init_sub.add_parser("resume", help="Resume last init session")
    init_resume.add_argument(
        "target",
        nargs="?",
        help="Project path or slug (defaults to current working directory)",
    )

    init_wizard = init_sub.add_parser("wizard", help="Run initialization wizard")
    init_wizard.add_argument(
        "target",
        nargs="?",
        help="Project path (defaults to current working directory)",
    )


def _build_worktree_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    worktree_parser = subparsers.add_parser(
        "worktree", help="Git worktree management commands"
    )
    worktree_sub = worktree_parser.add_subparsers(dest="worktree_command")
    worktree_sub.add_parser("list", help="List git worktrees")

    worktree_add_parser = worktree_sub.add_parser("add", help="Add a new worktree")
    worktree_add_parser.add_argument("branch", help="Branch name for the worktree")
    worktree_add_parser.add_argument(
        "--path",
        dest="worktree_path",
        help="Target path for the worktree (defaults to .worktrees/<branch>)",
    )
    worktree_add_parser.add_argument(
        "--base",
        dest="worktree_base",
        help="Base reference for a new branch (default: HEAD)",
    )
    worktree_add_parser.add_argument(
        "--force",
        action="store_true",
        help="Force add even if branch is checked out elsewhere",
    )
    worktree_add_parser.add_argument(
        "--no-gitignore",
        dest="worktree_gitignore",
        action="store_false",
        help="Skip updating .gitignore for local worktree directories",
    )

    worktree_remove_parser = worktree_sub.add_parser(
        "remove", help="Remove a worktree"
    )
    worktree_remove_parser.add_argument(
        "target", help="Worktree path or branch name"
    )
    worktree_remove_parser.add_argument(
        "--force",
        action="store_true",
        help="Force removal even if worktree is dirty",
    )

    worktree_prune_parser = worktree_sub.add_parser(
        "prune", help="Prune stale worktrees"
    )
    worktree_prune_parser.add_argument(
        "--dry-run",
        dest="worktree_dry_run",
        action="store_true",
        help="Show what would be pruned without deleting",
    )
    worktree_prune_parser.add_argument(
        "--verbose",
        dest="worktree_verbose",
        action="store_true",
        help="Verbose prune output",
    )

    worktree_dir_parser = worktree_sub.add_parser(
        "dir", help="Show or set the worktree base directory"
    )
    worktree_dir_parser.add_argument(
        "path",
        nargs="?",
        help="Base directory path to store in git config",
    )
    worktree_dir_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the configured base directory",
    )


def _build_ai_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    ai_parser = subparsers.add_parser("ai", help="AI assistant commands")
    ai_sub = ai_parser.add_subparsers(dest="ai_command")
    ai_sub.add_parser("recommend", help="Show intelligent agent recommendations")
    ai_sub.add_parser(
        "auto-activate", help="Auto-activate high-confidence recommendations"
    )
    ai_export = ai_sub.add_parser("export", help="Export recommendations to JSON")
    ai_export.add_argument(
        "--output",
        default="ai-recommendations.json",
        help="Output file path (default: ai-recommendations.json)",
    )
    ai_record = ai_sub.add_parser(
        "record-success", help="Record current session as successful for learning"
    )
    ai_record.add_argument(
        "--outcome",
        default="success",
        help="Outcome description (default: success)",
    )
    ai_watch = ai_sub.add_parser(
        "watch", help="Watch mode - real-time monitoring and recommendations"
    )
    ai_watch.add_argument(
        "--no-auto-activate",
        dest="no_auto_activate",
        action="store_true",
        default=None,
        help="Disable auto-activation of high-confidence agents",
    )
    ai_watch.add_argument(
        "--daemon",
        action="store_true",
        help="Run watch mode in the background as a daemon",
    )
    ai_watch.add_argument(
        "--status",
        action="store_true",
        help="Show watch daemon status",
    )
    ai_watch.add_argument(
        "--stop",
        action="store_true",
        help="Stop the watch daemon",
    )
    ai_watch.add_argument(
        "--log",
        dest="watch_log",
        help="Log file for daemon mode (default: ~/.cortex/logs/watch.log)",
    )
    ai_watch.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Confidence threshold for notifications (0.0-1.0, default: config or 0.7)",
    )
    ai_watch.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Check interval in seconds (default: config or 2.0)",
    )
    ai_watch.add_argument(
        "--dir",
        dest="watch_dirs",
        action="append",
        default=[],
        help="Directory to watch (can be repeated or comma-separated)",
    )


def _build_export_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    export_parser = subparsers.add_parser("export", help="Export context commands")
    export_sub = export_parser.add_subparsers(dest="export_command")
    export_list = export_sub.add_parser(
        "list", help="List available context components"
    )
    export_context = export_sub.add_parser(
        "context", help="Export context to markdown file"
    )
    export_context.add_argument(
        "output",
        help="Output file path (e.g., my-context.md) or '-' for stdout",
    )
    export_context.add_argument(
        "--exclude",
        dest="exclude_categories",
        action="append",
        choices=["core", "rules", "modes", "agents", "mcp_docs", "skills"],
        help="Exclude a category from export (can be used multiple times)",
    )
    export_context.add_argument(
        "--include",
        dest="include_categories",
        action="append",
        choices=["core", "rules", "modes", "agents", "mcp_docs", "skills"],
        help="Include only specified categories (can be used multiple times)",
    )
    export_context.add_argument(
        "--exclude-file",
        dest="exclude_files",
        action="append",
        help="Exclude specific file (e.g., rules/quality-rules.md)",
    )
    export_context.add_argument(
        "--no-agent-generic",
        dest="no_agent_generic",
        action="store_true",
        help="Use Claude-specific format instead of agent-generic",
    )


def _build_completion_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    completion_parser = subparsers.add_parser(
        "completion", help="Generate shell completion scripts"
    )
    completion_parser.add_argument(
        "shell", choices=["bash", "zsh", "fish"], help="Shell type (bash, zsh, or fish)"
    )
    completion_parser.add_argument(
        "--install", action="store_true", help="Show installation instructions"
    )


def _build_install_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    install_parser = subparsers.add_parser(
        "install", help="Install CLI integrations and optional extras"
    )
    install_sub = install_parser.add_subparsers(dest="install_command")

    # Install aliases
    aliases_parser = install_sub.add_parser(
        "aliases", help="Install shell aliases for Warp AI and terminal AI tools"
    )
    aliases_parser.add_argument(
        "--shell",
        choices=["bash", "zsh", "fish"],
        help="Target shell (auto-detected if not specified)",
    )
    aliases_parser.add_argument(
        "--rc-file",
        dest="rc_file",
        type=Path,
        help="Target RC file (auto-detected if not specified)",
    )
    aliases_parser.add_argument(
        "--force", action="store_true", help="Reinstall even if already installed"
    )
    aliases_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    aliases_parser.add_argument(
        "--uninstall", action="store_true", help="Remove installed aliases"
    )
    aliases_parser.add_argument(
        "--show", action="store_true", help="Show available aliases without installing"
    )

    # Install shell completions
    completions_parser = install_sub.add_parser(
        "completions", help="Install shell completion scripts"
    )
    completions_parser.add_argument(
        "--shell",
        choices=["bash", "zsh", "fish"],
        help="Target shell (auto-detected if not specified)",
    )
    completions_parser.add_argument(
        "--path",
        dest="completion_path",
        type=Path,
        help="Target completion file path (overrides default)",
    )
    completions_parser.add_argument(
        "--system",
        action="store_true",
        help="Use system completion directory (may require sudo)",
    )
    completions_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing completion file"
    )
    completions_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )

    # Install manpages
    manpage_parser = install_sub.add_parser(
        "manpage", help="Install manpage files"
    )
    manpage_parser.add_argument(
        "--path",
        dest="manpath",
        type=Path,
        help="Target man1 directory (overrides default)",
    )
    manpage_parser.add_argument(
        "--system",
        action="store_true",
        help="Install to system manpath (may require sudo)",
    )
    manpage_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )

    # Install architecture docs
    docs_parser = install_sub.add_parser(
        "docs", help="Install architecture docs to ~/.cortex/docs"
    )
    docs_parser.add_argument(
        "--target",
        dest="docs_target",
        type=Path,
        help="Target docs directory (overrides default)",
    )
    docs_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )

    # Bootstrap ~/.cortex with bundled assets
    bootstrap_parser = install_sub.add_parser(
        "bootstrap", help="Initialize ~/.cortex with bundled assets and config"
    )
    bootstrap_parser.add_argument(
        "--target",
        dest="bootstrap_target",
        type=Path,
        help="Target directory (default: ~/.cortex)",
    )
    bootstrap_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing directories"
    )
    bootstrap_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )
    bootstrap_parser.add_argument(
        "--link-rules",
        action="store_true",
        help="Also create symlinks in ~/.claude/rules/cortex/ for Claude discovery",
    )

    # Sync rule symlinks
    rules_parser = install_sub.add_parser(
        "rules", help="Sync rule symlinks to ~/.claude/rules/cortex/"
    )
    rules_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without making changes",
    )
    rules_parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove all cortex rule symlinks",
    )

    # Run all post-install steps
    post_parser = install_sub.add_parser(
        "post", help="Install completions, manpages, and docs"
    )
    post_parser.add_argument(
        "--shell",
        choices=["bash", "zsh", "fish"],
        help="Target shell (auto-detected if not specified)",
    )
    post_parser.add_argument(
        "--completion-path",
        dest="completion_path",
        type=Path,
        help="Override completion output path",
    )
    post_parser.add_argument(
        "--manpath",
        dest="manpath",
        type=Path,
        help="Override manpage directory",
    )
    post_parser.add_argument(
        "--docs-target",
        dest="docs_target",
        type=Path,
        help="Override docs target directory",
    )
    post_parser.add_argument(
        "--system",
        action="store_true",
        help="Use system paths for completions/manpages",
    )
    post_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing completion file"
    )
    post_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing files",
    )

    # Install package via pip/uv/pipx
    package_parser = install_sub.add_parser(
        "package", help="Install the package via pip, uv, or pipx"
    )
    package_parser.add_argument(
        "--manager",
        choices=["pip", "uv", "pipx"],
        default="pip",
        help="Package manager to use",
    )
    package_parser.add_argument(
        "--path",
        type=Path,
        help="Local path to install (defaults to current directory when used)",
    )
    package_parser.add_argument(
        "--name",
        default="claude-cortex",
        help="Package name for non-path installs",
    )
    package_parser.add_argument(
        "--editable",
        action="store_true",
        help="Install in editable mode (local paths only)",
    )
    package_parser.add_argument(
        "--dev",
        action="store_true",
        help="Install with [dev] extras",
    )
    package_parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Upgrade if already installed",
    )
    package_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without running",
    )


def _build_docs_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    docs_parser = subparsers.add_parser("docs", help="Documentation viewer")
    docs_parser.add_argument(
        "page",
        nargs="?",
        help="Documentation page to view (e.g., architecture/overview). Lists pages if omitted.",
    )


def _build_statusline_parser(
    subparsers: argparse._SubParsersAction[Any],
) -> None:
    from . import statusline

    statusline_parser = subparsers.add_parser(
        "statusline", help="Render Claude Code status line"
    )
    statusline.add_statusline_arguments(statusline_parser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cortex",
        description="Python implementation of cortex list and status commands",
    )
    parser.add_argument(
        "--scope",
        choices=["auto", "project", "global", "plugin"],
        help="Select which scope to use (default: auto)",
    )
    parser.add_argument(
        "--plugin-root",
        dest="plugin_root",
        type=Path,
        help="Explicit path to the plugin root (overrides --scope)",
    )
    parser.add_argument(
        "--skip-wizard",
        "--no-init",
        dest="skip_wizard",
        action="store_true",
        help="Skip the first-run wizard even if ~/.cortex doesn't exist",
    )
    subparsers = parser.add_subparsers(dest="command")

    _build_agent_parser(subparsers)
    _build_rules_parser(subparsers)
    _build_hooks_parser(subparsers)
    _build_skills_parser(subparsers)
    _build_mcp_parser(subparsers)
    _build_init_parser(subparsers)
    _build_worktree_parser(subparsers)
    subparsers.add_parser("status", help="Show overall status")
    _build_statusline_parser(subparsers)
    tui_parser = subparsers.add_parser(
        "tui", help="Launch interactive TUI for agent management"
    )
    tui_parser.add_argument(
        "--theme",
        type=Path,
        help="Path to a Textual .tcss theme override file",
    )
    tui_parser.add_argument(
        "--tour",
        action="store_true",
        help="Start with the interactive tour",
    )
    tui_parser.add_argument(
        "--view",
        type=str,
        help="Start on a specific view (e.g., 'flags', 'agents', 'rules')",
    )
    _build_ai_parser(subparsers)
    _build_export_parser(subparsers)
    _build_completion_parser(subparsers)
    _build_install_parser(subparsers)
    _build_docs_parser(subparsers)
    _build_doctor_parser(subparsers)
    _build_memory_parser(subparsers)
    _build_setup_parser(subparsers)
    subparsers.add_parser("dashboard", help="Launch web-based dashboard")
    review_parser = subparsers.add_parser("review", help="Run review gate before task completion")
    review_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what reviewers would be activated without activating",
    )
    review_parser.add_argument(
        "--context", "-c",
        action="append",
        dest="review_contexts",
        help="Additional context signals (e.g., -c debug -c feature)",
    )

    return parser


def _handle_agent_command(args: argparse.Namespace) -> int:
    if args.agent_command == "list":
        _print(core.list_agents())
        return 0
    if args.agent_command == "status":
        _print(core.agent_status())
        return 0
    if args.agent_command == "activate":
        messages = []
        final_exit_code = 0
        changed = False
        for agent in args.agents:
            exit_code, message = core.agent_activate(agent)
            messages.append(message)
            if exit_code == 0:
                changed = True
            else:
                final_exit_code = exit_code
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return final_exit_code
    if args.agent_command == "deactivate":
        messages = []
        final_exit_code = 0
        changed = False
        for agent in args.agents:
            exit_code, message = core.agent_deactivate(agent, force=args.force)
            messages.append(message)
            if exit_code == 0:
                changed = True
            else:
                final_exit_code = exit_code
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return final_exit_code
    if args.agent_command == "deps":
        exit_code, message = core.agent_deps(args.agent)
        _print(message)
        return exit_code
    if args.agent_command == "graph":
        exit_code, message = core.agent_graph(export_path=args.export)
        _print(message)
        return exit_code
    if args.agent_command == "validate":
        exit_code, message = core.agent_validate(
            *args.agents, include_all=getattr(args, "include_all", False)
        )
        _print(message)
        return exit_code
    return 1


def _handle_rules_command(args: argparse.Namespace) -> int:
    if args.rules_command == "list":
        _print(core.list_rules())
        return 0
    if args.rules_command == "status":
        _print(core.rules_status())
        return 0
    if args.rules_command == "activate":
        messages = []
        changed = False
        for rule in args.rules:
            message = core.rules_activate(rule)
            messages.append(message)
            if _message_indicates_change(message):
                changed = True
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return 0
    if args.rules_command == "deactivate":
        messages = []
        changed = False
        for rule in args.rules:
            message = core.rules_deactivate(rule)
            messages.append(message)
            if _message_indicates_change(message):
                changed = True
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return 0
    return 1


def _handle_hooks_command(args: argparse.Namespace) -> int:
    if args.hooks_command == "validate":
        path = getattr(args, "path", None)
        if path is None:
            plugin_root = getattr(args, "plugin_root", None) or core._resolve_plugin_assets_root()
            path = plugin_root / "hooks" / "hooks.json"
        if not path.exists():
            _print(f"Hooks config not found: {path}")
            return 1
        is_valid, errors = core.validate_hooks_config_file(path)
        if is_valid:
            _print(f"Hooks config OK: {path}")
            return 0
        for error in errors:
            _print(error)
        return 1
    _print("Hooks command required. Use 'cortex hooks --help' for options.")
    return 1


def _handle_skills_command(args: argparse.Namespace) -> int:
    if args.skills_command == "list":
        _print(core.list_skills())
        return 0
    if args.skills_command == "info":
        exit_code, message = core.skill_info(args.skill)
        _print(message)
        return exit_code
    if args.skills_command == "validate":
        targets = list(getattr(args, "skills", []) or [])
        if getattr(args, "validate_all", False):
            targets.insert(0, "--all")
        exit_code, message = core.skill_validate(*targets)
        _print(message)
        return exit_code
    if args.skills_command == "analyze":
        text = getattr(args, "text", "")
        exit_code, message = core.skill_analyze(text)
        _print(message)
        return exit_code
    if args.skills_command == "suggest":
        project_dir = getattr(args, "suggest_project_dir", ".")
        exit_code, message = core.skill_suggest(project_dir)
        _print(message)
        return exit_code
    if args.skills_command == "metrics":
        if getattr(args, "metrics_reset", False):
            exit_code, message = core.skill_metrics_reset()
            _print(message)
            return exit_code
        skill_name = getattr(args, "skill", None)
        exit_code, message = core.skill_metrics(skill_name)
        _print(message)
        return exit_code
    if args.skills_command == "deps":
        exit_code, message = core.skill_deps(args.skill)
        _print(message)
        return exit_code
    if args.skills_command == "agents":
        exit_code, message = core.skill_agents(args.skill)
        _print(message)
        return exit_code
    if args.skills_command == "compose":
        exit_code, message = core.skill_compose(args.skill)
        _print(message)
        return exit_code
    if args.skills_command == "versions":
        exit_code, message = core.skill_versions(args.skill)
        _print(message)
        return exit_code
    if args.skills_command == "analytics":
        metric = getattr(args, "analytics_metric", None)
        exit_code, message = core.skill_analytics(metric)
        _print(message)
        return exit_code
    if args.skills_command == "report":
        format = getattr(args, "report_format", "text")
        exit_code, message = core.skill_report(format)
        _print(message)
        return exit_code
    if args.skills_command == "trending":
        days = getattr(args, "trending_days", 30)
        exit_code, message = core.skill_trending(days)
        _print(message)
        return exit_code
    if args.skills_command == "recommend":
        exit_code, message = core.skill_recommend()
        _print(message)
        return exit_code
    if args.skills_command == "feedback":
        skill = cast(str, args.skill)
        rating = cast(str, args.rating)
        comment = getattr(args, "feedback_comment", None)
        exit_code, message = core.skill_feedback(skill, rating, comment)
        _print(message)
        return exit_code
    if args.skills_command == "rate":
        skill = cast(str, args.skill)
        stars = cast(int, args.stars)
        helpful = not getattr(args, "not_helpful", False)
        task_succeeded = not getattr(args, "task_failed", False)
        review = getattr(args, "review", None)
        exit_code, message = core.skill_rate(
            skill, stars, helpful, task_succeeded, review
        )
        _print(message)
        return exit_code
    if args.skills_command == "ratings":
        skill = cast(str, args.skill)
        exit_code, message = core.skill_ratings(skill)
        _print(message)
        return exit_code
    if args.skills_command == "top-rated":
        category = getattr(args, "top_rated_category", None)
        limit = getattr(args, "top_rated_limit", 10)
        exit_code, message = core.skill_top_rated(category, limit)
        _print(message)
        return exit_code
    if args.skills_command == "export-ratings":
        skill = cast(str, args.export_skill)
        format = getattr(args, "export_format", "json")
        exit_code, message = core.skill_ratings_export(skill, format)
        _print(message)
        return exit_code
    if args.skills_command == "community":
        community_command = getattr(args, "community_command", None)
        if community_command == "list":
            tags = (
                [getattr(args, "community_list_tag")]
                if getattr(args, "community_list_tag", None)
                else None
            )
            search = getattr(args, "community_list_search", None)
            verified = getattr(args, "community_list_verified", False)
            sort_by = getattr(args, "community_list_sort", "name")
            exit_code, message = core.skill_community_list(
                tags=tags, search=search, verified=verified, sort_by=sort_by
            )
            _print(message)
            return exit_code
        if community_command == "install":
            skill = cast(str, args.skill)
            exit_code, message = core.skill_community_install(skill)
            _print(message)
            return exit_code
        if community_command == "validate":
            skill = cast(str, args.skill)
            exit_code, message = core.skill_community_validate(skill)
            _print(message)
            return exit_code
        if community_command == "rate":
            skill = cast(str, args.skill)
            community_rating = cast(int, args.community_rating)
            exit_code, message = core.skill_community_rate(
                skill, community_rating
            )
            _print(message)
            return exit_code
        if community_command == "search":
            query = cast(str, args.query)
            tags = getattr(args, "community_search_tags", None)
            exit_code, message = core.skill_community_search(query, tags=tags)
            _print(message)
            return exit_code
    return 1


def _handle_mcp_command(args: argparse.Namespace) -> int:
    if args.mcp_command == "list":
        exit_code, message = core.mcp_list()
        _print(message)
        return exit_code
    if args.mcp_command == "list-docs":
        _print(core.mcp_list_docs())
        return 0
    if args.mcp_command == "status":
        _print(core.mcp_docs_status())
        return 0
    if args.mcp_command == "activate":
        messages = []
        final_exit_code = 0
        changed = False
        for doc in args.docs:
            exit_code, message = core.mcp_activate(doc)
            messages.append(message)
            if exit_code == 0:
                changed = True
            else:
                final_exit_code = exit_code
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return final_exit_code
    if args.mcp_command == "deactivate":
        messages = []
        final_exit_code = 0
        changed = False
        for doc in args.docs:
            exit_code, message = core.mcp_deactivate(doc)
            messages.append(message)
            if exit_code == 0:
                changed = True
            else:
                final_exit_code = exit_code
        _print("\n".join(messages))
        if changed:
            _print(_restart_notice())
        return final_exit_code
    if args.mcp_command == "show":
        exit_code, message = core.mcp_show(args.server)
        _print(message)
        return exit_code
    if args.mcp_command == "docs":
        exit_code, message = core.mcp_docs(args.server)
        _print(message)
        return exit_code
    if args.mcp_command == "test":
        exit_code, message = core.mcp_test(args.server)
        _print(message)
        return exit_code
    if args.mcp_command == "diagnose":
        exit_code, message = core.mcp_diagnose()
        _print(message)
        return exit_code
    if args.mcp_command == "snippet":
        exit_code, message = core.mcp_snippet(args.server)
        _print(message)
        return exit_code
    return 1


def _handle_init_command(args: argparse.Namespace) -> int:
    init_command = getattr(args, "init_command", None)
    if init_command == "detect":
        exit_code, message = core.init_detect(
            getattr(args, "path", None),
            cwd=Path.cwd(),
        )
        if message:
            _print(message)
        return exit_code
    if init_command == "minimal":
        exit_code, message = core.init_minimal()
        if message:
            _print(message)
        if exit_code == 0:
            _print(_restart_notice())
        return exit_code
    if init_command == "profile":
        exit_code, message = core.init_profile(getattr(args, "name", None))
        if message:
            _print(message)
        if exit_code == 0:
            _print(_restart_notice())
        return exit_code
    if init_command == "status":
        exit_code, output, warnings = core.init_status(
            getattr(args, "target", None),
            json_output=getattr(args, "json", False),
            cwd=Path.cwd(),
        )
        if warnings:
            if not warnings.endswith("\n"):
                warnings = warnings + "\n"
            sys.stderr.write(warnings)
        if output:
            if getattr(args, "json", False):
                sys.stdout.write(output)
                if not output.endswith("\n"):
                    sys.stdout.write("\n")
            else:
                _print(output)
        return exit_code
    if init_command == "reset":
        exit_code, message = core.init_reset(
            getattr(args, "target", None),
            cwd=Path.cwd(),
        )
        if message:
            _print(message)
        return exit_code
    if init_command == "resume":
        exit_code, message = core.init_resume(
            getattr(args, "target", None),
            cwd=Path.cwd(),
        )
        if message:
            _print(message)
        return exit_code
    if init_command == "wizard":
        exit_code, message = core.init_wizard(
            getattr(args, "target", None),
            cwd=Path.cwd(),
        )
        if message:
            _print(message)
        return exit_code

    if getattr(args, "init_resume_flag", False):
        exit_code, message = core.init_resume(cwd=Path.cwd())
    else:
        exit_code, message = core.init_wizard(cwd=Path.cwd())
    if message:
        _print(message)
    if exit_code == 0:
        _print(_restart_notice())
    return exit_code


def _handle_worktree_command(args: argparse.Namespace) -> int:
    if args.worktree_command == "list":
        exit_code, message = core.worktree_list()
        _print(message)
        return exit_code
    if args.worktree_command == "add":
        exit_code, message = core.worktree_add(
            args.branch,
            path=getattr(args, "worktree_path", None),
            base=getattr(args, "worktree_base", None),
            force=getattr(args, "force", False),
            ensure_gitignore=getattr(args, "worktree_gitignore", True),
        )
        _print(message)
        return exit_code
    if args.worktree_command == "remove":
        exit_code, message = core.worktree_remove(
            args.target,
            force=getattr(args, "force", False),
        )
        _print(message)
        return exit_code
    if args.worktree_command == "prune":
        exit_code, message = core.worktree_prune(
            dry_run=getattr(args, "worktree_dry_run", False),
            verbose=getattr(args, "worktree_verbose", False),
        )
        _print(message)
        return exit_code
    if args.worktree_command == "dir":
        if getattr(args, "clear", False):
            exit_code, message = core.worktree_clear_base_dir()
            _print(message)
            return exit_code
        path = getattr(args, "path", None)
        if path:
            exit_code, message = core.worktree_set_base_dir(path)
            _print(message)
            return exit_code

        base_dir, source, error = core.worktree_get_base_dir()
        if error:
            _print(error)
            return 1
        if base_dir:
            _print(f"{base_dir} ({source})")
            return 0
        _print("No worktree base directory configured")
        return 0
    return 1


def _handle_ai_command(args: argparse.Namespace) -> int:
    from . import cmd_ai

    if args.ai_command == "recommend":
        return cmd_ai.ai_recommend()
    elif args.ai_command == "auto-activate":
        return cmd_ai.ai_auto_activate()
    elif args.ai_command == "export":
        return cmd_ai.ai_export_json(args.output)
    elif args.ai_command == "record-success":
        return cmd_ai.ai_record_success(args.outcome)
    elif args.ai_command == "watch":
        from . import watch

        if args.status and args.stop:
            _print("Choose either --status or --stop.")
            return 1
        if (args.status or args.stop) and args.daemon:
            _print("Use --status/--stop without --daemon.")
            return 1
        if args.status:
            exit_code, message = watch.watch_daemon_status()
            _print(message)
            return exit_code
        if args.stop:
            exit_code, message = watch.stop_watch_daemon()
            _print(message)
            return exit_code

        defaults = watch.load_watch_defaults()
        for warning in defaults.warnings:
            _print(f"Config warning: {warning}")

        watch_dirs: List[Path] = []
        for entry in getattr(args, "watch_dirs", []) or []:
            for raw in entry.split(","):
                cleaned = raw.strip()
                if not cleaned:
                    continue
                watch_dirs.append(Path(os.path.expanduser(cleaned)))

        if watch_dirs:
            invalid = [p for p in watch_dirs if not p.exists() or not p.is_dir()]
            if invalid:
                _print("Invalid watch directory(s):")
                for path in invalid:
                    _print(f"  - {path}")
                return 1

        if args.no_auto_activate is True:
            auto_activate = False
        elif defaults.auto_activate is not None:
            auto_activate = defaults.auto_activate
        else:
            auto_activate = True

        threshold = (
            args.threshold
            if args.threshold is not None
            else (defaults.threshold if defaults.threshold is not None else 0.7)
        )
        interval = (
            args.interval
            if args.interval is not None
            else (defaults.interval if defaults.interval is not None else 2.0)
        )
        directories = watch_dirs or defaults.directories

        if args.daemon:
            log_path = None
            if args.watch_log:
                log_path = Path(os.path.expanduser(args.watch_log)).resolve()
            exit_code, message = watch.start_watch_daemon(
                auto_activate=auto_activate,
                threshold=threshold,
                interval=interval,
                directories=directories,
                log_path=log_path,
            )
            _print(message)
            return exit_code

        return watch.watch_main(
            auto_activate=auto_activate,
            threshold=threshold,
            interval=interval,
            directories=directories,
        )
    else:
        _print("AI command required. Use 'cortex ai --help' for options.")
        return 1


def _handle_export_command(args: argparse.Namespace) -> int:
    if args.export_command == "list":
        _print(core.list_context_components())
        return 0
    if args.export_command == "context":
        from pathlib import Path

        # Support "-" for stdout
        output_path: Path | str
        if args.output == "-":
            output_path = "-"
        else:
            output_path = Path(args.output)

        exclude_categories = set(args.exclude_categories or [])
        include_categories = set(args.include_categories or [])
        exclude_files = set(args.exclude_files or [])
        agent_generic = not args.no_agent_generic

        exit_code, message = core.export_context(
            output_path=output_path,
            exclude_categories=exclude_categories,
            include_categories=include_categories,
            exclude_files=exclude_files,
            agent_generic=agent_generic,
        )
        if message:  # Only print if there's a message (empty for stdout)
            _print(message)
        return exit_code
    return 1


def _handle_completion_command(args: argparse.Namespace) -> int:
    from . import completions

    try:
        if args.install:
            # Show installation instructions
            instructions = completions.get_installation_instructions(args.shell)
            _print(instructions)
        else:
            # Generate completion script
            script = completions.get_completion_script(args.shell)
            _print(script)
        return 0
    except ValueError as e:
        _print(f"Error: {e}")
        return 1


def _handle_install_command(args: argparse.Namespace) -> int:
    if args.install_command == "aliases":
        from . import shell_integration

        # Show aliases without installing
        if args.show:
            _print(shell_integration.show_aliases())
            return 0

        # Uninstall aliases
        if args.uninstall:
            exit_code, message = shell_integration.uninstall_aliases(
                shell=args.shell, rc_file=args.rc_file, dry_run=args.dry_run
            )
            _print(message)
            return exit_code

        # Install aliases
        exit_code, message = shell_integration.install_aliases(
            shell=args.shell,
            rc_file=args.rc_file,
            force=args.force,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "completions":
        from . import installer

        exit_code, message = installer.install_completions(
            shell=args.shell,
            target_path=args.completion_path,
            system=args.system,
            force=args.force,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "manpage":
        from . import installer

        exit_code, message = installer.install_manpages(
            target_dir=args.manpath,
            system=args.system,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "docs":
        from . import installer

        exit_code, message = installer.install_docs(
            target_dir=args.docs_target,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "bootstrap":
        from . import installer

        exit_code, message = installer.bootstrap(
            target_dir=args.bootstrap_target,
            force=args.force,
            dry_run=args.dry_run,
            link_rules=args.link_rules,
        )
        _print(message)
        return exit_code
    if args.install_command == "rules":
        from .core.base import _resolve_plugin_assets_root
        from .core.rules import sync_rule_symlinks, DEFAULT_RULES_SUBDIR

        plugin_root = _resolve_plugin_assets_root()
        if plugin_root is None:
            _print("Unable to resolve plugin root.")
            return 1

        if args.clean:
            # Remove all symlinks in target
            if DEFAULT_RULES_SUBDIR.exists():
                removed = 0
                for link in DEFAULT_RULES_SUBDIR.glob("*.md"):
                    if link.is_symlink():
                        if args.dry_run:
                            _print(f"Would remove: {link.name}")
                        else:
                            link.unlink()
                            _print(f"Removed: {link.name}")
                        removed += 1
                if removed == 0:
                    _print("No cortex rule symlinks found.")
            else:
                _print(f"Rules directory does not exist: {DEFAULT_RULES_SUBDIR}")
            return 0

        # Auto-discover all rules from rules/ directory
        rules_source = plugin_root / "rules"
        if not rules_source.is_dir():
            _print(f"Rules directory not found: {rules_source}")
            return 1

        all_rules = [p.stem for p in sorted(rules_source.glob("*.md"))]
        if not all_rules:
            _print("No rule files found.")
            return 0

        if args.dry_run:
            _print(f"Would link {len(all_rules)} rules to {DEFAULT_RULES_SUBDIR}:")
            for rule in all_rules:
                _print(f"  - {rule}.md")
            return 0

        _, messages = sync_rule_symlinks(
            rules_root=plugin_root,
            active_rules=all_rules,
            target_dir=DEFAULT_RULES_SUBDIR,
        )
        for msg in messages:
            _print(msg)
        _print(f"✓ Synced {len(all_rules)} rules to {DEFAULT_RULES_SUBDIR}")
        return 0
    if args.install_command == "post":
        from . import installer

        exit_code, message = installer.install_post(
            shell=args.shell,
            completion_path=args.completion_path,
            manpath=args.manpath,
            docs_target=args.docs_target,
            system=args.system,
            force=args.force,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "package":
        from . import installer

        path = args.path
        if path is None and args.editable:
            path = Path(".")
        exit_code, message = installer.install_package(
            manager=args.manager,
            path=path,
            name=args.name,
            editable=args.editable,
            dev=args.dev,
            upgrade=args.upgrade,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    else:
        _print("Install subcommand required. Use 'cortex install --help'")
        return 1


def _handle_dashboard_command(args: argparse.Namespace) -> int:
    from . import cmd_dashboard
    return cmd_dashboard.dashboard()


def _handle_review_command(args: argparse.Namespace) -> int:
    from . import cmd_review
    return cmd_review.main(
        dry_run=getattr(args, "dry_run", False),
        extra_context=getattr(args, "review_contexts", None),
    )


def _handle_docs_command(args: argparse.Namespace) -> int:
    from . import cmd_docs

    if args.page:
        exit_code, message = cmd_docs.view_doc(args.page)
    else:
        exit_code, message = cmd_docs.list_docs()
    
    if message:
        _print(message)
    return exit_code


def _handle_statusline_command(args: argparse.Namespace) -> int:
    from . import statusline

    return statusline.render_statusline(args)


def _build_memory_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Build the memory command parser for persistent knowledge capture."""
    memory_parser = subparsers.add_parser(
        "memory", help="Memory capture commands for persistent knowledge storage"
    )
    memory_sub = memory_parser.add_subparsers(dest="memory_command")

    # remember - Quick knowledge capture
    remember_parser = memory_sub.add_parser(
        "remember", help="Quick capture of domain knowledge"
    )
    remember_parser.add_argument("text", help="Knowledge text to capture")
    remember_parser.add_argument(
        "--topic", dest="remember_topic", help="Explicit topic name"
    )
    remember_parser.add_argument(
        "--tags",
        dest="remember_tags",
        help="Comma-separated additional tags",
    )

    # project - Project context capture
    project_parser = memory_sub.add_parser(
        "project", help="Capture or update project context"
    )
    project_parser.add_argument("name", help="Project name")
    project_parser.add_argument(
        "--path", dest="project_path", help="Repository path"
    )
    project_parser.add_argument(
        "--purpose", dest="project_purpose", help="One-line description"
    )
    project_parser.add_argument(
        "--related",
        dest="project_related",
        help="Comma-separated related project names",
    )
    project_parser.add_argument(
        "--update",
        dest="project_update",
        action="store_true",
        help="Update mode (prompts for which sections)",
    )

    # capture - Session summary
    capture_parser = memory_sub.add_parser(
        "capture", help="Capture session summary"
    )
    capture_parser.add_argument(
        "title", nargs="?", help="Session title (optional)"
    )
    capture_parser.add_argument(
        "--summary", dest="capture_summary", help="What we worked on"
    )
    capture_parser.add_argument(
        "--decisions",
        dest="capture_decisions",
        help="Pipe-separated decisions made",
    )
    capture_parser.add_argument(
        "--implementations",
        dest="capture_implementations",
        help="Pipe-separated implementations",
    )
    capture_parser.add_argument(
        "--open",
        dest="capture_open",
        help="Pipe-separated open items",
    )
    capture_parser.add_argument(
        "--project", dest="capture_project", help="Related project name"
    )
    capture_parser.add_argument(
        "--quick",
        dest="capture_quick",
        action="store_true",
        help="Minimal prompts (summary only)",
    )

    # fix - Bug fix documentation
    fix_parser = memory_sub.add_parser("fix", help="Record a bug fix")
    fix_parser.add_argument("title", help="Issue title")
    fix_parser.add_argument(
        "--problem", dest="fix_problem", help="What was broken/wrong"
    )
    fix_parser.add_argument(
        "--cause", dest="fix_cause", help="Root cause"
    )
    fix_parser.add_argument(
        "--solution", dest="fix_solution", help="How we fixed it"
    )
    fix_parser.add_argument(
        "--files",
        dest="fix_files",
        help="Comma-separated changed file paths",
    )
    fix_parser.add_argument(
        "--project", dest="fix_project", help="Related project name"
    )

    # auto - Toggle auto-capture
    auto_parser = memory_sub.add_parser(
        "auto", help="Toggle or check auto-capture state"
    )
    auto_parser.add_argument(
        "action",
        nargs="?",
        choices=["on", "off", "status"],
        default="status",
        help="Action: on, off, or status (default: status)",
    )

    # list - List notes
    list_parser = memory_sub.add_parser("list", help="List notes in the vault")
    list_parser.add_argument(
        "note_type",
        nargs="?",
        choices=["knowledge", "projects", "sessions", "fixes"],
        help="Filter by note type",
    )
    list_parser.add_argument(
        "--recent",
        dest="list_recent",
        type=int,
        help="Limit to N most recent notes",
    )
    list_parser.add_argument(
        "--tags",
        dest="list_tags",
        help="Comma-separated tags to filter by",
    )

    # search - Search notes
    search_parser = memory_sub.add_parser("search", help="Search notes by content")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--type",
        dest="search_type",
        choices=["knowledge", "projects", "sessions", "fixes"],
        help="Filter by note type",
    )
    search_parser.add_argument(
        "--limit",
        dest="search_limit",
        type=int,
        help="Maximum number of results",
    )

    # stats - Show vault statistics
    memory_sub.add_parser("stats", help="Show vault statistics")


def _build_doctor_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    doctor_parser = subparsers.add_parser(
        "doctor", help="Diagnose and fix context issues"
    )
    doctor_parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix issues"
    )


def _handle_doctor_command(args: argparse.Namespace) -> int:
    exit_code, message = core.doctor_run(fix=args.fix)
    _print(message)
    return exit_code


def _handle_setup_command(args: argparse.Namespace) -> int:
    """Handle setup/migration commands."""
    if args.setup_command == "migrate":
        exit_code, message = migrate_to_file_activation()
        _print(message)
        if _message_indicates_change(message):
            _print(_restart_notice())
        return exit_code
    if args.setup_command == "migrate-commands":
        exit_code, message = migrate_commands_layout(
            dry_run=getattr(args, "dry_run", False),
            force=getattr(args, "force", False),
        )
        _print(message)
        return exit_code
    return 1


def _handle_memory_command(args: argparse.Namespace) -> int:
    """Handle memory subcommands for persistent knowledge capture."""
    from . import memory

    if args.memory_command == "remember":
        tags = None
        if getattr(args, "remember_tags", None):
            tags = [t.strip() for t in args.remember_tags.split(",")]
        exit_code, message = memory.memory_remember(
            text=args.text,
            topic=getattr(args, "remember_topic", None),
            tags=tags,
        )
        _print(message)
        return exit_code

    if args.memory_command == "project":
        related = None
        if getattr(args, "project_related", None):
            related = [r.strip() for r in args.project_related.split(",")]
        exit_code, message = memory.memory_project(
            name=args.name,
            path=getattr(args, "project_path", None),
            purpose=getattr(args, "project_purpose", None),
            related=related,
            update=getattr(args, "project_update", False),
        )
        _print(message)
        return exit_code

    if args.memory_command == "capture":
        decisions = None
        if getattr(args, "capture_decisions", None):
            decisions = [d.strip() for d in args.capture_decisions.split("|")]
        implementations = None
        if getattr(args, "capture_implementations", None):
            implementations = [i.strip() for i in args.capture_implementations.split("|")]
        open_items = None
        if getattr(args, "capture_open", None):
            open_items = [o.strip() for o in args.capture_open.split("|")]
        exit_code, message = memory.memory_capture(
            title=getattr(args, "title", None),
            summary=getattr(args, "capture_summary", None),
            decisions=decisions,
            implementations=implementations,
            open_items=open_items,
            project=getattr(args, "capture_project", None),
            quick=getattr(args, "capture_quick", False),
        )
        _print(message)
        return exit_code

    if args.memory_command == "fix":
        files = None
        if getattr(args, "fix_files", None):
            files = [f.strip() for f in args.fix_files.split(",")]
        exit_code, message = memory.memory_fix(
            title=args.title,
            problem=getattr(args, "fix_problem", None),
            cause=getattr(args, "fix_cause", None),
            solution=getattr(args, "fix_solution", None),
            files=files,
            project=getattr(args, "fix_project", None),
        )
        _print(message)
        return exit_code

    if args.memory_command == "auto":
        exit_code, message = memory.memory_auto(
            action=getattr(args, "action", "status"),
        )
        _print(message)
        return exit_code

    if args.memory_command == "list":
        tags = None
        if getattr(args, "list_tags", None):
            tags = [t.strip() for t in args.list_tags.split(",")]
        exit_code, message = memory.memory_list(
            note_type=getattr(args, "note_type", None),
            recent=getattr(args, "list_recent", None),
            tags=tags,
        )
        _print(message)
        return exit_code

    if args.memory_command == "search":
        exit_code, message = memory.memory_search(
            query=args.query,
            note_type=getattr(args, "search_type", None),
            limit=getattr(args, "search_limit", None),
        )
        _print(message)
        return exit_code

    if args.memory_command == "stats":
        stats = memory.get_vault_stats()
        lines = [
            f"Vault: {stats['vault_path']}",
            f"Exists: {'yes' if stats['exists'] else 'no'}",
            "",
            "Note counts:",
        ]
        for note_type, count in stats["types"].items():
            lines.append(f"  {note_type}: {count}")
        lines.append(f"  total: {stats['total']}")
        _print("\n".join(lines))
        return 0

    _print("Memory command required. Use 'cortex memory --help' for options.")
    return 1


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    _enable_argcomplete(parser)
    args, extra_args = parser.parse_known_args(list(argv) if argv is not None else None)

    if getattr(args, "plugin_root", None):
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(args.plugin_root)
    if getattr(args, "scope", None):
        os.environ["CORTEX_SCOPE"] = str(args.scope)

    # Run first-run wizard if needed (before any command processing)
    skip_wizard = getattr(args, "skip_wizard", False)
    if not skip_wizard:
        from .wizard import should_run_wizard, run_wizard

        if should_run_wizard():
            exit_code, _ = run_wizard()
            if exit_code != 0:
                return exit_code
            # Continue to execute the requested command after wizard

    handlers: Dict[str, Callable[[argparse.Namespace], int]] = {
        "agent": _handle_agent_command,
        "rules": _handle_rules_command,
        "hooks": _handle_hooks_command,
        "skills": _handle_skills_command,
        "mcp": _handle_mcp_command,
        "init": _handle_init_command,
        "worktree": _handle_worktree_command,
        "ai": _handle_ai_command,
        "export": _handle_export_command,
        "completion": _handle_completion_command,
        "install": _handle_install_command,
        "docs": _handle_docs_command,
        "statusline": _handle_statusline_command,
        "doctor": _handle_doctor_command,
        "memory": _handle_memory_command,
        "setup": _handle_setup_command,
        "dashboard": _handle_dashboard_command,
        "review": _handle_review_command,
    }

    if args.command == "status":
        _print(core.show_status())
        return 0

    if args.command == "tui":
        from .tui.main import main as tui_main
        return tui_main(
            theme_path=getattr(args, "theme", None),
            start_tour=getattr(args, "tour", False),
            start_view=getattr(args, "view", None),
        )

    if extra_args:
        parser.error(f"unrecognized arguments: {' '.join(extra_args)}")

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
