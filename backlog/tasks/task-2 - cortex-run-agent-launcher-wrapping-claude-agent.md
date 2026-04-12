---
id: TASK-2
title: 'cortex run: agent launcher wrapping claude --agent'
status: To Do
assignee: []
created_date: '2026-04-05 18:16'
labels:
  - cli
  - feature
  - claude-cli-integration
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Menu selector that lists active agents from `.active-agents`, lets the user pick one, then launches `claude --agent <name> --worktree` with the right system prompt composed from active skills + rules. Essentially the TUI's agent view but as a CLI launcher.

Key Claude CLI flags to wrap: `--agent`, `--append-system-prompt`, `--worktree`, `--permission-mode`.

Context: Claude CLI exposes `--agent`, `--agents`, `--system-prompt`, `--append-system-prompt`, `-p`, `--worktree`, `--output-format stream-json`, and `--allowed-tools` — a rich set of primitives for composing specialized agent sessions from the shell.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cortex run lists active agents and launches selected one via claude --agent
- [ ] #2 System prompt is composed from active skills and rules automatically
- [ ] #3 Supports --worktree flag passthrough for isolation
- [ ] #4 Works without TUI (pure CLI interaction)
<!-- AC:END -->
