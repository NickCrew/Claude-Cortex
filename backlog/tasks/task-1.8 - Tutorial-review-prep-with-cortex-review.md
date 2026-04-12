---
id: TASK-1.8
title: 'Tutorial: review prep with cortex review'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 06:39'
labels:
  - documentation
  - site
  - tutorial
dependencies: []
parent_task_id: TASK-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a short tutorial showing how cortex review helps load review-relevant skills before a manual or agent-assisted review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Keep cortex review clearly separate from agent-loops
- [x] #2 Show context flags and follow-on skill loading
- [x] #3 Position the tutorial as review preparation, not a full review engine
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated tutorial in site/tutorials/ for review prep with cortex review.
2. Keep the workflow clearly separate from agent-loops and focus on review preparation only.
3. Show dry-run and context-driven examples plus the follow-on cortex skills context step.
4. Update the tutorials index and verify the CLI surface and site build.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/review-prep.md as a short tutorial for using cortex review as a standalone review-preparation step. The page keeps cortex review clearly separate from agent-loops, shows dry-run and context-driven usage, and walks from recommendation preview into cortex skills context and the actual follow-on review skill. Updated site/tutorials/index.md to expose the tutorial and verified the review CLI help, direct cmd_review dry-run behavior, and a successful site/ Jekyll build.
<!-- SECTION:FINAL_SUMMARY:END -->
