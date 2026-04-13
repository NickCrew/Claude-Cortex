---
layout: default
title: Skill Recommendation System
parent: Reference
nav_order: 6
permalink: /reference/skill-recommendation-system/
---

# Skill Recommendation System

This is the developer-facing reference for Cortex's skill recommendation
pipeline. It covers the runtime architecture, review-learning path, and the
current limits of the implementation.

For a user-facing guide to making the most of Cortex's skill suggestions,
see [Working with Skills]({% link guides/working-with-skills.md %}). That
page covers the mental model, feedback loop, and troubleshooting without
the internals below.

## Scope

The skill system has two jobs:

1. **Suggest skills in the moment**
   - via the prompt hook, `cortex skills recommend`, and watch mode
2. **Learn which skills were actually useful**
   - from feedback, recorded successes, and ingested review artifacts

The core implementation lives in `claude_ctx_py/skill_recommender.py`.

## Core Objects

### `SkillRecommendation`

Represents one suggested skill:

- `skill_name`
- `confidence`
- `reason`
- `triggers`
- `related_agents`
- `estimated_value`
- `auto_activate`

`should_notify()` currently treats `confidence >= 0.7` as user-visible.

### `SkillRecommender`

Coordinates:

- SQLite initialization
- loading `recommendation-rules.json`
- optional semantic matching
- recommendation generation
- recommendation history
- feedback recording
- learned context-pattern updates

## Recommendation Pipeline

`SkillRecommender.recommend_for_context()` executes in this order:

1. semantic similarity
2. rule-based recommendations
3. agent-based recommendations
4. pattern-based recommendations

Results are merged into a single `Dict[str, SkillRecommendation]` keyed by skill
name. Later strategies can boost an existing recommendation's confidence:

- rule-based overlap adds `+0.05`
- agent-based overlap adds `+0.05`
- pattern-based overlap adds `+0.03`

Confidence is capped at `0.99`.

## Strategy Details

### Semantic similarity

Uses the optional `SemanticMatcher` from `claude_ctx_py/intelligence/semantic.py`.

Input:

- changed file paths
- serialized `SessionContext`
- optional skills used in a past successful session

Behavior:

- finds similar sessions with `min_similarity=0.6`
- aggregates the skills that appeared in those sessions
- normalizes the score into a recommendation confidence

This is the most context-sensitive strategy, but it only contributes when the
embedding dependency is installed and the semantic cache already contains useful
history.

### Rule-based

Rules come from `recommendation-rules.json` and are file-pattern driven.

Examples from the current defaults:

- auth/security paths -> `owasp-top-10`, `secure-coding-practices`
- test files -> `testing-anti-patterns`, `test-driven-development`
- `docs/`, `README.md`, or `.mdx` files -> `documentation-production`
- OpenAPI/Swagger files -> `openapi-specification`, `api-design-patterns`

This is the most reliable strategy for first-run recommendations because it does
not require history.

### Agent-based

Maps `SessionContext.active_agents` through `AGENT_SKILL_MAP`.

Examples:

- `security-auditor` -> `owasp-top-10`, `secure-coding-practices`
- `docs-architect` -> `documentation-production`, `reference-documentation`
- `react-specialist` -> `react-performance-optimization`, `design-system-architecture`

Implementation note:

- the strategy exists today
- most CLI/watch flows do not populate `active_agents`
- this means it is currently strongest in programmatic integrations, not the
  default CLI path

### Pattern-based

Reads `context_patterns` rows from SQLite where `success_rate > 0.7`, then
recommends skills that repeatedly succeeded in similar contexts.

The context hash currently includes:

- file types
- `has_auth`
- `has_api`
- `has_frontend`
- `has_backend`
- sorted active agents

This is intentionally coarse-grained. It favors stable buckets over overly
precise matching.

## Review Learning

Review learning is the most concrete bridge between verification outcomes and
future skill suggestions.

### Entry point

```bash
cortex ai ingest-review path/to/review.md
```

### Implementation

`claude_ctx_py/review_parser.py`:

1. parses the review markdown
2. extracts the selected perspectives
3. keeps only productive perspectives that actually found issues
4. maps those perspectives through `PERSPECTIVE_SKILL_MAP`
5. reconstructs a file-based context from the review's `**File:**` annotations
6. calls `SkillRecommender.record_skill_success()`

### Why this matters

This means specialist reviews can improve future skill suggestions without
humans manually tagging every session. If a review repeatedly finds security
problems, Cortex can learn to suggest the security skills earlier next time.

## Feedback and Storage

### Recommendation history

Every recommendation is recorded in:

- `recommendations_history`

Tracked fields include:

- timestamp
- skill name
- confidence
- context hash
- reason
- whether it was activated
- whether it was later marked helpful

### Explicit feedback

```bash
cortex skills feedback <skill> helpful
cortex skills feedback <skill> not-helpful
```

This records:

- a standalone feedback row in `recommendation_feedback`
- a helpful / not-helpful update against the most recent recommendation row for
  that skill, when available

### Recorded success

`record_skill_success()` updates:

- `context_patterns`
- the semantic cache, when available

This is the main write path used by review ingestion and best-effort session
success recording.

## CLI Surface

### Recommendation commands

```bash
cortex skills recommend
cortex skills context
cortex skills feedback <skill> helpful
```

### Ratings and quality signals

```bash
cortex skills rate <skill> --stars 5 --review "Great fit"
cortex skills ratings <skill>
cortex skills top-rated
cortex skills export-ratings --format json
```

These rating commands are related but distinct from recommendation feedback:

- `skills feedback` teaches the recommender whether a suggestion was useful
- `skills rate` writes richer skill quality data into `skill-ratings.db`

## Current Limits

### CLI context is git-centric

`cortex skills recommend` uses `get_current_context()` and therefore mostly sees:

- changed files from git
- derived booleans such as `has_auth`, `has_api`, and `has_frontend`

It does not currently inject:

- prompt text (see note below)
- active agents from disk
- active rules
- active modes

That is why the prompt hook and watch mode often feel more responsive than the
raw CLI recommender for "what am I doing right now?" questions.

**Prompt passthrough status.** The recommendation engine's public API
(`SkillRecommender.recommend_for_context`, `_semantic_skill_recommendations`,
`record_skill_success`, and `learn_from_feedback`) now accepts a keyword-only
`prompt` kwarg, and `SemanticMatcher._session_to_text` embeds it alongside
file-path and context-flag signals when present. The prompt auto-suggester
hook already threads `CLAUDE_HOOK_PROMPT` through this path. The CLI
`cortex skills recommend` command still does not capture or forward a prompt
argument, so its results remain file-centric. Adding a `--prompt` flag or
reading stdin would close the gap without further changes to the engine.

### Layer 1 and Layer 2 are complementary

The hook's keyword matcher should not be treated as redundant. It is the safe,
deterministic fallback that still works when:

- the package is not importable
- SQLite is unavailable
- semantic dependencies are missing
- the richer recommender throws an exception

### Session success learning is best-effort

`cortex ai record-success` feeds active agents into agent learning directly and
then makes a best-effort call into skill learning. That bridge is intentionally
non-blocking and should not be treated as the only source of truth for skill
learning.

## Keeping Docs in Sync

When changing this subsystem, check these published pages for drift:

- [Working with Skills]({% link guides/working-with-skills.md %}) -- the
  user-facing overview. Update the mental-model and troubleshooting
  sections if the recommendation strategies, failure modes, or feedback
  commands change.
- [Skills]({% link guides/skills.md %}) -- the command reference. Update
  if `cortex skills recommend`, `feedback`, `rate`, or `context` subcommand
  behavior changes.
- [AI Intelligence]({% link guides/ai-intelligence.md %}) -- the
  agent-side story. The fastembed troubleshooting callout there mirrors
  the one in Working with Skills; keep them consistent.
- [Hooks]({% link guides/hooks.md %}) -- Skill Auto-Suggester section.
  Update if the hook's input signals or confidence cutoffs change.

These are the user-visible pages most likely to mislead if the runtime
behavior they describe drifts from the code.
