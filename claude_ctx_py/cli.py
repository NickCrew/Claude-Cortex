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
    agent_sub.add_parser(
        "rebuild-index",
        help="Regenerate agents/agent-index.json from agent front matter",
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

    rules_edit = rules_sub.add_parser(
        "edit", help="Open rule file(s) in $EDITOR"
    )
    rules_edit.add_argument("rules", nargs="+", help="Rule name(s) (without .md)")


def _build_completions_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Top-level ``cortex completions <shell>`` that prints the script to stdout.

    Kept separate from ``cortex install completions`` (which writes to a file
    in the user's shell config) because Homebrew's
    ``generate_completions_from_executable`` helper captures stdout at build
    time. The two share the same backing generator in ``claude_ctx_py.completions``.
    """
    completions_parser = subparsers.add_parser(
        "completions",
        help="Print shell completion script to stdout",
    )
    completions_parser.add_argument(
        "shell",
        choices=["bash", "zsh", "fish"],
        help="Target shell",
    )


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
    from .hooks import HOOK_SUBCOMMANDS

    for _hook_name, _hook_meta in HOOK_SUBCOMMANDS.items():
        hooks_sub.add_parser(_hook_name, help=_hook_meta["help"])

    hooks_install = hooks_sub.add_parser(
        "install",
        help="Register a cortex hook subcommand in ~/.claude/settings.json",
    )
    hooks_install.add_argument(
        "name",
        choices=sorted(HOOK_SUBCOMMANDS.keys()),
        help="Hook subcommand to install",
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
    skills_sub.add_parser(
        "rebuild-index",
        help="Regenerate skills/skill-index.json from SKILL.md front matter",
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
    skills_context_parser = skills_sub.add_parser(
        "context", help="Generate skill context for current session"
    )
    skills_context_parser.add_argument(
        "--no-write", action="store_true",
        help="Print to stdout only, skip writing .claude/skill-context.md"
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

    # audit - Quality audit for skills
    skills_audit_parser = skills_sub.add_parser(
        "audit", help="Audit skill quality and completeness"
    )
    skills_audit_parser.add_argument("skill", help="Skill name to audit")
    skills_audit_parser.add_argument(
        "--quick", action="store_true", help="Run quick audit (skip detailed checks)"
    )
    skills_audit_parser.add_argument(
        "--full", action="store_true", help="Run full comprehensive audit"
    )
    skills_audit_parser.add_argument(
        "--output", "-o", type=Path, help="Output report to file"
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
    ai_ingest = ai_sub.add_parser(
        "ingest-review", help="Ingest specialist review into skill learning"
    )
    ai_ingest.add_argument("file", help="Path to review markdown file")
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
        help="Log file for daemon mode (default: ~/.claude/logs/watch.log)",
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


def _build_suggest_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    suggest_parser = subparsers.add_parser(
        "suggest",
        help="Unified skill and agent suggestions for the current context",
    )

    # Filter mode
    suggest_parser.add_argument(
        "--skills",
        action="store_true",
        help="Show skill recommendations only",
    )
    suggest_parser.add_argument(
        "--agents",
        action="store_true",
        help="Show agent recommendations only",
    )
    suggest_parser.add_argument(
        "--activate",
        action="store_true",
        help="Auto-activate high-confidence matches",
    )
    suggest_parser.add_argument(
        "--text",
        dest="suggest_text",
        metavar="TEXT",
        help="Analyze text for skill matches",
    )
    suggest_parser.add_argument(
        "--project-dir",
        dest="suggest_project_dir",
        default=".",
        help="Project directory to analyze (default: current directory)",
    )

    # Watch mode
    suggest_parser.add_argument(
        "--watch",
        action="store_true",
        help="Real-time monitoring mode",
    )
    suggest_parser.add_argument(
        "--no-auto-activate",
        dest="no_auto_activate",
        action="store_true",
        default=None,
        help="Disable auto-activation in watch mode",
    )
    suggest_parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run watch mode in background as daemon",
    )
    suggest_parser.add_argument(
        "--status",
        action="store_true",
        help="Show watch daemon status",
    )
    suggest_parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop the watch daemon",
    )
    suggest_parser.add_argument(
        "--log",
        dest="watch_log",
        help="Log file for daemon mode",
    )
    suggest_parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Confidence threshold (0.0-1.0)",
    )
    suggest_parser.add_argument(
        "--interval",
        type=float,
        default=None,
        help="Check interval in seconds for watch mode",
    )
    suggest_parser.add_argument(
        "--dir",
        dest="watch_dirs",
        action="append",
        default=[],
        help="Directory to watch (repeatable or comma-separated)",
    )

    # Export
    suggest_parser.add_argument(
        "--export",
        dest="export_file",
        metavar="FILE",
        nargs="?",
        const="suggestions.json",
        help="Export suggestions to JSON file (default: suggestions.json)",
    )

    # Review gate
    suggest_parser.add_argument(
        "--review",
        action="store_true",
        help="Pre-completion review gate (suggest skills based on git context)",
    )
    suggest_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without activating",
    )
    suggest_parser.add_argument(
        "--context", "-c",
        action="append",
        dest="review_contexts",
        help="Additional context signals for review mode",
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
    export_agents = export_sub.add_parser(
        "agents", help="Export selected agent definitions"
    )
    export_agents.add_argument(
        "agents",
        nargs="+",
        help="Agent name(s) to export (without .md)",
    )
    export_agents.add_argument(
        "--output",
        default="-",
        help="Output file path or '-' for stdout (default: stdout)",
    )
    export_agents.add_argument(
        "--no-agent-generic",
        dest="no_agent_generic",
        action="store_true",
        help="Use Claude-specific format instead of agent-generic",
    )


def _build_install_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    install_parser = subparsers.add_parser(
        "install", help="Install CLI integrations and optional extras"
    )
    install_sub = install_parser.add_subparsers(dest="install_command")

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

    # Link bundled content into ~/.claude
    link_parser = install_sub.add_parser(
        "link", help="Symlink bundled content (agents, skills, rules, schemas) into ~/.claude"
    )
    link_parser.add_argument(
        "--source",
        dest="link_source",
        type=Path,
        help="Source directory (default: auto-detect plugin root)",
    )
    link_parser.add_argument(
        "--target",
        dest="link_target",
        type=Path,
        help="Target directory (default: ~/.claude)",
    )
    link_parser.add_argument(
        "--force", action="store_true", help="Replace existing directories/symlinks"
    )
    link_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    # Configure statusline
    statusline_parser = install_sub.add_parser(
        "statusline", help="Configure Claude Code statusline to use cortex"
    )
    statusline_parser.add_argument(
        "--command",
        default="cortex statusline --color",
        help="Statusline command to use (default: cortex statusline --color)",
    )
    statusline_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing statusline configuration"
    )


def _build_statusline_parser(
    subparsers: argparse._SubParsersAction[Any],
) -> None:
    from . import statusline

    statusline_parser = subparsers.add_parser(
        "statusline", help="Render Claude Code status line"
    )
    statusline.add_statusline_arguments(statusline_parser)


def _resolve_version() -> str:
    """Return the installed package version, or 'dev' if not installed."""
    try:
        from importlib.metadata import version as _pkg_version
        return _pkg_version("claude-cortex")
    except Exception:
        return "dev"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cortex",
        description="Python implementation of cortex list and status commands",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"cortex {_resolve_version()}",
    )
    parser.add_argument(
        "--scope",
        choices=["auto", "project", "global"],
        help="Select which scope to use (default: auto)",
    )
    parser.add_argument(
        "--cortex-root",
        "--plugin-root",  # Deprecated alias for backward compatibility
        dest="cortex_root",
        type=Path,
        help="Explicit path to the cortex package root (for development)",
    )
    parser.add_argument(
        "--skip-wizard",
        "--no-init",
        dest="skip_wizard",
        action="store_true",
        help="Skip the first-run wizard even if content is not linked to ~/.claude",
    )
    subparsers = parser.add_subparsers(dest="command")

    _build_agent_parser(subparsers)
    _build_rules_parser(subparsers)
    _build_hooks_parser(subparsers)
    _build_skills_parser(subparsers)
    _build_completions_parser(subparsers)
    _build_mcp_parser(subparsers)
    _build_worktree_parser(subparsers)
    from .cmd_git import build_git_parser
    build_git_parser(subparsers)
    from .cmd_tmux import build_tmux_parser
    build_tmux_parser(subparsers)
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
    _build_suggest_parser(subparsers)
    _build_export_parser(subparsers)
    _build_install_parser(subparsers)
    _build_memory_parser(subparsers)
    _build_plan_parser(subparsers)
    _build_docs_parser(subparsers)
    _build_dev_parser(subparsers)
    _build_file_parser(subparsers)
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall cortex")
    uninstall_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )
    uninstall_parser.add_argument(
        "--keep-config",
        action="store_true",
        help="Keep configuration files in ~/.claude/",
    )
    status_parser = subparsers.add_parser("status", help="Show overall status")
    status_parser.add_argument(
        "--rich",
        action="store_true",
        help="Use Rich markup instead of ANSI colors",
    )
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
    if args.agent_command == "rebuild-index":
        from . import agent_index
        exit_code, message = agent_index.rebuild_index()
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
    if args.rules_command == "edit":
        import subprocess

        editor = os.environ.get("EDITOR", "vim")
        rules_dir = Path.home() / ".claude" / "rules"

        # Collect rule paths
        rule_paths = []
        missing = []
        for rule_name in args.rules:
            # Try direct file first
            rule_file = rules_dir / f"{rule_name}.md"
            if rule_file.exists():
                rule_paths.append(rule_file)
            # Try cortex subdirectory
            elif (rules_dir / "cortex" / f"{rule_name}.md").exists():
                rule_paths.append(rules_dir / "cortex" / f"{rule_name}.md")
            else:
                missing.append(rule_name)

        if missing:
            _print(f"Rule(s) not found: {', '.join(missing)}")
            if not rule_paths:
                return 1

        if rule_paths:
            try:
                subprocess.run([editor] + [str(p) for p in rule_paths])
                return 0
            except FileNotFoundError:
                _print(f"Editor not found: {editor}")
                _print("Set $EDITOR environment variable to your preferred editor")
                return 1
            except Exception as e:
                _print(f"Failed to open editor: {e}")
                return 1

        return 1
    return 1


def _handle_completions_command(args: argparse.Namespace) -> int:
    from . import completions
    sys.stdout.write(completions.get_completion_script(args.shell))
    return 0


def _handle_hooks_command(args: argparse.Namespace) -> int:
    if args.hooks_command == "validate":
        path = getattr(args, "path", None)
        if path is None:
            cortex_root = getattr(args, "cortex_root", None) or core._resolve_cortex_root()
            path = cortex_root / "hooks" / "hooks.json"
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
    from .hooks import HOOK_SUBCOMMANDS, install_hook_command

    if args.hooks_command in HOOK_SUBCOMMANDS:
        if args.hooks_command == "skill-suggest":
            from .hooks.skill_suggest import run
        elif args.hooks_command == "agent-suggest":
            from .hooks.agent_suggest import run
        elif args.hooks_command == "large-file-gate":
            from .hooks.large_file_gate import run
        elif args.hooks_command == "subagent-output-validator":
            from .hooks.subagent_output_validator import run
        elif args.hooks_command == "workspace-validator":
            from .hooks.workspace_validator import run
        else:
            _print(f"Unknown hook: {args.hooks_command}")
            return 1
        return run()

    if args.hooks_command == "install":
        if args.name not in HOOK_SUBCOMMANDS:
            _print(f"Unknown hook: {args.name}")
            return 1
        meta = HOOK_SUBCOMMANDS[args.name]
        ok, message = install_hook_command(
            subcommand=args.name,
            event=meta["event"],
            matcher=meta["matcher"],
        )
        _print(message)
        return 0 if ok else 1

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
        print("Note: 'cortex skills analyze' is deprecated. Use 'cortex suggest --text' instead.", file=sys.stderr)
        text = getattr(args, "text", "")
        exit_code, message = core.skill_analyze(text)
        _print(message)
        return exit_code
    if args.skills_command == "rebuild-index":
        exit_code, message = core.skill_rebuild_index()
        _print(message)
        return exit_code
    if args.skills_command == "suggest":
        print("Note: 'cortex skills suggest' is deprecated. Use 'cortex suggest' instead.", file=sys.stderr)
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
    if args.skills_command == "context":
        no_write = getattr(args, "no_write", False)
        exit_code, message = core.skill_context(write=not no_write)
        _print(message)
        return exit_code
    if args.skills_command == "recommend":
        print("Note: 'cortex skills recommend' is deprecated. Use 'cortex suggest --skills' instead.", file=sys.stderr)
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
    if args.skills_command == "audit":
        from claude_ctx_py.commands.skill_audit import audit_skill
        skill_id = cast(str, args.skill)
        show_calls = getattr(args, "show_calls", False)
        show_context = getattr(args, "show_context", False)
        show_examples = getattr(args, "show_examples", False)
        output_format = getattr(args, "output_format", "text")
        exit_code, message = audit_skill(
            skill_id,
            show_calls=show_calls,
            show_context=show_context,
            show_examples=show_examples,
            output_format=output_format,
        )
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
        print("Note: 'cortex ai recommend' is deprecated. Use 'cortex suggest' instead.", file=sys.stderr)
        return cmd_ai.ai_recommend()
    elif args.ai_command == "auto-activate":
        print("Note: 'cortex ai auto-activate' is deprecated. Use 'cortex suggest --activate' instead.", file=sys.stderr)
        return cmd_ai.ai_auto_activate()
    elif args.ai_command == "export":
        print("Note: 'cortex ai export' is deprecated. Use 'cortex suggest --export' instead.", file=sys.stderr)
        return cmd_ai.ai_export_json(args.output)
    elif args.ai_command == "record-success":
        return cmd_ai.ai_record_success(args.outcome)
    elif args.ai_command == "ingest-review":
        return cmd_ai.ai_ingest_review(args.file)
    elif args.ai_command == "watch":
        print("Note: 'cortex ai watch' is deprecated. Use 'cortex suggest --watch' instead.", file=sys.stderr)
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


def _handle_suggest_command(args: argparse.Namespace) -> int:
    from . import cmd_suggest

    # --text mode: text analysis
    if getattr(args, "suggest_text", None):
        return cmd_suggest.suggest_text(args.suggest_text)

    # --watch mode (or --status/--stop): real-time monitoring
    if getattr(args, "watch", False) or getattr(args, "status", False) or getattr(args, "stop", False):
        return cmd_suggest.suggest_watch(
            no_auto_activate=getattr(args, "no_auto_activate", False) or False,
            daemon=getattr(args, "daemon", False),
            status=getattr(args, "status", False),
            stop=getattr(args, "stop", False),
            watch_log=getattr(args, "watch_log", None),
            threshold=getattr(args, "threshold", None),
            interval=getattr(args, "interval", None),
            watch_dirs=getattr(args, "watch_dirs", None),
        )

    # --export mode: JSON export
    if getattr(args, "export_file", None):
        return cmd_suggest.suggest_export(args.export_file)

    # --review mode: pre-completion gate
    if getattr(args, "review", False):
        return cmd_suggest.suggest_review(
            dry_run=getattr(args, "dry_run", False),
            extra_context=getattr(args, "review_contexts", None),
        )

    # --activate mode: auto-activate high-confidence
    if getattr(args, "activate", False):
        return cmd_suggest.suggest_activate()

    # Default mode: context-aware combined suggestions
    return cmd_suggest.suggest_default(
        skills_only=getattr(args, "skills", False),
        agents_only=getattr(args, "agents", False),
        project_dir=getattr(args, "suggest_project_dir", "."),
    )


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
    if args.export_command == "agents":
        from pathlib import Path

        output_path: Path | str
        if args.output == "-":
            output_path = "-"
        else:
            output_path = Path(args.output)

        exit_code, message = core.export_agents(
            agent_names=list(args.agents),
            output_path=output_path,
            agent_generic=not args.no_agent_generic,
        )
        if message:
            _print(message)
        return exit_code
    return 1


def _handle_install_command(args: argparse.Namespace) -> int:
    if args.install_command == "manpage":
        from . import installer

        exit_code, message = installer.install_manpages(
            target_dir=args.manpath,
            system=args.system,
            dry_run=args.dry_run,
        )
        _print(message)
        return exit_code
    if args.install_command == "link":
        from . import installer

        exit_code, message = installer.link_content(
            source_dir=getattr(args, "link_source", None),
            target_dir=getattr(args, "link_target", None),
            force=getattr(args, "force", False),
            dry_run=getattr(args, "dry_run", False),
        )
        _print(message)
        return exit_code
    if args.install_command == "statusline":
        from .core import hooks

        exit_code, message = hooks.configure_statusline(
            command=getattr(args, "command", "cortex statusline --color"),
            force=getattr(args, "force", False),
        )
        _print(message)
        return exit_code
    else:
        _print("Install subcommand required. Use 'cortex install --help'")
        return 1


def _handle_review_command(args: argparse.Namespace) -> int:
    print("Note: 'cortex review' is deprecated. Use 'cortex suggest --review' instead.", file=sys.stderr)
    from . import cmd_review
    return cmd_review.main(
        dry_run=getattr(args, "dry_run", False),
        extra_context=getattr(args, "review_contexts", None),
    )


def _handle_git_command(args: argparse.Namespace) -> int:
    from .cmd_git import handle_git_command
    return handle_git_command(args)


def _handle_tmux_command(args: argparse.Namespace) -> int:
    from .cmd_tmux import handle_tmux_command
    return handle_tmux_command(args)


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


def _build_plan_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Build the plan command parser for viewing plan files."""
    plan_parser = subparsers.add_parser(
        "plan", help="View and manage plan files"
    )
    plan_sub = plan_parser.add_subparsers(dest="plan_command")

    # list - List all plan files
    plan_list = plan_sub.add_parser("list", help="List all plan files")
    plan_list.add_argument(
        "--limit", type=int, default=10, help="Number of recent plans to show (default: 10)"
    )
    plan_list.add_argument(
        "--all", action="store_true", help="Show all plans (no limit)"
    )

    # view - View a plan file
    plan_view = plan_sub.add_parser("view", help="View a plan file")
    plan_view.add_argument("plan", help="Plan filename (with or without .md)")
    plan_view.add_argument(
        "--raw", action="store_true", help="Show raw markdown without rendering"
    )

    # edit - Edit a plan file
    plan_edit = plan_sub.add_parser("edit", help="Edit a plan file in $EDITOR")
    plan_edit.add_argument("plan", help="Plan filename (with or without .md)")

    # path - Show the plans directory path
    plan_sub.add_parser("path", help="Show the plans directory path")


def _build_docs_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Build the docs command parser for browsing project documentation."""
    docs_parser = subparsers.add_parser(
        "docs", help="Browse documentation (includes bundled package docs)"
    )
    docs_parser.add_argument(
        "--path", type=Path, default=None,
        help="Browse docs from an arbitrary directory instead of Cortex docs"
    )
    docs_sub = docs_parser.add_subparsers(dest="docs_command")

    # list - List all documentation files
    docs_list = docs_sub.add_parser("list", help="List all documentation files")
    docs_list.add_argument(
        "--filter", help="Filter docs by path pattern (e.g., 'reference', 'archive')"
    )
    docs_list.add_argument(
        "--sort", choices=["name", "modified", "size"], default="name",
        help="Sort order (default: name)"
    )

    # tree - Show documentation folder structure
    docs_sub.add_parser("tree", help="Show documentation folder structure")

    # view - View a documentation file
    docs_view = docs_sub.add_parser("view", help="View a documentation file")
    docs_view.add_argument("path", help="Path to doc file (relative to docs/)")
    docs_view.add_argument(
        "--raw", action="store_true", help="Show raw markdown without rendering"
    )

    # search - Search documentation
    docs_search = docs_sub.add_parser("search", help="Search documentation")
    docs_search.add_argument("query", help="Search query")
    docs_search.add_argument(
        "--limit", type=int, default=20, help="Max results to show (default: 20)"
    )

    # edit - Edit a documentation file
    docs_edit = docs_sub.add_parser("edit", help="Edit a doc file in $EDITOR")
    docs_edit.add_argument("path", help="Path to doc file (relative to docs/)")

    # bookmark - Manage bookmarks
    bookmark_sub = docs_sub.add_parser("bookmark", help="Manage doc bookmarks")
    bookmark_cmds = bookmark_sub.add_subparsers(dest="bookmark_command")

    bookmark_add = bookmark_cmds.add_parser("add", help="Add a bookmark")
    bookmark_add.add_argument("path", help="Path to doc file")
    bookmark_add.add_argument("--name", help="Bookmark name (defaults to filename)")

    bookmark_cmds.add_parser("list", help="List all bookmarks")

    bookmark_remove = bookmark_cmds.add_parser("remove", help="Remove a bookmark")
    bookmark_remove.add_argument("name", help="Bookmark name to remove")

    bookmark_view = bookmark_cmds.add_parser("view", help="View a bookmarked doc")
    bookmark_view.add_argument("name", help="Bookmark name")

    # path - Show the docs directory path
    docs_sub.add_parser("path", help="Show the docs directory path")

    # tui - Launch the documentation browser TUI
    docs_sub.add_parser("tui", help="Launch interactive documentation browser")


def _build_dev_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Build the dev command parser for development tools."""
    dev_parser = subparsers.add_parser(
        "dev", help="Development and maintenance tools"
    )
    dev_sub = dev_parser.add_subparsers(dest="dev_command")

    # validate - Validate skills registry
    validate_parser = dev_sub.add_parser(
        "validate", help="Validate skills registry against schema"
    )
    validate_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed validation output"
    )
    validate_parser.add_argument(
        "--check-paths", action="store_true", help="Verify skill paths exist"
    )

    # manpages - Generate manpages
    manpages_parser = dev_sub.add_parser(
        "manpages", help="Generate manpage files"
    )
    manpages_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for manpages (default: docs/reference/)",
    )

    # validate-manpages - Validate manpages are current
    validate_manpages_parser = dev_sub.add_parser(
        "validate-manpages", help="Validate manpages are current with CLI definitions"
    )
    validate_manpages_parser.add_argument(
        "--verbose", action="store_true", help="Show detailed validation output"
    )
    validate_manpages_parser.add_argument(
        "--docs-dir", type=Path, help="Directory containing manpage files"
    )


def _build_file_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    """Build the file command parser for file utilities."""
    file_parser = subparsers.add_parser(
        "file", help="Claude Files API utilities"
    )
    file_sub = file_parser.add_subparsers(dest="file_command")

    # download - Download file by ID
    download_parser = file_sub.add_parser(
        "download", help="Download file by ID"
    )
    download_parser.add_argument("file_id", help="File ID to download")
    download_parser.add_argument(
        "--output", "-o", type=Path, help="Output file path"
    )

    # extract-ids - Extract file IDs from response
    extract_parser = file_sub.add_parser(
        "extract-ids", help="Extract file IDs from API response"
    )
    extract_parser.add_argument(
        "response_file", type=Path, help="JSON response file"
    )


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


def _get_plans_dir() -> Path:
    """Get the plans directory from settings.json or use default."""
    from .core.hooks import load_settings

    settings = load_settings()
    plans_dir_str = settings.get("plansDirectory", "~/.claude/plans")
    plans_dir = Path(plans_dir_str).expanduser().resolve()
    return plans_dir


def _handle_plan_command(args: argparse.Namespace) -> int:
    """Handle plan subcommands for viewing plan files."""
    import subprocess
    from datetime import datetime

    if args.plan_command == "path":
        plans_dir = _get_plans_dir()
        _print(str(plans_dir))
        return 0

    if args.plan_command == "list":
        plans_dir = _get_plans_dir()
        if not plans_dir.exists():
            _print(f"Plans directory does not exist: {plans_dir}")
            return 1

        # Get all .md files
        plan_files = list(plans_dir.glob("*.md"))
        if not plan_files:
            _print(f"No plan files found in {plans_dir}")
            return 0

        # Sort by modification time (newest first)
        plan_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Apply limit
        limit = None if args.all else args.limit
        if limit:
            plan_files = plan_files[:limit]

        # Print header
        _print(f"[0;34mPlans in {plans_dir}:[0m")
        _print("")

        # Print each plan with metadata
        for plan_file in plan_files:
            stat = plan_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024

            # Read first line for title/preview
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    # Remove markdown heading markers
                    preview = first_line.lstrip("#").strip()
                    if not preview:
                        preview = plan_file.stem
            except Exception:
                preview = plan_file.stem

            _print(f"  [0;32m{plan_file.stem}[0m")
            _print(f"    Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            _print(f"    Size: {size_kb:.1f}KB")
            if preview != plan_file.stem:
                _print(f"    Preview: {preview[:80]}")
            _print("")

        if limit and len(plan_files) == limit:
            _print(f"[0;33mShowing {limit} most recent plans. Use --all to see all plans.[0m")

        return 0

    if args.plan_command == "view":
        plans_dir = _get_plans_dir()
        plan_name = args.plan
        if not plan_name.endswith(".md"):
            plan_name += ".md"

        plan_file = plans_dir / plan_name
        if not plan_file.exists():
            _print(f"Plan not found: {plan_file}")
            return 1

        try:
            content = plan_file.read_text(encoding="utf-8")

            # Check if raw mode is requested
            if getattr(args, "raw", False):
                _print(content)
            else:
                # Render markdown with Rich
                from rich.console import Console
                from rich.markdown import Markdown

                console = Console()
                md = Markdown(content)
                console.print(md)
            return 0
        except Exception as e:
            _print(f"Failed to read plan: {e}")
            return 1

    if args.plan_command == "edit":
        import subprocess

        plans_dir = _get_plans_dir()
        plan_name = args.plan
        if not plan_name.endswith(".md"):
            plan_name += ".md"

        plan_file = plans_dir / plan_name
        if not plan_file.exists():
            _print(f"Plan not found: {plan_file}")
            return 1

        editor = os.environ.get("EDITOR", "vim")
        try:
            subprocess.run([editor, str(plan_file)])
            return 0
        except FileNotFoundError:
            _print(f"Editor not found: {editor}")
            _print("Set $EDITOR environment variable to your preferred editor")
            return 1
        except Exception as e:
            _print(f"Failed to open editor: {e}")
            return 1

    _print("Plan command required. Use 'cortex plan --help' for options.")
    return 1


def _get_docs_dir() -> Path:
    """Get the docs directory from cortex root or bundled package installation."""

    # 1. Check cortex root (repo/source installation)
    # Prefer site/ (curated user-facing docs) over docs/ (legacy/development)
    from .core.base import _resolve_cortex_root
    cortex_root = _resolve_cortex_root()
    if cortex_root:
        site_dir = cortex_root / "site"
        if site_dir.is_dir():
            return site_dir
        if (cortex_root / "docs").is_dir():
            return cortex_root / "docs"

    # 2. Check bundled package docs (pip/pipx installation)
    import sys
    for prefix in [sys.prefix, sys.base_prefix]:
        bundled_docs = Path(prefix) / "share" / "claude-cortex" / "docs"
        if bundled_docs.is_dir():
            return bundled_docs

    # 3. Check user site-packages (--user installations)
    import site
    if hasattr(site, 'USER_BASE'):
        user_docs = Path(site.USER_BASE) / "share" / "claude-cortex" / "docs"
        if user_docs.is_dir():
            return user_docs

    # 4. No docs found — return a path that will produce a clear error
    return Path.cwd() / "docs"


def _get_codex_dir() -> Path:
    """Get the codex directory from the current working directory, cortex root, or bundled package."""
    cwd = Path.cwd()

    # 1. Check if we're in a repo with a codex/ folder (development)
    if (cwd / "codex").is_dir():
        return cwd / "codex"

    # 2. Check cortex root (repo/source installation)
    from .core.base import _resolve_cortex_root
    cortex_root = _resolve_cortex_root()
    if cortex_root and (cortex_root / "codex").is_dir():
        return cortex_root / "codex"

    # 3. Check bundled package codex (pip/pipx installation)
    import sys
    for prefix in [sys.prefix, sys.base_prefix]:
        bundled_codex = Path(prefix) / "share" / "claude-cortex" / "codex"
        if bundled_codex.is_dir():
            return bundled_codex

    # 4. Check user site-packages (--user installations)
    import site
    if hasattr(site, 'USER_BASE'):
        user_codex = Path(site.USER_BASE) / "share" / "claude-cortex" / "codex"
        if user_codex.is_dir():
            return user_codex

    # 5. Fallback to cwd/codex
    return cwd / "codex"


def _get_provider_dir(provider: str) -> Path:
    """Get a provider directory (codex, gemini, etc.) using the same resolution as _get_codex_dir."""
    cwd = Path.cwd()

    # 1. Check if we're in a repo with a <provider>/ folder (development)
    if (cwd / provider).is_dir():
        return cwd / provider

    # 2. Check cortex root (repo/source installation)
    from .core.base import _resolve_cortex_root
    cortex_root = _resolve_cortex_root()
    if cortex_root and (cortex_root / provider).is_dir():
        return cortex_root / provider

    # 3. Check bundled package (pip/pipx installation)
    import sys
    for prefix in [sys.prefix, sys.base_prefix]:
        bundled = Path(prefix) / "share" / "claude-cortex" / provider
        if bundled.is_dir():
            return bundled

    # 4. Check user site-packages (--user installations)
    import site
    if hasattr(site, 'USER_BASE'):
        user_dir = Path(site.USER_BASE) / "share" / "claude-cortex" / provider
        if user_dir.is_dir():
            return user_dir

    # 5. Fallback
    return cwd / provider


def _get_bookmarks_file() -> Path:
    """Get the path to the bookmarks file."""
    return Path.home() / ".claude" / "cortex" / "docs-bookmarks.json"


def _load_bookmarks() -> Dict[str, str]:
    """Load bookmarks from file."""
    import json
    bookmarks_file = _get_bookmarks_file()
    if not bookmarks_file.exists():
        return {}
    try:
        return json.loads(bookmarks_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_bookmarks(bookmarks: Dict[str, str]) -> None:
    """Save bookmarks to file."""
    import json
    bookmarks_file = _get_bookmarks_file()
    bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
    bookmarks_file.write_text(
        json.dumps(bookmarks, indent=2) + "\n",
        encoding="utf-8"
    )


def _handle_docs_command(args: argparse.Namespace) -> int:
    """Handle docs subcommands for browsing project documentation."""
    import subprocess
    from datetime import datetime

    # --path override: browse an arbitrary docs directory
    _override = getattr(args, "path", None)
    def _docs_dir() -> Path:
        return _override if _override else _get_docs_dir()

    if args.docs_command == "path":
        docs_dir = _docs_dir()
        _print(str(docs_dir))
        return 0

    if args.docs_command == "tui":
        from .tui.docs_browser import run_docs_browser

        docs_dir = _docs_dir()
        if not docs_dir.exists():
            _print(f"Docs directory does not exist: {docs_dir}")
            return 1

        bookmarks_file = _get_bookmarks_file()
        try:
            run_docs_browser(docs_dir, bookmarks_file)
            return 0
        except Exception as e:
            _print(f"TUI error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    if args.docs_command == "list":
        docs_dir = _docs_dir()
        if not docs_dir.exists():
            _print(f"Docs directory does not exist: {docs_dir}")
            return 1

        # Get all .md files recursively
        md_files = list(docs_dir.rglob("*.md"))
        if not md_files:
            _print(f"No markdown files found in {docs_dir}")
            return 0

        # Apply filter
        filter_pattern = getattr(args, "filter", None)
        if filter_pattern:
            md_files = [f for f in md_files if filter_pattern in str(f.relative_to(docs_dir))]

        # Sort
        sort_by = getattr(args, "sort", "name")
        if sort_by == "name":
            md_files.sort(key=lambda p: str(p.relative_to(docs_dir)))
        elif sort_by == "modified":
            md_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        elif sort_by == "size":
            md_files.sort(key=lambda p: p.stat().st_size, reverse=True)

        # Print header
        _print(f"[0;34mDocumentation in {docs_dir}:[0m")
        _print(f"[0;33m{len(md_files)} files found[0m")
        _print("")

        # Group by directory for better readability
        current_dir = None
        for md_file in md_files:
            rel_path = md_file.relative_to(docs_dir)
            file_dir = rel_path.parent

            # Print directory header when it changes
            if file_dir != current_dir:
                current_dir = file_dir
                if str(file_dir) != ".":
                    _print(f"[0;36m{file_dir}/[0m")

            stat = md_file.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            size_kb = stat.st_size / 1024

            _print(f"  [0;32m{rel_path.name}[0m")
            _print(f"    Path: {rel_path}")
            _print(f"    Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")
            _print(f"    Size: {size_kb:.1f}KB")
            _print("")

        return 0

    if args.docs_command == "tree":
        docs_dir = _docs_dir()
        if not docs_dir.exists():
            _print(f"Docs directory does not exist: {docs_dir}")
            return 1

        from rich.console import Console
        from rich.tree import Tree

        console = Console()
        tree = Tree(f"[bold blue]{docs_dir.name}/[/bold blue]", guide_style="dim")

        def add_to_tree(parent_tree, parent_path):
            items = sorted(parent_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
            for item in items:
                if item.is_dir() and not item.name.startswith('.'):
                    branch = parent_tree.add(f"[blue]{item.name}/[/blue]", guide_style="dim")
                    add_to_tree(branch, item)
                elif item.suffix == ".md":
                    parent_tree.add(f"[green]{item.name}[/green]")

        add_to_tree(tree, docs_dir)
        console.print(tree)
        return 0

    if args.docs_command == "view":
        docs_dir = _docs_dir()
        doc_path = Path(args.path)

        # Handle relative path
        if not doc_path.is_absolute():
            doc_path = docs_dir / doc_path

        # Add .md extension if missing
        if not doc_path.suffix:
            doc_path = doc_path.with_suffix(".md")

        if not doc_path.exists():
            _print(f"Documentation file not found: {doc_path}")
            return 1

        try:
            content = doc_path.read_text(encoding="utf-8")

            # Check if raw mode is requested
            if getattr(args, "raw", False):
                _print(content)
            else:
                # Render markdown with Rich
                from rich.console import Console
                from rich.markdown import Markdown

                console = Console()
                md = Markdown(content)
                console.print(md)
            return 0
        except Exception as e:
            _print(f"Failed to read documentation: {e}")
            return 1

    if args.docs_command == "search":
        docs_dir = _docs_dir()
        if not docs_dir.exists():
            _print(f"Docs directory does not exist: {docs_dir}")
            return 1

        query = args.query.lower()
        limit = getattr(args, "limit", 20)
        results = []

        # Search through all markdown files
        for md_file in docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                # Search for matches
                for line_num, line in enumerate(lines, 1):
                    if query in line.lower():
                        results.append({
                            "file": md_file.relative_to(docs_dir),
                            "line": line_num,
                            "content": line.strip(),
                        })
                        if len(results) >= limit:
                            break
            except Exception:
                continue

            if len(results) >= limit:
                break

        if not results:
            _print(f"No results found for '{query}'")
            return 0

        _print(f"[0;34mSearch results for '{query}':[0m")
        _print(f"[0;33mFound {len(results)} matches[0m")
        _print("")

        for result in results:
            _print(f"[0;32m{result['file']}[0m:[0;33m{result['line']}[0m")
            _print(f"  {result['content'][:100]}")
            _print("")

        return 0

    if args.docs_command == "edit":
        docs_dir = _docs_dir()
        doc_path = Path(args.path)

        if not doc_path.is_absolute():
            doc_path = docs_dir / doc_path

        if not doc_path.suffix:
            doc_path = doc_path.with_suffix(".md")

        if not doc_path.exists():
            _print(f"Documentation file not found: {doc_path}")
            return 1

        editor = os.environ.get("EDITOR", "vim")
        try:
            subprocess.run([editor, str(doc_path)])
            return 0
        except FileNotFoundError:
            _print(f"Editor not found: {editor}")
            _print("Set $EDITOR environment variable to your preferred editor")
            return 1
        except Exception as e:
            _print(f"Failed to open editor: {e}")
            return 1

    if args.docs_command == "bookmark":
        bookmarks = _load_bookmarks()

        if args.bookmark_command == "add":
            docs_dir = _docs_dir()
            doc_path = Path(args.path)

            if not doc_path.is_absolute():
                doc_path = docs_dir / doc_path

            if not doc_path.suffix:
                doc_path = doc_path.with_suffix(".md")

            if not doc_path.exists():
                _print(f"Documentation file not found: {doc_path}")
                return 1

            # Use provided name or default to filename
            name = getattr(args, "name", None) or doc_path.stem

            # Store relative path
            try:
                rel_path = str(doc_path.relative_to(docs_dir))
            except ValueError:
                rel_path = str(doc_path)

            bookmarks[name] = rel_path
            _save_bookmarks(bookmarks)

            _print(f"[0;32m✓ Added bookmark '[0;33m{name}[0;32m' -> {rel_path}[0m")
            return 0

        if args.bookmark_command == "list":
            if not bookmarks:
                _print("No bookmarks saved")
                return 0

            _print("[0;34mSaved bookmarks:[0m")
            _print("")
            for name, path in sorted(bookmarks.items()):
                _print(f"  [0;33m{name}[0m")
                _print(f"    {path}")
            return 0

        if args.bookmark_command == "remove":
            name = args.name
            if name not in bookmarks:
                _print(f"Bookmark not found: {name}")
                return 1

            del bookmarks[name]
            _save_bookmarks(bookmarks)
            _print(f"[0;32m✓ Removed bookmark '{name}'[0m")
            return 0

        if args.bookmark_command == "view":
            name = args.name
            if name not in bookmarks:
                _print(f"Bookmark not found: {name}")
                _print(f"Available bookmarks: {', '.join(bookmarks.keys())}")
                return 1

            docs_dir = _docs_dir()
            doc_path = docs_dir / bookmarks[name]

            if not doc_path.exists():
                _print(f"Bookmarked file no longer exists: {doc_path}")
                return 1

            try:
                content = doc_path.read_text(encoding="utf-8")
                from rich.console import Console
                from rich.markdown import Markdown

                console = Console()
                md = Markdown(content)
                console.print(md)
                return 0
            except Exception as e:
                _print(f"Failed to read documentation: {e}")
                return 1

        _print("Bookmark command required. Use 'cortex docs bookmark --help'")
        return 1

    _print("Docs command required. Use 'cortex docs --help' for options.")
    return 1


def _handle_dev_command(args: argparse.Namespace) -> int:
    """Handle dev subcommands for development tools."""
    if args.dev_command == "validate":
        from .commands.dev_validate import main as validate_main
        return validate_main([
            *(["--verbose"] if getattr(args, "verbose", False) else []),
            *(["--check-paths"] if getattr(args, "check_paths", False) else []),
        ])

    if args.dev_command == "manpages":
        from .commands.dev_manpages import main as manpages_main
        return manpages_main()

    if args.dev_command == "validate-manpages":
        from .commands.dev_validate_manpages import validate_manpages
        exit_code, messages = validate_manpages(
            docs_dir=getattr(args, "docs_dir", None),
            verbose=getattr(args, "verbose", False)
        )
        for message in messages:
            _print(message)
        return exit_code

    _print("Dev command required. Use 'cortex dev --help' for options.")
    return 1


def _handle_file_command(args: argparse.Namespace) -> int:
    """Handle file subcommands for Claude Files API utilities."""
    if args.file_command == "download":
        from .utils.files import download_file, save_file
        from anthropic import Anthropic

        client = Anthropic()
        file_id = args.file_id
        output_path = getattr(args, "output", None)

        try:
            content = download_file(client, file_id)
            if output_path:
                save_file(content, output_path)
                _print(f"File saved to: {output_path}")
            else:
                _print(content)
            return 0
        except Exception as e:
            _print(f"Error downloading file: {e}")
            return 1

    if args.file_command == "extract-ids":
        from .utils.files import extract_file_ids
        import json

        response_file = args.response_file
        try:
            with open(response_file, "r") as f:
                response = json.load(f)
            file_ids = extract_file_ids(response)
            for file_id in file_ids:
                _print(file_id)
            return 0
        except Exception as e:
            _print(f"Error extracting file IDs: {e}")
            return 1

    _print("File command required. Use 'cortex file --help' for options.")
    return 1


def _handle_uninstall_command(args: argparse.Namespace) -> int:
    """Handle uninstall command."""
    from .commands.uninstall import uninstall

    exit_code, message = uninstall(
        dry_run=getattr(args, "dry_run", False),
        keep_config=getattr(args, "keep_config", False),
    )
    _print(message)
    return exit_code


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    _enable_argcomplete(parser)
    args, extra_args = parser.parse_known_args(list(argv) if argv is not None else None)

    if getattr(args, "cortex_root", None):
        os.environ["CORTEX_ROOT"] = str(args.cortex_root)
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
        "completions": _handle_completions_command,
        "mcp": _handle_mcp_command,
        "worktree": _handle_worktree_command,
        "ai": _handle_ai_command,
        "export": _handle_export_command,
        "install": _handle_install_command,
        "statusline": _handle_statusline_command,
        "memory": _handle_memory_command,
        "plan": _handle_plan_command,
        "docs": _handle_docs_command,
        "dev": _handle_dev_command,
        "file": _handle_file_command,
        "uninstall": _handle_uninstall_command,
        "review": _handle_review_command,
        "suggest": _handle_suggest_command,
        "git": _handle_git_command,
        "tmux": _handle_tmux_command,
    }

    if args.command == "status":
        use_rich = getattr(args, "rich", False)
        _print(core.show_status(use_rich=use_rich))
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
