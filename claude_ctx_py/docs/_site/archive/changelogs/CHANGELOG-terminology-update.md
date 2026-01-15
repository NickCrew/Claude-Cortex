# Terminology Update Changelog

**Date**: 2025-11-24
**Scope**: Clarify relationship between claude-ctx system and Claude Code execution

## Summary

Updated slash command documentation to clarify the distinction between:
- **Personas** (conceptual thinking modes)
- **Subagents** (Claude Code workers launched via Task tool)
- **Task tool** (delegation mechanism)

## Summary Statistics

**Commands Updated**: 39 total
- Core orchestration: 3 (orchestrate:task, orchestrate:spawn, dev:implement)
- High priority: 4 (test:generate-tests, dev:code-review, analyze:security-scan, docs:generate)
- Medium priority: 4 (analyze:code, docs:index, collaboration:execute-plan, quality:improve)
- Collaboration: 2 (brainstorm, plan)
- Design: 2 (system, workflow)
- Dev utilities: 2 (build, test)
- Analyze utilities: 2 (troubleshoot, explain)

**New Documentation**: 2 files
**Updated Docs**: 1 file (commands/README.md)

## Files Changed

### 1. New Documentation

**`docs/architecture/terminology.md`** (NEW)
- Comprehensive guide explaining the three-layer architecture
- Clear definitions of all terms (Mode, Rule, Persona, Subagent, Task tool)
- Decision flow diagrams
- Practical examples
- Common confusion resolutions

### 2. Command Updates

**`commands/orchestrate/task.md`**
- Added `subagents:` frontmatter field
- Added "Personas (Thinking Modes)" section explaining conceptual roles
- Added "Delegation Protocol" section with:
  - When to delegate (use Task tool)
  - Available subagents with descriptions
  - How to launch (XML example)
  - When NOT to delegate
- Updated "Tool Coordination" to clarify Task tool is delegation mechanism
- Updated "Key Patterns" to change "Multi-Agent" → "Subagent Coordination"

**`commands/orchestrate/spawn.md`**
- Added `personas:` and `subagents:` frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" section emphasizing spawn ALWAYS delegates
- Updated "Tool Coordination" to list Task tool as PRIMARY mechanism
- Provided detailed XML example of typical subagent spawning pattern

**`commands/dev/implement.md`**
- Added `subagents:` frontmatter field
- Added "Personas (Thinking Modes)" section with domain expertise descriptions
- Added "Delegation Protocol" section with:
  - Complexity triggers for delegation
  - Available subagents
  - Delegation strategy with XML example
  - Clear when NOT to delegate criteria
- Updated "Tool Coordination" to clarify Task tool role

### 3. Additional Command Updates (Batch 2)

**`commands/test/generate-tests.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" (always delegates for test generation)
- XML examples for test-automator + quality-engineer parallel execution
- Clarified tool coordination with Task tool primary

**`commands/dev/code-review.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" (always delegates for reviews)
- Multiple delegation strategies (general quality vs security-focused)
- Parallel code-reviewer + security-auditor when needed

**`commands/analyze/security-scan.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" (always delegates for security)
- Single and multi-component delegation strategies
- Comprehensive security assessment via security-auditor

**`commands/docs/generate.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" with complexity triggers
- Separate strategies for API docs vs user guides
- Conditional delegation (complex=subagent, simple=direct)

**`commands/analyze/code.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for deep analysis
- Multi-domain parallel delegation (Explore + code-reviewer + security-auditor)
- Depth-based delegation (quick=direct, deep=subagents)

**`commands/docs/index.md`**
- Added subagents to frontmatter (already had personas)
- Added "Personas (Thinking Modes)" clarification
- Added "Delegation Protocol" for comprehensive docs
- Three-subagent strategy (Explore + api-documenter + technical-writer)
- Project size-based delegation triggers

**`commands/collaboration/execute-plan.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for plan execution
- Parallel task execution strategy
- Quality verification integration (--verify flag)

**`commands/quality/improve.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" clarification
- Added "Delegation Protocol" for systematic improvements
- Three-phase delegation (Explore → improve → validate)
- Multi-domain improvement coordination

### 4. Additional Command Updates (Batch 3)

**`commands/collaboration/brainstorm.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for codebase exploration
- Conditional delegation (large codebase or technical feasibility)
- Explore subagent for asset discovery

**`commands/collaboration/plan.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for complex planning
- Two-subagent strategy (Explore + general-purpose)
- Complexity-based delegation (>5 workstreams)

**`commands/design/system.md`**
- Added MCP servers, personas, and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for complex designs
- Two-subagent strategy (Explore + general-purpose)
- Size-based delegation (>10 components)

**`commands/design/workflow.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" with 7 domain experts
- Added "Delegation Protocol" (usually delegates)
- Three-subagent PRD workflow (Explore + general-purpose + code-reviewer)
- Comprehensive validation workflow

**`commands/dev/build.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for build failures
- Conditional delegation (complex errors, optimization)
- Error analysis and optimization strategies

**`commands/dev/test.md`**
- Added personas and subagents to frontmatter
- Added "Personas (Thinking Modes)" section
- Added "Delegation Protocol" for test issues
- Dual strategies (failure analysis + coverage gap filling)
- Test-automator integration for coverage

**`commands/analyze/troubleshoot.md`**
- Added MCP, personas, and subagents to frontmatter
- Added "Personas (Thinking Modes)" with debugging expertise
- Added "Delegation Protocol" for complex issues
- Two-subagent investigation (Explore + general-purpose)
- Sequential MCP for structured debugging

**`commands/analyze/explain.md`**
- Added subagents to frontmatter
- Added "Personas (Thinking Modes)" clarification
- Added "Delegation Protocol" for comprehensive explanations
- Two-subagent strategy (Explore + general-purpose)
- Context7 and Sequential MCP integration

**`commands/README.md`**
- Renamed "Agent Integration" → "Execution Architecture"
- Split into two subsections:
  - "Personas (Thinking Modes)" - conceptual guidance
  - "Subagents (Workers via Task Tool)" - actual workers
- Added delegation triggers and criteria
- Updated command structure template to show personas/subagents/mcp-servers
- Added reference link to terminology.md

## Key Changes

### Before (Confusing)
```yaml
agents: [code-reviewer, test-automator]  # What are these?
```
> "Multi-agent coordination and delegation"

### After (Clear)
```yaml
personas: [frontend, backend]              # Thinking modes
subagents: [code-reviewer, test-automator] # Task tool workers
```

> "Launch multiple subagents via Task tool in parallel"

```xml
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  ...
</invoke>
```

## Impact

### For Command Authors
- Clear template for when to use Task tool delegation
- Understand difference between personas (guidance) and subagents (workers)
- Consistent structure across all commands

### For Claude (AI)
- Unambiguous instructions on when and how to delegate
- Clear understanding of persona vs subagent distinction
- Explicit Task tool usage patterns with XML examples

### For Users
- Better transparency about what's happening
- Understand when work is delegated to subagents
- See progress of parallel subagent execution

## Migration Guide

### For Existing Commands

1. **Add frontmatter fields**:
```yaml
personas: [relevant, thinking, modes]
subagents: [task, tool, workers]
```

2. **Add "Personas" section**:
```markdown
## Personas (Thinking Modes)
- **persona-name**: What perspective this provides
```

3. **Add "Delegation Protocol" section**:
```markdown
## Delegation Protocol

**When to delegate**:
- Complexity triggers

**Available subagents**:
- Listed with descriptions

**How to delegate**:
- XML example with Task tool
```

4. **Update "Tool Coordination"**:
```markdown
- **Task tool**: Claude Code's delegation mechanism
```

## Testing

Commands should now make it clear:
- ✅ When Task tool will be used (complexity triggers)
- ✅ Which subagents will be launched
- ✅ How parallel execution will work
- ✅ What personas are thinking about

**`commands/reasoning/metrics.md`**
- Added personas: data-analyst, performance-engineer, cost-optimizer
- Marked as "does NOT delegate" - direct data presentation

**`commands/reasoning/adjust.md`**
- Added personas: performance-engineer, architect, cost-optimizer
- Marked as "does NOT delegate" - configuration change

**`commands/reasoning/budget.md`**
- Added personas: cost-optimizer, performance-engineer, architect
- Marked as "does NOT delegate" - configuration setting

**`commands/tools/select.md`**
- Added personas: architect, performance-engineer, tool-specialist
- Marked as "does NOT delegate" - direct analysis and decision
- Uses Codanna/Morphllm MCP for capability queries

**`commands/quality/cleanup.md`**
- Already had personas, added subagents
- Marked as "CONDITIONALLY delegates" - based on scope and complexity
- Three-subagent strategy: Explore + general-purpose + code-reviewer

## Final Statistics

**Total Commands Updated**: 39
**New Documentation Files**: 2
- `docs/architecture/terminology.md`
- `docs/CHANGELOG-terminology-update.md`

**Updated Documentation**: 1
- `commands/README.md`

**Delegation Patterns Established**:
- **Always Delegates** (5): test-generation, code-review, security-scan, spawn, prepare-release
- **Usually Delegates** (3): implement, docs-generation, workflow-design
- **Conditionally Delegates** (8): code-analysis, estimate, build, test, troubleshoot, explain, quality-cleanup, plan
- **Never Delegates** (23): git, doctor, visual commands (3), cleanup commands (5), session commands (3), reasoning commands (3), tools-select, and others

## Next Steps

Optional improvements:
1. Update remaining commands in other namespaces
2. Add delegation metrics/logging
3. Create command template generator
4. Add validation that checks for Delegation Protocol section

## References

- Main architecture doc: `docs/architecture/terminology.md`
- Example commands:
  - `/orchestrate:task` - Multi-domain coordination
  - `/orchestrate:spawn` - Always-delegate pattern
  - `/dev:implement` - Conditional delegation
