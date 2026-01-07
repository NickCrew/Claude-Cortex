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
    _extract_front_matter,
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


def _extract_command_name(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    front_matter = _extract_front_matter(content)
    if not front_matter:
        return None

    for line in front_matter.splitlines():
        if not line.strip().startswith("name:"):
            continue
        value = line.split(":", 1)[1].strip()
        if not value:
            return None
        if value[0] in ("'", '"') and value[-1:] == value[0]:
            value = value[1:-1]
        return value or None
    return None


def _command_target_filename(path: Path, namespace: str | None) -> str:
    name = _extract_command_name(path)
    if name:
        if ":" in name:
            return f"{name.replace(':', '-')}.md"
        if namespace:
            return f"{namespace}-{name}.md"
        return f"{name}.md"
    if namespace:
        return f"{namespace}-{path.stem}.md"
    return f"{path.stem}.md"


def _backup_path(path: Path) -> Path:
    candidate = path.with_suffix(path.suffix + ".bak")
    if not candidate.exists():
        return candidate
    index = 1
    while True:
        candidate = path.with_suffix(path.suffix + f".bak{index}")
        if not candidate.exists():
            return candidate
        index += 1


def migrate_commands_layout(
    home: Path | None = None,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> Tuple[int, str]:
    """Flatten commands/ into a single directory and move README files out."""
    claude_dir = _resolve_claude_dir(home)
    commands_dir = claude_dir / "commands"
    if not commands_dir.exists():
        return 0, _color("No commands directory found", YELLOW)

    moved = 0
    skipped = 0
    readmes = 0
    overwritten = 0
    warnings: List[str] = []

    docs_dir = claude_dir / "docs" / "commands"
    readme_files = list(commands_dir.rglob("README.md"))
    for readme in readme_files:
        if not readme.is_file():
            continue
        target = docs_dir / ("index.md" if readme.parent == commands_dir else f"{readme.parent.name}.md")
        if target.exists():
            if not force:
                warnings.append(_color(f"Skipped README (exists): {target}", YELLOW))
                continue
            overwritten += 1
            if not dry_run:
                backup = _backup_path(target)
                target.rename(backup)
        if not dry_run:
            docs_dir.mkdir(parents=True, exist_ok=True)
            readme.rename(target)
        readmes += 1

    command_files = [p for p in commands_dir.rglob("*.md") if p.is_file()]
    for path in command_files:
        if path.name == "README.md":
            continue
        namespace = None
        if path.parent != commands_dir:
            namespace = path.parent.name
        target_name = _command_target_filename(path, namespace)
        target = commands_dir / target_name
        if path == target:
            continue
        if target.exists():
            if not force:
                warnings.append(_color(f"Skipped (exists): {target.name}", YELLOW))
                skipped += 1
                continue
            overwritten += 1
            if not dry_run:
                backup = _backup_path(target)
                target.rename(backup)
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
        moved += 1

    # Clean up empty subdirectories
    if not dry_run:
        for subdir in [p for p in commands_dir.iterdir() if p.is_dir()]:
            try:
                subdir.rmdir()
            except OSError:
                continue

    prefix = "Dry run: " if dry_run else ""
    message = _color(
        f"{prefix}Commands flattened: moved {moved}, overwrote {overwritten}, "
        f"skipped {skipped}, readmes moved {readmes}",
        GREEN,
    )
    if warnings:
        message = " | ".join([message, *warnings])
    return 0, message
