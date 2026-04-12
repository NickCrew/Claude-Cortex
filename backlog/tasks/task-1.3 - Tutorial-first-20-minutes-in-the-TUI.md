---
id: TASK-1.3
title: 'Tutorial: first 20 minutes in the TUI'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 04:58'
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
Turn the current TUI outline into a real onboarding tutorial that teaches the major views, when to use the TUI, and how it fits with CLI workflows.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Cover navigation, agents, skills, export, and command palette basics
- [x] #2 Explain when to switch between TUI and CLI
- [x] #3 Keep the walkthrough grounded in current bindings and screens
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated TUI onboarding tutorial in site/tutorials/.
2. Ground the walkthrough in current TUI view bindings and user flows.
3. Update the tutorials index to point to the new page.
4. Verify bindings/commands and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/tui-first-20-minutes.md as a real onboarding walkthrough and linked it from site/tutorials/index.md. Verified the documented bindings against claude_ctx_py/tui/constants.py and cortex tui --help, then rebuilt site/ successfully.
<!-- SECTION:FINAL_SUMMARY:END -->
