"""Onboarding assistant command."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.base import BLUE, GREEN, RED, YELLOW, NC, _color, _resolve_cortex_root
from .core.workflows import workflow_run


def fetch_good_first_issues() -> List[Dict[str, Any]]:
    """Fetch 'good first issue' items from GitHub.

    Tries to use `gh` CLI first, falls back to public API if possible.
    """
    # 1. Try gh CLI
    if shutil.which("gh"):
        try:
            # Check auth status first to avoid hanging/prompting
            subprocess.run(
                ["gh", "auth", "status"],
                check=True,
                capture_output=True,
                timeout=5
            )
            
            # Fetch issues
            cmd = [
                "gh", "issue", "list",
                "--label", "good first issue",
                "--limit", "5",
                "--state", "open",
                "--json", "number,title,url,body"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass

    # 2. Fallback: Try to parse git remote and use public API (rate limited but maybe okay)
    # For now, just return empty list to simulate "no issues found" or "not connected"
    # implementing robust public API fallback without auth is flaky.
    return []


def format_issues_markdown(issues: List[Dict[str, Any]]) -> str:
    """Format issues list as Markdown."""
    if not issues:
        return "No 'good first issue' items found. You can look for small bugs or documentation fixes."

    lines = ["# Good First Issues\n"]
    lines.append("Here are some recommended tasks for your first contribution:\n")
    
    for issue in issues:
        number = issue.get("number", "?")
        title = issue.get("title", "Untitled")
        url = issue.get("url", "#")
        lines.append(f"- [#{number}: {title}]({url})")
    
    return "\n".join(lines)


def onboard() -> int:
    """Run the project onboarding assistant."""
    print(_color("👋 Welcome to the Project Onboarding Assistant!", BLUE))
    print("I'll help you get set up and find your first task.\n")

    # 1. Fetch Issues
    print("🔍 Looking for 'good first issues'...")
    issues = fetch_good_first_issues()
    
    if issues:
        print(f"{_color('✓', GREEN)} Found {len(issues)} issues.")
    else:
        print(f"{_color('!', YELLOW)} Could not fetch specific issues (gh CLI not ready or no issues labeled).")

    # 2. Write Context File
    # We write this file so the AI agent running the workflow can "see" the issues
    context_file = Path("ONBOARDING_ISSUES.md")
    content = format_issues_markdown(issues)
    try:
        context_file.write_text(content, encoding="utf-8")
        # Add to ignore list temporarily? No, we want the user/agent to see it.
    except OSError as e:
        print(f"{_color('x', RED)} Failed to write issue context: {e}")

    # 3. Start Workflow
    print("\n🚀 Starting onboarding workflow...")
    exit_code, message = workflow_run("onboarding-education")
    
    print(message)
    
    if exit_code == 0:
        print("\n" + _color("💡 Tip:", YELLOW) + " The workflow has started. Open your editor or check `ONBOARDING_ISSUES.md`.")
        
    return exit_code
