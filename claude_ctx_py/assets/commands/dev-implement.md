---
name: "dev:implement"
description: "Feature and code implementation with intelligent persona activation and MCP integration"
category: workflow
complexity: standard
mcp-servers: [context7, sequential, magic, playwright]
personas: [architect, frontend, backend, security, qa-specialist]
subagents: [general-purpose, code-reviewer, test-automator]
---

# /dev:implement — Skill-backed implementation

## Use
- Load `skills/feature-implementation/SKILL.md` (skill `feature-implementation`) and follow it.
- Then load `skills/feature-implementation/references/implement.md` for the detailed workflow.

## Usage
```
/dev:implement [feature-description] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```