"""Shared helpers for Cortex hooks: logging, prompt/file/git context.

Extracted from ``skill_suggest.py``, which had accreted into the de-facto
home for these utilities. Several hooks (``agent_suggest``,
``large_file_gate``, ``commit_cadence``, ``workspace_validator``,
``subagent_output_validator``) depend on them, so they live here in a
neutral module rather than inside any one hook — which lets the
``skill-suggest`` hook be retired without stranding its consumers.

Environment inputs (provided by the Claude Code harness):
    CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
    CORTEX_HOOK_LOG_PATH / CLAUDE_HOOK_LOG_PATH   Optional log path override
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set


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
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        OSError,
        subprocess.TimeoutExpired,
    ):
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
            fh.write(f"{timestamp} [cortex hooks] {message}\n")
    except Exception:
        return


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
                "feature",
                "fix",
                "bug",
                "hotfix",
                "release",
                "main",
                "master",
                "develop",
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
                "the",
                "and",
                "for",
                "with",
                "this",
                "that",
                "from",
                "into",
                "update",
                "updated",
                "add",
                "added",
                "fix",
                "fixed",
                "remove",
                "removed",
                "change",
                "changed",
                "merge",
                "commit",
            }
            for line in result.stdout.strip().split("\n"):
                words = re.findall(r"\b[a-z]{3,}\b", line.lower())
                keywords.update(w for w in words if w not in skip_commit)
    except (subprocess.TimeoutExpired, OSError):
        pass

    return keywords
