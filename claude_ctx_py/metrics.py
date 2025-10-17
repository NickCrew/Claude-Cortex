"""Skill metrics tracking and reporting."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import (
    InvalidMetricsDataError,
    MetricsFileError,
)
from .error_utils import safe_load_json, safe_save_json, ensure_directory


def get_metrics_path() -> Path:
    """Get metrics storage path (~/.claude/.metrics/skills/).

    Raises:
        MetricsFileError: If metrics directory cannot be created
    """
    claude_home = os.environ.get("CLAUDE_CTX_HOME") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if claude_home:
        base = Path(claude_home)
    else:
        base = Path.home() / ".claude"

    metrics_dir = base / ".metrics" / "skills"
    try:
        ensure_directory(metrics_dir, purpose="metrics storage")
    except Exception as exc:
        raise MetricsFileError(
            str(metrics_dir),
            "create directory",
            str(exc)
        ) from exc

    return metrics_dir


def load_metrics() -> Dict[str, Any]:
    """Load metrics from stats.json.

    Returns:
        Dictionary containing metrics data, or default structure on error
    """
    metrics_path = get_metrics_path() / "stats.json"

    if not metrics_path.exists():
        return {"skills": {}}

    try:
        return safe_load_json(metrics_path)
    except (InvalidMetricsDataError, FileNotFoundError):
        # Return default structure on error (backward compatibility)
        return {"skills": {}}


def _save_metrics(metrics: Dict[str, Any]) -> None:
    """Save metrics to stats.json.

    Raises:
        MetricsFileError: If save operation fails
    """
    metrics_path = get_metrics_path() / "stats.json"

    try:
        safe_save_json(metrics_path, metrics)
    except Exception as exc:
        raise MetricsFileError(
            str(metrics_path),
            "write",
            f"Failed to save metrics: {exc}"
        ) from exc


def record_activation(skill_name: str, tokens_used: int, success: bool) -> None:
    """Record a skill activation.

    Args:
        skill_name: Name of the skill being activated
        tokens_used: Number of tokens used/saved by the skill
        success: Whether the activation was successful
    """
    metrics = load_metrics()

    if "skills" not in metrics:
        metrics["skills"] = {}

    if skill_name not in metrics["skills"]:
        metrics["skills"][skill_name] = {
            "activation_count": 0,
            "total_tokens_saved": 0,
            "avg_tokens": 0,
            "last_activated": None,
            "success_rate": 0.0
        }

    skill_metrics = metrics["skills"][skill_name]

    # Update activation count
    skill_metrics["activation_count"] += 1

    # Update tokens
    skill_metrics["total_tokens_saved"] += tokens_used
    skill_metrics["avg_tokens"] = (
        skill_metrics["total_tokens_saved"] // skill_metrics["activation_count"]
    )

    # Update timestamp
    skill_metrics["last_activated"] = datetime.utcnow().isoformat() + "Z"

    # Update success rate
    # Track successes based on previous rate and new result
    previous_successes = int(
        skill_metrics["success_rate"] * (skill_metrics["activation_count"] - 1)
    )
    new_successes = previous_successes + (1 if success else 0)
    skill_metrics["success_rate"] = new_successes / skill_metrics["activation_count"]

    _save_metrics(metrics)


def get_skill_metrics(skill_name: str) -> Optional[Dict[str, Any]]:
    """Get metrics for a specific skill.

    Args:
        skill_name: Name of the skill

    Returns:
        Dictionary of metrics or None if skill has no metrics
    """
    metrics = load_metrics()
    skills: Dict[str, Any] = metrics.get("skills", {})
    return skills.get(skill_name)


def get_all_metrics() -> Dict[str, Any]:
    """Get all skill metrics.

    Returns:
        Dictionary mapping skill names to their metrics
    """
    metrics = load_metrics()
    skills: Dict[str, Any] = metrics.get("skills", {})
    return skills


def reset_metrics() -> None:
    """Reset all metrics."""
    metrics_path = get_metrics_path() / "stats.json"

    if metrics_path.exists():
        metrics_path.unlink()


def record_detailed_activation(
    skill_name: str,
    context: Dict[str, Any]
) -> None:
    """Record a detailed skill activation with rich context.

    Args:
        skill_name: Name of the skill being activated
        context: Dictionary containing:
            - tokens_loaded: Number of tokens in skill content
            - tokens_saved: Estimated tokens saved
            - duration_ms: Time taken to load/process
            - success: Whether activation succeeded
            - agent: Name of activating agent (optional)
            - task_type: Type of task (optional)
            - project_type: Type of project (optional)
            - relevance_score: How relevant the skill was 0-1 (optional)
            - completion_improvement: Task completion improvement (optional)
            - user_satisfaction: User rating 1-5 (optional)

    Raises:
        MetricsFileError: If activation record cannot be saved
    """
    metrics_path = get_metrics_path()

    # Load or initialize detailed activations log
    activations_file = metrics_path / "activations.json"

    if activations_file.exists():
        try:
            activations_data = safe_load_json(activations_file)
        except (InvalidMetricsDataError, FileNotFoundError):
            activations_data = {"activations": []}
    else:
        activations_data = {"activations": []}

    # Create activation record
    activation_record = {
        "activation_id": str(uuid.uuid4()),
        "skill_name": skill_name,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "context": {
            "agent": context.get("agent", "unknown"),
            "task_type": context.get("task_type", "unknown"),
            "project_type": context.get("project_type", "unknown"),
            "co_activated_skills": context.get("co_activated_skills", [])
        },
        "metrics": {
            "tokens_loaded": context.get("tokens_loaded", 0),
            "tokens_saved": context.get("tokens_saved", 0),
            "duration_ms": context.get("duration_ms", 0),
            "success": context.get("success", True)
        },
        "effectiveness": {
            "relevance_score": context.get("relevance_score", 0.8),
            "completion_improvement": context.get("completion_improvement", 0.0),
            "user_satisfaction": context.get("user_satisfaction", 3)
        }
    }

    # Add to activations list
    activations_data["activations"].append(activation_record)

    # Keep only last 1000 activations to prevent unbounded growth
    if len(activations_data["activations"]) > 1000:
        activations_data["activations"] = activations_data["activations"][-1000:]

    # Save detailed activations
    try:
        safe_save_json(activations_file, activations_data)
    except Exception as exc:
        raise MetricsFileError(
            str(activations_file),
            "write",
            f"Failed to save activation record: {exc}"
        ) from exc

    # Also update the summary metrics
    tokens_saved = context.get("tokens_saved", 0)
    success = context.get("success", True)
    record_activation(skill_name, tokens_saved, success)


def get_effectiveness_score(skill_name: str) -> float:
    """Calculate effectiveness score for a skill (0-100).

    Score is based on success rate, token efficiency, usage frequency, and recency.

    Args:
        skill_name: Name of the skill

    Returns:
        Effectiveness score from 0 to 100
    """
    from . import analytics

    all_metrics = get_all_metrics()
    return analytics.get_effectiveness_score(skill_name, all_metrics)


def get_correlation_matrix() -> Dict[str, Dict[str, float]]:
    """Get skill co-activation correlation matrix.

    Returns:
        Dictionary mapping skill names to correlation scores with other skills
    """
    from . import analytics

    all_metrics = get_all_metrics()
    return analytics.get_correlation_matrix(all_metrics)


def get_impact_report(skill_name: str) -> Dict[str, Any]:
    """Generate comprehensive impact analysis for a skill.

    Args:
        skill_name: Name of the skill

    Returns:
        Dictionary containing comprehensive impact metrics
    """
    from . import analytics
    from pathlib import Path

    claude_dir = Path.home() / ".claude"
    return analytics.get_impact_report(skill_name, claude_dir)


def generate_analytics_report(output_format: str = 'text') -> str:
    """Generate comprehensive analytics report.

    Args:
        output_format: Format of report ('text' or 'json')

    Returns:
        Formatted report string
    """
    from . import analytics
    from pathlib import Path

    claude_dir = Path.home() / ".claude"
    return analytics.generate_analytics_report(output_format, claude_dir)


def format_metrics(metrics: Dict[str, Any], skill_name: Optional[str] = None) -> str:
    """Format metrics for CLI display.

    Args:
        metrics: Metrics dictionary to format
        skill_name: Optional skill name for single-skill display

    Returns:
        Formatted string for display
    """
    if not metrics:
        return "No metrics recorded yet."

    if skill_name:
        # Single skill display
        if skill_name not in metrics:
            return f"No metrics found for skill: {skill_name}"

        m = metrics[skill_name]
        output = [
            f"\nSkill: {skill_name}",
            f"  Activation Count:    {m['activation_count']}",
            f"  Total Tokens Saved:  {m['total_tokens_saved']:,}",
            f"  Avg Tokens/Use:      {m['avg_tokens']:,}",
            f"  Success Rate:        {m['success_rate']:.1%}",
            f"  Last Activated:      {m['last_activated'] or 'Never'}",
        ]
        return "\n".join(output)

    # All skills display
    output = ["\nSkill Metrics Summary:\n"]

    # Sort by activation count (most used first)
    sorted_skills = sorted(
        metrics.items(),
        key=lambda x: x[1]["activation_count"],
        reverse=True
    )

    if not sorted_skills:
        return "No metrics recorded yet."

    # Table header
    output.append(
        f"{'Skill':<40} {'Uses':<8} {'Tokens Saved':<15} {'Avg':<10} {'Success':<10} {'Last Used':<20}"
    )
    output.append("-" * 120)

    for skill, m in sorted_skills:
        last_used = m["last_activated"] or "Never"
        if m["last_activated"]:
            # Format datetime to shorter form
            try:
                dt = datetime.fromisoformat(m["last_activated"].replace("Z", "+00:00"))
                last_used = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, AttributeError):
                pass

        output.append(
            f"{skill:<40} {m['activation_count']:<8} "
            f"{m['total_tokens_saved']:>14,} {m['avg_tokens']:>9,} "
            f"{m['success_rate']:>9.1%} {last_used:<20}"
        )

    # Summary statistics
    total_activations = sum(m["activation_count"] for m in metrics.values())
    total_tokens = sum(m["total_tokens_saved"] for m in metrics.values())

    output.append("-" * 120)
    output.append(f"\nTotal: {len(metrics)} skills, {total_activations} activations, {total_tokens:,} tokens saved")

    return "\n".join(output)
