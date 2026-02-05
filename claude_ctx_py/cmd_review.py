#!/usr/bin/env python3
"""
cortex review - Pre-completion review gate.

This command:
1. Detects context from git changes
2. Identifies top 5 relevant skills (weighted by signal strength)
3. REQUIRES Claude to load and apply those skills
4. Outputs a completion checklist

Usage: cortex review [--dry-run] [-c CONTEXT]
"""

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple, Set, Dict
from collections import Counter

# Skill mappings - signal -> (primary_skill, weight)
# Higher weight = more specific/important
SKILL_MAPPINGS: Dict[str, List[Tuple[str, int]]] = {
    # Languages (weight 2 - common)
    "typescript": [("typescript-advanced-patterns", 2)],
    "python": [("python-testing-patterns", 2), ("async-python-patterns", 1)],
    "rust": [],
    
    # Frameworks (weight 2)
    "react": [("react-performance-optimization", 2)],
    
    # Security (weight 3 - important)
    "auth": [("secure-coding-practices", 3), ("defense-in-depth", 2)],
    "security": [("secure-coding-practices", 3), ("owasp-top-10", 2)],
    
    # API (weight 2)
    "api": [("api-design-patterns", 2)],
    
    # Testing (weight 2)
    "test": [("test-driven-development", 2), ("testing-anti-patterns", 1)],
    
    # Performance (weight 2)
    "performance": [("python-performance-optimization", 2)],
    
    # Infrastructure (weight 2)
    "kubernetes": [("kubernetes-deployment-patterns", 2)],
    "terraform": [("terraform-best-practices", 2)],
    "docker": [("kubernetes-deployment-patterns", 1)],
    
    # Database (weight 2)
    "sql": [("database-design-patterns", 2)],
    "database": [("database-design-patterns", 2)],
    
    # Debug/refactor (weight 2)
    "debug": [("systematic-debugging", 2), ("root-cause-tracing", 1)],
    "refactor": [("code-quality-workflow", 2)],
    
    # Multi-perspective (weight 3 - for complex changes)
    "complex": [("multi-perspective-analysis", 3)],
}


def detect_file_types() -> List[str]:
    """Get list of changed file extensions from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return [Path(f).suffix.lower() for f in files]
    except Exception:
        return []


def get_changed_files() -> Tuple[str, int]:
    """Get the raw list of changed files as lowercase string and count."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return result.stdout.lower(), len(files)
    except Exception:
        return "", 0


def detect_context_signals() -> Dict[str, int]:
    """Detect which context signals are present with counts."""
    signals: Counter[str] = Counter()

    extensions = detect_file_types()
    paths, file_count = get_changed_files()

    # Language detection - count occurrences
    ts_count = extensions.count(".ts") + extensions.count(".tsx")
    if ts_count:
        signals["typescript"] += ts_count
    if ".tsx" in extensions or ".jsx" in extensions:
        signals["react"] += extensions.count(".tsx") + extensions.count(".jsx")
    py_count = extensions.count(".py")
    if py_count:
        signals["python"] += py_count
    rs_count = extensions.count(".rs")
    if rs_count:
        signals["rust"] += rs_count
    sql_count = extensions.count(".sql")
    if sql_count:
        signals["sql"] += sql_count

    # Rust cargo files
    if "cargo.toml" in paths or "cargo.lock" in paths:
        signals["rust"] += 1

    # Auth signals
    auth_hits = sum(1 for kw in ["auth", "login", "session", "password", "token"] if kw in paths)
    if auth_hits:
        signals["auth"] += auth_hits
        signals["security"] += auth_hits
    
    # API signals
    api_hits = sum(1 for kw in ["api", "routes", "endpoint", "handler"] if kw in paths)
    if api_hits:
        signals["api"] += api_hits
    
    # Test signals
    test_hits = sum(1 for kw in ["test", "spec", "_test", "test_"] if kw in paths)
    if test_hits:
        signals["test"] += test_hits

    # Performance signals
    perf_keywords = ["performance", "perf", "benchmark", "cache", "async", "parallel"]
    perf_hits = sum(1 for kw in perf_keywords if kw in paths)
    if perf_hits:
        signals["performance"] += perf_hits

    # Infrastructure signals
    if "dockerfile" in paths or "docker-compose" in paths:
        signals["docker"] += 1
    if "kubernetes" in paths or "k8s" in paths or "/deploy/" in paths:
        signals["kubernetes"] += 1
    if ".tf" in extensions or "terraform" in paths:
        signals["terraform"] += 1

    # Database signals
    if "migration" in paths or "models" in paths or "schema" in paths:
        signals["database"] += 1

    # Complex change detection - many domains = add multi-perspective
    if len(signals) >= 3 or file_count >= 10:
        signals["complex"] += 1

    return dict(signals)


def get_top_skills(signals: Dict[str, int], max_skills: int = 5) -> List[str]:
    """Get top skills based on weighted signal strength."""
    skill_scores: Counter[str] = Counter()
    
    for signal, signal_count in signals.items():
        if signal in SKILL_MAPPINGS:
            for skill, weight in SKILL_MAPPINGS[signal]:
                # Score = signal occurrences * skill weight
                skill_scores[skill] += signal_count * weight
    
    # Return top skills by score
    return [skill for skill, _score in skill_scores.most_common(max_skills)]


def get_skill_path(skill_name: str) -> str:
    """Get the path to a skill's SKILL.md file."""
    # Check common locations
    base = Path(__file__).parent.parent / "skills"
    
    # Direct match
    direct = base / skill_name / "SKILL.md"
    if direct.exists():
        return f"skills/{skill_name}/SKILL.md"
    
    # Check subdirectories (like collaboration/pre_mortem)
    for subdir in base.iterdir():
        if subdir.is_dir():
            nested = subdir / skill_name.replace("-", "_") / "SKILL.md"
            if nested.exists():
                return f"skills/{subdir.name}/{skill_name.replace('-', '_')}/SKILL.md"
    
    # Fallback
    return f"skills/{skill_name}/SKILL.md"


def main(dry_run: bool = False, extra_context: List[str] | None = None) -> int:
    """Main review gate logic."""

    print("=" * 60)
    print("⚡ REVIEW GATE")
    print("=" * 60)

    # 1. Detect context with counts
    signals = detect_context_signals()
    
    # Add extra context signals if provided
    if extra_context:
        for ctx in extra_context:
            signals[ctx] = signals.get(ctx, 0) + 1
    
    # Sort by count for display
    sorted_signals = sorted(signals.items(), key=lambda x: -x[1])
    signal_names = [s for s, _ in sorted_signals]
    
    print(f"\n📍 Detected: {', '.join(signal_names) if signal_names else 'general'}")

    # 2. Get top 5 skills weighted by signal strength
    skills = get_top_skills(signals, max_skills=5)
    
    if dry_run:
        print(f"\n[DRY RUN] Required skills: {', '.join(skills)}")
        return 0

    # 3. Output REQUIRED skills
    if skills:
        print("\n" + "=" * 60)
        print("🚨 REQUIRED SKILLS - LOAD BEFORE PROCEEDING")
        print("=" * 60)
        print()
        print("You MUST load each of these skills fully before continuing:")
        print()
        for skill in skills:
            print(f"   • {skill}")
        print()
        print("DO NOT skip this step. DO NOT summarize. Load each skill completely.")

    # 4. Output completion checklist
    print("\n" + "=" * 60)
    print("📋 COMPLETION CHECKLIST")
    print("=" * 60)
    print(
        """
Before marking complete:

[ ] All required skills loaded and applied"""
    )

    if skills:
        for skill in skills:
            print(f"    [ ] {skill}")

    print(
        """
[ ] All files written to disk
[ ] Tests executed and passing
[ ] No code blocks left in chat (everything in files)
"""
    )

    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Review gate for task completion")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen")
    parser.add_argument("--context", "-c", action="append", dest="contexts", 
                        help="Additional context signals (can repeat)")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run, extra_context=args.contexts))
