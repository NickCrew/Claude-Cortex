---
layout: default
title: Overview
nav_order: 1
permalink: /
---

# Claude CTX Plugin - Documentation Index

> Version 0.1.0 · Last updated 2025-10-17

<div class="hero">
  <div class="hero__copy">
    <h2>Claude CTX keeps your agents, commands &amp; workflows in perfect sync.</h2>
    <p>
      Activate a fully curated context stack for Claude Code: purpose-built slash commands,
      dependency-aware agents, behavioural modes, and a Python CLI that all speak the same
      language. Configure once, deploy everywhere.
    </p>

    <div class="hero__cta">
      <a href="https://github.com/NickCrew/claude-ctx-plugin" target="_blank" rel="noopener">
        View on GitHub →
      </a>
      <a class="secondary" href="#installation">Install the plugin</a>
    </div>

    <div class="hero__pills">
      <span>Claude Code Native</span>
      <span>Python CLI</span>
      <span>MCP Ready</span>
      <span>Blue Ops Theme</span>
    </div>
  </div>
  <div class="hero__visual">
    <img src="{{ '/assets/images/hero.png' | relative_url }}" alt="Claude CTX blueprint" />
  </div>
</div>

## Overview

The Claude CTX Plugin is a comprehensive context management toolkit packaged as a Claude Code plugin. It provides curated agents, slash commands, behavioral modes, rules, and workflow orchestration for systematic software development.

<div class="metrics-row">
  <div class="metric-box">
    <div class="metric-value">78</div>
    <div class="metric-label">Total Agents</div>
    <div class="metric-sublabel">27 Sonnet • 31 Haiku • 9 Context</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">68%</div>
    <div class="metric-label">Cost Savings</div>
    <div class="metric-sublabel">Hybrid model optimization</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">30-50%</div>
    <div class="metric-label">Token Reduction</div>
    <div class="metric-sublabel">Progressive skill disclosure</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">20</div>
    <div class="metric-label">Skills Available</div>
    <div class="metric-sublabel">Phase 4 Complete</div>
  </div>
</div>

### Quick Links

<div class="quick-links">
  <a href="getting-started.html">Getting Started</a>
  <a href="commands.html">Command Reference</a>
  <a href="#installation">Install Plugin</a>
  <a href="#project-structure">Project Structure</a>
  <a href="#data-directory-overrides">CLI Overrides</a>
</div>

---

## Project Structure

```
claude-ctx-plugin/
├── commands/           # Slash command definitions (37 commands across 11 categories)
│   ├── analyze/       # Code analysis, security scanning, troubleshooting
│   ├── deploy/        # Release preparation and deployment
│   ├── design/        # System design and workflow planning
│   ├── dev/           # Development tasks (build, test, review, git, implement)
│   ├── docs/          # Documentation generation and indexing
│   ├── orchestrate/   # Multi-agent task orchestration
│   ├── quality/       # Code quality improvement and cleanup
│   ├── reasoning/     # Dynamic reasoning depth control
│   ├── session/       # Session persistence and reflection
│   ├── test/          # Test generation
│   └── tools/         # Tool selection and optimization
│
├── agents/            # Active specialized agents (11 agents)
│   ├── cloud-architect.md
│   ├── code-reviewer.md
│   ├── debugger.md
│   ├── deployment-engineer.md
│   ├── kubernetes-architect.md
│   ├── python-pro.md
│   ├── security-auditor.md
│   ├── terraform-specialist.md
│   ├── typescript-pro.md
│   ├── dependencies.map         # Agent dependency graph
│   └── triggers.yaml            # Agent activation triggers
│
├── agents-disabled/   # Disabled agents library (65 agents available)
│
├── modes/             # Active behavioral modes
│   └── Task_Management.md
│
├── modes-inactive/    # Inactive modes (can be activated as needed)
│   ├── Brainstorming.md
│   ├── Introspection.md
│   ├── Orchestration.md
│   └── Token_Efficiency.md
│
├── rules/             # Reusable rule sets
│   ├── workflow-rules.md       # Git workflow, task patterns
│   ├── quality-rules.md        # Code organization, failure investigation
│   └── efficiency-rules.md     # Tool optimization, workspace hygiene
│
├── profiles/          # Profile templates for different workflows
│   ├── enhanced/
│   └── templates/
│
├── workflows/         # Multi-agent workflow definitions
│   ├── bug-fix.yaml
│   ├── feature-development.yaml
│   ├── performance-optimize.yaml
│   └── security-audit.yaml
│
├── scenarios/         # Scenario-based orchestration definitions
│
├── claude_ctx_py/     # Python CLI implementation
│   ├── cli.py         # CLI entry point
│   ├── core.py        # Core functionality
│   └── init_cmds.py   # Command initialization
│
├── schema/            # Validation schemas
├── scripts/           # Helper scripts
│
├── CLAUDE.md          # Framework entry point
├── FLAGS.md           # Behavioral flags and execution modes
├── RULES.md           # Core behavioral rules
├── README.md          # Project overview
└── pyproject.toml     # Python package configuration
```


### Key Capabilities

<div class="feature-grid">
  <div class="feature-card">
    <h3>Turnkey Plugin Stack</h3>
    <p>Ships with pre-wired agents, rules, modes, and workflows so Claude Code starts with a curated context from the first prompt.</p>
  </div>
  <div class="feature-card">
    <h3>Python CLI Included</h3>
    <p>An installable `claude-ctx` CLI mirrors the plugin structure, enabling scripts, CI checks, and local automation.</p>
  </div>
  <div class="feature-card">
    <h3>MCP &amp; Hook Ready</h3>
    <p>Designed to plug in Model Context Protocol servers and command hooks for custom toolchains or compliance gates.</p>
  </div>
  <div class="feature-card">
    <h3>Blue Ops UX</h3>
    <p>Gradients, iconography, and documentation tuned to keep designers, developers, and operators aligned.</p>
  </div>
</div>

---

## Installation

### Via Claude Code Plugin System

1. Add the marketplace that references this repository:
   ```bash
   # See companion project: NickCrew/claude-marketplace
   ```

2. Install the plugin:
   ```bash
   /plugin install claude-ctx@<marketplace-name>
   ```

3. Restart Claude Code to load commands and agents

### Via Python CLI

**Quick Install (Recommended):**
```bash
# Install everything (package, completions, manpage)
./scripts/install.sh

# Or use make
make install
```

**Manual Installation:**
```bash
# Install package (editable installs supported)
python3 -m pip install -e ".[dev]"

# Verify installation
claude-ctx --version

# View documentation
man claude-ctx

# List available modes
claude-ctx mode list

# Generate dependency map
claude-ctx agent graph --export dependency-map.md
```

**What Gets Installed:**
- Python package (`claude-ctx` command)
- Shell completions (bash/zsh/fish)
- Manpage (`man claude-ctx`)
- Development dependencies (pytest, mypy, black)

For more detailed setup guidance (including shell completion and CLI overrides) see [Getting Started](getting-started.md).

---

## Data Directory Overrides

The CLI resolves its workspace using the following precedence:

1. `CLAUDE_CTX_HOME`
2. `CLAUDE_PLUGIN_ROOT` (automatically set when commands run inside Claude Code)
3. `~/.claude`

Examples:

```bash
# Use the plugin cache that Claude Code maintains
export CLAUDE_CTX_HOME="$HOME/.claude/plugins/cache/claude-ctx"

# Or target a local checkout of this repository
export CLAUDE_CTX_HOME="$HOME/Developer/personal/claude-ctx-plugin"

claude-ctx mode status
```

Once exported (for example in `~/.zshrc`), both the CLI and Claude Code share a single source of truth for agents, commands, and workflows.

---

## Core Systems

### 1. Command System
**Location**: `commands/`
**Count**: 34 slash commands across 10 categories

Commands provide curated behavioral prompts for specific development tasks. Each command includes:
- Trigger conditions for automatic activation
- Usage patterns and examples
- MCP integration specifications
- Tool coordination patterns
- Success criteria and boundaries

**Categories**:
- `/analyze` - Code analysis, security, troubleshooting (6 commands)
- `/deploy` - Release preparation (1 command)
- `/design` - System design, workflow planning (2 commands)
- `/dev` - Development tasks (6 commands)
- `/docs` - Documentation generation (2 commands)
- `/orchestrate` - Multi-agent orchestration (3 commands)
- `/quality` - Code quality (2 commands)
- `/session` - Session management (3 commands)
- `/test` - Test generation (1 command)
- `/tools` - Tool selection (1 command)

**Reference**: [Command Documentation](COMMANDS.md)

---

### 2. Agent System
**Location**: `agents/` and `agents-disabled/`
**Active Agents**: 11 | **Available**: 65

Agents are specialized personas with domain expertise and specific capabilities. The system includes:
- **Dependency Management**: `dependencies.map` tracks agent relationships
- **Trigger System**: `triggers.yaml` defines automatic activation patterns
- **Activation Control**: Move between `agents/` and `agents-disabled/` to control availability

**Active Agents**:
- `cloud-architect` - Cloud infrastructure design
- `code-reviewer` - Code quality analysis
- `debugger` - Issue diagnosis and resolution
- `deployment-engineer` - Release engineering
- `kubernetes-architect` - K8s orchestration
- `python-pro` - Python expertise
- `security-auditor` - Security assessment
- `terraform-specialist` - Infrastructure as code
- `typescript-pro` - TypeScript expertise

**Reference**: [Agent Documentation](AGENTS.md)

---

### 3. Mode System
**Location**: `modes/` and `modes-inactive/`
**Active Modes**: 1 | **Available**: 4

Modes are opinionated context modules that toggle workflow defaults and behavioral patterns.

**Active**:
- `Task_Management` - Multi-step task orchestration

**Available**:
- `Brainstorming` - Collaborative discovery
- `Introspection` - Meta-cognitive analysis
- `Orchestration` - Multi-tool optimization
- `Token_Efficiency` - Symbol-enhanced communication

**Activation**: Move mode files between `modes/` and `modes-inactive/` or use flags

---

### 4. Flag System
**Location**: `FLAGS.md`

Behavioral flags enable specific execution modes and tool selection patterns.

**Categories**:
- **Mode Activation**: `--brainstorm`, `--introspect`, `--task-manage`, `--orchestrate`
- **MCP Servers**: `--c7`, `--seq`, `--serena`, `--magic`, `--morph`, `--play`
- **Analysis Depth**: `--think`, `--think-hard`, `--ultrathink`
- **Execution Control**: `--delegate`, `--loop`, `--validate`, `--safe-mode`
- **Output Optimization**: `--uc`, `--scope`, `--focus`

---

### 5. Rule System
**Location**: `rules/`

Reusable rule sets that define behavioral constraints and best practices.

**Rule Sets**:
- `workflow-rules.md` - Task patterns, git workflow, implementation completeness
- `quality-rules.md` - Code organization, naming conventions, failure investigation
- `efficiency-rules.md` - Tool optimization, parallel operations, workspace hygiene

**Priority System**:
- 🔴 CRITICAL - Security, data safety (never compromise)
- 🟡 IMPORTANT - Quality, maintainability (strong preference)
- 🟢 RECOMMENDED - Optimization, style (apply when practical)

---

### 6. Workflow System
**Location**: `workflows/`

Pre-defined multi-agent sequences for common development tasks.

**Available Workflows**:
- `feature-development.yaml` - Complete feature implementation workflow
- `bug-fix.yaml` - Systematic bug resolution
- `security-audit.yaml` - Comprehensive security assessment
- `performance-optimize.yaml` - Performance analysis and optimization

**Reference**: [Workflow Documentation](workflows/README.md)

---

### 7. Python CLI
**Location**: `claude_ctx_py/`
**Entry Point**: `claude-ctx`

Python CLI for managing context components outside of Claude Code.

**Capabilities**:
- Mode management (list, activate, deactivate)
- Agent dependency visualization
- Command execution
- Context validation

**Reference**: [CLI Documentation](CLI.md)

---

## Deep Dive Documentation

Comprehensive guides to claude-ctx architecture, optimization strategies, and advanced patterns.

<div class="doc-grid">
  <a href="architecture.html" class="doc-card">
    <h3>Architecture & Design</h3>
    <p>System architecture, design patterns, and component interactions. Explore dependency injection, progressive disclosure, lazy loading, and extension points.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>17KB guide</span>
      <span>Core systems</span>
    </div>
  </a>

  <a href="agents.html" class="doc-card">
    <h3>Agent Catalog</h3>
    <p>Complete catalog of 78 specialized agents organized by category. Includes model assignments, dependencies, workflows, and activation criteria for all agents.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>23KB reference</span>
      <span>78 agents</span>
    </div>
  </a>

  <a href="skills.html" class="doc-card">
    <h3>Agent Skills</h3>
    <p>Progressive disclosure architecture for specialized knowledge. Learn how to create skills, integrate with agents, and achieve 30-50% token reduction.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>16KB guide</span>
      <span>2 skills active</span>
    </div>
  </a>

  <a href="model-optimization.html" class="doc-card">
    <h3>Model Optimization</h3>
    <p>Strategic Haiku vs Sonnet assignment for 68% cost savings. Hybrid orchestration patterns, decision matrix, and performance benchmarks.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>13KB strategy</span>
      <span>68% savings</span>
    </div>
  </a>

  <a href="phase4-summary.html" class="doc-card">
    <h3>Phase 4 Features</h3>
    <p>Complete implementation of skill composition, semantic versioning, community integration, and effectiveness analytics. Production-ready enterprise features.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>32KB reference</span>
      <span>4 feature sets</span>
    </div>
  </a>

  <a href="quality-improvements.html" class="doc-card">
    <h3>Quality & DevOps</h3>
    <p>Testing infrastructure with 150+ tests, code refactoring, error handling improvements, installation automation, and CI/CD pipeline. Grade improved from B+ to A.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>Production ready</span>
      <span>95/100 score</span>
    </div>
  </a>
</div>

---

## Framework Entry Points

### CLAUDE.md
Primary framework entry point that loads:
- Core framework (FLAGS.md, PRINCIPLES.md, RULES.md)
- Workflow rules (automatic for all development tasks)
- Conditional rules (loaded as needed)
- Active behavioral modes
- MCP documentation

### PRINCIPLES.md
Software engineering principles and philosophy:
- Task-First Approach: Understand → Plan → Execute → Validate
- Evidence-Based Reasoning
- Parallel Thinking
- SOLID principles
- Systems Thinking
- Decision Framework

### RULES.md
Core behavioral rules with priority system:
- Scope Discipline
- Professional Honesty
- Safety Rules
- Temporal Awareness

---

## Configuration Files

### Plugin Manifest
**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "claude-ctx",
  "version": "0.1.0",
  "description": "Context orchestration plugin",
  "commands": ["./commands"]
}
```

### Python Package
**File**: `pyproject.toml`

```toml
[project]
name = "claude-ctx-py"
version = "0.1.0"
requires-python = ">=3.9"

[project.scripts]
claude-ctx = "claude_ctx_py.cli:main"
```

---

## Development Workflows

### Feature Development
1. Create feature branch (`git checkout -b feature/name`)
2. Use `/design:workflow` to plan implementation
3. Use `/dev:implement` with appropriate persona flags
4. Use `/dev:code-review` for quality validation
5. Use `/test:generate-tests` for test coverage
6. Use `/dev:git` for commit with semantic message
7. Use `/deploy:prepare-release` for deployment preparation

### Bug Fixing
1. Use `/analyze:troubleshoot` for diagnosis
2. Use `/dev:implement` to fix issue
3. Use `/test:generate-tests` for regression coverage
4. Use `/dev:code-review` for validation
5. Use `/dev:git` to commit fix

### Code Quality
1. Use `/analyze:code` for quality assessment
2. Use `/quality:improve` for systematic improvements
3. Use `/quality:cleanup` for dead code removal
4. Use `/dev:code-review` for validation

---

## MCP Integration

The plugin integrates with Model Context Protocol servers for enhanced capabilities:

### Context7
- **Purpose**: Official library documentation lookup
- **Flag**: `--c7` or `--context7`
- **Use For**: Framework patterns, API documentation, version-specific implementations

### Sequential
- **Purpose**: Multi-step reasoning and analysis
- **Flag**: `--seq` or `--sequential`
- **Use For**: Complex debugging, system design, hypothesis testing

### Serena
- **Purpose**: Symbol operations and session persistence
- **Flag**: `--serena`
- **Use For**: Large codebase navigation, project memory, semantic understanding

---

## Best Practices

### Command Usage
1. Use namespace prefixes (`/dev:`, `/test:`, etc.)
2. Specify scope with flags (`--scope file|module|project`)
3. Focus analysis with `--focus` flags
4. Enable validation for critical operations (`--validate`)

### Agent Coordination
1. Let dependency system manage agent activation
2. Use `triggers.yaml` for automatic agent selection
3. Compose multiple agents for complex tasks
4. Review `dependencies.map` for orchestration patterns

### Mode Management
1. Activate modes based on task complexity
2. Use `Task_Management` for multi-step operations
3. Enable `Token_Efficiency` for large operations
4. Combine modes for optimal behavior

### Flag Optimization
1. Use `--safe-mode` for production operations
2. Apply `--think-hard` for architectural decisions
3. Enable `--delegate` for large-scale changes
4. Use `--uc` for token efficiency under pressure

---

## Troubleshooting

### Commands Not Loading
1. Verify plugin installation: `/plugin list`
2. Check plugin manifest: `.claude-plugin/plugin.json`
3. Restart Claude Code
4. Validate command syntax in markdown files

### Agent Not Activating
1. Check agent location (`agents/` vs `agents-disabled/`)
2. Review `triggers.yaml` for activation conditions
3. Verify dependencies in `dependencies.map`
4. Manually invoke with `/agent activate <name>`

### CLI Issues
1. Verify installation: `python3 -m pip show claude-ctx-py`
2. Check Python version: `python3 --version` (>=3.9 required)
3. Reinstall: `python3 -m pip install --force-reinstall .`

---

## Contributing

### Adding Commands
1. Choose appropriate namespace under `commands/`
2. Create markdown file following template structure
3. Add to namespace README.md
4. Update command count in this index

### Creating Agents
1. Create markdown file in `agents-disabled/`
2. Define triggers in `triggers.yaml`
3. Add dependencies to `dependencies.map`
4. Move to `agents/` when ready for activation

### Defining Workflows
1. Create YAML file in `workflows/`
2. Define trigger conditions and steps
3. Specify agent sequence and success criteria
4. Update workflows/README.md

---

## References

### Internal Documentation
- [Architecture Guide](architecture.html) - System design and patterns
- [Agent Catalog](agents.html) - Complete agent reference with 78 agents
- [Agent Skills Guide](skills.html) - Progressive disclosure and token optimization
- [Model Optimization](model-optimization.html) - Haiku vs Sonnet strategy
- [Command Reference](commands.html) - Complete command catalog
- [Getting Started](getting-started.html) - Installation and setup

### External Resources
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Plugin Development Guide](https://docs.claude.com/claude-code/plugins)
- [MCP Specification](https://modelcontextprotocol.io)

---

## Version History

### 0.1.0 (2025-10-17)
- Initial plugin release
- 34 slash commands across 10 categories
- 11 active agents, 65 total available
- 4 behavioral modes
- 4 pre-defined workflows
- Python CLI for context management
- Complete documentation system

---

## Support

**Repository**: [github.com/NickCrew/claude-ctx-plugin](https://github.com/NickCrew/claude-ctx-plugin)

**Issues**: [Report a bug or request a feature](https://github.com/NickCrew/claude-ctx-plugin/issues)

**Marketplace**: [claude-marketplace](https://github.com/NickCrew/claude-marketplace)

---

*This documentation was generated using `/docs:index` command*
