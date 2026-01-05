---
layout: default
title: Hooks & Automation
nav_order: 8
---

# Hooks & Automation

Claude Code hooks let you run scripts whenever a user submits a prompt or a tool completes. This repository ships two ready-made hooks and a default hook config at `hooks/hooks.json`.

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
            "command": "python3",
            "args": [
              "${CLAUDE_PLUGIN_ROOT}/hooks/examples/skill_auto_suggester.py"
            ]
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

## 2. Implementation Quality Gate

`hooks/examples/implementation-quality-gate.sh` enforces the three-phase workflow (testing → docs → code review). Add it to `hooks/hooks.json` under `UserPromptSubmit` and activate the required agents (`test-automator`, `docs-architect`, `quality-engineer`, etc.).

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash",
            "args": [
              "${CLAUDE_PLUGIN_ROOT}/hooks/examples/implementation-quality-gate.sh"
            ]
          }
        ]
      }
    ]
  }
}
```

### Configuration

```bash
vim hooks/examples/implementation-quality-gate.sh

COVERAGE_THRESHOLD=85
DOCS_REVIEW_THRESHOLD=7.5
CODE_REVIEW_REQUIRED=true
```

Refer to `hooks/examples/HOOK_DOCUMENTATION.md` for the full workflow.

---

## Hook examples

- `hooks/examples/skill_auto_suggester.py` — suggests relevant `/ctx:*` commands.
- `hooks/examples/memory_auto_capture.py` — captures memory on session end.
- `hooks/examples/implementation-quality-gate.sh` — enforces the quality gate workflow.
- `hooks/examples/HOOK_DOCUMENTATION.md` — full walkthrough and configuration notes.

---

## Writing Your Own Hooks

1. Create a script in `hooks/examples/` (or `hooks/` if you want to ship it directly).
2. Register it in `hooks/hooks.json` and reference the script with `${CLAUDE_PLUGIN_ROOT}`.
3. Update `hooks/README.md` and this guide with installation notes.
