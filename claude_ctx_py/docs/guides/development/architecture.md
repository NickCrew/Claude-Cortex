---
layout: default
title: Architecture
nav_order: 3
---

# cortex Architecture & Design

Comprehensive architecture documentation for the cortex context management framework.

## Overview

cortex is a sophisticated context orchestration framework for Claude Code that provides:

- **On-Demand Loading**: Agents, modes, and skills load only when needed
- **Dependency Management**: Automatic resolution of agent dependencies
- **Progressive Disclosure**: Skills load knowledge in tiers (metadata → instructions → resources)
- **Hybrid Orchestration**: Strategic Haiku/Sonnet model assignment for cost/performance
- **Workflow Automation**: Multi-phase structured workflows with metrics
- **Project Intelligence**: Auto-detection and context-aware initialization

## Core Philosophy

### 1. Context Efficiency
Load only what's needed, when it's needed. Reduce token usage through progressive disclosure and intelligent activation.

### 2. Dependency-Driven Activation
Agents declare their dependencies (`requires` and `recommends`), enabling automatic resolution and validation.

### 3. Structured Workflows
Every agent follows multi-phase workflows (discovery → implementation → validation) with measurable outcomes.

### 4. Observable Execution
Track metrics per agent (latency, coverage, success rates) for continuous optimization.

### 5. Project-Aware Intelligence
Auto-detect project type, language, and framework to activate relevant agents and modes.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Interface                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   cortex CLI                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Agent Mgmt  │  │  Skill Mgmt  │  │  Init System │      │
│  │              │  │              │  │              │      │
│  │ activate     │  │ list         │  │ detect       │      │
│  │ deactivate   │  │ info         │  │ wizard       │      │
│  │ deps         │  │ validate     │  │ profile      │      │
│  │ graph        │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Context Resolution Engine                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Dependency Graph     →  Activation Logic          │    │
│  │  Trigger Matching     →  Skill Loading             │    │
│  │  Model Selection      →  Workflow Orchestration    │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Context Storage                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  agents/ │  │  skills/ │  │  modes/  │  │ profiles/│   │
│  │          │  │          │  │          │  │          │   │
│  │ 11 active│  │ 2 skills │  │ 3 modes  │  │ 3 saved  │   │
│  │ 67 inact │  │          │  │ 4 inact  │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Agent System

**Structure:**
```
agents/
├── agent-name.md              # Active agent (loaded when triggered)
└── dependencies.map           # Dependency graph export

inactive/
└── agents/
    └── agent-name.md          # Inactive (can be activated via CLI)
```

**Agent Frontmatter (v2.0):**
```yaml
---
version: 2.0
name: backend-architect
alias: [server-architect]
summary: One-line description
description: |
  Detailed multi-line description
category: core-development
tags: [backend, architecture, reliability]
tier:
  id: core
  activation_strategy: tiered
  conditions:
    - "**/api/**"
    - "**/services/**"
model:
  preference: sonnet                    # or haiku
  fallbacks: [haiku]
  reasoning: "Complex architectural analysis"
  escalation:                           # optional
    to: sonnet
    when: ["architectural refactoring"]
tools:
  catalog: [Read, Write, MultiEdit, Exec]
  tiers:
    core: [Read, Write]
    enhanced: [Exec]
    specialist: [MultiEdit]
activation:
  keywords: ["backend architecture", "api design"]
  auto: true
  priority: high
dependencies:
  requires: []                          # Must be active
  recommends: [database-optimizer]      # Nice to have
skills:                                 # NEW: Agent skills
  - api-design-patterns
  - microservices-patterns
workflows:
  default: backend-architecture
  phases:
    - name: discovery
      responsibilities:
        - Analyze requirements
    - name: design
      responsibilities:
        - Produce service contracts
metrics:
  tracked:
    - latency_budget_ms
    - availability_slo
---
```

**Dependency Graph:**
```
cloud-architect
├── recommends: terraform-specialist
├── recommends: kubernetes-architect
└── workflow: assessment → architecture → enablement

backend-architect
├── recommends: database-optimizer
├── recommends: security-auditor
├── recommends: performance-engineer
├── skills: api-design-patterns, microservices-patterns
└── workflow: discovery → design → evolution

deployment-engineer
├── requires: cloud-architect
├── recommends: kubernetes-architect
├── recommends: terraform-specialist
└── workflow: assessment → implementation → verification
```

---

### Skill System

**Purpose**: Progressive disclosure of specialized knowledge to reduce token usage.

**Structure:**
```
skills/
├── api-design-patterns/
│   └── SKILL.md                # ~1,800 tokens
├── microservices-patterns/
│   └── SKILL.md                # ~3,200 tokens
└── README.md
```

**Skill Frontmatter:**
```yaml
---
name: api-design-patterns
description: REST/GraphQL patterns with versioning, pagination, error handling. Use when designing APIs, defining endpoints, or architecting service contracts.
---

# Skill Content (Progressive Tiers)

## When to Use This Skill
[Activation criteria]

## Core Patterns
[Essential knowledge - 40% of content]

## Advanced Patterns
[Detailed examples - 40% of content]

## Resources
[References and links - 20% of content]
```

**Loading Strategy:**
```
1. Agent activated → Load agent core content (~3K tokens)
2. Skill triggered → Load skill metadata (~50 tokens)
3. Skill needed → Load skill instructions (~1.8K tokens)
4. Resources requested → Load additional examples (~500 tokens)

Total: 3K + 50 + 1.8K = 4.85K (vs. 8K without skills)
Savings: 39%
```

---

### Mode System

**Purpose**: Toggle workflow defaults and behavioral presets.

**Structure:**
```
modes/
├── Task_Management.md         # Active mode
├── Project_Memory.md
└── Agile_Sprint.md

inactive/
└── modes/
    ├── Deep_Analysis.md
    ├── Rapid_Prototyping.md
    └── Documentation_Focus.md
```

**Mode Content:**
```markdown
# Mode: Task Management

## Activation
- Multi-step operations (>3 steps)
- Complex scope (>2 directories OR >3 files)

## Behavior Modifications
1. ALWAYS use TodoWrite for task tracking
2. Mark tasks in_progress before starting
3. Mark completed immediately after finishing
4. One task in_progress at a time

## Tool Preferences
- Prefer Task agents for delegation
- Use parallel operations when independent
```

---

### Profile System

**Purpose**: Save and restore agent/mode/rule configurations.

**Structure:**
```
profiles/
├── minimal.profile            # Essential agents only
├── backend.profile            # Backend development stack
└── full-stack.profile         # Complete development environment
```

**Profile Format:**
```bash
# Profile: backend
# Generated: 2024-01-15 10:30:00

# Active agents
AGENTS="python-pro backend-architect database-optimizer security-auditor"

# Active modes
MODES="Task_Management"

# Active rules
RULES="workflow-rules quality-rules"
```

---

### Init System

**Purpose**: Auto-detect project context and configure cortex appropriately.

**Workflow:**
```
1. detect → Analyze project structure
   - Language detection (package.json, requirements.txt, etc.)
   - Framework detection (FastAPI, React, Django, etc.)
   - Tool detection (Docker, K8s, Terraform, etc.)

2. profile → Recommend profile based on detection
   - Python + FastAPI → backend + python-pro + api patterns
   - TypeScript + React → frontend + typescript-pro + react-specialist
   - Monorepo → full-stack + multi-agent-coordinator

3. wizard → Interactive configuration
   - User confirms/adjusts recommendations
   - Activate agents, modes, skills
   - Save as project-specific profile

4. status → Show current configuration
   - Active agents with dependencies
   - Loaded skills
   - Active modes
```

**Detection Cache:**
```
~/.claude/.init/
├── projects/
│   └── project-slug-abc123.json      # Cached detection results
└── cache/
    └── last-session.json              # Resume interrupted init
```

---

## Component Relationships & Layered Architecture

### No Redundancy - Clear Separation

The cortex components form a **well-layered architecture** with no redundancy. Each component serves a distinct purpose:

| Component | Purpose | Analogy |
|-----------|---------|---------|
| **Agents** | WHO does work | Team members with expertise |
| **Modes** | HOW to execute | Workflow methodology (Agile/Waterfall) |
| **Rules** | WHAT to enforce | Company policies |
| **Skills** | Reusable patterns | Playbooks & SOPs |
| **Profiles** | Agent bundles | Team composition |
| **Scenarios** | Workflow tests | Integration tests |

### Key Distinctions

**Agents vs Modes**:
- **Agents** = Individual workers (personas with specific expertise)
- **Modes** = Orchestration strategy (how workers collaborate)
- Example: `code-reviewer` agent + `Parallel_Orchestration` mode = parallel code review

**Rules vs Modes**:
- **Rules** = Permanent policies (WHAT standards to meet)
- **Modes** = Switchable strategies (HOW to apply those standards)
- Example: `quality-gate-rules` defines 85% coverage; `Parallel_Orchestration` enforces it

**Skills vs Modes**:
- **Skills** = Passive documentation (reference library)
- **Modes** = Active behavior changes (execution strategy)
- Example: `systematic-debugging` documents a process; modes actively change execution

### Execution Flow

```
User Request → MODE (strategy)
                ↓
            References RULES (policies)
                ↓
            Orchestrates AGENTS (workers)
                ↓
            May invoke SKILLS (patterns)
                ↓
            Validated by SCENARIOS (tests)
```

### Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│ LAYER 1: Configuration                              │
│ → Profiles (pre-configured agent bundles)           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 2: Behavioral                                 │
│ → Modes (strategies) + Rules (policies)             │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 3: Execution                                  │
│ → Agents (specialized workers)                      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 4: Knowledge                                  │
│ → Skills (patterns and best practices)              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ LAYER 5: Validation                                 │
│ → Scenarios (workflow tests)                        │
└─────────────────────────────────────────────────────┘
```

### Concrete Example

**Task**: "Add user authentication with tests"

1. **MODE activates**: `Parallel_Orchestration`
   - Sets execution strategy: parallel workstreams + quality gates
   - Declares dependencies: `parallel-execution-rules`, `quality-gate-rules`
   - Overrides: `test_coverage_min: 85`

2. **RULES enforce**:
   - `quality-gate-rules`: Mandates tests with ≥85% coverage
   - `parallel-execution-rules`: Requires parallel agent execution

3. **AGENTS execute** (in parallel):
   - `general-purpose`: Implements authentication code
   - `test-automator`: Writes test suite (runs in parallel)
   - `code-reviewer`: Reviews code quality (runs in parallel)

4. **SKILLS may be invoked**:
   - `test-driven-development`: Provides TDD workflow pattern
   - `secure-coding-practices`: Provides auth security checklist

5. **PROFILE** (optional):
   - `full-stack` profile pre-configured these agents

### Component Relationships

**Modes ↔ Rules**:
- Modes **reference** rules via `dependencies` field
- Modes can **override** rule thresholds via `overrides` field
- Rules are permanent; modes are switchable

**Modes ↔ Agents**:
- Modes **orchestrate** agents (define how/when agents run)
- Modes can specify preferred agents for tasks
- Agents execute independently of modes

**Modes ↔ Skills**:
- Skills can **recommend** mode activation
- Modes can **invoke** skills for specific patterns
- Skills are passive; modes are active

**Modes ↔ Modes**:
- Modes can **conflict** with each other (mutually exclusive)
- Modes can **depend** on other modes
- Modes belong to **groups** (only one per group active)

---

## Workflow Orchestration

### Multi-Phase Workflows

**Pattern:**
```
Phase 1: Discovery/Assessment
  - Gather context and requirements
  - Map existing systems
  - Identify constraints

Phase 2: Design/Implementation
  - Produce artifacts
  - Apply patterns
  - Build solutions

Phase 3: Validation/Evolution
  - Test and verify
  - Document
  - Hand off
```

**Example: Backend Feature Development**
```
/dev:implement "user authentication API"

1. backend-architect (Sonnet)
   Phase: discovery
   - Analyze auth requirements
   - Map security constraints
   Outputs: API spec, security requirements

2. backend-architect (Sonnet)
   Phase: design
   - Design JWT flow
   - Define endpoints
   - Activates skill: api-design-patterns
   Outputs: OpenAPI spec

3. python-pro (Haiku)
   Phase: implementation
   - Implement endpoints
   - Apply FastAPI patterns
   Outputs: auth.py, routes.py

4. test-automator (Haiku)
   Phase: validation
   - Generate unit tests
   - Generate integration tests
   Outputs: test_auth.py

5. security-auditor (Sonnet)
   Phase: validation
   - Review auth implementation
   - Check OWASP compliance
   Outputs: Security report

6. code-reviewer (Sonnet)
   Phase: validation
   - Architectural review
   - Code quality check
   Outputs: Review comments

Total: 3 Sonnet + 2 Haiku calls
Cost: ~40% less than all-Sonnet
```

---

## Model Optimization

### Hybrid Strategy

**Sonnet 4.5 (27 agents):**
- Architecture & Design
- Security & Compliance
- Incident & Troubleshooting
- Code Review (with architectural considerations)
- Business & Product

**Haiku 4 (31 agents):**
- Code Generation
- Testing
- Infrastructure as Code
- Documentation
- Build & Deployment
- Data Processing

**Context-Dependent (9 agents):**
- Default to Haiku, escalate to Sonnet for complex cases

**Cost Savings:**
```
All Sonnet: $15 per 1M tokens × 1000 tasks = $15,000
Hybrid: $4.76 per task × 1000 = $4,760
Savings: 68%
```

---

## Performance Characteristics

### Latency

| Operation | Latency | Notes |
|-----------|---------|-------|
| Agent activation | <10ms | Filesystem read + YAML parse |
| Skill loading | <5ms | Metadata only |
| Dependency resolution | <20ms | Graph traversal |
| CLI command | <100ms | Python startup + execution |

### Scalability

| Metric | Current | Target |
|--------|---------|--------|
| Total agents | 78 | 100+ |
| Active agents | 11 | 20-30 typical |
| Skills per agent | 0-3 | 2-5 |
| Context size | 5-15K tokens | Target <10K |

---

## Design Patterns

### Pattern 1: Lazy Loading
```
Problem: Loading all agents consumes excessive tokens
Solution: Load agents only when triggered by keywords/patterns
Benefit: 60-80% token reduction
```

### Pattern 2: Dependency Injection
```
Problem: Agents need other agents but tight coupling
Solution: Declare dependencies in frontmatter, auto-resolve
Benefit: Loose coupling, validation, clear relationships
```

### Pattern 3: Progressive Disclosure
```
Problem: Heavyweight agents with rarely-used knowledge
Solution: Extract knowledge into skills, load on-demand
Benefit: 30-50% token reduction per agent
```

### Pattern 4: Strategy Pattern (Model Selection)
```
Problem: One model doesn't fit all tasks
Solution: Assign Haiku/Sonnet based on complexity
Benefit: 40-60% cost savings
```

### Pattern 5: Command Pattern (CLI)
```
Problem: Complex operations need structured interface
Solution: CLI with subcommands (agent, skill, init, etc.)
Benefit: Discoverability, automation, scripting
```

---

## Anti-Patterns to Avoid

1. **Monolithic Agents**: Keep agents focused, extract knowledge to skills
2. **Circular Dependencies**: Agents should form DAG, not cycles
3. **Missing Activation Criteria**: Always define keywords and conditions
4. **Ignoring Model Optimization**: Use Haiku for deterministic tasks
5. **No Metrics**: Track performance to inform optimization
6. **Premature Agent Creation**: Start with fewer, split when needed
7. **Skill Explosion**: Don't create skills for every small topic
8. **Shared State**: Agents should be stateless (use profiles for state)

---

## Extension Points

### Adding New Agents

1. **Research**: Identify clear responsibility and activation criteria
2. **Design**: Define dependencies, workflows, metrics
3. **Implement**: Create agent .md with complete frontmatter
4. **Validate**: `cortex agent validate agent-name`
5. **Test**: Activate and verify behavior
6. **Document**: Add to guides/agents.md catalog
7. **Optimize**: Assign appropriate model (Haiku/Sonnet)

### Creating Skills

1. **Identify**: Find 1000+ token knowledge chunks in agents
2. **Extract**: Create skill/ directory with SKILL.md
3. **Structure**: Frontmatter + progressive tiers
4. **Link**: Add skill to agent frontmatter
5. **Validate**: `cortex skills validate skill-name`
6. **Document**: Update skills/README.md

### Custom Workflows

1. **Define**: Identify multi-phase process
2. **Map Agents**: Which agents participate in each phase
3. **Create Command**: Add to commands/ directory
4. **Orchestrate**: Define agent sequence and data flow
5. **Measure**: Track metrics and optimize

---

## Future Enhancements

### Smart Routing
- Analyze task complexity before model selection
- Auto-escalate from Haiku to Sonnet when confidence low
- Learn from corrections

### Auto-Skill Activation
- Parse user intent for skill keywords
- Load skills proactively based on context
- Track skill effectiveness

### Cross-Session Memory
- Persist agent state between sessions
- Remember user preferences and patterns
- Build project-specific knowledge base

### Distributed Execution
- Parallel agent execution for independent tasks
- Queue-based orchestration for complex workflows
- Resource pooling and throttling

---

## Resources

- [Agent Skills Guide](../skills.md)
- [Agent Catalog](../agents.md)
- [Model Optimization](./model-optimization.md)
- [CLI Reference](../../../README.md#using-the-bundled-cli)
- [Workflow Patterns](../../../workflows/)
