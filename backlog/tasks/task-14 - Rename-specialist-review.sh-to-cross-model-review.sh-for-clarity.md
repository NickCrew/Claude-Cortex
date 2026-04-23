---
id: TASK-14
title: Rename specialist-review.sh to cross-model-review.sh for clarity
status: To Do
assignee: []
created_date: '2026-04-23 06:01'
labels:
  - refactor
  - naming
  - agent-loops
  - clarity
dependencies: []
references:
  - skills/agent-loops/scripts/specialist-review.sh
  - skills/agent-loops/SKILL.md
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The script name `specialist-review.sh` doesn't signal what makes the tool valuable — its real role is enabling **cross-model independent review** via provider rotation (reviewer is a different model family than the current agent). "Specialist" reads like "domain specialist" but the reviewer isn't a specialist — it's just a single-turn review from whatever provider the rotation picks.

The mismatch is epistemic, not functional: future readers spend time figuring out what "specialist" means instead of immediately understanding the design. The "Why Shell-Based Review" section already added to agent-loops/SKILL.md calls this out as "cross-model independent review" — naming the script after that concept would make the design legible end-to-end.

**Proposed name:** `cross-model-review.sh`

**Alternatives considered:**
- `independent-review.sh` — too ambiguous (cross-model vs. fresh-context)
- `single-turn-review.sh` — jargon-heavy
- `provider-review.sh` — confusable with existing `review-provider.sh`

**Blast radius (estimated):** 60-90 call sites across:
- skills/agent-loops/SKILL.md (many mentions, including polling invocation examples)
- docs/reference/skill-showcase.md (showcase entry)
- site/reference/skills.md (parallel showcase)
- tests/unit/test_agent_loops_review_scripts.py (5+ dedicated tests + shared constants)
- codex/skills/claude-consult/SKILL.md (cross-reference)
- backlog/tasks/task-* (any tasks referencing it, e.g., task-4, task-6)
- Sibling scripts (review-provider.sh comments, diff-test-audit.sh if it mentions)

**Recommend as its own focused session**, not bundled with other work. The previous rename (test-review-request → diff-test-audit, ~42 sites) had a git-stash recovery incident. Specialist-review is larger and deserves clean scope.

**Environment variable names left unchanged** (user-facing API):
- `SPECIALIST_REVIEW_PROVIDER` stays
- `AGENT_LOOPS_LLM_PROVIDER` stays
- This creates a minor inconsistency (script name vs. env var name) but avoids a breaking change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script renamed to cross-model-review.sh (or agreed alternative)
- [ ] #2 All call sites across skills, docs, tests, backlog, and sibling scripts updated
- [ ] #3 Environment variable names left unchanged for backward compatibility
- [ ] #4 Full pytest suite passes (currently 15/15 for test_agent_loops_review_scripts.py)
- [ ] #5 SKILL.md updated to reflect new name in bundled-scripts listing and all invocation examples
<!-- AC:END -->
