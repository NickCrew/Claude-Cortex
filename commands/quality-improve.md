---
name: "quality:improve"
description: "Apply systematic improvements to code quality, performance, and maintainability"
category: workflow
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, performance-engineer, quality-engineer, security-specialist]
subagents: [general-purpose, code-reviewer, Explore]
---

# /quality:improve — Skill-backed improvement

## Use
- Load `skills/code-quality-workflow/SKILL.md` (skill `code-quality-workflow`) and follow it.
- Then load `skills/code-quality-workflow/references/quality-improve.md` for the detailed workflow.

## Usage
```
/quality:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```