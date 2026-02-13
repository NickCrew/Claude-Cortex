#!/usr/bin/env python3
"""
cortex review - Pre-completion review gate.

This command:
1. Detects context from git changes via shared context provider
2. Identifies top 5 relevant skills via SkillRecommender
3. REQUIRES Claude to load and apply those skills
4. Outputs a completion checklist

Usage: cortex review [--dry-run] [-c CONTEXT]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List


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
    from .intelligence import get_current_context
    from .skill_recommender import SkillRecommender

    print("=" * 60)
    print("\u26a1 REVIEW GATE")
    print("=" * 60)

    # 1. Build context using the shared provider
    context = get_current_context()

    # Map extra -c args into the context's active_agents list so the
    # recommender can pick up additional signals.
    if extra_context:
        for ctx in extra_context:
            if ctx not in context.active_agents:
                context.active_agents.append(ctx)

    # Summarize detected signals for display
    signals = []
    if context.has_auth:
        signals.append("auth")
    if context.has_api:
        signals.append("api")
    if context.has_tests:
        signals.append("tests")
    if context.has_frontend:
        signals.append("frontend")
    if context.has_backend:
        signals.append("backend")
    if context.has_database:
        signals.append("database")
    if context.active_agents:
        signals.extend(context.active_agents)

    print(f"\n\U0001f4cd Detected: {', '.join(signals) if signals else 'general'}")

    # 2. Get top 5 skills from SkillRecommender (all four strategies)
    recommender = SkillRecommender()
    recs = recommender.recommend_for_context(context)[:5]
    skills = [r.skill_name for r in recs]

    if dry_run:
        print(f"\n[DRY RUN] Required skills: {', '.join(skills)}")
        return 0

    # 3. Output REQUIRED skills
    if skills:
        print("\n" + "=" * 60)
        print("\U0001f6a8 REQUIRED SKILLS - LOAD BEFORE PROCEEDING")
        print("=" * 60)
        print()
        print("You MUST load each of these skills fully before continuing:")
        print()
        for skill in skills:
            print(f"   \u2022 {skill}")
        print()
        print("DO NOT skip this step. DO NOT summarize. Load each skill completely.")

    # 4. Output completion checklist
    print("\n" + "=" * 60)
    print("\U0001f4cb COMPLETION CHECKLIST")
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
