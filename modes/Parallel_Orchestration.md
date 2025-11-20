---
name: Parallel_Orchestration
category: execution
priority: high
conflicts:
  - Sequential_Processing
  - Serial_Execution
dependencies:
  - parallel-execution-rules
  - quality-gate-rules
group: orchestration
overrides:
  quality_score_min: 7
  test_coverage_min: 85
tags:
  - performance
  - parallel
  - quality
  - agents
auto_activate_triggers:
  - multi_file_operations
  - code_generation
  - feature_request
  - bug_fix
---

# Parallel Orchestration Mode

**Purpose**: Enforce parallel-first execution with mandatory quality gates

## 🔴 CRITICAL DIRECTIVES

### 1. Parallel Execution is MANDATORY
- Serial execution is a FAILURE unless dependencies proven
- ALWAYS identify parallel opportunities before starting
- ALWAYS launch parallel agents in single message
- NO sequential work when parallel possible

### 2. Quality Gates are MANDATORY
- EVERY code change MUST have quality workstream
- Quality runs in PARALLEL with implementation
- Three pillars: Code Review + Tests + Documentation
- NO code merges without passing all gates

### 3. Agent Maximization is MANDATORY
- Use maximum available Task agents (visible subagents) for every task
- Idle agents during execution = planning failure
- Workstream coordination is required
- Agent output monitored and integrated
- User can see all agents' progress in real-time

## Auto-Activation Triggers

This mode ACTIVATES AUTOMATICALLY when:
- User requests ANY code change (creation, edit, refactor)
- Task involves >2 independent subtasks
- Multi-file operations (>3 files)
- Multi-domain work (code + tests + docs)
- Feature requests or bug fixes
- Performance optimization needed

**Manual Activation**: Use `--orchestrate` flag or activate mode explicitly

## Execution Protocol

### Phase 1: Analysis (30-60 seconds)
**REQUIRED STEPS**:
1. **Task Decomposition**: Break into smallest independent units
2. **Dependency Mapping**: Identify what MUST be sequential
3. **Parallel Grouping**: Group all independent work
4. **Agent Selection**: Choose optimal agents for each workstream
5. **Quality Planning**: Define quality workstream components

**OUTPUT**: Parallel execution plan with workstreams

### Phase 2: Planning (30 seconds)
**REQUIRED STEPS**:
1. **Workstream Definition**: Name and scope each workstream
2. **Agent Assignment**: Assign specific agent to each workstream
3. **Quality Gate Definition**: Code review + tests + docs agents
4. **Coordination Plan**: How workstreams will integrate
5. **Validation Criteria**: Pass/fail criteria for quality gates

**OUTPUT**: Detailed workstream launch plan

### Phase 3: Execution (Parallel)
**REQUIRED STEPS**:
1. **Single Message Launch**: ALL parallel Task agents in ONE message (visible to user)
2. **Quality Parallel Launch**: Quality workstream launches with primary via Task tool
3. **Progress Monitoring**: User and Claude track all agent outputs in real-time
4. **Coordination**: Manage dependencies between workstreams
5. **Integration**: Merge results as agents complete

**OUTPUT**: All Task agents (visible subagents) running simultaneously, user can monitor progress

### Phase 4: Validation (After Completion)
**REQUIRED STEPS**:
1. **Quality Gate Check**: Verify all gates passed
2. **Integration Verification**: Ensure workstreams integrated cleanly
3. **Issue Resolution**: Fix any quality gate failures
4. **Re-validation**: Run gates again if fixes applied
5. **Final Approval**: All gates green = task complete

**OUTPUT**: Validated, quality-assured deliverable

## Workstream Templates

### Template 1: Feature Implementation
```markdown
## Workstreams

### Primary: Feature Implementation
- **Agent**: general-purpose
- **Scope**: Core feature logic
- **Files**: src/feature.ts, src/utils.ts
- **Duration**: ~5 minutes

### Quality (PARALLEL):

#### Code Review
- **Agent**: code-reviewer
- **Scope**: All changes
- **Checks**: Security, performance, quality
- **Duration**: ~3 minutes

#### Test Automation
- **Agent**: test-automator
- **Scope**: Feature functionality
- **Target**: ≥85% coverage
- **Duration**: ~4 minutes

#### Documentation
- **Agent**: api-documenter
- **Scope**: Public API
- **Format**: OpenAPI + examples
- **Duration**: ~3 minutes

### Validation (AFTER Primary + Quality):
- Build verification
- Integration test
- Deployment check
```

### Template 2: Multi-File Refactor
```markdown
## Workstreams

### Primary 1: Files 1-5
- **Agent**: general-purpose
- **Scope**: Error handling in auth module
- **Files**: auth/*.ts (1-5)

### Primary 2: Files 6-10 (PARALLEL with Primary 1)
- **Agent**: general-purpose
- **Scope**: Error handling in API module
- **Files**: api/*.ts (1-5)

### Quality (PARALLEL with Primary 1 & 2):

#### Code Review
- **Agent**: code-reviewer
- **Scope**: All refactored files

#### Test Updates
- **Agent**: test-automator
- **Scope**: Updated test cases

### Validation (AFTER All):
- All tests pass
- No regressions
- Code review score ≥7/10
```

### Template 3: Bug Fix
```markdown
## Workstreams

### Primary: Bug Fix
- **Agent**: general-purpose
- **Scope**: Fix memory leak in auth service
- **Files**: src/auth/session.ts

### Quality (PARALLEL):

#### Code Review
- **Agent**: code-reviewer
- **Scope**: Verify fix doesn't introduce issues
- **Focus**: Memory management, resource cleanup

#### Regression Test
- **Agent**: test-automator
- **Scope**: Create test to prevent recurrence
- **Type**: Integration test

#### Documentation Update
- **Agent**: technical-writer
- **Scope**: Update known issues list
- **Format**: Changelog + migration notes

### Validation (AFTER All):
- Memory leak resolved (verified)
- Regression test passes
- No new issues introduced
```

## Parallel Execution Patterns

### Pattern 1: Simple Operations (Direct Tool Calls)
```markdown
✅ CORRECT for quick reads (1-2 files):
<function_calls>
<invoke name="Read"><parameter name="file_path">file1.ts</parameter></invoke>
<invoke name="Read"><parameter name="file_path">file2.ts</parameter></invoke>
</function_calls>

✅ BETTER for 3+ files or complex work (Visible Task agents):
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze files 1-5</description>
  <prompt>Read and analyze files 1-5...</prompt>
</invoke>
</function_calls>
User can now monitor this agent's progress!

❌ WRONG (Sequential):
Read file1 → Then read file2 → Then read file3
```

### Pattern 2: Parallel Agent Launch
```markdown
✅ CORRECT:
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implementation</description>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Code review</description>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Test generation</description>
</invoke>
</function_calls>

❌ WRONG (Sequential):
Launch implementation → Wait for completion → Launch tests
```

### Pattern 3: Multi-Directory Work
```markdown
✅ CORRECT:
Workstream 1: Frontend changes (agent 1)
Workstream 2: Backend changes (agent 2) - PARALLEL
Workstream 3: Database migrations (agent 3) - PARALLEL
Workstream 4: Quality gate (agent 4) - PARALLEL

All launched in single message

❌ WRONG:
Do frontend → Then backend → Then database
```

## Quality Gate Integration

### Mandatory Quality Workstream:

**EVERY task must have**:
1. **Primary workstream**: Implementation/changes
2. **Quality workstream**: Review + tests + docs (PARALLEL)
3. **Validation workstream**: Final checks (AFTER)

**No exceptions**: If implementing code, quality gate MUST run.

### Quality Agent Selection:

**For ANY code change**:
- code-reviewer (ALWAYS)
- test-automator (ALWAYS)
- Documentation agent (ALWAYS - pick based on type):
  - api-documenter (API changes)
  - technical-writer (Complex logic)
  - tutorial-engineer (User features)

### Quality Pass Criteria:

**ALL must pass**:
- [ ] Code review score ≥7/10
- [ ] Test coverage ≥85%
- [ ] All tests pass
- [ ] Documentation complete
- [ ] No critical/high issues

**If ANY fails**: Fix and re-run quality gate

## Agent Coordination

### Communication Flow:
```
Primary Agent → Work Output → Quality Agents
                                    ↓
Quality Agents → Reports → Validation Check
                                    ↓
                          Pass → Complete
                          Fail → Fix → Re-validate
```

### Status Tracking:
- Monitor all agent outputs in real-time
- Identify when agents complete
- Coordinate dependent work
- Report progress to user

### Issue Handling:
- Quality gate finds issues → Report to user
- Primary agent fixes issues → Re-run quality gate
- Maximum 3 iterations before requesting user guidance

## Performance Optimization

### Speed Targets:
- **Planning**: <60 seconds to create parallel plan
- **Launch**: All agents launched in <10 seconds (single message)
- **Execution**: All independent work runs simultaneously
- **Integration**: <30 seconds to merge results

### Efficiency Metrics:
- **Parallelization Rate**: >80% of work runs in parallel
- **Agent Utilization**: >90% of agents busy during execution
- **Quality Gate Coverage**: 100% of code changes
- **First-Time Pass Rate**: >90% quality gates pass on first run

## Failure Recovery

### Common Failures and Fixes:

**Failure**: Serial execution when parallel possible
**Fix**: STOP, replan with parallel execution, relaunch

**Failure**: Quality gate missing
**Fix**: STOP, add quality workstream, launch in parallel

**Failure**: Single agent when multiple possible
**Fix**: STOP, split work, launch multiple Task agents (visible subagents)

**Failure**: Using direct tool calls for complex work
**Fix**: STOP, use Task tool so user can monitor progress

**Failure**: No visible progress for user
**Fix**: STOP, switch to Task agents instead of direct tool calls

**Failure**: Quality gate failure (score <7, coverage <85%)
**Fix**: Address issues, re-run quality gate (max 3 iterations)

## Examples

### ✅ PERFECT EXECUTION:

**User Request**: "Add pagination to the users API"

**Analysis (30s)**:
- Primary: API endpoint changes
- Quality 1: Code review (parallel)
- Quality 2: Tests (parallel)
- Quality 3: API docs (parallel)
- Dependencies: None - all can run in parallel

**Plan (20s)**:
```markdown
Workstream 1: Implementation
- Modify GET /users endpoint
- Add pagination params
- Add pagination response metadata

Workstream 2: Code Review (PARALLEL)
- Review API changes
- Check for security issues
- Verify performance impact

Workstream 3: Tests (PARALLEL)
- Unit tests for pagination logic
- Integration tests for endpoint
- Edge case tests (page size, invalid params)

Workstream 4: Documentation (PARALLEL)
- Update OpenAPI spec
- Add pagination examples
- Document query parameters
```

**Execution (5min)**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement pagination</description>
  <prompt>Add pagination to GET /users endpoint...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review pagination implementation</description>
  <prompt>Review pagination changes for security, performance...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate pagination tests</description>
  <prompt>Create comprehensive test suite for pagination...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>api-documenter</subagent_type>
  <description>Document pagination API</description>
  <prompt>Update OpenAPI docs with pagination parameters...</prompt>
</invoke>
</function_calls>
```

**Validation (2min)**:
- Code review: 8/10 ✅
- Tests: 92% coverage, all pass ✅
- Docs: Complete with examples ✅
- **RESULT**: ALL GATES PASSED → COMPLETE

---

**Total Time**: ~7 minutes (vs ~15 minutes serial)
**Quality**: All gates passed
**Efficiency**: 4 agents ran in parallel = 4x faster
