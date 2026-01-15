#!/usr/bin/env python3
"""Block oversized files in changed set.

Hook event: PostToolUse
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

DEFAULT_SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build"}


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
        print("Large file gate blocked these files:", file=sys.stderr)
        for line in blocks:
            print(f"- {line}", file=sys.stderr)
        print(
            f"Limit is {block_mb:.1f} MB. Reduce size or adjust LARGE_FILE_BLOCK_MB.",
            file=sys.stderr,
        )
        return 1

    if warnings:
        print("Large file warning:", file=sys.stderr)
        for line in warnings:
            print(f"- {line}", file=sys.stderr)
        print(
            f"Warning threshold is {warn_mb:.1f} MB. Consider excluding binaries.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
