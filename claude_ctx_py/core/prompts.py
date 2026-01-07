"""Prompt library management functions (reference-based activation).

Prompts are organized in subdirectories under ~/.cortex/prompts/:
- prompts/guidelines/code-review.md
- prompts/templates/pr-description.md
- prompts/personas/senior-dev.md

Slugs use category/name format: "guidelines/code-review"
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    _color,
    _resolve_claude_dir,
    _parse_active_entries,
    _write_active_entries,
    _refresh_claude_md,
    _extract_front_matter,
    _tokenize_front_matter,
    _extract_scalar_from_paths,
)


COMPONENT_TYPE = "prompts"
BASE_PATH = "prompts"


@dataclass
class PromptInfo:
    """Metadata about a prompt definition."""

    name: str
    slug: str  # category/filename-stem (e.g., "guidelines/code-review")
    description: str
    category: str
    tokens: int
    path: Path
    status: str  # "active" or "inactive"


def _parse_prompt_file(path: Path, prompts_dir: Path) -> Optional[PromptInfo]:
    """Parse a prompt markdown file and extract metadata."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    # Extract front matter
    front_matter = _extract_front_matter(content)
    tokens_list = _tokenize_front_matter(
        front_matter.strip().splitlines() if front_matter else None
    )

    # Extract metadata from front matter
    name = _extract_scalar_from_paths(tokens_list, (("name",),)) or path.stem.replace(
        "-", " "
    ).title()
    description = (
        _extract_scalar_from_paths(tokens_list, (("description",),))
        or "No description provided"
    )
    tokens_str = _extract_scalar_from_paths(tokens_list, (("tokens",),)) or "0"

    try:
        tokens_count = int(tokens_str)
    except ValueError:
        tokens_count = 0

    # Determine category from parent directory
    try:
        relative = path.relative_to(prompts_dir)
        if len(relative.parts) > 1:
            category = relative.parts[0]
            slug = f"{category}/{path.stem}"
        else:
            category = ""
            slug = path.stem
    except ValueError:
        category = ""
        slug = path.stem

    return PromptInfo(
        name=name,
        slug=slug,
        description=description,
        category=category,
        tokens=tokens_count,
        path=path,
        status="inactive",  # Will be updated by caller
    )


def discover_prompts(home: Path | None = None) -> List[PromptInfo]:
    """Discover all prompts from ~/.cortex/prompts/ directory.

    Scans subdirectories recursively for .md files with front matter.
    Returns list of PromptInfo with status set based on .active-prompts file.
    """
    claude_dir = _resolve_claude_dir(home)
    prompts_dir = claude_dir / BASE_PATH

    if not prompts_dir.is_dir():
        return []

    # Get active prompts from .active-prompts file
    active_slugs = set(_parse_active_entries(claude_dir / ".active-prompts"))

    prompts: List[PromptInfo] = []

    # Scan all subdirectories for .md files
    for md_file in sorted(prompts_dir.rglob("*.md")):
        if md_file.name.lower() == "readme.md":
            continue
        if md_file.name.startswith("."):
            continue

        info = _parse_prompt_file(md_file, prompts_dir)
        if info:
            info.status = "active" if info.slug in active_slugs else "inactive"
            prompts.append(info)

    return prompts


def prompt_activate(slug: str, home: Path | None = None) -> Tuple[int, str]:
    """Activate a prompt by adding it to .active-prompts.

    Args:
        slug: Prompt slug in category/name format (e.g., "guidelines/code-review")
        home: Optional home directory override

    Returns:
        Tuple of (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    prompts_dir = claude_dir / BASE_PATH

    # Verify prompt file exists
    prompt_path = prompts_dir / f"{slug}.md"
    if not prompt_path.is_file():
        return 1, _color(f"Prompt '{slug}' not found at {BASE_PATH}/{slug}.md", RED)

    # Check if already active
    active_file = claude_dir / ".active-prompts"
    active = _parse_active_entries(active_file)

    if slug in active:
        return 1, _color(f"Prompt '{slug}' is already active", YELLOW)

    # Add to active list
    active.append(slug)
    _write_active_entries(active_file, active)
    _refresh_claude_md(claude_dir)

    return 0, _color(f"Activated prompt: {slug}", GREEN)


def prompt_deactivate(slug: str, home: Path | None = None) -> Tuple[int, str]:
    """Deactivate a prompt by removing it from .active-prompts.

    Args:
        slug: Prompt slug in category/name format
        home: Optional home directory override

    Returns:
        Tuple of (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)

    active_file = claude_dir / ".active-prompts"
    active = _parse_active_entries(active_file)

    if slug not in active:
        return 1, _color(f"Prompt '{slug}' is not active", YELLOW)

    active = [a for a in active if a != slug]
    _write_active_entries(active_file, active)
    _refresh_claude_md(claude_dir)

    return 0, _color(f"Deactivated prompt: {slug}", YELLOW)


def list_prompts(home: Path | None = None) -> str:
    """List all prompts with their status.

    Returns:
        Formatted string with all prompts and their status.
    """
    prompts = discover_prompts(home)

    lines: List[str] = [_color("Available prompts:", BLUE)]

    if not prompts:
        lines.append("  No prompts found")
        lines.append(f"  Create prompts in ~/.cortex/{BASE_PATH}/")
        return "\n".join(lines)

    # Group by category
    by_category: dict[str, List[PromptInfo]] = {}
    for prompt in prompts:
        cat = prompt.category or "(root)"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(prompt)

    for category in sorted(by_category.keys()):
        lines.append(f"\n  {_color(category, BLUE)}:")
        for prompt in by_category[category]:
            if prompt.status == "active":
                status_text = _color(f"{prompt.slug} (active)", GREEN)
            else:
                status_text = f"{prompt.slug} (inactive)"
            tokens_text = f"~{prompt.tokens}t" if prompt.tokens else ""
            lines.append(f"    {status_text} {tokens_text}")

    return "\n".join(lines)


def prompt_status(home: Path | None = None) -> str:
    """Show currently active prompts.

    Returns:
        Formatted string with active prompts.
    """
    claude_dir = _resolve_claude_dir(home)

    active = _parse_active_entries(claude_dir / ".active-prompts")

    lines: List[str] = [_color("Active prompts:", BLUE)]

    if active:
        for slug in sorted(active):
            lines.append(f"  {_color(slug, GREEN)}")
    else:
        lines.append("  None")

    return "\n".join(lines)


def get_prompt_by_slug(slug: str, home: Path | None = None) -> Optional[PromptInfo]:
    """Get a specific prompt by its slug.

    Args:
        slug: Prompt slug in category/name format
        home: Optional home directory override

    Returns:
        PromptInfo if found, None otherwise
    """
    prompts = discover_prompts(home)
    for prompt in prompts:
        if prompt.slug == slug:
            return prompt
    return None
