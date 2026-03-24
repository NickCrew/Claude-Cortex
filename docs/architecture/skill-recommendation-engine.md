# Skill Recommendation Engine

The skill recommendation system surfaces relevant skills at three different
entry points:

- the Claude Code prompt hook in `hooks/skill_auto_suggester.py`
- `cortex skills recommend`
- watch mode in `claude_ctx_py/watch.py`

It is intentionally separate from the **agent intelligence** system behind
`cortex ai ...`. Agent recommendations decide which agents to activate. Skill
recommendations suggest which reusable knowledge packs to load.

## Architecture At A Glance

```
User prompt / changed files / git context
                  │
                  ▼
         Layer 1: keyword matcher
      hooks/skill_auto_suggester.py
                  │
                  ├─ fast, deterministic suggestions from skill-rules.json
                  │
                  ▼
     Layer 2: SkillRecommender (optional)
    claude_ctx_py/skill_recommender.py
                  │
                  ├─ semantic similarity
                  ├─ rule-based file-pattern matches
                  ├─ agent-to-skill mapping
                  └─ pattern-based history from SQLite
                  │
                  ▼
      merged, de-duplicated skill names
```

## The Two Runtime Layers

### Layer 1: Keyword matcher

**Primary file:** `hooks/skill_auto_suggester.py`

Layer 1 is the low-latency baseline that runs safely even when the Python package
or optional dependencies are unavailable.

It combines:

- prompt text from `CLAUDE_HOOK_PROMPT`
- changed files from `CLAUDE_CHANGED_FILES`
- derived keywords from file patterns, directory names, and file extensions
- git branch names
- the last few commit subjects

It matches those signals against `keywords` entries in `skills/skill-rules.json`
and prints the top matches as:

```text
Suggested skills: agent-loops, documentation-production
```

### Layer 2: SkillRecommender

**Primary file:** `claude_ctx_py/skill_recommender.py`

Layer 2 is the richer recommendation engine. It returns structured
`SkillRecommendation` objects instead of plain names.

`SkillRecommender.recommend_for_context()` runs four strategies:

| Strategy | Source | Notes |
|---|---|---|
| Semantic | previous successful sessions | optional, requires embeddings dependency |
| Rule-based | `recommendation-rules.json` file patterns | always available |
| Agent-based | `AGENT_SKILL_MAP` | only contributes when `SessionContext.active_agents` is populated |
| Pattern-based | SQLite `context_patterns` history | reuses skills that succeeded in similar contexts |

The engine merges results by `skill_name`, boosts confidence when several
strategies agree, records the recommendation event into SQLite, and returns the
sorted list.

## Important Distinction: `skill-rules.json` vs `recommendation-rules.json`

The system uses **two different rule files** for different jobs:

### `skill-rules.json`

- used by the prompt hook and watch-mode keyword matcher
- format: keyword-centric
- goal: produce fast skill-name suggestions from prompt/file/git text

### `recommendation-rules.json`

- used by `SkillRecommender`
- format: file-pattern trigger rules that emit structured recommendations
- goal: produce confidence-scored `SkillRecommendation` objects

In a normal install, the active copies live under `~/.claude/skills/`, while the
repo ships defaults in `skills/skill-rules.json` and `skills/recommendation-rules.json`.

## Data Flow

### CLI path: `cortex skills recommend`

```
git diff → get_current_context() → SkillRecommender.recommend_for_context()
                                         │
                                         ├─ semantic (optional)
                                         ├─ rule-based
                                         ├─ agent-based (usually empty in CLI today)
                                         └─ pattern-based
```

### Hook path: prompt-time suggestions

```
prompt + changed files + git context
        │
        ├─ Layer 1 keyword matcher
        └─ Layer 2 SkillRecommender enrichment (if import succeeds)
                 │
                 └─ filtered to confidence >= 0.7
```

### Watch path: live terminal suggestions

```
git polling loop
    │
    ├─ agent recommendations from IntelligentAgent
    ├─ keyword skill suggestions from _match_skills()
    └─ Layer 2 SkillRecommender enrichment
```

## Storage Model

`SkillRecommender` stores history in `~/.claude/data/skill-recommendations.db`.

Main tables:

- `recommendations_history`
  - every emitted skill recommendation
  - tracks confidence, reason, context hash, activation/helpfulness flags
- `recommendation_feedback`
  - explicit helpful / not-helpful feedback
- `context_patterns`
  - learned mapping from a coarse context hash to successful skills

Optional semantic cache:

- `~/.claude/data/skill_semantic_cache/`

## Learning Paths

The engine learns from three places:

### 1. Explicit recommendation feedback

```bash
cortex skills feedback <skill> helpful
cortex skills feedback <skill> not-helpful
```

This updates recommendation history and the feedback table.

### 2. Review ingestion

```bash
cortex ai ingest-review path/to/review.md
```

`claude_ctx_py/review_parser.py` parses structured review artifacts, maps
productive review perspectives such as `security`, `testing`, or `architecture`
to skills, and records those skills as successful for similar future contexts.

### 3. Successful sessions

```bash
cortex ai record-success --outcome "feature complete"
```

This primarily teaches the **agent** recommender, but Cortex also makes a
best-effort bridge into skill learning.

## Confidence and Display Rules

Current behavior worth documenting precisely:

- `SkillRecommendation.should_notify()` returns `True` at `confidence >= 0.7`
- the prompt hook only appends Layer 2 results with `confidence >= 0.7`
- pattern-based history only emits recommendations once its normalized confidence
  reaches `0.6`
- semantic skill recommendations are generated at lower internal thresholds, but
  may still be filtered out by the caller

## Caveats

### Agent-based skill recommendations are context-dependent

`SkillRecommender` supports an `AGENT_SKILL_MAP`, but that strategy only fires
when callers populate `SessionContext.active_agents`.

Today:

- `cortex skills recommend` builds context from git changes and does not pass active agents
- watch mode enriches from changed files only

That means file-pattern and historical strategies currently do most of the work
in normal CLI/watch usage.

### The hook must degrade gracefully

`hooks/skill_auto_suggester.py` is intentionally defensive:

- if importing `claude_ctx_py` fails, Layer 1 still works
- if `SkillRecommender` throws an exception, the hook still returns keyword matches
- if no rules can be loaded, the hook exits silently

This keeps skill suggestions safe to use in lightweight or partially installed
environments.

## File Map

| File | Responsibility |
|---|---|
| `hooks/skill_auto_suggester.py` | prompt-time keyword matcher plus optional Layer 2 enrichment |
| `claude_ctx_py/skill_recommender.py` | structured recommendation engine and SQLite learning |
| `claude_ctx_py/review_parser.py` | specialist review ingestion into skill learning |
| `claude_ctx_py/watch.py` | live watch-mode skill suggestions |
| `claude_ctx_py/intelligence/base.py` | shared `SessionContext` and `ContextDetector` |
| `skills/skill-rules.json` | repo-shipped keyword rules for Layer 1; active installs are linked under `~/.claude/skills/` |
| `skills/recommendation-rules.json` | repo-shipped trigger rules for Layer 2; active installs are linked under `~/.claude/skills/` |

## Related Docs

- [AI Intelligence Features](../AI_INTELLIGENCE.md)
- [Skill Recommendation & Review Learning](../guides/development/skill-recommendation-system.md)
- [Skills Guide](../guides/skills.md)
