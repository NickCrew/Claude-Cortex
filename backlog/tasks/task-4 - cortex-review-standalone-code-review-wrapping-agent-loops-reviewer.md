---
id: TASK-4
title: 'cortex review: standalone code review wrapping agent-loops reviewer'
status: To Do
assignee: []
created_date: '2026-04-05 18:16'
labels:
  - cli
  - feature
  - code-review
  - agent-loops
dependencies: []
references:
  - skills/agent-loops/scripts/specialist-review.sh
  - skills/agent-loops/scripts/triage_perspectives.py
  - skills/agent-loops/references/perspective-catalog.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Standalone CLI entry point for the agent-loops code review flow. Runs `triage_perspectives.py` on the current diff, selects 3-5 review perspectives from the catalog, composes the review prompt with relevant skill content, and dispatches to a reviewer (Claude preferred, Gemini/Codex fallback).

Now that `cortex review` has been deprecated in favor of `cortex suggest --review`, the `review` command name is free for actual code review.

Key assets to reuse:
- `skills/agent-loops/scripts/specialist-review.sh` — provider-aware review script
- `skills/agent-loops/scripts/triage_perspectives.py` — perspective selection
- `skills/agent-loops/references/perspective-catalog.md` — perspective-to-skill mapping
- `skills/agent-loops/references/review-prompt.md` — review prompt template
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 cortex review runs triage_perspectives.py on current diff
- [ ] #2 Selects 3-5 perspectives and composes review prompt with relevant skills
- [ ] #3 Dispatches to reviewer via specialist-review.sh provider chain
- [ ] #4 Outputs structured review artifact to .agents/reviews/
- [ ] #5 Supports --scope flag to limit review to specific files/dirs
<!-- AC:END -->
