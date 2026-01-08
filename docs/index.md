---
layout: default
title: Overview
nav_order: 1
permalink: /
---

# Cortex - Documentation Index

> Version 2.0.0 · Last updated January 8, 2026

<div class="hero">
  <div class="hero__copy">
    <h2>Cortex keeps your agents, commands &amp; workflows in perfect sync.</h2>
    <p>
      Activate a fully curated context stack for Claude Code: purpose-built slash commands,
      dependency-aware agents, behavioural modes, and a Python CLI that all speak the same
      language. Configure once, deploy everywhere.
    </p>

    <div class="hero__cta">
      <a href="https://github.com/NickCrew/claude-cortex" target="_blank" rel="noopener">
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
    <img src="{{ '/assets/images/hero.png' | relative_url }}" alt="Cortex blueprint" />
  </div>
</div>

## Overview

Cortex is a comprehensive context management toolkit packaged as a Claude Code plugin. It provides curated agents, slash commands, behavioral modes, flags, rules, profiles, workflows, and scenarios for systematic software development.

<div class="metrics-row">
  <div class="metric-box">
    <div class="metric-value">107</div>
    <div class="metric-label">Total Agents</div>
    <div class="metric-sublabel">19 active • 88 inactive</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">49</div>
    <div class="metric-label">Slash Commands</div>
    <div class="metric-sublabel">Analyze • Dev • Docs • Orchestrate</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">22</div>
    <div class="metric-label">Flag Modules</div>
    <div class="metric-sublabel">Toggle via FLAGS.md</div>
  </div>
  <div class="metric-box">
    <div class="metric-value">54</div>
    <div class="metric-label">Skills Available</div>
    <div class="metric-sublabel">Progressive disclosure packs</div>
  </div>
</div>

### Quick Links

<div class="quick-links">
  <a href="tutorials/getting-started-tui/">→ TUI Tutorial</a>
  <a href="guides/getting-started.html">Getting Started</a>
  <a href="guides/commands.html">Command Reference</a>
  <a href="guides/modes.html">Modes</a>
  <a href="guides/asset-manager.html">Asset Manager</a>
  <a href="guides/worktrees.html">Worktree Manager</a>
  <a href="guides/FLAGS_MANAGEMENT.html">Flags Management</a>
  <a href="#presentations">▶ Presentations</a>
  <a href="#installation">Install Plugin</a>
  <a href="#ai-intelligence">AI Intelligence</a>
  <a href="#collaboration">Collaboration Flow</a>
  <a href="#project-structure">Project Structure</a>
</div>

---

## ▶ Presentation Decks {#presentations}

Reveal.js presentations for demos, enablement sessions, and executive briefings.

<div class="doc-grid">
  <a href="{{ '/presentations/cortex-overview.html' | relative_url }}" class="doc-card" target="_blank">
    <h3>→ Cortex Intro Overview</h3>
    <p>High-level story of the platform: AI intelligence, watch mode, asset manager, visual excellence, and multi-LLM consult. Great for quick introductions.</p>
    <p class="muted"><strong>Topics:</strong> AI Intelligence • Watch Mode • Asset Manager • Visual Excellence • Multi-LLM Consult • Recent Improvements</p>
    <span class="doc-card__arrow">Launch →</span>
    <div class="doc-card__meta">
      <span>9 slides</span>
      <span>Screenshots included</span>
    </div>
  </a>

  <a href="{{ '/presentations/cortex-technical-deep-dive.html' | relative_url }}" class="doc-card" target="_blank">
    <h3>→ Technical Deep Dive</h3>
    <p>Deep focus on activation, recommendations, intelligence signals, watch mode loops, skill ratings, and plugin/CLI integration.</p>
    <p class="muted"><strong>Topics:</strong> Activation Pipeline • Intelligence Signals • Watch Mode • Skill Ratings • Install Flow • Plugin + CLI</p>
    <span class="doc-card__arrow">Launch →</span>
    <div class="doc-card__meta">
      <span>13 slides</span>
      <span>Technical focus</span>
    </div>
  </a>

  <a href="{{ '/presentations/cortex-executive-roadmap.html' | relative_url }}" class="doc-card" target="_blank">
    <h3>→ Executive Overview & Roadmap</h3>
    <p>Executive-friendly narrative with capability highlights, recent improvements, adoption plan, and phased roadmap.</p>
    <p class="muted"><strong>Topics:</strong> Business Value • Capability Highlights • Recent Improvements • Roadmap • Adoption • Risks</p>
    <span class="doc-card__arrow">Launch →</span>
    <div class="doc-card__meta">
      <span>9 slides</span>
      <span>Strategy + roadmap</span>
    </div>
  </a>

  <a href="{{ '/presentations/tui-showcase.html' | relative_url }}" class="doc-card" target="_blank">
    <h3>▶ Feature Catalog (TUI + CLI)</h3>
    <p>Comprehensive catalog of every capability, with how-to guidance, docs links, and up-to-date TUI screenshots.</p>
    <p class="muted"><strong>Coverage:</strong> AI Assistant • Watch Mode • Agents • Skills • Command Palette • Slash Commands • Modes • Profiles • Principles • Flags • Workflows • Scenarios • Worktrees • Asset Manager • Hooks • Backups • Memory • MCP • Export • Setup Wizard • Shortcuts • CLI</p>
    <span class="doc-card__arrow">Launch →</span>
    <div class="doc-card__meta">
      <span>26 slides</span>
      <span>Docs-linked catalog</span>
    </div>
  </a>
</div>

<div class="callout" style="margin-top: 1rem;">
  <strong>ℹ How to View:</strong> Open presentations directly in your browser or serve locally with `python3 -m http.server 8080` from the presentations directory. See <a href="{{ '/presentations/README.md' | relative_url }}">presentations/README.md</a> for keyboard controls and customization guide.
</div>

---

## → Tutorials {#tutorials}

Hands-on tutorials to master cortex from beginner to advanced.

<div class="doc-grid">
  <a href="tutorials/getting-started-tui/" class="doc-card">
    <h3>→ Getting Started with Cortex TUI</h3>
    <p>Master the Terminal User Interface in 20-30 minutes. Learn navigation, agent management, workflows, and when to use CLI vs TUI. Perfect for beginners and visual learners.</p>
    <p class="muted"><strong>You'll Learn:</strong> TUI Navigation • Agents & Modes • Skills & Workflows • Command Palette • Export • AI Assistant • MCP Servers • Profiles</p>
    <span class="doc-card__arrow">Start Tutorial →</span>
    <div class="doc-card__meta">
      <span>⏳ 20-30 minutes</span>
      <span>✓ 15+ checkpoints</span>
      <span>→ 60+ examples</span>
    </div>
  </a>
</div>

<div class="callout" style="margin-top: 1rem;">
  <strong>→ New to cortex?</strong> Start with the TUI tutorial above. It includes CLI alternatives for power users and clear markers for advanced features. <a href="tutorials/">View all tutorials →</a>
</div>

---

## → AI Intelligence & Automation {#ai-intelligence}

Stay in Claude Code flow with intelligent, self-managing context and flags-first customization:

<div class="feature-grid">
  <div class="feature-card">
    <h3>ℹ Context-Aware Recommendations</h3>
    <p>Detects project signals and suggests agents/skills with confidence scores.</p>
  </div>
  <div class="feature-card">
    <h3>→ Auto-Activation + Watch Mode</h3>
    <p>Watch mode monitors changes and auto-activates high-confidence agents.</p>
  </div>
  <div class="feature-card">
    <h3>🚩 Flags & Context Packs</h3>
    <p>Enable or disable context modules by adding/removing entries in FLAGS.md.</p>
  </div>
  <div class="feature-card">
    <h3>→ Workflow Orchestration</h3>
    <p>Run workflows and scenarios, then export or share context snapshots.</p>
  </div>
</div>

### Watch Mode - Real-Time Monitoring

```bash
# Start watch mode (foreground, no daemon)
cortex ai watch

# Monitor as you code:
# • Git commits detected
# • Context analyzed instantly
# • Agents auto-activated
# • Statistics tracked

# Press Ctrl+C to stop
```

**Example output:**

```
[10:33:12] 🔍 Context detected: Backend, Auth
  3 files changed

  ℹ Recommendations:
     🔴 security-auditor [AUTO]
        95% - Auth code detected

[10:33:12] → Auto-activating 1 agents...
     ✓ security-auditor
```

### TUI AI Assistant

```bash
cortex tui
# Press '0' for AI Assistant view
# Press 'A' to auto-activate recommendations
```

Interactive AI view shows:

- → Intelligent recommendations with confidence scores
- → Workflow predictions from learned patterns
- → Context analysis (files, detected contexts)
- → Quick actions (keyboard shortcuts)

### CLI Commands

```bash
# Get recommendations for current context
cortex ai recommend

# Auto-activate high-confidence agents
cortex ai auto-activate

# Export recommendations to JSON
cortex ai export --output recommendations.json

# Record successful session for learning
cortex ai record-success --outcome "feature complete"
```

<div class="callout" style="margin-top: 1rem;">
  <strong>✅ Stability update:</strong> AI recommendations, auto-activation, and watch mode have been hardened. Context activation now tracks consistently across sessions and exports.
</div>

### Documentation

- [AI Intelligence Guide](AI_INTELLIGENCE.html) - Complete AI system overview
- [LLM Intelligence Guide](guides/ai/LLM_INTELLIGENCE_GUIDE.html) - Advanced Claude API configuration and usage
- [Watch Mode Guide](guides/development/WATCH_MODE_GUIDE.html) - Real-time monitoring deep dive

---

## 🩺 System Diagnostics {#diagnostics}

**New in November 2025** - Keep your context healthy and optimized.

```bash
# Run system health check
cortex doctor

# Attempt to auto-fix issues
cortex doctor --fix
```

Checks performed:

- **Consistency**: Verifies active agents/modes/rules exist.
- **Duplicates**: Finds duplicate agent definitions.
- **Optimization**: Identifies large files or unused resources.

---

## 📦 Asset Manager {#asset-manager}

Install, diff, and update plugin assets directly from the TUI.

**What it covers:**

- Hooks, commands, agents, skills, modes, workflows, and flags
- Install/uninstall to any detected `.claude` directory
- Diff installed vs source, bulk install by category, update outdated assets

**Quick start:**

```bash
cortex tui
# Press 'A' for Asset Manager
# i=install, u=uninstall, d=diff, U=update all, I=bulk install, T=target dir
```

**Documentation**: [Asset Manager Guide](guides/asset-manager.html)

---

## 🌿 Worktree Manager {#worktree-manager}

Manage git worktrees from the CLI or the TUI.

**CLI quick start:**

```bash
cortex worktree list
cortex worktree add my-branch --path ../worktrees/my-branch
cortex worktree remove my-branch
cortex worktree prune --dry-run
cortex worktree dir ../worktrees
```

**TUI quick start:**

```bash
cortex tui
# Press 'C' for Worktrees
# Ctrl+N add, Ctrl+O open, Ctrl+W remove, Ctrl+K prune, B set base dir
```

**Documentation**: [Worktree Manager Guide](guides/worktrees.html)

---

## 🤝 Collaboration Flow & Skill Auto-Suggestions {#collaboration}

**New in November 2025** – Inspired by Superpowers and SuperClaude frameworks.

<div class="feature-grid">
  <div class="feature-card">
    <h3>/ctx:brainstorm</h3>
    <p>Supersaiyan-aligned ideation capturing goals, success signals, and solution options.</p>
  </div>
  <div class="feature-card">
    <h3>/ctx:plan</h3>
    <p>Transforms brainstorms into stream-based plans and seeds the Task TUI automatically.</p>
  </div>
  <div class="feature-card">
    <h3>/ctx:execute-plan</h3>
    <p>Locks plans into orchestration view, enforces verification, and syncs tasks.</p>
  </div>
  <div class="feature-card">
    <h3>Skill Auto-Suggester Hook</h3>
    <p>`hooks/examples/skill_auto_suggester.py` reads <code>skills/skill-rules.json</code> and surfaces relevant skills after each prompt.</p>
  </div>
</div>

### Install the skill auto-suggester hook

```bash
cp hooks/examples/skill_auto_suggester.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill_auto_suggester.py

# settings.json snippet
{
  "hooks": {
    "user-prompt-submit": [
      {"command": "python3", "args": ["~/.claude/hooks/skill_auto_suggester.py"]}
    ]
  }
}
```

Edit `skills/skill-rules.json` to tweak keyword → `/ctx:*` mappings; no code changes required.

### Recommended workflow

1. `/session:load` – loads context and reminds you to brainstorm.
2. `/ctx:brainstorm` – capture options + constraints.
3. `/ctx:plan` – define workstreams, DoD, verification, and seed tasks.
4. `/ctx:execute-plan` – drive execution via Task TUI + orchestrate view.
5. `/dev:*` commands – build, test, review with quality gate hooks.

See [guides/skills.md](guides/skills.md) for the full catalog and resource snippets.

---

## ℹ AI-Powered Skills & Rating System {#skills-intelligence}

**New in November 2025** – Intelligent skill discovery and community feedback.

<div class="feature-grid">
  <div class="feature-card">
    <h3>→ AI Recommendations</h3>
    <p>Get personalized skill suggestions based on your project type, tech stack, and current task. Confidence scoring and reasoning included.</p>
  </div>
  <div class="feature-card">
    <h3>✓ Rating & Reviews</h3>
    <p>Rate skills 1-5 stars with optional reviews. Track quality metrics, success rates, and community feedback. Anonymous and private.</p>
  </div>
  <div class="feature-card">
    <h3>→ Quality Metrics</h3>
    <p>View aggregated ratings, helpful percentages, task success correlation, usage counts, and token efficiency for every skill.</p>
  </div>
  <div class="feature-card">
    <h3>→ Top Rated Skills</h3>
    <p>Discover highest-rated skills by category. Export ratings data in JSON or CSV for analysis and reporting.</p>
  </div>
</div>

### Quick Start

```bash
# Get AI-recommended skills for your project
cortex skills recommend

# Rate a skill you just used
cortex skills rate owasp-top-10 --stars 5 --review "Essential for security"

# View ratings and reviews
cortex skills ratings owasp-top-10

# See top-rated skills
cortex skills top-rated
```

**Example recommendation output:**

```
=== AI-Recommended Skills ===

Based on project type: python-fastapi
Active context: Building REST API with authentication

1. api-design-patterns (Confidence: 95%)
   Why: FastAPI project with REST API requirements

2. secure-coding-practices (Confidence: 90%)
   Why: Authentication requires security best practices
```

**Documentation**: [Skills Guide](guides/skills.md) - Complete reference including AI recommendations and rating system

---

## Project Structure

```
claude-cortex/
├── commands/           # Slash command definitions (49 across 13 categories)
│   ├── analyze/       # Code analysis, security scanning, troubleshooting
│   ├── cleanup/       # Cleanup and maintenance
│   ├── collaboration/ # Brainstorming, planning, execution
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
├── agents/            # Active specialized agents (19 agents)
│   ├── cloud-architect.md
│   ├── code-reviewer.md
│   ├── debugger.md
│   ├── deployment-engineer.md
│   ├── dx-optimizer.md
│   ├── knowledge-synthesizer.md
│   ├── kubernetes-architect.md
│   ├── learning-guide.md
│   ├── memory-keeper.md
│   ├── mermaid-expert.md
│   ├── orchestrator.md
│   ├── prompt-engineer.md
│   ├── python-pro.md
│   ├── refiner.md
│   ├── security-auditor.md
│   ├── sql-pro.md
│   ├── terraform-specialist.md
│   ├── tutorial-engineer.md
│   ├── typescript-pro.md
│   ├── dependencies.map         # Agent dependency graph
│   └── triggers.yaml            # Agent activation triggers
│
├── inactive/
│   └── agents/        # Disabled agents library (88 agents available)
│
├── modes/             # Behavioral modes (9 core)
│   ├── Amphetamine.md
│   ├── Architect.md
│   ├── Brainstorming.md
│   ├── Idea_Lab.md
│   ├── Introspection.md
│   ├── Security_Audit.md
│   ├── Super_Saiyan.md
│   ├── Teacher.md
│   ├── Token_Efficiency.md
│   └── supersaiyan/   # Platform-specific variants
│
├── flags/             # Modular flag packs (22)
├── hooks/             # Automation hooks
├── tasks/             # Task tracking and logs
│
├── rules/             # Reusable rule sets
│   ├── workflow-rules.md       # Git workflow, task patterns
│   ├── quality-rules.md        # Code organization, failure investigation
│   └── efficiency-rules.md     # Tool optimization, workspace hygiene
│
├── skills/            # Skill packs and metadata
├── prompts/           # Prompt library (guidelines, templates, personas)
│   ├── guidelines/    # Code review, style guides, checklists
│   ├── templates/     # PR descriptions, ADRs, documentation
│   └── personas/      # Specialized behavioral profiles
├── mcp/               # MCP docs + server resources
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
│   ├── core/          # Core management modules
│   ├── init_cmds.py   # Project init helpers
│   └── watch.py       # Watch mode implementation
│
├── schema/            # Validation schemas
├── scripts/           # Helper scripts
│
├── templates/         # Framework configuration templates
│   ├── CLAUDE.md
│   ├── FLAGS.md
│   ├── PRINCIPLES.md
│   ├── principles/
│   │   ├── 00-core-directive.md
│   │   ├── 10-philosophy.md
│   │   ├── 20-engineering-mindset.md
│   │   ├── 30-decision-framework.md
│   │   └── 40-quality-philosophy.md
│   ├── RULES.md
│   └── settings.json
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
    <p>An installable `cortex` CLI mirrors the plugin structure, enabling scripts, CI checks, and local automation.</p>
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
   /plugin install cortex@<marketplace-name>
   ```

3. Restart Claude Code to load commands and agents

### Via Python CLI

**Recommended (pip/uv/pipx + post-install):**

```bash
# Install the package (pick one)
python3 -m pip install -e ".[dev]"
# or: uv pip install -e ".[dev]"
# or: pipx install -e .

# Finish setup (completions, manpages, docs)
cortex install post
```

**Legacy installer (deprecated):**

```bash
./scripts/deprecated/install.sh
just install
```

**Manual Usage:**

```bash
# Verify installation
cortex --version

# View documentation
man cortex

# List available modes
cortex mode list

# Generate dependency map
cortex agent graph --export dependency-map.md
```

**What Gets Installed:**

- Python package (`cortex` command)
- Shell completions (bash/zsh/fish)
- Manpage (`man cortex`)
- Development dependencies (pytest, mypy, black)

For more detailed setup guidance (including shell completion and CLI overrides) see [guides/getting-started.md](guides/getting-started.md).

After adding new CLI subcommands, regenerate shell completions so the new options appear.

---

## Setup, Init & Migration

Keep your local context healthy and consistent across upgrades:

```bash
# Detect project type and recommend a profile
cortex init detect

# Apply a profile directly
cortex init profile backend

# Check current init status
cortex init status

# Migrate CLAUDE.md comment activation → .active-* files
cortex setup migrate
```

---

## Data Directory Overrides

The CLI resolves its workspace using the following precedence:

1. `CORTEX_SCOPE` (project/global/plugin)
2. `CLAUDE_PLUGIN_ROOT` (automatically set when commands run inside Claude Code)
3. `~/.claude`

Examples:

```bash
# Use the plugin cache that Claude Code maintains
export CLAUDE_PLUGIN_ROOT="$HOME/.claude/plugins/cache/cortex"

# Or target a local checkout of this repository
export CLAUDE_PLUGIN_ROOT="$HOME/Developer/personal/claude-cortex"

cortex mode status
```

Project-local and explicit directory examples:

```bash
cortex --scope project status
cortex --plugin-root /path/to/claude-cortex status
```

Once exported (for example in `~/.zshrc`), both the CLI and Claude Code share a single source of truth for agents, commands, and workflows.

---

## Core Systems

### 1. Command System

**Location**: `commands/`
**Count**: 49 slash commands across 13 categories

Commands provide curated behavioral prompts for specific development tasks. Each command includes:

- Trigger conditions for automatic activation
- Usage patterns and examples
- MCP integration specifications
- Tool coordination patterns
- Success criteria and boundaries

**Categories**:

- `/analyze` - Code analysis, security, troubleshooting
- `/cleanup` - Cleanup and maintenance
- `/collaboration` - Brainstorming, planning, and execution
- `/deploy` - Release preparation
- `/design` - System design and workflow planning
- `/dev` - Development tasks
- `/docs` - Documentation generation
- `/orchestrate` - Multi-agent orchestration
- `/quality` - Code quality
- `/reasoning` - Reasoning frameworks and structure
- `/session` - Session management
- `/test` - Test generation
- `/tools` - Tool selection

**Reference**: [Command Documentation](guides/commands.md)

---

### 2. Agent System

**Location**: `agents/` and `inactive/agents/`
**Active Agents**: 19 | **Available**: 107

Agents are specialized personas with domain expertise and specific capabilities. The system includes:

- **Dependency Management**: `dependencies.map` tracks agent relationships
- **Trigger System**: `triggers.yaml` defines automatic activation patterns
- **Activation Control**: Move between `agents/` and `inactive/agents/` to control availability

**Active Agents**:

- `cloud-architect` - Cloud infrastructure design
- `code-reviewer` - Code quality analysis
- `debugger` - Issue diagnosis and resolution
- `deployment-engineer` - Release engineering
- `dx-optimizer` - Developer experience and workflow tooling
- `knowledge-synthesizer` - Cross-agent pattern synthesis
- `kubernetes-architect` - K8s orchestration
- `learning-guide` - Guided explanations and onboarding
- `memory-keeper` - Memory vault curation
- `mermaid-expert` - Architecture diagrams and visuals
- `orchestrator` - High-level planning and delegation
- `prompt-engineer` - Prompt optimization
- `python-pro` - Python expertise
- `refiner` - Iterative improvements
- `security-auditor` - Security assessment
- `sql-pro` - SQL expertise
- `terraform-specialist` - Infrastructure as code
- `tutorial-engineer` - Hands-on tutorials
- `typescript-pro` - TypeScript expertise

**Reference**: [Agent Documentation](guides/agents.md)

---

### 3. Mode System

**Location**: `modes/` (core) and `modes/supersaiyan/` (platform variants)
**Core Modes**: 9 | **Super Saiyan variants**: 4

Modes are opinionated context modules that toggle workflow defaults and behavioral patterns.

**Core Modes**:

- `Amphetamine` - Maximum-velocity MVP prototyping
- `Architect` - Strategic system design & trade-offs
- `Brainstorming` - Collaborative discovery and exploration
- `Idea_Lab` - Timeboxed ideation with rapid options
- `Introspection` - Meta-cognitive analysis & reflection
- `Security_Audit` - Security-first review mindset
- `Super_Saiyan` - Visual excellence mode (see variants)
- `Teacher` - Educational explanations and mentoring
- `Token_Efficiency` - Concise, token-aware responses

**Activation**: Use `cortex mode activate`, the TUI (press `3`), or `FLAGS.md`. Active state is tracked in `.active-modes` (use `cortex setup migrate` for legacy `CLAUDE.md` references).

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
**Entry Point**: `cortex`

Python CLI for managing context components outside of Claude Code.

**Capabilities**:

- Mode/rule/agent management (list, activate, deactivate)
- AI recommendations, watch mode, and export
- Init detection and profile setup
- Worktree management (list/add/remove/prune/base dir)
- Migration helpers (`setup migrate`) and diagnostics (`doctor`)
- Agent dependency visualization and context export

**Reference**: [CLI Documentation](CLI.md)

---

## Deep Dive Documentation

Comprehensive guides to cortex architecture, optimization strategies, and advanced patterns.

<div class="doc-grid">
  <a href="guides/development/architecture.html" class="doc-card">
    <h3>Architecture & Design</h3>
    <p>System architecture, design patterns, and component interactions. Explore dependency injection, progressive disclosure, lazy loading, and extension points.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>17KB guide</span>
      <span>Core systems</span>
    </div>
  </a>

  <a href="guides/agents.html" class="doc-card">
    <h3>Agent Catalog</h3>
    <p>Catalog of 107 agents (19 active, 88 inactive) organized by category with model assignments, dependencies, workflows, and activation criteria.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>23KB reference</span>
      <span>107 agents</span>
    </div>
  </a>

  <a href="guides/skills.html" class="doc-card">
    <h3>Agent Skills</h3>
    <p>Progressive disclosure architecture for specialized knowledge. Learn how to create skills, integrate with agents, and keep context lean.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>16KB guide</span>
      <span>54 skills</span>
    </div>
  </a>

  <a href="guides/development/model-optimization.html" class="doc-card">
    <h3>Model Optimization ✓</h3>
    <p>Strategic Haiku vs Sonnet assignment guidance. Hybrid orchestration patterns, decision matrix, and performance benchmarks.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>13KB strategy</span>
      <span>Tuning guide</span>
    </div>
  </a>

  <a href="guides/development/PHASE5_ROADMAP.html" class="doc-card">
    <h3>Skills Roadmap →</h3>
    <p>Skill System Intelligence: AI recommendations ✓, ratings & feedback ✓, advanced discovery, analytics, smart bundling, and personalization. Features 1-2 complete.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>32KB roadmap</span>
      <span>2/6 features complete</span>
    </div>
  </a>

  <a href="archive/reports/phase4-summary.html" class="doc-card">
    <h3>Recent Features ✓</h3>
    <p>Complete implementation of skill composition, semantic versioning, community integration, and effectiveness analytics. Production-ready enterprise features.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>32KB reference</span>
      <span>4 features complete</span>
    </div>
  </a>

  <a href="guides/development/quality-improvements.html" class="doc-card">
    <h3>Quality & DevOps</h3>
    <p>Testing infrastructure with 150+ tests, code refactoring, error handling improvements, installation automation, and CI/CD pipeline. Grade improved from B+ to A.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>Production ready</span>
      <span>95/100 score</span>
    </div>
  </a>

  <a href="guides/memory.html" class="doc-card">
    <h3>Memory Vault ℹ</h3>
    <p>Persistent knowledge storage for Claude Code sessions. Capture domain knowledge, project context, session summaries, and bug fixes in Markdown format with TUI integration.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>4 note types</span>
      <span>Auto-capture</span>
    </div>
  </a>
</div>

---

## → Technical Architecture Documentation

Comprehensive technical documentation for developers, maintainers, and contributors.

<div class="doc-grid">
  <a href="architecture/MASTER_ARCHITECTURE.html" class="doc-card">
    <h3>→ Master Architecture</h3>
    <p>Complete system architecture covering all 8 core subsystems: CLI, TUI, AI Intelligence, Memory Vault, Skills, MCP, Component Toggle, and Doctor Diagnostics. The definitive technical reference.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>3,700+ lines</span>
      <span>8 subsystems</span>
      <span>v1.1</span>
    </div>
  </a>

  <a href="guides/development/TUI_ARCHITECTURE.html" class="doc-card">
    <h3>▶ TUI Architecture</h3>
    <p>Textual framework integration, reactive state management, SPA patterns, command palette, styling system (TCSS), and performance optimization strategies.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>963 lines</span>
      <span>Package refactoring</span>
    </div>
  </a>

  <a href="guides/development/MEMORY_VAULT_ARCHITECTURE.html" class="doc-card">
    <h3>ℹ Memory Vault System</h3>
    <p>3-layer architecture (Interfaces, Memory Module, Storage), 4 note types, auto-capture system, full-text search with relevance scoring, CLI/TUI integration.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>1,085 lines</span>
      <span>5 Python modules</span>
    </div>
  </a>

  <a href="guides/development/AI_INTELLIGENCE_ARCHITECTURE.html" class="doc-card">
    <h3>→ AI Intelligence System</h3>
    <p>4-layer architecture, pattern learning with collaborative filtering, skill recommendation engine (3 strategies), context detection (6 signals), auto-activation at ≥80% confidence.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>1,330 lines</span>
      <span>Machine learning</span>
    </div>
  </a>

  <a href="guides/development/WATCH_MODE_ARCHITECTURE.html" class="doc-card">
    <h3>→ Watch Mode Implementation</h3>
    <p>Real-time monitoring with 2s polling (~1% CPU), git integration, notification system with threshold filtering, auto-activation tracking, resource management.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>1,027 lines</span>
      <span>~20MB memory</span>
    </div>
  </a>

  <a href="guides/development/SKILL_RATING_ARCHITECTURE.html" class="doc-card">
    <h3>✓ Skill Rating & Feedback</h3>
    <p>SQLite storage (3 tables), auto-prompt system (12hr lookback, 24hr cooldown), quality metrics (6 dimensions), TUI integration (Ctrl+R), anonymous hashing.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>933 lines</span>
      <span>Privacy-first</span>
    </div>
  </a>

  <a href="guides/development/MCP_SERVER_MANAGEMENT_ARCHITECTURE.html" class="doc-card">
    <h3>→ MCP Server Management</h3>
    <p>Cross-platform server discovery, curated registry (25+ servers, 10 categories), automated installation, configuration validation, TUI browser (Key 7), documentation integration.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>1,850 lines</span>
      <span>4 core modules</span>
    </div>
  </a>

  <a href="guides/development/SUPER_SAIYAN_MODE_ARCHITECTURE.html" class="doc-card">
    <h3>→ Super Saiyan Mode</h3>
    <p>Enhanced TUI components with smooth animations (CSS transitions), rich styling (semantic color palette), 5 core components, accessibility-first design, performance optimization.</p>
    <span class="doc-card__arrow">→</span>
    <div class="doc-card__meta">
      <span>1,254 lines</span>
      <span>< 2% CPU overhead</span>
    </div>
  </a>
</div>

<div class="callout" style="margin-top: 1rem;">
  <strong>→ For Developers:</strong> These documents provide deep-dive technical details including data models, workflows, performance benchmarks, and development guides. Perfect for onboarding, technical reviews, and system maintenance.
</div>

---

## Framework Entry Points

> **Note**: In this repo, core framework files live in `templates/`.
> Copy `templates/CLAUDE.md`, `templates/FLAGS.md`, `templates/RULES.md`,
> `templates/settings.json`, plus `templates/principles/` and
> `templates/.active-principles` into `~/.claude/`, then run
> `cortex principles build` to generate `PRINCIPLES.md`.

### CLAUDE.md

Primary framework entry point that loads:

- Core framework (FLAGS.md, PRINCIPLES.md, RULES.md)
- Workflow rules (automatic for all development tasks)
- Conditional rules (loaded as needed)
- Active behavioral modes
- MCP documentation

### PRINCIPLES.md

Generated from `principles/*.md` snippets (tracked in `.active-principles` and ordered by filename).
Use `cortex principles build` to regenerate.

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
  "name": "cortex",
  "version": "0.1.0",
  "description": "Context orchestration plugin",
  "commands": ["./commands"]
}
```

### Python Package

**File**: `pyproject.toml`

```toml
[project]
name = "cortex-py"
version = "0.1.0"
requires-python = ">=3.9"

[project.scripts]
cortex = "claude_ctx_py.cli:main"
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
2. Use `Architect` for multi-phase system work
3. Enable `Token_Efficiency` for large operations
4. Combine modes thoughtfully (conflicts are detected via mode metadata)

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

1. Check agent location (`agents/` vs `inactive/agents/`)
2. Review `triggers.yaml` for activation conditions
3. Verify dependencies in `dependencies.map`
4. Manually invoke with `/agent activate <name>`

### CLI Issues

1. Verify installation: `python3 -m pip show cortex-py`
2. Check Python version: `python3 --version` (>=3.9 required)
3. Reinstall: `python3 -m pip install --force-reinstall .`

---

## Contributing

### Adding Commands

1. Pick a namespace and command name (e.g., `analyze:doctor`)
2. Create a markdown file in `commands/` (colon replaced with dash, e.g., `commands/analyze-doctor.md`)
3. Set `name: "analyze:doctor"` in front matter
4. Update command count in this index if needed

### Creating Agents

1. Create markdown file in `inactive/agents/`
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

**Core Documentation**

- [Getting Started](guides/getting-started.html) - Installation and setup
- [Installation Guide](guides/INSTALL.html) - Detailed installation instructions
- [Architecture Guide](guides/development/architecture.html) - System design and patterns
- [Command Reference](guides/commands.html) - Complete command catalog

**Agent System**

- [Agent Catalog](guides/agents.html) - Agent reference with 107 documented agents
- [Agent Skills Guide](guides/skills.html) - Progressive disclosure and token optimization
- [Model Optimization](guides/development/model-optimization.html) - Haiku vs Sonnet strategy

**Feature Guides**

- [AI Intelligence Guide](AI_INTELLIGENCE.html) - AI intelligence & automation system overview
- [LLM Intelligence Guide](guides/ai/LLM_INTELLIGENCE_GUIDE.html) - Claude API configuration, pricing, and advanced usage
- [Watch Mode Guide](guides/development/WATCH_MODE_GUIDE.html) - Real-time monitoring and auto-activation
- [Modes Guide](guides/modes.html) - Behavioral modes and activation
- [Asset Manager Guide](guides/asset-manager.html) - Install, diff, and update assets
- [Worktree Manager Guide](guides/worktrees.html) - Git worktree workflows
- [Command Palette Guide](guides/COMMAND_PALETTE_GUIDE.html) - Interactive command palette
- [TUI Guide](guides/tui.html) - Terminal user interface
- [TUI Quick Start](guides/tui-quick-start.html) - Get started with TUI in 5 minutes
- [TUI Integration Guide](guides/tui-integration.html) - Integrate TUI into your workflow
- [Skills TUI Integration](guides/skills-tui-integration.html) - Skills system TUI integration
- [TUI Keyboard Reference](guides/tui/tui-keyboard-reference.html) - Complete keyboard shortcuts
- [TUI Navigation](guides/tui/tui-navigation-summary.html) - Navigation patterns

**CLI & Integration**

- [Shell Completions](guides/COMPLETIONS.html) - Bash, Zsh, and Fish completion scripts
- [Warp AI Integration](guides/features/WARP_AI_INTEGRATION.html) - Terminal AI tools integration with context export aliases
- [Prompt Library](guides/prompt-library.html) - On-demand prompts, guidelines, and templates

**Advanced Features**

- [Super Saiyan Mode](features/SUPER_SAIYAN_MODE.html) - Visual excellence framework
- [Kamehameha Overview](features/KAMEHAMEHA_OVERVIEW.html) - Power levels and activation
- [Contextual RAG](features/contextual-rag.html) - Enhanced retrieval with situated context
- [Frontend Aesthetics](features/frontend-aesthetics.html) - Performance-first UI generation
- [Super Saiyan Integration](guides/features/SUPER_SAIYAN_INTEGRATION.html) - Integration guide
- [Parallel Orchestration](guides/development/PARALLEL_ORCHESTRATION_GUIDE.html) - Multi-agent coordination
- [Quality Improvements](guides/development/quality-improvements.html) - Code quality enhancements

### External Resources

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Plugin Development Guide](https://docs.claude.com/claude-code/plugins)
- [MCP Specification](https://modelcontextprotocol.io)

---

## Version History

### 2.0.0 (2026-01-08)

- Renamed claude-ctx to cortex across the CLI/TUI, env vars, and docs
- Introduced `CORTEX_ROOT` with a default `~/.cortex` layout and rules sync to `~/.claude/rules/cortex`
- Bundled all plugin assets into the Python package for self-contained installs
- Updated launcher/config flow to prefer `~/.cortex` and bundled asset discovery

### 1.2.0 (2025-12-21)

- Asset Manager TUI for installing, diffing, and updating assets
- Worktree Manager (CLI + TUI) with base directory control
- Init detection and migration tooling (`init` and `setup migrate`)
- New modes (Amphetamine, Idea_Lab, Teacher) + mode metadata/conflict detection
- AI stability and context tracking fixes

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

**Repository**: [github.com/NickCrew/claude-cortex](https://github.com/NickCrew/claude-cortex)

**Issues**: [Report a bug or request a feature](https://github.com/NickCrew/claude-cortex/issues)

**Marketplace**: [claude-marketplace](https://github.com/NickCrew/claude-marketplace)

---

*This documentation was generated using `/docs:index` command*
