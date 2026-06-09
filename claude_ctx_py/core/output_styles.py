"""Output style management.

Output styles are markdown files (with YAML front matter) that Claude Code
loads from ``<claude-dir>/output-styles/`` and applies by name via the
``outputStyle`` key in ``settings.json``.

This module manages them the same way the rest of Cortex manages assets:

- **discover** the styles shipped in the repo's ``output-styles/`` directory,
- **install / uninstall** = create / remove a symlink in
  ``<claude-dir>/output-styles/`` (mirrors ``asset_installer._install_rule``),
- **activate / deactivate** = write the ``outputStyle`` key in ``settings.json``
  (reuses ``hooks.load_settings`` / ``hooks.save_settings``).

The active style is stored as a flat string (e.g. ``"Engineering"``) matching
how Claude Code stores the builtin styles; ``"default"`` means no custom style.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from .base import (
    _clean_scalar,
    _extract_front_matter,
    _resolve_claude_dir,
    _resolve_cortex_root,
    _tokenize_front_matter,
)
from .hooks import load_settings, save_settings

OUTPUT_STYLES_DIRNAME = "output-styles"
DEFAULT_STYLE = "default"
_SETTINGS_KEY = "outputStyle"


@dataclass
class OutputStyle:
    """A discovered output style and its install/active state."""

    slug: str  # filename stem, e.g. "engineering"
    name: str  # front-matter name, e.g. "Engineering" (value written to settings)
    description: str
    source_path: Path
    installed: bool = False
    active: bool = False


def _source_dir() -> Path:
    """Repo directory that ships the output styles."""
    return _resolve_cortex_root() / OUTPUT_STYLES_DIRNAME


def _target_dir() -> Path:
    """Resolved ``<claude-dir>/output-styles`` install location."""
    return _resolve_claude_dir() / OUTPUT_STYLES_DIRNAME


def _parse_style_metadata(path: Path) -> Tuple[str, str]:
    """Return ``(name, description)`` from a style file's front matter.

    Falls back to the filename stem for ``name`` and an empty description when
    the file is unreadable or has no front matter.
    """
    name = path.stem
    description = ""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return name, description

    front_matter = _extract_front_matter(text)
    if not front_matter:
        return name, description

    for indent, line in _tokenize_front_matter(front_matter.splitlines()):
        if indent != 0 or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        if key == "name":
            cleaned = _clean_scalar(value)
            if cleaned:
                name = cleaned
        elif key == "description":
            description = _clean_scalar(value)
    return name, description


def _is_installed(link: Path, source_path: Path) -> bool:
    """True when ``link`` is our symlink to ``source_path`` (or a real file)."""
    try:
        if link.is_symlink():
            return link.resolve() == source_path.resolve()
        return link.is_file()
    except OSError:
        return False


def get_active_output_style() -> str:
    """Return the currently active style name, or ``"default"``."""
    value = load_settings().get(_SETTINGS_KEY, DEFAULT_STYLE)
    return value if isinstance(value, str) else DEFAULT_STYLE


def list_output_styles() -> List[OutputStyle]:
    """Discover output styles in the repo, with install/active state resolved."""
    source_dir = _source_dir()
    if not source_dir.is_dir():
        return []

    target_dir = _target_dir()
    active = get_active_output_style()
    styles: List[OutputStyle] = []
    for md in sorted(source_dir.glob("*.md")):
        name, description = _parse_style_metadata(md)
        link = target_dir / md.name
        styles.append(
            OutputStyle(
                slug=md.stem,
                name=name,
                description=description,
                source_path=md,
                installed=_is_installed(link, md),
                active=(active == name),
            )
        )
    return styles


def get_output_style(slug: str) -> Optional[OutputStyle]:
    """Return the discovered style with the given slug, if any."""
    for style in list_output_styles():
        if style.slug == slug:
            return style
    return None


def install_output_style(slug: str) -> Tuple[int, str]:
    """Symlink a style file into ``<claude-dir>/output-styles`` (idempotent)."""
    source = _source_dir() / f"{slug}.md"
    if not source.is_file():
        return 1, f"Output style not found: {slug}"

    target_dir = _target_dir()
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        link = target_dir / source.name
        # Re-point stale links / replace files (matches the link-repair pattern).
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(source)
    except OSError as e:
        return 1, f"Failed to install output style: {e}"
    return 0, f"Installed output style: {slug}"


def uninstall_output_style(slug: str) -> Tuple[int, str]:
    """Remove the style symlink; reset to default if it was the active style."""
    source = _source_dir() / f"{slug}.md"
    link = _target_dir() / f"{slug}.md"
    if not link.is_symlink() and not link.exists():
        return 1, f"Output style not installed: {slug}"

    name = _parse_style_metadata(source)[0] if source.is_file() else slug
    try:
        link.unlink()
    except OSError as e:
        return 1, f"Failed to uninstall output style: {e}"

    # Don't leave settings.json pointing at a style we just removed.
    if get_active_output_style() == name:
        deactivate_output_style()
    return 0, f"Uninstalled output style: {slug}"


def activate_output_style(slug: str) -> Tuple[int, str]:
    """Set ``outputStyle`` to the style's name, installing it first if needed."""
    source = _source_dir() / f"{slug}.md"
    if not source.is_file():
        return 1, f"Output style not found: {slug}"

    # Claude Code can only apply a style it can find on disk.
    link = _target_dir() / source.name
    if not _is_installed(link, source):
        code, message = install_output_style(slug)
        if code != 0:
            return code, message

    name = _parse_style_metadata(source)[0]
    settings = load_settings()
    settings[_SETTINGS_KEY] = name
    ok, message = save_settings(settings)
    if not ok:
        return 1, message
    return 0, f"Activated output style: {name}"


def deactivate_output_style() -> Tuple[int, str]:
    """Reset ``outputStyle`` to ``"default"``."""
    settings = load_settings()
    settings[_SETTINGS_KEY] = DEFAULT_STYLE
    ok, message = save_settings(settings)
    if not ok:
        return 1, message
    return 0, "Reset output style to default"
