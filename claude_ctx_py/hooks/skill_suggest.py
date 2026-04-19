"""Suggest relevant skills on UserPromptSubmit by keyword + file + git context.

Exposed to the harness as ``cortex hooks skill-suggest``. Registered in
``~/.claude/settings.json`` by ``cortex hooks install skill-suggest``.

Environment inputs (provided by the Claude Code harness):
    CLAUDE_HOOK_PROMPT     The user prompt text
    CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
    CLAUDE_SKILL_INDEX     Optional override path to skill-index.json
    CLAUDE_SKILL_RULES     Legacy override path to skill-rules.json (fallback)
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


def candidate_rule_paths() -> List[Path]:
    """Return possible locations for the legacy skill-rules.json fallback."""
    paths: List[Path] = []
    if os.getenv("CLAUDE_SKILL_RULES"):
        paths.append(Path(os.environ["CLAUDE_SKILL_RULES"]).expanduser())

    try:
        from ..core.base import _resolve_cortex_root

        paths.append(_resolve_cortex_root() / "skills" / "skill-rules.json")
    except Exception:
        pass

    paths.append(Path.home() / ".claude" / "skills" / "skill-rules.json")
    return paths


def load_entries() -> List[Dict[str, Any]]:
    """Load skill entries from skill-index.json or the legacy fallback.

    Both shapes expose ``name`` and ``keywords`` on each element, which is
    everything ``match_entries`` requires.
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

    for path in candidate_rule_paths():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rules = data.get("rules", [])
        if rules:
            return list(rules)

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


def match_entries(
    prompt: str,
    files: List[str],
    entries: List[Dict[str, Any]],
    max_results: int = 5,
) -> List[Tuple[int, Dict[str, Any]]]:
    """Rank entries by keyword hits against prompt + file + git context."""
    if not entries:
        return []

    prompt_lower = prompt.lower()
    file_text = " ".join(f.lower() for f in files)
    all_keywords = extract_file_context(files) | get_git_context()
    search_text = f"{prompt_lower} {file_text} {' '.join(all_keywords)}"

    matches: List[Tuple[int, Dict[str, Any]]] = []
    for entry in entries:
        keywords = [str(k).lower() for k in entry.get("keywords", [])]
        hits = sum(1 for kw in keywords if kw in search_text)
        if hits > 0:
            matches.append((hits, entry))

    matches.sort(key=lambda item: (-item[0], str(item[1].get("name", ""))))
    return matches[:max_results]


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
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
    changed_files = split_changed_files(os.getenv("CLAUDE_CHANGED_FILES", ""))
    entries = load_entries()

    if not entries:
        return 0

    max_results = 5
    matches = match_entries(prompt, changed_files, entries, max_results=max_results)

    keyword_names = [entry.get("name", "unknown") for _, entry in matches]
    recommender_names = _recommender_suggestions(changed_files, prompt)

    seen: Set[str] = set(keyword_names)
    merged_names = list(keyword_names)
    for name in recommender_names:
        if name not in seen:
            seen.add(name)
            merged_names.append(name)
    merged_names = merged_names[:max_results]

    if merged_names:
        print(f"Suggested skills: {', '.join(merged_names)}")
    return 0


def run() -> int:
    """CLI entrypoint — logs unhandled errors before re-raising."""
    try:
        return main()
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
