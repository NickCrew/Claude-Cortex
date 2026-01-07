#!/usr/bin/env python3
"""
Suggest relevant /ctx:* skills based on the user's prompt and changed files.

Hook event: UserPromptSubmit
Register in hooks/hooks.json with:
  "command": "python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/examples/skill_auto_suggester.py"]
Environment:
  CLAUDE_HOOK_PROMPT     The user prompt text (provided by Claude Code)
  CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
  CLAUDE_SKILL_RULES     Optional override path to skill-rules.json

The hook reads skill keywords from skills/skill-rules.json (or the override) and
prints the top matching skills. No suggestions → silent success (exit 0).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


def candidate_rule_paths() -> List[Path]:
    """Return possible locations for skill-rules.json."""
    paths = []
    if os.getenv("CLAUDE_SKILL_RULES"):
        paths.append(Path(os.environ["CLAUDE_SKILL_RULES"]).expanduser())

    script_path = Path(__file__).resolve()
    repo_rules = script_path.parents[2] / "skills" / "skill-rules.json"
    paths.append(repo_rules)

    home_rules = Path.home() / ".claude" / "skills" / "skill-rules.json"
    paths.append(home_rules)

    return paths


def load_rules() -> list:
    """Load rules from the first readable candidate path."""
    for path in candidate_rule_paths():
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        rules = data.get("rules", [])
        if rules:
            return rules
    return []


def split_changed_files(raw: str) -> List[str]:
    """Parse CLAUDE_CHANGED_FILES into a list."""
    if not raw:
        return []
    # Colon is the typical separator; fall back to newline/space.
    parts: Iterable[str] = raw.split(":")
    files: List[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        files.append(part)
    return files


def match_rules(prompt: str, files: List[str], rules: list) -> List[Tuple[int, dict]]:
    """Return rules with at least one keyword match, sorted by hit count."""
    prompt_l = prompt.lower()
    files_l = " ".join(f.lower() for f in files)
    matches: List[Tuple[int, dict]] = []
    for rule in rules:
        keywords = [k.lower() for k in rule.get("keywords", [])]
        hits = sum(1 for kw in keywords if kw in prompt_l or kw in files_l)
        if hits > 0:
            matches.append((hits, rule))
    matches.sort(key=lambda item: (-item[0], item[1].get("name", "")))
    return matches[:5]


def print_suggestions(matches: List[Tuple[int, dict]]) -> None:
    """Emit suggestions in a compact, readable format."""
    if not matches:
        return
    print("Skill suggestions:")
    for hits, rule in matches:
        name = rule.get("name", "unknown")
        cmd = rule.get("command", "")
        desc = rule.get("description", "").strip()
        print(f"- {cmd} — {desc} (matched {hits} keyword{'s' if hits != 1 else ''})")


def main() -> int:
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
    changed_files = split_changed_files(os.getenv("CLAUDE_CHANGED_FILES", ""))
    rules = load_rules()

    if not rules:
        # Fail silently to avoid breaking the submit flow.
        return 0

    matches = match_rules(prompt, changed_files, rules)
    print_suggestions(matches)
    return 0


if __name__ == "__main__":
    sys.exit(main())
