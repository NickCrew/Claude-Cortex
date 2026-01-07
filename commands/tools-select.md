---
name: "tools:select"
description: "Intelligent MCP tool selection based on complexity scoring and operation analysis"
category: special
complexity: high
mcp-servers: [codanna, morphllm]
personas: [architect, performance-engineer, tool-specialist]
subagents: []
---

# /tools:select — Skill-backed tool selection

## Use
- Load `skills/tool-selection/SKILL.md` (skill `tool-selection`) and follow it.
- Then load `skills/tool-selection/references/select.md` for the detailed workflow.

## Usage
```
/tools:select [operation] [--analyze] [--explain]
```