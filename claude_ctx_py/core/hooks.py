"""Hooks management for Claude Code."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .asset_discovery import find_claude_directories
from .base import _resolve_claude_dir


# Hook event types supported by Claude Code
HOOK_EVENTS = [
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "Stop",
    "SubagentStop",
    "UserPromptSubmit",
]


@dataclass
class HookDefinition:
    """Definition of a hook."""

    name: str
    description: str
    event: str
    command: str
    source_path: Optional[Path] = None
    matcher: str = ""
    is_installed: bool = False


@dataclass
class InstalledHook:
    """Represents an installed hook in settings.json."""

    event: str
    matcher: str
    command: str
    hook_type: str = "command"


def get_settings_path() -> Path:
    """Get path to cortex settings.json."""
    claude_dir = _resolve_claude_dir()
    return claude_dir / "settings.json"


def get_settings_scope(settings_path: Path) -> str:
    """Infer scope (project/parent/global/custom) for a settings.json path."""
    for claude_dir in find_claude_directories(Path.cwd()):
        if settings_path.parent.resolve() == claude_dir.path.resolve():
            return claude_dir.scope
    # If not in discovered dirs, mark as custom/override
    return "custom"


def detect_settings_files() -> List[Tuple[Path, str]]:
    """List discovered settings.json files with their scope.

    Returns:
        List of (path, scope) tuples ordered by specificity (project → parent → global).
    """
    results: List[Tuple[Path, str]] = []
    for claude_dir in find_claude_directories(Path.cwd()):
        settings_path = claude_dir.path / "settings.json"
        if settings_path.exists():
            results.append((settings_path, claude_dir.scope))
    return results


def load_settings() -> Dict[str, Any]:
    """Load settings.json."""
    settings_path = get_settings_path()
    if not settings_path.exists():
        return {}
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_settings(settings: Dict[str, Any]) -> Tuple[bool, str]:
    """Save settings.json."""
    settings_path = get_settings_path()
    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(settings, indent=2) + "\n", encoding="utf-8"
        )
        return True, "Settings saved"
    except OSError as e:
        return False, f"Failed to save settings: {e}"


def get_installed_hooks() -> List[InstalledHook]:
    """Get list of installed hooks from settings.json."""
    settings = load_settings()
    hooks_config = settings.get("hooks", {})
    installed: List[InstalledHook] = []

    for event, matchers in hooks_config.items():
        if not isinstance(matchers, list):
            continue
        for matcher_entry in matchers:
            matcher = matcher_entry.get("matcher", "")
            for hook in matcher_entry.get("hooks", []):
                installed.append(
                    InstalledHook(
                        event=event,
                        matcher=matcher,
                        command=hook.get("command", ""),
                        hook_type=hook.get("type", "command"),
                    )
                )

    return installed


def get_available_hooks(plugin_dir: Optional[Path] = None) -> List[HookDefinition]:
    """Get available hooks from hooks/examples directory.

    Args:
        plugin_dir: Plugin directory. If None, uses package location.

    Returns:
        List of available hook definitions.
    """
    hooks: List[HookDefinition] = []

    # Find hooks/examples directory
    if plugin_dir is None:
        # Try to find from package location
        import claude_ctx_py

        pkg_dir = Path(claude_ctx_py.__file__).parent.parent
        examples_dir = pkg_dir / "hooks" / "examples"
    else:
        examples_dir = plugin_dir / "hooks" / "examples"

    if not examples_dir.is_dir():
        return hooks

    # Parse each hook file
    for hook_file in sorted(examples_dir.glob("*.py")):
        hook_def = parse_hook_file(hook_file)
        if hook_def:
            hooks.append(hook_def)

    # Also check user's hooks directory
    claude_dir = _resolve_claude_dir()
    user_hooks_dir = claude_dir / "hooks"
    if user_hooks_dir.is_dir():
        for hook_file in sorted(user_hooks_dir.glob("*.py")):
            # Skip if already in examples
            if any(h.name == hook_file.stem for h in hooks):
                continue
            hook_def = parse_hook_file(hook_file)
            if hook_def:
                hook_def.is_installed = True
                hooks.append(hook_def)

    # Mark installed hooks
    installed = get_installed_hooks()
    installed_commands = {h.command for h in installed}
    for hook in hooks:
        if any(hook.source_path and str(hook.source_path) in cmd for cmd in installed_commands):
            hook.is_installed = True

    return hooks


def parse_hook_file(hook_file: Path) -> Optional[HookDefinition]:
    """Parse a hook file to extract metadata.

    Expects docstring at top with:
    - First line: description
    - Usage section with hook event type
    """
    try:
        content = hook_file.read_text(encoding="utf-8")
    except OSError:
        return None

    # Extract docstring
    lines = content.split("\n")
    in_docstring = False
    docstring_lines: List[str] = []

    for line in lines:
        if '"""' in line:
            if not in_docstring:
                in_docstring = True
                # Handle single-line docstring
                if line.count('"""') >= 2:
                    start = line.index('"""') + 3
                    end = line.rindex('"""')
                    docstring_lines.append(line[start:end])
                    break
            else:
                break
        elif in_docstring:
            docstring_lines.append(line)

    if not docstring_lines:
        return HookDefinition(
            name=hook_file.stem,
            description="No description",
            event="UserPromptSubmit",
            command=f"python3 {hook_file}",
            source_path=hook_file,
        )

    # Parse docstring
    description = docstring_lines[0].strip() if docstring_lines else "No description"

    # Try to find event type from docstring
    event = "UserPromptSubmit"  # Default
    full_docstring = "\n".join(docstring_lines).lower()

    if "session-end" in full_docstring or "stop" in full_docstring:
        event = "Stop"
    elif "pretooluse" in full_docstring or "pre-tool" in full_docstring:
        event = "PreToolUse"
    elif "posttooluse" in full_docstring or "post-tool" in full_docstring:
        event = "PostToolUse"
    elif "notification" in full_docstring:
        event = "Notification"
    elif "subagent" in full_docstring:
        event = "SubagentStop"

    return HookDefinition(
        name=hook_file.stem,
        description=description,
        event=event,
        command=f"python3 {hook_file}",
        source_path=hook_file,
    )


def install_hook(
    hook: HookDefinition,
    target_dir: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Install a hook by copying to hooks dir and registering in settings.

    Args:
        hook: Hook definition to install
        target_dir: Target directory for hooks. Defaults to ~/.cortex/hooks/

    Returns:
        Tuple of (success, message)
    """
    claude_dir = _resolve_claude_dir()
    hooks_dir = target_dir or (claude_dir / "hooks")
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Copy hook file if it has a source path
    installed_path = hooks_dir / f"{hook.name}.py"
    if hook.source_path and hook.source_path.exists():
        try:
            shutil.copy2(hook.source_path, installed_path)
        except OSError as e:
            return False, f"Failed to copy hook: {e}"

    # Update settings.json
    settings = load_settings()
    if "hooks" not in settings:
        settings["hooks"] = {}

    if hook.event not in settings["hooks"]:
        settings["hooks"][hook.event] = []

    # Check if already installed
    command = f"python3 {installed_path}"
    for matcher_entry in settings["hooks"][hook.event]:
        for existing_hook in matcher_entry.get("hooks", []):
            if existing_hook.get("command") == command:
                return True, f"Hook {hook.name} already installed"

    # Add new hook
    settings["hooks"][hook.event].append(
        {
            "matcher": hook.matcher,
            "hooks": [{"type": "command", "command": command}],
        }
    )

    success, msg = save_settings(settings)
    if success:
        return True, f"Installed hook: {hook.name}"
    return False, msg


def uninstall_hook(hook: HookDefinition) -> Tuple[bool, str]:
    """Uninstall a hook by removing from settings.

    Args:
        hook: Hook to uninstall

    Returns:
        Tuple of (success, message)
    """
    settings = load_settings()
    if "hooks" not in settings or hook.event not in settings["hooks"]:
        return False, f"Hook {hook.name} not found"

    # Find and remove the hook
    modified = False
    new_matchers = []
    for matcher_entry in settings["hooks"][hook.event]:
        new_hooks = []
        for existing_hook in matcher_entry.get("hooks", []):
            cmd = existing_hook.get("command", "")
            if hook.name not in cmd:
                new_hooks.append(existing_hook)
            else:
                modified = True

        if new_hooks:
            matcher_entry["hooks"] = new_hooks
            new_matchers.append(matcher_entry)

    if modified:
        settings["hooks"][hook.event] = new_matchers
        success, msg = save_settings(settings)
        if success:
            return True, f"Uninstalled hook: {hook.name}"
        return False, msg

    return False, f"Hook {hook.name} not found in settings"


def get_hook_events() -> List[str]:
    """Get list of supported hook events."""
    return HOOK_EVENTS.copy()


def create_hook_template(name: str, event: str, target_dir: Optional[Path] = None) -> Tuple[bool, str, Optional[Path]]:
    """Create a new hook from template.

    Args:
        name: Hook name (without .py extension)
        event: Hook event type
        target_dir: Target directory. Defaults to ~/.cortex/hooks/

    Returns:
        Tuple of (success, message, path)
    """
    claude_dir = _resolve_claude_dir()
    hooks_dir = target_dir or (claude_dir / "hooks")
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hooks_dir / f"{name}.py"
    if hook_path.exists():
        return False, f"Hook {name} already exists", None

    template = f'''#!/usr/bin/env python3
"""Custom hook: {name}

This hook is triggered on {event} events.

Usage:
    Register this hook in ~/.claude/settings.json:

    {{
      "hooks": {{
        "{event}": [
          {{
            "matcher": "",
            "hooks": [
              {{
                "type": "command",
                "command": "python3 ~/.cortex/hooks/{name}.py"
              }}
            ]
          }}
        ]
      }}
    }}

Environment Variables:
    CLAUDE_HOOK_PROMPT: The user's prompt (for UserPromptSubmit)
    CLAUDE_SESSION_CONTEXT: Session context (for Stop)
    CLAUDE_CHANGED_FILES: Colon-separated list of changed files
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    """Main entry point for the hook."""
    # Get environment variables
    prompt = os.getenv("CLAUDE_HOOK_PROMPT", "")
    context = os.getenv("CLAUDE_SESSION_CONTEXT", "")

    # Add your hook logic here
    print(f"Hook {name} triggered!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

    try:
        hook_path.write_text(template, encoding="utf-8")
        hook_path.chmod(0o755)
        return True, f"Created hook template: {hook_path}", hook_path
    except OSError as e:
        return False, f"Failed to create hook: {e}", None
