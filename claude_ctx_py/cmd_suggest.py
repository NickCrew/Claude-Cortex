"""Unified suggestion CLI commands.

Consolidates skill and agent recommendation functionality into a single
``cortex suggest`` entry point.  All recommendation engines are reused
as-is; this module only orchestrates their output.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core import _resolve_claude_dir
from .intelligence import IntelligentAgent, get_current_context


# ── Formatting helpers ────────────────────────────────────────────


def _print_agent_recommendations(recommendations: List[Any]) -> None:
    """Format and print agent recommendations."""
    print("\nAGENT RECOMMENDATIONS\n")

    for i, rec in enumerate(recommendations, 1):
        if rec.urgency == "critical":
            urgency_icon = "!!"
        elif rec.urgency == "high":
            urgency_icon = "! "
        elif rec.urgency == "medium":
            urgency_icon = ". "
        else:
            urgency_icon = "  "

        auto_badge = " [AUTO]" if rec.auto_activate else ""
        print(f"  {urgency_icon}{i}. {rec.agent_name}{auto_badge}")
        print(f"       Confidence: {rec.confidence * 100:.0f}%")
        print(f"       {rec.reason}")


def _print_skill_recommendations(recommendations: List[Any]) -> None:
    """Format and print skill recommendations grouped by confidence."""
    print("\nSKILL RECOMMENDATIONS\n")

    high_conf = [r for r in recommendations if r.confidence >= 0.8]
    med_conf = [r for r in recommendations if 0.6 <= r.confidence < 0.8]
    low_conf = [r for r in recommendations if r.confidence < 0.6]

    if high_conf:
        print("  High Confidence:")
        for rec in high_conf:
            print(f"    + {rec.skill_name} ({int(rec.confidence * 100)}%)")
            print(f"      {rec.reason}")
            if rec.related_agents:
                agents_str = ", ".join(rec.related_agents[:3])
                print(f"      Related agents: {agents_str}")

    if med_conf:
        print("  Medium Confidence:")
        for rec in med_conf:
            print(f"    - {rec.skill_name} ({int(rec.confidence * 100)}%)")
            print(f"      {rec.reason}")

    if low_conf:
        print("  Low Confidence:")
        for rec in low_conf[:3]:
            print(f"    o {rec.skill_name} ({int(rec.confidence * 100)}%)")


def _print_workflow_prediction(workflow: Any) -> None:
    """Format and print workflow prediction."""
    print(f"\nWORKFLOW PREDICTION\n")
    print(f"  Workflow: {workflow.workflow_name}")
    print(f"  Confidence: {workflow.confidence * 100:.0f}%")
    print(
        f"  Estimated Duration: {workflow.estimated_duration // 60}m "
        f"{workflow.estimated_duration % 60}s"
    )
    print(f"  Success Probability: {workflow.success_probability * 100:.0f}%")
    if workflow.agents_sequence:
        print(f"  Agent Sequence:")
        for i, agent_name in enumerate(workflow.agents_sequence, 1):
            print(f"    {i}. {agent_name}")


def _print_context_summary(context: Any) -> None:
    """Format and print detected context signals."""
    signals = []
    if context.has_frontend:
        signals.append("Frontend")
    if context.has_backend:
        signals.append("Backend")
    if context.has_database:
        signals.append("Database")
    if context.has_tests:
        signals.append("Tests")
    if context.has_auth:
        signals.append("Auth")
    if context.has_api:
        signals.append("API")

    if signals:
        print(f"\nCONTEXT: {', '.join(signals)}")
    if context.errors_count > 0 or context.test_failures > 0:
        print(
            f"  Issues: {context.errors_count} errors, "
            f"{context.test_failures} test failures"
        )


# ── Handler functions ─────────────���───────────────────────────────


def suggest_default(
    *,
    skills_only: bool = False,
    agents_only: bool = False,
    project_dir: str = ".",
) -> int:
    """Context-aware unified suggestion (default mode).

    Combines agent recommendations (IntelligentAgent) and skill
    recommendations (SkillRecommender) into a single output.

    Returns:
        Exit code (0 for success)
    """
    from .skill_recommender import SkillRecommender

    claude_dir = _resolve_claude_dir()
    context = get_current_context()

    agent_recs: List[Any] = []
    skill_recs: List[Any] = []
    intelligent_agent: Optional[IntelligentAgent] = None

    # Agent recommendations
    if not skills_only:
        try:
            intelligent_agent = IntelligentAgent(claude_dir / "intelligence")
            intelligent_agent.analyze_context()
            agent_recs = intelligent_agent.get_recommendations()
        except Exception as exc:
            print(f"Warning: Agent recommendations unavailable: {exc}", file=sys.stderr)

    # Skill recommendations
    if not agents_only:
        try:
            recommender = SkillRecommender()
            skill_recs = recommender.recommend_for_context(context)
        except Exception as exc:
            print(f"Warning: Skill recommendations unavailable: {exc}", file=sys.stderr)

    if not agent_recs and not skill_recs:
        print("No suggestions for the current context.")
        return 0

    print("=" * 60)
    print("SUGGESTIONS")
    print("=" * 60)

    if agent_recs:
        _print_agent_recommendations(agent_recs)

    if skill_recs:
        _print_skill_recommendations(skill_recs)

    # Workflow prediction
    if intelligent_agent and not skills_only:
        try:
            workflow = intelligent_agent.predict_workflow()
            if workflow:
                _print_workflow_prediction(workflow)
        except Exception:
            pass

    # Context summary
    _print_context_summary(context)

    print("\n" + "=" * 60)
    print("Tip: Use 'cortex suggest --activate' to auto-activate high-confidence matches")

    return 0


def suggest_text(text: str) -> int:
    """Analyze free text for skill matches.

    Wraps ``core.skill_analyze(text)``.

    Returns:
        Exit code
    """
    from .core import skill_analyze

    exit_code, message = skill_analyze(text)
    print(message)
    return exit_code


def suggest_activate() -> int:
    """Auto-activate high-confidence agents and display skill matches.

    Reuses the activation logic from ``cmd_ai.ai_auto_activate()``.

    Returns:
        Exit code
    """
    from .core import agent_activate
    from .messages import RESTART_REQUIRED_MESSAGE as RESTART_MSG
    from .skill_recommender import SkillRecommender

    claude_dir = _resolve_claude_dir()
    agent = IntelligentAgent(claude_dir / "intelligence")
    agent.analyze_context()

    # --- Agent auto-activation ---
    auto_agents = agent.get_auto_activations()

    if auto_agents:
        agents_dir = claude_dir / "agents"
        already_active = []
        to_activate = []

        for agent_name in auto_agents:
            agent_file = agents_dir / f"{agent_name}.md"
            if agent_file.is_file():
                already_active.append(agent_name)
            else:
                to_activate.append(agent_name)

        if already_active:
            print(f"Already active ({len(already_active)} agents):")
            for name in already_active:
                print(f"  + {name}")
            print()

        if to_activate:
            print(f"Activating {len(to_activate)} agents...\n")
            activated = []
            failed = []

            for agent_name in to_activate:
                try:
                    exit_code, message = agent_activate(agent_name)
                    if exit_code == 0:
                        activated.append(agent_name)
                        agent.mark_auto_activated(agent_name)
                        print(f"  + {agent_name}")
                    else:
                        failed.append(agent_name)
                        print(f"  x {agent_name}: {message}")
                except Exception as e:
                    failed.append(agent_name)
                    print(f"  x {agent_name}: {e}")

            if activated:
                print(f"\nActivated {len(activated)} agent(s)")
                print(f"\n  {RESTART_MSG}")

            if failed:
                print(f"Failed: {', '.join(failed)}")
                return 1
        else:
            print("No new agents to activate.")
    else:
        print("No auto-activation recommendations for current context.")

    # --- Skill recommendations (display only) ---
    try:
        context = get_current_context()
        recommender = SkillRecommender()
        skill_recs = recommender.recommend_for_context(context)
        high_conf = [r for r in skill_recs if r.confidence >= 0.8]

        if high_conf:
            print(f"\nHigh-confidence skill recommendations ({len(high_conf)}):")
            for rec in high_conf:
                print(f"  {rec.skill_name} ({int(rec.confidence * 100)}%)")
    except Exception:
        pass

    return 0


def suggest_watch(
    *,
    no_auto_activate: bool = False,
    daemon: bool = False,
    status: bool = False,
    stop: bool = False,
    watch_log: Optional[str] = None,
    threshold: Optional[float] = None,
    interval: Optional[float] = None,
    watch_dirs: Optional[List[str]] = None,
) -> int:
    """Real-time monitoring mode.

    Delegates to ``watch.watch_main()`` / ``watch.start_watch_daemon()``.

    Returns:
        Exit code
    """
    from . import watch

    if status and stop:
        print("Choose either --status or --stop.")
        return 1
    if (status or stop) and daemon:
        print("Use --status/--stop without --daemon.")
        return 1

    if status:
        exit_code, message = watch.watch_daemon_status()
        print(message)
        return exit_code

    if stop:
        exit_code, message = watch.stop_watch_daemon()
        print(message)
        return exit_code

    defaults = watch.load_watch_defaults()
    for warning in defaults.warnings:
        print(f"Config warning: {warning}")

    # Resolve watch directories
    resolved_dirs: List[Path] = []
    for entry in (watch_dirs or []):
        for raw in entry.split(","):
            cleaned = raw.strip()
            if cleaned:
                resolved_dirs.append(Path(os.path.expanduser(cleaned)))

    if resolved_dirs:
        invalid = [p for p in resolved_dirs if not p.exists() or not p.is_dir()]
        if invalid:
            print("Invalid watch directory(s):")
            for path in invalid:
                print(f"  - {path}")
            return 1

    # Merge CLI args with config defaults
    if no_auto_activate:
        auto_activate = False
    elif defaults.auto_activate is not None:
        auto_activate = defaults.auto_activate
    else:
        auto_activate = True

    final_threshold = (
        threshold
        if threshold is not None
        else (defaults.threshold if defaults.threshold is not None else 0.7)
    )
    final_interval = (
        interval
        if interval is not None
        else (defaults.interval if defaults.interval is not None else 2.0)
    )
    directories = resolved_dirs or defaults.directories

    if daemon:
        log_path = None
        if watch_log:
            log_path = Path(os.path.expanduser(watch_log)).resolve()
        exit_code, message = watch.start_watch_daemon(
            auto_activate=auto_activate,
            threshold=final_threshold,
            interval=final_interval,
            directories=directories,
            log_path=log_path,
        )
        print(message)
        return exit_code

    return watch.watch_main(
        auto_activate=auto_activate,
        threshold=final_threshold,
        interval=final_interval,
        directories=directories,
    )


def suggest_export(output_file: str = "suggestions.json") -> int:
    """Export unified suggestions to JSON.

    Combines agent recommendations and skill recommendations.

    Returns:
        Exit code
    """
    from .skill_recommender import SkillRecommender

    claude_dir = _resolve_claude_dir()

    # Agent suggestions
    agent = IntelligentAgent(claude_dir / "intelligence")
    agent.analyze_context()
    agent_data = agent.get_smart_suggestions()

    # Skill suggestions
    context = get_current_context()
    recommender = SkillRecommender()
    skill_recs = recommender.recommend_for_context(context)

    combined: Dict[str, Any] = {
        **agent_data,
        "skill_recommendations": [r.to_dict() for r in skill_recs],
    }

    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(combined, f, indent=2)

    agent_count = len(combined.get("agent_recommendations", []))
    skill_count = len(combined.get("skill_recommendations", []))
    print(f"Exported to {output_path}")
    print(f"  {agent_count} agent recommendations")
    print(f"  {skill_count} skill recommendations")

    return 0


def suggest_review(
    *,
    dry_run: bool = False,
    extra_context: Optional[List[str]] = None,
) -> int:
    """Pre-completion review gate.

    Delegates to ``cmd_review.main()``.

    Returns:
        Exit code
    """
    from . import cmd_review

    return cmd_review.main(dry_run=dry_run, extra_context=extra_context)
