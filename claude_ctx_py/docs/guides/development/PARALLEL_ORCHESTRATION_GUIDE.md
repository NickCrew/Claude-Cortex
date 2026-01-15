# Parallel Orchestration & Quality Gates - Quick Reference

## ✅ What Was Configured

Your Claude context now ENFORCES:

1. **Parallel-First Execution**: Serial execution is a failure unless dependencies proven
2. **Mandatory Quality Gates**: Every code change gets code review + tests + docs
3. **Agent Maximization**: Use maximum available agents for every task
4. **Automatic Orchestration**: Parallel Orchestration mode auto-activates for code tasks

## 📋 Active Configuration

### Rules (ALWAYS ACTIVE):
- `/rules/parallel-execution-rules.md` - Enforces parallel execution patterns
- `/rules/quality-gate-rules.md` - Enforces quality gates for all code changes

### Modes (ALWAYS ACTIVE):
- `/modes/Parallel_Orchestration.md` - Orchestrates parallel execution with quality gates

### Agents (REQUIRED - Already Active):
- `code-reviewer` - Code quality and security analysis
- `test-automator` - Test generation and execution
- `api-documenter` - API documentation
- `quality-engineer` - Quality coordination
- `technical-writer` - Technical documentation

## 🎯 How It Works

### For ANY Code Change:

**Before (Serial)**:
```
1. Write code
2. Wait... then write tests
3. Wait... then write docs
4. Wait... then review code
Total Time: ~20 minutes
```

**Now (Parallel)**:
```
Launch in SINGLE message:
- Agent 1: Write code
- Agent 2: Generate tests (parallel)
- Agent 3: Write docs (parallel)
- Agent 4: Review code (parallel)

Total Time: ~5-7 minutes
Quality: All gates enforced
```

### Execution Pattern:

Every task follows this flow:

```markdown
## Task: [Your Request]

### Analysis (30-60s)
- Break into subtasks
- Identify dependencies
- Group parallel work
- Select agents
- Define quality gates

### Plan (30s)
Workstream 1: Implementation
Workstream 2: Code Review (PARALLEL)
Workstream 3: Tests (PARALLEL)
Workstream 4: Documentation (PARALLEL)

### Execution (Parallel)
<function_calls>
<invoke name="Task">Implementation agent</invoke>
<invoke name="Task">Code review agent</invoke>
<invoke name="Task">Test agent</invoke>
<invoke name="Task">Documentation agent</invoke>
</function_calls>

### Validation
- Code review score ≥7/10
- Test coverage ≥85%
- Documentation complete
- All gates PASS → Complete
```

## 🔍 What Claude Will Do Differently

### 1. Automatic Parallel Planning
**Before every task, Claude will:**
- Analyze for parallel opportunities
- Identify dependencies
- Create parallel execution plan
- Launch agents in single message

### 2. Mandatory Quality Gates
**For every code change, Claude will:**
- Launch quality workstream in parallel
- Run code review analysis
- Generate/update tests
- Create/update documentation
- Validate all gates pass

### 3. Agent Maximization
**Claude will prefer:**
- Multiple agents over single agent
- Parallel tool calls over sequential
- Delegation over direct execution
- Concurrent work over serial work

## 📊 Enforcement Triggers

### Parallel Execution Triggers:
- ✅ 3+ files → Parallel tool calls
- ✅ 8+ files → Multiple agents
- ✅ 2+ directories → Parallel agents per directory
- ✅ Multiple domains (code+tests+docs) → Parallel workstreams

### Quality Gate Triggers (ALL CODE CHANGES):
- ✅ File created/edited → Quality gate
- ✅ Function implemented → Quality gate
- ✅ API changed → Quality gate
- ✅ Configuration modified → Quality gate

## 🎬 Example: "Add User Profile Endpoint"

### Claude's Response:

```markdown
I'll implement the user profile endpoint with parallel quality assurance.

## Analysis
This requires:
1. API endpoint implementation
2. Code review for security/quality
3. Test generation for coverage
4. API documentation

All can run in parallel after implementation starts.

## Execution Plan

### Workstream 1: Implementation
- Create GET /api/profile endpoint
- Add authentication middleware
- Implement profile retrieval logic
- Files: src/api/profile.ts, src/middleware/auth.ts

### Workstream 2: Code Review (PARALLEL)
- Review security (auth, data exposure)
- Check performance (query optimization)
- Validate error handling
- Agent: code-reviewer

### Workstream 3: Test Generation (PARALLEL)
- Unit tests for profile endpoint
- Integration tests for auth flow
- Edge cases (invalid tokens, missing users)
- Target: ≥85% coverage
- Agent: test-automator

### Workstream 4: API Documentation (PARALLEL)
- OpenAPI specification
- Request/response examples
- Authentication requirements
- Error responses
- Agent: api-documenter

## Launching Workstreams

[Claude launches all 4 agents in single message]

## Results
- ✅ Implementation complete
- ✅ Code review: 8/10 (no critical issues)
- ✅ Tests: 92% coverage, all passing
- ✅ Documentation: Complete with examples

All quality gates passed! Implementation ready for deployment.
```

## 🛠️ Verification Commands

### Check Active Configuration:
```bash
# View status
cortex status

# List active modes
cortex mode status

# List active agents
cortex agent status

# Export current context
cortex export context my-config.md
```

### View Documentation:
```bash
# Parallel execution rules
cat ~/.claude/rules/parallel-execution-rules.md

# Quality gate rules
cat ~/.claude/rules/quality-gate-rules.md

# Orchestration mode
cat ~/.claude/modes/Parallel_Orchestration.md
```

## ⚙️ Configuration Files

All configuration is in `~/.claude/CLAUDE.md`:

```markdown
# Execution Rules (CRITICAL - ALWAYS ACTIVE)
@rules/parallel-execution-rules.md
@rules/quality-gate-rules.md

# Active Behavioral Modes
@modes/Parallel_Orchestration.md
```

## 🎯 Quality Gate Pass Criteria

For every code change, ALL must pass:

- [ ] **Code Review**: Score ≥7/10
  - No critical security issues
  - No major performance issues
  - Follows conventions

- [ ] **Tests**: Coverage ≥85%
  - All tests pass
  - Edge cases covered
  - No flaky tests

- [ ] **Documentation**: Complete
  - Public APIs documented
  - Complex logic explained
  - Examples provided

## 🚀 Benefits

### Speed:
- 3-4x faster execution through parallelization
- No waiting for sequential steps
- Maximum agent utilization

### Quality:
- 100% code review coverage
- Mandatory test coverage (≥85%)
- Complete documentation
- Issues caught early

### Consistency:
- Every change gets same quality treatment
- No skipped steps
- Enforced standards

## 📝 Notes

- **Automatic**: These rules apply automatically to all code tasks
- **Enforced**: Claude will stop and replan if patterns violated
- **Flexible**: User can override with explicit instructions
- **Quality-First**: Quality gates are mandatory, not optional

## 🔗 Related Documentation

- `/rules/parallel-execution-rules.md` - Complete parallel execution guide
- `/rules/quality-gate-rules.md` - Complete quality gate guide
- `/modes/Parallel_Orchestration.md` - Orchestration mode details
- `/rules/workflow-rules.md` - General workflow patterns

---

**Status**: ✅ ACTIVE - All rules and modes are enforced
**Last Updated**: 2025-10-21
