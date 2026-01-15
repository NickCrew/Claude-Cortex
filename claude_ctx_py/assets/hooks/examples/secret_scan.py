#!/usr/bin/env python3
"""Scan changed files for common secret patterns.

Hook event: PostToolUse
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r"(?i)aws(.{0,20})?(secret|access)?_?key[^\n]{0,10}['\"][A-Za-z0-9/+=]{40}['\"]"),
    "github_token": re.compile(r"ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}"),
    "google_api_key": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    "slack_token": re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,48}"),
    "stripe_secret": re.compile(r"sk_(live|test)_[0-9a-zA-Z]{24,}"),
    "private_key": re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----"),
}

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


def _is_binary(sample: bytes) -> bool:
    return b"\x00" in sample


def _scan_file(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError:
        return []
    if _is_binary(data[:2048]):
        return []
    text = data.decode("utf-8", errors="ignore")
    findings: list[str] = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            findings.append(name)
    return findings


def main() -> int:
    raw = os.getenv("CLAUDE_CHANGED_FILES", "")
    files = _split_changed_files(raw)
    if not files:
        files = _git_changed_files()
    if not files:
        return 0

    hits: list[str] = []
    for entry in files:
        path = Path(entry)
        if _skip_path(path):
            continue
        if not path.is_file():
            continue
        findings = _scan_file(path)
        if findings:
            hits.append(f"{path}: {', '.join(findings)}")

    if hits:
        print("Potential secrets detected:", file=sys.stderr)
        for line in hits:
            print(f"- {line}", file=sys.stderr)
        print("Resolve or remove secrets before continuing.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
