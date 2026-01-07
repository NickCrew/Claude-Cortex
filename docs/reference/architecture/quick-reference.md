# Cortex Quick Reference

**One-page guide to the three-layer automation system**

---

## The Three Layers

```
┌──────────────────────────────────────────────────────────┐
│  🎯 Layer 1: USER COMMANDS (What to do)                  │
│  43 slash commands across 16 namespaces                  │
│  Examples: /refactor:analyze, /workflow:run, /mode:activate │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  🎨 Layer 2: BEHAVIORAL MODES (How to do it)             │
│  8 modes that change Claude's operation style            │
│  Examples: Brainstorm, Deep_Analysis, Quality_Focus     │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│  🔄 Layer 3: WORKFLOWS (Step-by-step execution)          │
│  9 multi-step processes with agent coordination         │
│  Examples: feature-development, refactoring, api-design │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Lookup

### 🎯 Common Commands

| Command | Purpose | Time |
|---------|---------|------|
| `/refactor:analyze src/` | Find refactoring opportunities | 2-3 min |
| `/refactor:execute plan.md` | Execute refactoring safely | 10-30 min |
| `/workflow:run feature-development` | Build new feature end-to-end | 30-60 min |
| `/workflow:run api-design` | Design and implement API | 45-90 min |
| `/mode:activate Deep_Analysis` | Enable maximum reasoning | Instant |
| `/dev:code-review src/` | Review code quality | 3-5 min |
| `/test:generate-tests src/` | Generate test suite | 5-10 min |
| `/docs:generate src/` | Generate documentation | 5-10 min |

### 🎨 Behavioral Modes

| Mode | When to Use | Key Features |
|------|-------------|--------------|
| **Brainstorm** | Unclear requirements | Socratic questions, options, collaboration |
| **Deep_Analysis** | Complex problems | Max reasoning (~32K tokens), hypothesis testing |
| **Quality_Focus** | Production code | 8/10 review, 90% coverage, strict standards |
| **Token_Efficient** | Large operations | 30-50% reduction, symbol communication |
| **Parallel_Orchestration** | Multi-file work | Parallel agents, quality gates |
| **Super_Saiyan** | UI/UX work | Visual excellence, animations, polish |
| **Task_Management** | Complex tasks | Hierarchical tracking, progress monitoring |

### 🔄 Workflows

| Workflow | Use Case | Duration | Key Modes |
|----------|----------|----------|-----------|
| **feature-development** | New features | 30-60 min | Task_Management, Parallel_Orchestration |
| **bug-fix** | Fix bugs | 15-30 min | Deep_Analysis |
| **refactoring** | Clean code | 20-45 min | Deep_Analysis, Quality_Focus |
| **api-design** | Design APIs | 45-90 min | Brainstorm, Parallel_Orchestration |
| **technical-debt** | Quarterly cleanup | 2-4 hours | Deep_Analysis, Quality_Focus |
| **architecture-review** | Quarterly review | 3-5 hours | Deep_Analysis |
| **onboarding** | New developer | 4 weeks | Brainstorm, Task_Management |
| **security-audit** | Monthly security | 1-2 hours | Deep_Analysis |
| **performance-optimize** | Speed issues | 30-60 min | Deep_Analysis |

---

## Decision Guide

### "Which command should I use?"

```
Need to DO something specific?
└─ Use a COMMAND
   Examples: /refactor:analyze, /test:generate-tests

Need Claude to THINK differently?
└─ Use a MODE
   Examples: /mode:activate Deep_Analysis

Need to EXECUTE a process?
└─ Use a WORKFLOW
   Examples: /workflow:run feature-development
```

### "How do they work together?"

```
Command → Activates Mode(s) → Triggers Workflow → Coordinates Agents
```

**Example Flow**:

```
User: /refactor:analyze src/auth
  ↓
Activates: Deep_Analysis + Quality_Focus modes
  ↓
Triggers: Refactoring workflow (steps 1-3)
  ↓
Uses: code-reviewer agent + Codanna MCP
  ↓
Produces: Refactoring plan with priorities
```

---

## Integration Patterns

### Pattern 1: Quick Action

```bash
/refactor:analyze src/auth
# Fast, focused analysis
```

### Pattern 2: Workflow with Modes

```bash
/workflow:run feature-development
# Auto-activates: Task_Management, Parallel_Orchestration
# Executes: 9-step process with multiple agents
```

### Pattern 3: Manual Mode Control

```bash
/mode:activate Brainstorm
# Then discuss requirements
# Mode influences all subsequent interactions
```

### Pattern 4: Chained Commands

```bash
/refactor:analyze src/
# Review the plan
/refactor:execute refactor-plan.md
# Executes with Parallel_Orchestration + Quality_Focus
```

---

## Command Namespaces

| Namespace | Purpose | Commands |
|-----------|---------|----------|
| `/refactor:*` | Code refactoring | analyze, execute |
| `/workflow:*` | Workflow execution | run, status, resume |
| `/mode:*` | Mode management | activate, deactivate, list |
| `/dev:*` | Development | code-review, git, build, implement |
| `/test:*` | Testing | generate-tests |
| `/deploy:*` | Deployment | prepare-release |
| `/analyze:*` | Analysis | code, explain, security-scan, troubleshoot |
| `/docs:*` | Documentation | generate, index |
| `/quality:*` | Quality | cleanup, improve |
| `/design:*` | Design | system, workflow |
| `/collaboration:*` | Collaboration | brainstorm, plan, execute-plan |
| `/orchestrate:*` | Orchestration | task, spawn, brainstorm |
| `/session:*` | Session mgmt | save, load, reflect |
| `/reasoning:*` | Analysis control | budget, adjust, metrics |
| `/cleanup:*` | Cleanup | test, code, deps, docs |
| `/tools:*` | Tool selection | select |

---

## Keyboard Shortcuts (in TUI)

```
1  →  Overview
2  →  Agents
3  →  Modes       ← View your 8 modes
4  →  Rules
5  →  Skills
6  →  Workflows   ← View your 9 workflows
7  →  MCP
8  →  Profiles
9  →  Export
0  →  AI Assistant

S  →  Scenarios
o  →  Orchestrate
Alt+g  →  Galaxy
t  →  Tasks
r  →  Refresh
```

---

## Typical Workflows

### Starting a New Feature

```
1. /collaboration:brainstorm [feature idea]
   ↓ Clarify requirements
2. /workflow:run feature-development
   ↓ Full development cycle
3. /dev:code-review src/
   ↓ Final quality check
```

### Refactoring Code

```
1. /refactor:analyze src/module
   ↓ Get refactoring plan
2. Review priorities
3. /refactor:execute refactor-plan.md
   ↓ Safe incremental execution
4. /test:generate-tests src/module
   ↓ Ensure coverage
```

### Designing an API

```
1. /workflow:run api-design --input api-params.yaml
   ↓ Full API design process
   ↓ Produces: OpenAPI spec, mock server, implementation
2. /test:generate-tests api/
3. /docs:generate api/
```

### Monthly Maintenance

```
1. /workflow:run security-audit
   ↓ Security check
2. /workflow:run performance-optimize
   ↓ Performance tuning
3. /quality:improve src/
   ↓ Code quality
```

### Quarterly Cleanup

```
1. /workflow:run technical-debt
   ↓ 13-step debt reduction
2. /workflow:run architecture-review
   ↓ 15-step architecture assessment
```

---

## Quality Gates

All workflows enforce quality standards:

- ✅ **Code Review**: Score ≥ 7/10 (8/10 in Quality_Focus mode)
- ✅ **Test Coverage**: ≥ 85% (90% in Quality_Focus mode)
- ✅ **Security Scan**: No critical/high vulnerabilities
- ✅ **Performance**: No regression > 10%
- ✅ **Documentation**: Complete for public APIs

---

## Tips & Best Practices

### 💡 Efficiency Tips

- Use `/workflow:run` for multi-step processes
- Activate modes at session start for persistent behavior
- Use `--dry-run` to preview workflows
- Check `/workflow:status` to monitor progress

### 🎯 Quality Tips

- Always use Quality_Focus mode for production code
- Let workflows handle quality gates automatically
- Review refactoring plans before executing
- Run security audits monthly

### 🚀 Speed Tips

- Use Parallel_Orchestration for independent tasks
- Leverage `--parallel` flag in workflows
- Batch similar commands together
- Use Token_Efficient mode for large codebases

### 🛡️ Safety Tips

- Workflows auto-checkpoint for resume capability
- Refactoring uses incremental execution with rollback
- Quality gates block on failures
- All changes are validated before merging

---

## Getting Help

```bash
# In TUI
?  →  Help

# View detailed diagrams
cat ~/.cortex/docs/architecture-diagrams.md

# List all commands
ls ~/.cortex/commands/*.md

# List all modes
ls ~/.cortex/modes/

# List all workflows
ls ~/.cortex/workflows/
```

---

## System Stats

- **43** Slash Commands
- **16** Command Namespaces
- **8** Behavioral Modes
- **9** Multi-step Workflows
- **25+** Specialized Agents
- **3** MCP Servers (Codanna, Context7, Sequential)

**Coverage**: Feature development, bug fixing, refactoring, API design, security, performance, testing, documentation, onboarding, architecture, technical debt

---

*Last Updated: 2025-11-11*
