---
layout: default
title: Skills
nav_order: 5
---

# Agent Skills Guide

Progressive disclosure architecture for specialized knowledge that loads on-demand to optimize token usage.

## Overview

Agent skills enable **progressive disclosure** - loading specialized knowledge only when needed, significantly reducing token usage while maintaining deep expertise.

**Token Efficiency:**
- Without skills: Agent loads ~8,000 tokens (all knowledge)
- With skills: Agent core ~3,000 + skills on-demand ~1,800-3,200
- **Savings: 30-50% per agent**

**Architecture:**
```
Tier 1: Metadata (always loaded)
   ↓ 50 tokens - name, description, triggers
Tier 2: Instructions (loaded when activated)
   ↓ 1,800-3,200 tokens - core patterns and guidance
Tier 3: Resources (loaded on deep-dive)
   ↓ 500-1,000 tokens - examples, templates, references
```

---

## Available Skills

### api-design-patterns

**Agent**: backend-architect
**Size**: ~1,800 tokens
**Model Impact**: Haiku-friendly (deterministic patterns)

**Covers:**
- REST and GraphQL API design
- Versioning strategies (URI, header, query)
- Pagination patterns (offset, cursor, keyset)
- Error handling with standard schemas
- Rate limiting and caching
- Authentication patterns (Bearer, API Key, OAuth)
- HATEOAS and hypermedia
- Field selection and filtering
- Idempotency patterns

**Use When:**
- Designing new APIs or refactoring existing ones
- Defining service contracts for microservices
- Implementing API versioning
- Standardizing error responses
- Architecting API gateways

**CLI:**
```bash
claude-ctx skills info api-design-patterns
```

---

### microservices-patterns

**Agent**: backend-architect
**Size**: ~3,200 tokens
**Model Impact**: Sonnet-friendly (complex architecture)

**Covers:**
- Service decomposition (business capability, subdomain, transaction)
- Communication patterns (sync/async, API Gateway, gRPC, pub/sub)
- Data management (database per service, CQRS, saga, event sourcing)
- Resilience patterns (circuit breaker, retry, bulkhead, timeout)
- Observability (distributed tracing, centralized logging, metrics)
- Service mesh architecture
- Deployment strategies (blue-green, canary, rolling)
- Migration patterns (strangler fig, branch by abstraction)

**Use When:**
- Breaking down monoliths into services
- Designing distributed systems
- Implementing service-to-service communication
- Managing data consistency across services
- Building resilient microservices
- Defining service boundaries

**CLI:**
```bash
claude-ctx skills info microservices-patterns
```

---

## Creating New Skills

### Skill Development Workflow

```
1. Identify candidate
   ↓ Find 1000+ token knowledge chunk in agent

2. Extract and structure
   ↓ Create skill directory and SKILL.md

3. Write frontmatter
   ↓ Name, description with "Use when" triggers

4. Organize content
   ↓ Progressive tiers: essential → detailed → advanced

5. Link to agent
   ↓ Add skill to agent frontmatter

6. Validate
   ↓ claude-ctx skills validate skill-name

7. Document
   ↓ Update skills/README.md and this guide
```

### Identifying Skill Candidates

**Good candidates:**
- **Size**: 1,000+ tokens of specialized knowledge
- **Specificity**: Applies to specific scenarios, not always needed
- **Reusability**: Could benefit multiple agents
- **Clarity**: Clear activation criteria

**Examples:**
```
✓ async-python-patterns (Python async programming)
✓ kubernetes-security-policies (K8s security best practices)
✓ graphql-schema-design (GraphQL patterns)
✓ ci-cd-pipeline-patterns (CI/CD best practices)

✗ "python basics" (too general, always needed)
✗ "code quality" (too vague, no clear triggers)
✗ "tips and tricks" (no structure, random knowledge)
```

### Skill Structure Template

```markdown
---
name: skill-name
description: What it covers. Use when [clear trigger criteria].
---

# Skill Title

Brief overview (1-2 paragraphs) explaining scope and purpose.

## When to Use This Skill

- Specific scenario 1
- Specific scenario 2
- Specific scenario 3
- Specific scenario 4
- Specific scenario 5

## Core Principles (Optional)

Foundational concepts that underpin the patterns.

## Fundamental Patterns (Tier 1 - Essential)

80% use cases, most common patterns.

### Pattern 1: Name
**Definition:** Brief explanation
**Example:** Code example with comments
**Benefits:** Why use this pattern
**Trade-offs:** When not to use

### Pattern 2: Name
...

## Advanced Patterns (Tier 2 - Detailed)

Complex scenarios, edge cases, performance optimization.

### Pattern N: Name
...

## Real-World Applications (Optional)

Practical examples showing patterns in production context.

## Anti-Patterns to Avoid

Common mistakes and how to prevent them.

## Best Practices Summary

Quick reference checklist.

## Resources

- Official documentation links
- RFCs, specifications
- Tools and libraries
```

### Frontmatter Requirements

**Required Fields:**
```yaml
---
name: skill-name                 # Hyphen-case, unique
description: Brief description. Use when [trigger]. # < 1024 chars
---
```

**Validation Rules:**
- `name`: Must be hyphen-case, unique across all skills
- `description`: Must contain "Use when" for clear activation trigger
- `description`: Must be < 1024 characters

**Examples:**

✓ **Good:**
```yaml
---
name: async-python-patterns
description: Python asyncio and concurrent programming patterns for high-performance applications. Use when building async APIs, concurrent systems, or I/O-bound applications requiring non-blocking operations.
---
```

✗ **Bad:**
```yaml
---
name: Python_Async          # Wrong format (not hyphen-case)
description: Async patterns for Python.  # Missing "Use when", too vague
---
```

---

## Token Budget Guidelines

| Skill Complexity | Token Range | Use Case |
|-----------------|-------------|----------|
| Focused | 500-1,500 | Single pattern or technique |
| Standard | 1,500-3,000 | Set of related patterns |
| Comprehensive | 3,000-5,000 | Domain expertise |
| Specialized | 5,000-8,000 | Deep technical knowledge |

**Rule**: If skill exceeds 8,000 tokens, split into multiple focused skills.

### Examples by Size

**Focused (500-1,500 tokens):**
- git-workflow-patterns
- docker-optimization-tips
- sql-index-strategies

**Standard (1,500-3,000 tokens):**
- api-design-patterns (~1,800 tokens) ✓
- react-performance-optimization
- terraform-module-patterns

**Comprehensive (3,000-5,000 tokens):**
- microservices-patterns (~3,200 tokens) ✓
- kubernetes-deployment-patterns
- event-driven-architecture

**Specialized (5,000-8,000 tokens):**
- distributed-systems-patterns
- ml-system-design-patterns
- blockchain-smart-contract-security

---

## Progressive Disclosure in Practice

### Example: backend-architect + api-design-patterns

**Scenario:** User asks "Design a REST API for user management"

**Without Skills (Old Way):**
```
1. Load backend-architect.md (8,000 tokens)
   - API patterns (needed) ✓
   - Microservices (not needed) ✗
   - Event-driven (not needed) ✗
   - CQRS (not needed) ✗
   - Database patterns (not needed) ✗
Total: 8,000 tokens, 60% unused
```

**With Skills (New Way):**
```
1. Load backend-architect.md core (3,000 tokens)
   - Architecture principles ✓
   - Workflow guidance ✓

2. Detect "REST API" trigger → Activate api-design-patterns

3. Load api-design-patterns skill (1,800 tokens)
   - REST design ✓
   - Versioning ✓
   - Pagination ✓
   - Error handling ✓

Total: 4,800 tokens, 0% waste
Savings: 40%
```

---

## Skill Composition

Skills can reference other skills for complex workflows:

```
User: "Build a microservices-based e-commerce platform"

1. backend-architect activates
2. Loads skills in sequence:
   - api-design-patterns (service contracts)
   - microservices-patterns (architecture)
   - event-driven-architecture (async communication)

3. Coordinates with other agents:
   - database-optimizer (data patterns)
   - kubernetes-architect (deployment)
   - security-auditor (security validation)
```

---

## Integration with Agents

### Agent Frontmatter

```yaml
---
name: backend-architect
# ... other fields ...
skills:                          # NEW field
  - api-design-patterns          # Skill 1
  - microservices-patterns       # Skill 2
  - event-driven-architecture    # Skill 3
---
```

### Activation Logic

**Automatic (Keyword-Based):**
```
User message contains:
  "REST API" → api-design-patterns
  "microservices" → microservices-patterns
  "event-driven" → event-driven-architecture
```

**Explicit (Agent-Requested):**
```
Agent determines it needs specific knowledge:
  "I need guidance on API versioning strategies"
  → Load api-design-patterns
```

**Context-Driven (Project Detection):**
```
Project type: FastAPI microservices
  → Automatically suggest:
     - api-design-patterns
     - microservices-patterns
     - async-python-patterns
```

---

## CLI Commands

```bash
# List all available skills
claude-ctx skills list

# Show skill details
claude-ctx skills info api-design-patterns

# Validate skill metadata
claude-ctx skills validate api-design-patterns

# Validate all skills
claude-ctx skills validate --all

# Show which agents use a skill (future)
claude-ctx skills deps api-design-patterns
```

---

## Quality Checklist

Before committing a new skill, verify:

- [ ] Clear, specific name (hyphen-case)
- [ ] Description < 1024 chars with "Use when" trigger
- [ ] "When to Use This Skill" section with 5-10 scenarios
- [ ] Progressive disclosure (essential → detailed → advanced)
- [ ] Practical code examples with annotations
- [ ] Best practices summary at the end
- [ ] No emojis (unless explicitly requested)
- [ ] Grammar and spelling checked
- [ ] Links to official documentation
- [ ] Validates with `claude-ctx skills validate`
- [ ] Token count within budget (< 8K)
- [ ] Linked to relevant agent(s) in frontmatter

---

## Skill Roadmap

### Phase 1: Foundation (Current)
- [x] Skills directory structure
- [x] SKILL.md format specification
- [x] CLI integration (list, info, validate)
- [x] First skill: api-design-patterns
- [x] Second skill: microservices-patterns

### Phase 2: Core Skills (Next 2 Months)

**Architecture & Design:**
- [ ] event-driven-architecture
- [ ] database-design-patterns
- [ ] cqrs-event-sourcing
- [ ] api-gateway-patterns

**Infrastructure:**
- [ ] kubernetes-deployment-patterns
- [ ] kubernetes-security-policies
- [ ] helm-chart-patterns
- [ ] gitops-workflows
- [ ] terraform-best-practices

**Development:**
- [ ] async-python-patterns (borrow from ~/agents)
- [ ] python-testing-patterns
- [ ] python-performance-optimization
- [ ] typescript-advanced-patterns
- [ ] react-performance-optimization

**Security:**
- [ ] owasp-top-10
- [ ] secure-coding-practices
- [ ] threat-modeling-techniques
- [ ] security-testing-patterns

### Phase 3: Integration (Months 3-4)
- [ ] Automatic skill activation based on keywords
- [ ] Context-driven skill suggestions
- [ ] Skill performance metrics (token savings tracking)
- [ ] Dependency tracking (skill → agent relationships)

### Phase 4: Advanced (Months 5-6)
- [ ] Skill composition (skills reference other skills)
- [ ] Versioned skills (skill evolution without breaking)
- [ ] Community contributed skills
- [ ] Skill effectiveness analytics

---

## Metrics & Analytics

### Token Efficiency

| Agent | Without Skills | With Skills | Savings |
|-------|---------------|-------------|---------|
| backend-architect | 8,000 tokens | 4,800 tokens | 40% |
| kubernetes-architect | 7,500 tokens | ~4,500 tokens | 40% |
| security-auditor | 6,800 tokens | ~4,500 tokens | 34% |
| deployment-engineer | 7,200 tokens | ~4,800 tokens | 33% |

**Aggregate Savings**: 35-40% across heavyweight agents

### Skill Usage Patterns

Track skill activation frequency to prioritize future skills:
- Most requested skills → Create first
- Rarely activated → Consider merging or removing
- High token savings → Validate investment

---

## Best Practices

### For Skill Authors

1. **Start with "When to Use"**: Clear activation criteria prevent confusion
2. **Progressive Structure**: Essential patterns first, advanced later
3. **Practical Examples**: Show don't tell with code examples
4. **Link Official Docs**: Point to authoritative sources
5. **Token Budget**: Keep under 5K for standard skills
6. **Avoid Duplication**: Reference other skills instead of repeating
7. **Update Regularly**: As patterns evolve, update skills
8. **Validate Often**: Run validation before committing

### For Skill Users

1. **Check Available Skills**: `claude-ctx skills list` before creating agents
2. **Link Skills**: Add relevant skills to agent frontmatter
3. **Monitor Usage**: Track which skills activate most frequently
4. **Provide Feedback**: Report skill effectiveness to maintainers
5. **Suggest New Skills**: Identify patterns that warrant extraction

---

## FAQs

**Q: When should I create a skill vs. keeping knowledge in agent?**
A: Create a skill if knowledge is:
- 1,000+ tokens
- Specific to scenarios (not always needed)
- Could benefit multiple agents
- Has clear activation triggers

**Q: Can multiple agents use the same skill?**
A: Yes! That's a key benefit. api-design-patterns could be used by backend-architect, api-documenter, and code-reviewer.

**Q: How do I know if a skill is being loaded?**
A: Currently via agent behavior. Future: skill activation metrics in logs.

**Q: What if my skill exceeds 8,000 tokens?**
A: Split into multiple focused skills. Example: "microservices-patterns" + "microservices-resilience" + "microservices-observability"

**Q: Can skills reference other skills?**
A: Not yet, but planned for Phase 4 (skill composition).

**Q: How often should skills be updated?**
A: Review quarterly, update when:
- Patterns evolve (new best practices)
- Community feedback indicates gaps
- Official specs change (e.g., OpenAPI 3.1 → 4.0)

**Q: Can I contribute skills?**
A: Yes! Follow the creation workflow, validate, and submit PR.

---

## Examples from ~/agents

The ~/agents marketplace has 47 skills across 14 plugins. Key examples:

**Python Development (5 skills):**
- async-python-patterns (~695 tokens) - Comprehensive asyncio guide
- python-testing-patterns - pytest and fixtures
- python-packaging - Modern packaging with pyproject.toml
- python-performance-optimization - Profiling and optimization
- uv-package-manager - Fast dependency management

**Kubernetes (4 skills):**
- k8s-manifest-generator - YAML generation
- helm-chart-scaffolding - Helm templating
- gitops-workflow - ArgoCD/Flux patterns
- k8s-security-policies - Pod Security Standards

**Backend (3 skills):**
- api-design-principles - REST fundamentals
- architecture-patterns - SOLID, DDD, Clean Architecture
- microservices-patterns - Microservices best practices

**LLM Applications (4 skills):**
- langchain-patterns - LangChain usage
- prompt-engineering - Effective prompts
- rag-systems - Retrieval Augmented Generation
- llm-evaluation - Model evaluation metrics

These serve as excellent reference implementations.

---

## Resources

- [Anthropic Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)
- [~/agents Skills Guide](https://github.com/wshobson/agents/blob/main/docs/agent-skills.md)
- [Claude Code Skills Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- Internal: `skills/README.md` - Detailed integration guide
- Internal: `docs/architecture.md` - Overall architecture
- Internal: `docs/agents.md` - Agent catalog
