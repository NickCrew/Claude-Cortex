---
name: "analyze:code"
description: "Comprehensive code analysis across quality, security, performance, and architecture domains"
category: utility
complexity: basic
mcp-servers: []
personas: [analyzer, architect, security-specialist, performance-engineer]
subagents: [code-reviewer, security-auditor, Explore]
---

# /analyze:code — Skill-backed quality analysis

## Use
- Load `skills/code-quality-workflow/SKILL.md` (skill `code-quality-workflow`) and follow it.
- Then load `skills/code-quality-workflow/references/analyze-code.md` for the detailed workflow.

## Usage
```
/analyze:code [target] [--focus quality|security|performance|architecture] [--depth quick|deep|ultra] [--reasoning-profile default|security|performance|architecture|data|testing] [--format text|json|report]
```