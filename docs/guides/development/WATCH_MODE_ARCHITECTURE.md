# Watch Mode: Real-Time Recommendation Architecture

Watch mode is the real-time integration point where Cortex's **agent**
recommendation system and **skill** recommendation system are shown together.

Implementation lives in `claude_ctx_py/watch.py`.

## Main Responsibilities

Watch mode:

- polls git-backed changes on a configurable interval
- detects context from changed files
- queries `IntelligentAgent` for agent recommendations
- generates keyword-based skill suggestions
- optionally enriches skills through `SkillRecommender`
- auto-activates eligible agents when configured

## High-Level Flow

```
git changes
   │
   ▼
WatchMode._get_changed_files()
   │
   ▼
IntelligentAgent.analyze_context(changed_files)
   │
   ├─ agent recommendations
   └─ session context
   │
   ▼
_match_skills(changed_files, skill_rules, directories=...)
   │
   └─ optional Layer 2 enrichment via SkillRecommender
   │
   ▼
print context + agents + skills
   │
   ▼
optional auto-activation
```

## Key Types

### `WatchDefaults`

Resolved from `~/.cortex/cortex-config.json`:

- `directories`
- `auto_activate`
- `threshold`
- `interval`
- parse warnings

### `SkillSuggestion`

The lightweight skill display type used by watch mode:

- `name`
- `path`
- `description`
- `hits`

This is separate from `SkillRecommendation`, which belongs to the richer
`SkillRecommender` path.

### `WatchMode`

Owns the long-running state:

- watched directories
- last git heads
- last agent recommendations
- last skill suggestions
- activated agents
- counters and notification history

## Recommendation Sources

### Agents

Agent recommendations come from:

- `self.intelligent_agent.analyze_context(changed_files)`
- `self.intelligent_agent.get_recommendations()`

Only recommendations above the configured notification threshold are shown.

### Skills

Skill suggestions come from two layers:

1. `_match_skills(...)`
   - keyword-based
   - uses `skills/skill-rules.json`
   - includes prompt-independent git context from watched directories
2. optional `SkillRecommender`
   - adds richer suggestions for `confidence >= 0.7`
   - de-duplicates against the keyword suggestions already found

## Auto-Activation

Watch mode never invents its own auto-activation threshold. It activates the
agents whose recommendations already have `auto_activate=True`.

The activation path:

1. filter recommended agents to those marked auto-activatable
2. skip agents already activated in this watch session
3. skip agents already active on disk
4. call `agent_activate()` for the remainder

This keeps the behavior aligned with the main `IntelligentAgent` logic.

## Daemon Architecture

The daemon flow is intentionally simple:

- `start_watch_daemon()` spawns `python -m claude_ctx_py.cli ai watch`
- PID and logs are written under `~/.cortex/`
- status and stop commands operate on that PID file

This avoids maintaining separate foreground and background watch implementations.

## TUI Relationship

The TUI does not reimplement watch mode. It may start the daemon from
`AgentTUI._try_auto_start_watch_daemon()` and then expose related actions in the
AI Assistant view.

That means recommendation behavior should stay aligned between:

- `cortex ai watch`
- the TUI AI Assistant
- the watch daemon started on TUI mount

## Design Constraints

### Git-first change detection

Watch mode only reacts to changes visible through git diff state. It does not
run a general filesystem watcher.

### Graceful degradation

If `SkillRecommender` fails to initialize, watch mode still works with keyword
skill suggestions and agent recommendations.

### Noise control

To avoid spam:

- only high-confidence agent recommendations are displayed
- skill changes are diffed against the last suggestion set
- identical recommendation sets are not reprinted every loop

## Files To Keep In Sync

- `claude_ctx_py/watch.py`
- `claude_ctx_py/cmd_ai.py`
- `docs/AI_INTELLIGENCE.md`
- `docs/tutorials/ai-watch-mode.md`
- `docs/guides/development/WATCH_MODE_GUIDE.md`
