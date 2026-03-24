# AI Intelligence System: Technical Architecture

This document describes the **agent intelligence** subsystem behind
`cortex ai ...` and the TUI AI Assistant.

For skill-specific architecture, see
[Skill Recommendation & Review Learning](skill-recommendation-system.md).

## Responsibilities

The agent intelligence stack is responsible for:

- building a `SessionContext` from changed files
- recommending agents for the current work
- auto-activating high-confidence recommendations
- learning from successful sessions
- predicting likely workflows from historical patterns
- feeding watch mode and the TUI AI Assistant

## Main Components

### `SessionContext`

Defined in `claude_ctx_py/intelligence/base.py`.

It captures the current working context:

- changed files
- file types
- directories
- booleans such as `has_auth`, `has_api`, `has_frontend`, `has_backend`, and `has_database`
- issue counters such as `test_failures`
- active agents, modes, and rules when provided by the caller

### `ContextDetector`

Also defined in `claude_ctx_py/intelligence/base.py`.

Primary entry points:

- `detect_from_files(files)`
- `detect_from_git()`
- `get_current_context(...)`

The implementation is intentionally lightweight and path-driven. It does not
inspect ASTs or application semantics; it infers context from filenames,
directories, and extensions.

### `PatternLearner`

Stores and reuses successful-session history.

Key features:

- semantic similarity against past sessions when available
- exact-context frequency matching through context buckets
- rule-based heuristics for reliable baseline recommendations
- workflow prediction from common historical agent sequences

Persistent storage:

- `~/.claude/intelligence/session_history.json`

### `IntelligentAgent`

The public orchestrator used by the CLI, watch mode, and TUI.

Key methods:

- `analyze_context()`
- `get_recommendations()`
- `get_auto_activations()`
- `record_session_success()`
- `predict_workflow()`
- `get_smart_suggestions()`

## Recommendation Pipeline

`PatternLearner.predict_agents()` merges three strategies:

1. **Semantic recommendations**
   - uses the optional semantic matcher
   - surfaces agents that were useful in similar past sessions
2. **Pattern recommendations**
   - groups contexts into coarse buckets such as `backend_api_tests`
   - recommends agents that frequently appeared in successful sessions for that bucket
3. **Rule-based recommendations**
   - always runs
   - adds deterministic domain knowledge on top of the learned signals

The output is then:

- de-duplicated by `agent_name`
- sorted by descending confidence

### Context buckets

The history-based strategy groups sessions into a coarse **context bucket** such
as `backend_api_tests`. That bucket comes from the boolean signals in
`SessionContext`:

- frontend
- backend
- database
- tests
- auth
- api

The resulting key is intentionally simple so similar sessions collide often
enough to be useful for pattern learning.

Compact flow:

```text
changed files
   -> ContextDetector / get_current_context()
   -> PatternLearner.predict_agents()
      -> semantic similarity (optional)
      -> exact-context history
      -> rule-based heuristics
   -> deduplicate + sort
   -> CLI / watch mode / TUI AI Assistant
```

## Rule-Based Heuristics

The current rule set in `PatternLearner._rule_based_recommendations()` includes
recommendations such as:

- `security-auditor` when auth-related files are detected
- `test-automator` when test failures are present
- `code-reviewer` for any non-empty changeset
- `python-pro`, `rust-pro`, and `typescript-pro` for language-specific changes
- `react-specialist` and `ui-ux-designer` for user-facing work
- `architect-review` for cross-cutting structural changes
- `database-optimizer` and `sql-pro` for database-heavy work
- `performance-monitor` for performance-sensitive paths
- `docs-architect` for larger API-related changes

These heuristics are the most important thing to keep in sync with the docs,
because they shape the out-of-the-box experience even before any history exists.

## Auto-Activation Semantics

Agent recommendations carry an `auto_activate` flag. The CLI path:

```bash
cortex ai auto-activate
```

simply activates the agents that currently qualify.

Watch mode can also auto-activate agents on the fly. The general thresholds come
from the recommendation data itself:

- some heuristics mark recommendations as auto-activatable immediately
- watch mode respects those flags and only activates agents it has not already
  activated in the current session

The TUI AI Assistant exposes the same behavior through the `A` key.

## Workflow Prediction

`PatternLearner.predict_workflow()` predicts a likely agent sequence when there
are at least three successful sessions for the current context bucket.

It returns a `WorkflowPrediction` with:

- workflow name
- ordered agent sequence
- confidence
- estimated duration
- success probability

If there is not enough history, the system intentionally returns `None`.

## Watch Mode Integration

`claude_ctx_py/watch.py` uses `IntelligentAgent` directly.

Flow:

1. poll git for staged and unstaged changes
2. build a `SessionContext`
3. ask for agent recommendations
4. display recommendations above the configured notification threshold
5. optionally auto-activate the eligible agents

Watch mode also runs the skill suggestion pipeline, which means the watch stream
is the point where the two recommendation systems meet.

## TUI Integration

The TUI imports `IntelligentAgent`, analyzes context on startup, and shows the
results in the AI Assistant view.

Notable behaviors:

- `0` opens the AI Assistant
- `A` triggers auto-activation
- `r` refreshes recommendations
- on startup, the TUI may auto-start the watch daemon in the background

The current AI Assistant view is recommendation- and context-oriented. Older
"context health" and "modes" descriptions no longer match the implementation.

## Learning Loop

Successful sessions are recorded through:

```bash
cortex ai record-success --outcome "feature complete"
```

That writes a session entry containing:

- timestamp
- serialized context
- active agents
- duration
- outcome
- changed files

Those entries feed:

- semantic similarity
- frequency-based exact-context matching
- workflow prediction

## Current Limits

### Context detection is heuristic, not semantic

The system does not inspect application meaning deeply. It depends on path and
extension signals, so repo naming conventions matter.

### Active runtime state is optional

`SessionContext` can store active agents, rules, and modes, but many CLI paths
only populate file-based context. Documentation should avoid implying that every
recommendation path knows the full runtime state.

### History quality depends on explicit recording

If teams never run `cortex ai record-success`, the system still works, but mostly
through rule-based heuristics rather than learned patterns.

## Files To Read When Modifying This Subsystem

- `claude_ctx_py/intelligence/base.py`
- `claude_ctx_py/cmd_ai.py`
- `claude_ctx_py/watch.py`
- `claude_ctx_py/tui/main.py`
- `docs/AI_INTELLIGENCE.md`
- `docs/tutorials/ai-watch-mode.md`
