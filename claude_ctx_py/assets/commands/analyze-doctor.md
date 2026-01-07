---
name: "analyze:doctor"
description: "Diagnose, validate, and optimize the cortex environment by checking for consistency, duplicates, redundancies, and suggesting optimizations."
category: utility
complexity: basic
mcp-servers: []
personas: [system-analyst, quality-engineer]
subagents: []
---

# /analyze:doctor — Skill-backed diagnostics

## Use
- Load `skills/context-health/SKILL.md` (skill `context-health`) and follow it.
- Then load `skills/context-health/references/doctor.md` for the detailed workflow.

## Usage
```bash
cortex doctor [--fix]
```
