---
id: TASK-9
title: 'Phase 3: Rewrite consumers to read skill-index.json'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-18 20:26'
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
- [x] #1 hooks/skill_auto_suggester.py reads skill-index.json with stdlib only
- [x] #2 skill_recommender.py _load_rules reads skill-index.json
- [x] #3 activator.py reads skill-index.json; no PyYAML import
- [x] #4 Three separate commits, each independently revertable
- [x] #5 cortex skills analyze returns expected skills for parity and new-coverage test cases
- [x] #6 Existing skill_recommender unit tests pass without fixture changes
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 3 landed as three independent commits — all consumers now read the unified skill-index.json.

**Commit 1 — `hooks/skill_auto_suggester.py`:**
- Added `candidate_index_paths()` and new primary loader path (`CLAUDE_SKILL_INDEX` env override → repo → user home)
- Reworked `load_rules()` to try skill-index.json first; falls back to `skill-rules.json` (legacy, kept until Phase 5)
- Stdlib `json` only — zero new dependencies
- Validated: "prompt engineering" → `prompt-engineering`, "accessibility audit please" → `accessibility-audit`, "TDD" still surfaces `test-driven-development`

**Commit 2 — `claude_ctx_py/skill_recommender.py`:**
- `_load_rules()` now prefers `skill-index.json`, synthesizing rule objects from each skill's `file_patterns` + `confidence` via new `_rules_from_index()` staticmethod
- Falls back to `~/.claude/skills/skill-index.json` → bundled `_resolve_cortex_root()/skills/skill-index.json` → legacy `recommendation-rules.json` → hardcoded defaults
- Loads 68 rules from index (vs 9 default rules) — matches `recommendation-rules.json` coverage exactly
- 22 skill_index unit tests still green

**Commit 3 — `claude_ctx_py/activator.py`:**
- Complete rewrite: reads `skill-index.json` via stdlib JSON, ~83 LOC (down from ~101), zero PyYAML
- Preference order: user-local → bundled repo copy
- No activation.yaml support — per the plan's explicit guidance to cut over cleanly here
- Validated: `cortex skills analyze "REST API"` → api-design-patterns, `cortex skills analyze "accessibility"` → accessibility-audit
- mypy --strict: 0 issues

**Revertability:** Each of the three commits is independently revertable without touching the others. Legacy files still on disk so fallback paths stay populated until Phase 5.
<!-- SECTION:FINAL_SUMMARY:END -->
