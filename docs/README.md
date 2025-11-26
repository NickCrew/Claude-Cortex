# claude-ctx Documentation

Comprehensive documentation for the claude-ctx context management framework.

## 📐 Architecture Documentation

**NEW**: Comprehensive visual documentation of the three-layer system!

- **[Architecture Diagrams](reference/architecture/architecture-diagrams.md)** - 10+ Mermaid diagrams showing system architecture, flows, and integration patterns
- **[Quick Reference](reference/architecture/quick-reference.md)** - One-page cheat sheet for daily use (commands, modes, workflows)
- **[Visual Summary](reference/architecture/VISUAL_SUMMARY.txt)** - Beautiful ASCII art diagram for terminal viewing
- **[Diagrams Guide](reference/architecture/DIAGRAMS_README.md)** - How to use, read, and maintain all diagrams

**After installation**: These docs are available at `~/.claude/docs/`

**Quick view**:
```bash
cat ~/.claude/docs/VISUAL_SUMMARY.txt       # Terminal-friendly overview
/docs:diagrams                               # View via command
```

---

## Documentation Map

### Core Guides

**[Architecture](./guides/development/architecture.md)** - System design and technical architecture
- Component overview and system architecture
- Dependency management and workflow orchestration
- Performance characteristics and design patterns
- Extension points and future enhancements

**[Agent Catalog](./guides/agents.md)** - Complete agent reference
- 74 agents organized by category
- Model assignments (Haiku/Sonnet/Opus)
- Dependencies and relationships
- Use cases and activation patterns

**[Agent Skills](./guides/skills.md)** - Progressive disclosure system
- 42 available skills
- Creating new skills with templates
- Token efficiency metrics (30-50% savings)
- Integration with agents

**[Model Optimization](./guides/development/model-optimization.md)** - Cost and performance strategy
- Haiku vs Sonnet assignment criteria
- Hybrid orchestration patterns
- Cost analysis (68% savings)
- Migration plan and monitoring

---

## Quick Start

### Understanding claude-ctx

claude-ctx is a context orchestration framework that provides:

1. **On-Demand Loading**: Agents load only when triggered
2. **Progressive Disclosure**: Skills load knowledge in tiers
3. **Dependency Resolution**: Automatic agent dependency management
4. **Hybrid Execution**: Strategic Haiku/Sonnet model assignment
5. **Workflow Automation**: Multi-phase structured workflows

### Key Concepts

**Agents**: Specialized AI agents with focused responsibilities (74 total)
- 9 active by default
- 65 available on-demand
- Each has dependencies, workflows, and metrics

**Skills**: Modular knowledge packages that load progressively
- 42 available skills
- 30-50% token reduction per agent
- Shared across multiple agents

**Modes**: Behavioral presets that toggle workflow defaults
- Task_Management, Project_Memory, Agile_Sprint
- Control tool preferences and activation patterns

**Profiles**: Saved configurations of agents/modes/rules
- minimal, backend, full-stack
- Quick environment setup

---

## Common Workflows

### Backend Development
```
backend-architect (Sonnet) → Design API
  ↓
python-pro (Haiku) → Implement endpoints
  ↓
test-automator (Haiku) → Generate tests
  ↓
security-auditor (Sonnet) → Security review
```

### Infrastructure Setup
```
cloud-architect (Sonnet) → Design infrastructure
  ↓
terraform-specialist (Haiku) → Write IaC
  ↓
kubernetes-architect (Sonnet) → K8s architecture
  ↓
deployment-engineer (Sonnet) → CI/CD pipelines
```

### Incident Response
```
incident-responder (Sonnet) → Coordinate triage
  ↓
debugger (Sonnet) → Diagnose root cause
  ↓
python-pro (Haiku) → Implement fix
  ↓
test-automator (Haiku) → Add regression tests
```

---

## CLI Quick Reference

### Agent Management
```bash
# List agents
claude-ctx agent list

# Show agent details
claude-ctx agent deps backend-architect

# Activate/deactivate
claude-ctx agent activate backend-architect
claude-ctx agent deactivate backend-architect

# Dependency graph
claude-ctx agent graph --export deps.md

# Validate agents
claude-ctx agent validate --all
```

### Skill Management
```bash
# List skills
claude-ctx skills list

# Show skill details
claude-ctx skills info api-design-patterns

# Validate skills
claude-ctx skills validate --all
```

### Project Initialization
```bash
# Auto-detect project
claude-ctx init detect

# Interactive wizard
claude-ctx init wizard

# Show current config
claude-ctx init status

# Load profile
claude-ctx profile backend
```

### Status
```bash
# Show all status
claude-ctx status

### Diagnostics
```bash
# Run system check
claude-ctx doctor

# Attempt auto-fix
claude-ctx doctor --fix
```
```

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│      Claude Code Interface          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         claude-ctx CLI              │
│  ┌──────────┐  ┌──────────┐        │
│  │  Agents  │  │  Skills  │        │
│  │  list    │  │  list    │        │
│  │  activate│  │  info    │        │
│  │  deps    │  │  validate│        │
│  └──────────┘  └──────────┘        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Context Resolution Engine         │
│  • Dependency Resolution            │
│  • Trigger Matching                 │
│  • Model Selection                  │
│  • Skill Loading                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Context Storage                │
│  agents/    skills/    modes/       │
│  9 active   42 skills  3 active     │
│  65 inactive           4 inactive   │
└─────────────────────────────────────┘
```

---

## Performance Metrics

### Token Efficiency

| Agent | Without Skills | With Skills | Savings |
|-------|---------------|-------------|---------|
| backend-architect | 8,000 | 4,800 | 40% |
| kubernetes-architect | 7,500 | 4,500 | 40% |
| security-auditor | 6,800 | 4,500 | 34% |

**Average Savings**: 35-40%

### Cost Optimization

| Scenario | All Sonnet | Hybrid | Savings |
|----------|-----------|--------|---------|
| Per 1M tokens | $15.00 | $4.76 | 68% |
| 1000 tasks/day | $15,000 | $4,760 | 68% |

### Latency

| Agent Type | Haiku P95 | Sonnet P95 | Improvement |
|------------|-----------|------------|-------------|
| Code Gen | 1.2s | 4.8s | 4x faster |
| Tests | 0.8s | 3.2s | 4x faster |
| IaC | 1.0s | 3.5s | 3.5x faster |

---

## Getting Help

### Documentation

- **Architecture**: System design, patterns, extension points
- **Agents**: Complete catalog with dependencies
- **Skills**: Progressive disclosure system
- **Model Optimization**: Cost and performance strategy

### CLI Help
```bash
claude-ctx --help
claude-ctx agent --help
claude-ctx skills --help
claude-ctx init --help
```

### Examples

See [~/agents](https://github.com/wshobson/agents) for:
- 63 granular plugins
- 85 agent examples
- 47 skill implementations
- Multi-agent orchestration patterns

---

## Roadmap

All planned phases for skill development and integration are now **COMPLETED**. The framework supports a wide array of skills, including those for architecture, infrastructure, development, security, and collaboration. The total number of available skills has significantly expanded, enhancing the system's overall capabilities.

---

## Contributing

### Adding Agents

1. Research clear responsibility
2. Define dependencies and workflows
3. Create agent .md with frontmatter
4. Validate: `claude-ctx agent validate`
5. Document in guides/agents.md
6. Assign model (Haiku/Sonnet)

### Creating Skills

1. Identify 1000+ token knowledge chunk
2. Create skills/skill-name/SKILL.md
3. Write frontmatter with triggers
4. Structure with progressive tiers
5. Link to agent frontmatter
6. Validate: `claude-ctx skills validate`
7. Document in guides/skills.md

### Documentation Updates

- Keep guides/development/architecture.md aligned with system changes
- Update guides/agents.md when adding/modifying agents
- Update guides/skills.md when adding skills
- Include examples and use cases

---

## Resources

### Internal
- [Main README](../../README.md) - Project overview
- [Skills README](../../skills/README.md) - Skill integration guide
- [CLI Source](../../claude_ctx_py/) - Python CLI implementation

### External
- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Agent Skills Specification](https://github.com/anthropics/skills/blob/main/agent_skills_spec.md)
- [~/agents Reference](https://github.com/wshobson/agents)
- [Anthropic Model Documentation](https://docs.anthropic.com/en/docs/models-overview)

---

## License

MIT License - see [LICENSE](../../LICENSE) file for details.
