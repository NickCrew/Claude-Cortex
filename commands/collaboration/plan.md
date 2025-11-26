---
name: plan
description: "Plan-writing flow linking borrowed Superpowers skill to claude-ctx workflows and Task TUI"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, project-manager]
subagents: [Explore, general-purpose]
---

# /ctx:plan – Plan Writing

## Trigger Pattern
```
/ctx:plan [summary] [--streams n] [--save]
```

## Behavior
1. Restate objective + constraints from `/ctx:brainstorm`.
2. Break work into streams; map each to modes, rules, and agents.
3. For every task bullet:
   - Include Definition of Done + verification (tests, Supersaiyan visual, MCP check).
   - Create/update Task TUI entries (press `T` → `A`/`E`).
4. Document risks/mitigations + checkpoints.
5. Store plan in `docs/plans/<date>-<slug>.md` when `--save` is provided.

## Output
- Markdown plan table following `skills/collaboration/writing-plans/SKILL.md` template.
- Tasks synced to `tasks/current/active_agents.json`.

## Personas (Thinking Modes)
- **architect**: Technical structure, component organization, dependency mapping
- **project-manager**: Task breakdown, risk assessment, resource coordination

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Complex plan (>5 workstreams)
- ✅ Need codebase exploration for realistic estimates
- ✅ Multi-domain planning requiring technical validation
- ✅ Plan involves new feature assessment

**Available subagents**:
- **Explore**: Codebase analysis for technical planning context
- **general-purpose**: Complex task breakdown requiring deep analysis

**Delegation strategy for complex planning**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze codebase for planning context</description>
  <prompt>
    Explore for plan development:
    - Existing patterns and structure
    - Potential implementation approaches
    - Technical dependencies
    - Effort estimation context
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Break down complex feature into tasks</description>
  <prompt>
    Analyze feature requirements and break into tasks:
    - Stream organization
    - Definition of Done per task
    - Verification requirements
    - Risk identification
    Adopt architect + project-manager thinking.
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple plan (1-3 workstreams, clear scope)
- ❌ Plan refinement (already have context)
- ❌ Quick task list generation

## Tool Coordination
- **Task tool**: Launches subagents for complex planning requiring exploration/analysis
- **Read**: Brainstorm output, existing docs (direct)
- **Write**: Plan markdown document (direct)
- **TodoWrite**: Sync tasks to Task TUI

## Follow-up
- Run `/ctx:execute-plan` to enforce orchestration + verification.
