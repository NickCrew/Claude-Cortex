"""Command-line interface for claude-ctx-py."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from . import core


def _enable_argcomplete(parser: argparse.ArgumentParser) -> None:
    """Integrate argcomplete if it is available."""

    try:  # pragma: no cover - optional dependency
        import argcomplete  # type: ignore
    except ImportError:  # pragma: no cover
        return

    argcomplete.autocomplete(parser)  # type: ignore[attr-defined]


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="claude-ctx",
        description="Python implementation of claude-ctx list and status commands",
    )
    subparsers = parser.add_subparsers(dest="command")

    mode_parser = subparsers.add_parser("mode", help="Mode commands")
    mode_sub = mode_parser.add_subparsers(dest="mode_command")
    mode_sub.add_parser("list", help="List available modes")
    mode_sub.add_parser("status", help="Show active modes")
    mode_activate = mode_sub.add_parser("activate", help="Activate a mode")
    mode_activate.add_argument("mode", help="Mode name (without .md)")
    mode_deactivate = mode_sub.add_parser(
        "deactivate", help="Deactivate a mode"
    )
    mode_deactivate.add_argument("mode", help="Mode name (without .md)")

    agent_parser = subparsers.add_parser("agent", help="Agent commands")
    agent_sub = agent_parser.add_subparsers(dest="agent_command")
    agent_sub.add_parser("list", help="List available agents")
    agent_sub.add_parser("status", help="Show active agents")
    agent_activate = agent_sub.add_parser("activate", help="Activate an agent")
    agent_activate.add_argument("agent", help="Agent name (without .md)")
    agent_deactivate = agent_sub.add_parser(
        "deactivate", help="Deactivate an agent"
    )
    agent_deactivate.add_argument("agent", help="Agent name (without .md)")
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

    rules_parser = subparsers.add_parser("rules", help="Rule commands")
    rules_sub = rules_parser.add_subparsers(dest="rules_command")
    rules_sub.add_parser("list", help="List available rules")
    rules_sub.add_parser("status", help="Show active rule modules")
    rules_activate = rules_sub.add_parser("activate", help="Activate a rule module")
    rules_activate.add_argument("rule", help="Rule name (without .md)")
    rules_deactivate = rules_sub.add_parser(
        "deactivate", help="Deactivate a rule module"
    )
    rules_deactivate.add_argument("rule", help="Rule name (without .md)")

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

    # Profile commands
    profile_parser = subparsers.add_parser("profile", help="Profile commands")
    profile_sub = profile_parser.add_subparsers(dest="profile_command")
    profile_sub.add_parser("list", help="List available profiles")
    profile_save_parser = profile_sub.add_parser("save", help="Save current configuration to a profile")
    profile_save_parser.add_argument("name", help="Profile name")
    profile_sub.add_parser("minimal", help="Load minimal profile (essential agents only)")
    profile_sub.add_parser("backend", help="Load backend profile")

    # Workflow commands
    workflow_parser = subparsers.add_parser("workflow", help="Workflow commands")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_command")
    workflow_run_parser = workflow_sub.add_parser("run", help="Run a predefined workflow")
    workflow_run_parser.add_argument("workflow", help="Workflow name")
    workflow_sub.add_parser("list", help="List available workflows")
    workflow_sub.add_parser("status", help="Show current workflow progress")
    workflow_sub.add_parser("resume", help="Resume interrupted workflow")

    # Orchestrate/Scenario commands
    orchestrate_parser = subparsers.add_parser(
        "orchestrate",
        help="Scenario orchestration commands",
        aliases=["orch"]
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
    orchestrate_run_parser = orchestrate_sub.add_parser(
        "run", help="Run a scenario"
    )
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

    subparsers.add_parser("status", help="Show overall status")

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    _enable_argcomplete(parser)
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "mode":
        if args.mode_command == "list":
            _print(core.list_modes())
            return 0
        if args.mode_command == "status":
            _print(core.mode_status())
            return 0
        if args.mode_command == "activate":
            exit_code, message = core.mode_activate(args.mode)
            _print(message)
            return exit_code
        if args.mode_command == "deactivate":
            exit_code, message = core.mode_deactivate(args.mode)
            _print(message)
            return exit_code
    elif args.command == "agent":
        if args.agent_command == "list":
            _print(core.list_agents())
            return 0
        if args.agent_command == "status":
            _print(core.agent_status())
            return 0
        if args.agent_command == "activate":
            exit_code, message = core.agent_activate(args.agent)
            _print(message)
            return exit_code
        if args.agent_command == "deactivate":
            exit_code, message = core.agent_deactivate(
                args.agent, force=args.force
            )
            _print(message)
            return exit_code
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
    elif args.command == "rules":
        if args.rules_command == "list":
            _print(core.list_rules())
            return 0
        if args.rules_command == "status":
            _print(core.rules_status())
            return 0
        if args.rules_command == "activate":
            _print(core.rules_activate(args.rule))
            return 0
        if args.rules_command == "deactivate":
            _print(core.rules_deactivate(args.rule))
            return 0
    elif args.command == "skills":
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
    elif args.command == "init":
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
    elif args.command == "profile":
        if args.profile_command == "list":
            _print(core.profile_list())
            return 0
        if args.profile_command == "save":
            exit_code, message = core.profile_save(args.name)
            _print(message)
            return exit_code
        if args.profile_command == "minimal":
            exit_code, message = core.profile_minimal()
            _print(message)
            return exit_code
        if args.profile_command == "backend":
            exit_code, message = core.profile_backend()
            _print(message)
            return exit_code
    elif args.command == "workflow":
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
    elif args.command in ("orchestrate", "orch"):
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
    elif args.command == "status":
        _print(core.show_status())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
