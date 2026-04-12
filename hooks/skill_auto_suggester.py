#!/usr/bin/env python3
"""
Suggest relevant /ctx:* skills based on the user's prompt and changed files.

Hook event: UserPromptSubmit

Register in ~/.claude/settings.json (or install via `cortex tui` → Hooks view).
A typical entry looks like:
  {
    "type": "command",
    "command": "python3 ${CORTEX_ROOT}/hooks/skill_auto_suggester.py"
  }

Environment:
  CLAUDE_HOOK_PROMPT     The user prompt text (provided by Claude Code)
  CLAUDE_CHANGED_FILES   Optional colon-separated list of changed files
  CLAUDE_SKILL_RULES     Optional override path to skill-rules.json
  CORTEX_ROOT            Absolute path to the Cortex install root (set by
                         Cortex; used to locate bundled rules and scripts)

The hook reads skill keywords from skills/skill-rules.json (or the override) and
prints the top matching skills. No suggestions → silent success (exit 0).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")

# File pattern → keyword mappings for enhanced matching
FILE_PATTERNS: Dict[str, List[str]] = {
    # Test files
    r"test_.*\.py$": ["test", "pytest", "unit"],
    r".*_test\.py$": ["test", "pytest", "unit"],
    r".*\.test\.(ts|tsx|js|jsx)$": ["test", "jest", "unit"],
    r".*\.spec\.(ts|tsx|js|jsx)$": ["test", "spec", "unit"],
    r".*_test\.go$": ["test", "go test"],
    # Config files
    r"dockerfile$": ["docker", "container", "deployment"],
    r"docker-compose\.ya?ml$": ["docker", "container", "orchestration"],
    r"k8s/.*\.ya?ml$": ["kubernetes", "k8s", "deployment"],
    r"terraform/.*\.tf$": ["terraform", "infrastructure"],
    r"\.github/workflows/.*\.ya?ml$": ["ci", "github actions", "workflow"],
    r"jenkinsfile$": ["ci", "jenkins", "pipeline"],
    # Security
    r".*auth.*\.(py|ts|js|go)$": ["auth", "security"],
    r".*security.*\.(py|ts|js|go)$": ["security", "audit"],
    # API
    r".*api.*\.(py|ts|js|go)$": ["api", "endpoint"],
    r".*routes?.*\.(py|ts|js|go)$": ["api", "routing"],
    r"openapi\.ya?ml$": ["api", "openapi", "swagger"],
    # Frontend
    r".*\.(tsx|jsx)$": ["react", "frontend", "component"],
    r".*\.vue$": ["vue", "frontend", "component"],
    r".*\.svelte$": ["svelte", "frontend", "component"],
    # Database
    r".*migrations?/.*\.(py|sql)$": ["database", "migration"],
    r".*models?\.py$": ["database", "orm", "model"],
    r".*schema.*\.(py|ts|graphql)$": ["schema", "database"],
}

# Directory name → keyword mappings
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

# Extension → keyword mappings
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
            fh.write(f"{timestamp} [{Path(__file__).name}] {message}\n")
    except Exception:
        return


def candidate_rule_paths() -> List[Path]:
    """Return possible locations for skill-rules.json."""
    paths = []
    if os.getenv("CLAUDE_SKILL_RULES"):
        paths.append(Path(os.environ["CLAUDE_SKILL_RULES"]).expanduser())

    script_path = Path(__file__).resolve()
    repo_rules = script_path.parents[1] / "skills" / "skill-rules.json"
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
    parts = raw.split(":")
    return [p.strip() for p in parts if p.strip()]


def extract_file_context(files: List[str]) -> Set[str]:
    """Extract contextual keywords from file paths."""
    keywords: Set[str] = set()

    for file_str in files:
        file_path = Path(file_str)
        path_lower = file_str.lower()

        # Check file patterns (regex)
        for pattern, pattern_keywords in FILE_PATTERNS.items():
            if re.search(pattern, path_lower, re.IGNORECASE):
                keywords.update(pattern_keywords)

        # Check directory names
        for part in file_path.parts:
            part_lower = part.lower()
            if part_lower in DIR_PATTERNS:
                keywords.update(DIR_PATTERNS[part_lower])

        # Check file extension
        ext = file_path.suffix.lower()
        if ext in EXT_PATTERNS:
            keywords.update(EXT_PATTERNS[ext])

        # Add filename words (split on common separators)
        name_parts = re.split(r"[_\-./]", file_path.stem.lower())
        keywords.update(p for p in name_parts if len(p) > 2)

    return keywords


def get_git_context() -> Set[str]:
    """Extract keywords from git branch name and recent commits."""
    keywords: Set[str] = set()

    # Get current branch name
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
            skip_branch = {"feature", "fix", "bug", "hotfix", "release", "main", "master", "develop"}
            keywords.update(p for p in parts if len(p) > 2 and p not in skip_branch)
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Get last few commit messages
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


def match_rules(
    prompt: str,
    files: List[str],
    rules: list,
    max_results: int = 5,
) -> List[Tuple[int, dict]]:
    """Return rules with keyword matches, sorted by hit count.
    
    Uses multiple signals:
    - User prompt text
    - File names and paths
    - File patterns (test files, config files, etc.)
    - Directory context (tests/, api/, etc.)
    - File extensions
    - Git branch name and recent commits
    """
    if not rules:
        return []

    # Gather all context
    prompt_lower = prompt.lower()
    file_text = " ".join(f.lower() for f in files)
    
    # Enhanced context from file patterns
    file_keywords = extract_file_context(files)
    
    # Git context
    git_keywords = get_git_context()
    
    # Combine all searchable text
    all_keywords = file_keywords | git_keywords
    search_text = f"{prompt_lower} {file_text} {' '.join(all_keywords)}"

    matches: List[Tuple[int, dict]] = []
    for rule in rules:
        keywords = [k.lower() for k in rule.get("keywords", [])]
        hits = sum(1 for kw in keywords if kw in search_text)
        if hits > 0:
            matches.append((hits, rule))

    matches.sort(key=lambda item: (-item[0], item[1].get("name", "")))
    return matches[:max_results]


def print_suggestions(matches: List[Tuple[int, dict]]) -> None:
    """Emit suggestions in a compact, readable format."""
    if not matches:
        return
    names = [rule.get("name", "unknown") for _, rule in matches]
    print(f"Suggested skills: {', '.join(names)}")


def _recommender_suggestions(
    changed_files: List[str],
    prompt: str,
) -> List[str]:
    """Get richer skill suggestions from SkillRecommender (Layer 2).

    Attempts to import the full recommendation engine and run it against
    the current context.  Returns an empty list on any failure so the
    hook never breaks when the package is unavailable.
    """
    if os.getenv("CORTEX_SKIP_RECOMMENDER", "").strip() in ("1", "true", "yes"):
        return []

    try:
        from claude_ctx_py.intelligence.base import ContextDetector
        from claude_ctx_py.skill_recommender import SkillRecommender
    except ImportError:
        return []

    try:
        # Build context from changed files, falling back to git diff
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
            rec.skill_name
            for rec in recommendations
            if rec.confidence >= 0.7
        ]
    except Exception:
        return []


def main() -> int:
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
    changed_files = split_changed_files(os.getenv("CLAUDE_CHANGED_FILES", ""))
    rules = load_rules()

    if not rules:
        return 0

    max_results = 5
    matches = match_rules(prompt, changed_files, rules, max_results=max_results)

    # Merge Layer 2 (SkillRecommender) results after keyword matches
    keyword_names = [rule.get("name", "unknown") for _, rule in matches]
    recommender_names = _recommender_suggestions(changed_files, prompt)

    # Deduplicate: keyword matches first, then recommender additions
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


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
