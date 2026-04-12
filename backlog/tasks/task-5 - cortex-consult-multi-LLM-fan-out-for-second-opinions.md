---
id: TASK-5
title: 'cortex consult: multi-LLM fan-out for second opinions'
status: To Do
assignee: []
created_date: '2026-04-05 18:16'
labels:
  - cli
  - feature
  - multi-llm
  - claude-cli-integration
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Multi-LLM fan-out command. Launches `claude -p --model sonnet` and shells out to `gemini`/`codex` in parallel, collects responses, and synthesizes. Basically the `multi-llm-consult` skill as a CLI command.

Target use cases: getting a second opinion on a plan, comparing approaches across models, delegating a subtask to a specific model.

```
cortex consult "should we use WebSockets or SSE for this?"
cortex consult --models claude,gemini "review this migration plan"
cortex consult --plan  # fan out the current plan for review
```
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cortex consult launches multiple LLM providers in parallel
- [ ] #2 Collects and displays responses side-by-side or synthesized
- [ ] #3 Supports --models flag to select which providers to query
- [ ] #4 Supports piping context via stdin or --plan flag
- [ ] #5 Handles provider unavailability gracefully (partial results OK)
<!-- AC:END -->
