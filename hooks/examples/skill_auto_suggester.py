#!/usr/bin/env python3
"""Skill auto-suggestion hook inspired by diet103/claude-code-infrastructure-showcase.

Reads the user prompt and changed files (when provided) and suggests relevant
claude-ctx skills/commands based on `skills/skill-rules.json`.

Usage:
    CLAUDE_HOOK_PROMPT="implement api" hooks/examples/skill_auto_suggester.py
    hooks/examples/skill_auto_suggester.py "fix frontend layout"
    git diff --name-only | hooks/examples/skill_auto_suggester.py

Outputs a markdown block that Claude Code can surface to the user.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_rules() -> List[Dict[str, Any]]:
    rules_path = _repo_root() / "skills" / "skill-rules.json"
    data = json.loads(rules_path.read_text(encoding="utf-8"))
    return data.get("rules", [])


def _read_prompt() -> str:
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "").strip()
    if prompt:
        return prompt

    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    if not sys.stdin.isatty():
        stdin_value = sys.stdin.read().strip()
        if stdin_value:
            return stdin_value

    return ""


def _read_changed_files() -> str:
    files = os.getenv("CLAUDE_CHANGED_FILES", "").strip()
    return files


def main() -> int:
    prompt = _read_prompt().lower()
    files = _read_changed_files().lower()

    if not prompt and not files:
        return 0

    matches: List[Dict[str, Any]] = []
    for rule in _load_rules():
        keywords = [kw.lower() for kw in rule.get("keywords", [])]
        window = " ".join(filter(None, [prompt, files]))
        if any(kw in window for kw in keywords):
            matches.append(rule)

    if not matches:
        return 0

    print("### Suggested claude-ctx skills")
    for match in matches:
        command = match.get("command", "(command missing)")
        desc = match.get("description", "")
        print(f"- `{command}` – {desc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
