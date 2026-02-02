#!/usr/bin/env python3
"""Block oversized files in changed set.

Hook event: PostToolUse
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build"}
HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")


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


def _skip_path(path: Path) -> bool:
    return any(part in DEFAULT_SKIP_DIRS for part in path.parts)


def _to_mb(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)


def main() -> int:
    warn_mb = float(os.getenv("LARGE_FILE_WARN_MB", "1"))
    block_mb = float(os.getenv("LARGE_FILE_BLOCK_MB", "5"))

    raw = os.getenv("CLAUDE_CHANGED_FILES", "")
    files = _split_changed_files(raw)
    if not files:
        files = _git_changed_files()
    if not files:
        return 0

    warnings: list[str] = []
    blocks: list[str] = []

    for entry in files:
        path = Path(entry)
        if _skip_path(path):
            continue
        if not path.is_file():
            continue
        try:
            size_bytes = path.stat().st_size
        except OSError:
            continue
        size_mb = _to_mb(size_bytes)
        if size_mb >= block_mb:
            blocks.append(f"{path} ({size_mb:.2f} MB)")
        elif size_mb >= warn_mb:
            warnings.append(f"{path} ({size_mb:.2f} MB)")

    if blocks:
        _log_hook("Large file gate blocked: " + "; ".join(blocks))
        print("Large file gate blocked these files:", file=sys.stderr)
        for line in blocks:
            print(f"- {line}", file=sys.stderr)
        print(
            f"Limit is {block_mb:.1f} MB. Reduce size or adjust LARGE_FILE_BLOCK_MB.",
            file=sys.stderr,
        )
        return 1

    if warnings:
        _log_hook("Large file warnings: " + "; ".join(warnings))
        print("Large file warning:", file=sys.stderr)
        for line in warnings:
            print(f"- {line}", file=sys.stderr)
        print(
            f"Warning threshold is {warn_mb:.1f} MB. Consider excluding binaries.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
