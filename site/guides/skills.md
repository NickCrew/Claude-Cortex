---
layout: default
title: Skills
parent: Guides
nav_order: 4
---

# Skills

Skills are reusable knowledge modules that provide specialized capabilities on demand. Cortex ships with 100+ skills covering security, testing, architecture, DevOps, and more.

## How Skills Work

Skills use progressive disclosure -- they're loaded only when needed, keeping your context lean. Each skill has:

- **Trigger conditions** for automatic suggestion
- **Dependencies** on other skills or agents
- **References** to detailed instruction files

## Discovering Skills

In Claude Code, skills are surfaced automatically by the skill auto-suggester hook based on your current task. You can also browse them:

```bash
# Get AI-recommended skills for your project
cortex skills recommend

# List all available skills
cortex skills list

# View top-rated skills
cortex skills top-rated
```

## Using Skills in Claude Code

Skills appear as slash commands. When a skill is relevant to your current work, the auto-suggester hook recommends it:

```
Suggested skills: security-testing-patterns, owasp-top-10
```

## Rating Skills

Rate skills to improve future recommendations:

```bash
# Rate via CLI
cortex skills rate owasp-top-10 --stars 5 --review "Essential for security"

# Rate in TUI
cortex tui
# Press 5 for Skills view, select a skill, press Ctrl+R
```

## Viewing Ratings

```bash
# View ratings for a specific skill
cortex skills ratings owasp-top-10

# See top-rated skills
cortex skills top-rated --limit 10

# Export ratings for analysis
cortex skills export-ratings --format csv > ratings.csv
```

## Skill Categories

Skills are organized by domain:

| Category | Examples |
|:---------|:---------|
| Security | `owasp-top-10`, `security-testing-patterns`, `threat-modeling` |
| Testing | `test-driven-development`, `vitest-expert`, `python-testing-patterns` |
| Architecture | `system-design`, `microservices-patterns`, `event-driven-architecture` |
| Frontend | `react-performance-optimization`, `tailwind-expert`, `accessibility-audit` |
| DevOps | `kubernetes-deployment-patterns`, `terraform-best-practices`, `github-actions-workflows` |
| Database | `database-design-patterns`, `postgres-expert`, `sql-pro` |
| Documentation | `documentation-production`, `reference-documentation`, `tutorial-design` |
| Workflow | `workflow-feature`, `workflow-bug-fix`, `workflow-performance` |

## Auto-Suggester Hook

The skill auto-suggester runs after each prompt and recommends relevant skills:

```bash
# Install the hook
cp hooks/skill_auto_suggester.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill_auto_suggester.py
```

Configure keyword-to-skill mappings in `skills/skill-rules.json`.
