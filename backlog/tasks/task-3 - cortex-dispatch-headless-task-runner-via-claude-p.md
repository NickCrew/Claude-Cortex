---
id: TASK-3
title: 'cortex dispatch: headless task runner via claude -p'
status: To Do
assignee: []
created_date: '2026-04-05 18:16'
labels:
  - cli
  - feature
  - claude-cli-integration
  - automation
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Headless task runner that pulls a task from backlog, composes context (active skills, rules, relevant files), and launches `claude -p --system-prompt <composed> --worktree --max-budget-usd <cap> --output-format json` to execute it unattended. Captures result and updates task status.

Target use cases: CI pipelines, cron jobs, batch processing — anywhere the TUI isn't open.

Key Claude CLI flags to wrap: `-p` (headless), `--system-prompt`, `--worktree`, `--max-budget-usd`, `--output-format json`, `--allowed-tools`.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cortex dispatch <task-id> pulls task from backlog and composes context
- [ ] #2 Launches claude -p with composed system prompt in a worktree
- [ ] #3 Respects --max-budget-usd for cost capping
- [ ] #4 Captures structured output and updates task status on completion
- [ ] #5 Works headlessly without user interaction
<!-- AC:END -->
