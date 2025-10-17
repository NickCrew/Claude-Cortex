"""Skill metrics tracking and reporting."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def get_metrics_path() -> Path:
    """Get metrics storage path (~/.claude/.metrics/skills/)."""
    claude_home = os.environ.get("CLAUDE_CTX_HOME") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if claude_home:
        base = Path(claude_home)
    else:
        base = Path.home() / ".claude"

    metrics_dir = base / ".metrics" / "skills"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


def load_metrics() -> Dict:
    """Load metrics from stats.json."""
    metrics_path = get_metrics_path() / "stats.json"

    if not metrics_path.exists():
        return {"skills": {}}

    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"skills": {}}


def _save_metrics(metrics: Dict) -> None:
    """Save metrics to stats.json."""
    metrics_path = get_metrics_path() / "stats.json"

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


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


def get_skill_metrics(skill_name: str) -> Optional[Dict]:
    """Get metrics for a specific skill.

    Args:
        skill_name: Name of the skill

    Returns:
        Dictionary of metrics or None if skill has no metrics
    """
    metrics = load_metrics()
    return metrics.get("skills", {}).get(skill_name)


def get_all_metrics() -> Dict:
    """Get all skill metrics.

    Returns:
        Dictionary mapping skill names to their metrics
    """
    metrics = load_metrics()
    return metrics.get("skills", {})


def reset_metrics() -> None:
    """Reset all metrics."""
    metrics_path = get_metrics_path() / "stats.json"

    if metrics_path.exists():
        metrics_path.unlink()


def format_metrics(metrics: Dict, skill_name: Optional[str] = None) -> str:
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
