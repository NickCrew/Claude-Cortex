---
layout: default
title: Tutorials
nav_order: 5
has_children: true
permalink: /tutorials/
---

# Tutorials

Hands-on walkthroughs for common Cortex tasks.
{: .fs-6 .fw-300 }

---

## Skill Recommendations

Learn how the AI-powered recommendation engine discovers, suggests, and learns from your skill usage. Covers CLI and TUI workflows, the rating system, and how feedback improves future suggestions.

[Start Tutorial]({% link tutorials/skill-recommendations.md %}){: .btn .btn-primary .mr-2 }
~15 minutes
{: .fs-3 .text-grey-dk-000 }

---

## Getting Started with the TUI

Master the terminal UI in 20-30 minutes. Covers navigation, agent management, and when to use CLI vs TUI.

```bash
cortex tui
```

**What you'll learn:**

1. Navigate between views (Agents, Skills, AI Assistant)
2. Activate and configure agents
3. Use the Command Palette (`Ctrl+P`)
4. Browse generated slash commands in the Commands view
5. Rate skills and track quality metrics
6. Export context snapshots

---

## Feature Development Workflow

Build a feature from ideation to implementation using skill-backed commands:

1. **Plan** -- `/collaboration:brainstorming` to capture goals and options
2. **Write the plan** -- `/collaboration:writing-plans` to define workstreams and steps
3. **Execute** -- `/collaboration:executing-plans` to drive the implementation
4. **Implement safely** -- `/ctx:agent-loops` with quality gates
5. **Test** -- `/ctx:test-generation` for coverage
6. **Review and wrap up** -- `/ctx:requesting-code-review`, then `/ctx:git-ops`

---

## Bug Fix Workflow

Systematic bug resolution:

1. **Diagnose** -- `/ctx:systematic-debugging` for root cause analysis
2. **Fix** -- `/ctx:agent-loops` to apply the change with review gates
3. **Verify** -- `/ctx:test-generation` for regression tests
4. **Review** -- `/ctx:requesting-code-review` for validation
5. **Commit** -- `/ctx:git-ops` with a focused fix commit

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

Watch mode detects file changes, analyzes context, and can auto-activate
relevant agents when they cross your configured threshold. The default threshold
is `0.7` unless you override it in `cortex-config.json` or at runtime.

---

## Multi-LLM Consultation

Get second opinions from other LLMs:

1. Open the TUI: `cortex tui`
2. Press `Ctrl+P` for Command Palette
3. Type "Configure LLM Providers"
4. Set up API keys for Gemini, OpenAI, or Qwen
5. Use the `multi-llm-consult` skill for independent reviews
