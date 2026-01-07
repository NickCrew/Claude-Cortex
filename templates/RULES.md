# Claude Code Behavioral Rules

## Rule Priority System

**🔴 CRITICAL**: Security, data safety, production breaks - Never compromise  
**🟡 IMPORTANT**: Quality, maintainability, professionalism - Strong preference  
**🟢 RECOMMENDED**: Optimization, style, best practices - Apply when practical

## Core Directives

- **Scope Discipline**: Build only what's asked, MVP first
- **Professional Honesty**: No marketing language, evidence-based claims
- **Safety Rules**: Follow existing patterns and review dependencies
- **Temporal Awareness**: Use <env> context for dates and time

## 🔴 Critical Rule Modules (Always Enforced)

### Git Commits (Zero Tolerance)
- No AI attribution in commit messages or metadata
- Use conventional commit format and keep commits atomic
- See: @rules/git-rules.md

### Parallel Execution
- Parallelize independent workstreams; avoid unnecessary serial execution
- Use Task agents or parallel tool calls for multi-file work
- See: @rules/parallel-execution-rules.md

### Quality Gates
- Run review, tests, and docs in parallel with implementation
- Complete only after gates are satisfied
- See: @rules/quality-gate-rules.md

## Quick Reference

**🔴 Before File Operations**: Read existing -> Understand patterns -> Edit safely  
**🟡 Starting Features**: Scope clear? -> TodoWrite -> Follow patterns -> Validate  
**🟢 Tool Selection**: MCP tools > native > basic, parallel > sequential
