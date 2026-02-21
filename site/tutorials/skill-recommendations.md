---
layout: default
title: Skill Recommendations
parent: Tutorials
nav_order: 1
---

# Discover and Rate Skills with the Recommendation Engine

Cortex includes an AI-powered skill recommendation system that suggests relevant skills based on your project context, learns from your feedback, and improves over time. This tutorial walks through the full workflow: getting recommendations, rating skills, and understanding how the feedback loop works.

## What You'll Learn

- Get context-aware skill recommendations from the CLI and TUI
- Understand how the four recommendation strategies work together
- Rate skills and write reviews
- View quality metrics and top-rated skills
- See how your ratings improve future recommendations

## Prerequisites

- Cortex installed with the Python CLI (`pip install claude-cortex`)
- A project directory with some source files (any language)

## Time Estimate

~15 minutes

---

## 1. Get Your First Recommendations

The recommendation engine analyzes your current project context -- file types, directory structure, git history, and active agents -- to suggest skills you're likely to need.

### Via CLI

Run this from any project directory:

```bash
cortex skills recommend
```

Expected output:

```
=== AI-Recommended Skills ===

Based on project type: python-fastapi
Active context: Building REST API with authentication

1. api-design-patterns (Confidence: 95%)
   Why: FastAPI project with REST API requirements

2. secure-coding-practices (Confidence: 90%)
   Why: Authentication requires security best practices

3. python-testing-patterns (Confidence: 85%)
   Why: Python project with test infrastructure detected
```

Each recommendation includes:

| Field | Meaning |
|:------|:--------|
| **Skill name** | The skill's identifier (use this in slash commands) |
| **Confidence** | How certain the engine is that this skill is relevant |
| **Why** | The signal that triggered this recommendation |

Confidence levels: **High** (80%+) means strong contextual match, **Medium** (60-80%) means likely useful, **Low** (<60%) means tangentially related.

### Via TUI

```bash
cortex tui
```

Press `0` to open the AI Assistant view. Recommendations appear with confidence scores. Press `A` to auto-activate recommended agents associated with those skills.

### Checkpoint

At this point you should have:

- [ ] Run `cortex skills recommend` and seen at least one recommendation
- [ ] Noted the confidence score and reasoning for each suggestion

**No recommendations showing?** The engine needs file context. Make sure you're running the command from inside a project with source files, not an empty directory.

---

## 2. How Recommendations Work

The engine combines four strategies, each contributing signals. When multiple strategies recommend the same skill, confidence gets a boost.

### Strategy 1: Rule-Based Matching

Matches file patterns in your project to skills. For example:

| File Pattern | Recommended Skill | Confidence |
|:-------------|:------------------|:-----------|
| `**/auth/**/*.py` | `owasp-top-10` | 90% |
| `**/*.test.ts` | `test-driven-development` | 85% |
| `Dockerfile` | `kubernetes-deployment-patterns` | 75% |

### Strategy 2: Agent-Based Mapping

When agents are active, their expert skills are recommended:

| Active Agent | Recommended Skills |
|:-------------|:-------------------|
| `security-auditor` | `owasp-top-10` (95%), `threat-modeling` (90%) |
| `react-specialist` | `react-performance-optimization` (90%) |
| `database-optimizer` | `database-design-patterns` (85%) |

### Strategy 3: Pattern Learning

Learns from your past sessions. When you rate a skill as helpful after a successful task, the engine records the context. Future sessions with similar context get that skill recommended.

Skills need a success rate above 70% in recorded patterns to be recommended through this strategy.

### Strategy 4: Semantic Similarity (Optional)

If `fastembed` is installed (`pip install claude-cortex[ai]`), the engine uses embeddings to find skills that were useful in similar past sessions, even when file patterns don't match exactly.

### Auto-Suggester Hook

Separately from the AI engine, the auto-suggester hook runs after each prompt in Claude Code and matches keywords from your prompt, changed files, and git branch name against `skills/skill-rules.json`:

```
Suggested skills: security-testing-patterns, owasp-top-10
```

This is the fastest path -- it uses keyword matching rather than the full AI engine.

---

## 3. Rate a Skill

Ratings are what make the recommendation engine smarter. After using a skill, rate it to provide feedback.

### Via CLI

```bash
cortex skills rate owasp-top-10 --stars 5 --review "Caught a missing CSRF check"
```

All options:

```bash
cortex skills rate <skill-name> \
  --stars 4 \                    # Required: 1-5
  --helpful \                    # Optional: was it helpful? (default: yes)
  --task-succeeded \             # Optional: did the task succeed? (default: yes)
  --review "Free-form text"      # Optional: text review
```

### Via TUI

1. Launch the TUI: `cortex tui`
2. Press `5` to open the Skills view
3. Select a skill with arrow keys
4. Press `Ctrl+R` to open the rating dialog
5. Enter your star rating (1-5)
6. Answer "Was it helpful?" (y/n)
7. Answer "Did the task succeed?" (y/n)
8. Optionally write a review (or press Enter to skip)

The TUI also auto-prompts for ratings: after startup, if you recently used a skill that hasn't been rated, a prompt appears asking for feedback. Dismiss it to snooze for 24 hours, or rate it to clear the prompt.

### Checkpoint

At this point you should have:

- [ ] Rated at least one skill (CLI or TUI)
- [ ] Seen the success confirmation

**Error: "Skill not found"?** Check the exact skill name with `cortex skills list`. Names are hyphenated lowercase (e.g., `owasp-top-10`, not `OWASP Top 10`).

---

## 4. View Ratings and Metrics

### Single Skill

```bash
cortex skills ratings owasp-top-10
```

Output:

```
=== owasp-top-10 ===

Rating: 4.8/5.0 (12 ratings)
Helpful: 92%
Task Success: 83%

Distribution:
  5 ████████████████ 9
  4 ██████           3
  3                  0
  2                  0
  1                  0

Recent Reviews:
  [2026-02-14] "Caught a missing CSRF check" (5 stars)
  [2026-02-10] "Essential for security audits" (5 stars)
```

### Top-Rated Skills

```bash
cortex skills top-rated --limit 5
```

Skills need at least 3 ratings to appear in the top-rated list. This prevents a single 5-star rating from dominating.

### Export for Analysis

```bash
# JSON format
cortex skills export-ratings --format json > ratings.json

# CSV format
cortex skills export-ratings --format csv > ratings.csv

# Filter to one skill
cortex skills export-ratings --skill owasp-top-10 --format json
```

### In the TUI

In the Skills view (`5`), the ratings column shows inline:

```
Skill                    Rating
─────────────────────    ─────────────────
owasp-top-10             4.8/5.0 (12 ratings)
test-driven-development  4.5/5.0 (8 ratings)
system-design            -- (no ratings)
```

### Checkpoint

At this point you should have:

- [ ] Viewed ratings for a specific skill
- [ ] Seen the distribution histogram and review list
- [ ] Run `cortex skills top-rated`

---

## 5. The Feedback Loop

Your ratings directly influence future recommendations. Here's the cycle:

```
You use a skill
       │
       ▼
You rate it (stars, helpful, task-succeeded)
       │
       ├──→ record_rating() updates quality metrics
       │         │
       │         ▼
       │    Aggregated scores updated:
       │    avg rating, helpful %, success correlation
       │
       ├──→ learn_from_feedback() records context pattern
       │         │
       │         ▼
       │    Context hash + skill stored with success flag
       │    (skills with >70% success rate get recommended)
       │
       └──→ Semantic matcher updated (if fastembed installed)
                 │
                 ▼
            Session embedding stored for similarity matching
                 │
                 ▼
      Future similar sessions → this skill recommended
```

### What Each Rating Field Affects

| Field | Effect on Recommendations |
|:------|:--------------------------|
| **Stars** | Drives the average rating and top-rated rankings |
| **Helpful** | Directly fed to `learn_from_feedback()` -- high helpful % increases future confidence |
| **Task Succeeded** | Updates `success_correlation` metric -- skills with high success rates get recommended more |
| **Review** | Informational only -- helps other users decide, doesn't affect the algorithm |

### Practical Example

You're working on a Python API project. The engine recommends `api-design-patterns` at 80% confidence. You use it, rate it 5 stars with `--helpful` and `--task-succeeded`. Next week, you start a similar API project. The engine now recommends `api-design-patterns` at 90%+ confidence because:

1. Pattern learning recorded the success in this context type
2. Semantic similarity matches the new project to the old session
3. The high rating confirms the skill's quality

Over time, the system converges on recommending the right skills for your workflow.

---

## 6. Database Locations

Ratings and recommendation data are stored in SQLite databases:

| Database | Location | Contents |
|:---------|:---------|:---------|
| Ratings | `~/.cortex/data/skill-ratings.db` | Stars, reviews, quality metrics, usage tracking |
| Recommendations | `~/.cortex/data/skill-recommendations.db` | Recommendation history, context patterns, feedback |
| Semantic cache | `~/.cortex/data/skill_semantic_cache/` | Embeddings (only if `fastembed` installed) |

These are local to your machine. No data is sent externally.

---

## Summary

You've learned how to:

- Get AI-powered skill recommendations with `cortex skills recommend` and the TUI AI Assistant
- Rate skills from the CLI (`cortex skills rate`) and TUI (`Ctrl+R`)
- View quality metrics, distributions, and reviews with `cortex skills ratings`
- Discover top-rated skills with `cortex skills top-rated`
- Understand how the four recommendation strategies combine
- See how ratings feed back into the engine to improve future suggestions

## Next Steps

- [Skills Guide]({% link guides/skills.md %}) -- full skill catalog by category
- [AI Intelligence Guide]({% link guides/ai-intelligence.md %}) -- how context detection and agent recommendations work
- [Configuration]({% link getting-started/configuration.md %}) -- customize profiles and flag sets
- Install semantic matching for richer recommendations: `pip install claude-cortex[ai]`
