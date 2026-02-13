# cortex Documentation

Comprehensive documentation for the cortex context management framework.

## 📐 Architecture Documentation

**NEW**: Comprehensive visual documentation of the three-layer system!

- **[Architecture Diagrams](reference/architecture/architecture-diagrams.md)** - 10+ Mermaid diagrams showing system architecture, flows, and integration patterns
- **[Quick Reference](reference/architecture/quick-reference.md)** - One-page cheat sheet for daily use (commands, modes, workflows)
- **[Visual Summary](reference/architecture/VISUAL_SUMMARY.txt)** - Beautiful ASCII art diagram for terminal viewing
- **[Diagrams Guide](reference/architecture/DIAGRAMS_README.md)** - How to use, read, and maintain all diagrams

**After installation**: These docs are available at `~/.cortex/docs/`

**Quick view**:

```bash
cat ~/.cortex/docs/VISUAL_SUMMARY.txt       # Terminal-friendly overview
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

- 29 agents organized by category
- Model assignments (Opus/Haiku)
- Dependencies and relationships
- Use cases and activation patterns

**[Agent Skills](./guides/skills.md)** - Progressive disclosure system

- 100+ available skills
- Creating new skills with templates
- Token efficiency metrics and activation guidance
- Integration with agents

**[Skill Recommendation & Review Learning](./guides/development/skill-recommendation-system.md)** - Self-improving feedback loop

- Four recommendation strategies (semantic, rule-based, agent-based, pattern-based)
- Review outcome parsing and skill learning
- CLI commands for recommendations and feedback
- Review gate integration

**[Flags Management](./guides/FLAGS_MANAGEMENT.md)** - Context flag modules

- 22 modular flag packs in `flags/`
- Toggle via `FLAGS.md` or the TUI Flag Explorer
- Supports per-project customization

**[Model Optimization](./guides/development/model-optimization.md)** - Cost and performance strategy

- Haiku vs Sonnet assignment criteria
- Hybrid orchestration patterns
- Cost optimization guidance
- Migration plan and monitoring

---

## Quick Start

### Understanding cortex

cortex is a context orchestration framework that provides:

1. **On-Demand Loading**: Agents load only when triggered
2. **Progressive Disclosure**: Skills load knowledge in tiers
3. **Dependency Resolution**: Automatic agent dependency management
4. **Hybrid Execution**: Strategic Haiku/Sonnet model assignment
5. **Workflow Automation**: Multi-phase structured workflows

### Key Concepts

**Agents**: Specialized AI agents with focused responsibilities (29 total)

- Auto-activation supported via `agents/triggers.yaml`
- Activate/deactivate in the TUI or CLI
- Each can declare dependencies, workflows, and metrics

**Skills**: Modular knowledge packages that load progressively

- 100+ available skills
- Shared across multiple agents
- Progressive disclosure keeps context lean

**Flags**: Context modules toggled via `FLAGS.md`

- 22 flag files under `flags/`
- Add/remove `@flags/*.md` lines to enable/disable

**Modes**: Behavioral presets that shape workflow defaults

- Architect, Brainstorming, Security Audit, Super Saiyan, Token Efficiency, and more

**Profiles**: Saved configurations of agents/modes/rules

- 5 enhanced profiles under `profiles/enhanced`
- Quick environment setup

---

## Common Workflows

### Code Quality Pass

```
code-reviewer (Sonnet) → Review changes
  ↓
security-auditor (Sonnet) → Threat sweep
  ↓
debugger (Sonnet) → Root-cause analysis
  ↓
python-pro / typescript-pro (Haiku) → Implement fix
```

### Infrastructure Setup

```
cloud-architect (Sonnet) → Design infrastructure
  ↓
kubernetes-architect (Haiku) → K8s architecture
  ↓
docs-architect (Haiku) → Document infrastructure
```

### Documentation & Enablement

```
mermaid-expert (Haiku) → System diagrams
  ↓
tutorial-engineer (Haiku) → Hands-on walkthroughs
  ↓
learning-guide (Haiku) → Learning paths + explanations
```

---

## CLI Quick Reference

### Agent Management

```bash
# List agents
cortex agent list

# Show agent details
cortex agent deps backend-architect

# Activate/deactivate
cortex agent activate backend-architect
cortex agent deactivate backend-architect

# Dependency graph
cortex agent graph --export deps.md

# Validate agents
cortex agent validate --all
```

### Skill Management

```bash
# List skills
cortex skills list

# Show skill details
cortex skills info api-design-patterns

# Validate skills
cortex skills validate --all
```

### Project Initialization

```bash
# Auto-detect project
cortex init detect

# Interactive wizard
cortex init wizard

# Show current config
cortex init status

# Load profile
cortex profile backend
```

### Status

```bash
# Show all status
cortex status

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
│         cortex CLI              │
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
│  29 total   100+ skills 9 modes     │
│  flags/     rules/     profiles/    │
│  22 flags   6 rules    5 profiles   │
└─────────────────────────────────────┘

```

---

## Performance Notes

- Model selection is configured per agent (Haiku or Sonnet) in agent frontmatter.
- Skills load on demand to keep default context lightweight.
- See `guides/development/model-optimization.md` for tuning guidance and deeper analysis.

---

## Getting Help

### Documentation

- **Architecture**: System design, patterns, extension points
- **Agents**: Complete catalog with dependencies
- **Skills**: Progressive disclosure system
- **Model Optimization**: Cost and performance strategy

### CLI Help
```bash
cortex --help
cortex agent --help
cortex skills --help
cortex init --help
```

### Examples

Browse the local catalog for up-to-date examples:

- `agents/` for current agent definitions
- `skills/` for skill packs and templates
- `commands/` for slash command specs

---

## Roadmap

All planned phases for skill development and integration are now **COMPLETED**. The framework supports a wide array of skills, including those for architecture, infrastructure, development, security, and collaboration. The total number of available skills has significantly expanded, enhancing the system's overall capabilities.

---

## Contributing

### Adding Agents

1. Research clear responsibility
2. Define dependencies and workflows
3. Create agent .md with frontmatter
4. Validate: `cortex agent validate`
5. Document in guides/agents.md
6. Assign model (Haiku/Sonnet)

### Creating Skills

1. Identify 1000+ token knowledge chunk
2. Create skills/skill-name/SKILL.md
3. Write frontmatter with triggers
4. Structure with progressive tiers
5. Link to agent frontmatter
6. Validate: `cortex skills validate`
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
