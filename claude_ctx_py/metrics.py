"""Skill metrics tracking and reporting."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.base import _resolve_claude_dir
from .exceptions import (
    InvalidMetricsDataError,
    MetricsFileError,
)
from .error_utils import safe_load_json, safe_save_json, ensure_directory


def get_metrics_path() -> Path:
    """Get metrics storage path (~/.cortex/.metrics/skills/).

    Raises:
        MetricsFileError: If metrics directory cannot be created
    """
    claude_dir = _resolve_claude_dir()
    metrics_dir = claude_dir / ".metrics" / "skills"
    try:
        ensure_directory(metrics_dir, purpose="metrics storage")
    except Exception as exc:
        raise MetricsFileError(str(metrics_dir), "create directory", str(exc)) from exc

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
            str(metrics_path), "write", f"Failed to save metrics: {exc}"
        ) from exc


def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format with trailing Z."""

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _activations_path() -> Path:
    """Return the path to the detailed activations log."""

    return get_metrics_path() / "activations.json"


def _load_activation_data() -> Dict[str, Any]:
    """Load activation log contents, returning an empty structure on error."""

    path = _activations_path()
    if not path.exists():
        return {"activations": []}

    try:
        data = safe_load_json(path)
    except (InvalidMetricsDataError, FileNotFoundError):
        return {"activations": []}

    activations = data.get("activations")
    if not isinstance(activations, list):
        data["activations"] = []
    return data


def _save_activation_data(data: Dict[str, Any]) -> None:
    """Persist activation log data to disk."""

    path = _activations_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_save_json(path, data)


def _append_activation_record(record: Dict[str, Any]) -> None:
    """Append a single activation record, trimming history to 1000 entries."""

    data = _load_activation_data()
    activations = data.setdefault("activations", [])
    activations.append(record)
    if len(activations) > 1000:
        data["activations"] = activations[-1000:]
    _save_activation_data(data)


def record_activation(
    skill_name: str,
    tokens_used: int,
    success: bool,
    *,
    context: Optional[Dict[str, Any]] = None,
    log_detail: bool = True,
) -> None:
    """Record a skill activation.

    Args:
        skill_name: Name of the skill being activated
        tokens_used: Number of tokens used/saved by the skill
        success: Whether the activation was successful
        context: Optional metadata about the activation (agent, task_type, etc.)
        log_detail: Whether to append this activation to the detailed log
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
            "success_rate": 0.0,
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
    skill_metrics["last_activated"] = _utc_now_iso()

    # Update success rate
    # Track successes based on previous rate and new result
    previous_successes = int(
        skill_metrics["success_rate"] * (skill_metrics["activation_count"] - 1)
    )
    new_successes = previous_successes + (1 if success else 0)
    skill_metrics["success_rate"] = new_successes / skill_metrics["activation_count"]

    _save_metrics(metrics)

    if log_detail:
        activation_context = context or {}
        activation_record = {
            "activation_id": str(uuid.uuid4()),
            "skill_name": skill_name,
            "timestamp": _utc_now_iso(),
            "context": {
                "agent": activation_context.get("agent", "unknown"),
                "task_type": activation_context.get("task_type", "unknown"),
                "project_type": activation_context.get("project_type", "unknown"),
                "co_activated_skills": activation_context.get(
                    "co_activated_skills", []
                ),
            },
            "metrics": {
                "tokens_loaded": activation_context.get("tokens_loaded", 0),
                "tokens_saved": tokens_used,
                "duration_ms": activation_context.get("duration_ms", 0),
                "success": success,
            },
            "effectiveness": {
                "relevance_score": activation_context.get("relevance_score", 0.8),
                "completion_improvement": activation_context.get(
                    "completion_improvement", 0.0
                ),
                "user_satisfaction": activation_context.get("user_satisfaction", 3),
            },
        }
        _append_activation_record(activation_record)


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


def record_detailed_activation(skill_name: str, context: Dict[str, Any]) -> None:
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
    activation_record = {
        "activation_id": str(uuid.uuid4()),
        "skill_name": skill_name,
        "timestamp": _utc_now_iso(),
        "context": {
            "agent": context.get("agent", "unknown"),
            "task_type": context.get("task_type", "unknown"),
            "project_type": context.get("project_type", "unknown"),
            "co_activated_skills": context.get("co_activated_skills", []),
        },
        "metrics": {
            "tokens_loaded": context.get("tokens_loaded", 0),
            "tokens_saved": context.get("tokens_saved", 0),
            "duration_ms": context.get("duration_ms", 0),
            "success": context.get("success", True),
        },
        "effectiveness": {
            "relevance_score": context.get("relevance_score", 0.8),
            "completion_improvement": context.get("completion_improvement", 0.0),
            "user_satisfaction": context.get("user_satisfaction", 3),
        },
    }

    _append_activation_record(activation_record)

    # Also update the summary metrics
    tokens_saved = context.get("tokens_saved", 0)
    success = context.get("success", True)
    record_activation(
        skill_name,
        tokens_saved,
        success,
        context=context,
        log_detail=False,
    )


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

    claude_dir = _resolve_claude_dir()
    return analytics.get_impact_report(skill_name, claude_dir)


def generate_analytics_report(output_format: str = "text") -> str:
    """Generate comprehensive analytics report.

    Args:
        output_format: Format of report ('text' or 'json')

    Returns:
        Formatted report string
    """
    from . import analytics

    claude_dir = _resolve_claude_dir()
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
        metrics.items(), key=lambda x: x[1]["activation_count"], reverse=True
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
    output.append(
        f"\nTotal: {len(metrics)} skills, {total_activations} activations, {total_tokens:,} tokens saved"
    )

    return "\n".join(output)
