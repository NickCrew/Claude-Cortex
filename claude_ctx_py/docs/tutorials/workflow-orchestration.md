---
layout: default
title: Workflow Orchestration
parent: Tutorials
nav_order: 4
permalink: /tutorials/workflow-orchestration/
---

# Workflow Orchestration Tutorial

Master multi-phase workflows and scenario orchestration in cortex for complex development tasks.

## What You'll Learn

By the end of this tutorial, you'll be able to:

- Define and run predefined workflows
- Create multi-phase scenarios with dependencies
- Configure parallel vs sequential phase execution
- Use conditions and success criteria
- Monitor and manage long-running orchestrations

**Time Estimate:** 20-25 minutes
**Prerequisites:** Completed [Getting Started with TUI](../getting-started-tui/)

---

## Part 1: Understanding Workflows vs Scenarios

### Workflows

**Workflows** are predefined task sequences stored in `~/.cortex/workflows/`. They guide Claude Code through a series of steps.

```bash
# List available workflows
cortex workflow list

# Run a workflow
cortex workflow run code-modernization

# Check status
cortex workflow status

# Resume if interrupted
cortex workflow resume
```

### Scenarios

**Scenarios** are more advanced orchestrations with phases, conditions, and agent coordination. They live in `~/.cortex/scenarios/`.

```bash
# List scenarios
cortex orchestrate list

# Validate scenario syntax
cortex orchestrate validate my-scenario

# Run a scenario
cortex orchestrate run my-scenario

# Preview without executing
cortex orchestrate preview my-scenario
```

### Key Differences

| Aspect | Workflow | Scenario |
|--------|----------|----------|
| **Structure** | Sequential steps | Multi-phase with conditions |
| **Parallelism** | Linear only | Supports parallel phases |
| **Agent Control** | Manual | Automatic activation/deactivation |
| **Conditions** | None | Before/after criteria |
| **Use Case** | Simple guided tasks | Complex orchestrations |

---

## Part 2: Creating Your First Workflow

### Workflow Structure

Create `~/.cortex/workflows/feature-development.yaml`:

```yaml
name: feature-development
description: Standard feature development workflow

steps:
  - name: Planning
    prompt: |
      Analyze the feature requirements and create a plan:
      1. Identify affected files
      2. List dependencies
      3. Define test strategy

  - name: Implementation
    prompt: |
      Implement the feature according to the plan:
      1. Create/modify necessary files
      2. Follow existing patterns
      3. Add error handling

  - name: Testing
    prompt: |
      Test the implementation:
      1. Write unit tests
      2. Run existing tests
      3. Fix any failures

  - name: Documentation
    prompt: |
      Update documentation:
      1. Add/update docstrings
      2. Update README if needed
      3. Add usage examples
```

### Running the Workflow

```bash
# Start the workflow
cortex workflow run feature-development

# Output:
# Started workflow: feature-development
#
# Workflow steps will be executed by Claude Code
# To check progress: cortex workflow status
# To resume if interrupted: cortex workflow resume
#
# Steps:
#   -> Planning
#   -> Implementation
#   -> Testing
#   -> Documentation
```

---

## Part 3: Advanced Scenarios

### Scenario Structure

Scenarios support phases with conditions, parallel execution, and agent coordination.

Create `~/.cortex/scenarios/full-stack-feature.yaml`:

```yaml
name: full-stack-feature
description: Complete full-stack feature implementation with testing
priority: high
type: development

phases:
  - name: analysis
    description: Analyze requirements and plan implementation
    condition: manual
    agents:
      - architect-reviewer
      - system-architect
    profiles:
      - development
    success_criteria:
      - Plan document created
      - Dependencies identified

  - name: backend
    description: Implement backend components
    condition: after:analysis
    parallel: false
    agents:
      - python-pro
      - database-admin
    success_criteria:
      - API endpoints functional
      - Database migrations applied

  - name: frontend
    description: Implement frontend components
    condition: after:analysis
    parallel: true  # Can run with backend
    agents:
      - react-specialist
      - ui-ux-designer
    success_criteria:
      - Components render correctly
      - State management working

  - name: integration
    description: Integration testing and deployment prep
    condition: after:backend,frontend
    agents:
      - quality-engineer
      - test-automator
    success_criteria:
      - All integration tests pass
      - Performance benchmarks met
```

### Phase Conditions

| Condition | Meaning |
|-----------|---------|
| `manual` | Requires explicit start |
| `auto` | Starts automatically when scenario runs |
| `after:phase` | Starts after named phase completes |
| `after:phase1,phase2` | Starts after all listed phases complete |

### Parallel Execution

When `parallel: true`, phases with the same condition can run simultaneously:

```
┌─────────────────────────────────────────────────────────┐
│  Phase: analysis (manual start)                          │
└────────────────────────┬────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
┌───────────────────┐     ┌───────────────────┐
│  Phase: backend   │     │  Phase: frontend  │
│  (parallel: true) │     │  (parallel: true) │
└─────────┬─────────┘     └─────────┬─────────┘
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
          ┌───────────────────────┐
          │   Phase: integration  │
          │   (after both)        │
          └───────────────────────┘
```

---

## Part 4: Running and Monitoring Scenarios

### Preview Before Running

Always preview complex scenarios first:

```bash
cortex orchestrate preview full-stack-feature

# Output:
# Scenario: full-stack-feature
# Type: development
# Priority: high
#
# Phases:
#   1. analysis [manual]
#      Agents: architect-reviewer, system-architect
#
#   2. backend [after:analysis]
#      Agents: python-pro, database-admin
#
#   3. frontend [after:analysis] [PARALLEL]
#      Agents: react-specialist, ui-ux-designer
#
#   4. integration [after:backend,frontend]
#      Agents: quality-engineer, test-automator
#
# Estimated phases: 4
# Parallel opportunities: 1 (backend + frontend)
```

### Running a Scenario

```bash
# Start the scenario
cortex orchestrate run full-stack-feature

# Check status
cortex orchestrate status

# Output:
# Scenario: full-stack-feature
# Status: running
#
# Phase Status:
#   [x] analysis     - completed (15m ago)
#   [>] backend      - in_progress (5m)
#   [>] frontend     - in_progress (3m)
#   [ ] integration  - pending
#
# Active Agents:
#   - python-pro (backend)
#   - react-specialist (frontend)
```

### Stopping a Scenario

```bash
# Stop gracefully
cortex orchestrate stop full-stack-feature

# Agents are deactivated
# Progress is saved
# Can be resumed later
```

---

## Part 5: Validation and Schema

### Validating Scenarios

```bash
# Validate a specific scenario
cortex orchestrate validate full-stack-feature

# Validate all scenarios
cortex orchestrate validate --all

# Output (on success):
# [OK] full-stack-feature.yaml - Valid
#   - 4 phases defined
#   - 6 unique agents referenced
#   - No circular dependencies
#
# Output (on error):
# [ERROR] broken-scenario.yaml
#   - Missing required field: description
#   - Unknown condition: after:nonexistent
#   - Agent not found: fake-agent
```

### Schema Definition

Create `~/.cortex/scenarios/schema.yaml` to enforce standards:

```yaml
required:
  - name
  - description
  - phases

fields:
  type:
    enum:
      - development
      - deployment
      - maintenance
      - migration

  priority:
    enum:
      - low
      - medium
      - high
      - critical

  condition:
    enum:
      - manual
      - auto
      # Patterns like "after:X" are validated separately
```

---

## Part 6: Real-World Patterns

### Pattern 1: Microservice Migration

```yaml
name: microservice-migration
description: Extract a service from monolith
priority: high
type: migration

phases:
  - name: identify
    description: Identify service boundaries
    condition: manual
    agents:
      - system-architect
    success_criteria:
      - Service boundary diagram created
      - Dependencies mapped

  - name: interface
    description: Define API contracts
    condition: after:identify
    agents:
      - api-documenter
    success_criteria:
      - OpenAPI spec created
      - Breaking changes documented

  - name: extract
    description: Extract and implement service
    condition: after:interface
    agents:
      - python-pro
      - database-optimizer
    success_criteria:
      - Service runs independently
      - Data migration complete

  - name: integrate
    description: Connect to existing system
    condition: after:extract
    agents:
      - quality-engineer
    success_criteria:
      - All endpoints working
      - Latency within SLA
```

### Pattern 2: Release Preparation

```yaml
name: release-prep
description: Prepare for production release
priority: critical
type: deployment

phases:
  - name: changelog
    description: Generate changelog and bump version
    condition: auto
    agents:
      - technical-writer
    success_criteria:
      - CHANGELOG.md updated
      - Version bumped correctly

  - name: test-suite
    description: Run comprehensive tests
    condition: auto
    parallel: true
    agents:
      - test-automator
      - security-auditor
    success_criteria:
      - All tests pass
      - No security vulnerabilities

  - name: docs
    description: Update documentation
    condition: auto
    parallel: true
    agents:
      - api-documenter
    success_criteria:
      - API docs current
      - Migration guide ready

  - name: approval
    description: Final review gate
    condition: after:test-suite,docs,changelog
    agents:
      - code-reviewer
    success_criteria:
      - Code review approved
      - Release notes reviewed
```

### Pattern 3: Incident Response

```yaml
name: incident-response
description: Systematic incident investigation
priority: critical
type: maintenance

phases:
  - name: triage
    description: Initial assessment and stabilization
    condition: auto
    agents:
      - performance-engineer
    success_criteria:
      - Issue categorized
      - Impact assessed

  - name: investigate
    description: Root cause analysis
    condition: after:triage
    agents:
      - python-pro
      - database-optimizer
    success_criteria:
      - Root cause identified
      - Reproduction steps documented

  - name: fix
    description: Implement and verify fix
    condition: after:investigate
    agents:
      - test-automator
    success_criteria:
      - Fix deployed
      - Issue resolved

  - name: postmortem
    description: Document lessons learned
    condition: after:fix
    agents:
      - technical-writer
    success_criteria:
      - Postmortem document complete
      - Prevention measures identified
```

---

## Part 7: TUI Integration

### Scenario Panel

Access scenarios from the TUI:

1. Press `Ctrl+P` for command palette
2. Type "scenario" or "orchestrate"
3. Select from:
   - **Scenario List** - View all scenarios
   - **Scenario Run** - Start a scenario
   - **Scenario Status** - Monitor progress

### Visual Progress

The TUI shows scenario progress with:
- Phase completion indicators
- Active agent badges
- Time tracking
- Success criteria checklist

---

## Troubleshooting

### Common Issues

**Scenario won't start:**
```bash
# Check validation
cortex orchestrate validate my-scenario

# Common fixes:
# - Check YAML syntax
# - Verify all agents exist
# - Ensure no circular dependencies
```

**Phase stuck on condition:**
```bash
# Check which phases are blocking
cortex orchestrate status

# Manually mark phase complete if needed
# (by updating ~/.cortex/scenarios/.state/)
```

**Agent not activating:**
```bash
# Check agent exists
cortex agent status <agent-name>

# Ensure agent is in active state
cortex agent activate <agent-name>
```

---

## Summary

You've learned how to:

- Create and run predefined workflows
- Build multi-phase scenarios with conditions
- Configure parallel execution for efficiency
- Validate scenario definitions
- Monitor orchestration progress

**Next Steps:**
- [CI/CD Integration](../ci-cd-integration/) - Automate workflows in pipelines
- [Custom Skills](../custom-skills/) - Extend scenario capabilities
- [AI Watch Mode](../ai-watch-mode/) - Intelligent agent recommendations

---

## Quick Reference

```bash
# Workflows
cortex workflow list              # List workflows
cortex workflow run <name>        # Run workflow
cortex workflow status            # Check progress
cortex workflow resume            # Resume interrupted

# Scenarios
cortex orchestrate list           # List scenarios
cortex orchestrate validate <name> # Validate syntax
cortex orchestrate preview <name>  # Preview phases
cortex orchestrate run <name>      # Run scenario
cortex orchestrate status          # Check progress
cortex orchestrate stop <name>     # Stop scenario
```
