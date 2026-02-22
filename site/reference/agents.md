---
layout: default
title: Agents
parent: Reference
nav_order: 2
---

# Agent Catalog

Cortex ships with 29 active agents organized by domain. Agents are specialized personas with specific expertise and capabilities.

## Architecture & Design

| Agent | Purpose |
|:------|:--------|
| `architect-review` | Architecture review and validation |
| `cloud-architect` | Cloud infrastructure design (AWS, Azure, GCP) |
| `component-architect` | Component design and architecture |
| `state-architect` | State management architecture |

## Code Quality

| Agent | Purpose |
|:------|:--------|
| `code-reviewer` | Code quality analysis |
| `debugger` | Issue diagnosis and resolution |
| `performance-monitor` | Performance monitoring and analysis |
| `frontend-optimizer` | Frontend performance optimization |

## Security

| Agent | Purpose |
|:------|:--------|
| `security-auditor` | Security assessment and vulnerability scanning |

## Database

| Agent | Purpose |
|:------|:--------|
| `database-admin` | Database administration and operations |
| `database-optimizer` | Database performance optimization |
| `postgres-expert` | PostgreSQL expertise |
| `sql-pro` | SQL expertise |

## Language Specialists

| Agent | Purpose |
|:------|:--------|
| `javascript-pro` | JavaScript expertise |
| `typescript-pro` | TypeScript expertise |
| `python-pro` | Python expertise |
| `rust-pro` | Rust expertise |

## Frontend

| Agent | Purpose |
|:------|:--------|
| `react-specialist` | React best practices |
| `tailwind-expert` | Tailwind CSS expertise |
| `ui-ux-designer` | UI/UX design and user experience |

## Testing

| Agent | Purpose |
|:------|:--------|
| `test-automator` | Test automation and generation |
| `vitest-expert` | Vitest testing framework |

## Infrastructure

| Agent | Purpose |
|:------|:--------|
| `kubernetes-architect` | Kubernetes orchestration |
| `websocket-engineer` | WebSocket implementation |
| `rest-expert` | REST API design |

## Coordination

| Agent | Purpose |
|:------|:--------|
| `orchestrator` | High-level planning and delegation |
| `context-manager` | Context and session management |
| `memory-keeper` | Memory vault curation |
| `docs-architect` | Documentation architecture |

## Activation

Agents activate through several mechanisms:

1. **Trigger-based** -- defined in `agents/triggers.yaml`
2. **AI recommendation** -- confidence-scored suggestions
3. **Manual** -- `cortex agent activate <name>`
4. **Dependency-driven** -- pulled in by `agents/dependencies.map`

## Dependency Graph

View agent dependencies:

```bash
cortex agent graph
cortex agent graph --export dependency-map.md
```

## Inactive Agents

Additional agents are available in `inactive/agents/`. Move them to `agents/` to activate:

```bash
# Via TUI
cortex tui  # Press 1 for Agents view

# Via file system
mv inactive/agents/<name>.md agents/
```
