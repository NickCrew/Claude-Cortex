"""Command-line interface for cortex-py."""

from __future__ import annotations

import argparse
import os
import sys
import re
from pathlib import Path
from typing import Iterable, List, cast, Dict, Any, Callable

from . import core
from .core.migration import migrate_to_file_activation, migrate_commands_layout


def _enable_argcomplete(parser: argparse.ArgumentParser) -> None:
    """Integrate argcomplete if it is available."""

    try:  # pragma: no cover - optional dependency
        import argcomplete
    except ImportError:  # pragma: no cover
        return

    argcomplete.autocomplete(parser)


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def _build_mode_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    mode_parser = subparsers.add_parser("mode", help="Mode commands")
    mode_sub = mode_parser.add_subparsers(dest="mode_command")
    mode_sub.add_parser("list", help="List available modes")
    mode_sub.add_parser("status", help="Show active modes")
    mode_activate = mode_sub.add_parser("activate", help="Activate one or more modes")
    mode_activate.add_argument("modes", nargs="+", help="Mode name(s) (without .md)")
    mode_deactivate = mode_sub.add_parser(
        "deactivate", help="Deactivate one or more modes"
    )
    mode_deactivate.add_argument("modes", nargs="+", help="Mode name(s) (without .md)")


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


def _build_principles_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    principles_parser = subparsers.add_parser(
        "principles", help="Principles snippet commands"
    )
    principles_sub = principles_parser.add_subparsers(dest="principles_command")
    principles_sub.add_parser("list", help="List available principle snippets")
    principles_sub.add_parser("status", help="Show active principle snippets")
    principles_activate = principles_sub.add_parser(
        "activate", help="Activate one or more principle snippets"
    )
    principles_activate.add_argument(
        "principles", nargs="+", help="Snippet name(s) (without .md)"
    )
    principles_deactivate = principles_sub.add_parser(
        "deactivate", help="Deactivate one or more principle snippets"
    )
    principles_deactivate.add_argument(
        "principles", nargs="+", help="Snippet name(s) (without .md)"
    )
    principles_sub.add_parser(
        "build", help="Build PRINCIPLES.md from active snippets"
    )


def _build_prompts_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    prompts_parser = subparsers.add_parser("prompts", help="Prompt library commands")
    prompts_sub = prompts_parser.add_subparsers(dest="prompts_command")
    prompts_sub.add_parser("list", help="List available prompts")
    prompts_sub.add_parser("status", help="Show active prompts")
    prompts_activate = prompts_sub.add_parser(
        "activate", help="Activate one or more prompts"
    )
    prompts_activate.add_argument(
        "slugs", nargs="+", help="Prompt slug(s) in category/name format"
    )
    prompts_deactivate = prompts_sub.add_parser(
        "deactivate", help="Deactivate one or more prompts"
    )
    prompts_deactivate.add_argument(
        "slugs", nargs="+", help="Prompt slug(s) in category/name format"
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


def _build_profile_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    profile_parser = subparsers.add_parser("profile", help="Profile commands")
    profile_sub = profile_parser.add_subparsers(dest="profile_command")
    profile_sub.add_parser("list", help="List available profiles")
    profile_save_parser = profile_sub.add_parser(
        "save", help="Save current configuration to a profile"
    )
    profile_save_parser.add_argument("name", help="Profile name")

    # Add subcommands for all built-in profiles
    profile_descriptions = {
        "minimal": "Load minimal profile (essential agents only)",
        "frontend": "Load frontend profile (TypeScript + code review)",
        "web-dev": "Load web-dev profile (full-stack web development)",
        "backend": "Load backend profile (Python + security)",
        "devops": "Load devops profile (infrastructure and deployment)",
        "documentation": "Load documentation profile (documentation focused)",
        "data-ai": "Load data-ai profile (data science and AI)",
        "quality": "Load quality profile (code quality and security)",
        "meta": "Load meta profile (meta-programming and tooling)",
        "developer-experience": "Load developer-experience profile (DX optimization)",
        "product": "Load product profile (product development)",
        "full": "Load full profile (all available agents)",
    }
    for profile_name, description in profile_descriptions.items():
        profile_sub.add_parser(profile_name, help=description)


def _build_workflow_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    workflow_parser = subparsers.add_parser("workflow", help="Workflow commands")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_command")
    workflow_run_parser = workflow_sub.add_parser(
        "run", help="Run a predefined workflow"
    )
    workflow_run_parser.add_argument("workflow", help="Workflow name")
    workflow_sub.add_parser("list", help="List available workflows")
    workflow_sub.add_parser("status", help="Show current workflow progress")
    workflow_sub.add_parser("resume", help="Resume interrupted workflow")
    workflow_stop_parser = workflow_sub.add_parser(
        "stop", help="Stop the currently running workflow"
    )
    workflow_stop_parser.add_argument(
        "workflow",
        nargs="?",
        help="Optional workflow name to confirm stopping",
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


def _build_orchestrate_parser(subparsers: argparse._SubParsersAction[Any]) -> None:
    orchestrate_parser = subparsers.add_parser(
        "orchestrate", help="Scenario orchestration commands", aliases=["orch"]
    )
    orchestrate_sub = orchestrate_parser.add_subparsers(dest="orchestrate_command")
    orchestrate_sub.add_parser("list", help="List available scenarios")
    orchestrate_validate_parser = orchestrate_sub.add_parser(
        "validate", help="Validate scenario metadata"
    )
    orchestrate_validate_parser.add_argument(
        "scenarios",
        nargs="*",
        help="Scenario names to validate (default: all)",
    )
    orchestrate_validate_parser.add_argument(
        "--all",
        dest="validate_all",
        action="store_true",
        help="Validate all scenarios",
    )
    orchestrate_sub.add_parser("status", help="Show scenario execution status")
    orchestrate_stop_parser = orchestrate_sub.add_parser(
        "stop", help="Stop a running scenario"
    )
    orchestrate_stop_parser.add_argument("scenario", help="Scenario name")
    orchestrate_run_parser = orchestrate_sub.add_parser("run", help="Run a scenario")
    orchestrate_run_parser.add_argument("scenario", help="Scenario name")
    orchestrate_run_parser.add_argument(
        "mode_args",
        nargs="*",
        help="Additional run options (e.g., plan)",
    )
    orchestrate_run_parser.add_argument(
        "--auto", dest="run_auto", action="store_true", help="Automatic mode"
    )
    orchestrate_run_parser.add_argument(
        "--interactive",
        dest="run_interactive",
        action="store_true",
        help="Interactive mode",
    )
    orchestrate_run_parser.add_argument(
        "--plan", dest="run_plan", action="store_true", help="Plan mode"
    )
    orchestrate_run_parser.add_argument(
        "--preview", dest="run_preview", action="store_true", help="Preview mode"
    )
    orchestrate_run_parser.add_argument(
        "--validate", dest="run_validate", action="store_true", help="Alias for plan"
    )
    orchestrate_preview_parser = orchestrate_sub.add_parser(
        "preview", help="Preview a scenario without executing"
    )
    orchestrate_preview_parser.add_argument("scenario", help="Scenario name")


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
        help="Disable auto-activation of high-confidence agents",
    )
    ai_watch.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Confidence threshold for notifications (0.0-1.0, default: 0.7)",
    )
    ai_watch.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Check interval in seconds (default: 2.0)",
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


def _build_statusline_parser(
    subparsers: argparse._SubParsersAction[Any],
) -> None:
    from . import statusline

    statusline_parser = subparsers.add_parser(
        "statusline", help="Render Claude Code status line"
    )
    statusline.add_statusline_arguments(statusline_parser)


def _add_start_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to cortex-config.json (default: ~/.cortex/cortex-config.json)",
    )
    parser.add_argument(
        "--plugin-dir",
        type=Path,
        help="Path to Cortex plugin assets (commands, agents, skills, hooks)",
    )
    parser.add_argument(
        "--claude-bin",
        default="claude",
        help="Claude Code binary to execute (default: claude)",
    )
    parser.add_argument(
        "--settings",
        type=Path,
        help="Claude settings.json path (overrides config)",
    )
    parser.add_argument(
        "--modes",
        help="Comma-separated list of modes to append for this launch",
    )
    parser.add_argument(
        "--flags",
        help="Comma-separated list of flags to append for this launch",
    )
    parser.add_argument(
        "claude_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to Claude Code",
    )


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
    subparsers = parser.add_subparsers(dest="command")

    _build_mode_parser(subparsers)
    _build_agent_parser(subparsers)
    _build_rules_parser(subparsers)
    _build_principles_parser(subparsers)
    _build_prompts_parser(subparsers)
    _build_skills_parser(subparsers)
    _build_mcp_parser(subparsers)
    _build_init_parser(subparsers)
    _build_profile_parser(subparsers)
    _build_workflow_parser(subparsers)
    _build_worktree_parser(subparsers)
    _build_orchestrate_parser(subparsers)
    subparsers.add_parser("status", help="Show overall status")
    _build_statusline_parser(subparsers)
    start_parser = subparsers.add_parser(
        "start", help="Launch Claude Code with Cortex configuration"
    )
    _add_start_arguments(start_parser)
    claude_parser = subparsers.add_parser(
        "claude", help="Alias for 'start'"
    )
    _add_start_arguments(claude_parser)
    tui_parser = subparsers.add_parser(
        "tui", help="Launch interactive TUI for agent management"
    )
    tui_parser.add_argument(
        "--theme",
        type=Path,
        help="Path to a Textual .tcss theme override file",
    )
    _build_ai_parser(subparsers)
    _build_export_parser(subparsers)
    _build_completion_parser(subparsers)
    _build_install_parser(subparsers)
    _build_doctor_parser(subparsers)
    _build_memory_parser(subparsers)
    _build_setup_parser(subparsers)

    return parser


def _handle_mode_command(args: argparse.Namespace) -> int:
    if args.mode_command == "list":
        _print(core.list_modes())
        return 0
    if args.mode_command == "status":
        _print(core.mode_status())
        return 0
    if args.mode_command == "activate":
        messages = []
        final_exit_code = 0
        for mode in args.modes:
            exit_code, message = core.mode_activate(mode)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.mode_command == "deactivate":
        messages = []
        final_exit_code = 0
        for mode in args.modes:
            exit_code, message = core.mode_deactivate(mode)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    return 1


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
        for agent in args.agents:
            exit_code, message = core.agent_activate(agent)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.agent_command == "deactivate":
        messages = []
        final_exit_code = 0
        for agent in args.agents:
            exit_code, message = core.agent_deactivate(agent, force=args.force)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
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
        for rule in args.rules:
            messages.append(core.rules_activate(rule))
        _print("\n".join(messages))
        return 0
    if args.rules_command == "deactivate":
        messages = []
        for rule in args.rules:
            messages.append(core.rules_deactivate(rule))
        _print("\n".join(messages))
        return 0
    return 1


def _handle_principles_command(args: argparse.Namespace) -> int:
    if args.principles_command == "list":
        _print(core.list_principles())
        return 0
    if args.principles_command == "status":
        _print(core.principles_status())
        return 0
    if args.principles_command == "activate":
        messages = []
        final_exit_code = 0
        for name in args.principles:
            exit_code, message = core.principles_activate(name)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.principles_command == "deactivate":
        messages = []
        final_exit_code = 0
        for name in args.principles:
            exit_code, message = core.principles_deactivate(name)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.principles_command == "build":
        exit_code, message = core.principles_build()
        _print(message)
        return exit_code
    return 1


def _handle_start_command(args: argparse.Namespace, extra_args: List[str]) -> int:
    from .launcher import DEFAULT_CONFIG_PATH, start_claude

    config_path = getattr(args, "config", None) or DEFAULT_CONFIG_PATH
    claude_args = list(getattr(args, "claude_args", []) or [])
    if extra_args:
        claude_args.extend(extra_args)
    if claude_args and claude_args[0] == "--":
        claude_args = claude_args[1:]

    try:
        return start_claude(
            config_path=config_path,
            plugin_dir=getattr(args, "plugin_dir", None) or getattr(args, "plugin_root", None),
            claude_bin=getattr(args, "claude_bin", "claude"),
            settings_path=getattr(args, "settings", None),
            modes_override=getattr(args, "modes", None),
            flags_override=getattr(args, "flags", None),
            extra_args=claude_args,
        )
    except RuntimeError as exc:
        _print(str(exc))
        return 1


def _handle_prompts_command(args: argparse.Namespace) -> int:
    if args.prompts_command == "list":
        _print(core.list_prompts())
        return 0
    if args.prompts_command == "status":
        _print(core.prompt_status())
        return 0
    if args.prompts_command == "activate":
        messages = []
        final_exit_code = 0
        for slug in args.slugs:
            exit_code, message = core.prompt_activate(slug)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.prompts_command == "deactivate":
        messages = []
        final_exit_code = 0
        for slug in args.slugs:
            exit_code, message = core.prompt_deactivate(slug)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
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
        for doc in args.docs:
            exit_code, message = core.mcp_activate(doc)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
        return final_exit_code
    if args.mcp_command == "deactivate":
        messages = []
        final_exit_code = 0
        for doc in args.docs:
            exit_code, message = core.mcp_deactivate(doc)
            messages.append(message)
            if exit_code != 0:
                final_exit_code = exit_code
        _print("\n".join(messages))
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
        return exit_code
    if init_command == "profile":
        exit_code, message = core.init_profile(getattr(args, "name", None))
        if message:
            _print(message)
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
    return exit_code


def _handle_profile_command(args: argparse.Namespace) -> int:
    if args.profile_command == "list":
        _print(core.profile_list())
        return 0
    if args.profile_command == "save":
        exit_code, message = core.profile_save(args.name)
        _print(message)
        return exit_code

    # Handle all built-in profile commands dynamically
    profile_loaders = {
        "minimal": core.profile_minimal,
        "frontend": core.profile_frontend,
        "web-dev": core.profile_web_dev,
        "backend": core.profile_backend,
        "devops": core.profile_devops,
        "documentation": core.profile_documentation,
        "data-ai": core.profile_data_ai,
        "quality": core.profile_quality,
        "meta": core.profile_meta,
        "developer-experience": core.profile_developer_experience,
        "product": core.profile_product,
        "full": core.profile_full,
    }
    loader = profile_loaders.get(args.profile_command)
    if loader:
        exit_code, message = loader()
        _print(message)
        return exit_code
    return 1


def _handle_workflow_command(args: argparse.Namespace) -> int:
    if args.workflow_command == "run":
        exit_code, message = core.workflow_run(args.workflow)
        _print(message)
        return exit_code
    if args.workflow_command == "list":
        _print(core.workflow_list())
        return 0
    if args.workflow_command == "status":
        exit_code, message = core.workflow_status()
        _print(message)
        return exit_code
    if args.workflow_command == "resume":
        exit_code, message = core.workflow_resume()
        _print(message)
        return exit_code
    if args.workflow_command == "stop":
        exit_code, message = core.workflow_stop(getattr(args, "workflow", None))
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


def _handle_orchestrate_command(args: argparse.Namespace) -> int:
    if args.orchestrate_command == "list":
        _print(core.scenario_list())
        return 0
    if args.orchestrate_command == "validate":
        targets = list(getattr(args, "scenarios", []) or [])
        if getattr(args, "validate_all", False):
            targets.insert(0, "--all")
        exit_code, message = core.scenario_validate(*targets)
        _print(message)
        return exit_code
    if args.orchestrate_command == "status":
        _print(core.scenario_status())
        return 0
    if args.orchestrate_command == "stop":
        exit_code, message = core.scenario_stop(args.scenario)
        _print(message)
        return exit_code
    if args.orchestrate_command == "run":
        options: List[str] = []
        if getattr(args, "run_auto", False):
            options.append("--auto")
        if getattr(args, "run_interactive", False):
            options.append("--interactive")
        if getattr(args, "run_plan", False) or getattr(args, "run_validate", False):
            options.append("--plan")
        if getattr(args, "run_preview", False):
            options.append("--preview")
        options.extend(getattr(args, "mode_args", []) or [])
        exit_code, message = core.scenario_run(args.scenario, *options)
        _print(message)
        return exit_code
    if args.orchestrate_command == "preview":
        exit_code, message = core.scenario_preview(args.scenario)
        _print(message)
        return exit_code
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

        return watch.watch_main(
            auto_activate=not args.no_auto_activate,
            threshold=args.threshold,
            interval=args.interval,
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

    handlers: Dict[str, Callable[[argparse.Namespace], int]] = {
        "mode": _handle_mode_command,
        "agent": _handle_agent_command,
        "rules": _handle_rules_command,
        "principles": _handle_principles_command,
        "prompts": _handle_prompts_command,
        "skills": _handle_skills_command,
        "mcp": _handle_mcp_command,
        "init": _handle_init_command,
        "profile": _handle_profile_command,
        "workflow": _handle_workflow_command,
        "worktree": _handle_worktree_command,
        "orchestrate": _handle_orchestrate_command,
        "orch": _handle_orchestrate_command,
        "ai": _handle_ai_command,
        "export": _handle_export_command,
        "completion": _handle_completion_command,
        "install": _handle_install_command,
        "statusline": _handle_statusline_command,
        "doctor": _handle_doctor_command,
        "memory": _handle_memory_command,
        "setup": _handle_setup_command,
    }

    if args.command == "status":
        _print(core.show_status())
        return 0
    
    if args.command == "tui":
        from .tui.main import main as tui_main
        return tui_main(theme_path=getattr(args, "theme", None))

    if args.command in ("start", "claude"):
        return _handle_start_command(args, extra_args)

    if extra_args:
        parser.error(f"unrecognized arguments: {' '.join(extra_args)}")

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
