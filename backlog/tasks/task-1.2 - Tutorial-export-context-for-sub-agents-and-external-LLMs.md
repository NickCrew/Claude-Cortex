---
id: TASK-1.2
title: 'Tutorial: export context for sub-agents and external LLMs'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 04:49'
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
Create a task-oriented export tutorial focused on packaging the right context for another session, sub-agent, or external model without over-exporting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Cover export categories and selective export patterns
- [x] #2 Show a sub-agent handoff example and an external LLM handoff example
- [x] #3 Document safe defaults around scope and sensitive context
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated export tutorial page in site/tutorials/.
2. Cover selective export for sub-agents and external LLMs using verified cortex export commands.
3. Update the tutorials index so the new walkthrough is visible from the public manual.
4. Verify CLI help and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/export-context.md as a dedicated handoff tutorial and linked it from site/tutorials/index.md. Verified the documented cortex export command surface via CLI help and rebuilt site/ successfully. Live export execution in this worktree still hits the existing missing rich dependency, so the tutorial avoids claiming exact runtime output.
<!-- SECTION:FINAL_SUMMARY:END -->
