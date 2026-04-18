"""Skill activation lookup: map free text to matching skill names via skill-index.json.

Powers ``cortex skills analyze <text>``. Reads the unified skill index (either
the user-local copy under ``~/.claude/skills/`` or the bundled Cortex repo copy)
and returns every skill whose keywords appear as substrings of the input.

Zero-YAML by design — the legacy ``skills/activation.yaml`` is no longer read
from here. Users who haven't regenerated their index after upgrading should run
``cortex skills rebuild-index`` once.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .core.base import _resolve_cortex_root


def load_activation_map(claude_dir: Path) -> Dict[str, List[str]]:
    """Return a ``{skill_name: [lowercased keywords]}`` map from skill-index.json.

    Preference order: the user's installed copy (``claude_dir/skills/skill-index.json``),
    then the bundled Cortex repo copy. Returns ``{}`` if neither is readable —
    callers treat that as "no skills matched".
    """
    for candidate in _index_candidates(claude_dir):
        if not candidate.exists():
            continue
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        skills = data.get("skills") or []
        if not skills:
            continue
        return {
            str(entry["name"]): [
                str(kw).lower()
                for kw in (entry.get("keywords") or [])
                if isinstance(kw, str) and kw.strip()
            ]
            for entry in skills
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
    return {}


def _index_candidates(claude_dir: Path) -> List[Path]:
    candidates = [claude_dir / "skills" / "skill-index.json"]
    try:
        bundled = _resolve_cortex_root() / "skills" / "skill-index.json"
        if bundled != candidates[0]:
            candidates.append(bundled)
    except Exception:
        pass
    return candidates


def analyze_text(text: str, claude_dir: Path) -> List[str]:
    """Return the sorted set of skill names whose keywords appear in ``text``."""
    activation_map = load_activation_map(claude_dir)
    if not activation_map:
        return []
    text_lower = text.lower()
    return sorted(
        name
        for name, keywords in activation_map.items()
        if any(keyword in text_lower for keyword in keywords)
    )


def suggest_skills(text: str, claude_dir: Path) -> str:
    """Format the ``analyze_text`` result for CLI output."""
    matches = analyze_text(text, claude_dir)
    if not matches:
        return "No matching skills found for the provided text."
    lines = [f"Found {len(matches)} matching skill(s):", ""]
    lines.extend(f"  - {name}" for name in matches)
    lines.append("")
    lines.append("To view skill details, run: cortex skills info <skill-name>")
    return "\n".join(lines)
