"""Mode management functions."""

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
    _is_disabled,
    _iter_md_files,
    _refresh_claude_md,
    _remove_exact_entries,
    _resolve_claude_dir,
    _update_with_backup
)






def _mode_active_file(claude_dir: Path) -> Path:
    return claude_dir / ".active-modes"




def _mode_inactive_dir(claude_dir: Path) -> Path:
    return claude_dir / "modes" / "inactive"




def mode_activate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = inactive_dir / f"{mode}.md"
    active_path = modes_dir / f"{mode}.md"

    if not inactive_path.is_file():
        return 1, _color(f"Mode '{mode}' not found in inactive modes", RED)

    modes_dir.mkdir(parents=True, exist_ok=True)
    inactive_dir.mkdir(parents=True, exist_ok=True)
    active_path.parent.mkdir(parents=True, exist_ok=True)

    if active_path.exists():
        active_path.unlink()
    inactive_path.replace(active_path)

    active_modes = _mode_active_file(claude_dir)
    with active_modes.open("a", encoding="utf-8") as handle:
        handle.write(f"{mode}\n")

    _refresh_claude_md(claude_dir)
    return 0, _color(f"Activated mode: {mode}", GREEN)




def mode_deactivate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    active_path = modes_dir / f"{mode}.md"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = inactive_dir / f"{mode}.md"

    if not active_path.is_file():
        return 1, _color(f"Mode '{mode}' is not currently active", RED)

    inactive_dir.mkdir(parents=True, exist_ok=True)
    if inactive_path.exists():
        inactive_path.unlink()
    active_path.replace(inactive_path)

    active_modes = _mode_active_file(claude_dir)
    if active_modes.is_file():
        _update_with_backup(
            active_modes, lambda content: _remove_exact_entries(content, mode)
        )
    else:
        active_modes.touch(exist_ok=True)

    _refresh_claude_md(claude_dir)

    return 0, _color(f"Deactivated mode: {mode}", YELLOW)




def list_modes(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"

    lines: List[str] = [_color("Available modes:", BLUE)]

    inactive_dir = modes_dir / "inactive"
    for path in _iter_md_files(inactive_dir):
        lines.append(f"  {path.stem} (inactive)")

    disabled_dir = modes_dir / "disabled"
    for path in _iter_md_files(disabled_dir):
        lines.append(f"  {path.stem} (disabled)")

    for path in _iter_md_files(modes_dir):
        if _is_disabled(path):
            continue
        lines.append(f"  {_color(f'{path.stem} (active)', GREEN)}")

    return "\n".join(lines)




def mode_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    active_file = claude_dir / ".active-modes"

    lines: List[str] = [_color("Active modes:", BLUE)]
    if active_file.is_file():
        for raw in active_file.read_text(encoding="utf-8").splitlines():
            lines.append(f"  {_color(raw, GREEN)}")
    else:
        lines.append("  None")
    return "\n".join(lines)


