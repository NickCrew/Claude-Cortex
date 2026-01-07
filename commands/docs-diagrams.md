---
name: "docs:diagrams"
description: "Generate Mermaid diagrams for documentation and system visualization"
category: utility
complexity: standard
mcp-servers: []
personas: [technical-writer, architect]
subagents: [mermaid-expert]
---

# /docs:diagrams — Skill-backed docs

## Use
- Load `skills/documentation-production/SKILL.md` (skill `documentation-production`) and follow it.
- Then load `skills/documentation-production/references/diagrams.md` for the detailed workflow.

## Usage
```
/docs:diagrams [description|input] [--type flowchart|sequence|erd|state|gantt|timeline|class|journey|quadrant|pie|gitgraph] [--style basic|styled]
```