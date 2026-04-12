---
id: TASK-1.7
title: 'Tutorial: multi-LLM consultation workflow'
status: Done
assignee:
  - '@myself'
created_date: '2026-03-25 04:45'
updated_date: '2026-03-25 06:23'
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
Create a tutorial for using exported context with the multi-llm-consult skill and external providers for second opinions or delegated analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Show how export context feeds a consultation workflow
- [x] #2 Explain how to interpret external model output as advisory
- [x] #3 Link the workflow back to main-session decision making
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a dedicated tutorial in site/tutorials/ for multi-LLM consultation.
2. Ground it in the current multi-llm-consult skill, provider configuration path, and export workflow.
3. Update the tutorials index to replace the summary-only block with a real tutorial link.
4. Verify the referenced script and rebuild site/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added site/tutorials/multi-llm-consultation.md as a step-by-step tutorial for provider setup, minimal context export, prompt-file creation, consult script invocation, and folding external model feedback back into the main Cortex workflow as advisory input. Updated site/tutorials/index.md to replace the summary-only Multi-LLM block with a real tutorial link. Verified the consult script help, the TUI entrypoint, and a successful site/ Jekyll build.
<!-- SECTION:FINAL_SUMMARY:END -->
