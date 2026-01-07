"""Utilities for discovering slash command metadata."""

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
    commands_dir: Path, *, home_dir: Optional[Path] = None
) -> List[SlashCommandInfo]:
    """Scan a commands directory and return parsed slash command metadata."""

    if home_dir is None:
        home_dir = _resolve_claude_dir()

    if not commands_dir.is_dir():
        return []

    commands: List[SlashCommandInfo] = []
    for path in sorted(commands_dir.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        if _is_disabled(path):
            continue
        info = _parse_slash_command(path, commands_dir, home_dir)
        if info:
            commands.append(info)

    commands.sort(key=lambda info: (info.namespace.lower(), info.name.lower()))
    return commands


def _parse_slash_command(
    path: Path, commands_dir: Path, home_dir: Optional[Path]
) -> Optional[SlashCommandInfo]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    front_matter = _extract_front_matter(content)
    if not front_matter:
        return None

    tokens = _tokenize_front_matter(front_matter.strip().splitlines())

    name = _extract_scalar_from_paths(tokens, (("name",),)) or path.stem
    description = _clean_text(
        _extract_scalar_from_paths(tokens, (("description",),)) or ""
    )
    category = _extract_scalar_from_paths(tokens, (("category",),)) or "general"
    complexity = _extract_scalar_from_paths(tokens, (("complexity",),)) or "standard"

    agents = _extract_values_from_paths(tokens, (("agents",),)) or []
    personas = _extract_values_from_paths(tokens, (("personas",),)) or []
    mcp_servers = (
        _extract_values_from_paths(
            tokens, (("mcp-servers",), ("mcp_servers",), ("mcp", "servers"))
        )
        or []
    )

    namespace = _detect_namespace(content, path, commands_dir)
    slug = name.strip() or path.stem

    location = "user"
    if home_dir and home_dir not in path.parents:
        location = "project"

    return SlashCommandInfo(
        command=f"/{namespace}:{slug}",
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


def _detect_namespace(content: str, path: Path, commands_dir: Path) -> str:
    match = COMMAND_PATTERN.search(content)
    if match:
        return match.group(1).lower()

    try:
        relative_parts = path.relative_to(commands_dir).parts
    except ValueError:
        relative_parts = path.parts

    if len(relative_parts) > 1:
        candidate = relative_parts[0]
    else:
        candidate = path.parent.name

    candidate = candidate or "ctx"
    candidate = candidate.lower()
    if candidate == "commands":
        candidate = "ctx"
    return candidate


def _clean_text(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return "No description provided"
    return " ".join(stripped.split())
