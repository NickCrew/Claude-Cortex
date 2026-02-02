"""Utilities for discovering slash command metadata from skills."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .core.base import (
    _extract_front_matter,
    _extract_scalar_from_paths,
    _extract_values_from_paths,
    _is_disabled,
    _tokenize_front_matter,
    _resolve_claude_dir,
)

COMMAND_PATTERN = re.compile(r"/([a-z0-9_-]+):([a-z0-9_-]+)", re.IGNORECASE)


@dataclass
class SlashCommandInfo:
    """Metadata about a slash command definition."""

    command: str
    namespace: str
    name: str
    description: str
    category: str
    complexity: str
    agents: List[str]
    personas: List[str]
    mcp_servers: List[str]
    path: Path
    location: str


def scan_slash_commands(
    skills_dir: Path, *, home_dir: Optional[Path] = None
) -> List[SlashCommandInfo]:
    """Scan a skills directory and return parsed slash command metadata.
    
    Scans for SKILL.md files in the skills directory. Supports both:
    - Flat skills: skills/foo/SKILL.md → /ctx:foo
    - Nested skills: skills/namespace/foo/SKILL.md → /namespace:foo
    
    The command can be overridden via front matter `command:` field.
    """
    if home_dir is None:
        home_dir = _resolve_claude_dir()

    if not skills_dir.is_dir():
        return []

    commands: List[SlashCommandInfo] = []
    for path in sorted(skills_dir.rglob("SKILL.md")):
        if _is_disabled(path):
            continue
        info = _parse_skill_command(path, skills_dir, home_dir)
        if info:
            commands.append(info)

    commands.sort(key=lambda info: (info.namespace.lower(), info.name.lower()))
    return commands


def _parse_skill_command(
    path: Path, skills_dir: Path, home_dir: Optional[Path]
) -> Optional[SlashCommandInfo]:
    """Parse a SKILL.md file into slash command info."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    front_matter = _extract_front_matter(content)
    tokens = {}
    if front_matter:
        tokens = _tokenize_front_matter(front_matter.strip().splitlines())

    # Extract metadata from front matter
    name = _extract_scalar_from_paths(tokens, (("name",),)) or ""
    description = _clean_text(
        _extract_scalar_from_paths(tokens, (("description",),)) or ""
    )
    category = _extract_scalar_from_paths(tokens, (("category",),)) or "general"
    complexity = _extract_scalar_from_paths(tokens, (("complexity",),)) or "standard"
    explicit_command = _extract_scalar_from_paths(tokens, (("command",),)) or ""

    agents = _extract_values_from_paths(tokens, (("agents",),)) or []
    personas = _extract_values_from_paths(tokens, (("personas",),)) or []
    mcp_servers = (
        _extract_values_from_paths(
            tokens, (("mcp-servers",), ("mcp_servers",), ("mcp", "servers"))
        )
        or []
    )

    # Determine command from explicit field or derive from path
    if explicit_command:
        # Use explicit command from front matter
        match = COMMAND_PATTERN.match(explicit_command)
        if match:
            namespace = match.group(1).lower()
            slug = match.group(2).lower()
            command = explicit_command
        else:
            # Malformed command, derive from path
            namespace, slug = _derive_command_from_path(path, skills_dir)
            command = f"/{namespace}:{slug}"
    else:
        # Derive from path
        namespace, slug = _derive_command_from_path(path, skills_dir)
        command = f"/{namespace}:{slug}"

    # Use front matter name if no slug
    if not slug and name:
        slug = _slugify(name)
        command = f"/{namespace}:{slug}"

    if not slug:
        return None

    location = "user"
    if home_dir and home_dir not in path.parents:
        location = "project"

    return SlashCommandInfo(
        command=command,
        namespace=namespace,
        name=slug,
        description=description,
        category=category,
        complexity=complexity,
        agents=agents,
        personas=personas,
        mcp_servers=mcp_servers,
        path=path,
        location=location,
    )


def _derive_command_from_path(path: Path, skills_dir: Path) -> tuple[str, str]:
    """Derive namespace and slug from skill path.
    
    Examples:
        skills/foo/SKILL.md → ("ctx", "foo")
        skills/collaboration/pre_mortem/SKILL.md → ("collaboration", "pre-mortem")
        skills/dev-workflows/SKILL.md → ("ctx", "dev-workflows")
    """
    try:
        relative = path.relative_to(skills_dir)
    except ValueError:
        return ("ctx", path.parent.name)

    parts = relative.parts[:-1]  # Exclude SKILL.md

    if len(parts) == 0:
        return ("ctx", "unknown")
    elif len(parts) == 1:
        # Flat skill: skills/foo/SKILL.md → /ctx:foo
        return ("ctx", _slugify(parts[0]))
    else:
        # Nested skill: skills/namespace/foo/SKILL.md → /namespace:foo
        namespace = _slugify(parts[0])
        slug = _slugify(parts[-1])
        return (namespace, slug)


def _slugify(text: str) -> str:
    """Convert text to a slug suitable for commands."""
    # Replace underscores with hyphens, lowercase
    slug = text.lower().replace("_", "-")
    # Remove any non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _clean_text(value: str) -> str:
    """Clean description text."""
    stripped = value.strip()
    if not stripped:
        return "No description provided"
    return " ".join(stripped.split())
