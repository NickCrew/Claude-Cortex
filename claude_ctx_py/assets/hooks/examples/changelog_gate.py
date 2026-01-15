#!/usr/bin/env python3
"""Require changelog updates when release-like changes occur.

Hook event: SessionEnd
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

VERSION_FILES = {
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "Cargo.toml",
    "VERSION",
    "version.txt",
}

RELEASE_KEYWORDS = re.compile(r"\b(release|version|bump|publish|ship|changelog)\b", re.I)


def _split_changed_files(raw: str) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(":" ) if part.strip()]


def _git_changed_files() -> list[str]:
    try:
        cached = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).splitlines()
    except Exception:
        cached = []
    if cached:
        return cached
    try:
        return subprocess.check_output(
            ["git", "diff", "--name-only"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).splitlines()
    except Exception:
        return []


def _needs_changelog(changed: list[str], context: str) -> bool:
    if any(Path(path).name == "CHANGELOG.md" for path in changed):
        return False
    if any(Path(path).name in VERSION_FILES for path in changed):
        return True
    if RELEASE_KEYWORDS.search(context):
        return True
    return False


def main() -> int:
    raw = os.getenv("CLAUDE_CHANGED_FILES", "")
    changed = _split_changed_files(raw)
    if not changed:
        changed = _git_changed_files()
    if not changed:
        return 0

    context = (os.getenv("CLAUDE_SESSION_CONTEXT", "") + "\n" + os.getenv("CLAUDE_HOOK_PROMPT", "")).strip()

    if _needs_changelog(changed, context):
        print("Changelog gate: CHANGELOG.md was not updated.", file=sys.stderr)
        print("Update CHANGELOG.md for release/version changes before closing.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
