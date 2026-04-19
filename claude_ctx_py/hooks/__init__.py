"""In-process hook implementations exposed via ``cortex hooks <name>``.

Each hook module provides a ``run()`` entrypoint callable from the CLI. The
``cortex hooks install <name>`` subcommand registers these as
UserPromptSubmit (or other) handlers in ``~/.claude/settings.json`` without
copying script files around — the invocation is always ``cortex hooks <name>``,
so upgrading the installed package upgrades the hook logic with no further
action.
"""

from __future__ import annotations

from typing import Dict, Tuple

from ..core.hooks import load_settings, save_settings


HOOK_COMMAND_PREFIX = "cortex hooks"

# Legacy standalone scripts whose registrations should be migrated away from
# when a subcommand replacement is installed. Each value is the subcommand
# name that supersedes the script.
LEGACY_SCRIPT_REPLACEMENTS: Dict[str, str] = {
    "skill_auto_suggester.py": "skill-suggest",
    "skill_auto_suggester": "skill-suggest",
}


def _matches_legacy_script(command: str, subcommand: str) -> bool:
    """Return True if ``command`` invokes a legacy script superseded by
    ``subcommand``."""
    lower = command.lower()
    for script, replacement in LEGACY_SCRIPT_REPLACEMENTS.items():
        if replacement == subcommand and script.lower() in lower:
            return True
    return False


def install_hook_command(
    subcommand: str,
    event: str,
    matcher: str = "",
) -> Tuple[bool, str]:
    """Register ``cortex hooks <subcommand>`` in ``~/.claude/settings.json``.

    Removes any existing entry whose command references a legacy standalone
    script that this subcommand replaces (see ``LEGACY_SCRIPT_REPLACEMENTS``),
    then appends a new ``cortex hooks <subcommand>`` entry if one does not
    already exist.

    Returns ``(ok, message)``. ``ok`` is False only on settings.json I/O
    failure — an idempotent no-op (already installed) is a successful True.
    """
    settings = load_settings()
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
        return True, f"Already registered: {target_command}"

    ok, msg = save_settings(settings)
    if not ok:
        return False, msg

    note = f"Registered: {target_command} (event={event})"
    if migrated_from:
        note += f"\n  Migrated from legacy: {', '.join(migrated_from)}"
    return True, note
