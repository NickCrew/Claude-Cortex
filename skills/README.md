# Agent Skills - Progressive Disclosure Architecture

Agent skills implement **progressive disclosure** - loading specialized knowledge only when needed, reducing token usage while maintaining deep expertise.

## Architecture

### Three-Tier Progressive Loading

1. **Metadata (Always Loaded)**: YAML frontmatter with name, description, and activation triggers
2. **Instructions (Loaded When Activated)**: Core guidance and patterns
3. **Resources (On-Demand)**: Detailed examples, templates, and references

### Token Efficiency

```
Without Skills:
  backend-architect.md (full agent) = ~8,000 tokens loaded immediately

With Skills:
  backend-architect.md (core agent) = ~3,000 tokens
  + api-design-patterns skill (when needed) = +2,500 tokens
  + microservices-patterns skill (when needed) = +2,800 tokens
  Total loaded only what's needed = 30-40% reduction
```

## Skill Structure

### Directory Layout
```
skills/
├── api-design-patterns/
│   └── SKILL.md                    # Skill content
├── microservices-patterns/
│   └── SKILL.md
├── event-driven-architecture/
│   └── SKILL.md
└── README.md                       # This file
```

### SKILL.md Format
```yaml
---
name: skill-name                    # Hyphen-case, unique identifier
description: What the skill does. Use when [trigger condition]. # < 1024 chars
---

# Skill Title

Overview paragraph explaining the skill's purpose and scope.

## When to Use This Skill

- Specific scenario 1
- Specific scenario 2
- Specific scenario 3

## Core Content

[Progressive disclosure tiers: foundational → intermediate → advanced]
```

## Integration with Agents

### Agent Frontmatter Enhancement
```yaml
---
name: backend-architect
# ... existing fields ...
skills:                             # NEW: Skills this agent can activate
  - api-design-patterns
  - microservices-patterns
  - event-driven-architecture
---
```

### CLI Commands

```bash
# List available skills
claude-ctx skills list

# Show skill details
claude-ctx skills info api-design-patterns

# Show which agents use a skill
claude-ctx skills deps api-design-patterns
```

### Activation Triggers

Skills activate automatically when:
1. **Keywords match**: User request contains skill-specific keywords
2. **Agent requests**: Active agent explicitly invokes skill
3. **Context indicates**: File patterns or project structure suggest need

## Creating New Skills

### 1. Identify Knowledge Domain

Extract heavyweight knowledge from agents that:
- Contains >1000 tokens of specialized patterns
- Applies to specific scenarios (not always needed)
- Has clear activation criteria
- Benefits multiple agents

### 2. Create Skill Directory
```bash
mkdir -p skills/your-skill-name
```

### 3. Write SKILL.md

```yaml
---
name: your-skill-name
description: Brief description. Use when [clear trigger condition].
---

# Skill Title

## When to Use This Skill
[Specific scenarios with clear triggers]

## Core Patterns
[Progressive disclosure: essential → detailed → advanced]

## Best Practices Summary
[Quick reference for common cases]

## Resources
[External references and documentation]
```

### 4. Link to Agents

Update agent frontmatter to reference the skill:
```yaml
skills:
  - your-skill-name
```

### 5. Validate
```bash
# Ensure skill metadata is valid
claude-ctx skills validate your-skill-name

# Test skill loading
claude-ctx skills info your-skill-name
```

## Existing Skills

### Phase 1 Skills (Foundation)

#### api-design-patterns
**Agents**: backend-architect
**Triggers**: API design, REST, GraphQL, endpoint design, service contracts
**Content**: Versioning, pagination, error handling, HATEOAS, rate limiting, caching
**Size**: ~1,800 tokens

### Newly Added Skills

In addition to the core skills, the following skills have been integrated from personal collections and the `obra/superpowers` project:

*   **From personal collection:** `canvas-design`, `internal-comms`, `skill-creator`, `template-skill`, `webapp-testing`.
*   **From `obra/superpowers`:** `condition-based-waiting`, `defense-in-depth`, `dispatching-parallel-agents`, `finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`, `root-cause-tracing`, `sharing-skills`, `subagent-driven-development`, `systematic-debugging`, `test-driven-development`, `testing-anti-patterns`, `testing-skills-with-subagents`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `writing-skills`.

### Collaboration Skills (borrowed from obra/superpowers, MIT)

| Skill | Command | Purpose |
| --- | --- | --- |
| `collaboration/brainstorming` | `/ctx:brainstorm` | Structured ideation aligned with Supersaiyan mode + Task TUI seeding |
| `collaboration/writing-plans` | `/ctx:plan` | Produces actionable plans that map to workflows + tasks |
| `collaboration/executing-plans` | `/ctx:execute-plan` | Drives plan execution, orchestration view, verification |

#### microservices-patterns
**Agents**: backend-architect
**Triggers**: Microservices, service decomposition, distributed systems
**Content**: Service decomposition, communication patterns, CQRS, saga, resilience, observability
**Size**: ~3,200 tokens

### Phase 2 Skills (Core Skills)

#### Architecture & Design (4 skills)

##### event-driven-architecture
**Agents**: backend-architect
**Triggers**: Event sourcing, CQRS, message brokers, eventual consistency
**Content**: Event sourcing, CQRS, pub/sub, saga patterns, Kafka/RabbitMQ
**Size**: ~3,400 tokens

##### database-design-patterns
**Agents**: backend-architect
**Triggers**: Database schema, query optimization, data modeling
**Content**: Normalization, indexing, partitioning, sharding, replication patterns
**Size**: ~3,200 tokens

##### cqrs-event-sourcing
**Agents**: backend-architect
**Triggers**: CQRS, event sourcing, temporal queries, audit systems
**Content**: Command/query separation, event store design, projections, snapshots
**Size**: ~3,500 tokens

##### api-gateway-patterns
**Agents**: backend-architect
**Triggers**: API gateway, BFF, service composition, routing
**Content**: Gateway routing, authentication, rate limiting, circuit breakers, BFF
**Size**: ~2,400 tokens

#### Infrastructure (4 skills)

##### kubernetes-deployment-patterns
**Agents**: kubernetes-architect
**Triggers**: K8s deployments, rollout strategies, StatefulSets
**Content**: Deployment strategies (rolling, blue-green, canary), workload types, autoscaling
**Size**: ~2,800 tokens

##### kubernetes-security-policies
**Agents**: kubernetes-architect
**Triggers**: K8s security, RBAC, network policies, Pod Security Standards
**Content**: PSS/PSA, Network Policies, RBAC, Security Contexts, admission control
**Size**: ~2,500 tokens

##### helm-chart-patterns
**Agents**: kubernetes-architect
**Triggers**: Helm charts, K8s packaging, templating
**Content**: Chart structure, values files, templates, dependencies, hooks, Helmfile
**Size**: ~2,700 tokens

##### gitops-workflows
**Agents**: kubernetes-architect
**Triggers**: GitOps, ArgoCD, Flux, declarative deployments
**Content**: GitOps principles, ArgoCD, Flux, environment promotion, secret management
**Size**: ~2,600 tokens

##### terraform-best-practices
**Agents**: terraform-specialist
**Triggers**: Terraform, IaC, infrastructure automation
**Content**: Module design, state management, workspaces, security, testing
**Size**: ~2,400 tokens

#### Development (5 skills)

##### async-python-patterns
**Agents**: python-pro
**Triggers**: Python asyncio, async/await, concurrent programming
**Content**: asyncio fundamentals, async/await, event loops, context managers
**Size**: ~2,000 tokens

##### python-testing-patterns
**Agents**: python-pro
**Triggers**: pytest, unit testing, mocking, test automation
**Content**: pytest fundamentals, fixtures, parametrize, mocking, property-based testing
**Size**: ~2,700 tokens

##### python-performance-optimization
**Agents**: python-pro
**Triggers**: Python performance, profiling, optimization
**Content**: Profiling tools, algorithmic optimization, memoization, Cython, multiprocessing
**Size**: ~2,400 tokens

##### typescript-advanced-patterns
**Agents**: typescript-pro
**Triggers**: TypeScript, advanced types, type safety
**Content**: Conditional types, mapped types, template literals, type guards, generics
**Size**: ~2,800 tokens

##### react-performance-optimization
**Agents**: typescript-pro
**Triggers**: React performance, memoization, code splitting
**Content**: React.memo, useMemo/useCallback, code splitting, virtualization, concurrent features
**Size**: ~2,500 tokens

#### Security (4 skills)

##### owasp-top-10
**Agents**: security-auditor
**Triggers**: Security vulnerabilities, OWASP, security audit
**Content**: OWASP Top 10 2021 vulnerabilities with detection and remediation
**Size**: ~3,200 tokens

##### secure-coding-practices
**Agents**: security-auditor
**Triggers**: Secure coding, input validation, authentication, cryptography
**Content**: Input validation, output encoding, authentication, cryptography, secure defaults
**Size**: ~3,400 tokens

##### threat-modeling-techniques
**Agents**: security-auditor
**Triggers**: Threat modeling, STRIDE, attack trees, risk assessment
**Content**: STRIDE methodology, attack trees, DFD, trust boundaries, DREAD
**Size**: ~3,600 tokens

##### security-testing-patterns
**Agents**: security-auditor
**Triggers**: Security testing, SAST, DAST, penetration testing
**Content**: SAST/DAST, penetration testing, fuzzing, API security testing
**Size**: ~3,200 tokens

### Summary

**Total Skills**: 42
**Average Skill Size**: ~2,800 tokens (estimated)
**Token Efficiency**: 30-50% reduction per agent (estimated)

## Skill Development Guidelines

### Naming Conventions
- Use hyphen-case: `api-design-patterns`, not `API_Design_Patterns`
- Be specific: `react-performance-optimization`, not `performance`
- Focus on domain: `kubernetes-security-policies`, not `k8s-stuff`

### Description Format
```
[What it does]. Use when [specific trigger].

Good:
"REST and GraphQL API design with versioning and pagination. Use when designing endpoints or service contracts."

Bad:
"Helps with APIs and stuff. Use when you need API help."
```

### Content Structure

1. **Overview** (1-2 paragraphs): What and why
2. **When to Use** (bulleted list): Clear activation criteria
3. **Core Patterns** (progressive sections): Essential → detailed → advanced
4. **Examples** (practical): Real-world code with annotations
5. **Anti-Patterns** (optional): Common mistakes to avoid
6. **Resources** (links): Official docs and references

### Progressive Disclosure Tiers

**Tier 1 - Essential (always include):**
- Core concepts and principles
- Most common patterns (80% use cases)
- Quick reference tables

**Tier 2 - Detailed (include for depth):**
- Advanced patterns and edge cases
- Performance optimization techniques
- Complex examples with explanations

**Tier 3 - Reference (optional, link externally):**
- Exhaustive specifications
- Framework-specific implementations
- Academic research or RFCs

## Token Budget Guidelines

| Skill Complexity | Target Token Range | Example |
|-----------------|-------------------|---------|
| Focused | 500-1,500 tokens | git-workflow-patterns |
| Standard | 1,500-3,000 tokens | api-design-patterns |
| Comprehensive | 3,000-5,000 tokens | async-python-patterns |
| Specialized | 5,000-8,000 tokens | kubernetes-operator-patterns |

**Rule**: If skill exceeds 8,000 tokens, split into multiple focused skills.

## Quality Checklist

- [ ] Clear, specific skill name (hyphen-case)
- [ ] Description < 1024 chars with "Use when" trigger
- [ ] "When to Use This Skill" section with 5-10 scenarios
- [ ] Progressive disclosure (essential → detailed → advanced)
- [ ] Practical code examples with annotations
- [ ] Best practices summary at the end
- [ ] No emojis unless explicitly requested
- [ ] Grammar and spelling checked
- [ ] Links to official documentation included
- [ ] Validated with `claude-ctx skills validate`

## Benefits vs. Full Agent Loading

### Before (Agent-Only)
```
User: "Design a REST API for user management"
→ Loads entire backend-architect agent (~8,000 tokens)
→ Includes DB patterns, caching, event-driven, etc. (not needed)
→ Context pollution with irrelevant knowledge
```

### After (Agent + Skills)
```
User: "Design a REST API for user management"
→ Loads backend-architect core agent (~3,000 tokens)
→ Activates api-design-patterns skill (~2,500 tokens)
→ Total: 5,500 tokens (31% reduction)
→ Only relevant knowledge in context
```

## Roadmap

All planned phases for skill development and integration are now **COMPLETED**. The framework supports a wide array of skills, including those for architecture, infrastructure, development, security, and collaboration. The total number of available skills has significantly expanded, enhancing the system's overall capabilities.

## See Also

- [Anthropic Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)
- [~/agents Agent Skills Guide](https://github.com/wshobson/agents/blob/main/docs/agent-skills.md)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
