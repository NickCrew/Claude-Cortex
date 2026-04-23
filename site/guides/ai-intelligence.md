---
layout: default
title: AI Intelligence
parent: Guides
nav_order: 3
---

# AI Intelligence

Cortex ships two related recommendation systems:

1. **Agent intelligence** powers `cortex suggest ...`
2. **Skill recommendations** power `cortex skills recommend`, the Claude Code
   hook, and watch-mode skill suggestions

This page focuses on the **agent** side: which agents Cortex thinks you should
activate for the work in front of you.

## What Agent Intelligence Does

Agent intelligence answers:

> Given the files I am changing right now, which agents should I activate?

It works from the current git-backed session context, including:

- changed files and file extensions
- path signals (`auth`, `schema`, `routes`, `tests`, `api`, `frontend`, `backend`, `database`)
- test failures, build failures, and error counts
- active agents, modes, and rules
- previously successful sessions

Recommendations include:

- agent name
- confidence score
- reason and context triggers
- urgency (`low`, `medium`, `high`, `critical`)
- whether the recommendation qualifies for auto-activation

### Deactivation Recommendations

The system also recommends agents to **deactivate** when they're no longer relevant.
It analyzes active agents against the current context and historical usage patterns.
Agents with low usage in similar contexts (usage score below 0.3) are flagged for
deactivation. High-confidence, high-impact deactivations can be auto-applied.

## Commands

### Inspect recommendations

```bash
cortex suggest
```

Analyzes the current git diff, prints recommended agents, and shows a workflow
prediction when enough history exists (minimum 3 recorded sessions).

### Auto-activate high-confidence agents

```bash
cortex suggest --activate
```

Activates agents whose recommendation is marked for auto-activation.

### Export recommendations

```bash
cortex suggest --export
cortex suggest --export --output recommendations.json
```

Exports agent recommendations and workflow predictions to a JSON file
(default: `ai-recommendations.json`).

### Record a successful session

```bash
cortex suggest --record-success --outcome "feature complete"
```

Records the current session as successful, improving future agent recommendations
through pattern learning.

### Ingest a specialist review

```bash
cortex suggest --ingest-review path/to/review.md
```

Feeds structured specialist review output into the learning system.

## Watch Mode

Watch mode monitors git-backed changes and continuously provides recommendations.

### Starting watch mode

```bash
# Foreground
cortex suggest --watch

# Background daemon
cortex suggest --watch --daemon

# Inspect / stop the daemon
cortex suggest --watch --status
cortex suggest --watch --stop
```

### Overriding defaults

```bash
cortex suggest --watch --no-auto-activate
cortex suggest --watch --threshold 0.8
cortex suggest --watch --interval 5
cortex suggest --watch --dir ~/project-a --dir ~/project-b
```

### Default behavior

| Setting | Default | Description |
|:--------|:--------|:------------|
| auto-activate | `true` | Activate high-confidence recommendations automatically |
| threshold | `0.7` | Minimum confidence score |
| interval | `2.0` seconds | Polling interval |

These defaults can be set in `cortex-config.json`. See the
[Configuration Reference]({% link reference/configuration.md %}) for the full
config file format and all available keys.

Watch mode prints:
- detected context
- high-confidence **agent recommendations**
- suggested **skills** from the skill matcher and optional richer recommender

## How Recommendations Are Produced

The agent recommender combines three strategies:

1. **Semantic similarity** --- matches the current context against past sessions
   using FastEmbed embeddings (requires optional `fastembed` dependency)
2. **Pattern matching** --- learns from recorded successful sessions
3. **Rule-based heuristics** --- maps file signals to agents

> **If suggestions go quiet**, the semantic layer is the usual culprit. When
> `fastembed` isn't installed in the active Python env, the semantic strategy
> silently returns nothing. The other two strategies still work, but
> recommendations will feel thinner. Install with `pip install fastembed` and
> rerun. The same failure mode affects the skill auto-suggester hook -- see
> [Working with Skills]({% link guides/working-with-skills.md %}#troubleshooting)
> for the full troubleshooting flow.

### Rule-Based Triggers

| Signal | Agent |
|:-------|:------|
| Auth-related files | `security-auditor` |
| Test failures | `test-automator` |
| Any non-empty changeset | `code-reviewer` |
| Python files | `python-pro` |
| TypeScript files | `typescript-pro` |
| Rust files | `rust-pro` |
| React/UI signals | `react-specialist` |
| UI/UX changes (HTML, CSS) | `ui-ux-designer` |
| Database-heavy changes | `database-optimizer` |
| SQL files / migrations | `sql-pro` |
| Performance-sensitive patterns | `performance-monitor` |
| Cross-cutting changes (frontend + backend) | `architect-review` |
| API changes spanning 3+ files | `docs-architect` |
| Large changesets (5+ files) | `code-reviewer` (elevated confidence) |

### LLM-Powered Intelligence (Optional)

When `llm_enabled` is set to `true` in `intelligence-config.json`, Cortex uses
Claude API calls for more sophisticated recommendations. The system auto-selects
the most cost-effective model based on task complexity:

| Complexity | Model | Use case |
|:-----------|:------|:---------|
| Low (< 0.4) | Haiku | Simple recommendations, small context |
| Medium (0.4--0.75) | Sonnet | Standard complexity |
| High (> 0.75) | Opus | Complex analysis, large context |

Budget controls, prompt caching, and model overrides are configured in
`intelligence-config.json`. See the
[Configuration Reference]({% link reference/configuration.md %}) for details.

## TUI Integration

```bash
cortex tui
```

Then:

- press `0` for the AI Assistant view
- press `a` to auto-activate recommended agents
- press `r` to refresh recommendations

The AI Assistant view shows agent recommendations **and** deactivation suggestions.
The Skills view (press `5`) is where you browse and rate skills separately.

## Teaching The System

Record a successful session:

```bash
cortex suggest --record-success --outcome "feature complete"
```

This primarily improves future **agent** recommendations through pattern learning.

If you use structured specialist reviews, you can also feed them into skill
learning:

```bash
cortex suggest --ingest-review path/to/review.md
```

## Important Distinction

Do not use these terms interchangeably:

- **agent recommendations** decide which agents to activate
- **skill recommendations** suggest which reusable knowledge packs to load

For the skill side, see the [Skills]({% link guides/skills.md %}) guide.

## Related

- [Configuration Reference]({% link reference/configuration.md %}) --- config files, env vars, and resolution rules
- [Skills]({% link guides/skills.md %}) --- skill recommendation system
- [Terminal UI]({% link guides/tui.md %}) --- TUI views and keybindings
