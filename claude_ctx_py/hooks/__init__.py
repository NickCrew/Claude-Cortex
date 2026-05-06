"""In-process hook implementations exposed via ``cortex hooks <name>``.

Each hook module provides a ``run()`` entrypoint callable from the CLI. The
``cortex hooks install <name>`` subcommand registers these as
UserPromptSubmit (or other) handlers in ``~/.claude/settings.json`` without
copying script files around — the invocation is always ``cortex hooks <name>``,
so upgrading the installed package upgrades the hook logic with no further
action.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Literal, Tuple, TypedDict

from ..core.hooks import load_settings, save_settings


HOOK_COMMAND_PREFIX = "cortex hooks"


# Supported registration targets. Each maps to a config file the harness
# reads at startup. Both files share the JSON shape `{"hooks": {<event>:
# [...]}}` — only the path differs.
HookTarget = Literal["claude", "codex"]
INSTALL_TARGETS: Tuple[HookTarget, ...] = ("claude", "codex")


class HookMeta(TypedDict):
    """Registration metadata for a ``cortex hooks <name>`` subcommand."""

    event: str
    matcher: str
    help: str


# Single source of truth for every hook subcommand: help text for the argparse
# parser, plus the (event, matcher) pair that ``cortex hooks install`` writes
# into settings.json. Keeping this in one place means adding a new hook is a
# single-file edit, and the install allowlist and argparse choices stay in sync
# automatically.
HOOK_SUBCOMMANDS: Dict[str, HookMeta] = {
    "skill-suggest": {
        "event": "UserPromptSubmit",
        "matcher": "",
        "help": (
            "UserPromptSubmit hook: suggest relevant skills "
            "(invoked by Claude Code, not usually run directly)"
        ),
    },
    "agent-suggest": {
        "event": "UserPromptSubmit",
        "matcher": "",
        "help": (
            "UserPromptSubmit hook: suggest relevant specialist agents "
            "for consultation or delegation"
        ),
    },
    "large-file-gate": {
        "event": "PostToolUse",
        "matcher": "",
        "help": "PostToolUse hook: block oversized files in the changed set",
    },
    "subagent-output-validator": {
        "event": "SubagentStop",
        "matcher": "",
        "help": (
            "SubagentStop hook: flag hallucinated file references in "
            "subagent output"
        ),
    },
    "workspace-validator": {
        "event": "PreToolUse",
        "matcher": "Task",
        "help": (
            "PreToolUse hook (Task matcher): validate paths referenced in "
            "Task prompts before subagent spawns"
        ),
    },
    "commit-cadence": {
        "event": "Stop",
        "matcher": "",
        "help": (
            "Stop hook: nudge the model to offer a commit when the working "
            "tree has uncommitted changes at turn end"
        ),
    },
}


# Legacy standalone scripts whose registrations should be migrated away from
# when a subcommand replacement is installed. Each value is the subcommand
# name that supersedes the script.
LEGACY_SCRIPT_REPLACEMENTS: Dict[str, str] = {
    "skill_auto_suggester.py": "skill-suggest",
    "skill_auto_suggester": "skill-suggest",
    "large_file_gate.py": "large-file-gate",
    "subagent_output_validator.py": "subagent-output-validator",
    "workspace_validator.py": "workspace-validator",
}


def _matches_legacy_script(command: str, subcommand: str) -> bool:
    """Return True if ``command`` invokes a legacy script superseded by
    ``subcommand``."""
    lower = command.lower()
    for script, replacement in LEGACY_SCRIPT_REPLACEMENTS.items():
        if replacement == subcommand and script.lower() in lower:
            return True
    return False


def _codex_hooks_config_path() -> Path:
    """Path to ``~/.codex/hooks.json``. Codex also accepts a ``[hooks]``
    table in ``~/.codex/config.toml``, but JSON is trivially merged
    without disturbing user TOML; that's our chosen sibling."""
    return Path.home() / ".codex" / "hooks.json"


def _load_target_config(target: HookTarget) -> Dict[str, Any]:
    if target == "codex":
        path = _codex_hooks_config_path()
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return load_settings()


def _save_target_config(target: HookTarget, data: Dict[str, Any]) -> Tuple[bool, str]:
    if target == "codex":
        path = _codex_hooks_config_path()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            return True, f"Saved {path}"
        except OSError as exc:
            return False, f"Failed to save {path}: {exc}"
    return save_settings(data)


def _target_config_label(target: HookTarget) -> str:
    if target == "codex":
        return str(_codex_hooks_config_path())
    return "~/.claude/settings.json"


def install_hook_command(
    subcommand: str,
    event: str,
    matcher: str = "",
    target: HookTarget = "claude",
) -> Tuple[bool, str]:
    """Register ``cortex hooks <subcommand>`` in the harness's hooks config.

    Target ``"claude"`` (default) writes to ``~/.claude/settings.json``;
    ``"codex"`` writes to ``~/.codex/hooks.json``. Both files share the
    same JSON shape, so the body below is target-agnostic — only load/
    save are parameterized.

    Removes any existing entry whose command references a legacy standalone
    script that this subcommand replaces (see ``LEGACY_SCRIPT_REPLACEMENTS``),
    then appends a new ``cortex hooks <subcommand>`` entry if one does not
    already exist.

    Returns ``(ok, message)``. ``ok`` is False only on config I/O failure —
    an idempotent no-op (already installed) is a successful True.
    """
    settings = _load_target_config(target)
    hooks_section = settings.setdefault("hooks", {})
    event_entries = hooks_section.setdefault(event, [])

    target_command = f"{HOOK_COMMAND_PREFIX} {subcommand}"
    changed = False
    migrated_from: list[str] = []
    already_present = False

    new_event_entries = []
    for matcher_entry in event_entries:
        if not isinstance(matcher_entry, dict):
            new_event_entries.append(matcher_entry)
            continue
        kept_hooks = []
        for hook_def in matcher_entry.get("hooks", []) or []:
            command = str(hook_def.get("command", ""))
            if command == target_command:
                already_present = True
                kept_hooks.append(hook_def)
                continue
            if _matches_legacy_script(command, subcommand):
                migrated_from.append(command)
                changed = True
                continue
            kept_hooks.append(hook_def)
        if kept_hooks:
            new_matcher = dict(matcher_entry)
            new_matcher["hooks"] = kept_hooks
            new_event_entries.append(new_matcher)
        else:
            changed = True
    hooks_section[event] = new_event_entries

    if not already_present:
        hooks_section[event].append(
            {
                "matcher": matcher,
                "hooks": [{"type": "command", "command": target_command}],
            }
        )
        changed = True

    if not changed:
        return True, f"Already registered: {target_command} ({_target_config_label(target)})"

    ok, msg = _save_target_config(target, settings)
    if not ok:
        return False, msg

    note = f"Registered: {target_command} (event={event}, {_target_config_label(target)})"
    if migrated_from:
        note += f"\n  Migrated from legacy: {', '.join(migrated_from)}"
    return True, note
