---
layout: default
title: Commands
parent: Reference
nav_order: 1
---

# Command Reference

Cortex provides 49 slash commands across 13 categories. Commands are behavioral prompts that guide Claude through specific development tasks.

## Categories

### /analyze -- Code Analysis

| Command | Description |
|:--------|:------------|
| `/analyze:code` | Analyze code structure and quality |
| `/analyze:security` | Security vulnerability scanning |
| `/analyze:troubleshoot` | Systematic troubleshooting |

### /cleanup -- Maintenance

| Command | Description |
|:--------|:------------|
| `/cleanup:dead-code` | Find and remove dead code |
| `/cleanup:dependencies` | Audit and clean dependencies |

### /collaboration -- Team Workflows

| Command | Description |
|:--------|:------------|
| `/ctx:brainstorm` | Structured ideation with goals and options |
| `/ctx:plan` | Transform brainstorms into execution plans |
| `/ctx:execute-plan` | Drive plan execution with task tracking |

### /deploy -- Release

| Command | Description |
|:--------|:------------|
| `/deploy:prepare-release` | Pre-release checklist and validation |

### /design -- Architecture

| Command | Description |
|:--------|:------------|
| `/design:system` | System architecture design |
| `/design:workflow` | Workflow planning and visualization |

### /dev -- Development

| Command | Description |
|:--------|:------------|
| `/dev:implement` | Implement features with quality gates |
| `/dev:code-review` | Code quality and security review |
| `/dev:build` | Build and compilation tasks |
| `/dev:git` | Git workflow with semantic commits |
| `/dev:test` | Run and manage tests |

### /docs -- Documentation

| Command | Description |
|:--------|:------------|
| `/docs:generate` | Generate documentation for components |
| `/docs:index` | Build project documentation index |

### /orchestrate -- Multi-Agent

| Command | Description |
|:--------|:------------|
| `/orchestrate:task` | Delegate tasks to multiple agents |
| `/orchestrate:parallel` | Run parallel agent workstreams |

### /quality -- Code Quality

| Command | Description |
|:--------|:------------|
| `/quality:improve` | Systematic quality improvements |
| `/quality:cleanup` | Code cleanup and refactoring |

### /reasoning -- Reasoning Control

| Command | Description |
|:--------|:------------|
| `/reasoning:depth` | Adjust reasoning depth dynamically |

### /session -- Session Management

| Command | Description |
|:--------|:------------|
| `/session:load` | Load session context |
| `/session:save` | Save session state |
| `/session:reflect` | Reflect on session progress |

### /test -- Testing

| Command | Description |
|:--------|:------------|
| `/test:generate` | Generate tests for modules |
| `/test:coverage` | Analyze test coverage |

### /tools -- Tool Selection

| Command | Description |
|:--------|:------------|
| `/tools:select` | Optimal MCP tool routing |

## Usage Patterns

### Scope Flags

```
/analyze:code --scope module    # Analyze one module
/dev:implement --scope project  # Project-wide implementation
```

### Focus Flags

```
/dev:code-review --focus security
/quality:improve --focus performance
```

### Validation

```
/dev:implement --validate       # Enable validation gates
```
