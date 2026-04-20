"""Detect hallucinated file references in subagent outputs.

Exposed to the harness as ``cortex hooks subagent-output-validator``.
Registered in ``~/.claude/settings.json`` via
``cortex hooks install subagent-output-validator``.

Hook event: SubagentStop.

Returns exit 1 (with warning messages on stderr) when the subagent claims to
have created files that do not exist on disk. Other reference-path misses
are logged only — this is a detection aid, not a strict blocker.

Environment variables:
- ``CLAUDE_SUBAGENT_OUTPUT``: text output from the completed subagent.
- ``CLAUDE_WORKING_DIRECTORY``: cwd against which relative paths resolve
  (defaults to ``os.getcwd()``).
"""

from __future__ import annotations

import os
import re
import sys
from glob import glob
from pathlib import Path
from typing import List, Set, Tuple

from .skill_suggest import _log_hook


WARNING_THRESHOLD = 3

PATH_PATTERNS = [
    re.compile(r"(/(?:Users|home|var|tmp|etc|opt)[^\s\"\'\)\]\}:,]+)"),
    re.compile(
        r"(?:^|[\s\"\'\(\[\{:,])"
        r"([a-zA-Z0-9_\-./]+\.(?:rs|ts|tsx|js|jsx|py|go|java|json|yaml|yml|toml|md))"
        r"(?:[\s\"\'\)\]\}:,]|$)"
    ),
    re.compile(
        r"(?:^|[\s\"\'\(\[\{:,])"
        r"((?:src|apps|packages|libs|tests|test)/[a-zA-Z0-9_\-./]+)"
        r"(?:[\s\"\'\)\]\}:,]|$)"
    ),
]

CREATION_INDICATORS = [
    re.compile(
        r"(?:created|wrote|modified|updated|added|implemented)\s+"
        r"(?:the\s+)?(?:file\s+)?[`'\"]?"
        r"([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)[`'\"]?",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:new\s+file|new\s+test|added)\s*[:\s]+[`'\"]?"
        r"([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)[`'\"]?",
        re.IGNORECASE,
    ),
]


def _extract_paths(text: str) -> Set[str]:
    paths: Set[str] = set()
    for pattern in PATH_PATTERNS:
        for match in pattern.finditer(text):
            path = match.group(1).strip().rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)
    return paths


def _extract_claimed_creations(text: str) -> Set[str]:
    paths: Set[str] = set()
    for pattern in CREATION_INDICATORS:
        for match in pattern.finditer(text):
            path = match.group(1).strip().rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)
    return paths


def _path_exists(path_str: str, cwd: Path) -> bool:
    path = Path(path_str)
    if path.is_absolute():
        return path.exists()
    if (cwd / path).exists():
        return True
    if "*" in path_str:
        return bool(glob(str(cwd / path_str), recursive=True))
    return False


def validate_output(output: str, cwd: str) -> Tuple[List[str], List[str]]:
    """Return ``(missing_referenced_paths, missing_claimed_creations)``."""
    cwd_path = Path(cwd)
    all_paths = _extract_paths(output)
    missing_refs = [p for p in all_paths if not _path_exists(p, cwd_path)]
    claimed = _extract_claimed_creations(output)
    missing_claimed = [p for p in claimed if not _path_exists(p, cwd_path)]
    return missing_refs, missing_claimed


def main() -> int:
    output = os.getenv("CLAUDE_SUBAGENT_OUTPUT", "")
    cwd = os.getenv("CLAUDE_WORKING_DIRECTORY", os.getcwd())
    if not output:
        return 0

    missing_refs, missing_claimed = validate_output(output, cwd)

    if missing_claimed:
        _log_hook(
            f"subagent-output-validator: agent claimed to create "
            f"{len(missing_claimed)} files that don't exist: "
            f"{missing_claimed[:5]}"
        )
        print(
            "[subagent-output-validator] Warning: agent claimed to create "
            "files that don't exist:",
            file=sys.stderr,
        )
        for path in missing_claimed[:5]:
            print(f"  - {path}", file=sys.stderr)
        if len(missing_claimed) > 5:
            print(f"  ... and {len(missing_claimed) - 5} more", file=sys.stderr)
        return 1

    if len(missing_refs) >= WARNING_THRESHOLD:
        _log_hook(
            f"subagent-output-validator: {len(missing_refs)} referenced "
            f"paths don't exist: {missing_refs[:5]}"
        )
        print(
            f"[subagent-output-validator] Warning: {len(missing_refs)} "
            "referenced paths don't exist",
            file=sys.stderr,
        )

    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:
        try:
            _log_hook(f"subagent-output-validator unhandled error: {exc}")
        except Exception:
            pass
        raise
