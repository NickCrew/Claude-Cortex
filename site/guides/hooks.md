---
layout: default
title: Hooks
parent: Guides
nav_order: 6
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

### Via CLI

```bash
cortex install link
```

This symlinks `hooks/` to `~/.claude/hooks/`.

### Manual Installation

Copy hook files and register them in `~/.claude/settings.json`:

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

## Hook Configuration

Hooks are configured in `hooks/hooks.json`, which the plugin manifest references:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/workspace_validator.py\""
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/secret_scan.py\""
          },
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/large_file_gate.py\""
          }
        ]
      }
    ]
  }
}
```

## Environment Variables

Hooks receive context through environment variables set by Claude Code:

| Variable | Description |
|:---------|:------------|
| `CLAUDE_HOOK_PROMPT` | The user's prompt text |
| `CLAUDE_CHANGED_FILES` | Colon-separated list of changed files |
| `CLAUDE_PLUGIN_ROOT` | Absolute path to the plugin directory |
| `CLAUDE_PROJECT_DIR` | Project root directory |

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

The most visible hook. It analyzes your prompt and project context to suggest skills after each message.

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

**Configuration:** Keyword-to-skill mappings are defined in `skills/skill-rules.json`. Edit this file to customize which skills are suggested for which keywords.

## Settings File Locations

Hook settings can be placed in three locations:

| File | Scope |
|:-----|:------|
| `~/.claude/settings.json` | Global (all projects) |
| `.claude/settings.json` | Project-specific (committed) |
| `.claude/settings.local.json` | Project-specific (not committed) |
