---
layout: default
title: Tutorials
nav_order: 5
has_children: true
permalink: /tutorials/
---

# Tutorials

Hands-on walkthroughs for common Cortex workflows.
{: .fs-6 .fw-300 }

---

## Skill Recommendations

Learn how the AI-powered recommendation engine discovers, suggests, and learns from your skill usage. Covers CLI and TUI workflows, the rating system, and how feedback improves future suggestions.

[Start Tutorial]({% link tutorials/skill-recommendations.md %}){: .btn .btn-primary .mr-2 }
~15 minutes
{: .fs-3 .text-grey-dk-000 }

---

## Getting Started with the TUI

Master the terminal UI in 20-30 minutes. Covers navigation, agent management, workflows, and when to use CLI vs TUI.

```bash
cortex tui
```

**What you'll learn:**

1. Navigate between views (Agents, Modes, Skills, AI Assistant)
2. Activate and configure agents
3. Use the Command Palette (`Ctrl+P`)
4. Manage flags with the Flag Manager (`Ctrl+G`)
5. Rate skills and track quality metrics
6. Export context snapshots

---

## Feature Development Workflow

Build a feature from design to deployment using Cortex commands:

1. **Plan** -- `/ctx:brainstorm` to capture goals and options
2. **Design** -- `/design:workflow` to define implementation steps
3. **Implement** -- `/dev:implement` with quality gates
4. **Test** -- `/test:generate` for coverage
5. **Review** -- `/dev:code-review` for quality validation
6. **Ship** -- `/dev:git` for semantic commits, `/deploy:prepare-release`

---

## Bug Fix Workflow

Systematic bug resolution:

1. **Diagnose** -- `/analyze:troubleshoot` for root cause analysis
2. **Fix** -- `/dev:implement` to apply the fix
3. **Verify** -- `/test:generate` for regression tests
4. **Review** -- `/dev:code-review` for validation
5. **Commit** -- `/dev:git` with `fix(scope): description`

---

## Setting Up Watch Mode

Configure real-time project monitoring:

```bash
# Start watching (foreground)
cortex ai watch

# Or run as a background daemon
cortex ai watch --daemon

# Check status
cortex ai watch --status

# Stop the daemon
cortex ai watch --stop
```

Watch mode detects file changes, analyzes context, and auto-activates relevant agents when confidence is above 80%.

---

## Multi-LLM Consultation

Get second opinions from other LLMs:

1. Open the TUI: `cortex tui`
2. Press `Ctrl+P` for Command Palette
3. Type "Configure LLM Providers"
4. Set up API keys for Gemini, OpenAI, or Qwen
5. Use the `multi-llm-consult` skill for independent reviews
