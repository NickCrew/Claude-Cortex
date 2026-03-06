---
layout: default
title: Hooks & Automation
nav_order: 8
---

# Hooks & Automation

Claude Code hooks let you run scripts whenever a user submits a prompt or a tool completes. This repository ships a default hook config at `hooks/hooks.json` plus several ready-made hooks.

## 1. Skill Auto-Suggester (new)

Borrowed from diet103’s infrastructure showcase, this Python hook reads the current prompt (and optional `CLAUDE_CHANGED_FILES`) and suggests relevant `/ctx:*` commands.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/skill_auto_suggester.py\""
          }
        ]
      }
    ]
  }
}
```

Make sure your plugin manifest points at the hooks file: `"hooks": "./hooks/hooks.json"`.

- Rules live in `skills/skill-rules.json`. Edit keywords/commands there—no code changes required.
- Suggested commands appear inline in Claude Code, nudging you to run `/ctx:brainstorm`, `/ctx:plan`, `/dev:test`, etc.

## Available Hooks

- `hooks/skill_auto_suggester.py` — suggests relevant skills based on the current prompt.
- `hooks/secret_scan.py` — scans changed files for common secrets.
- `hooks/large_file_gate.py` — blocks oversized files in changes.
- `hooks/audit.sh` — audit logging for tool calls.
- `hooks/execution-enforcer.sh` — enforces execution discipline.
- `hooks/issue-generator.sh` — generates issues from tool output.
- `hooks/post-edit-check.sh` — validates files after edits.
- `hooks/subagent_output_validator.py` — validates subagent output quality.
- `hooks/workspace_validator.py` — validates workspace state.

---

## Hook logging

Hook failures are now captured in `~/.claude/logs/hooks.log` to make debugging easier. You can override the log location by setting `CORTEX_HOOK_LOG_PATH` (or `CLAUDE_HOOK_LOG_PATH`) in your environment.

---

## Writing Your Own Hooks

1. Create a script in `hooks/` (or `hooks/examples/` for drafts/templates).
2. Register it in `hooks/hooks.json` and reference the script with `${CLAUDE_PLUGIN_ROOT}`.
3. Update `hooks/README.md` and this guide with installation notes.
