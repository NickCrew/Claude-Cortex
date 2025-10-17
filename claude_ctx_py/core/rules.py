"""Rule management functions."""

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
    _comment_rule_line,
    _is_disabled,
    _iter_md_files,
    _parse_active_entries,
    _remove_exact_entries,
    _resolve_claude_dir,
    _uncomment_rule_line,
    _update_with_backup
)






def rules_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    active_file = claude_dir / ".active-rules"

    lines: List[str] = [_color("Active rule modules:", BLUE)]

    if active_file.is_file():
        entries = [line.strip() for line in active_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        entries = []

    if entries:
        for rule in entries:
            lines.append(f"  {_color(rule, GREEN)}")
    else:
        lines.append("  None")

    return "\n".join(lines)




def rules_activate(rule: str, home: Path | None = None) -> str:
    """Activate a rule module, mirroring the Bash implementation."""

    claude_dir = _resolve_claude_dir(home)
    claude_dir.mkdir(parents=True, exist_ok=True)

    active_rules = claude_dir / ".active-rules"
    with active_rules.open("a", encoding="utf-8") as handle:
        handle.write(f"{rule}\n")

    claude_md = claude_dir / "CLAUDE.md"
    _update_with_backup(claude_md, lambda content: _uncomment_rule_line(content, rule))

    return _color(f"Activated rule module: {rule}", GREEN)




def rules_deactivate(rule: str, home: Path | None = None) -> str:
    """Deactivate a rule module, restoring comment markers and state."""

    claude_dir = _resolve_claude_dir(home)
    claude_dir.mkdir(parents=True, exist_ok=True)

    active_rules = claude_dir / ".active-rules"
    if active_rules.is_file():
        _update_with_backup(
            active_rules, lambda content: _remove_exact_entries(content, rule)
        )

    claude_md = claude_dir / "CLAUDE.md"
    _update_with_backup(claude_md, lambda content: _comment_rule_line(content, rule))

    return _color(f"Deactivated rule module: {rule}", YELLOW)




def list_rules(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    rules_dir = claude_dir / "rules"
    active_rules_file = claude_dir / ".active-rules"

    active_rules = set(_parse_active_entries(active_rules_file))

    lines: List[str] = [_color("Available rule modules:", BLUE)]
    for path in _iter_md_files(rules_dir):
        if _is_disabled(path):
            continue
        rule_name = path.stem
        if rule_name in active_rules:
            lines.append(f"  {_color(f'{rule_name} (active)', GREEN)}")
        else:
            lines.append(f"  {rule_name} (inactive)")

    return "\n".join(lines)


