---
layout: default
title: Skill Recommendation & Review Learning
nav_order: 10
parent: Development
---

# Skill Recommendation & Review Learning System

**Version**: 2.0
**Last Updated**: 2026-02-12
**Status**: Current

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agent-to-Skill Conversion](#agent-to-skill-conversion)
4. [Context Detection](#context-detection)
5. [Recommendation Strategies](#recommendation-strategies)
6. [Review Learning Pipeline](#review-learning-pipeline)
7. [CLI Reference](#cli-reference)
8. [Review Gate](#review-gate)
9. [Specialist Review Integration](#specialist-review-integration)
10. [Data Model](#data-model)
11. [Extending the System](#extending-the-system)

---

## Overview

The Skill Recommendation System is a self-improving feedback loop that learns which
skills matter in which contexts. It combines four recommendation strategies
(semantic, rule-based, agent-based, pattern-based) and feeds review outcomes back
into its learning database so future recommendations improve automatically.

### Key Capabilities

- Recommends skills based on file changes, active agents, and historical patterns
- Learns from specialist review outcomes (which perspectives found real issues)
- Records session successes for semantic similarity matching
- Provides CLI commands and TUI integration for recommendations and feedback
- Gates task completion via review-required skill loading

### Design Principles

```
Learn from reviews > Hard-code rules
Context detection > Static config
Best-effort learning > Pipeline-blocking recording
Productive perspectives only > All perspectives equal
```

---

## Architecture

### System Diagram

```
                          ┌──────────────────────────┐
                          │   specialist-review.sh    │
                          │ provider-aware review CLI │
                          └───────────┬──────────────┘
                                      │ review markdown
                                      v
┌──────────────┐    ┌─────────────────────────────────┐
│ git changes  │───>│        review_parser.py          │
│ (context)    │    │  Parse perspectives & findings   │
└──────────────┘    │  Map perspectives -> skills      │
       │            │  Gate on verdict                 │
       │            └───────────┬─────────────────────┘
       │                        │ skills + context
       v                        v
┌──────────────────────────────────────────────────────┐
│              SkillRecommender                         │
│                                                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────────────┐│
│  │  Strategy 0 │ │  Strategy 1 │ │  Strategy 2        ││
│  │  Semantic   │ │  Rule-Based │ │  Agent-Based       ││
│  │  Similarity │ │  File Globs │ │  AGENT_SKILL_MAP   ││
│  └─────┬──────┘ └─────┬──────┘ └────────┬───────────┘│
│        │              │                  │            │
│        v              v                  v            │
│  ┌────────────────────────────────────────────┐      │
│  │  Strategy 3: Pattern-Based (SQLite history) │      │
│  └──────────────────────┬─────────────────────┘      │
│                         │                             │
│                         v                             │
│  ┌──────────────────────────────────────────────┐    │
│  │  record_skill_success(context, skills)        │    │
│  │  -> context_patterns table                    │    │
│  │  -> SemanticMatcher embeddings                │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Module Map

| Module | Purpose |
|--------|---------|
| `claude_ctx_py/skill_recommender.py` | Core recommendation engine |
| `claude_ctx_py/review_parser.py` | Review outcome parser and learning bridge |
| `claude_ctx_py/intelligence/base.py` | Context detection (`ContextDetector`, `SessionContext`) |
| `claude_ctx_py/intelligence/semantic.py` | Embedding-based similarity matching |
| `claude_ctx_py/cmd_ai.py` | CLI handlers for `cortex ai` commands |
| `claude_ctx_py/cmd_review.py` | Review gate command |
| `claude_ctx_py/core/skills.py` | CLI handlers for `cortex skills` commands |
| `skills/agent-loops/scripts/specialist-review.sh` | Review pipeline script |

---

## Agent-to-Skill Conversion

### Background

Commit `5c90af1` converted 23 agents into skills with JIT (just-in-time) activation.
This was the largest structural change to the recommendation system.

### What Changed

- **23 agents** became **17 new skills** plus enhancements to 10 existing skills
- **87 agent definitions** archived to `archive/agents/`
- Agent frontmatter now references skills rather than embedding knowledge directly
- `AGENT_SKILL_MAP` updated to reflect the new skill names

### New Skills Created

| Skill | Converted From |
|-------|----------------|
| `compliance-audit` | compliance-auditor agent |
| `mermaid-diagramming` | mermaid-expert agent |
| `tutorial-design` | tutorial-engineer agent |
| `reference-documentation` | reference-builder agent |
| `product-strategy` | product-strategist agent |
| `interaction-design` | interaction-designer agent |
| `prompt-engineering` | prompt-engineer agent |
| `evaluator-optimizer` | refiner agent |
| `knowledge-synthesis` | knowledge-synthesizer agent |
| `research-methodology` | search-specialist agent |
| `incident-response` | incident-responder agent |
| `openapi-specification` | openapi-expert agent |
| `socratic-questioning` | socratic-mentor agent |
| `legacy-modernization` | legacy-modernizer agent |
| `requirements-discovery` | requirements-analyst agent |
| `build-optimization` | build-engineer agent |
| `github-actions-workflows` | github-actions-expert agent |

### Impact on Recommendations

Skills load on-demand instead of being pre-activated as full agents.
The `AGENT_SKILL_MAP` now maps built-in Claude Code agent types (like
`security-auditor`, `rest-expert`) to the cortex skill catalog, so
recommendations adapt based on which agent is currently active.

---

## Context Detection

### How Context is Built

`ContextDetector.detect_from_files()` analyzes file paths and produces a
`SessionContext`:

```python
SessionContext(
    files_changed=["auth/login.py", "tests/test_login.py"],
    file_types={".py"},
    directories={"auth", "tests"},
    has_tests=True,       # "test" in filename
    has_auth=True,        # "auth" in path
    has_api=False,        # "api" or "routes" in path
    has_frontend=False,   # .tsx, .jsx, .vue, .html
    has_backend=True,     # .py, .go, .java, .rs
    has_database=False,   # "db", "migration", "schema"
    active_agents=[...],
    errors_count=0,
    test_failures=0,
)
```

### Context Sources

| Source | Function | Used By |
|--------|----------|---------|
| Git changes | `get_current_context()` | `cortex review`, `cortex ai recommend` |
| File list | `ContextDetector.detect_from_files()` | `review_parser.ingest_review()` |
| Manual | `SessionContext(...)` | Tests, direct API usage |

### Context Hash

Each context is hashed using its file types, boolean signals, and active agents.
This hash is the key for the `context_patterns` table — when the same kind of
context recurs, historical skill successes boost future recommendations.

---

## Recommendation Strategies

The recommender runs four strategies in parallel and merges the results.
When multiple strategies recommend the same skill, confidence is boosted.

### Strategy 0: Semantic Similarity

Uses `SemanticMatcher` (optional, requires `fastembed`) to find past sessions
with similar context and surface the skills that worked in those sessions.

```
Current context --embed--> find_similar(top_k=10, min=0.6)
                           --> aggregate skill scores
                           --> recommend top matches
```

Falls back gracefully if `fastembed` is not installed.

### Strategy 1: Rule-Based

Matches file glob patterns against changed files:

| Pattern | Skill | Confidence |
|---------|-------|------------|
| `**/auth/**/*.py`, `**/security/**` | `owasp-top-10` | 0.90 |
| `**/*.test.py`, `**/tests/**` | `testing-anti-patterns` | 0.85 |
| `**/*.tf`, `**/terraform/**` | `terraform-best-practices` | 0.95 |
| `**/k8s/**`, `**/kubernetes/**` | `kubernetes-deployment-patterns` | 0.90 |
| `**/.github/workflows/**` | `github-actions-workflows` | 0.95 |
| `**/openapi*.yml` | `openapi-specification` | 0.90 |
| `**/routes/**`, `**/api/**` | `api-design-patterns` | 0.85 |
| `**/migrations/**`, `**/*.sql` | `database-design-patterns` | 0.85 |
| `**/docs/**`, `**/*.mdx` | `documentation-production` | 0.80 |

Rules are stored in `skills/recommendation-rules.json` and can be customized.

### Strategy 2: Agent-Based

Maps active Claude Code agents to skills via `AGENT_SKILL_MAP`:

```python
AGENT_SKILL_MAP = {
    "security-auditor": [
        ("owasp-top-10", 0.95),
        ("threat-modeling-techniques", 0.9),
        ("secure-coding-practices", 0.85),
        ("security-testing-patterns", 0.8),
    ],
    "rest-expert": [
        ("api-design-patterns", 0.9),
        ("openapi-specification", 0.85),
        ("api-gateway-patterns", 0.8),
    ],
    # ... 20+ agent mappings
}
```

### Strategy 3: Pattern-Based (Historical)

Queries the `context_patterns` table for contexts with `success_rate > 0.7`
and surfaces skills that were previously successful. This is the strategy
that improves from review feedback and `record-success` calls.

### Confidence Merging

When strategies overlap:
- Same skill from rule + agent: confidence += 0.05
- Same skill from pattern: confidence += 0.03
- Same skill from semantic: already has base score, boosted on overlap
- Maximum confidence capped at 0.99

### Auto-Activation Threshold

Skills with confidence >= 0.80 are flagged `auto_activate=True`.
The `cortex ai auto-activate` command activates these.

---

## Review Learning Pipeline

### Overview

Specialist reviews produce rich outcome data — which perspectives found issues,
at what severity, with what verdict. The review parser extracts this data and
feeds it back into the SkillRecommender so future recommendations improve.

### How It Works

```
specialist-review.sh runs Claude review
  -> writes review to .agents/reviews/review-TIMESTAMP.md
  -> calls: python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE"
```

The review parser:

1. **Parses** the review markdown (perspectives, findings, verdict, file paths)
2. **Identifies productive perspectives** — those with at least one finding
3. **Maps perspectives to skills** via `PERSPECTIVE_SKILL_MAP`
4. **Gates on verdict**:
   - `APPROVE` -> skip (nothing actionable to learn)
   - `APPROVE WITH CHANGES` -> record skills
   - `REQUEST CHANGES` -> record skills
5. **Records** via `SkillRecommender.record_skill_success(context, skills)`

### Perspective-to-Skill Map

Derived from `skills/agent-loops/references/perspective-catalog.md`:

| Perspective | Mapped Skills |
|-------------|---------------|
| Correctness | *(none — foundational, always applies)* |
| Security | `owasp-top-10`, `secure-coding-practices`, `threat-modeling-techniques`, `security-testing-patterns` |
| Performance | `python-performance-optimization`, `react-performance-optimization`, `workflow-performance`, `database-design-patterns` |
| Maintainability | `code-quality-workflow` |
| Testing | `python-testing-patterns`, `test-generation`, `test-driven-development`, `testing-anti-patterns` |
| Architecture | `system-design`, `api-design-patterns`, `microservices-patterns`, `event-driven-architecture` |
| Infrastructure | `terraform-best-practices`, `kubernetes-deployment-patterns`, `kubernetes-security-policies`, `helm-chart-patterns`, `gitops-workflows` |
| API Contract | `api-design-patterns`, `api-gateway-patterns` |
| Accessibility | `accessibility-audit` |
| UX / Design | `ux-review`, `ui-design-aesthetics` |

### Supported Review Formats

The parser handles two formats found in production reviews:

**Format 1: Numbered-bold perspectives with letter-prefix findings**
```markdown
## Phase 1: Triage — Selected Perspectives
1. **Correctness** — Always included.
2. **Security** — Auth code detected.

### C-1: Argument parsing crashes
**File:** `src/parser.py:59-67`
**Severity:** IMPORTANT

### S-1: Missing input validation
**File:** `src/auth.py:120`
**Severity:** CRITICAL
```

**Format 2: Specialists line with priority-prefix findings**
```markdown
**Specialists**: Security, Architecture, Configuration Consistency

#### P0-1: hooks.json references deleted scripts
**File**: `hooks/hooks.json`
**Severity:** CRITICAL

#### P1-1: Manpage lists nonexistent commands
**Files**: `docs/reference/cortex.1`
**Severity:** HIGH
```

### Why Only Productive Perspectives

Not all perspectives generate findings. A "clean" perspective (no findings) is
ambiguous — it could mean the code is genuinely clean in that dimension, or the
perspective was irrelevant for the change. Recording these as successes would
add noise to the learning signal.

Only perspectives that actually found issues produce a clear signal: "this skill
domain was relevant and productive for this kind of change."

### Why APPROVE Skips Recording

When a review produces an `APPROVE` verdict, no perspective found actionable
issues. There is nothing to learn from — no productive perspective, no useful
skill signal. Only reviews that surface real issues (`APPROVE WITH CHANGES`,
`REQUEST CHANGES`) contribute to learning.

---

## CLI Reference

### Skills Commands

```bash
# List and inspect
cortex skills list                              # All available skills
cortex skills info <skill>                      # Detailed skill information
cortex skills validate [--all] [skill...]       # Validate skill metadata

# Recommendations
cortex skills recommend                         # AI-powered recommendations
cortex skills context                           # Generate skill-context.md
cortex skills feedback <skill> helpful|not-helpful

# Analytics
cortex skills metrics [skill]                   # Usage metrics
cortex skills analytics [--metric trending|roi|effectiveness]
cortex skills trending [--days 30]              # Trending skills over time
cortex skills report [--format text|json|csv]   # Comprehensive report

# Ratings
cortex skills rate <skill> --stars 1-5 [--review "text"]
cortex skills ratings <skill>                   # View ratings
cortex skills top-rated [--category CAT] [--limit N]
cortex skills export-ratings [--format json|csv]
```

### AI Commands

```bash
# Recommendations
cortex ai recommend                             # Show context-aware recommendations
cortex ai auto-activate                         # Activate high-confidence skills

# Learning
cortex ai record-success [--outcome "description"]  # Record session for learning
cortex ai ingest-review <review-file>                # Ingest review into learning

# Export
cortex ai export [--output file.json]           # Export recommendations to JSON
```

### Review Commands

```bash
cortex review [--dry-run] [-c CONTEXT]          # Run review gate
```

### Direct Module Usage

```bash
# Parse and ingest a review (best-effort, exits 0)
python3 -m claude_ctx_py.review_parser .beads/reviews/review-20260209-135121.md
```

---

## Review Gate

### Purpose

The review gate (`cortex review`) is a pre-completion check that requires
skill loading before a task can be considered done. It uses the
SkillRecommender to determine which skills are most relevant.

### How It Works

1. Detects context from current git changes
2. Gets top 5 skill recommendations from `SkillRecommender`
3. Outputs a mandatory skill list that must be loaded
4. Generates a completion checklist

### Extra Context

Additional signals can be injected to influence recommendations:

```bash
cortex review -c security -c database
```

This adds the specified context words to the detection signals, potentially
triggering additional rule-based recommendations.

---

## Specialist Review Integration

### Pipeline Flow

```
1. specialist-review.sh [--git] [-- paths...]
   -> Captures diff (git diff or file or stdin)
   -> Truncates to 2000 lines if needed
   -> Inlines perspective catalog + diff into prompt template
   -> Invokes the provider chain (Claude first, self-last when detectable)
   -> Captures output to .agents/reviews/review-TIMESTAMP.md

2. On success:
   -> python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE" (best-effort)
   -> Prints output file path to stdout

3. On failure:
   -> Preserves partial output if any
   -> Reports error to stderr
```

### Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `AGENT_LOOPS_LLM_PROVIDER` | `auto` | Force a specific review provider or keep provider auto-selection |
| `AGENT_LOOPS_SELF_PROVIDER` | auto-detect | Keep same-model shell-outs last when the current agent is known |
| `CLAUDE_TIMEOUT` | 300s | Max review duration |
| `CLAUDE_MAX_BUDGET` | $0.50 | Max spend per review |

### Best-Effort Guarantee

The review_parser call uses `2>/dev/null || true` — it will never cause
the review script to fail. Even if the parser encounters a malformed review,
an import error, or a database problem, the review output is still delivered.

---

## Data Model

### SQLite Tables

Located at `~/.claude/data/skill-recommendations.db`:

**`recommendations_history`** — Every recommendation made:
```sql
id INTEGER PRIMARY KEY
timestamp TEXT NOT NULL
skill_name TEXT NOT NULL
confidence REAL NOT NULL
context_hash TEXT NOT NULL
was_activated BOOLEAN DEFAULT 0
was_helpful BOOLEAN NULL
reason TEXT
```

**`recommendation_feedback`** — User feedback on recommendations:
```sql
id INTEGER PRIMARY KEY
recommendation_id INTEGER  -- FK to recommendations_history
timestamp TEXT NOT NULL
helpful BOOLEAN NOT NULL
comment TEXT
```

**`context_patterns`** — Learned context-to-skill mappings:
```sql
id INTEGER PRIMARY KEY
context_hash TEXT UNIQUE NOT NULL
file_patterns TEXT   -- JSON array of file types
active_agents TEXT   -- JSON array
successful_skills TEXT  -- JSON array
success_rate REAL    -- 0.0-1.0, boosted by +0.1 per success
last_updated TEXT
```

### Learning Flow

```
record_skill_success(context, skills)
  -> compute context_hash
  -> UPSERT context_patterns:
     - new: insert with success_rate = 0.8
     - existing: merge skills, rate += 0.1 (capped at 1.0)
  -> if SemanticMatcher available:
     - add_session({files, context, agents, skills})
```

---

## Extending the System

### Adding a New Perspective Mapping

Edit `PERSPECTIVE_SKILL_MAP` in `claude_ctx_py/review_parser.py`:

```python
PERSPECTIVE_SKILL_MAP["data engineering"] = [
    "database-design-patterns",
    "event-driven-architecture",
]
```

Then add the perspective to `skills/agent-loops/references/perspective-catalog.md`
so the specialist review can select it.

### Adding a New Recommendation Rule

Add to the `_get_default_rules()` method in `claude_ctx_py/skill_recommender.py`:

```python
{
    "trigger": {
        "file_patterns": ["**/graphql/**", "**/*.graphql"]
    },
    "recommend": [
        {
            "skill": "api-design-patterns",
            "confidence": 0.9,
            "reason": "GraphQL schema files detected"
        }
    ]
}
```

Or add directly to `~/.claude/skills/recommendation-rules.json` for
user-specific rules.

### Adding a New Agent Mapping

Add to `AGENT_SKILL_MAP` in `claude_ctx_py/skill_recommender.py`:

```python
"new-agent-type": [
    ("relevant-skill-1", 0.9),
    ("relevant-skill-2", 0.85),
],
```

### Testing

Run the full test suite:

```bash
pytest tests/unit/test_review_parser.py -v        # Review parser (26 tests)
pytest tests/unit/test_skill_recommender.py -v     # Recommender (24 tests)
```
