---
name: "dev:code-review"
description: Comprehensive code quality review and analysis
category: development
personas: [quality-engineer, security-specialist]
subagents: [code-reviewer, security-auditor]
---

# /dev:code-review — Skill-backed review

## Use
- Load `skills/code-quality-workflow/SKILL.md` (skill `code-quality-workflow`) and follow it.
- Then load `skills/code-quality-workflow/references/code-review.md` for the detailed workflow.

## Usage
```
/dev:code-review [path] [--focus quality|security|performance|all]
```