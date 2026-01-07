# Architecture Terminology Guide

**Purpose**: Clarify the relationship between cortex system concepts and Claude Code's execution mechanisms.

## The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Cortex System (Your Framework)                │
├─────────────────────────────────────────────────────────────┤
│ - Modes: Behavioral states (Token_Efficiency, etc.)        │
│ - Rules: Mandatory behaviors (quality-gate-rules.md)       │
│ - Slash Commands: User workflows (/dev:implement)          │
│ - Personas: Conceptual roles (architect, frontend, etc.)   │
│ - MCP Servers: External integrations (Context7, etc.)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: Work Concepts (What Needs Doing)                  │
├─────────────────────────────────────────────────────────────┤
│ - Tasks: Work items tracked in TodoWrite                   │
│ - Features: User-facing functionality to build             │
│ - Bugs: Issues to fix                                      │
│ - Refactorings: Code improvements needed                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: Claude Code Execution (How Work Gets Done)        │
├─────────────────────────────────────────────────────────────┤
│ - Task Tool: Claude Code's delegation mechanism            │
│ - Subagents: Workers launched via Task tool                │
│ - Direct Tools: Read, Write, Edit, Grep, Bash, etc.        │
└─────────────────────────────────────────────────────────────┘
```

## Mental Model: Flags vs Commands vs Skills

Use this as the default mental model when deciding what to reach for:

- **Commands** are explicit workflows. They set personas, may delegate to subagents, and often
  instruct which skills to load. Use them when you want a guided, repeatable process.
- **Skills** are on-demand knowledge modules. They are loaded when a command calls them,
  when keywords match, or when you explicitly invoke `/ctx:skill <name>`. Use them for
  depth in a specific domain without committing to a whole workflow.
- **Flags** are background behavior toggles. They are enabled via `FLAGS.md`, profiles, or
  the TUI, and shape how Claude behaves across all interactions.

### Activation Sources (current)

1. **Explicit command** (e.g., `/dev:implement`) → loads referenced skills
2. **Explicit skill invocation** (e.g., `/ctx:skill api-design-patterns`)
3. **Auto-suggestion / auto-activation**
   - `skills/activation.yaml` maps keywords → skills
   - `skills/skill-rules.json` maps keywords → command suggestions (hooks/recommender)
4. **Flags** apply continuously as defaults

### Naming Note

The CLI binary is `cortex`. `cortex` remains as a deprecated alias.

## Key Terms

### Cortex System Terms

**Mode**

- What: Behavioral state that modifies Claude's approach
- Example: `Token_Efficiency` optimizes for concise output
- Location: `~/.cortex/modes/` or project `.claude/modes/`
- Activation: `cortex mode activate [name]`

**Rule**

- What: Mandatory behavior Claude must follow
- Example: `quality-gate-rules.md` requires review + tests + docs
- Location: `~/.cortex/rules/` or project `.claude/rules/`
- Activation: active when the file is in `rules/`; move to `inactive/rules/` (or use `cortex rules deactivate`) to disable

**Slash Command**

- What: User-triggered workflow that expands to prompt
- Example: `/dev:implement` → Full implementation workflow prompt
- Location: `~/.cortex/commands/` or project `.claude/commands/`
- Usage: Type in Claude Code chat

**Persona** (Conceptual Role)

- What: Domain expertise lens that guides Claude's approach
- Example: `frontend` → Think about UI/UX, accessibility, user experience
- NOT: A Claude Code subagent type (common confusion!)
- Purpose: Influences behavior and decision-making
- Listed in: Slash command frontmatter as guidance

**MCP Server**

- What: External tool/service integration
- Example: `context7` for library docs, `sequential` for structured reasoning
- Connection: Provides additional capabilities beyond native tools
- Usage: Automatically used when appropriate

### Work Concept Terms

**Task** (Work Item)

- What: Unit of work that needs doing
- Example: "Fix memory leak in auth service"
- Tracked: TodoWrite tool, project management systems
- Confusion: Different from "Task tool" (see below)

**Feature**

- What: New functionality to implement
- Scope: Often multiple tasks
- Example: "User authentication system"

### Claude Code Execution Terms

**Task Tool** (Delegation Mechanism)

- What: Claude Code's built-in tool to launch subagents
- Purpose: Delegate complex work to specialized workers
- Usage: `<invoke name="Task"><subagent_type>...</invoke>`
- When: >3 files, complex work, multi-step operations
- Result: Launches a subagent that works independently

**Subagent** (Worker)

- What: Specialized agent launched via Task tool
- Types: `general-purpose`, `code-reviewer`, `test-automator`, `Explore`, etc.
- Characteristics: Works independently, returns results, visible to user
- Confusion: In cortex, we historically called these "agents" (imprecise!)

**Direct Tool**

- What: Claude Code's native tools (Read, Write, Edit, Grep, Glob, Bash)
- When: Simple operations, 1-2 files, quick reads
- Characteristics: Synchronous, immediate results

## Common Confusions

### ❌ "Agent" is Ambiguous

**OLD usage** (imprecise):

```markdown
agents: [code-reviewer, test-automator]  # What are these exactly?
```

**BETTER** (precise):

```markdown
subagents: [code-reviewer, test-automator]  # Claude Code subagents via Task tool
personas: [frontend, backend]              # Conceptual guidance roles
```

### ✅ "Delegation" Means Task Tool

**VAGUE**:
> "Multi-agent coordination and delegation"

**CLEAR**:
> "Launch multiple subagents via Task tool in parallel for concurrent work"

### ✅ Personas ≠ Subagents

**Personas** (your system):

- `architect` - Think about system design
- `frontend` - Focus on UI/UX
- `backend` - Focus on APIs/data
- `security` - Security-first mindset

These guide **how Claude thinks**, not execution mechanism.

**Subagents** (Claude Code):

- `general-purpose` - Versatile coding agent
- `code-reviewer` - Quality analysis agent
- `test-automator` - Test generation agent
- `Explore` - Codebase exploration agent

These are **actual workers** launched via Task tool.

### ✅ When Commands Say "Activate Personas"

**What this means**:

```
Command lists: personas: [architect, frontend, security]
            ↓
Claude adopts those thinking modes/perspectives
            ↓
When delegation needed:
            ↓
Launch Task tool with appropriate subagent_type
            ↓
Subagent works with that persona's guidance in mind
```

## Decision Flow for Execution

```
┌─────────────────────────────────────┐
│ Slash Command Triggered             │
│ (e.g., /dev:implement auth API)     │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Activate Personas from Command      │
│ (backend, security thinking modes)  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│ Check Complexity & Rules            │
│ - File count? >3 files?             │
│ - Steps? >5 steps?                  │
│ - Domain split? Code+Tests+Docs?    │
└──────────────┬──────────────────────┘
               ↓
       ┌───────┴────────┐
       ↓                ↓
┌─────────────┐   ┌─────────────┐
│ Simple Work │   │ Complex Work│
│ Direct Tools│   │ Task Tool   │
└─────────────┘   └──────┬──────┘
                         ↓
                ┌────────────────────┐
                │ Launch Subagents   │
                │ - Implementation   │
                │ - Code Review      │
                │ - Test Generation  │
                └────────────────────┘
```

## Practical Examples

### Example 1: Simple Task (Direct Tools)

```
User: Fix typo in README
  ↓
No personas needed (trivial)
  ↓
Simple work: 1 file
  ↓
Direct tools: Read → Edit → Done
```

### Example 2: Feature with Personas (Task Tool)

```
User: /dev:implement user profile API
  ↓
Activate personas: backend, security
  ↓
Complex: API + tests + docs (>3 domains)
  ↓
Launch Task tool with 3 subagents in parallel:
  - general-purpose (implementation, thinking: backend)
  - test-automator (tests, thinking: security)
  - api-documenter (docs, thinking: backend)
```

### Example 3: Orchestration (Multiple Subagents)

```
User: /orchestrate:task "enterprise auth system"
  ↓
Activate personas: architect, backend, frontend, security
  ↓
Complex multi-domain work
  ↓
Launch multiple Task tool subagents:
  - Explore (discover existing patterns)
  - general-purpose (backend implementation)
  - general-purpose (frontend implementation)
  - code-reviewer (security review)
  - test-automator (comprehensive tests)
  ↓
All think through persona lenses
```

## Command Template Guidance

When writing slash commands, use this structure:

```markdown
---
name: command-name
personas: [conceptual, roles, here]     # Thinking modes
subagents: [specific, claude, types]    # Task tool subagents
---

## Personas (Thinking Modes)
These guide Claude's perspective and decision-making:
- **architect**: System design, scalability, architecture patterns
- **frontend**: UI/UX, accessibility, user experience

## Delegation Protocol
**When to delegate** (use Task tool):
- >3 files or >5 steps
- Multi-domain work (code + tests + docs)
- User needs progress visibility

**Subagents to launch**:
- `general-purpose`: Implementation work
- `code-reviewer`: Quality/security analysis
- `test-automator`: Test generation

**How to launch**:
Single message with multiple Task tool calls for parallel execution.
```

## Summary

**Your system provides**:

- 🎭 Personas → How to think
- 📋 Modes → Behavior patterns
- 📏 Rules → What must happen
- 🔧 Slash Commands → Workflow triggers
- 🔌 MCP Servers → External capabilities

**Claude Code provides**:

- 🛠️ Task Tool → Delegation mechanism
- 👷 Subagents → Workers for complex tasks
- 📝 Direct Tools → Simple operations

**Together**:
Your workflows trigger → Personas guide thinking → Complexity determines → Task tool delegates when needed → Subagents execute with persona guidance
