---
layout: default
title: Hooks
parent: Guides
nav_order: 5
---

# Hooks

Hooks are scripts that run automatically in response to Claude Code events -- before or after tool calls, when a prompt is submitted, when a session starts, and more.

## Available Hooks

Cortex ships with these hooks in `hooks/`:

| Hook | Event | Purpose |
|:-----|:------|:--------|
| `skill_auto_suggester.py` | UserPromptSubmit | Suggests relevant skills based on prompt and file context |
| `secret_scan.py` | PostToolUse | Scans changed files for leaked secrets (AWS keys, tokens) |
| `large_file_gate.py` | PostToolUse | Blocks oversized files from being committed |
| `workspace_validator.py` | PreToolUse (Task) | Validates workspace context before spawning subagents |
| `subagent_output_validator.py` | SubagentStop | Checks subagent outputs for hallucinated file references |
| `execution-enforcer.sh` | UserPromptSubmit | Reinforces execution principles |
| `post-edit-check.sh` | PostToolUse | Runs type checks after Rust/TypeScript edits |

## Hook Events

Hooks fire on specific Claude Code lifecycle events:

| Event | When It Fires |
|:------|:-------------|
| `PreToolUse` | After Claude creates tool parameters, before the tool runs |
| `PostToolUse` | Immediately after a tool completes |
| `UserPromptSubmit` | When you submit a prompt, before Claude processes it |
| `Stop` | When Claude finishes responding |
| `SubagentStop` | When a subagent (Task tool) finishes |
| `SessionStart` | When a new session begins or resumes |
| `SessionEnd` | When a session ends |
| `PreCompact` | Before context compaction |
| `Notification` | When Claude Code sends a notification |

### Matchers

Hooks can target specific tools using matchers:

| Matcher | Matches |
|:--------|:--------|
| `Task` | Subagent tasks |
| `Bash` | Shell commands |
| `Edit` | File editing |
| `Write` | File writing |
| `Read` | File reading |
| `""` or `*` | All tools |

## Installation

Hooks are registered in `~/.claude/settings.json`. You have three ways to get
them there, from easiest to most manual.

### From the TUI (recommended)

```bash
cortex tui
```

Press `7` to open the **Hooks** view. You'll see a list of available hooks
on one side and installed hooks on the other. Select the hook you want,
confirm, and the TUI writes the settings.json entry for you. Uninstalling
from the same view removes it cleanly.

This is the recommended path: it validates the event name, resolves the
script path, and makes sure the JSON structure is correct.

### Via CLI

```bash
cortex install link
```

This symlinks `hooks/` to `~/.claude/hooks/` so that hook scripts are
available under `~/.claude/hooks/`. It does **not** register the hooks in
settings.json -- you still need to install individual hooks through the TUI
or by hand.

### By hand

If you want to edit `~/.claude/settings.json` directly, add entries under
the `hooks` key keyed by event name:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/skill_auto_suggester.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/secret_scan.py"
          }
        ]
      }
    ]
  }
}
```

The TUI Hooks view produces the same shape, so you can use hand edits as a
fallback or to diff against what the TUI wrote.

## Where Hooks Are Registered

Hook registration lives in `~/.claude/settings.json` (or one of the
project-scoped settings files listed at the bottom of this page). Cortex
used to be distributed as a Claude Code plugin with a `hooks/hooks.json`
manifest in the repo; that manifest has been removed. The files under
`hooks/` in the repo are plain hook scripts that settings.json points at
via `${CORTEX_ROOT}`, not a manifest.

If you're looking for the canonical list of what's installed on your
machine, check:

1. The **Hooks** view in `cortex tui` (press `7`) -- this is the friendliest
   view.
2. `~/.claude/settings.json` directly -- this is the underlying truth.

## Environment Variables

Hooks receive context through environment variables. Claude Code sets the
prompt- and project-level variables; Cortex sets `CORTEX_ROOT` when the
hook is launched through the Cortex install path.

| Variable | Set by | Description |
|:---------|:-------|:------------|
| `CLAUDE_HOOK_PROMPT` | Claude Code | The user's prompt text |
| `CLAUDE_CHANGED_FILES` | Claude Code | Colon-separated list of changed files |
| `CLAUDE_PROJECT_DIR` | Claude Code | Project root directory |
| `CORTEX_ROOT` | Cortex | Absolute path to the Cortex install root (where `hooks/`, `skills/`, etc. live). Use this to locate bundled scripts from inside a hook. |

## Logging

Hook failures are logged to a file for debugging:

```bash
# Default location
~/.claude/logs/hooks.log

# Override with environment variable
export CORTEX_HOOK_LOG_PATH=~/my-logs/hooks.log
```

Log entries include timestamps and hook names:

```
2026-02-16 15:30:45 [skill_auto_suggester.py] Suggested skills: owasp-top-10
2026-02-16 15:31:02 [secret_scan.py] No secrets detected in 3 files
```

## Skill Auto-Suggester

The most visible hook. It analyzes your prompt and project context to
suggest skills after each message.

**Install it:** open `cortex tui`, press `7`, select
**skill_auto_suggester** from the available hooks, and install it. See
[Working with Skills]({% link guides/working-with-skills.md %}) for the
end-to-end story of how the suggestions are generated and how to teach
the system which ones are helpful.

**What it checks:**
- Prompt text keywords
- File patterns in changed files (e.g., `test_*.py` triggers testing skills)
- Directory names (e.g., `auth/` triggers security skills)
- File extensions (e.g., `.tsx` triggers React and TypeScript skills)
- Git branch name and recent commit messages

**Output:**

```
Suggested skills: security-testing-patterns, owasp-top-10
```

**Configuration:** Keyword-to-skill mappings are defined in
`skills/skill-rules.json`. Edit this file to customize which skills are
suggested for which keywords.

## Settings File Locations

Hook settings can be placed in three locations:

| File | Scope |
|:-----|:------|
| `~/.claude/settings.json` | Global (all projects) |
| `.claude/settings.json` | Project-specific (committed) |
| `.claude/settings.local.json` | Project-specific (not committed) |
