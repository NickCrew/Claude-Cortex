#!/usr/bin/env python3
"""
cortex review - Unified review gate that Claude must run before task completion.

This command:
1. Detects context from git changes
2. Activates appropriate reviewers (AI-powered or fallback defaults)
3. Identifies relevant skills to apply
4. Outputs a completion checklist

Usage: cortex review [--dry-run]
"""

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple, Set, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fallback reviewers if AI recommendations aren't available
DEFAULT_REVIEWERS: List[str] = ["code-reviewer"]

# Context-specific fallbacks (used when AI isn't confident enough)
CONTEXT_FALLBACKS: Dict[str, List[str]] = {
    "typescript": ["typescript-pro"],
    "react": ["react-specialist", "ui-ux-designer"],
    "python": ["python-pro"],
    "rust": ["rust-pro"],
    "sql": ["sql-pro"],
    "auth": ["security-auditor"],
    "api": ["api-documenter"],
    "test": ["debugger"],
    "performance": ["performance-engineer"],
}

# Skill mappings - signal -> list of relevant skills
SKILL_MAPPINGS: Dict[str, List[str]] = {
    # Languages
    "typescript": ["typescript-advanced-patterns"],
    "python": ["python-testing-patterns", "python-performance-optimization", "async-python-patterns"],
    "rust": [],  # Add rust skills when available
    
    # Frameworks
    "react": ["react-performance-optimization", "super-saiyan"],
    
    # Domains
    "api": ["api-design-patterns", "api-gateway-patterns"],
    "sql": ["database-design-patterns"],
    "auth": ["secure-coding-practices", "owasp-top-10", "defense-in-depth"],
    "test": ["test-driven-development", "python-testing-patterns", "testing-anti-patterns"],
    "performance": ["python-performance-optimization", "react-performance-optimization"],
    
    # UI/UX
    "ui": ["super-saiyan"],
    "frontend": ["super-saiyan"],
    "tui": ["super-saiyan"],
    "cli": ["super-saiyan"],
    
    # Infrastructure
    "kubernetes": ["kubernetes-deployment-patterns", "kubernetes-security-policies", "helm-chart-patterns"],
    "terraform": ["terraform-best-practices"],
    "docker": ["kubernetes-deployment-patterns"],
    "gitops": ["gitops-workflows"],
    
    # Patterns
    "microservices": ["microservices-patterns", "event-driven-architecture", "cqrs-event-sourcing"],
    "security": ["secure-coding-practices", "owasp-top-10", "security-testing-patterns", "threat-modeling-techniques", "defense-in-depth"],
    
    # Workflows
    "debug": ["systematic-debugging", "root-cause-tracing", "workflow-bug-fix"],
    "bugfix": ["workflow-bug-fix"],
    "refactor": ["code-quality-workflow"],
    "release": ["release-prep", "verification-before-completion"],
    "review": ["receiving-code-review", "requesting-code-review"],
    "feature": ["feature-implementation", "workflow-feature-development"],
    "audit": ["workflow-security-audit"],
    "optimize": ["workflow-performance"],
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


def get_changed_files() -> str:
    """Get the raw list of changed files as lowercase string."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.lower()
    except Exception:
        return ""


def detect_context_signals() -> List[str]:
    """Detect which context signals are present."""
    signals: Set[str] = set()

    extensions = detect_file_types()
    paths = get_changed_files()

    # Language detection
    if ".ts" in extensions or ".tsx" in extensions:
        signals.add("typescript")
    if ".tsx" in extensions or ".jsx" in extensions:
        signals.add("react")
    if ".py" in extensions:
        signals.add("python")
    if ".rs" in extensions:
        signals.add("rust")
    if ".sql" in extensions:
        signals.add("sql")

    # Rust cargo files
    if "cargo.toml" in paths or "cargo.lock" in paths:
        signals.add("rust")

    # Auth signals
    if "auth" in paths or "login" in paths or "session" in paths:
        signals.add("auth")
        signals.add("security")
    
    # API signals
    if "api" in paths or "routes" in paths or "endpoint" in paths:
        signals.add("api")
    
    # Test signals
    if "test" in paths or "spec" in paths:
        signals.add("test")

    # Performance signals
    perf_keywords = [
        "performance", "perf", "benchmark", "cache", "redis",
        "async", "concurrent", "parallel", "thread", "worker",
        "optimization", "profil",
    ]
    if any(kw in paths for kw in perf_keywords):
        signals.add("performance")

    # Infrastructure signals
    if "dockerfile" in paths or "docker-compose" in paths:
        signals.add("docker")
    if "kubernetes" in paths or "k8s" in paths or "/deploy/" in paths:
        signals.add("kubernetes")
    if ".tf" in extensions or "terraform" in paths:
        signals.add("terraform")

    # Architecture signals
    if "microservice" in paths or "/services/" in paths:
        signals.add("microservices")

    # UI/UX signals
    ui_keywords = [
        "/components/", "/ui/", "/views/", "/pages/", "/layouts/",
        "button", "modal", "dialog", "form", "input",
    ]
    if any(kw in paths for kw in ui_keywords):
        signals.add("ui")
        signals.add("frontend")
    
    # TUI signals
    if "textual" in paths or "ratatui" in paths or "bubbletea" in paths:
        signals.add("tui")
    
    # CLI signals (Rich, Click, Typer)
    if "cli.py" in paths or "__main__.py" in paths or "commands/" in paths:
        signals.add("cli")

    return list(signals)


def get_relevant_skills(signals: List[str]) -> List[str]:
    """Get relevant skills based on detected context signals."""
    skills: Set[str] = set()
    
    for signal in signals:
        if signal in SKILL_MAPPINGS:
            skills.update(SKILL_MAPPINGS[signal])
    
    return sorted(skills)


def get_reviewers_from_ai() -> Tuple[List[str], bool]:
    """Try to get reviewers from AI recommendation system.

    Returns:
        Tuple of (reviewer list, success boolean)
    """
    try:
        result = subprocess.run(
            ["cortex", "ai", "auto-activate"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse activated agents from output
        activated: List[str] = []
        for line in result.stdout.split("\n"):
            if line.strip().startswith("✓"):
                # Extract agent name from "✓ agent-name"
                parts = line.strip().split()
                if len(parts) >= 2:
                    activated.append(parts[1])

        return activated, len(activated) > 0
    except Exception:
        return [], False


def get_fallback_reviewers(signals: List[str]) -> List[str]:
    """Get reviewers based on detected context signals."""
    reviewers: Set[str] = set(DEFAULT_REVIEWERS)

    for signal in signals:
        if signal in CONTEXT_FALLBACKS:
            reviewers.update(CONTEXT_FALLBACKS[signal])

    return list(reviewers)


def activate_agent(agent: str) -> Tuple[str, bool, str]:
    """Activate a single agent.

    Returns:
        Tuple of (agent_name, success, message)
    """
    try:
        result = subprocess.run(
            ["cortex", "agent", "activate", agent],
            capture_output=True,
            text=True,
            timeout=10,
        )
        success = result.returncode == 0
        return agent, success, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return agent, False, str(e)


def run_reviews_parallel(reviewers: List[str]) -> List[Tuple[str, bool, str]]:
    """Activate all reviewers in parallel."""
    results: List[Tuple[str, bool, str]] = []

    if not reviewers:
        return results

    with ThreadPoolExecutor(max_workers=len(reviewers)) as executor:
        futures = {executor.submit(activate_agent, r): r for r in reviewers}

        for future in as_completed(futures):
            results.append(future.result())

    return results


def get_skill_paths() -> Tuple[Path, str]:
    """Get the skill directory path and display prefix.
    
    Returns:
        Tuple of (skill_dir Path, display_prefix str)
    """
    # Try to find plugin root
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.environ.get("CORTEX_PLUGIN_ROOT")
    if plugin_root:
        return Path(plugin_root) / "skills", f"{plugin_root}/skills"
    
    # Try ~/.cortex
    home_cortex = Path.home() / ".cortex" / "skills"
    if home_cortex.exists():
        return home_cortex, str(home_cortex)
    
    # Fallback to relative
    return Path("skills"), "skills"


def main(dry_run: bool = False, extra_context: List[str] | None = None) -> int:
    """Main review gate logic.
    
    Args:
        dry_run: Show what would happen without activating
        extra_context: Additional context signals to include
    """

    print("=" * 60)
    print("⚡ REVIEW GATE")
    print("=" * 60)

    # 1. Detect context
    signals = detect_context_signals()
    
    # Add extra context signals if provided
    if extra_context:
        signals.extend(extra_context)
        signals = list(set(signals))  # dedupe
    
    print(f"\n📍 Context: {', '.join(signals) if signals else 'general'}")

    # 2. Detect relevant skills
    skills = get_relevant_skills(signals)
    
    # 3. Try AI-powered reviewer selection
    print("\n🤖 Getting AI recommendations...")
    ai_reviewers, ai_success = get_reviewers_from_ai()

    reviewers: List[str]

    if ai_success and ai_reviewers:
        print(f"   AI activated: {', '.join(ai_reviewers)}")
        reviewers = ai_reviewers
    else:
        # Fall back to context-based selection
        print("   AI unavailable, using context fallbacks...")
        reviewers = get_fallback_reviewers(signals)

        if dry_run:
            print(f"\n[DRY RUN] Would activate: {', '.join(reviewers)}")
            if skills:
                print(f"[DRY RUN] Relevant skills: {', '.join(skills)}")
            return 0

        # Activate fallback reviewers in parallel
        print(f"\n🔄 Activating {len(reviewers)} reviewers in parallel...")
        results = run_reviews_parallel(reviewers)

        activated: List[str] = []
        for agent, success, msg in results:
            if success:
                activated.append(agent)
                print(f"   ✓ {agent}")
            else:
                print(f"   ✗ {agent}: {msg}")

        reviewers = activated

    # 4. Output skills section
    if skills:
        skill_dir, skill_prefix = get_skill_paths()
        print("\n" + "=" * 60)
        print("📚 MANDATORY: READ THESE SKILLS BEFORE CODING")
        print("=" * 60)
        print("\nRun these commands NOW:\n")
        for skill in skills:
            print(f"   cat {skill_prefix}/{skill}/SKILL.md")
        print("\n⛔ DO NOT proceed until you have read the skill files.")

    # 5. Output completion checklist
    print("\n" + "=" * 60)
    print("📋 COMPLETION CHECKLIST")
    print("=" * 60)
    print(
        """
Before marking this task complete, verify:

[ ] All files written to disk (run: ls -la <paths>)
[ ] Tests executed and passing (not "will run" - ACTUALLY RUN)"""
    )

    if skills:
        print("[ ] Skills applied:")
        for skill in skills:
            print(f"    [ ] {skill}")

    print("[ ] Review feedback addressed:")
    for r in reviewers:
        print(f"    [ ] {r}")

    print(
        """
[ ] No code blocks left in chat (everything in files)

⚠️  DO NOT mark complete until all boxes checked.
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
