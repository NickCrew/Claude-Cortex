"""Suggest specialist subagents on UserPromptSubmit.

Exposed to the harness as ``cortex hooks agent-suggest``. Registered in
``~/.claude/settings.json`` via ``cortex hooks install agent-suggest``.

Two output modes:

- ``Consult: a, b, c`` — agents matched by keyword/file/git context;
  reach out for plan review, explanation, pros/cons, hazard scan,
  design opinion, or rubber-ducking. See ``rules/specialist-consultation.md``.
- ``Delegate: d`` — matched agents whose ``delegate_when:`` aligns with a
  delegation signal in the prompt. Only fires when both conditions hold.

Both lines emit only when they have content. A consultation-capable agent
always appears in ``Consult:`` if keyword-matched; its appearance in
``Delegate:`` is additive, never exclusive.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from .skill_suggest import (
    DIR_PATTERNS,
    EXT_PATTERNS,
    FILE_PATTERNS,
    extract_file_context,
    get_git_context,
    split_changed_files,
)


# Delegation signal -> phrases in the prompt that activate it.
DELEGATE_MARKERS: Dict[str, Tuple[str, ...]] = {
    "isolation": (
        "audit",
        "all files",
        "every file",
        "read through",
        "scan the codebase",
        "sweep",
    ),
    "independence": (
        "review",
        "second opinion",
        "verify independently",
        "get another take",
        "critique",
        "sanity check my",
    ),
    "parallel": (
        "while you",
        "in parallel",
        "at the same time",
        "meanwhile",
    ),
    "large_scope": (
        "comprehensive",
        "entire codebase",
        "every",
        "all of",
        "exhaustive",
        "end to end",
        "end-to-end",
    ),
}


def candidate_index_paths() -> List[Path]:
    paths: List[Path] = []
    if os.getenv("CORTEX_AGENT_INDEX"):
        paths.append(Path(os.environ["CORTEX_AGENT_INDEX"]).expanduser())

    try:
        from ..core.base import _resolve_cortex_root

        paths.append(_resolve_cortex_root() / "agents" / "agent-index.json")
    except Exception:
        pass

    paths.append(Path.home() / ".claude" / "agents" / "agent-index.json")
    return paths


def load_entries() -> List[Dict[str, Any]]:
    for path in candidate_index_paths():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        agents = data.get("agents", [])
        if agents:
            return list(agents)
    return []


def detected_delegation_signals(search_text: str) -> Set[str]:
    """Return the set of delegation signals present in ``search_text``."""
    found: Set[str] = set()
    for signal, phrases in DELEGATE_MARKERS.items():
        for phrase in phrases:
            if phrase in search_text:
                found.add(signal)
                break
    return found


#: See ``claude_ctx_py.hooks.skill_suggest.PROMPT_HIT_WEIGHT`` — same rationale.
PROMPT_HIT_WEIGHT = 3


def match_entries(
    prompt: str,
    files: List[str],
    entries: List[Dict[str, Any]],
) -> List[Tuple[int, Dict[str, Any]]]:
    """Rank agent entries by weighted keyword + file-pattern hits.

    Keyword hits in the user's prompt carry ``PROMPT_HIT_WEIGHT`` points;
    the same keyword in file-context or git-context carries 1 point. File
    pattern matches (glob against changed files) also carry 1 point — those
    are inherently context signals, not prompt-driven.
    """
    if not entries:
        return []

    prompt_lower = prompt.lower()
    file_text = " ".join(f.lower() for f in files)
    context_keywords = extract_file_context(files) | get_git_context()
    context_text = f"{file_text} {' '.join(context_keywords)}"

    matches: List[Tuple[int, Dict[str, Any]]] = []
    for entry in entries:
        prompt_hits = 0
        context_hits = 0
        for kw in entry.get("keywords", []):
            if not isinstance(kw, str) or not kw.strip():
                continue
            kw_lower = kw.lower()
            if kw_lower in prompt_lower:
                prompt_hits += 1
            elif kw_lower in context_text:
                context_hits += 1
        for pattern in entry.get("file_patterns", []):
            if isinstance(pattern, str) and _glob_match_any(pattern, files):
                context_hits += 1
        score = prompt_hits * PROMPT_HIT_WEIGHT + context_hits
        if score > 0:
            matches.append((score, entry))

    matches.sort(key=lambda item: (-item[0], str(item[1].get("name", ""))))
    return matches


def _glob_match_any(pattern: str, files: List[str]) -> bool:
    from fnmatch import fnmatch

    return any(fnmatch(f, pattern) for f in files)


def main() -> int:
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
    changed_files = split_changed_files(os.getenv("CLAUDE_CHANGED_FILES", ""))
    entries = load_entries()
    if not entries:
        return 0

    matches = match_entries(prompt, changed_files, entries)
    if not matches:
        return 0

    prompt_lower = prompt.lower()
    file_text = " ".join(f.lower() for f in changed_files)
    signals = detected_delegation_signals(f"{prompt_lower} {file_text}")

    consult_names: List[str] = []
    delegate_names: List[str] = []
    seen_consult: Set[str] = set()
    seen_delegate: Set[str] = set()

    max_results = 5
    for _, entry in matches[:max_results]:
        name = str(entry.get("name", ""))
        if not name:
            continue
        if name not in seen_consult:
            consult_names.append(name)
            seen_consult.add(name)
        delegate_when = entry.get("delegate_when") or []
        if signals and any(s in signals for s in delegate_when):
            if name not in seen_delegate:
                delegate_names.append(name)
                seen_delegate.add(name)

    if consult_names:
        print(f"Consult: {', '.join(consult_names)}")
    if delegate_names:
        print(f"Delegate: {', '.join(delegate_names)}")
    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:
        try:
            from .skill_suggest import _log_hook

            _log_hook(f"agent-suggest unhandled error: {exc}")
        except Exception:
            pass
        raise
