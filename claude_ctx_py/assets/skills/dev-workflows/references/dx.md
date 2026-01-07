# Reference: dx

# /dev:dx - Developer Experience Optimization

## Triggers
- Onboarding friction, slow setup, or inconsistent environments
- Repetitive development workflows that should be automated
- Build/test feedback loops that feel slow or unreliable
- Tooling or documentation gaps hurting productivity

## Usage
```
/dev:dx [scope] [--focus onboarding|workflow|tooling|docs|automation] [--depth light|normal|deep]
```

## Behavioral Flow
1. **Profile**: Map the current developer journey and daily workflows
2. **Identify**: Surface pain points, time sinks, and manual steps
3. **Improve**: Propose concrete automation and tooling changes
4. **Implement**: Update scripts, configs, docs, and helpers
5. **Validate**: Measure impact and provide a follow-up plan

Key behaviors:
- Prefer low-risk, incremental improvements with quick wins
- Document changes so teams can maintain them
- Provide before/after metrics when possible

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Multi-area DX work (onboarding + tooling + docs)
- ✅ Large repos with multiple workflows and environments
- ✅ Cross-team tooling audits

**Available subagents**:
- **dx-optimizer**: Workflow profiling, automation, tooling, documentation updates

**Delegation strategy**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>dx-optimizer</subagent_type>
  <description>Audit developer experience and propose improvements</description>
  <prompt>
    Analyze DX for the provided scope:
    - Onboarding time and setup steps
    - Workflow friction and automation opportunities
    - Tooling and docs gaps
    Deliver prioritized recommendations + implementation plan.
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Single script tweak or small README update
- ❌ One-off command alias creation

## Tool Coordination
- **Task tool**: Delegates to dx-optimizer for audits and plans
- **Read**: Inspect docs and tooling configs
- **Write**: Apply updates to scripts, docs, and config files
- **Exec**: Validate tooling changes where safe

## Examples

### Onboarding Improvements
```
/dev:dx onboarding --focus onboarding --depth deep
```

### Workflow Automation
```
/dev:dx "frontend build/test" --focus workflow
```

### Tooling and Docs Sweep
```
/dev:dx --focus tooling --depth normal
```

## Boundaries

**Will:**
- Improve onboarding, workflows, and documentation for developer productivity
- Recommend automation with clear justification and rollout steps

**Will Not:**
- Make sweeping changes without validation or a rollback plan
- Introduce tooling that conflicts with existing stack constraints
