---
name: brainstorm
description: "Kick-off brainstorming flow adapted from Superpowers, wired to claude-ctx Supersaiyan mode and Task TUI"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, product]
---

# /ctx:brainstorm – Structured Ideation

## Trigger Pattern
```
/ctx:brainstorm [topic] [--constraints ...]
```

## Behavior
1. Load `modes/Super_Saiyan.md` for visual/tone context.
2. Capture **Goals**, **Success Signals**, **Constraints**, **Existing Assets** (agents/modes/rules/workflows).
3. Generate ≥3 solution options with pros/cons and required verification.
4. Select a direction, list open questions, and specify immediate next checks.
5. Seed Task view entries (press `T` → `A`) or hand off to `/ctx:plan`.

## Output
- Markdown block following the template in `skills/collaboration/brainstorming/SKILL.md`.
- Optional file drop under `docs/plans/<date>-brainstorm.md`.

## Follow-up
- Run `/ctx:plan` immediately, feeding it the brainstorm output.
