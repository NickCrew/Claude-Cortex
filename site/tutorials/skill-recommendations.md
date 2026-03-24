---
layout: default
title: Skill Recommendations
parent: Tutorials
nav_order: 1
---

# Discover and Use Skill Recommendations

Cortex can suggest relevant skills from three entry points:

- the Claude Code prompt hook
- `cortex skills recommend`
- watch-mode skill suggestions

This tutorial walks through the current workflow without mixing skill
recommendations up with the separate **agent intelligence** system.

## What You'll Learn

- get skill recommendations from the CLI
- understand the difference between hook, watch, and CLI recommendations
- record recommendation feedback
- rate skills in the CLI and TUI
- understand how Cortex learns from successful usage

## Prerequisites

- Cortex installed with the Python CLI
- a git-backed project with some changed files

## Time Estimate

~15 minutes

---

## 1. Get Your First Skill Recommendations

Start with the structured recommender:

```bash
cortex skills recommend
```

This uses git-backed session context and the richer recommendation pipeline to
produce a short list of relevant skills.

You can also write or print the current skill context:

```bash
# Writes .claude/skill-context.md
cortex skills context

# Prints to stdout only
cortex skills context --no-write
```

### What these recommendations are based on

In normal CLI usage, Cortex mainly uses:

- file-pattern rules
- learned history from past successful sessions
- optional semantic similarity

Agent-to-skill mappings also exist, but they are strongest when active agents
are explicitly present in the recommendation context.

### Checkpoint

At this point you should have:

- [ ] Run `cortex skills recommend`
- [ ] Seen at least one recommended skill
- [ ] Run `cortex skills context` or `cortex skills context --no-write`

---

## 2. Compare The Three Skill Surfaces

### CLI: structured recommendations

```bash
cortex skills recommend
```

This is the richest terminal-facing path and is the best place to start when
you want a focused shortlist.

### Hook: prompt-time suggestions

Inside Claude Code, the prompt hook can emit suggestions like:

```text
Suggested skills: agent-loops, documentation-production
```

This path is fast and deterministic. It uses:

- prompt text
- changed files
- file types and directories
- git branch name
- recent commit subjects

### Watch mode: live suggestions while you work

```bash
cortex ai watch --no-auto-activate
```

Watch mode can show both:

- **agent recommendations** for activation decisions
- **skill suggestions** for prompt-level guidance

That distinction matters:

- agents answer "who should help with this?"
- skills answer "what knowledge pack should I load?"

### Important TUI note

The TUI AI Assistant (`0`) is focused on **agent** recommendations, not the
main place to inspect skill recommendations. For skill workflows in the TUI,
use the Skills view.

---

## 3. Understand How Skill Recommendations Work

The richer skill recommender combines four strategies:

1. **Semantic similarity**
2. **Rule-based file-pattern matching**
3. **Agent-based mapping**
4. **Pattern-based history from successful contexts**

In practice:

- file-pattern rules are the most reliable first-run signal
- learned history becomes more useful over time
- semantic similarity helps most when the optional embeddings dependency and
  historical data are present
- agent-based mapping depends on active agents being present in the context

The prompt hook is separate from this layered recommender. It uses
`skills/skill-rules.json` for low-latency keyword matching and can still work
even when the richer Layer 2 path is unavailable.

---

## 4. Give Recommendation Feedback

If Cortex suggested a skill and it was useful, record that directly:

```bash
cortex skills feedback documentation-production helpful
```

If it was not useful:

```bash
cortex skills feedback documentation-production not-helpful
```

You can also attach a short explanation:

```bash
cortex skills feedback documentation-production helpful \
  --comment "Matched a docs-heavy refactor well"
```

This teaches the recommender whether a suggestion was actually helpful.

---

## 5. Rate A Skill

Ratings are broader quality signals than recommendation feedback.

### Via CLI

```bash
cortex skills rate documentation-production \
  --stars 5 \
  --helpful \
  --succeeded \
  --review "Helpful for restructuring docs"
```

Useful variants:

```bash
cortex skills rate documentation-production --stars 4 --not-helpful
cortex skills rate documentation-production --stars 2 --failed
```

### Via TUI

1. Launch the TUI: `cortex tui`
2. Press `4` to open the Skills view
3. Select a skill with the arrow keys
4. Press `Ctrl+R` to open the rating dialog

The Skills view is the right TUI surface for browsing and rating the catalog.

### Checkpoint

At this point you should have:

- [ ] Left recommendation feedback with `skills feedback`
- [ ] Rated at least one skill with `skills rate` or `Ctrl+R` in the TUI

---

## 6. Inspect Ratings And Quality Signals

View ratings for one skill:

```bash
cortex skills ratings documentation-production
```

See top-rated skills:

```bash
cortex skills top-rated --limit 10
```

Export ratings:

```bash
cortex skills export-ratings --format json
cortex skills export-ratings --format csv
```

These commands are useful for comparing long-term skill quality, while
`skills feedback` is focused on recommendation usefulness.

---

## 7. How Cortex Learns

Skill learning currently comes from three places:

### 1. Recommendation feedback

```bash
cortex skills feedback <skill> helpful
```

This updates recommendation history and helpfulness signals.

### 2. Review ingestion

```bash
cortex ai ingest-review path/to/review.md
```

Structured specialist reviews can be mapped back into skill learning so Cortex
gets better at suggesting the right skills earlier.

### 3. Successful sessions

```bash
cortex ai record-success --outcome "feature complete"
```

This primarily teaches the **agent** recommender, but Cortex also makes a
best-effort bridge into skill learning.

---

## 8. Where The Data Lives

Recommendation data:

- `~/.claude/data/skill-recommendations.db`
- `~/.claude/skills/recommendation-rules.json`
- `~/.claude/skills/skill-rules.json`

Ratings data:

- `~/.claude/data/skill-ratings.db`

Optional semantic cache:

- `~/.claude/data/skill_semantic_cache/`

These are local files on your machine.

---

## Summary

You now know how to:

- get skill recommendations from `cortex skills recommend`
- compare CLI, hook, and watch-mode suggestion paths
- record recommendation usefulness with `skills feedback`
- rate skills in the CLI and TUI
- understand how review ingestion and session success improve future skill suggestions

## Next Steps

- Read the [Skills](../guides/skills.md) guide
- Read [AI Intelligence](../guides/ai-intelligence.md) for the separate agent system
- Read [Configuration Reference](../reference/configuration.md)
