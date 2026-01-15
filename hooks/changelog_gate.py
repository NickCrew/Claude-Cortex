#!/usr/bin/env python3
"""Require changelog updates when release-like changes occur.

Hook event: SessionEnd
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
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
HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")


def _hook_log_path() -> Path:
    for name in HOOK_LOG_ENV:
        value = os.getenv(name, "").strip()
        if value:
            return Path(value).expanduser()
    return Path.home() / ".cortex" / "logs" / "hooks.log"


def _log_hook(message: str) -> None:
    try:
        path = _hook_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} [{Path(__file__).name}] {message}\n")
    except Exception:
        return


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
        _log_hook("Changelog gate failed: CHANGELOG.md missing.")
        print("Changelog gate: CHANGELOG.md was not updated.", file=sys.stderr)
        print("Update CHANGELOG.md for release/version changes before closing.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
