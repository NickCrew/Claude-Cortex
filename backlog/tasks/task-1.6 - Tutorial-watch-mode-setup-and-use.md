---
id: TASK-1.6
title: 'Tutorial: watch mode setup and use'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 06:08'
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
Create a practical watch mode tutorial covering setup, thresholds, daemon usage, and what auto-activation feels like during real work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Cover foreground and daemon workflows
- [x] #2 Explain threshold tuning and when watch mode is useful versus noisy
- [x] #3 Reflect current cortex ai watch behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated watch-mode tutorial in site/tutorials/.
2. Base it on the current cortex ai watch CLI help and implementation defaults.
3. Update the tutorials index to point to the new page and retire the summary-only block.
4. Verify referenced commands and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/watch-mode.md as a dedicated watch-mode tutorial and linked it from site/tutorials/index.md. The new page uses the current cortex ai watch surfaces for foreground mode, daemon mode, threshold and interval tuning, scope narrowing, and when to prefer a one-time cortex ai recommend call. Verified the referenced CLI commands and rebuilt site/ successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
