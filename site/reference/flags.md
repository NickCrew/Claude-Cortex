---
layout: default
title: Flags
parent: Reference
nav_order: 3
---

# Flag Reference

Flags are token-efficient context modules that control Claude's behavior. There are 22 flag categories totaling 3,380 tokens when fully loaded.

## All Flag Categories

| Category | Tokens | Purpose |
|:---------|:-------|:--------|
| Mode Activation | 120 | Core behavioral flags (`--brainstorm`, `--introspect`, `--orchestrate`) |
| MCP Servers | 160 | MCP server control (`--c7`, `--seq`, `--serena`, `--magic`) |
| Thinking Budget | 140 | Reasoning budget controls and cost-aware tuning |
| Analysis Depth | 130 | Thinking depth (`--think`, `--think-hard`, `--ultrathink`) |
| Execution Control | 150 | Delegation, concurrency, iteration (`--delegate`, `--loop`, `--validate`) |
| Visual Excellence | 250 | Super Saiyan, UI polish, design system |
| Output Optimization | 120 | Scope, focus, compression (`--uc`, `--scope`, `--focus`) |
| Testing & Quality | 170 | TDD, coverage, mutation testing |
| Learning & Education | 160 | Educational modes, explanations |
| Cost Management | 120 | Budget limits, cost awareness |
| Refactoring Safety | 140 | Safe refactoring, behavior preservation |
| Domain Presets | 150 | Frontend, backend, fullstack presets |
| Debugging & Trace | 110 | Verbose logging, execution tracing |
| Interactive Control | 130 | Confirmation, pair programming modes |
| CI/CD | 100 | Headless, JSON output, automation |
| Auto-Escalation | 180 | Automatic reasoning depth adjustment |
| Performance Optimization | 180 | Profiling, benchmarking, scaling guidance |
| Security Hardening | 190 | Security-first workflows, threat modeling |
| Documentation Generation | 170 | Doc-driven workflows, reference output |
| Git Workflow | 160 | PR hygiene, commits, release steps |
| Migration & Upgrade | 170 | Version upgrades, compatibility guarantees |
| Database Operations | 180 | Schema changes, data safety, migrations |

## Managing Flags

### TUI Flag Manager

```bash
cortex tui
# Press Ctrl+G for Flag Manager
# Use Up/Down to select, Space to toggle
```

### Profile Defaults

Each profile auto-enables relevant flag categories:

| Profile | Active Categories | Token Savings |
|:--------|:------------------|:--------------|
| minimal | 3 | 87% |
| frontend | 7 | 67% |
| backend | 7 | 71% |
| devops | 5 | 81% |
| documentation | 3 | 87% |
| quality | 7 | 71% |
| full | 22 | 0% |

### Per-Session Override

```bash
cortex start --flags "security-hardening,testing-quality"
```

## Common Flags

### Analysis Depth

| Flag | Effect |
|:-----|:-------|
| `--think` | Standard reasoning depth |
| `--think-hard` | Extended analysis for complex problems |
| `--ultrathink` | Maximum reasoning for architectural decisions |

### MCP Servers

| Flag | Server | Purpose |
|:-----|:-------|:--------|
| `--c7` | Context7 | Library documentation lookup |
| `--seq` | Sequential | Multi-step reasoning |
| `--serena` | Serena | Symbol operations and persistence |
| `--magic` | Magic | Code generation |
| `--play` | Playwright | Browser automation |

### Execution Control

| Flag | Effect |
|:-----|:-------|
| `--delegate` | Enable multi-agent delegation |
| `--loop` | Allow iterative refinement |
| `--validate` | Enable validation gates |
| `--safe-mode` | Extra safety checks for production |

## File Locations

- **Flag definitions:** `~/.cortex/flags/`
- **Active flags:** `~/.cortex/FLAGS.md`
- **Referenced by:** `~/.cortex/CLAUDE.md` (loads FLAGS.md)
