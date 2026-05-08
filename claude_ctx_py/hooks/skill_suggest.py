"""Suggest relevant skills on UserPromptSubmit by keyword + file + git context.

Exposed to the harness as ``cortex hooks skill-suggest``. Registered in
``~/.claude/settings.json`` by ``cortex hooks install skill-suggest``.

Environment inputs (provided by the Claude Code harness):
    CLAUDE_HOOK_PROMPT     The user prompt text
    CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
    CLAUDE_SKILL_INDEX     Optional override path to skill-index.json
    CORTEX_ROOT            Absolute path to the Cortex install root

Migrated from ``hooks/skill_auto_suggester.py`` so the hook logic ships with
the installed package and upgrades transparently.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")


# File pattern → keyword mappings for enhanced matching
FILE_PATTERNS: Dict[str, List[str]] = {
    r"test_.*\.py$": ["test", "pytest", "unit"],
    r".*_test\.py$": ["test", "pytest", "unit"],
    r".*\.test\.(ts|tsx|js|jsx)$": ["test", "jest", "unit"],
    r".*\.spec\.(ts|tsx|js|jsx)$": ["test", "spec", "unit"],
    r".*_test\.go$": ["test", "go test"],
    r"dockerfile$": ["docker", "container", "deployment"],
    r"docker-compose\.ya?ml$": ["docker", "container", "orchestration"],
    r"k8s/.*\.ya?ml$": ["kubernetes", "k8s", "deployment"],
    r"terraform/.*\.tf$": ["terraform", "infrastructure"],
    r"\.github/workflows/.*\.ya?ml$": ["ci", "github actions", "workflow"],
    r"jenkinsfile$": ["ci", "jenkins", "pipeline"],
    r".*auth.*\.(py|ts|js|go)$": ["auth", "security"],
    r".*security.*\.(py|ts|js|go)$": ["security", "audit"],
    r".*api.*\.(py|ts|js|go)$": ["api", "endpoint"],
    r".*routes?.*\.(py|ts|js|go)$": ["api", "routing"],
    r"openapi\.ya?ml$": ["api", "openapi", "swagger"],
    r".*\.(tsx|jsx)$": ["react", "frontend", "component"],
    r".*\.vue$": ["vue", "frontend", "component"],
    r".*\.svelte$": ["svelte", "frontend", "component"],
    r".*migrations?/.*\.(py|sql)$": ["database", "migration"],
    r".*models?\.py$": ["database", "orm", "model"],
    r".*schema.*\.(py|ts|graphql)$": ["schema", "database"],
}

DIR_PATTERNS: Dict[str, List[str]] = {
    "tests": ["test", "testing", "pytest"],
    "test": ["test", "testing"],
    "__tests__": ["test", "jest"],
    "spec": ["test", "spec"],
    "e2e": ["e2e", "playwright", "end-to-end"],
    "integration": ["integration", "test"],
    "api": ["api", "endpoint", "rest"],
    "routes": ["api", "routing"],
    "controllers": ["api", "controller"],
    "components": ["react", "frontend", "component"],
    "pages": ["frontend", "routing", "page"],
    "views": ["frontend", "view"],
    "models": ["database", "orm", "model"],
    "migrations": ["database", "migration"],
    "schemas": ["schema", "validation"],
    "auth": ["auth", "security", "authentication"],
    "security": ["security", "audit"],
    "utils": ["utility", "helper"],
    "lib": ["library", "shared"],
    "hooks": ["react", "hooks"],
    "services": ["service", "business logic"],
    "infra": ["infrastructure", "terraform", "deployment"],
    "deploy": ["deployment", "ci", "release"],
    "k8s": ["kubernetes", "k8s", "deployment"],
    "docker": ["docker", "container"],
    ".github": ["ci", "github", "workflow"],
    "workflows": ["workflow", "ci"],
    "scripts": ["script", "automation"],
    "docs": ["documentation", "docs"],
}

EXT_PATTERNS: Dict[str, List[str]] = {
    ".py": ["python"],
    ".ts": ["typescript"],
    ".tsx": ["typescript", "react"],
    ".js": ["javascript"],
    ".jsx": ["javascript", "react"],
    ".go": ["go", "golang"],
    ".rs": ["rust"],
    ".rb": ["ruby"],
    ".java": ["java"],
    ".kt": ["kotlin"],
    ".swift": ["swift"],
    ".tf": ["terraform", "infrastructure"],
    ".sql": ["sql", "database"],
    ".graphql": ["graphql", "api"],
    ".proto": ["protobuf", "grpc"],
    ".yaml": ["yaml", "config"],
    ".yml": ["yaml", "config"],
    ".json": ["json", "config"],
    ".toml": ["toml", "config"],
    ".md": ["markdown", "documentation"],
    ".css": ["css", "styling"],
    ".scss": ["scss", "styling"],
    ".html": ["html", "frontend"],
}


def _read_codex_stdin() -> Dict[str, Any] | None:
    """Detect a Codex hook payload on stdin.

    Codex invokes hooks with a JSON object on stdin (per the Codex Hooks
    API). Claude Code uses env vars and pipes nothing relevant. We
    distinguish them mechanically: env-var presence wins (handled by the
    caller); only when no Claude env signal is set do we look at stdin.

    Returns the parsed dict if stdin contains a JSON object with the
    expected ``hook_event_name`` field, ``None`` otherwise. Robust against
    TTY stdin (manual invocation) and malformed input.
    """
    try:
        if sys.stdin.isatty():
            return None
    except (OSError, ValueError):
        return None
    try:
        text = sys.stdin.read()
    except (OSError, ValueError):
        return None
    if not text.strip():
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and data.get("hook_event_name"):
        return data
    return None


def _git_changed_files() -> List[str]:
    """Best-effort: list files changed vs HEAD (staged + unstaged).

    Used for Codex hook input where the harness does not pass changed
    files directly. Empty list on any failure (not a git repo, git
    missing, etc.) — the prompt-keyword gate still produces correct
    behavior with no context input, just without context-tiebreak.
    """
    import subprocess

    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return []


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
            fh.write(f"{timestamp} [cortex hooks skill-suggest] {message}\n")
    except Exception:
        return


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


def split_changed_files(raw: str) -> List[str]:
    if not raw:
        return []
    return [p.strip() for p in raw.split(":") if p.strip()]


def extract_file_context(files: List[str]) -> Set[str]:
    keywords: Set[str] = set()
    for file_str in files:
        file_path = Path(file_str)
        path_lower = file_str.lower()

        for pattern, pattern_keywords in FILE_PATTERNS.items():
            if re.search(pattern, path_lower, re.IGNORECASE):
                keywords.update(pattern_keywords)

        for part in file_path.parts:
            if part.lower() in DIR_PATTERNS:
                keywords.update(DIR_PATTERNS[part.lower()])

        ext = file_path.suffix.lower()
        if ext in EXT_PATTERNS:
            keywords.update(EXT_PATTERNS[ext])

        name_parts = re.split(r"[_\-./]", file_path.stem.lower())
        keywords.update(p for p in name_parts if len(p) > 2)

    return keywords


def get_git_context() -> Set[str]:
    keywords: Set[str] = set()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip().lower()
            parts = re.split(r"[/_\-]", branch)
            skip_branch = {
                "feature", "fix", "bug", "hotfix", "release",
                "main", "master", "develop",
            }
            keywords.update(p for p in parts if len(p) > 2 and p not in skip_branch)
    except (subprocess.TimeoutExpired, OSError):
        pass

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--format=%s"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            skip_commit = {
                "the", "and", "for", "with", "this", "that", "from", "into",
                "update", "updated", "add", "added", "fix", "fixed",
                "remove", "removed", "change", "changed", "merge", "commit",
            }
            for line in result.stdout.strip().split("\n"):
                words = re.findall(r"\b[a-z]{3,}\b", line.lower())
                keywords.update(w for w in words if w not in skip_commit)
    except (subprocess.TimeoutExpired, OSError):
        pass

    return keywords


#: Weight applied to keyword hits found in the user's prompt. Git and
#: file-context matches count at 1x; prompt matches carry more signal
#: because the user is actively asking about the topic.
PROMPT_HIT_WEIGHT = 3


# Compound tokens (alphanumeric + internal hyphen/underscore) — `doc-001`,
# `test-driven-development`, `auth_handler`. We treat these as atomic so
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
        prompt_tokens[i : i + n] == kw_tokens
        for i in range(len(prompt_tokens) - n + 1)
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
        return [
            rec.skill_name for rec in recommendations if rec.confidence >= 0.7
        ]
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
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": summary,
            }
        }))
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
