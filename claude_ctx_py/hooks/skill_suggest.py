"""Suggest relevant skills on UserPromptSubmit by keyword + file + git context.

Exposed to the harness as ``cortex hooks skill-suggest``. Registered in
``~/.claude/settings.json`` by ``cortex hooks install skill-suggest``.

Environment inputs (provided by the Claude Code harness):
    CLAUDE_HOOK_PROMPT     The user prompt text
    CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
    CLAUDE_SKILL_INDEX     Optional override path to skill-index.json
    CORTEX_ROOT            Absolute path to the Cortex install root

Shared context/logging helpers live in ``hooks/_context.py``; this module
keeps only the skill-index ranking logic specific to this hook.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from ._context import (
    _git_changed_files,
    _log_hook,
    _read_codex_stdin,
    extract_file_context,
    get_git_context,
    split_changed_files,
)


def candidate_index_paths() -> List[Path]:
    """Return possible locations for skill-index.json (preferred source)."""
    paths: List[Path] = []
    if os.getenv("CLAUDE_SKILL_INDEX"):
        paths.append(Path(os.environ["CLAUDE_SKILL_INDEX"]).expanduser())

    try:
        from ..core.base import _resolve_cortex_root

        paths.append(_resolve_cortex_root() / "skills" / "skill-index.json")
    except Exception:
        pass

    paths.append(Path.home() / ".claude" / "skills" / "skill-index.json")
    return paths


def load_entries() -> List[Dict[str, Any]]:
    """Load skill entries from skill-index.json.

    Returns an empty list if no readable index is found — callers treat that
    as "no skill suggestions this turn."
    """
    for path in candidate_index_paths():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        skills = data.get("skills", [])
        if skills:
            return list(skills)
    return []


#: Weight applied to keyword hits found in the user's prompt. Git and
#: file-context matches count at 1x; prompt matches carry more signal
#: because the user is actively asking about the topic.
PROMPT_HIT_WEIGHT = 3


# Compound tokens (alphanumeric + internal hyphen/underscore) — `doc-001`,
# `systematic-debugging`, `auth_handler`. We treat these as atomic so
# substrings like `doc` don't false-match inside `doc-001`. Surrounding
# punctuation (commas, periods) is stripped because tokens like `doc.`
# should still match the keyword `doc`.
_PROMPT_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]*", re.IGNORECASE)


def _prompt_tokens(text: str) -> List[str]:
    """Tokenize prompt text into lowercase atoms.

    Whitespace and punctuation (other than internal hyphens/underscores)
    are token boundaries. So `read doc-001 and doc, please` → `['read',
    'doc-001', 'and', 'doc', 'please']` — the standalone 'doc' is its
    own token, but 'doc-001' is one atomic unit and won't substring-match
    the keyword 'doc'.
    """
    return [m.group().lower() for m in _PROMPT_TOKEN_RE.finditer(text)]


def _keyword_matches_prompt(keyword: str, prompt_tokens: List[str]) -> bool:
    """Whole-token match of a (possibly multi-word) keyword against a
    tokenized prompt. Multi-word keywords like `wcag compliance` match
    when their words appear as adjacent tokens."""
    kw_tokens = keyword.lower().split()
    if not kw_tokens or len(kw_tokens) > len(prompt_tokens):
        return False
    n = len(kw_tokens)
    return any(
        prompt_tokens[i : i + n] == kw_tokens for i in range(len(prompt_tokens) - n + 1)
    )


def match_entries(
    prompt: str,
    files: List[str],
    entries: List[Dict[str, Any]],
    max_results: int = 5,
) -> List[Tuple[int, Dict[str, Any]]]:
    """Rank entries by weighted keyword hits.

    A keyword that appears in the user's prompt counts for
    ``PROMPT_HIT_WEIGHT`` points; the same keyword appearing only in
    file-context or git-context counts for 1 point. Prompts with explicit
    intent beat incidental matches from the working tree's git activity.
    """
    if not entries:
        return []

    # Prompt is matched at token-equality (so 'doc' won't false-match
    # inside 'doc-001' or 'documentation'). Context is still substring-
    # matched because it's a tiebreak among prompt-matched entries, not
    # a gate — and shared context naturally contains compound identifiers
    # (file paths, branch names) where token-strict matching would miss
    # legitimate signal.
    prompt_tokens = _prompt_tokens(prompt)
    file_text = " ".join(f.lower() for f in files)
    context_keywords = extract_file_context(files) | get_git_context()
    context_text = f"{file_text} {' '.join(context_keywords)}"

    # Multi-agent shared repos make git log + changed files cross-task
    # pollution rather than personal signal — the only honest indicator of
    # what *this* agent is doing is its own prompt. So we require at least
    # one prompt keyword match before surfacing suggestions, and drop any
    # entry whose hits come purely from shared file/git context. Context
    # still amplifies ranking among prompt-matched entries via the
    # PROMPT_HIT_WEIGHT factor, but it can no longer drive ranking on its
    # own.
    scored: List[Tuple[int, int, Dict[str, Any]]] = []
    saw_prompt_hit = False
    for entry in entries:
        keywords = [str(k).lower() for k in entry.get("keywords", [])]
        prompt_hits = sum(
            1 for kw in keywords if kw and _keyword_matches_prompt(kw, prompt_tokens)
        )
        context_hits = sum(1 for kw in keywords if kw and kw in context_text)
        score = prompt_hits * PROMPT_HIT_WEIGHT + context_hits
        if prompt_hits:
            saw_prompt_hit = True
        if score > 0:
            scored.append((score, prompt_hits, entry))

    if not saw_prompt_hit:
        return []

    prompt_matched = [item for item in scored if item[1] > 0]
    prompt_matched.sort(key=lambda item: (-item[0], str(item[2].get("name", ""))))
    return [(score, entry) for score, _, entry in prompt_matched[:max_results]]


def _recommender_suggestions(
    changed_files: List[str],
    prompt: str,
) -> List[str]:
    """Invoke the SkillRecommender for Layer 2 context-aware recommendations."""
    if os.getenv("CORTEX_SKIP_RECOMMENDER", "").strip() in ("1", "true", "yes"):
        return []

    try:
        from ..intelligence.base import ContextDetector
        from ..skill_recommender import SkillRecommender
    except ImportError:
        return []

    try:
        files = [Path(f) for f in changed_files] if changed_files else []
        if files:
            context = ContextDetector.detect_from_files(files)
        else:
            git_files = ContextDetector.detect_from_git()
            if git_files:
                context = ContextDetector.detect_from_files(git_files)
            elif prompt.strip():
                context = ContextDetector.detect_from_files([])
            else:
                return []

        recommender = SkillRecommender()
        recommendations = recommender.recommend_for_context(context, prompt=prompt)
        return [rec.skill_name for rec in recommendations if rec.confidence >= 0.7]
    except Exception:
        return []


def main() -> int:
    # Dispatch on harness shape: Claude Code passes input via env vars;
    # Codex passes a JSON payload on stdin. The CLAUDE_HOOK_PROMPT env
    # var is the definitive Claude marker — when it's set (even empty)
    # we take the env-var path. Otherwise we look for a Codex payload.
    # Both paths share the same scoring logic and multi-agent gate; only
    # the I/O envelope differs.
    if "CLAUDE_HOOK_PROMPT" in os.environ:
        harness = "claude"
        prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
        changed_files = split_changed_files(os.getenv("CLAUDE_CHANGED_FILES", ""))
    else:
        codex_payload = _read_codex_stdin()
        if codex_payload is None:
            return 0
        harness = "codex"
        prompt = str(codex_payload.get("prompt", ""))
        changed_files = _git_changed_files()

    entries = load_entries()
    if not entries:
        return 0

    max_results = 5
    matches = match_entries(prompt, changed_files, entries, max_results=max_results)

    # Layer 1 returns [] when the prompt fails to match any skill keyword.
    # In a shared multi-agent repo that is the only honest signal we have
    # that *this* agent's task is unrelated to the prevailing file/git
    # context — and any Layer 2 suggestion would just re-import the same
    # cross-task pollution under a fancier ranker. Silence both layers
    # together rather than letting the recommender backdoor noise in.
    if not matches:
        _log_hook(
            f"harness={harness} prompt_len={len(prompt)} silenced=true (no prompt hits)"
        )
        return 0

    keyword_names = [entry.get("name", "unknown") for _, entry in matches]
    recommender_names = _recommender_suggestions(changed_files, prompt)

    seen: Set[str] = set(keyword_names)
    merged_names = list(keyword_names)
    for name in recommender_names:
        if name not in seen:
            seen.add(name)
            merged_names.append(name)
    merged_names = merged_names[:max_results]

    _log_hook(
        f"harness={harness} prompt_len={len(prompt)} "
        f"keyword_matches={len(matches)} recommender={len(recommender_names)} "
        f"top={merged_names}"
    )

    if not merged_names:
        return 0

    summary = f"Suggested skills: {', '.join(merged_names)}"
    if harness == "codex":
        # Codex expects a structured JSON envelope; additionalContext is
        # how hook output reaches the model on the next turn.
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": summary,
                    }
                }
            )
        )
    else:
        print(summary)
    return 0


def run() -> int:
    """CLI entrypoint — logs unhandled errors before re-raising."""
    try:
        return main()
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
