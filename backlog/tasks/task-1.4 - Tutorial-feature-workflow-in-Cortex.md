---
id: TASK-1.4
title: 'Tutorial: feature workflow in Cortex'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 05:11'
labels:
  - documentation
  - site
  - tutorial
dependencies: []
parent_task_id: TASK-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create an end-to-end tutorial for feature work in Cortex, from planning and context setup through implementation, review, and commit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Show planning, skill context, agent activation, git worktree, tmux, and agent-loops together
- [x] #2 Use current command surfaces and skill-derived slash commands only
- [x] #3 End with a clean commit-oriented workflow
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated feature workflow tutorial in site/tutorials/.
2. Base it on the current skills, agent activation, worktree, tmux, agent-loops, and cortex git surfaces.
3. Update the tutorials index to point to the new page and retire the old summary-only section.
4. Verify referenced commands and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/feature-workflow.md as a real end-to-end feature workflow tutorial and linked it from site/tutorials/index.md. The tutorial now uses the current Cortex surfaces for skills, agent recommendations, agent activation, worktrees, tmux, agent-loops, review, and atomic git commits, without relying on the older missing collaboration skills. Verified the referenced CLI commands and rebuilt site/ successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
