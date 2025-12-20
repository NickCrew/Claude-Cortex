"""Migration helpers for moving CLAUDE.md comment-based activation to file-based."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .base import (
    _resolve_claude_dir,
    _inactive_category_dir,
    _write_active_entries,
    _refresh_claude_md,
    _parse_claude_md_refs,
    GREEN,
    YELLOW,
    RED,
    _color,
)


def _migrate_category(claude_dir: Path, category: str) -> Tuple[int, str]:
    """Migrate a single category (rules/modes) from CLAUDE.md refs to files."""
    active_refs = _parse_claude_md_refs(claude_dir, category)
    if not active_refs:
        return 0, _color(f"No {category} references found in CLAUDE.md", YELLOW)

    active_dir = claude_dir / category
    inactive_dir = _inactive_category_dir(claude_dir, category)
    active_dir.mkdir(parents=True, exist_ok=True)
    inactive_dir.mkdir(parents=True, exist_ok=True)

    activated: List[str] = []
    missing: List[str] = []

    for slug in sorted(active_refs):
        name = slug.split("/")[-1]
        filename = f"{name}.md" if not name.endswith(".md") else name
        active_path = active_dir / filename
        inactive_path = inactive_dir / filename

        if active_path.exists():
            activated.append(active_path.stem)
            continue

        if inactive_path.exists():
            inactive_path.rename(active_path)
            activated.append(active_path.stem)
            continue

        # Not found anywhere
        missing.append(filename)

    if activated:
        _write_active_entries(claude_dir / f".active-{category}", activated)

    message_parts: List[str] = []
    if activated:
        message_parts.append(
            _color(f"Activated {len(activated)} {category}: {', '.join(activated)}", GREEN)
        )
    if missing:
        message_parts.append(
            _color(f"Missing {category}: {', '.join(missing)} (install manually)", RED)
        )

    if not message_parts:
        message_parts.append(_color(f"No changes for {category}", YELLOW))

    return (0 if not missing else 1), " | ".join(message_parts)


def migrate_to_file_activation(home: Path | None = None) -> Tuple[int, str]:
    """Migrate rules/modes to file-based activation and refresh CLAUDE.md."""
    claude_dir = _resolve_claude_dir(home)

    codes: List[int] = []
    messages: List[str] = []

    for category in ("rules", "modes"):
        code, msg = _migrate_category(claude_dir, category)
        codes.append(code)
        messages.append(msg)

    _refresh_claude_md(claude_dir)

    overall = 0 if all(code == 0 for code in codes) else 1
    return overall, " | ".join(messages)
