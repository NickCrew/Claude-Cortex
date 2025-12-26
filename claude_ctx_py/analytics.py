"""Advanced analytics and reporting for skill metrics."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from .exceptions import ExportError, InvalidMetricsDataError, MetricsFileError
from .error_utils import safe_load_json, safe_save_json, safe_write_file

MetricRow = Dict[str, Any]
MetricsMap = Mapping[str, MetricRow]

# Claude model pricing (per million tokens) - Updated for accuracy
CLAUDE_PRICING: Dict[str, Dict[str, Union[float, str]]] = {
    "claude-opus-4-20250514": {
        "input": 15.0,  # $15/MTok
        "output": 75.0,  # $75/MTok
        "name": "Opus 4",
    },
    "claude-sonnet-4-20250514": {
        "input": 3.0,  # $3/MTok
        "output": 15.0,  # $15/MTok
        "name": "Sonnet 4",
    },
    "claude-haiku-4-20250514": {
        "input": 0.25,  # $0.25/MTok
        "output": 1.25,  # $1.25/MTok
        "name": "Haiku 4",
    },
}

# Deprecated: Legacy token cost (kept for backward compatibility)
# Use calculate_llm_cost() for accurate model-specific pricing
TOKEN_COST_PER_1K = 0.003  # ~$3/MTok for Sonnet


def calculate_llm_cost(
    model: str, input_tokens: int, output_tokens: int
) -> Dict[str, Any]:
    """Calculate actual LLM API cost for a request.

    Args:
        model: Model name (e.g., 'claude-sonnet-4-20250514')
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Dictionary with cost breakdown:
        - input_cost: Cost for input tokens
        - output_cost: Cost for output tokens
        - total_cost: Total cost in USD
        - model_name: Human-readable model name
        - savings_vs_sonnet: Cost savings compared to Sonnet (if using Haiku)
    """
    pricing = CLAUDE_PRICING.get(model, CLAUDE_PRICING["claude-sonnet-4-20250514"])

    input_cost = (input_tokens / 1_000_000) * float(pricing["input"])
    output_cost = (output_tokens / 1_000_000) * float(pricing["output"])
    total_cost = input_cost + output_cost

    result = {
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "model_name": str(pricing["name"]),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }

    # Calculate savings if using a cheaper model
    if model != "claude-sonnet-4-20250514":
        sonnet_pricing = CLAUDE_PRICING["claude-sonnet-4-20250514"]
        sonnet_cost = (
            (input_tokens / 1_000_000) * float(sonnet_pricing["input"])
            + (output_tokens / 1_000_000) * float(sonnet_pricing["output"])
        )
        savings = sonnet_cost - total_cost
        result["savings_vs_sonnet"] = round(savings, 6)
        result["savings_percentage"] = (
            round((savings / sonnet_cost) * 100, 1) if sonnet_cost > 0 else 0.0
        )

    return result


def get_effectiveness_score(skill_name: str, all_metrics: MetricsMap) -> float:
    """Calculate effectiveness score for a skill (0-100).

    Scoring algorithm:
    - Success rate: 40% weight
    - Token efficiency: 30% weight
    - Usage frequency: 20% weight
    - Recency: 10% weight

    Args:
        skill_name: Name of the skill to score
        all_metrics: Dictionary of all skill metrics

    Returns:
        Effectiveness score from 0 to 100
    """
    if skill_name not in all_metrics:
        return 0.0

    skill = all_metrics[skill_name]

    # Success rate component (40%)
    success_score = skill.get("success_rate", 0.0) * 40

    # Token efficiency component (30%)
    avg_tokens = skill.get("avg_tokens", 0)
    if avg_tokens > 0:
        # Normalize token efficiency: more tokens saved = higher score
        # Cap at 10K tokens for normalization
        token_efficiency = min(avg_tokens / 10000, 1.0) * 30
    else:
        token_efficiency = 0.0

    # Usage frequency component (20%)
    activation_count = skill.get("activation_count", 0)
    if all_metrics:
        max_activations = max(
            (s.get("activation_count", 0) for s in all_metrics.values()), default=1
        )
        usage_score = (
            (activation_count / max_activations) * 20 if max_activations > 0 else 0
        )
    else:
        usage_score = 0.0

    # Recency component (10%)
    last_activated = skill.get("last_activated")
    if last_activated:
        try:
            last_time = datetime.fromisoformat(last_activated.replace("Z", "+00:00"))
            days_ago = (datetime.now(last_time.tzinfo) - last_time).days
            # Recent use scores higher: exponential decay over 30 days
            recency_score = math.exp(-days_ago / 30) * 10
        except (ValueError, AttributeError):
            recency_score = 0.0
    else:
        recency_score = 0.0

    total_score = success_score + token_efficiency + usage_score + recency_score
    return float(round(total_score, 2))


def calculate_roi(skill_name: str, claude_dir: Path) -> Dict[str, float | int]:
    """Calculate return on investment for a skill.

    ROI calculation:
    - Token cost saved = total_tokens_saved * TOKEN_COST_PER_1K / 1000
    - Time saved (estimated) = activations * avg_time_per_activation
    - Efficiency ratio = tokens_saved / tokens_loaded

    Args:
        skill_name: Name of the skill
        claude_dir: Path to Claude configuration directory

    Returns:
        Dictionary containing ROI metrics:
        - cost_saved: Dollar amount saved
        - tokens_saved: Total tokens saved
        - activations: Number of times used
        - cost_per_activation: Average cost saved per use
        - efficiency_ratio: Ratio of tokens saved to loaded
    """
    from . import metrics as metrics_module

    skill_metrics = metrics_module.get_skill_metrics(skill_name)
    if not skill_metrics:
        return {
            "cost_saved": 0.0,
            "tokens_saved": 0,
            "activations": 0,
            "cost_per_activation": 0.0,
            "efficiency_ratio": 0.0,
        }

    total_tokens = skill_metrics.get("total_tokens_saved", 0)
    activations = skill_metrics.get("activation_count", 0)

    # Calculate cost savings
    cost_saved = (total_tokens / 1000) * TOKEN_COST_PER_1K

    # Calculate per-activation metrics
    cost_per_activation = cost_saved / activations if activations > 0 else 0.0

    # Try to calculate efficiency ratio from detailed activations
    efficiency_ratio = _calculate_efficiency_ratio(skill_name, claude_dir)

    return {
        "cost_saved": round(cost_saved, 4),
        "tokens_saved": total_tokens,
        "activations": activations,
        "cost_per_activation": round(cost_per_activation, 4),
        "efficiency_ratio": round(efficiency_ratio, 2),
    }


def _calculate_efficiency_ratio(skill_name: str, claude_dir: Path) -> float:
    """Calculate efficiency ratio from detailed activation logs.

    Args:
        skill_name: Name of the skill
        claude_dir: Path to Claude configuration directory

    Returns:
        Efficiency ratio (tokens_saved / tokens_loaded)
    """
    metrics_path = claude_dir / ".metrics" / "skills"
    activations_file = metrics_path / "activations.json"

    if not activations_file.exists():
        return 1.0  # Default assumption

    try:
        activations_data = safe_load_json(activations_file)

        total_loaded = 0
        total_saved = 0

        for activation in activations_data.get("activations", []):
            if activation.get("skill_name") == skill_name:
                metrics = activation.get("metrics", {})
                total_loaded += metrics.get("tokens_loaded", 0)
                total_saved += metrics.get("tokens_saved", 0)

        if total_loaded > 0:
            return total_saved / total_loaded
        return 1.0

    except (InvalidMetricsDataError, FileNotFoundError):
        return 1.0


def get_trending_skills(days: int, claude_dir: Path) -> List[MetricRow]:
    """Get trending skills based on recent activity.

    Args:
        days: Number of days to look back
        claude_dir: Path to Claude configuration directory

    Returns:
        List of dictionaries containing skill name and trend metrics
    """
    metrics_path = claude_dir / ".metrics" / "skills"
    activations_file = metrics_path / "activations.json"

    if not activations_file.exists():
        return []

    try:
        activations_data = safe_load_json(activations_file)

        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        skill_counts: Dict[str, int] = defaultdict(int)
        skill_tokens: Dict[str, int] = defaultdict(int)

        for activation in activations_data.get("activations", []):
            try:
                timestamp = datetime.fromisoformat(
                    activation["timestamp"].replace("Z", "+00:00")
                )
                if timestamp.replace(tzinfo=None) >= cutoff_date:
                    skill = activation["skill_name"]
                    skill_counts[skill] += 1
                    skill_tokens[skill] += activation.get("metrics", {}).get(
                        "tokens_saved", 0
                    )
            except (ValueError, KeyError):
                continue

        # Create trending list sorted by activation count
        trending: List[MetricRow] = []
        for skill, count in skill_counts.items():
            tokens_saved = skill_tokens[skill]
            efficiency = (tokens_saved / 1000) if tokens_saved else 1.0
            trend_score = count * efficiency
            trending.append(
                {
                    "skill": skill,
                    "activations": count,
                    "tokens_saved": tokens_saved,
                    "trend_score": trend_score,
                }
            )

        # Sort by trend score (activations * tokens efficiency)
        trending.sort(key=lambda item: float(item["trend_score"]), reverse=True)

        return trending

    except (InvalidMetricsDataError, FileNotFoundError):
        return []


def get_recommendations(
    usage_pattern: Mapping[str, Any], claude_dir: Path
) -> List[str]:
    """Generate skill usage recommendations.

    Analyzes usage patterns to recommend:
    - Underutilized high-value skills
    - Skills with low success rates that need review
    - Skills that are frequently co-activated
    - Skills that could be combined

    Args:
        usage_pattern: Dictionary of current usage statistics
        claude_dir: Path to Claude configuration directory

    Returns:
        List of recommendation strings
    """
    from . import metrics as metrics_module

    recommendations: List[str] = []
    all_metrics: Dict[str, Dict[str, Any]] = metrics_module.get_all_metrics()

    if not all_metrics:
        return ["No metrics available yet. Use skills to generate recommendations."]

    # Find underutilized high-value skills
    for skill_name, metrics in all_metrics.items():
        effectiveness = get_effectiveness_score(skill_name, all_metrics)
        activation_count = metrics.get("activation_count", 0)

        # High effectiveness but low usage
        if effectiveness > 70 and activation_count < 5:
            recommendations.append(
                f"Consider using '{skill_name}' more often "
                f"(effectiveness: {effectiveness:.1f}/100, only {activation_count} uses)"
            )

    # Find skills with low success rates
    for skill_name, metrics in all_metrics.items():
        success_rate = metrics.get("success_rate", 0.0)
        if success_rate < 0.6 and metrics.get("activation_count", 0) >= 3:
            recommendations.append(
                f"Review '{skill_name}' - low success rate "
                f"({success_rate:.1%}). May need updates or refinement."
            )

    # Find stale skills
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
    for skill_name, metrics in all_metrics.items():
        last_activated = metrics.get("last_activated")
        if last_activated:
            try:
                last_time = datetime.fromisoformat(
                    last_activated.replace("Z", "+00:00")
                )
                if last_time.replace(tzinfo=None) < cutoff:
                    recommendations.append(
                        f"'{skill_name}' hasn't been used in 30+ days. "
                        "Consider archiving if no longer needed."
                    )
            except (ValueError, AttributeError):
                pass

    # Analyze co-activation patterns
    correlations = get_correlation_matrix(all_metrics)
    for skill, correlated in correlations.items():
        for other_skill, correlation in correlated.items():
            if correlation > 0.7 and skill < other_skill:  # Avoid duplicates
                recommendations.append(
                    f"'{skill}' and '{other_skill}' are frequently used together "
                    f"(correlation: {correlation:.2f}). Consider creating a combined skill."
                )

    if not recommendations:
        recommendations.append(
            "All skills are being used effectively! Keep up the good work."
        )

    return recommendations[:10]  # Limit to top 10 recommendations


def export_analytics(format: str, claude_dir: Path) -> str:
    """Export analytics data in specified format.

    Args:
        format: Export format ('json', 'csv', or 'text')
        claude_dir: Path to Claude configuration directory

    Returns:
        Path to exported file

    Raises:
        ExportError: If format is not supported or export fails
    """
    from . import metrics as metrics_module

    all_metrics = metrics_module.get_all_metrics()

    if format not in ["json", "csv", "text"]:
        raise ExportError(format, reason="Supported formats: json, csv, text")

    # Create exports directory
    exports_dir = claude_dir / ".metrics" / "exports"
    try:
        exports_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExportError(
            format, reason=f"Failed to create exports directory: {exc}"
        ) from exc

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"analytics_{timestamp}.{format}"
    filepath = exports_dir / filename

    try:
        if format == "json":
            _export_json(all_metrics, filepath, claude_dir)
        elif format == "csv":
            _export_csv(all_metrics, filepath, claude_dir)
        elif format == "text":
            _export_text(all_metrics, filepath, claude_dir)
    except Exception as exc:
        raise ExportError(format, reason=f"Export operation failed: {exc}") from exc

    return str(filepath)


def _export_json(all_metrics: MetricsMap, filepath: Path, claude_dir: Path) -> None:
    """Export metrics as JSON."""
    skills_data: Dict[str, Dict[str, Any]] = {}
    export_data: Dict[str, Any] = {
        "exported_at": datetime.now(timezone.utc).isoformat() + "Z",
        "skills": skills_data,
    }

    for skill_name, metrics in all_metrics.items():
        roi = calculate_roi(skill_name, claude_dir)
        effectiveness = get_effectiveness_score(skill_name, all_metrics)

        skills_data[skill_name] = {
            "metrics": metrics,
            "roi": roi,
            "effectiveness_score": effectiveness,
        }

    safe_save_json(filepath, export_data)


def _export_csv(all_metrics: MetricsMap, filepath: Path, claude_dir: Path) -> None:
    """Export metrics as CSV."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "Skill Name",
                "Activation Count",
                "Total Tokens Saved",
                "Avg Tokens",
                "Success Rate",
                "Last Activated",
                "Cost Saved ($)",
                "Effectiveness Score",
            ]
        )

        # Data rows
        for skill_name, metrics in all_metrics.items():
            roi = calculate_roi(skill_name, claude_dir)
            effectiveness = get_effectiveness_score(skill_name, all_metrics)

            writer.writerow(
                [
                    skill_name,
                    metrics.get("activation_count", 0),
                    metrics.get("total_tokens_saved", 0),
                    metrics.get("avg_tokens", 0),
                    f"{metrics.get('success_rate', 0.0):.2%}",
                    metrics.get("last_activated", "Never"),
                    f"${roi['cost_saved']:.4f}",
                    f"{effectiveness:.2f}",
                ]
            )


def _export_text(all_metrics: MetricsMap, filepath: Path, claude_dir: Path) -> None:
    """Export metrics as formatted text."""
    from . import metrics as metrics_module

    lines: List[str] = []
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SKILL ANALYTICS REPORT\n")
        f.write(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("=" * 80 + "\n\n")

        # Summary statistics
        total_skills = len(all_metrics)
        total_activations = sum(
            m.get("activation_count", 0) for m in all_metrics.values()
        )
        total_tokens = sum(m.get("total_tokens_saved", 0) for m in all_metrics.values())
        total_cost_saved = (total_tokens / 1000) * TOKEN_COST_PER_1K

        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Skills:       {total_skills}\n")
        f.write(f"Total Activations:  {total_activations}\n")
        f.write(f"Total Tokens Saved: {total_tokens:,}\n")
        f.write(f"Total Cost Saved:   ${total_cost_saved:.4f}\n")
        f.write("\n")

        # Individual skill details
        f.write("SKILL DETAILS\n")
        f.write("-" * 80 + "\n\n")

        sorted_skills = sorted(
            all_metrics.items(),
            key=lambda x: get_effectiveness_score(x[0], all_metrics),
            reverse=True,
        )

        for skill_name, metrics in sorted_skills:
            roi = calculate_roi(skill_name, claude_dir)
            effectiveness = get_effectiveness_score(skill_name, all_metrics)

            f.write(f"Skill: {skill_name}\n")
            f.write(f"  Effectiveness Score: {effectiveness:.2f}/100\n")
            f.write(f"  Activations:         {metrics.get('activation_count', 0)}\n")
            f.write(
                f"  Tokens Saved:        {metrics.get('total_tokens_saved', 0):,}\n"
            )
            f.write(f"  Avg Tokens/Use:      {metrics.get('avg_tokens', 0):,}\n")
            f.write(f"  Success Rate:        {metrics.get('success_rate', 0.0):.1%}\n")
            f.write(f"  Cost Saved:          ${roi['cost_saved']:.4f}\n")
            f.write(
                f"  Last Used:           {metrics.get('last_activated', 'Never')}\n"
            )
            f.write("\n")


def visualize_metrics(metric: str, all_metrics: MetricsMap) -> str:
    """Generate ASCII bar chart visualization of metrics.

    Args:
        metric: Metric to visualize ('activations', 'tokens', 'effectiveness', 'success_rate')
        all_metrics: Dictionary of all skill metrics

    Returns:
        ASCII bar chart string

    Raises:
        ValueError: If metric is not supported
    """
    if not all_metrics:
        return "No metrics available to visualize."

    supported_metrics = ["activations", "tokens", "effectiveness", "success_rate"]
    if metric not in supported_metrics:
        raise ValueError(
            f"Unsupported metric: {metric}. Use one of {supported_metrics}"
        )

    # Get data for the metric
    data = []
    for skill_name, metrics in all_metrics.items():
        if metric == "activations":
            value = metrics.get("activation_count", 0)
        elif metric == "tokens":
            value = metrics.get("total_tokens_saved", 0)
        elif metric == "effectiveness":
            value = get_effectiveness_score(skill_name, all_metrics)
        elif metric == "success_rate":
            value = metrics.get("success_rate", 0.0) * 100

        data.append((skill_name, value))

    # Sort by value
    data.sort(key=lambda x: x[1], reverse=True)

    # Limit to top 15 for readability
    data = data[:15]

    if not data:
        return "No data available for this metric."

    # Find max value for scaling
    max_value = max(value for _, value in data)
    if max_value == 0:
        return "All values are zero for this metric."

    # Build chart
    chart_width = 50
    lines = []

    # Title
    metric_titles = {
        "activations": "Skill Activations",
        "tokens": "Tokens Saved",
        "effectiveness": "Effectiveness Score",
        "success_rate": "Success Rate (%)",
    }
    lines.append(f"\n{metric_titles[metric]}\n")
    lines.append("=" * 70 + "\n")

    # Bars
    max_label_width = max(len(name) for name, _ in data)

    for skill_name, value in data:
        # Calculate bar length
        bar_length = int((value / max_value) * chart_width)
        bar = "█" * bar_length

        # Format value based on metric type
        if metric == "tokens":
            value_str = f"{value:,}"
        elif metric in ["effectiveness", "success_rate"]:
            value_str = f"{value:.1f}"
        else:
            value_str = str(int(value))

        # Create line
        label = skill_name.ljust(max_label_width)
        line = f"{label} | {bar} {value_str}\n"
        lines.append(line)

    return "".join(lines)


def get_correlation_matrix(all_metrics: MetricsMap) -> Dict[str, Dict[str, float]]:
    """Calculate skill co-activation correlation matrix.

    Analyzes detailed activation logs to find skills that are frequently
    used together in the same session or timeframe.

    Args:
        all_metrics: Dictionary of all skill metrics

    Returns:
        Dictionary mapping skill names to correlation scores with other skills
    """
    from . import metrics as metrics_module

    metrics_path = metrics_module.get_metrics_path()
    activations_file = metrics_path / "activations.json"

    if not activations_file.exists():
        return {}

    try:
        activations_data = safe_load_json(activations_file)

        # Track co-activations
        co_activations: Dict[Tuple[str, str], int] = defaultdict(int)
        skill_counts: Dict[str, int] = defaultdict(int)

        for activation in activations_data.get("activations", []):
            skill = activation["skill_name"]
            skill_counts[skill] += 1

            # Get co-activated skills
            co_activated = activation.get("context", {}).get("co_activated_skills", [])
            for other_skill in co_activated:
                # Create ordered pair
                pair = tuple(sorted([skill, other_skill]))
                co_activations[pair] += 1

        # Calculate correlation scores
        correlations: Dict[str, Dict[str, float]] = defaultdict(dict)

        for (skill1, skill2), co_count in co_activations.items():
            # Jaccard similarity: intersection / union
            count1 = skill_counts[skill1]
            count2 = skill_counts[skill2]
            union = count1 + count2 - co_count

            if union > 0:
                correlation = co_count / union
                correlations[skill1][skill2] = correlation
                correlations[skill2][skill1] = correlation

        return dict(correlations)

    except (InvalidMetricsDataError, FileNotFoundError):
        return {}


def get_impact_report(skill_name: str, claude_dir: Path) -> Dict[str, Any]:
    """Generate comprehensive impact analysis for a skill.

    Args:
        skill_name: Name of the skill
        claude_dir: Path to Claude configuration directory

    Returns:
        Dictionary containing comprehensive impact metrics:
        - basic_metrics: Core usage statistics
        - roi: Return on investment calculations
        - effectiveness: Effectiveness score and components
        - trends: Usage trends over time
        - correlations: Related skills
    """
    from . import metrics as metrics_module

    all_metrics = metrics_module.get_all_metrics()
    skill_metrics = metrics_module.get_skill_metrics(skill_name)

    if not skill_metrics:
        return {
            "error": f"No metrics found for skill: {skill_name}",
            "skill_name": skill_name,
        }

    # Basic metrics
    basic_metrics = {
        "activation_count": skill_metrics.get("activation_count", 0),
        "total_tokens_saved": skill_metrics.get("total_tokens_saved", 0),
        "avg_tokens": skill_metrics.get("avg_tokens", 0),
        "success_rate": skill_metrics.get("success_rate", 0.0),
        "last_activated": skill_metrics.get("last_activated"),
    }

    # ROI calculations
    roi = calculate_roi(skill_name, claude_dir)

    # Effectiveness score
    effectiveness = get_effectiveness_score(skill_name, all_metrics)

    # Trends (last 7, 30, 90 days)
    trends = {
        "7_days": _count_activations_in_period(skill_name, 7, claude_dir),
        "30_days": _count_activations_in_period(skill_name, 30, claude_dir),
        "90_days": _count_activations_in_period(skill_name, 90, claude_dir),
    }

    # Correlations
    correlation_matrix = get_correlation_matrix(all_metrics)
    correlations = correlation_matrix.get(skill_name, {})

    # Sort correlations by score
    top_correlations = sorted(correlations.items(), key=lambda x: x[1], reverse=True)[
        :5
    ]

    return {
        "skill_name": skill_name,
        "basic_metrics": basic_metrics,
        "roi": roi,
        "effectiveness_score": effectiveness,
        "trends": trends,
        "top_correlations": dict(top_correlations),
    }


def _count_activations_in_period(skill_name: str, days: int, claude_dir: Path) -> int:
    """Count activations for a skill within a time period.

    Args:
        skill_name: Name of the skill
        days: Number of days to look back
        claude_dir: Path to Claude configuration directory

    Returns:
        Number of activations in the period
    """
    metrics_path = claude_dir / ".metrics" / "skills"
    activations_file = metrics_path / "activations.json"

    if not activations_file.exists():
        return 0

    try:
        activations_data = safe_load_json(activations_file)

        cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        count = 0

        for activation in activations_data.get("activations", []):
            if activation.get("skill_name") == skill_name:
                try:
                    timestamp = datetime.fromisoformat(
                        activation["timestamp"].replace("Z", "+00:00")
                    )
                    if timestamp.replace(tzinfo=None) >= cutoff_date:
                        count += 1
                except (ValueError, KeyError):
                    continue

        return count

    except (InvalidMetricsDataError, FileNotFoundError):
        return 0


def generate_analytics_report(output_format: str, claude_dir: Path) -> str:
    """Generate comprehensive analytics report.

    Args:
        output_format: Format of report ('text' or 'json')
        claude_dir: Path to Claude configuration directory

    Returns:
        Formatted report string

    Raises:
        ValueError: If output_format is not supported
    """
    from . import metrics as metrics_module

    if output_format not in ["text", "json"]:
        raise ValueError(f"Unsupported format: {output_format}. Use 'text' or 'json'")

    all_metrics = metrics_module.get_all_metrics()

    if not all_metrics:
        return "No metrics available. Use skills to generate analytics."

    if output_format == "json":
        return _generate_json_report(all_metrics, claude_dir)
    else:
        return _generate_text_report(all_metrics, claude_dir)


def _generate_json_report(all_metrics: MetricsMap, claude_dir: Path) -> str:
    """Generate JSON format analytics report."""
    skills_section: Dict[str, Any] = {}
    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "summary": {
            "total_skills": len(all_metrics),
            "total_activations": sum(
                m.get("activation_count", 0) for m in all_metrics.values()
            ),
            "total_tokens_saved": sum(
                m.get("total_tokens_saved", 0) for m in all_metrics.values()
            ),
            "total_cost_saved": sum(
                calculate_roi(skill, claude_dir)["cost_saved"]
                for skill in all_metrics.keys()
            ),
        },
        "skills": skills_section,
        "trending_7_days": get_trending_skills(7, claude_dir),
        "trending_30_days": get_trending_skills(30, claude_dir),
        "recommendations": get_recommendations({}, claude_dir),
    }

    # Add detailed skill data
    for skill_name in all_metrics.keys():
        skills_section[skill_name] = get_impact_report(skill_name, claude_dir)

    return json.dumps(report, indent=2)


def _generate_text_report(all_metrics: MetricsMap, claude_dir: Path) -> str:
    """Generate text format analytics report."""
    lines: List[str] = []

    # Header
    lines.append("\n" + "=" * 80)
    lines.append("COMPREHENSIVE ANALYTICS REPORT")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("=" * 80 + "\n")

    # Summary statistics
    total_skills = len(all_metrics)
    total_activations = sum(m.get("activation_count", 0) for m in all_metrics.values())
    total_tokens = sum(m.get("total_tokens_saved", 0) for m in all_metrics.values())
    total_cost_saved = sum(
        calculate_roi(skill, claude_dir)["cost_saved"] for skill in all_metrics.keys()
    )

    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Skills:       {total_skills}")
    lines.append(f"Total Activations:  {total_activations:,}")
    lines.append(f"Total Tokens Saved: {total_tokens:,}")
    lines.append(f"Total Cost Saved:   ${total_cost_saved:.4f}")
    lines.append("")

    # Top performers
    lines.append("TOP PERFORMING SKILLS (by Effectiveness)")
    lines.append("-" * 80)

    sorted_by_effectiveness = sorted(
        all_metrics.keys(),
        key=lambda s: get_effectiveness_score(s, all_metrics),
        reverse=True,
    )[:5]

    for i, skill_name in enumerate(sorted_by_effectiveness, 1):
        effectiveness = get_effectiveness_score(skill_name, all_metrics)
        roi = calculate_roi(skill_name, claude_dir)
        lines.append(
            f"{i}. {skill_name} - "
            f"Score: {effectiveness:.1f}/100, "
            f"Cost Saved: ${roi['cost_saved']:.4f}"
        )

    lines.append("")

    # Trending skills
    lines.append("TRENDING SKILLS (Last 7 Days)")
    lines.append("-" * 80)

    trending = get_trending_skills(7, claude_dir)
    if trending:
        for i, trend in enumerate(trending[:5], 1):
            lines.append(
                f"{i}. {trend['skill']} - "
                f"{trend['activations']} uses, "
                f"{trend['tokens_saved']:,} tokens saved"
            )
    else:
        lines.append("No activity in the last 7 days.")

    lines.append("")

    # Recommendations
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)

    recommendations = get_recommendations({}, claude_dir)
    for i, recommendation in enumerate(recommendations[:5], 1):
        lines.append(f"{i}. {recommendation}")

    lines.append("")

    # Visualizations
    lines.append("ACTIVATION VISUALIZATION")
    lines.append("-" * 80)
    lines.append(visualize_metrics("activations", all_metrics))

    lines.append("\nEFFECTIVENESS VISUALIZATION")
    lines.append("-" * 80)
    lines.append(visualize_metrics("effectiveness", all_metrics))

    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)

    return "\n".join(lines)
