# Skill Recommendation Engine

The skill recommendation engine surfaces relevant skills automatically as you work.
It operates in two layers — a fast keyword hook and a rich multi-strategy recommender —
that merge their results so every prompt gets the best suggestions the system can produce.

## Architecture Overview

```
User Prompt (UserPromptSubmit)
        │
        ▼
┌──────────────────────────┐
│  Layer 1 — Hook          │  hooks/skill_auto_suggester.py
│  (keyword matching)      │  Runs on every prompt (~50 ms)
│  skill-rules.json        │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Layer 2 — Recommender   │  claude_ctx_py/skill_recommender.py
│  (optional, ~100-200 ms) │  SkillRecommender.recommend_for_context()
│  4 strategies + SQLite   │
└────────────┬─────────────┘
             │
             ▼
      Merged, deduplicated
      skill suggestions (≤ 5)
```

### Layer 1: Hook (keyword matching)

**File**: `hooks/skill_auto_suggester.py`

The hook fires on every `UserPromptSubmit` Claude Code event. It is a standalone
Python script — no package install required.

**Signal sources**:

| Source | Example |
|--------|---------|
| Prompt text | `"fix the auth bug"` → matches `auth`, `security` keywords |
| Changed files | `src/auth/login.py` → file pattern + directory pattern matching |
| File extensions | `.py` → `python`, `.tsx` → `typescript`, `react` |
| Git branch name | `feature/k8s-deploy` → `k8s`, `deploy` keywords |
| Recent commit messages | Last 5 commit subjects, stopwords removed |

All signals are combined into a single search string and matched against the
`keywords` arrays in `skills/skill-rules.json`. Rules are scored by hit count
and the top matches are returned.

### Layer 2: SkillRecommender (multi-strategy)

**File**: `claude_ctx_py/skill_recommender.py`

When the `claude_ctx_py` package is installed (editable or pip), the hook and
the watch daemon can optionally call into the full recommendation engine. It
uses four complementary strategies, each producing `SkillRecommendation` objects
that are merged by skill name with confidence boosting when multiple strategies
agree.

| # | Strategy | Signal | Confidence Range |
|---|----------|--------|------------------|
| 0 | **Semantic** | FastEmbed similarity against past sessions | 0.5 – 0.95 |
| 1 | **Rule-based** | File type/path pattern → skill mapping | 0.6 – 0.9 |
| 2 | **Agent-based** | Active agents → associated skills (`AGENT_SKILL_MAP`) | 0.5 – 0.95 |
| 3 | **Historical** | Pattern learner (SQLite frequency data) | 0.3 – 0.8 |

When the same skill is recommended by multiple strategies, its confidence is
boosted (capped at 0.99). Only recommendations with confidence >= 0.7 are
surfaced to the user.

**Data flow**:

```
SessionContext (files, types, directories, has_* booleans)
      │
      ├─→ Semantic matching (FastEmbed embeddings)
      ├─→ Rule-based (file patterns → skills)
      ├─→ Agent-based (active agents → AGENT_SKILL_MAP)
      └─→ Historical (PatternLearner / SQLite)
      │
      ▼
Dict[skill_name, SkillRecommendation]
      │
      ▼
Sorted by confidence (descending)
```

## Integration Points

### 1. Hook (per-prompt)

After keyword matching, the hook calls `_recommender_suggestions()`:

```python
# Graceful fallback — never breaks if package is missing
try:
    from claude_ctx_py.intelligence.base import ContextDetector
    from claude_ctx_py.skill_recommender import SkillRecommender
except ImportError:
    return []
```

Context is built from `CLAUDE_CHANGED_FILES` (or git diff as fallback) via
`ContextDetector.detect_from_files()`. Results are deduplicated against keyword
matches (keyword matches appear first) and the merged list is capped at 5.

**Escape hatch**: Set `CORTEX_SKIP_RECOMMENDER=1` to disable Layer 2 in the hook
if it adds unwanted latency.

### 2. Watch daemon (background)

**File**: `claude_ctx_py/watch.py` — `WatchMode._analyze_context()`

The watch daemon already runs keyword-based `_match_skills()` on every file-change
cycle. After that, it optionally calls `SkillRecommender.recommend_for_context()`
and merges high-confidence results into the `SkillSuggestion` list.

The `SkillRecommender` is initialized once in `WatchMode.__init__()` (try/except
around the import so the daemon still works without SQLite or fastembed).

### 3. TUI auto-start

**File**: `claude_ctx_py/tui/main.py` — `AgentTUI.on_mount()`

On TUI startup, `_try_auto_start_watch_daemon()` checks whether the watch daemon
is already running. If not, it loads defaults from `cortex-config.json` and
starts the daemon in the background. This ensures users get continuous
recommendations without manually running `cortex ai watch`.

## Configuration

### skill-rules.json

Located at `skills/skill-rules.json`. Each rule maps a skill name to keywords:

```json
{
  "rules": [
    {
      "name": "test-driven-development",
      "keywords": ["test", "tdd", "coverage", "pytest", "jest"],
      "description": "Test-first development methodology"
    }
  ]
}
```

### cortex-config.json (watch defaults)

```json
{
  "watch": {
    "auto_activate": false,
    "threshold": 0.7,
    "interval": 2.0,
    "directories": ["."]
  }
}
```

### Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CORTEX_SKIP_RECOMMENDER` | unset | Set to `1` to disable Layer 2 in the hook |
| `CLAUDE_CHANGED_FILES` | unset | Colon-separated file list (set by Claude Code) |
| `CLAUDE_HOOK_PROMPT` | unset | User prompt text (set by Claude Code) |
| `CLAUDE_SKILL_RULES` | unset | Override path to `skill-rules.json` |

## Key Design Decisions

### Graceful degradation

Both integration points (hook and watch daemon) wrap the SkillRecommender import
in try/except. This means:

- **Bare install** (hooks only, no pip): Layer 1 keyword matching works.
- **Partial install** (pip without `[ai]` extra): Layers 1 + rule-based + agent-based + historical strategies.
- **Full install** (`pip install claude-cortex[ai]`): All strategies including semantic matching.

### Merge-not-replace

Layer 2 results are *appended* after Layer 1 keyword matches, never replacing
them. Keyword matches are deterministic and fast; Layer 2 adds depth. Users
always see the reliable baseline first.

### Confidence threshold

Only Layer 2 recommendations with confidence >= 0.7 are shown. This prevents
noisy low-confidence suggestions from cluttering the output. The threshold is
intentionally not configurable at the hook level to keep the interface simple.

## File Map

| File | Role |
|------|------|
| `hooks/skill_auto_suggester.py` | Hook entry point (Layer 1 + optional Layer 2) |
| `skills/skill-rules.json` | Keyword → skill mapping rules |
| `claude_ctx_py/skill_recommender.py` | SkillRecommender class (Layer 2) |
| `claude_ctx_py/intelligence/base.py` | SessionContext, ContextDetector |
| `claude_ctx_py/intelligence/semantic.py` | FastEmbed semantic matching |
| `claude_ctx_py/watch.py` | Watch daemon with merged recommendations |
| `claude_ctx_py/tui/main.py` | TUI with auto-start watch daemon |

## Related Documentation

- [AI Intelligence Features](../AI_INTELLIGENCE.md) — Agent recommendation system (separate from skills)
- [AI & LLM Guide](../guides/ai/README.md) — LLM-powered intelligence setup
- [Watch Mode Tutorial](../tutorials/ai-watch-mode.md) — Watch daemon usage
- [Configuration Reference](../reference/configuration.md) — All config files
