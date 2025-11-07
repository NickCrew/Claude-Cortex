---
layout: default
title: Hooks & Automation
nav_order: 8
---

# Hooks & Automation

Claude Code hooks let you run scripts whenever a user submits a prompt or a tool completes. claude-ctx now ships two ready-made hooks:

## 1. Skill Auto-Suggester (new)

Borrowed from diet103’s infrastructure showcase, this Python hook reads the current prompt (and optional `CLAUDE_CHANGED_FILES`) and suggests relevant `/ctx:*` commands.

```bash
cp hooks/examples/skill_auto_suggester.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill_auto_suggester.py

# settings.json snippet
{
  "hooks": {
    "user-prompt-submit": [
      {"command": "python3", "args": ["~/.claude/hooks/skill_auto_suggester.py"]}
    ]
  }
}
```

- Rules live in `skills/skill-rules.json`. Edit keywords/commands there—no code changes required.
- Suggested commands appear inline in Claude Code, nudging you to run `/ctx:brainstorm`, `/ctx:plan`, `/dev:test`, etc.

## 2. Implementation Quality Gate

`hooks/examples/implementation-quality-gate.sh` enforces the three-phase workflow (testing → docs → code review). Install via:

```bash
cp hooks/examples/implementation-quality-gate.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/implementation-quality-gate.sh
```

Add it to `user-prompt-submit` and activate the required agents (`test-automator`, `docs-architect`, `quality-engineer`, etc.).

### Configuration

```bash
vim ~/.claude/hooks/implementation-quality-gate.sh

COVERAGE_THRESHOLD=85
DOCS_REVIEW_THRESHOLD=7.5
CODE_REVIEW_REQUIRED=true
```

Refer to `hooks/examples/HOOK_DOCUMENTATION.md` for the full workflow.

---

## Writing Your Own Hooks

1. Create a script in `hooks/examples/`.
2. Document installation steps in this file and `hooks/README.md`.
3. Encourage users to add hooks under `~/.claude/hooks/` and update `settings.json`.
