#!/usr/bin/env python3
"""Auto-capture session summary on session end.

This hook is triggered by the Claude Code SessionEnd hook when auto-capture is enabled.
It reads session context and writes a summary to ~/basic-memory/sessions/

Usage:
    Register this hook in hooks/hooks.json:

    {
      "hooks": {
        "SessionEnd": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "python3",
                "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/examples/memory_auto_capture.py"]
              }
            ]
          }
        ]
      }
    }

Environment Variables:
    CLAUDE_SESSION_CONTEXT: Session context (if available)
    CORTEX_MEMORY_VAULT: Override vault path (optional)

The hook checks ~/.claude/memory-config.json for auto-capture enabled state.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_claude_dir() -> Path:
    """Get the Claude configuration directory."""
    if "CLAUDE_PLUGIN_ROOT" in os.environ:
        return Path(os.environ["CLAUDE_PLUGIN_ROOT"])
    return Path.home() / ".claude"


def get_config() -> dict:
    """Load memory configuration."""
    config_path = get_claude_dir() / "memory-config.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def is_auto_capture_enabled() -> bool:
    """Check if auto-capture is enabled."""
    config = get_config()
    return config.get("auto_capture", {}).get("enabled", False)


def get_vault_path() -> Path:
    """Get the vault path."""
    if "CORTEX_MEMORY_VAULT" in os.environ:
        return Path(os.environ["CORTEX_MEMORY_VAULT"]).expanduser()
    config = get_config()
    return Path(config.get("vault_path", "~/basic-memory")).expanduser()


def extract_session_info() -> dict:
    """Extract session information from environment and context.

    Returns:
        Dict with keys: title, summary, decisions, implementations, open_items
    """
    # Get session context from environment if available
    context = os.getenv("CLAUDE_SESSION_CONTEXT", "")

    # Extract information from changed files
    changed_files = os.getenv("CLAUDE_CHANGED_FILES", "")

    # Get prompt if available
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")

    # Build session info
    now = datetime.now()
    title = f"Auto-captured session {now.strftime('%H:%M')}"

    # Build summary from available context
    summary_parts = []
    if prompt:
        # Use first line of prompt as context hint
        first_line = prompt.split("\n")[0][:100]
        summary_parts.append(f"Context: {first_line}")
    if changed_files:
        file_list = changed_files.split(":")
        summary_parts.append(f"Changed {len(file_list)} file(s)")
    if context:
        # Extract key points from context
        summary_parts.append(f"Session context captured")

    if not summary_parts:
        summary_parts.append("Session auto-captured (no context available)")

    return {
        "title": title,
        "summary": "; ".join(summary_parts),
        "changed_files": changed_files.split(":") if changed_files else [],
    }


def create_session_note(info: dict) -> Optional[Path]:
    """Create a session note in the vault.

    Args:
        info: Session information dict

    Returns:
        Path to created note or None on failure
    """
    vault_path = get_vault_path()
    sessions_dir = vault_path / "sessions"

    # Ensure directory exists
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_slug = now.strftime("%H%M")
    filename = f"{date_str}-auto-{time_slug}.md"

    # Check for existing file with same name
    note_path = sessions_dir / filename
    if note_path.exists():
        # Append sequence number
        seq = 2
        while True:
            filename = f"{date_str}-auto-{time_slug}-{seq}.md"
            note_path = sessions_dir / filename
            if not note_path.exists():
                break
            seq += 1

    # Build content
    content_lines = [
        f"# {info['title']}",
        "",
        "## Date",
        date_str,
        "",
        "## Summary",
        info["summary"],
    ]

    # Add changed files if available
    if info.get("changed_files"):
        content_lines.extend([
            "",
            "## Files Changed",
        ])
        for f in info["changed_files"][:10]:  # Limit to 10 files
            content_lines.append(f"- `{f}`")
        if len(info["changed_files"]) > 10:
            content_lines.append(f"- ... and {len(info['changed_files']) - 10} more")

    content_lines.extend([
        "",
        "---",
        "tags: #session #auto-captured",
        f"captured: {date_str}",
    ])

    content = "\n".join(content_lines)

    try:
        note_path.write_text(content, encoding="utf-8")
        return note_path
    except OSError as e:
        print(f"Error writing note: {e}", file=sys.stderr)
        return None


def update_last_capture() -> None:
    """Update the last capture timestamp in config."""
    config = get_config()
    if "auto_capture" not in config:
        config["auto_capture"] = {}
    config["auto_capture"]["last_capture"] = datetime.now().isoformat()

    config_path = get_claude_dir() / "memory-config.json"
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except OSError:
        pass  # Non-critical, ignore


def main() -> int:
    """Main entry point for auto-capture hook."""
    # Check if auto-capture is enabled
    if not is_auto_capture_enabled():
        # Silently exit if not enabled
        return 0

    # Check for exclude patterns
    config = get_config()
    exclude_patterns = config.get("auto_capture", {}).get(
        "exclude_patterns", ["explain", "what is", "how do"]
    )

    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "").lower()
    for pattern in exclude_patterns:
        if pattern.lower() in prompt:
            # Skip capture for excluded patterns
            return 0

    # Check minimum session length (simple heuristic based on context)
    min_length = config.get("auto_capture", {}).get("min_session_length", 5)
    context = os.getenv("CLAUDE_SESSION_CONTEXT", "")
    changed_files = os.getenv("CLAUDE_CHANGED_FILES", "")

    # Simple heuristic: consider "significant" if there are changed files
    # or substantial context
    if not changed_files and len(context) < 100:
        # Session too short, skip
        return 0

    # Extract session info
    info = extract_session_info()

    # Create session note
    note_path = create_session_note(info)

    if note_path:
        print(f"Auto-captured session: {note_path}")
        update_last_capture()
        return 0
    else:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
