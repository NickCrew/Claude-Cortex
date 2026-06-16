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
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

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



def skill_rebuild_index(home: Path | None = None) -> Tuple[int, str]:
    """Rebuild skills/skill-index.json from SKILL.md front matter.

    Resolves the skills root from the Cortex install (falling back to the
    repo root in development mode) and writes a deterministic index document.
    """
    from .. import skill_index

    skills_root: Path
    if home is not None:
        skills_root = Path(home) / "skills"
    else:
        from .base import _resolve_cortex_root

        skills_root = _resolve_cortex_root() / "skills"

    return skill_index.rebuild_index(skills_root=skills_root)


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













def skill_context(
    write: bool = True,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Generate skill context for the current session.

    Analyzes the current working context and writes a skill-context.md file
    that both Claude Code and Codex can read at session start.

    Args:
        write: If True, writes .claude/skill-context.md in cwd
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, formatted_output)
    """
    from .. import skill_recommender
    from ..intelligence import get_current_context

    try:
        context = get_current_context()
        recommender = skill_recommender.SkillRecommender(home=home)
        recommendations = recommender.recommend_for_context(context)[:5]

        if not recommendations:
            return 0, "# Skill Context\n\nNo skill recommendations for this session."

        lines = [
            "# Skill Context",
            "",
            "Recommended skills for this session (auto-generated by `cortex skills context`):",
            "",
        ]
        for i, rec in enumerate(recommendations, 1):
            pct = int(rec.confidence * 100)
            lines.append(f"{i}. **{rec.skill_name}** ({pct}%) — {rec.reason}")

        lines.extend(["", "Load with `/ctx:<skill-name>`."])
        output = "\n".join(lines)

        if write:
            ctx_dir = Path.cwd() / ".claude"
            ctx_dir.mkdir(parents=True, exist_ok=True)
            (ctx_dir / "skill-context.md").write_text(output + "\n", encoding="utf-8")

        return 0, output

    except Exception as exc:
        return 1, _color(f"Error generating skill context: {exc}", RED)


def skill_recommend(home: Path | None = None) -> Tuple[int, str]:
    """Show AI-powered skill recommendations based on current context.

    Uses the SkillRecommender engine to analyze the current session context
    and suggest relevant skills based on active files, agents, and patterns.

    Args:
        home: Optional path to Claude directory

    Returns:
        Tuple of (exit_code, output_message)
    """
    from .. import skill_recommender
    from ..intelligence import get_current_context

    try:
        # Initialize recommender
        recommender = skill_recommender.SkillRecommender(home=home)

        # Build session context from git changes
        context = get_current_context()

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



def skill_activate(skill_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Activate a skill by installing it into the resolved .claude/skills/ directory.

    On project scope (CORTEX_SCOPE=project), the skill is copied into
    ``.agents/skills/<name>`` and a relative symlink is created in
    ``.claude/skills/<name>``.  On global scope a direct bundle symlink is
    created, preserving the original behaviour.

    Args:
        skill_name: Name of the skill to activate
        home: Home directory (uses default if not specified)

    Returns:
        Tuple of (exit_code, message)
    """
    import os
    from .base import _resolve_cortex_root
    from .skill_link import link_skill

    cortex_root = _resolve_cortex_root()
    scope = (os.environ.get("CORTEX_SCOPE") or "global").strip().lower()
    claude_dir = _resolve_claude_dir(home)

    source_skill = cortex_root / "skills" / skill_name
    return link_skill(source_skill, claude_dir, scope)


def skill_deactivate(skill_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Deactivate a skill by removing its link and, on project scope, the .agents copy.

    Args:
        skill_name: Name of the skill to deactivate
        home: Home directory (uses default if not specified)

    Returns:
        Tuple of (exit_code, message)
    """
    import os
    from .skill_link import unlink_skill

    scope = (os.environ.get("CORTEX_SCOPE") or "global").strip().lower()
    claude_dir = _resolve_claude_dir(home)
    return unlink_skill(claude_dir, skill_name, scope)


# ---------------------------------------------------------------------------
# Registry-backed category operations
# ---------------------------------------------------------------------------
#
# skills/registry.yaml is the single source of truth for skill catalog
# metadata, including the many-to-many skill -> categories mapping. The
# SKILL.md front matter does not carry a category, so category-aware features
# (grouping, bulk enable/disable) read it from here. Helpers degrade to "no
# categories" on a missing/malformed registry rather than crashing callers.


def load_skills_registry(cortex_root: Path | None = None) -> Dict[str, Any]:
    """Load ``skills/registry.yaml`` as a dict ({} on any failure)."""
    try:
        import yaml
    except ImportError:
        return {}
    from .base import _resolve_cortex_root

    root = cortex_root or _resolve_cortex_root()
    registry_path = root / "skills" / "registry.yaml"
    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def skill_categories_map(registry: Dict[str, Any]) -> Dict[str, List[str]]:
    """Build a ``{skill_slug: [category, ...]}`` map from a loaded registry.

    A skill may belong to several categories (e.g. ``accessibility-audit`` is
    in ``security``, ``design``, and ``analysis``), so the value is a list.
    """
    skills_data = registry.get("skills", {})
    result: Dict[str, List[str]] = {}
    if isinstance(skills_data, dict):
        for slug, info in skills_data.items():
            cats = info.get("categories", []) if isinstance(info, dict) else []
            result[str(slug)] = [str(c) for c in cats] if cats else []
    return result


def activate_skills_by_category(
    category: str, registry: Dict[str, Any], home: Path | None = None
) -> Tuple[int, List[str]]:
    """Activate every skill whose registry categories include ``category``.

    Mirrors ``codex_skills.link_provider_skills_by_category`` but drives the
    Claude activation symlinks (~/.claude/skills) via ``skill_activate``.
    """
    messages: List[str] = []
    success_count = 0
    for slug, cats in skill_categories_map(registry).items():
        if category in cats:
            exit_code, msg = skill_activate(slug, home)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1
    return success_count, messages


def deactivate_skills_by_category(
    category: str, registry: Dict[str, Any], home: Path | None = None
) -> Tuple[int, List[str]]:
    """Deactivate every skill whose registry categories include ``category``."""
    messages: List[str] = []
    success_count = 0
    for slug, cats in skill_categories_map(registry).items():
        if category in cats:
            exit_code, msg = skill_deactivate(slug, home)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1
    return success_count, messages
