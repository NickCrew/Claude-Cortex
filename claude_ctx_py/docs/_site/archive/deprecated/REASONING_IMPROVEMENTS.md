# Reasoning System Improvements

## Overview

This document describes improvements to claude-ctx's reasoning system inspired by [just-every/code](https://github.com/just-every/code).

## New Features

### 1. Dynamic Reasoning Depth Control (`/reasoning:adjust`)

**Location**: `commands/reasoning/adjust.md`

Runtime adjustment of reasoning depth without restarting tasks.

**Usage**:
```bash
/reasoning:adjust [low|medium|high|ultra] [--scope current|remaining]
```

**Levels**:
- **low** (~2K tokens): Native tools only, direct solutions
- **medium** (~4K tokens): Sequential MCP, systematic exploration (≡ `--think`)
- **high** (~10K tokens): Sequential + Context7, deep analysis (≡ `--think-hard`)
- **ultra** (~32K tokens): All MCPs, maximum depth (≡ `--ultrathink`)

**Examples**:
```bash
# Escalate for complex subtask
/reasoning:adjust ultra --scope current

# Reduce for faster iteration
/reasoning:adjust medium --scope remaining
```

### 2. Summary Output Control

**Location**: `FLAGS.md:71-78`

User-controllable verbosity for ultrathink mode.

**Usage**:
```bash
--ultrathink --summary [brief|detailed|comprehensive]
```

**Options**:
- `brief`: Key findings only (~25% reduction)
- `detailed`: Full analysis with reasoning (default)
- `comprehensive`: Include rationale, alternatives, trade-offs (~50% increase)

### 3. Reasoning Profiles for Analysis

**Location**: `commands/analyze/code.md`

Domain-specific reasoning optimization for code analysis.

**Usage**:
```bash
/analyze:code [target] --reasoning-profile [default|security|performance]
```

**Profiles**:

**security**
- Deep threat modeling and attack vector analysis
- OWASP Top 10 pattern matching, CVE correlation
- Compliance validation (GDPR, SOC2, PCI-DSS)
- Enables: Context7 (security best practices) + Sequential (threat chains)

**performance**
- Algorithmic complexity analysis (Big-O)
- Resource profiling, bottleneck identification
- Database query optimization, N+1 detection
- Enables: Sequential (performance impact chains)

**default**
- Balanced analysis across all domains
- Standard severity assessment

**Examples**:
```bash
# Deep security analysis
/analyze:code src/auth --focus security --depth deep --reasoning-profile security

# Performance optimization
/analyze:code --focus performance --depth ultra --reasoning-profile performance
```

### 4. Auto-Enable Introspection

**Location**: `FLAGS.md:11-14`

Transparency markers automatically activated during maximum depth analysis.

**Behavior**:
- `--ultrathink` now auto-enables `--introspect`
- Exposes reasoning with markers: 🤔 thinking, 🎯 focus, ⚡ insight, 📊 data, 💡 decision
- Provides visibility into deep analysis process

## Implementation Status

✅ Command files created
✅ FLAGS.md updated
✅ docs/commands.md updated
✅ docs/index.md updated
✅ Examples updated
✅ Documentation validated

## Comparison with just-every/code

| Feature | just-every/code | claude-ctx |
|---------|----------------|------------|
| Runtime depth control | `/reasoning low\|medium\|high` | `/reasoning:adjust low\|medium\|high\|ultra --scope current\|remaining` |
| Summary control | `model_reasoning_summary = 'detailed'` | `--summary brief\|detailed\|comprehensive` |
| Reasoning profiles | Separate commands (`/plan`, `/solve`, `/code`) | Reasoning profiles for existing commands |
| Transparency | Not documented | Auto-enabled introspection markers |

## Benefits

1. **Flexibility**: Adjust depth mid-task without restarting
2. **Efficiency**: Reduce token usage with `--summary brief` or escalate only when needed
3. **Specialization**: Domain-specific optimization with reasoning profiles
4. **Transparency**: Introspection markers show reasoning process in ultrathink mode

## Migration Notes

Existing functionality is **fully backward compatible**:
- `--think`, `--think-hard`, `--ultrathink` flags work unchanged
- `/analyze:code` works with default profile if none specified
- All existing commands continue to function normally

New features are **purely additive** and opt-in.

## Future Enhancements

Potential additions not implemented (from original analysis):

- **Auto-escalation** (`--auto-escalate`): Automatically escalate depth based on confidence scores or failure patterns
- **Enhanced safe-mode**: Granular controls (read-only, approval, sandboxed)
- **Progressive depth escalation**: Automatic depth increases when blocked

These features were not implemented to maintain scope and focus on high-impact, low-effort improvements.
