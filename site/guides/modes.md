---
layout: default
title: Modes
parent: Guides
nav_order: 5
---

# Modes

Modes are behavioral presets that change how Claude Code approaches tasks. They toggle workflow defaults, reasoning depth, and output style.

## Available Modes

| Mode | Purpose |
|:-----|:--------|
| **Architect** | Strategic system design with trade-off analysis |
| **Brainstorming** | Collaborative discovery and divergent thinking |
| **Idea Lab** | Timeboxed ideation with ranked options |
| **Security Audit** | Security-first review mindset |
| **Teacher** | Educational explanations and mentoring |
| **Introspection** | Meta-cognitive analysis and reflection |
| **Amphetamine** | Maximum-velocity MVP prototyping |
| **Token Efficiency** | Concise, token-aware responses |
| **Super Saiyan** | Visual excellence with platform-specific variants |

## Activating Modes

### Via CLI

```bash
cortex mode activate Architect
cortex mode deactivate Architect
```

### Via Launcher

```bash
cortex start --modes "Architect,Deep_Analysis"
```

### Via TUI

Press `2` in the TUI to open the modes view, then toggle modes with Enter.

## Mode Details

### Architect

Best for multi-phase system design work. Focuses on:

- Trade-off analysis between approaches
- Component interaction modeling
- Scalability and maintainability concerns
- Technical decision documentation

### Brainstorming

Enables divergent thinking for ideation sessions:

- Captures goals and success signals
- Generates multiple solution options
- Evaluates constraints and trade-offs

### Security Audit

Shifts all analysis toward security:

- OWASP Top 10 awareness
- Threat modeling
- Input validation and sanitization
- Authentication and authorization review

### Token Efficiency

Minimizes token usage in responses:

- Compressed communication with symbols
- Abbreviated explanations
- Focused, concise output

### Super Saiyan

Visual excellence framework with three power levels:

- **Super Saiyan** -- enhanced UI components
- **Kamehameha** -- rich animations and styling
- **Over 9000** -- maximum visual polish

Platform-specific variants: Web, TUI, CLI, Docs.

## Combining Modes

Modes can be combined, though some may conflict. Cortex detects conflicts via mode metadata and warns you:

```bash
cortex start --modes "Architect,Token_Efficiency"
```

## State Tracking

Active modes are tracked in `~/.cortex/.active-modes`. This file persists across sessions.

```bash
cortex mode status    # Show currently active modes
```
