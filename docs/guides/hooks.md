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

## 2. Implementation Quality Gate

`hooks/implementation-quality-gate.sh` enforces the three-phase workflow (testing → docs → code review). Add it to `hooks/hooks.json` under `UserPromptSubmit` and activate the required agents (`test-automator`, `docs-architect`, `quality-engineer`, etc.).

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/implementation-quality-gate.sh\""
          }
        ]
      }
    ]
  }
}
```

### Configuration

```bash
vim hooks/implementation-quality-gate.sh

COVERAGE_THRESHOLD=85
DOCS_REVIEW_THRESHOLD=7.5
CODE_REVIEW_REQUIRED=true
```

Refer to `archive/implementation-reports/HOOK_DOCUMENTATION.md` for the full workflow.

---

## 3. Parallel Workflow Enforcer

`hooks/parallel-workflow-enforcer.sh` enforces parallel planning/implementation/testing/review and blocks "intent-only" delivery. Add it to `hooks/hooks.json` under `UserPromptSubmit`. See `hooks/PARALLEL_WORKFLOW_README.md` for full details.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/parallel-workflow-enforcer.sh\""
          }
        ]
      }
    ]
  }
}
```

---

## Hook examples

- `hooks/skill_auto_suggester.py` — suggests relevant `/ctx:*` commands.
- `hooks/memory_auto_capture.py` — captures memory on session end.
- `hooks/implementation-quality-gate.sh` — enforces the quality gate workflow.
- `hooks/parallel-workflow-enforcer.sh` — enforces parallel execution and deliverables.
- `hooks/safety_pre_tool_guard.py` — blocks destructive tool calls and unsafe file ops.
- `hooks/secret_scan.py` — scans changed files for common secrets.
- `hooks/large_file_gate.py` — blocks oversized files in changes.
- `hooks/context_pack_injector.py` — suggests or applies context profiles from prompts.
- `hooks/changelog_gate.py` — requires CHANGELOG updates for release-like changes.
- `archive/implementation-reports/HOOK_DOCUMENTATION.md` — full walkthrough and configuration notes.

---

## Hook logging

Hook failures are now captured in `~/.cortex/logs/hooks.log` to make debugging easier. You can override the log location by setting `CORTEX_HOOK_LOG_PATH` (or `CLAUDE_HOOK_LOG_PATH`) in your environment.

---

## Writing Your Own Hooks

1. Create a script in `hooks/` (or `hooks/examples/` for drafts/templates).
2. Register it in `hooks/hooks.json` and reference the script with `${CLAUDE_PLUGIN_ROOT}`.
3. Update `hooks/README.md` and this guide with installation notes.
