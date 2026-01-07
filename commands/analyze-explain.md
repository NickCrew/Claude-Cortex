---
name: "analyze:explain"
description: "Provide clear explanations of code, concepts, and system behavior with educational clarity"
category: workflow
complexity: standard
mcp-servers: [sequential, context7]
personas: [educator, architect, security-specialist]
subagents: [Explore, general-purpose]
---

# /analyze:explain — Skill-backed explanation

## Use
- Load `skills/code-explanation/SKILL.md` (skill `code-explanation`) and follow it.
- Then load `skills/code-explanation/references/explain.md` for the detailed workflow.

## Usage
```
/analyze:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```