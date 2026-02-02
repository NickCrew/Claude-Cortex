#!/usr/bin/env python3
"""Validate subagent outputs for hallucinated file references.

Detects when subagents claim to have worked on files that don't exist,
logging warnings for post-mortem analysis.

Hook event: SubagentStop

Environment variables:
- CLAUDE_SUBAGENT_OUTPUT: Output from the completed subagent
- CLAUDE_WORKING_DIRECTORY: Current working directory
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime
from glob import glob
from pathlib import Path


HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")

# Threshold for logging warnings (not blocking)
WARNING_THRESHOLD = 3

# Patterns to extract file paths from output
PATH_PATTERNS = [
    # Absolute paths
    re.compile(r"(/(?:Users|home|var|tmp|etc|opt)[^\s\"\'\)\]\}:,]+)"),
    # Relative paths with file extensions
    re.compile(r"(?:^|[\s\"\'\(\[\{:,])([a-zA-Z0-9_\-./]+\.(?:rs|ts|tsx|js|jsx|py|go|java|json|yaml|yml|toml|md))(?:[\s\"\'\)\]\}:,]|$)"),
    # src/ or apps/ or packages/ relative paths
    re.compile(r"(?:^|[\s\"\'\(\[\{:,])((?:src|apps|packages|libs|tests|test)/[a-zA-Z0-9_\-./]+)(?:[\s\"\'\)\]\}:,]|$)"),
]

# Patterns that indicate the agent claims to have created/modified files
CREATION_INDICATORS = [
    re.compile(r"(?:created|wrote|modified|updated|added|implemented)\s+(?:the\s+)?(?:file\s+)?[`'\"]?([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)[`'\"]?", re.IGNORECASE),
    re.compile(r"(?:new\s+file|new\s+test|added)\s*[:\s]+[`'\"]?([a-zA-Z0-9_\-./]+\.[a-zA-Z]+)[`'\"]?", re.IGNORECASE),
]


def _hook_log_path() -> Path:
    for name in HOOK_LOG_ENV:
        value = os.getenv(name, "").strip()
        if value:
            return Path(value).expanduser()
    return Path.home() / ".claude" / "logs" / "hooks.log"


def _log_hook(message: str) -> None:
    try:
        path = _hook_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} [{Path(__file__).name}] {message}\n")
    except Exception:
        return


def _extract_paths(text: str) -> set[str]:
    """Extract file paths from text."""
    paths: set[str] = set()

    for pattern in PATH_PATTERNS:
        for match in pattern.finditer(text):
            path = match.group(1).strip()
            path = path.rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)

    return paths


def _extract_claimed_creations(text: str) -> set[str]:
    """Extract files the agent claims to have created/modified."""
    paths: set[str] = set()

    for pattern in CREATION_INDICATORS:
        for match in pattern.finditer(text):
            path = match.group(1).strip()
            path = path.rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)

    return paths


def _path_exists(path_str: str, cwd: Path) -> bool:
    """Check if a path exists."""
    path = Path(path_str)

    if path.is_absolute():
        return path.exists()

    full_path = cwd / path
    if full_path.exists():
        return True

    if "*" in path_str:
        matches = glob(str(cwd / path_str), recursive=True)
        return len(matches) > 0

    return False


def validate_output(output: str, cwd: str) -> tuple[list[str], list[str]]:
    """Validate subagent output for hallucinated file references.

    Returns:
        Tuple of (missing_referenced_paths, missing_claimed_creations)
    """
    cwd_path = Path(cwd)

    # Extract all referenced paths
    all_paths = _extract_paths(output)
    missing_refs = [p for p in all_paths if not _path_exists(p, cwd_path)]

    # Extract files claimed to have been created
    claimed = _extract_claimed_creations(output)
    missing_claimed = [p for p in claimed if not _path_exists(p, cwd_path)]

    return missing_refs, missing_claimed


def main() -> int:
    output = os.getenv("CLAUDE_SUBAGENT_OUTPUT", "")
    cwd = os.getenv("CLAUDE_WORKING_DIRECTORY", os.getcwd())

    if not output:
        return 0

    missing_refs, missing_claimed = validate_output(output, cwd)

    # Log if we found potential hallucinations
    if missing_claimed:
        _log_hook(f"HALLUCINATION WARNING: Agent claimed to create {len(missing_claimed)} files that don't exist: {missing_claimed[:5]}")
        print(f"[subagent_output_validator] Warning: Agent claimed to create files that don't exist:", file=sys.stderr)
        for path in missing_claimed[:5]:
            print(f"  - {path}", file=sys.stderr)
        if len(missing_claimed) > 5:
            print(f"  ... and {len(missing_claimed) - 5} more", file=sys.stderr)

    if len(missing_refs) >= WARNING_THRESHOLD:
        _log_hook(f"PATH WARNING: {len(missing_refs)} referenced paths don't exist: {missing_refs[:5]}")
        print(f"[subagent_output_validator] Warning: {len(missing_refs)} referenced paths don't exist", file=sys.stderr)

    # This is a detection hook, not a blocker - always return 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
