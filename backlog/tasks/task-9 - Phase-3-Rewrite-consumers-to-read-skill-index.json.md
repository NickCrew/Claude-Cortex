---
id: TASK-9
title: 'Phase 3: Rewrite consumers to read skill-index.json'
status: To Do
assignee: []
created_date: '2026-04-18 17:56'
labels:
  - skill-registry
  - consumers
dependencies: []
documentation:
  - doc-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Flip the three consumers to read the unified index. Ship as three independent commits so each can revert in isolation.

See plan: doc-1, section "Phase 3: Rewrite consumers".

**Deliverables (three separate commits):**
1. `hooks/skill_auto_suggester.py` reads `skills/skill-index.json` directly via stdlib JSON. Keeps current hit-count ranking algorithm. Keeps the SkillRecommender fallback for Layer 2.
2. `claude_ctx_py/skill_recommender.py::_load_rules` reads `skill-index.json` and constructs rule objects from `file_patterns` + `confidence` fields. Legacy `recommendation-rules.json` path remains as fallback until Phase 5.
3. `claude_ctx_py/activator.py` reads `skill-index.json`; drop PyYAML import; module shrinks to ~40 lines.

**Validation tests:**
- `cortex skills analyze "REST API"` returns `api-design-patterns` (parity)
- `cortex skills analyze "accessibility"` returns `accessibility-audit` (new coverage)
- UserPromptSubmit hook with prompt "prompt engineering" surfaces `prompt-engineering`
- Existing skill_recommender tests pass unmodified

**Depends on:** Phase 2 (needs populated index)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 hooks/skill_auto_suggester.py reads skill-index.json with stdlib only
- [ ] #2 skill_recommender.py _load_rules reads skill-index.json
- [ ] #3 activator.py reads skill-index.json; no PyYAML import
- [ ] #4 Three separate commits, each independently revertable
- [ ] #5 cortex skills analyze returns expected skills for parity and new-coverage test cases
- [ ] #6 Existing skill_recommender unit tests pass without fixture changes
<!-- AC:END -->
