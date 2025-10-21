# Parallel Execution Rules

## 🔴 CRITICAL: Parallel-First Mindset

**Core Directive**: ALWAYS identify and execute parallel workstreams. Serial execution is a FAILURE unless proven necessary.

## Mandatory Parallel Execution

### 🔴 ALWAYS Use Parallel Agents When:
1. **Multiple Independent Tasks**: >2 tasks with no dependencies → Launch parallel Task agents
2. **Multi-File Operations**: >3 files → Use parallel tool calls or delegate to agents
3. **Multi-Domain Work**: Code + Tests + Docs → MUST run in parallel workstreams
4. **Analysis + Implementation**: Research in parallel with execution planning
5. **Quality Gates**: Code review, testing, documentation MUST run concurrently with implementation

### Parallel Execution Triggers (Auto-Activate)

**File Count Triggers:**
- 3-7 files → Parallel tool calls in single message
- 8-15 files → Launch 2-3 parallel Task agents
- 16+ files → Full delegation mode with agent coordination

**Scope Triggers:**
- 2+ directories → Parallel agents per directory
- Multiple services → Parallel agents per service
- Frontend + Backend → MUST be parallel workstreams

**Domain Triggers:**
- Implementation task → Auto-spawn parallel quality workstream
- Feature request → Code + Tests + Docs in parallel
- Refactoring → Changes + Validation in parallel

## Parallel Execution Patterns

### Pattern 1: Multi-File Changes
```
❌ WRONG (Serial):
- Read file1 → Edit file1 → Read file2 → Edit file2

✅ CORRECT (Parallel):
- Single message: Read(file1, file2, file3) in parallel
- Single message: Edit(file1, file2, file3) in parallel
```

### Pattern 2: Complex Features
```
❌ WRONG (Serial):
1. Implement feature
2. Write tests
3. Write docs
4. Review code

✅ CORRECT (Parallel):
Workstream 1: Implementation agent
Workstream 2: Test automation agent (parallel)
Workstream 3: Documentation agent (parallel)
Workstream 4: Code review agent (runs after 1-3 complete)
```

### Pattern 3: Codebase Exploration
```
❌ WRONG (Serial):
- Search pattern1 → Analyze → Search pattern2 → Analyze

✅ CORRECT (Parallel):
- Launch Explore agent with "quick" thoroughness
- Continue working while agent explores
- Use results when ready
```

## Dependency Analysis Protocol

### Before Every Task:
1. **Identify all subtasks** (30 seconds thinking)
2. **Mark dependencies** (what MUST be sequential?)
3. **Group independent work** (what CAN be parallel?)
4. **Create parallel plan** (how to maximize concurrency?)

### Dependency Categories:
- 🔴 **Sequential**: Must wait (data dependency, order matters)
- 🟢 **Parallel**: Can run concurrently (independent)
- 🟡 **Conditional**: Parallel until merge point

## Workstream Coordination

### Required Workstreams for ANY Code Change:

**Primary Workstream**: Implementation
- Code changes
- Configuration updates
- Dependency management

**Quality Workstream** (ALWAYS parallel to primary):
- Code review analysis
- Test generation/execution
- Documentation updates

**Validation Workstream** (After primary completes):
- Build verification
- Integration testing
- Deployment validation

### Workstream Launch Pattern:
```markdown
# Implementation Plan

## Parallel Workstreams

### Workstream 1: Feature Implementation
- Task agent: Build feature X
- Files: src/feature.ts, src/utils.ts

### Workstream 2: Quality Assurance (PARALLEL)
- Task agent: Generate tests + docs
- Files: tests/feature.test.ts, docs/feature.md

### Workstream 3: Code Review (AFTER 1 & 2)
- Code review agent: Analyze changes
- Quality gate: MUST pass before merge
```

## Agent Parallelization Rules

### 🔴 ALWAYS Use Task Tool When:
1. Subtask has >5 steps
2. Subtask requires >3 tool calls
3. Subtask is in different domain (code vs tests vs docs)
4. Subtask can run independently for >30 seconds

### Agent Launch Protocol:
```markdown
# CORRECT: Single message with multiple Task calls
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement feature X</description>
  <prompt>...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate tests for feature X</description>
  <prompt>...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>api-documenter</subagent_type>
  <description>Document feature X API</description>
  <prompt>...</prompt>
</invoke>
</function_calls>
```

## Performance Requirements

### Speed Metrics:
- **Plan Phase**: <60 seconds to identify all parallel opportunities
- **Launch Phase**: All parallel agents launched in SINGLE message
- **Coordination**: No agent waits idle while others work
- **Quality Gate**: Runs in parallel, not after completion

### Quality Metrics:
- **Parallelization Rate**: >80% of independent tasks run in parallel
- **Agent Utilization**: All available agents busy during peak work
- **Serial Bottlenecks**: <20% of total execution time

## Enforcement

### Pre-Execution Checklist:
- [ ] Identified all subtasks
- [ ] Marked all dependencies
- [ ] Grouped parallel work
- [ ] Quality workstream defined
- [ ] Agent launch message prepared

### Failure Modes (Auto-Correct):
❌ Serial execution when parallel possible → STOP and replan
❌ Quality gate missing → ADD quality workstream immediately
❌ Single agent when multiple possible → LAUNCH parallel agents
❌ Sequential tool calls when batchable → BATCH in single message

## Examples

### ✅ CORRECT: Feature Implementation
```
User: "Add user authentication"

Plan:
1. Workstream 1 (Implementation): Auth service + routes + middleware
2. Workstream 2 (Quality - PARALLEL): Tests + API docs + security review
3. Workstream 3 (Validation - AFTER): Integration tests + deployment check

Execution:
- Launch 2 agents in single message (implementation + quality)
- Both run simultaneously
- Validation agent launches when both complete
```

### ✅ CORRECT: Multi-File Refactoring
```
User: "Refactor error handling in 12 files"

Plan:
- Workstream 1: Files 1-6 (agent 1)
- Workstream 2: Files 7-12 (agent 2)
- Workstream 3: Test updates (agent 3 - parallel)
- Workstream 4: Code review (agent 4 - after 1-3)

Execution:
- Single message: Launch 3 agents in parallel
- Review agent launches when others complete
```

### ❌ WRONG: Serial Execution
```
User: "Add feature X"

BAD Plan:
1. Implement feature
2. THEN write tests
3. THEN write docs
4. THEN review code

WHY WRONG: Steps 2, 3 don't depend on 1 completing - should be parallel!
```
