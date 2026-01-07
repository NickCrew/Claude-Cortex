---
name: "test:generate-tests"
description: Generate comprehensive test suite with high coverage
category: testing
personas: [qa-specialist, developer]
subagents: [test-automator, quality-engineer]
---

# /test:generate-tests — Skill-backed test generation

## Use
- Load `skills/test-generation/SKILL.md` (skill `test-generation`) and follow it.
- Then load `skills/test-generation/references/generate-tests.md` for the detailed workflow.

## Usage
```
/test:generate-tests [path] [--type unit|integration|e2e|all] [--coverage-target 80]
```