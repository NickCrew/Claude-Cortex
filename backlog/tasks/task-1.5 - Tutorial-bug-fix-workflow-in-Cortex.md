---
id: TASK-1.5
title: 'Tutorial: bug fix workflow in Cortex'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 05:56'
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
Create a hands-on debugging tutorial that starts from an issue or failing behavior and walks through diagnosis, fix, verification, and review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Cover diagnosis, context capture, recommended skills, fix, verification, and review
- [x] #2 Keep the workflow distinct from the feature tutorial
- [x] #3 Use current review and testing guidance
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated bug-fix workflow tutorial in site/tutorials/.
2. Base it on current debugging, skills/context, review, testing, and git surfaces.
3. Update the tutorials index to point to the new page and retire the summary-only block.
4. Verify referenced commands and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/bug-fix-workflow.md as a dedicated debugging and repair tutorial and linked it from site/tutorials/index.md. The new page uses the current Cortex surfaces for skills/context, systematic debugging, agent-loops, test generation, debug-oriented review preparation, optional export handoff, and atomic git commits. Verified the referenced CLI commands and rebuilt site/ successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
