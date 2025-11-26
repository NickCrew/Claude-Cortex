---
name: brainstorm
description: "Kick-off brainstorming flow adapted from Superpowers, wired to claude-ctx Supersaiyan mode and Task TUI"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, product-manager]
subagents: [Explore]
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

## Personas (Thinking Modes)
- **architect**: System design thinking, technical feasibility, architecture patterns
- **product-manager**: User value, business goals, success metrics, prioritization

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large existing codebase (need to explore assets/constraints)
- ✅ Technical feasibility research (>3 solution options requiring deep analysis)
- ✅ Multi-domain brainstorm (frontend + backend + infrastructure)

**Available subagents**:
- **Explore**: Discover existing assets (agents, modes, rules, workflows)

**Delegation strategy for codebase exploration**:
```xml
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Discover existing assets and constraints</description>
  <prompt>
    Explore project for brainstorming context:
    - Existing agents, modes, rules, workflows
    - Current architecture patterns
    - Technical constraints and capabilities
    - Reusable components
    Thoroughness: quick (just need overview)
  </prompt>
</invoke>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple brainstorming session (no codebase exploration)
- ❌ Conceptual ideation (no technical validation needed)
- ❌ Quick option generation (<3 solutions)

## Tool Coordination
- **Task tool**: Launches Explore for codebase asset discovery when needed
- **Read**: Existing plans, docs, constraints (direct)
- **Write**: Brainstorm output markdown (direct)
- **TodoWrite**: Seed Task TUI entries for follow-up

## Follow-up
- Run `/ctx:plan` immediately, feeding it the brainstorm output.
