"""Skill management functions."""

from __future__ import annotations


import builtins
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple

# Import from base module
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    NC,
    _color,
    _extract_front_matter,
    _extract_scalar_from_paths,
    _resolve_claude_dir,
    _tokenize_front_matter,
)


def list_skills(home: Path | None = None) -> str:
    """List all available skills."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skills_dir.is_dir():
        return "No skills directory found."

    skills: List[Tuple[str, str]] = []

    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue

        skill_file = skill_path / "SKILL.md"
        if not skill_file.is_file():
            continue

        skill_name = skill_path.name

        # Extract description from frontmatter
        try:
            content = skill_file.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)
            if front_matter:
                front_lines = front_matter.strip().splitlines()
                tokens = _tokenize_front_matter(front_lines)
                description = (
                    _extract_scalar_from_paths(tokens, (("description",),))
                    or "No description"
                )
            else:
                description = "No description"
        except Exception:
            description = "Error reading skill"

        skills.append((skill_name, description))

    if not skills:
        return "No skills found."

    lines: List[str] = [_color("Available skills:", BLUE)]

    # Find max skill name length for alignment
    max_name_len = max(len(name) for name, _ in skills) if skills else 0

    for skill_name, description in skills:
        # Truncate description if too long
        max_desc_len = 80
        if len(description) > max_desc_len:
            description = description[: max_desc_len - 3] + "..."

        lines.append(
            f"  {_color(skill_name.ljust(max_name_len), GREEN)}  {description}"
        )

    return "\n".join(lines)


def skill_info(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Show detailed information about a skill."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills info <skill_name>"

    skill_path = skills_dir / skill / "SKILL.md"

    if not skill_path.is_file():
        return 1, _color(f"Skill '{skill}' not found", RED)

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as exc:
        return 1, _color(f"Error reading skill: {exc}", RED)

    # Extract frontmatter
    front_matter = _extract_front_matter(content)
    if not front_matter:
        return 1, _color(f"Skill '{skill}' has no valid frontmatter", RED)

    lines = front_matter.strip().splitlines()
    tokens = _tokenize_front_matter(lines)

    skill_name = _extract_scalar_from_paths(tokens, (("name",),)) or skill
    description = (
        _extract_scalar_from_paths(tokens, (("description",),)) or "No description"
    )

    # Count tokens (rough estimate: words * 1.3)
    word_count = len(content.split())
    token_estimate = int(word_count * 1.3)

    output_lines: List[str] = [
        _color(f"=== Skill: {skill_name} ===", BLUE),
        "",
        _color("Description:", BLUE),
        f"  {description}",
        "",
        _color("Size:", BLUE),
        f"  ~{token_estimate} tokens (estimated)",
        "",
        _color("Location:", BLUE),
        f"  {skill_path}",
    ]

    return 0, "\n".join(output_lines)


def skill_versions(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Show version information for a skill.

    Args:
        skill: Name of the skill
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import versioner

    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills versions <skill_name>"

    skill_path = skills_dir / skill / "SKILL.md"

    if not skill_path.is_file():
        return 1, _color(f"Skill '{skill}' not found", RED)

    # Get current version from SKILL.md
    try:
        content = skill_path.read_text(encoding="utf-8")
        front_matter = _extract_front_matter(content)
        current_version = "1.0.0"  # Default

        if front_matter:
            lines = front_matter.strip().splitlines()
            tokens = _tokenize_front_matter(lines)
            version = _extract_scalar_from_paths(tokens, (("version",),))
            if version:
                current_version = version
    except Exception as exc:
        return 1, _color(f"Error reading skill: {exc}", RED)

    # Get available versions from versions.yaml
    available_versions = versioner.get_skill_versions(skill, claude_dir)
    latest_version = versioner.get_latest_version(skill, claude_dir)

    # Load compatibility info from versions.yaml
    versions_file = claude_dir / "skills" / "versions.yaml"
    compatibility_info = {}

    if versions_file.is_file():
        try:
            import yaml

            versions_data = (
                yaml.safe_load(versions_file.read_text(encoding="utf-8")) or {}
            )
            skill_data = versions_data.get("skills", {}).get(skill, {})
            compatibility_info = skill_data.get("compatibility", {})
        except Exception:
            pass

    output_lines: List[str] = [
        _color(f"=== Skill Versions: {skill} ===", BLUE),
        "",
        _color("Current version:", BLUE),
        f"  {current_version}",
        "",
        _color("Latest version:", BLUE),
        f"  {latest_version}",
        "",
        _color("Available versions:", BLUE),
    ]

    if available_versions:
        for version in available_versions:
            marker = " (current)" if version == current_version else ""
            marker += " (latest)" if version == latest_version else ""
            output_lines.append(f"  {_color(version, GREEN)}{marker}")

            # Show compatibility info if available
            if version in compatibility_info:
                compat = compatibility_info[version]

                if compat.get("breaking_changes"):
                    output_lines.append(f"    {_color('Breaking changes:', RED)}")
                    for change in compat["breaking_changes"]:
                        output_lines.append(f"      - {change}")

                if compat.get("deprecated"):
                    output_lines.append(f"    {_color('Deprecated:', YELLOW)}")
                    for item in compat["deprecated"]:
                        output_lines.append(f"      - {item}")

                if compat.get("added"):
                    output_lines.append(f"    {_color('Added:', GREEN)}")
                    for item in compat["added"]:
                        output_lines.append(f"      - {item}")
    else:
        output_lines.append("  No version information available")

    output_lines.append("")
    output_lines.append(_color("Usage in agent frontmatter:", BLUE))
    output_lines.append(f"  skills:")
    output_lines.append(f"    - {skill}@{current_version}  # Exact version")
    output_lines.append(
        f"    - {skill}@^{current_version}  # Compatible with {current_version.split('.')[0]}.x"
    )
    output_lines.append(f"    - {skill}@latest  # Always use latest")

    return 0, "\n".join(output_lines)


def skill_validate(*skills: str, home: Path | None = None) -> Tuple[int, str]:
    """Validate skill metadata against required schema."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skills_dir.is_dir():
        return 1, _color("No skills directory found", RED)

    validate_all = skills and skills[0] == "--all"

    if validate_all:
        skill_targets = [
            p.name
            for p in sorted(skills_dir.iterdir())
            if p.is_dir() and (p / "SKILL.md").is_file()
        ]
    elif skills:
        skill_targets = list(skills)
    else:
        skill_targets = [
            p.name
            for p in sorted(skills_dir.iterdir())
            if p.is_dir() and (p / "SKILL.md").is_file()
        ]

    if not skill_targets:
        return 1, _color("No skills to validate", YELLOW)

    results: List[str] = []
    errors: List[str] = []

    for skill_name in skill_targets:
        skill_path = skills_dir / skill_name / "SKILL.md"

        if not skill_path.is_file():
            errors.append(f"  {_color('✗', RED)} {skill_name}: SKILL.md not found")
            continue

        try:
            content = skill_path.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)

            if not front_matter:
                errors.append(f"  {_color('✗', RED)} {skill_name}: Missing frontmatter")
                continue

            lines = front_matter.strip().splitlines()
            tokens = _tokenize_front_matter(lines)

            # Validate required fields
            name = _extract_scalar_from_paths(tokens, (("name",),))
            description = _extract_scalar_from_paths(tokens, (("description",),))

            if not name:
                errors.append(
                    f"  {_color('✗', RED)} {skill_name}: Missing 'name' field"
                )
                continue

            if not description:
                errors.append(
                    f"  {_color('✗', RED)} {skill_name}: Missing 'description' field"
                )
                continue

            if len(description) > 1024:
                errors.append(
                    f"  {_color('⚠', YELLOW)} {skill_name}: Description too long ({len(description)} > 1024 chars)"
                )

            if "Use when" not in description:
                errors.append(
                    f"  {_color('⚠', YELLOW)} {skill_name}: Description missing 'Use when' trigger"
                )

            results.append(f"  {_color('✓', GREEN)} {skill_name}: Valid")

        except Exception as exc:
            errors.append(
                f"  {_color('✗', RED)} {skill_name}: Error reading file: {exc}"
            )

    output_lines: List[str] = [_color("=== Skill Validation ===", BLUE), ""]

    if results:
        output_lines.extend(results)

    if errors:
        if results:
            output_lines.append("")
        output_lines.extend(errors)

    output_lines.append("")
    output_lines.append(f"Validated: {len(results)} passed, {len(errors)} issues")

    exit_code = 0 if not errors else 1
    return exit_code, "\n".join(output_lines)


def skill_analyze(text: str, home: Path | None = None) -> Tuple[int, str]:
    """Analyze text and suggest matching skills based on keywords.

    Args:
        text: Input text to analyze for skill keywords
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import activator

    claude_dir = _resolve_claude_dir(home)

    if not text or not text.strip():
        return 1, _color("Usage:", RED) + " cortex skills analyze <text>"

    try:
        result = activator.suggest_skills(text, claude_dir)
        return 0, result
    except FileNotFoundError as e:
        return 1, _color(f"Error: {e}", RED)
    except Exception as e:
        return 1, _color(f"Error analyzing text: {e}", RED)


def skill_deps(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Show which agents use a specific skill."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"
    deps_file = skills_dir / "dependencies.map"

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills deps <skill_name>"

    if not deps_file.is_file():
        return 1, _color("Dependencies map not found at:", RED) + f" {deps_file}"

    try:
        content = deps_file.read_text(encoding="utf-8")
    except Exception as exc:
        return 1, _color(f"Error reading dependencies map: {exc}", RED)

    # Parse the reverse lookup section
    in_reverse_section = False
    current_skill = None
    agents_for_skill: List[str] = []

    for line in content.splitlines():
        line_stripped = line.strip()

        # Start of reverse lookup section
        if line_stripped == "## Skill → Agents (Reverse Lookup)":
            in_reverse_section = True
            continue

        if not in_reverse_section:
            continue

        # Empty line resets current skill
        if not line_stripped:
            current_skill = None
            continue

        # Skill name line (ends with colon)
        if line_stripped.endswith(":") and not line.startswith("  "):
            skill_name = line_stripped[:-1].strip()
            if skill_name == skill:
                current_skill = skill_name
            else:
                current_skill = None
            continue

        # Agent line (indented with dash)
        if current_skill and line.startswith("  - "):
            agent_name = line_stripped[2:].strip()
            agents_for_skill.append(agent_name)

    if not agents_for_skill:
        return 1, _color(f"Skill '{skill}' not found or has no agents using it", YELLOW)

    output_lines: List[str] = [
        _color(f"=== Agents using skill: {skill} ===", BLUE),
        "",
    ]

    for agent in sorted(agents_for_skill):
        output_lines.append(f"  • {agent}")

    output_lines.append("")
    output_lines.append(f"Total: {len(agents_for_skill)} agent(s)")

    return 0, "\n".join(output_lines)


def skill_agents(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Alias for skill_deps - show which agents use a specific skill."""
    return skill_deps(skill, home)


def skill_suggest(project_dir_str: str, home: Path | None = None) -> Tuple[int, str]:
    """Suggest skills based on project context analysis.

    Args:
        project_dir_str: Path to project directory to analyze
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import suggester

    project_dir = Path(project_dir_str).resolve()

    if not project_dir.is_dir():
        return 1, _color(f"Project directory not found: {project_dir}", RED)

    try:
        # Detect project features
        features = suggester.detect_project_type(project_dir)

        # Generate suggestions
        suggestions = suggester.suggest_skills_for_project(project_dir)

        if not suggestions:
            return 0, _color("No skill suggestions for this project type.", YELLOW)

        # Format output
        output_lines: List[str] = [
            _color(f"=== Skill Suggestions for: {project_dir.name} ===", BLUE),
            "",
            _color("Detected features:", BLUE),
        ]

        # Show detected features
        detected_features = [
            k.replace("has_", "").replace("_", " ").title()
            for k, v in features.items()
            if v
        ]
        if detected_features:
            for feature in detected_features:
                output_lines.append(f"  {_color('✓', GREEN)} {feature}")
        else:
            output_lines.append("  No specific features detected")

        output_lines.extend(
            [
                "",
                _color("Suggested skills:", BLUE),
            ]
        )

        for skill in suggestions:
            output_lines.append(f"  {_color(skill, GREEN)}")

        output_lines.extend(
            [
                "",
                _color(f"Total suggestions: {len(suggestions)}", YELLOW),
                "",
                "To activate a skill:",
                f"  {_color('cortex skills activate <skill_name>', YELLOW)}",
            ]
        )

        return 0, "\n".join(output_lines)

    except Exception as exc:
        return 1, _color(f"Error analyzing project: {exc}", RED)


def skill_metrics(
    skill_name: Optional[str] = None, home: Path | None = None
) -> Tuple[int, str]:
    """Show skill usage metrics.

    Args:
        skill_name: Optional skill name to show metrics for (shows all if None)
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from claude_ctx_py import metrics

    try:
        all_metrics = metrics.get_all_metrics()

        if skill_name:
            # Show metrics for specific skill
            formatted = metrics.format_metrics(all_metrics, skill_name)
        else:
            # Show all metrics
            formatted = metrics.format_metrics(all_metrics)

        return 0, formatted
    except Exception as exc:
        return 1, _color(f"Error reading metrics: {exc}", RED)


def skill_metrics_reset(home: Path | None = None) -> Tuple[int, str]:
    """Reset all skill metrics.

    Args:
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from claude_ctx_py import metrics

    try:
        metrics.reset_metrics()
        return 0, _color("Skill metrics reset successfully", GREEN)
    except Exception as exc:
        return 1, _color(f"Error resetting metrics: {exc}", RED)


def skill_analytics(
    metric: Optional[str] = None, home: Path | None = None
) -> Tuple[int, str]:
    """Show skill effectiveness analytics.

    Args:
        metric: Optional specific metric to visualize ('tokens', 'activations', 'success_rate',
                'trending', 'roi', 'effectiveness')
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import analytics, metrics

    claude_dir = _resolve_claude_dir(home)

    try:
        if metric == "trending":
            # Show trending skills
            trending = analytics.get_trending_skills(30, claude_dir)
            if not trending:
                return 0, _color("No skills used in the last 30 days", YELLOW)

            output = [_color("\nTrending Skills (Last 30 Days):", BLUE), ""]
            for i, skill_data in enumerate(trending[:10], 1):
                output.append(f"{i}. {skill_data['skill_name']}")
                output.append(f"   Trend Score: {skill_data['trend_score']}")
                output.append(f"   Uses: {skill_data['activation_count']}")
                output.append(f"   Last Used: {skill_data['days_since_use']} days ago")
                output.append(f"   Tokens Saved: {skill_data['tokens_saved']:,}")
                output.append("")

            return 0, "\n".join(output)

        elif metric == "roi":
            # Show ROI analysis
            all_metrics = metrics.get_all_metrics()
            if not all_metrics:
                return 0, _color("No metrics available for ROI analysis", YELLOW)

            roi_list = [
                (name, analytics.calculate_roi(name, claude_dir))
                for name in all_metrics.keys()
            ]
            roi_list.sort(key=lambda x: x[1].get("cost_savings_usd", 0), reverse=True)

            output = [_color("\nROI Analysis (Top 10 Skills):", BLUE), ""]
            for i, (skill_name, roi_data) in enumerate(roi_list[:10], 1):
                if "error" not in roi_data:
                    output.append(f"{i}. {skill_name}")
                    output.append(
                        f"   Cost Savings: ${roi_data['cost_savings_usd']:.2f}"
                    )
                    output.append(f"   ROI: {roi_data['roi_percentage']:.1f}%")
                    output.append(f"   Activations: {roi_data['activation_count']}")
                    status = (
                        "✓ Achieved"
                        if roi_data["payback_achieved"]
                        else f"Need {roi_data['payback_uses'] - roi_data['activation_count']} more"
                    )
                    output.append(f"   Payback: {status}")
                    output.append("")

            return 0, "\n".join(output)

        elif metric == "effectiveness":
            # Show effectiveness scores
            all_metrics = metrics.get_all_metrics()
            if not all_metrics:
                return 0, _color(
                    "No metrics available for effectiveness analysis", YELLOW
                )

            scores = [
                (name, analytics.get_effectiveness_score(name, all_metrics))
                for name in all_metrics.keys()
            ]
            scores.sort(key=lambda x: x[1], reverse=True)

            output = [_color("\nSkill Effectiveness Scores (Top 10):", BLUE), ""]
            for i, (skill_name, score) in enumerate(scores[:10], 1):
                skill_data = all_metrics[skill_name]
                output.append(f"{i}. {skill_name}")
                output.append(f"   Effectiveness: {score:.1f}/100")
                output.append(
                    f"   Success Rate: {skill_data.get('success_rate', 0):.1%}"
                )
                output.append(
                    f"   Activations: {skill_data.get('activation_count', 0)}"
                )
                output.append(f"   Avg Tokens: {skill_data.get('avg_tokens', 0):,}")
                output.append("")

            return 0, "\n".join(output)

        elif metric in ("tokens", "activations", "success_rate"):
            all_metrics = metrics.get_all_metrics()
            if not all_metrics:
                return 0, _color("No metrics available for analytics", YELLOW)
            visualization = analytics.visualize_metrics(metric, all_metrics)
            return 0, visualization

        else:
            # Show recommendations by default
            all_metrics = metrics.get_all_metrics()
            if not all_metrics:
                return 0, _color("No metrics available for analytics", YELLOW)

            recommendations = analytics.get_recommendations({}, claude_dir)

            output = [_color("\nSkill Analytics & Recommendations:", BLUE), ""]
            output.append(f"Total Skills Tracked: {len(all_metrics)}")
            output.append(
                f"Total Activations: {sum(s.get('activation_count', 0) for s in all_metrics.values()):,}"
            )
            output.append(
                f"Total Tokens Saved: {sum(s.get('total_tokens_saved', 0) for s in all_metrics.values()):,}"
            )
            output.append("")
            output.append(_color("Recommendations:", GREEN))
            for rec in recommendations:
                output.append(f"  • {rec}")
            output.append("")
            output.append("Available analytics views:")
            output.append("  • skills analytics --metric trending")
            output.append("  • skills analytics --metric roi")
            output.append("  • skills analytics --metric effectiveness")
            output.append("  • skills analytics --metric tokens")
            output.append("  • skills analytics --metric activations")
            output.append("  • skills analytics --metric success_rate")

            return 0, "\n".join(output)

    except Exception as exc:
        return 1, _color(f"Error generating analytics: {exc}", RED)


def skill_report(format: str = "text", home: Path | None = None) -> Tuple[int, str]:
    """Generate comprehensive skill analytics report.

    Args:
        format: Report format ('text', 'json', or 'csv')
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import analytics, metrics

    claude_dir = _resolve_claude_dir(home)

    try:
        if format in ("text", "json"):
            # Generate report
            report = analytics.generate_analytics_report(format, claude_dir)
            return 0, report

        elif format == "csv":
            # Export to CSV
            export_path = analytics.export_analytics("csv", claude_dir)
            return 0, _color(f"Analytics exported to: {export_path}", GREEN)

        else:
            return 1, _color(
                f"Unsupported format: {format}. Use 'text', 'json', or 'csv'", RED
            )

    except Exception as exc:
        return 1, _color(f"Error generating report: {exc}", RED)


def skill_trending(days: int = 30, home: Path | None = None) -> Tuple[int, str]:
    """Show trending skills over the specified time period.

    Args:
        days: Number of days to look back (default: 30)
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import analytics

    claude_dir = _resolve_claude_dir(home)

    try:
        trending = analytics.get_trending_skills(days, claude_dir)

        if not trending:
            return 0, _color(f"No skills used in the last {days} days", YELLOW)

        output = [_color(f"\nTrending Skills (Last {days} Days):", BLUE), ""]
        output.append(
            f"{'Rank':<6} {'Skill':<40} {'Score':<10} {'Uses':<8} {'Days Ago':<10}"
        )
        output.append("-" * 80)

        for i, skill_data in enumerate(trending[:15], 1):
            output.append(
                f"{i:<6} {skill_data['skill_name'][:39]:<40} "
                f"{skill_data['trend_score']:<10} {skill_data['activation_count']:<8} "
                f"{skill_data['days_since_use']:<10}"
            )

        return 0, "\n".join(output)

    except Exception as exc:
        return 1, _color(f"Error getting trending skills: {exc}", RED)


def skill_compose(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Show dependency tree for a skill.

    Args:
        skill: Name of the skill to analyze
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message)
    """
    from .. import composer

    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills compose <skill_name>"

    # Check if skill exists
    skill_path = skills_dir / skill / "SKILL.md"
    if not skill_path.is_file():
        return 1, _color(f"Skill '{skill}' not found", RED)

    # Load composition map
    try:
        composition_map = composer.load_composition_map(claude_dir)
    except ImportError as exc:
        return 1, _color(f"Error: {exc}", RED)
    except Exception as exc:
        return 1, _color(f"Failed to load composition map: {exc}", RED)

    # Validate no cycles
    is_valid, error_msg = composer.validate_no_cycles(composition_map)
    if not is_valid:
        return 1, _color(f"Composition validation failed: {error_msg}", RED)

    # Get dependencies
    dependencies = composer.get_dependencies(skill, composition_map)

    # Build output
    output_lines: List[str] = [
        _color(f"=== Skill Composition: {skill} ===", BLUE),
        "",
    ]

    if not dependencies:
        output_lines.extend(
            [
                _color("No dependencies", GREEN),
                "",
                "This skill can be loaded independently without other skills.",
            ]
        )
    else:
        output_lines.extend(
            [
                _color(
                    f"Direct dependencies: {len(composition_map.get(skill, []))}", BLUE
                ),
                _color(f"Total dependencies (transitive): {len(dependencies)}", BLUE),
                "",
                _color("Dependency tree:", BLUE),
            ]
        )

        # Generate and format tree
        tree = composer.get_dependency_tree(skill, composition_map)
        tree_str = composer.format_dependency_tree(tree)
        output_lines.append(tree_str)

        output_lines.extend(
            [
                "",
                _color("Load order:", BLUE),
            ]
        )
        for i, dep in enumerate(dependencies, 1):
            output_lines.append(f"  {i}. {dep}")
        output_lines.append(f"  {len(dependencies) + 1}. {skill}")

    return 0, "\n".join(output_lines)


def skill_community_list(
    tags: Optional[List[str]] = None,
    search: Optional[str] = None,
    verified: bool = False,
    sort_by: str = "name",
    home: Path | None = None,
) -> Tuple[int, str]:
    """List available community skills.

    Display a list of community-contributed skills with filtering and sorting options.
    Shows skill name, version, author, description, tags, rating, and installation status.

    Args:
        tags: Optional list of tags to filter by (e.g., ["frontend", "react"])
        search: Optional search query to filter by name/description
        verified: If True, only show verified community skills
        sort_by: Sort field - "name", "rating", or "author" (default: "name")
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message) where exit_code is 0 for success, 1 for error

    Examples:
        >>> skill_community_list()  # List all community skills
        >>> skill_community_list(tags=["react"], sort_by="rating")  # Filter by tag and sort
        >>> skill_community_list(search="hooks")  # Search for skills matching "hooks"
    """
    from .. import community

    claude_dir = _resolve_claude_dir(home)

    # Get all community skills
    skills = community.get_community_skills(claude_dir)

    if not skills:
        return 1, _color("No community skills found", YELLOW)

    # Apply filters
    filtered_skills = skills

    # Filter by tags if provided
    if tags:
        tags_lower = [tag.lower() for tag in tags]
        filtered_skills = [
            skill
            for skill in filtered_skills
            if any(tag.lower() in tags_lower for tag in skill.get("tags", []))
        ]

    # Filter by search query if provided
    if search:
        search_lower = search.lower()
        filtered_skills = [
            skill
            for skill in filtered_skills
            if search_lower in skill.get("name", "").lower()
            or search_lower in skill.get("description", "").lower()
        ]

    # Filter by verified status if requested
    if verified:
        # Verified skills have ratings >= 4.0 or are marked as verified
        filtered_skills = [
            skill
            for skill in filtered_skills
            if skill.get("rating") and skill["rating"] >= 4.0
        ]

    if not filtered_skills:
        return 1, _color("No skills match the specified criteria", YELLOW)

    # Sort skills
    if sort_by == "rating":
        # Sort by rating (highest first), None ratings go last
        filtered_skills.sort(
            key=lambda s: (s.get("rating") is None, -(s.get("rating") or 0))
        )
    elif sort_by == "author":
        filtered_skills.sort(key=lambda s: s.get("author", "").lower())
    else:  # default to name
        filtered_skills.sort(key=lambda s: s.get("name", "").lower())

    # Build output
    output_lines: List[str] = [
        _color("=== Community Skills ===", BLUE),
        "",
    ]

    if tags:
        output_lines.append(_color(f"Filtered by tags: {', '.join(tags)}", BLUE))
    if search:
        output_lines.append(_color(f"Search query: {search}", BLUE))
    if verified:
        output_lines.append(_color("Showing verified skills only", BLUE))
    if tags or search or verified:
        output_lines.append("")

    output_lines.append(_color(f"Found {len(filtered_skills)} skill(s)", GREEN))
    output_lines.append("")

    for skill in filtered_skills:
        name = skill.get("name", "unknown")
        version = skill.get("version", "unknown")
        author = skill.get("author", "unknown")
        description = skill.get("description", "No description")
        rating = skill.get("rating")
        installed = skill.get("installed", False)
        tags_list = skill.get("tags", [])

        # Truncate long descriptions
        if len(description) > 80:
            description = description[:77] + "..."

        # Format rating
        rating_str = ""
        if rating is not None:
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            rating_str = _color(f" {stars} ({rating:.1f})", YELLOW)

        # Format installed status
        installed_str = _color(" [INSTALLED]", GREEN) if installed else ""

        output_lines.extend(
            [
                _color(f"{name}", BLUE)
                + _color(f" v{version}", NC)
                + rating_str
                + installed_str,
                f"  by {author}",
                f"  {description}",
            ]
        )

        if tags_list:
            tags_str = ", ".join(tags_list[:5])  # Limit to first 5 tags
            if len(tags_list) > 5:
                tags_str += f" (+{len(tags_list) - 5} more)"
            output_lines.append(_color(f"  Tags: {tags_str}", NC))

        output_lines.append("")

    return 0, "\n".join(output_lines)


def skill_community_install(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Install a community skill to the local skills directory.

    Validates and installs a community-contributed skill, making it available
    for use in your local Claude environment. The skill is copied from the
    community/skills directory to your local skills directory.

    Args:
        skill: Name of the skill to install (without .md extension)
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message) where exit_code is 0 for success, 1 for error

    Examples:
        >>> skill_community_install("react-hooks")  # Install the react-hooks skill
    """
    from .. import community

    claude_dir = _resolve_claude_dir(home)

    if not skill:
        return (
            1,
            _color("Usage:", RED) + " cortex skills community install <skill_name>",
        )

    # Check if skill is already installed
    skills_dir = claude_dir / "skills"
    installed_path = skills_dir / f"{skill}.md"
    if installed_path.exists():
        return 1, _color(f"Skill '{skill}' is already installed", YELLOW)

    # Attempt installation
    try:
        success = community.install_community_skill(skill, claude_dir)
    except Exception as exc:
        return 1, _color(f"Installation failed: {exc}", RED)

    if not success:
        # Check if skill exists in community
        community_dir = claude_dir / "community" / "skills"
        skill_file = community_dir / f"{skill}.md"

        if not skill_file.exists():
            return 1, _color(f"Community skill '{skill}' not found", RED)
        else:
            # Validation must have failed
            is_valid, errors = community.validate_contribution(skill_file)
            if not is_valid:
                error_lines = [_color(f"Skill '{skill}' failed validation:", RED), ""]
                for error in errors:
                    error_lines.append(f"  - {error}")
                return 1, "\n".join(error_lines)
            else:
                return 1, _color(f"Failed to install skill '{skill}'", RED)

    output_lines: List[str] = [
        _color(f"Successfully installed community skill: {skill}", GREEN),
        "",
        _color("The skill is now available for use.", NC),
    ]

    return 0, "\n".join(output_lines)


def skill_community_validate(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Validate a community skill contribution.

    Checks that a skill file meets all requirements for community contribution,
    including required frontmatter fields, proper formatting, token budget limits,
    and required sections.

    Args:
        skill: Name of the skill to validate (without .md extension)
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message) where exit_code is 0 for valid, 1 for invalid

    Examples:
        >>> skill_community_validate("my-new-skill")  # Validate a skill before submission
    """
    from .. import community

    claude_dir = _resolve_claude_dir(home)

    if not skill:
        return (
            1,
            _color("Usage:", RED)
            + " cortex skills community validate <skill_name>",
        )

    # Check community skills directory
    community_dir = claude_dir / "community" / "skills"
    skill_file = community_dir / f"{skill}.md"

    if not skill_file.exists():
        # Also check local skills directory
        skills_dir = claude_dir / "skills"
        skill_file = skills_dir / f"{skill}.md"

        if not skill_file.exists():
            return 1, _color(f"Skill '{skill}' not found", RED)

    # Validate the skill
    try:
        is_valid, errors = community.validate_contribution(skill_file)
    except Exception as exc:
        return 1, _color(f"Validation error: {exc}", RED)

    # Build output
    if is_valid:
        output_lines: List[str] = [
            _color(f"✓ Skill '{skill}' is valid for community contribution", GREEN),
            "",
            _color("All validation checks passed:", GREEN),
            "  ✓ Valid YAML frontmatter",
            "  ✓ Required fields present",
            "  ✓ Name format correct (hyphen-case)",
            "  ✓ Version follows semver",
            "  ✓ License is Apache-2.0",
            "  ✓ Tags are valid (1-10 tags)",
            "  ✓ Token budget in range (800-5000)",
            "  ✓ Required sections present",
        ]
        return 0, "\n".join(output_lines)
    else:
        output_lines = [
            _color(f"✗ Skill '{skill}' failed validation", RED),
            "",
            _color(f"Found {len(errors)} error(s):", RED),
            "",
        ]
        for i, error in enumerate(errors, 1):
            output_lines.append(f"  {i}. {error}")

        output_lines.extend(
            [
                "",
                _color("Fix these errors before submitting to the community.", YELLOW),
            ]
        )
        return 1, "\n".join(output_lines)


def skill_community_rate(
    skill: str, rating: int, home: Path | None = None
) -> Tuple[int, str]:
    """Rate a community skill.

    Submit a rating for a community skill. Ratings help other users discover
    high-quality skills and provide feedback to skill authors.

    Args:
        skill: Name of the skill to rate (without .md extension)
        rating: Rating value from 1-5 stars
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message) where exit_code is 0 for success, 1 for error

    Examples:
        >>> skill_community_rate("react-hooks", 5)  # Give 5 stars
        >>> skill_community_rate("python-utils", 4)  # Give 4 stars
    """
    from .. import community

    claude_dir = _resolve_claude_dir(home)

    if not skill:
        return (
            1,
            _color("Usage:", RED)
            + " cortex skills community rate <skill_name> <rating>",
        )

    # Validate rating
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return 1, _color("Rating must be an integer between 1 and 5", RED)

    # Check if skill exists in community
    community_dir = claude_dir / "community" / "skills"
    skill_file = community_dir / f"{skill}.md"

    if not skill_file.exists():
        return 1, _color(f"Community skill '{skill}' not found", RED)

    # Submit rating
    try:
        success = community.rate_skill(skill, rating, claude_dir)
    except Exception as exc:
        return 1, _color(f"Failed to submit rating: {exc}", RED)

    if not success:
        return 1, _color(f"Failed to record rating for skill '{skill}'", RED)

    # Show stars
    stars = "★" * rating + "☆" * (5 - rating)

    output_lines: List[str] = [
        _color(f"Successfully rated '{skill}'", GREEN),
        "",
        _color(f"Your rating: {stars} ({rating}/5)", YELLOW),
        "",
        _color("Thank you for your feedback!", NC),
    ]

    return 0, "\n".join(output_lines)


def skill_community_search(
    query: str,
    tags: Optional[List[str]] = None,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Search for community skills.

    Search community skills by text query and optionally filter by tags.
    Results are sorted by relevance with exact name matches ranked highest.

    Args:
        query: Search query string (searches name and description)
        tags: Optional list of tags to filter by
        home: Optional path to cortex directory

    Returns:
        Tuple of (exit_code, message) where exit_code is 0 for success, 1 for error

    Examples:
        >>> skill_community_search("react")  # Search for "react"
        >>> skill_community_search("hooks", tags=["frontend"])  # Search with tag filter
    """
    from .. import community

    claude_dir = _resolve_claude_dir(home)

    if not query:
        return (
            1,
            _color("Usage:", RED)
            + " cortex skills community search <query> [--tags tag1,tag2]",
        )

    # Perform search
    try:
        results = community.search_skills(query, tags or [], claude_dir)
    except Exception as exc:
        return 1, _color(f"Search failed: {exc}", RED)

    if not results:
        search_desc = f"query '{query}'"
        if tags:
            search_desc += f" with tags: {', '.join(tags)}"
        return 1, _color(f"No skills found matching {search_desc}", YELLOW)

    # Build output
    output_lines: List[str] = [
        _color("=== Search Results ===", BLUE),
        "",
    ]

    if tags:
        output_lines.append(_color(f"Query: {query} | Tags: {', '.join(tags)}", BLUE))
    else:
        output_lines.append(_color(f"Query: {query}", BLUE))

    output_lines.append("")
    output_lines.append(_color(f"Found {len(results)} skill(s)", GREEN))
    output_lines.append("")

    for skill in results:
        name = skill.get("name", "unknown")
        version = skill.get("version", "unknown")
        author = skill.get("author", "unknown")
        description = skill.get("description", "No description")
        rating = skill.get("rating")
        installed = skill.get("installed", False)
        tags_list = skill.get("tags", [])

        # Truncate long descriptions
        if len(description) > 80:
            description = description[:77] + "..."

        # Format rating
        rating_str = ""
        if rating is not None:
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            rating_str = _color(f" {stars} ({rating:.1f})", YELLOW)

        # Format installed status
        installed_str = _color(" [INSTALLED]", GREEN) if installed else ""

        output_lines.extend(
            [
                _color(f"{name}", BLUE)
                + _color(f" v{version}", NC)
                + rating_str
                + installed_str,
                f"  by {author}",
                f"  {description}",
            ]
        )

        if tags_list:
            tags_str = ", ".join(tags_list[:5])  # Limit to first 5 tags
            if len(tags_list) > 5:
                tags_str += f" (+{len(tags_list) - 5} more)"
            output_lines.append(_color(f"  Tags: {tags_str}", NC))

        output_lines.append("")

    return 0, "\n".join(output_lines)

def skill_recommend(home: Path | None = None) -> Tuple[int, str]:
    """Show AI-powered skill recommendations based on current context.

    Uses the SkillRecommender engine to analyze the current session context
    and suggest relevant skills based on active files, agents, and patterns.

    Args:
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import skill_recommender, intelligence

    try:
        # Initialize recommender
        recommender = skill_recommender.SkillRecommender(home=home)

        # Build session context
        # For CLI usage, we'll use a minimal context based on current directory
        cwd = Path.cwd()
        python_files = list(cwd.glob("**/*.py"))[:20]

        # Create a minimal session context
        context = intelligence.SessionContext(
            files_changed=[str(f.relative_to(cwd)) for f in python_files],
            file_types={f.suffix for f in python_files},
            directories={str(f.parent.relative_to(cwd)) for f in python_files},
            has_tests=any('test' in str(f) for f in python_files),
            has_auth=any('auth' in str(f) for f in python_files),
            has_api=any('api' in str(f) for f in python_files),
            has_frontend=(cwd / 'src').exists() or (cwd / 'frontend').exists(),
            has_backend=(cwd / 'backend').exists() or (cwd / 'server').exists(),
            has_database=any('db' in str(f) or 'database' in str(f) for f in python_files),
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=datetime.datetime.now(),
            last_activity=datetime.datetime.now(),
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        # Get recommendations
        recommendations = recommender.recommend_for_context(context)

        if not recommendations:
            return 0, _color("No skill recommendations at this time.", YELLOW)

        # Format output
        output_lines: List[str] = [
            _color("=== AI-Powered Skill Recommendations ===", BLUE),
            "",
            _color("Based on your current context:", BLUE),
        ]

        # Group recommendations by confidence
        high_conf = [r for r in recommendations if r.confidence >= 0.8]
        med_conf = [r for r in recommendations if 0.6 <= r.confidence < 0.8]
        low_conf = [r for r in recommendations if r.confidence < 0.6]

        if high_conf:
            output_lines.extend(
                [
                    "",
                    _color("High Confidence (Auto-Activate):", GREEN),
                ]
            )
            for rec in high_conf:
                output_lines.append(
                    f"  {_color('✓', GREEN)} {_color(rec.skill_name, BLUE)} "
                    f"({int(rec.confidence * 100)}%)"
                )
                output_lines.append(f"    {rec.reason}")
                if rec.related_agents:
                    agents_str = ", ".join(rec.related_agents[:3])
                    output_lines.append(f"    Related agents: {agents_str}")

        if med_conf:
            output_lines.extend(
                [
                    "",
                    _color("Medium Confidence:", YELLOW),
                ]
            )
            for rec in med_conf:
                output_lines.append(
                    f"  {_color('•', YELLOW)} {_color(rec.skill_name, BLUE)} "
                    f"({int(rec.confidence * 100)}%)"
                )
                output_lines.append(f"    {rec.reason}")

        if low_conf:
            output_lines.extend(
                [
                    "",
                    _color("Low Confidence:", NC),
                ]
            )
            for rec in low_conf[:3]:  # Limit to top 3
                output_lines.append(
                    f"  {_color('○', NC)} {rec.skill_name} "
                    f"({int(rec.confidence * 100)}%)"
                )

        # Add usage tip
        output_lines.extend(
            [
                "",
                _color("Tip:", BLUE)
                + " Use 'cortex skills feedback <skill_name> <helpful|not-helpful>' to improve recommendations",
            ]
        )

        return 0, "\n".join(output_lines)

    except Exception as exc:
        return 1, _color(f"Error generating recommendations: {exc}", RED)


def skill_feedback(
    skill: str, rating: str, comment: str | None = None, home: Path | None = None
) -> Tuple[int, str]:
    """Provide feedback on a skill recommendation.

    Args:
        skill: Name of the skill
        rating: Feedback rating ("helpful" or "not-helpful")
        comment: Optional comment explaining the feedback
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import skill_recommender

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills feedback <skill_name> <helpful|not-helpful> [comment]"

    # Validate rating
    rating_lower = rating.lower()
    if rating_lower not in ["helpful", "not-helpful"]:
        return 1, _color("Rating must be 'helpful' or 'not-helpful'", RED)

    helpful = rating_lower == "helpful"

    try:
        # Initialize recommender
        recommender = skill_recommender.SkillRecommender(home=home)

        # Record feedback
        recommender.record_feedback(
            skill_name=skill, helpful=helpful, comment=comment or ""
        )

        # Show confirmation
        feedback_emoji = "👍" if helpful else "👎"
        feedback_text = _color("helpful", GREEN) if helpful else _color("not helpful", RED)

        output_lines: List[str] = [
            _color("=== Feedback Recorded ===", BLUE),
            "",
            f"Skill: {_color(skill, BLUE)}",
            f"Rating: {feedback_emoji} {feedback_text}",
        ]

        if comment:
            output_lines.extend(
                [
                    f"Comment: {comment}",
                ]
            )

        output_lines.extend(
            [
                "",
                _color(
                    "Thank you! Your feedback helps improve future recommendations.", GREEN
                ),
            ]
        )

        return 0, "\n".join(output_lines)

    except Exception as exc:
        return 1, _color(f"Error recording feedback: {exc}", RED)


def skill_rate(
    skill: str,
    stars: int,
    helpful: bool = True,
    task_succeeded: bool = True,
    review: Optional[str] = None,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Rate a skill with stars and optional review.

    Args:
        skill: Name of the skill to rate
        stars: Star rating (1-5)
        helpful: Was the skill helpful? (default: True)
        task_succeeded: Did the task succeed? (default: True)
        review: Optional written review
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)

    Examples:
        >>> skill_rate("owasp-top-10", 5, helpful=True, review="Essential for security")
        >>> skill_rate("api-design-patterns", 4)
    """
    from .. import skill_rating
    from ..skill_rating_prompts import SkillRatingPromptManager

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills rate <skill_name> --stars <1-5> [--review 'text']"

    try:
        # Initialize rating collector
        collector = skill_rating.SkillRatingCollector(home=home)

        # Check if user has already rated this skill
        existing = collector.has_user_rated(skill)
        if existing:
            user_rating = collector.get_user_rating(skill)
            if user_rating:
                return 1, _color(
                    f"You've already rated '{skill}' ({user_rating.stars} stars). "
                    f"Multiple ratings not yet supported.",
                    YELLOW,
                )

        # Record rating
        rating = collector.record_rating(
            skill=skill,
            stars=stars,
            helpful=helpful,
            task_succeeded=task_succeeded,
            review=review,
        )

        # Show confirmation with star display
        stars_display = "⭐" * stars
        helpful_emoji = "👍" if helpful else "👎"

        output_lines: List[str] = [
            _color("=== Rating Recorded ===", BLUE),
            "",
            f"Skill: {_color(skill, BLUE)}",
            f"Stars: {_color(stars_display, YELLOW)} ({stars}/5)",
            f"Helpful: {helpful_emoji} {_color('Yes' if helpful else 'No', GREEN if helpful else RED)}",
        ]

        if review:
            output_lines.extend([
                "",
                _color("Your Review:", BLUE),
                f"  {review}",
            ])

        output_lines.extend([
            "",
            _color("Thank you for rating this skill!", GREEN),
            "",
            _color("View skill ratings with:", BLUE) + " cortex skills ratings <skill_name>",
        ])

        try:
            SkillRatingPromptManager(home=home).mark_rated(skill)
        except Exception:
            pass

        return 0, "\n".join(output_lines)

    except ValueError as exc:
        return 1, _color(f"Invalid rating: {exc}", RED)
    except Exception as exc:
        return 1, _color(f"Error recording rating: {exc}", RED)


def skill_ratings(
    skill: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Show ratings and reviews for a skill.

    Args:
        skill: Name of the skill
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)

    Examples:
        >>> skill_ratings("owasp-top-10")
    """
    from .. import skill_rating

    if not skill:
        return 1, _color("Usage:", RED) + " cortex skills ratings <skill_name>"

    try:
        # Initialize rating collector
        collector = skill_rating.SkillRatingCollector(home=home)

        # Get quality metrics
        metrics = collector.get_skill_score(skill)

        if not metrics:
            return 0, _color(f"No ratings yet for '{skill}'", YELLOW)

        # Format star display
        star_display = metrics.star_display()

        # Build output
        output_lines: List[str] = [
            _color(f"=== Ratings: {skill} ===", BLUE),
            "",
            _color(star_display, YELLOW),
            f"Based on {_color(str(metrics.total_ratings), BLUE)} rating{'s' if metrics.total_ratings != 1 else ''}",
            "",
        ]

        # Rating distribution
        output_lines.extend([
            _color("Rating Distribution:", BLUE),
            f"  ⭐⭐⭐⭐⭐  {metrics.stars_5:>3} ({metrics.stars_5 / max(metrics.total_ratings, 1) * 100:>5.1f}%)",
            f"  ⭐⭐⭐⭐   {metrics.stars_4:>3} ({metrics.stars_4 / max(metrics.total_ratings, 1) * 100:>5.1f}%)",
            f"  ⭐⭐⭐    {metrics.stars_3:>3} ({metrics.stars_3 / max(metrics.total_ratings, 1) * 100:>5.1f}%)",
            f"  ⭐⭐     {metrics.stars_2:>3} ({metrics.stars_2 / max(metrics.total_ratings, 1) * 100:>5.1f}%)",
            f"  ⭐      {metrics.stars_1:>3} ({metrics.stars_1 / max(metrics.total_ratings, 1) * 100:>5.1f}%)",
            "",
        ])

        # Quality metrics
        output_lines.extend([
            _color("Quality Metrics:", BLUE),
            f"  {_color('👍', GREEN)} {metrics.helpful_percentage:.0f}% found helpful",
            f"  {_color('✅', GREEN)} {metrics.success_correlation:.0f}% task success rate",
            f"  {_color('🔄', BLUE)} Used {metrics.usage_count} times",
        ])

        if metrics.token_efficiency:
            output_lines.append(f"  {_color('📊', YELLOW)} {metrics.token_efficiency:.0f}% avg token reduction")

        # Recent reviews
        reviews = collector.get_recent_reviews(skill, limit=5)
        if reviews:
            output_lines.extend([
                "",
                _color("Recent Reviews:", BLUE),
            ])

            for review in reviews:
                stars_display = "⭐" * review["stars"]
                time_ago = review["time_ago"]
                review_text = review["review"]

                output_lines.extend([
                    "",
                    f"  {_color(stars_display, YELLOW)} - {time_ago}",
                    f"    {review_text}",
                ])

        return 0, "\n".join(output_lines)

    except Exception as exc:
        return 1, _color(f"Error retrieving ratings: {exc}", RED)


def skill_top_rated(
    category: Optional[str] = None,
    limit: int = 10,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Show top-rated skills.

    Args:
        category: Optional category filter (future implementation)
        limit: Maximum number of skills to show (default: 10)
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)

    Examples:
        >>> skill_top_rated(limit=10)
        >>> skill_top_rated(category="security", limit=5)
    """
    from .. import skill_rating

    try:
        # Initialize rating collector
        collector = skill_rating.SkillRatingCollector(home=home)

        # Get top-rated skills
        top_rated = collector.get_top_rated(category=category, limit=limit)

        if not top_rated:
            return 0, _color("No rated skills found", YELLOW)

        # Build output
        output_lines: List[str] = [
            _color("=== Top-Rated Skills ===", BLUE),
            "",
        ]

        if category:
            output_lines.append(_color(f"Category: {category}", BLUE))
            output_lines.append("")

        output_lines.append(_color(f"Showing top {len(top_rated)} skills:", GREEN))
        output_lines.append("")

        # Table header
        output_lines.append(
            f"{'Rank':<6} {'Skill':<35} {'Rating':<15} {'Ratings':<10} {'Success':<8}"
        )
        output_lines.append("-" * 80)

        # List skills
        for i, (skill_name, metrics) in enumerate(top_rated, 1):
            # Truncate skill name if too long
            display_name = skill_name[:34] if len(skill_name) > 34 else skill_name

            # Star display (compact)
            full_stars = int(metrics.avg_rating)
            stars = "⭐" * full_stars

            output_lines.append(
                f"{i:<6} {display_name:<35} {stars:<7} {metrics.avg_rating:.1f}/5 "
                f"{metrics.total_ratings:<10} {metrics.success_correlation:.0f}%"
            )

        output_lines.extend([
            "",
            _color("View details with:", BLUE) + " cortex skills ratings <skill_name>",
        ])

        return 0, "\n".join(output_lines)

    except Exception as exc:
        return 1, _color(f"Error retrieving top-rated skills: {exc}", RED)


def skill_ratings_export(
    skill: Optional[str] = None,
    format: str = "json",
    home: Path | None = None,
) -> Tuple[int, str]:
    """Export skill ratings data.

    Args:
        skill: Optional skill name to filter by (exports all if None)
        format: Export format ("json" or "csv", default: "json")
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)

    Examples:
        >>> skill_ratings_export(format="json")  # Export all ratings as JSON
        >>> skill_ratings_export(skill="owasp-top-10", format="csv")  # Export specific skill as CSV
    """
    from .. import skill_rating
    import json as json_lib
    import csv
    import io

    try:
        # Initialize rating collector
        collector = skill_rating.SkillRatingCollector(home=home)

        # Get export data
        data = collector.export_ratings(skill=skill)

        if format == "json":
            # Export as JSON
            json_output = json_lib.dumps(data, indent=2)
            return 0, json_output

        elif format == "csv":
            # Export ratings as CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                "skill_name", "stars", "timestamp", "project_type",
                "review", "was_helpful", "task_succeeded"
            ])

            # Write rows
            for rating in data["ratings"]:
                writer.writerow([
                    rating["skill_name"],
                    rating["stars"],
                    rating["timestamp"],
                    rating["project_type"],
                    rating["review"] or "",
                    rating["was_helpful"],
                    rating["task_succeeded"],
                ])

            return 0, output.getvalue()

        else:
            return 1, _color(f"Unsupported format: {format}. Use 'json' or 'csv'", RED)

    except Exception as exc:
        return 1, _color(f"Error exporting ratings: {exc}", RED)
