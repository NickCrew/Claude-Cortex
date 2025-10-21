# Quality Gate Rules

## 🔴 CRITICAL: Quality Gates are MANDATORY

**Core Directive**: EVERY code change MUST have a parallel quality workstream. No exceptions.

## The Three Pillars Quality Gate

### 🔴 ALWAYS Required (Run in Parallel):

1. **Code Review**: Quality analysis of all changes
2. **Tests**: Comprehensive test coverage
3. **Documentation**: API docs, guides, or comments

**Failure Mode**: If ANY code is written without a quality workstream → STOP and add it immediately.

## Quality Workstream Triggers

### Auto-Activate Quality Gate When:
- [ ] ANY file is created
- [ ] ANY file is edited
- [ ] ANY function is implemented
- [ ] ANY API is changed
- [ ] ANY configuration is modified
- [ ] ANY dependency is updated

**No Exceptions**: If code changes, quality gate MUST run.

## Quality Workstream Components

### 1. Code Review (ALWAYS)
**Agent**: code-reviewer
**Timing**: Launches in parallel with implementation
**Scope**: All changed files
**Output**: Quality report with issues prioritized

**Required Checks**:
- [ ] Security vulnerabilities
- [ ] Performance issues
- [ ] Code quality violations
- [ ] Architecture concerns
- [ ] Best practice violations

### 2. Tests (ALWAYS)
**Agent**: test-automator
**Timing**: Launches in parallel with implementation
**Scope**: All new/changed functionality
**Coverage**: ≥85% (configurable)

**Required Tests**:
- [ ] Unit tests for new functions
- [ ] Integration tests for API changes
- [ ] Edge cases and error handling
- [ ] Regression tests for bug fixes

### 3. Documentation (ALWAYS)
**Agent**: Depends on type
- API changes → api-documenter
- User features → tutorial-engineer
- Complex logic → technical-writer

**Required Docs**:
- [ ] API documentation (if public interface)
- [ ] Code comments (if complex logic)
- [ ] README updates (if user-facing)
- [ ] Migration guides (if breaking changes)

## Quality Gate Execution Pattern

### Standard Pattern:
```markdown
## Implementation Plan

### Primary Workstream: Implementation
**Task**: Implement feature X
**Agent**: general-purpose
**Files**: src/feature.ts, src/utils.ts

### Quality Workstream (PARALLEL - MANDATORY)
**Launches simultaneously with implementation**

#### Component 1: Code Review
**Agent**: code-reviewer
**Scope**: All changes
**Deliverable**: Quality report

#### Component 2: Testing
**Agent**: test-automator
**Scope**: Feature X functionality
**Deliverable**: Test suite with ≥85% coverage

#### Component 3: Documentation
**Agent**: api-documenter
**Scope**: Feature X public API
**Deliverable**: API documentation

### Validation Workstream (AFTER Implementation + Quality)
**Task**: Verify all gates passed
**Checks**:
- [ ] Code review score ≥7/10
- [ ] Tests pass with ≥85% coverage
- [ ] Documentation complete and accurate
```

## Quality Gate Launch Code

### ✅ CORRECT: Always Launch in Parallel
```xml
<function_calls>
<!-- Primary workstream -->
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement feature X</description>
  <prompt>Implement user authentication feature...</prompt>
</invoke>

<!-- Quality workstream (PARALLEL - MANDATORY) -->
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review authentication implementation</description>
  <prompt>Review all changes for security, performance, and quality issues...</prompt>
</invoke>

<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate tests for authentication</description>
  <prompt>Generate comprehensive test suite for authentication with ≥85% coverage...</prompt>
</invoke>

<invoke name="Task">
  <subagent_type>api-documenter</subagent_type>
  <description>Document authentication API</description>
  <prompt>Document authentication API endpoints, request/response formats...</prompt>
</invoke>
</function_calls>
```

### ❌ WRONG: No Quality Gate
```xml
<!-- THIS IS A FAILURE -->
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement feature X</description>
  <prompt>Implement feature...</prompt>
</invoke>
</function_calls>

<!-- WHERE IS THE QUALITY GATE?! -->
```

## Quality Gate Pass Criteria

### Minimum Requirements (ALL must pass):

1. **Code Review**: Score ≥7/10
   - No critical security issues
   - No major performance issues
   - Follows project conventions
   - Architecture is sound

2. **Tests**: Coverage ≥85%
   - All tests pass
   - Edge cases covered
   - Error handling tested
   - No flaky tests

3. **Documentation**: Completeness check
   - Public APIs documented
   - Complex logic explained
   - Examples provided
   - Migration guide (if needed)

### Failure Handling:

**If Quality Gate Fails**:
1. Agent reports specific issues
2. Implementation agent fixes issues
3. Quality gate re-runs automatically
4. Repeat until all gates pass

**Max Iterations**: 3 attempts
**Escalation**: If still failing after 3 attempts, request user guidance

## Integration with Development Workflow

### Every Feature Request:
```
User Request → Plan → Implementation + Quality (Parallel) → Validation → Complete
                          ↓                    ↓
                     Code written        Review/Test/Doc
                                              ↓
                                        Quality report
                                              ↓
                                    Pass? → Continue
                                    Fail? → Fix + Retry
```

### Every Bug Fix:
```
Bug Report → Analysis → Fix + Quality (Parallel) → Validation → Complete
                            ↓              ↓
                        Code fix      Test for regression
                                           ↓
                                    Quality report
                                           ↓
                                  Pass? → Continue
                                  Fail? → Fix + Retry
```

### Every Refactor:
```
Refactor Plan → Changes + Quality (Parallel) → Validation → Complete
                    ↓               ↓
                Updates      Review + Test updates
                                    ↓
                              Quality report
                                    ↓
                          Pass? → Continue
                          Fail? → Fix + Retry
```

## Quality Gate Agents

### Required Agents (Activate These):
```bash
# Core quality gate agents
claude-ctx agent activate code-reviewer
claude-ctx agent activate test-automator
claude-ctx agent activate api-documenter

# Additional quality agents (recommended)
claude-ctx agent activate quality-engineer
claude-ctx agent activate security-auditor
claude-ctx agent activate technical-writer
claude-ctx agent activate tutorial-engineer
```

### Agent Responsibilities:

**code-reviewer**:
- Security analysis
- Performance review
- Code quality assessment
- Architecture validation

**test-automator**:
- Unit test generation
- Integration test creation
- Coverage analysis
- Test execution

**api-documenter**:
- API endpoint documentation
- Request/response schemas
- Authentication details
- Rate limits and quotas

**quality-engineer**:
- Overall quality coordination
- Standards enforcement
- Metric tracking
- Process improvement

## Enforcement Mechanisms

### Pre-Flight Check (Before Any Code Change):
1. Is quality workstream defined? → YES/NO
2. Are quality agents identified? → YES/NO
3. Is parallel execution planned? → YES/NO

**If ANY answer is NO**: STOP and fix before proceeding

### Mid-Flight Check (During Implementation):
1. Is quality workstream running? → YES/NO
2. Are agents making progress? → YES/NO
3. Is coordination working? → YES/NO

**If ANY answer is NO**: Investigate and correct immediately

### Post-Flight Check (After Implementation):
1. Did all quality gates run? → YES/NO
2. Did all quality gates pass? → YES/NO
3. Were issues addressed? → YES/NO

**If ANY answer is NO**: Task is NOT complete

## Quality Gate Metrics

### Success Metrics:
- **Quality Gate Coverage**: 100% of code changes
- **Parallel Execution Rate**: >95% of quality gates run in parallel
- **Pass Rate**: >90% first-time pass rate
- **Issue Detection**: >80% of issues found by gates vs manual review

### Tracking:
Every quality gate execution should log:
- Timestamp
- Files reviewed
- Issues found (by severity)
- Tests generated/run
- Documentation created
- Pass/fail status

## Examples

### ✅ CORRECT: Feature with Quality Gate
```
User: "Add user profile endpoint"

Implementation Plan:

1. Primary Workstream: API Implementation
   - Create /api/profile endpoint
   - Add authentication middleware
   - Implement profile retrieval logic

2. Quality Workstream (PARALLEL):
   a. Code Review: Security, performance, best practices
   b. Tests: Unit + integration tests, ≥85% coverage
   c. Docs: API documentation with examples

3. Validation: All gates pass

Execution: Launch all in single message (1 implementation + 3 quality agents)
```

### ✅ CORRECT: Bug Fix with Quality Gate
```
User: "Fix memory leak in auth service"

Implementation Plan:

1. Primary Workstream: Bug Fix
   - Identify leak source
   - Implement fix
   - Verify fix resolves issue

2. Quality Workstream (PARALLEL):
   a. Code Review: Ensure fix doesn't introduce new issues
   b. Tests: Regression test to prevent future recurrence
   c. Docs: Update known issues list

3. Validation: All gates pass

Execution: Launch all in single message (1 fix + 3 quality agents)
```

### ❌ WRONG: No Quality Gate
```
User: "Add feature X"

BAD Implementation:
1. Implement feature
2. Commit code

MISSING:
- No code review
- No tests
- No documentation
- No quality validation

THIS IS A FAILURE - Quality gate is mandatory!
```

## Quality Gate Philosophy

**Principle**: Quality is not a phase, it's a parallel process.

**Mindset**: Every line of code written has a corresponding quality line written simultaneously.

**Practice**: Implementation and quality assurance are twins, not sequential siblings.

**Result**: Higher quality, faster delivery, fewer bugs, better docs, happier users.
