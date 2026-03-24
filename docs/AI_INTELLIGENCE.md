# AI Intelligence Features

Cortex ships two related, but separate, recommendation systems:

1. **Agent intelligence** powers `cortex ai ...`
   - Recommends which agents to activate
   - Can auto-activate high-confidence agent recommendations
   - Learns from successful sessions in `~/.claude/intelligence/`
2. **Skill recommendations** power `cortex skills recommend`, the Claude Code hook,
   and the watch daemon's skill suggestions
   - Suggests reusable skills to load for the current task
   - Uses keyword rules plus an optional multi-strategy recommender
   - Stores feedback/history in `~/.claude/data/skill-recommendations.db`

This page focuses on the **agent** side. For the skill pipeline, see
[Skill Recommendation Engine](architecture/skill-recommendation-engine.md).

## What Agent Intelligence Does

The agent system answers: "Given the files I'm changing right now, which agents
should I activate?"

It works from the current git-backed session context:

- changed files and file extensions
- directory names and file-path signals such as `auth`, `routes`, `schema`, and `tests`
- session issue counts such as test failures
- previously recorded successful sessions

The output is a ranked list of `AgentRecommendation` objects with:

- agent name
- confidence score
- reason
- urgency
- whether the recommendation qualifies for auto-activation

## Commands

### Inspect recommendations

```bash
cortex ai recommend
```

This analyzes the current git diff, prints recommended agents, shows a workflow
prediction when enough history exists, and summarizes the detected context.

### Auto-activate high-confidence agents

```bash
cortex ai auto-activate
```

This activates agents whose recommendations have `auto_activate=True`. In the
current rule set, most auto-activations come from strong rule-based signals such
as auth, test failures, language-specific changes, or large cross-cutting edits.

### Run watch mode

```bash
# Foreground
cortex ai watch

# Background daemon
cortex ai watch --daemon

# Inspect / stop the daemon
cortex ai watch --status
cortex ai watch --stop
```

Watch mode monitors git changes in real time and prints:

- detected context
- high-confidence agent recommendations
- suggested skills from the keyword hook plus optional Layer 2 skill recommender

Useful flags:

```bash
cortex ai watch --no-auto-activate
cortex ai watch --threshold 0.8
cortex ai watch --interval 5
cortex ai watch --dir ~/project-a --dir ~/project-b
```

### Teach the system from a successful session

```bash
cortex ai record-success --outcome "feature complete"
```

This records the current session into `~/.claude/intelligence/session_history.json`
using the active agents and the current git-backed context. It primarily improves
future **agent** recommendations. Cortex also makes a best-effort attempt to feed
that success into the skill-learning pipeline.

### Ingest a specialist review into skill learning

```bash
cortex ai ingest-review path/to/review.md
```

This parses a structured review artifact, maps productive review perspectives to
skills, and records those skills as successful for similar future contexts.

## How Agent Recommendations Are Produced

Agent recommendations come from `PatternLearner.predict_agents()` in
`claude_ctx_py/intelligence/base.py`. It merges three strategies:

1. **Semantic similarity** (optional)
   - Enabled when the optional embedding dependency is available
   - Finds similar past sessions and reuses the agents that worked there
2. **Pattern matching from history**
   - Looks for exact context buckets such as `backend_api_tests`
   - Recommends agents that appeared frequently in those successful sessions
3. **Rule-based heuristics**
   - Always available
   - Adds concrete recommendations such as:
     - `security-auditor` for auth-heavy changes
     - `test-automator` for test failures
     - `code-reviewer` for any non-empty changeset
     - `python-pro`, `typescript-pro`, `react-specialist`, `database-optimizer`, and others based on file types and path signals

The system de-duplicates recommendations by agent name, keeping the highest
confidence result for each agent.

### Common rule-based triggers

The exact logic lives in `PatternLearner._rule_based_recommendations()`, but the
current out-of-the-box triggers are:

| Signal | Agent | Default confidence |
|---|---|---|
| Auth-related files | `security-auditor` | `0.9` |
| Test failures | `test-automator` | `0.95` |
| Any non-empty changeset | `code-reviewer` | `0.75` |
| Python files | `python-pro` | `0.85` |
| Rust files | `rust-pro` | `0.85` |
| TypeScript files | `typescript-pro` | `0.85` |
| React/UI signals | `react-specialist` | `0.8` |
| User-facing UI work | `ui-ux-designer` | `0.8` |
| Cross-cutting structural changes | `architect-review` | `0.75` |
| Database-heavy changes | `database-optimizer` | `0.8` |
| SQL-heavy changes | `sql-pro` | `0.8` |
| Performance-sensitive paths | `performance-monitor` | `0.7` or `0.85` depending on signal strength |
| Larger API-related changes | `docs-architect` | `0.75` |

## Workflow Prediction

`cortex ai recommend` also attempts workflow prediction through
`PatternLearner.predict_workflow()`.

When Cortex has at least three successful sessions for the same context bucket,
it can predict:

- a likely agent sequence
- expected duration
- approximate success probability

If there is not enough history, the CLI reports that explicitly instead of
guessing.

## Watch Mode Details

Watch mode lives in `claude_ctx_py/watch.py` and layers multiple signals:

1. Detect changed files from unstaged and staged git changes
2. Build a `SessionContext`
3. Ask `IntelligentAgent` for agent recommendations
4. Run keyword-based skill matching from `skills/skill-rules.json`
5. Optionally enrich those skill suggestions with `SkillRecommender`

The result is one live stream that shows both:

- **agent recommendations** for activation decisions
- **skill suggestions** for prompt-level guidance

### Configuration

The watch CLI reads overrides from `$CORTEX_ROOT/cortex-config.json`
(default `~/.cortex/cortex-config.json`):

```json
{
  "watch": {
    "directories": ["~/projects/my-app"],
    "auto_activate": true,
    "threshold": 0.7,
    "interval": 2.0
  }
}
```

Notes:

- when you run `cortex ai watch` directly, the built-in defaults are:
  - auto-activation: `true`
  - threshold: `0.7`
  - interval: `2.0`
- the JSON example above is illustrative configuration, not a claim that every
  key is required
- the TUI's background auto-start path uses the same config, but falls back to
  notification-only behavior when no `watch.auto_activate` value is configured

## TUI Integration

In the TUI:

- press `0` for the AI Assistant view
- press `A` to auto-activate recommended agents
- press `r` to refresh recommendations

The AI Assistant view shows:

- recommended agents with confidence and reasoning
- workflow prediction when available
- a compact summary of the detected session context

The TUI also attempts to auto-start the watch daemon in the background so live
recommendations are available without a separate terminal session.

## Data and Storage

### Agent intelligence

- `~/.claude/intelligence/session_history.json`
  - successful-session history for pattern learning and workflow prediction
- `~/.claude/intelligence/semantic_cache/`
  - optional embedding cache for semantic similarity

### Skill recommendation data used alongside watch mode

- `~/.claude/data/skill-recommendations.db`
  - recommendation history, feedback, and learned context patterns
- `~/.claude/skills/recommendation-rules.json`
  - active rule-based skill recommendation rules
- `~/.claude/skills/skill-rules.json`
  - keyword rules used by the prompt hook and watch mode

## Related Docs

- [Skill Recommendation Engine](architecture/skill-recommendation-engine.md)
- [Skill Recommendation & Review Learning](guides/development/skill-recommendation-system.md)
- [AI Intelligence System: Technical Architecture](guides/development/AI_INTELLIGENCE_ARCHITECTURE.md)
- [AI Watch Mode Tutorial](tutorials/ai-watch-mode.md)
