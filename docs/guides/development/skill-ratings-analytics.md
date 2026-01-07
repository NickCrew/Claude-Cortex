---
layout: default
title: Skill Ratings & Analytics
nav_order: 9
parent: Development
---

# Skill Ratings & Analytics

Community-driven quality feedback and data-driven skill optimization.

---

## Skill Rating System ⭐

Rate skills and provide feedback to improve quality across the ecosystem.

### Overview

The rating system collects community feedback on skill quality, usefulness, and effectiveness. Ratings influence recommendations and help identify skills that need improvement.

### Rating a Skill

**CLI:**
```bash
# Rate a skill (1-5 stars)
cortex skills rate owasp-top-10 --stars 5

# Add a review
cortex skills rate owasp-top-10 --stars 5 \
  --review "Still the best security checklist"

# Mark as helpful/not helpful
cortex skills feedback owasp-top-10 --helpful
cortex skills feedback owasp-top-10 --not-helpful
```

**TUI:**
```bash
cortex tui
# Press 5 for Skills view
# Select a skill
# Press Ctrl+R to rate
```

**Interactive Rating Dialog:**
```
┌─────────────────────────────────┐
│ Rate Skill: owasp-top-10        │
├─────────────────────────────────┤
│ Stars: ⭐⭐⭐⭐⭐               │
│                                 │
│ Review (optional):              │
│ [ Still the best security... ] │
│                                 │
│ [Submit]  [Cancel]              │
└─────────────────────────────────┘
```

### Auto-Rating Prompts

The TUI automatically prompts for ratings after you've used a skill multiple times:

```
┌───────────────────────────────────────┐
│ 💡 Rate Your Experience               │
├───────────────────────────────────────┤
│ You've used owasp-top-10 5 times.     │
│ How would you rate it?                │
│                                       │
│ ⭐⭐⭐⭐⭐                           │
│                                       │
│ [Rate Now]  [Remind Later]  [Dismiss] │
└───────────────────────────────────────┘
```

**Trigger Conditions:**
- Skill used 3+ times
- No rating in last 30 days
- Recent activations (within 7 days)

### Viewing Ratings

```bash
# Show ratings for a skill
cortex skills ratings owasp-top-10

# Output:
# owasp-top-10 Ratings
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Average Rating: ⭐⭐⭐⭐⭐ (4.8/5.0)
# Total Ratings: 127
# 
# Distribution:
# 5★ ████████████████████ 89 (70%)
# 4★ ████████             24 (19%)
# 3★ ███                  10 (8%)
# 2★ █                     3 (2%)
# 1★                       1 (1%)
#
# Helpful Votes: 115 / 127 (91%)
# Success Rate: 94% (when used with security-auditor)
# Token Efficiency: -15.2K avg (high efficiency)

# Show top-rated skills
cortex skills top-rated --limit 10

# Export ratings data
cortex skills export-ratings --format csv > ratings.csv
cortex skills export-ratings --format json > ratings.json
```

### Rating Data

**Storage:** `~/.claude/data/skill-ratings.db` (SQLite)

**Schema:**
```sql
CREATE TABLE skill_ratings (
    id INTEGER PRIMARY KEY,
    skill_name TEXT NOT NULL,
    stars INTEGER CHECK(stars BETWEEN 1 AND 5),
    review TEXT,
    helpful_vote INTEGER,  -- 1=helpful, 0=not helpful
    user_hash TEXT,  -- Anonymous identifier
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    context_hash TEXT,  -- Session context when rated
    success_outcome BOOLEAN  -- Task completed successfully?
);
```

### Benefits

- ✅ **Quality Signals** — Community consensus on skill effectiveness
- ✅ **Feedback Loops** — Authors see what needs improvement
- ✅ **Better Discovery** — Top-rated skills surface in recommendations
- ✅ **Privacy First** — Anonymous, no personal data collected

---

## Skill Analytics 📊

Data-driven insights into skill usage, effectiveness, and trends.

### Overview

Analytics track skill performance metrics: usage frequency, token efficiency, success rates, and trends over time.

### Usage Metrics

```bash
# Show usage metrics for a skill
cortex skills metrics owasp-top-10

# Output:
# owasp-top-10 Metrics
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Activations: 127 (↑ 15% this month)
# Total Sessions: 89
# Avg Session Duration: 12m 34s
# Success Rate: 94% (84 successful / 89 total)
#
# Token Efficiency:
#   Avg Saved: -15.2K tokens/session
#   Total Saved: -1.35M tokens
#   Efficiency Grade: A+
#
# Co-Usage Patterns:
#   ↗️ security-auditor (89% co-activation)
#   ↗️ threat-modeling-techniques (45%)
#   ↗️ api-security-patterns (32%)

# Reset all metrics (development only)
cortex skills metrics --reset
```

### Analytics Dashboard

```bash
# Show comprehensive analytics
cortex skills analytics

# Filter by metric type
cortex skills analytics --metric trending
cortex skills analytics --metric roi
cortex skills analytics --metric effectiveness
cortex skills analytics --metric tokens
```

**Example Output:**
```
╭─────────────────────────────────────────────╮
│ Skill Analytics Dashboard                   │
├─────────────────────────────────────────────┤
│ Top Performers (Last 30 Days)               │
│                                             │
│ 1. owasp-top-10                             │
│    📊 127 uses │ ⭐ 4.8 │ 💰 -1.35M tokens   │
│    ↗️ +15% vs last month                    │
│                                             │
│ 2. python-testing-patterns                  │
│    📊 89 uses │ ⭐ 4.6 │ 💰 -890K tokens     │
│    ↗️ +22% vs last month                    │
│                                             │
│ 3. api-design-patterns                      │
│    📊 78 uses │ ⭐ 4.7 │ 💰 -1.12M tokens    │
│    ↘️ -3% vs last month                     │
├─────────────────────────────────────────────┤
│ Trending Skills                             │
│  🔥 kubernetes-security-policies (+89%)     │
│  🔥 gitops-workflows (+67%)                 │
│  🔥 event-driven-architecture (+45%)        │
╰─────────────────────────────────────────────╯
```

### Trending Analysis

```bash
# Show trending skills (usage growth)
cortex skills trending --days 30

# Output:
# Trending Skills (Last 30 Days)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔥 kubernetes-security-policies
#    📈 +89% growth (12 → 23 uses)
#    ⭐ 4.9 rating (new skill)
#
# 🔥 gitops-workflows  
#    📈 +67% growth (18 → 30 uses)
#    ⭐ 4.7 rating
#
# 🔥 event-driven-architecture
#    📈 +45% growth (22 → 32 uses)
#    ⭐ 4.5 rating
```

### Reports

```bash
# Generate comprehensive report
cortex skills report --format text
cortex skills report --format json > report.json
cortex skills report --format csv > report.csv
cortex skills report --format html > report.html

# Example HTML report includes:
# - Executive summary with key metrics
# - Usage trends (chart)
# - Rating distribution (chart)
# - Token efficiency analysis
# - Success rate correlations
# - Recommendations for improvement
```

### Success Rate Correlation

Track which skills correlate with successful outcomes:

```bash
# Record successful session
cortex ai record-success --outcome "feature complete"

# View success correlations
cortex skills analytics --metric success_rate

# Output:
# Skills with Highest Success Correlation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# python-testing-patterns: 96% success when used
# owasp-top-10: 94% success when used
# api-design-patterns: 92% success when used
```

### Token Efficiency

Measure how much token usage skills save/add:

```bash
# Skills ranked by token efficiency
cortex skills analytics --metric tokens

# Output:
# Token Efficiency Rankings
# ━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. python-concurrency-patterns: -18.2K avg (A+)
# 2. owasp-top-10: -15.2K avg (A+)
# 3. kubernetes-deployment: -12.4K avg (A)
#
# Negative = saves tokens (good)
# Positive = adds tokens (acceptable for value)
```

### Analytics Data

**Storage:** `~/.claude/data/skill-analytics.db` (SQLite)

**Tracked Metrics:**
- Activation count and frequency
- Session duration
- Token usage delta
- Success/failure outcomes
- Co-activation patterns
- Temporal trends

### Benefits

- ✅ **Data-Driven Decisions** — Know which skills work best
- ✅ **ROI Tracking** — Measure token efficiency gains
- ✅ **Trend Detection** — Spot emerging patterns early
- ✅ **Optimization** — Identify underperforming skills

---

## AI Skill Recommendations 🤖

Intelligent skill suggestions based on context, patterns, and ratings.

### Overview

The recommendation engine suggests skills based on:
- **Context analysis** (files, project type, recent changes)
- **Agent patterns** (active agents → complementary skills)
- **Historical success** (what worked in similar situations)
- **Community ratings** (highly-rated skills prioritized)

### Getting Recommendations

```bash
# Get AI recommendations
cortex skills recommend

# Output:
# 🤖 AI Skill Recommendations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔴 owasp-top-10 [95% confidence] [AUTO]
#    Reason: Auth code detected in 3 files
#    Triggers: auth/*, security/*
#    Rating: ⭐⭐⭐⭐⭐ 4.8 (127 ratings)
#
# 🟡 python-testing-patterns [78% confidence]
#    Reason: Similar projects found this helpful
#    Used by: 15 similar Python/FastAPI projects
#    Rating: ⭐⭐⭐⭐ 4.6 (89 ratings)
#
# 🟢 api-design-patterns [65% confidence]
#    Reason: FastAPI detected, API skills recommended
#    Rating: ⭐⭐⭐⭐ 4.7 (78 ratings)

# Auto-activate high-confidence skills (≥80%)
cortex skills recommend --auto-activate

# Explain recommendation reasoning
cortex skills recommend --explain owasp-top-10

# Provide feedback
cortex skills feedback owasp-top-10 --helpful
```

### TUI Integration

```bash
cortex tui
# Press 5 for Skills view
# Recommendations appear at top with confidence scores
# Press Space on recommendation to activate
```

### Recommendation Rules

**File:** `skills/recommendation-rules.yaml`

```yaml
rules:
  - trigger:
      file_patterns: ["**/auth/**/*.py", "**/security/**"]
    recommend:
      - skill: owasp-top-10
        confidence: 0.9
        reason: "Auth code detected, security review recommended"
      - skill: secure-coding-practices
        confidence: 0.85

  - trigger:
      active_agents: ["kubernetes-architect"]
    recommend:
      - skill: kubernetes-security-policies
        confidence: 0.9
      - skill: gitops-workflows
        confidence: 0.8
```

### Confidence Scores

- **≥80% (🔴 Red)** — Auto-activate recommended
- **60-80% (🟡 Yellow)** — Review and activate manually
- **<60% (🟢 Green)** — Optional, low priority

### Benefits

- ✅ **Context-Aware** — Suggestions match your current work
- ✅ **Time Saving** — No manual searching required
- ✅ **Quality First** — Ratings influence recommendations
- ✅ **Learning System** — Improves from feedback

---

## Best Practices

### For Rating

- **Be Honest** — Honest feedback improves the ecosystem
- **Be Specific** — Add reviews explaining why (optional)
- **Consider Context** — Rate based on skill fit for task
- **Update Ratings** — Re-rate after skill updates

### For Analytics

- **Track Regularly** — Check metrics monthly
- **Export Data** — Back up analytics for analysis
- **Act on Insights** — Use data to optimize workflow
- **Share Trends** — Help team discover effective skills

### For Recommendations

- **Trust High Confidence** — ≥80% rarely wrong
- **Review Medium** — 60-80% worth manual check
- **Provide Feedback** — Improves future recommendations
- **Watch Patterns** — Learn which skills work together

---

## Related Features

- **[Skill Composition & Versioning](skill-composition-versioning.html)** — Building modular skills
- **[AI Intelligence Guide](AI_INTELLIGENCE_GUIDE.html)** — Complete AI system
- **[Skills Guide](../skills.html)** — Skill system overview

---

*For implementation details, see `claude_ctx_py/skill_rating.py`, `skill_recommender.py`, and `skill_rating_prompts.py`*
