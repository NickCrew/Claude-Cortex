# cortex Documentation

Comprehensive documentation for the cortex context management framework.

## Architecture Documentation

- **[Architecture Overview](architecture/README.md)** - System design and module map
- **[Master Architecture](architecture/MASTER_ARCHITECTURE.md)** - Comprehensive technical reference
- **[Skill Recommendation Engine](architecture/skill-recommendation-engine.md)** - Two-layer recommendation pipeline
- **[Architecture Diagrams](reference/architecture/architecture-diagrams.md)** - Mermaid diagrams showing system architecture and flows
- **[Quick Reference](architecture/quick-reference.md)** - One-page cheat sheet for daily use
- **[Visual Summary](architecture/VISUAL_SUMMARY.txt)** - ASCII art diagram for terminal viewing
- **[Diagrams Guide](reference/architecture/DIAGRAMS_README.md)** - How to use and maintain diagrams

---

## Documentation Map

### Core Guides

**[Architecture](./guides/development/architecture.md)** - System design and technical architecture

- Component overview and system architecture
- Dependency management and workflow orchestration
- Performance characteristics and design patterns
- Extension points and future enhancements

**[Agent Skills](./guides/skills.md)** - Progressive disclosure system

- 124 available skills
- Creating new skills with templates
- Token efficiency metrics and activation guidance
- Integration with agents

**[Skill Recommendation & Review Learning](./guides/development/skill-recommendation-system.md)** - Self-improving feedback loop

- Four recommendation strategies (semantic, rule-based, agent-based, pattern-based)
- Review outcome parsing and skill learning
- CLI commands for recommendations and feedback
- Review gate integration

**[Model Optimization](./guides/development/model-optimization.md)** - Cost and performance strategy

- Haiku vs Sonnet assignment criteria
- Hybrid orchestration patterns
- Cost optimization guidance

---

## Quick Start

### Understanding cortex

cortex is a context orchestration framework that provides:

1. **On-Demand Loading**: Agents load only when triggered
2. **Progressive Disclosure**: Skills load knowledge in tiers
3. **Dependency Resolution**: Automatic agent dependency management
4. **Skill Recommendations**: Two-layer pipeline surfaces relevant skills per prompt
5. **Workflow Automation**: Multi-phase structured workflows

### Key Concepts

**Agents**: Specialized AI agents with focused responsibilities (28 total)

- Activate/deactivate in the TUI or CLI
- Each can declare dependencies, workflows, and metrics
- Context-aware recommendations via `cortex ai recommend`

**Skills**: Modular knowledge packages that load progressively

- 124 available skills
- Shared across multiple agents
- Progressive disclosure keeps context lean

**Hooks**: Automation scripts triggered by Claude Code events

- skill_auto_suggester, secret_scan, audit, and more

---

## Common Workflows

### Code Quality Pass

```
code-reviewer → Review changes
  ↓
security-auditor → Threat sweep
  ↓
debugger → Root-cause analysis
  ↓
python-pro / typescript-pro → Implement fix
```

### Infrastructure Setup

```
cloud-architect → Design infrastructure
  ↓
kubernetes-architect → K8s architecture
  ↓
docs-architect → Document infrastructure
```

### Frontend Development

```
react-specialist → Component architecture
  ↓
frontend-optimizer → Performance optimization
  ↓
ui-ux-designer → Design review
```

---

## CLI Quick Reference

### Agent Management

```bash
# List agents
cortex agent list

# Activate/deactivate
cortex agent activate cloud-architect
cortex agent deactivate cloud-architect

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

### Setup & Scope

```bash
# Link bundled assets into ~/.claude
cortex install link

# Install completions/manpages (optional)
cortex install post

# Use project-local scope
cortex --scope project status
```

### Status

```bash
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
│         cortex CLI                  │
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
│  • Skill Recommendation             │
│  • Model Selection                  │
│  • Skill Loading                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Context Storage                │
│  agents/    skills/    rules/       │
│  28 agents  124 skills              │
│  hooks/     commands/               │
└─────────────────────────────────────┘
```

---

## Performance Notes

- Model selection is configured per agent in agent frontmatter.
- Skills load on demand to keep default context lightweight.
- See `guides/development/model-optimization.md` for tuning guidance.

---

## Getting Help

### Documentation

- **Architecture**: System design, patterns, extension points
- **Skills**: Progressive disclosure system, recommendation engine
- **Model Optimization**: Cost and performance strategy

### CLI Help

```bash
cortex --help
cortex agent --help
cortex skills --help
cortex install --help
```

### Examples

Browse the local catalog for up-to-date examples:

- `agents/` for current agent definitions
- `skills/` for skill packs and templates
- `commands/` for slash command specs

---

## Contributing

### Adding Agents

1. Research clear responsibility
2. Define dependencies and workflows
3. Create agent `.md` with YAML frontmatter in `agents/`
4. Add dependencies to `dependencies.map`
5. Validate: `cortex agent validate`

### Creating Skills

1. Identify 1000+ token knowledge chunk
2. Create `skills/skill-name/SKILL.md`
3. Write frontmatter with triggers
4. Structure with progressive tiers
5. Validate: `cortex skills validate`
6. Update `guides/skills.md` when adding skills

### Documentation Updates

- Keep `guides/development/architecture.md` aligned with system changes
- Update `guides/skills.md` when adding skills
- Include examples and use cases

---

## Resources

### Internal

- [Main README](../README.md) - Project overview
- [Documentation Navigator](NAVIGATOR.md) - Full docs map by topic and audience
- [CLI Source](../claude_ctx_py/) - Python CLI implementation

### External

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Anthropic Model Documentation](https://docs.anthropic.com/en/docs/about-claude/models)

---

## License

MIT License - see [LICENSE](../LICENSE) file for details.
