#!/usr/bin/env python3
"""Suggest or apply context packs based on the user's prompt.

Hook event: UserPromptSubmit
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

PROFILE_KEYWORDS: list[tuple[str, list[str]]] = [
    ("frontend", ["frontend", "ui", "ux", "react", "typescript", "css", "tailwind", "next" ]),
    ("web-dev", ["fullstack", "web app", "web-app", "webapp", "website"]),
    ("backend", ["backend", "api", "server", "database", "fastapi", "django", "flask"]),
    ("devops", ["devops", "kubernetes", "terraform", "infrastructure", "ci/cd", "deploy"]),
    ("documentation", ["docs", "documentation", "readme", "guide", "tutorial", "manual"]),
    ("data-ai", ["data", "ml", "ai", "model", "pandas", "notebook"]),
    ("quality", ["refactor", "cleanup", "lint", "testing", "quality"]),
    ("product", ["product", "roadmap", "requirements", "spec"]),
]


def _match_profile(prompt: str) -> str | None:
    lowered = prompt.lower()
    for profile, keywords in PROFILE_KEYWORDS:
        for keyword in keywords:
            if keyword in lowered:
                return profile
    return None


def _should_apply(prompt: str) -> bool:
    if os.getenv("CORTEX_CONTEXT_PACK_AUTO", "").strip().lower() in {"1", "true", "yes"}:
        return True
    return bool(re.search(r"\b(context pack|apply profile|set up context)\b", prompt, re.I))


def _run_profile(profile: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["cortex", "profile", profile],
            check=False,
            capture_output=True,
            text=True,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output.strip()
    except Exception as exc:
        return 1, f"Failed to run cortex profile {profile}: {exc}"


def main() -> int:
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "").strip()
    if not prompt:
        return 0

    profile = _match_profile(prompt)
    if not profile:
        return 0

    if _should_apply(prompt):
        code, output = _run_profile(profile)
        if code != 0:
            print(output or f"Failed to apply profile {profile}", file=sys.stderr)
            return 0
        if output:
            print(output)
        print(f"Context pack applied: {profile}")
        return 0

    print("Context pack suggestion:")
    print(f"- Recommended profile: {profile}")
    print(f"- Run: cortex profile {profile} (or set CORTEX_CONTEXT_PACK_AUTO=1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
