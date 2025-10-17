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

### api-design-patterns
**Agent**: backend-architect
**Triggers**: API design, REST, GraphQL, endpoint design, service contracts
**Content**: Versioning, pagination, error handling, HATEOAS, rate limiting, caching
**Size**: ~2,500 tokens

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

### Phase 1: Foundation (Current)
- [x] Skills directory structure
- [x] SKILL.md format specification
- [x] First skill: api-design-patterns
- [ ] CLI integration (list, info, validate)

### Phase 2: Core Skills (Next)
- [ ] microservices-patterns
- [ ] event-driven-architecture
- [ ] database-design-patterns
- [ ] kubernetes-deployment-patterns
- [ ] async-python-patterns (from ~/agents)

### Phase 3: Integration
- [ ] Automatic skill activation based on keywords
- [ ] Agent frontmatter `skills:` field support
- [ ] Dependency tracking (skill → agent relationships)
- [ ] Performance metrics (token usage reduction)

### Phase 4: Advanced
- [ ] Skill composition (skills reference other skills)
- [ ] Versioned skills (skill evolution without breaking)
- [ ] Community contributed skills
- [ ] Skill marketplace integration

## See Also

- [Anthropic Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)
- [~/agents Agent Skills Guide](https://github.com/wshobson/agents/blob/main/docs/agent-skills.md)
- [Claude Code Skills Documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
