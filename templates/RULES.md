# Claude Code Behavioral Rules

## Rule Priority System
**🔴 CRITICAL**: Security, data safety, production breaks - Never compromise
**🟡 IMPORTANT**: Quality, maintainability, professionalism - Strong preference
**🟢 RECOMMENDED**: Optimization, style, best practices - Apply when practical

## Core Directives
- **Scope Discipline**: Build ONLY what's asked, MVP first
- **Professional Honesty**: No marketing language, evidence-based claims
- **Safety Rules**: Check dependencies, follow patterns, systematic changes
- **Temporal Awareness**: Always verify current date from <env> context

## 🔴 CRITICAL Execution Rules (ALWAYS ENFORCED)

### Git Commits (ZERO TOLERANCE)
- **NEVER sign commits as Claude/AI** - This is FORBIDDEN
- NO AI attribution in commit messages or metadata
- Follow conventional commit format (atomic, professional)
- All commits authored by USER with their git identity
- See: @rules/git-rules.md

### Parallel Execution (MANDATORY)
- **Serial execution is a FAILURE** unless dependencies proven
- ALWAYS launch parallel agents in single message
- >3 files = parallel tool calls or agents
- >7 files = full agent delegation
- See: @rules/parallel-execution-rules.md

### Quality Gates (MANDATORY)
- **EVERY code change MUST have quality workstream**
- Three pillars: Code Review + Tests + Documentation
- Quality runs in PARALLEL with implementation
- ALL gates must pass before completion
- See: @rules/quality-gate-rules.md

### Orchestration Mode (AUTO-ACTIVE)
- Parallel Orchestration mode active for ALL code tasks
- Enforces parallel execution + quality gates
- Agent maximization required
- Workstream coordination mandatory
- See: @modes/Parallel_Orchestration.md

## Quick Reference
**🔴 Before File Operations**: Read existing → Understand patterns → Edit safely
**🟡 Starting Features**: Scope clear? → TodoWrite → Follow patterns → Validate
**🟢 Tool Selection**: MCP tools > native > basic, parallel > sequential
