---
name: "analyze:troubleshoot"
description: "Diagnose and resolve issues in code, builds, deployments, and system behavior"
category: utility
complexity: basic
mcp-servers: [sequential]
personas: [debugger, system-analyst, devops-engineer]
subagents: [general-purpose, Explore]
---

# /analyze:troubleshoot — Skill-backed troubleshooting

## Use
- Load `skills/systematic-debugging/SKILL.md` (skill `systematic-debugging`) as the primary workflow.
- If the failure originates deep in the stack or data corruption is suspected, also load `skills/root-cause-tracing/SKILL.md` (skill `root-cause-tracing`).
- Keep the evidence-first, hypothesis-driven flow from the skill(s).

## Usage
```
/analyze:troubleshoot [issue] [--type bug|build|performance|deployment] [--trace] [--fix]
```