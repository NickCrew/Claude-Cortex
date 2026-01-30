# Settings Files Catalog

This catalog lists the configuration, state, and reference files that the app
reads or writes. For detailed documentation with schemas and examples, see the
[Configuration Reference](reference/configuration.md). Paths are shown relative to the active Cortex directory
(default `~/.cortex/`). You can override the active directory with
`CORTEX_ROOT` or `CLAUDE_PLUGIN_ROOT` / `--plugin-root`, or use project-local
`.claude/` via `--scope project` or `CORTEX_SCOPE=project`.

## Core Framework Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `CLAUDE.md` | Main manifest with `@` references | Primary entry point for context assembly |
| `FLAGS.md` | Flag activation list (`@flags/*.md`) | Updated by TUI Flag Manager |
| `PRINCIPLES.md` | Engineering principles | Generated from `principles/*.md` |
| `RULES.md` | Core rules | Included by `CLAUDE.md` |

## Principles Snippets

| Path | Purpose | Notes |
| --- | --- | --- |
| `principles/*.md` | Principles snippets | Concatenated by `cortex principles build` |

## Activation State Files

| Path | Purpose | Notes |
| --- | --- | --- |
| `.active-modes` | Active mode list | Reference-based activation |
| `.active-rules` | Active rules list | Reference-based activation |
| `.active-mcp` | Active MCP docs list | Reference-based activation |
| `.active-principles` | Active principles snippet list | Used by `cortex principles build` (order is filename-sorted) |

## Agent and Skill Settings

| Path | Purpose | Notes |
| --- | --- | --- |
| `agents/triggers.yaml` | Agent trigger metadata | Used by recommendations |
| `skills/activation.yaml` | Skill keyword activation map | Used by auto-activation |
| `skills/composition.yaml` | Skill composition rules | Used by skill composer |
| `skills/versions.yaml` | Skill version registry | Used by `skills versions` |
| `skills/skill-rules.json` | Skill selection rules | [Docs](reference/configuration.md#skill-rulesjson) |
| `skills/recommendation-rules.json` | Recommendation rules | [Docs](reference/configuration.md#recommendation-rulesjson) |
| `skills/community/registry.yaml` | Community skill registry | Community skill install |
| `skills/analytics.schema.json` | Skill analytics schema | Validation/reference |
| `skills/metrics.schema.json` | Skill metrics schema | Validation/reference |

## Hooks and MCP

| Path | Purpose | Notes |
| --- | --- | --- |
| `settings.json` | Claude Code settings (hooks) | TUI hooks manager updates this |
| `mcp/docs/*.md` | Local MCP docs | Activated via `.active-mcp` |

## TUI

| Path | Purpose | Notes |
| --- | --- | --- |
| `tui/theme.tcss` | TUI theme override | Optional; loaded after `styles.tcss` |

## Launcher Configuration

| Path | Purpose | Notes |
| --- | --- | --- |
| `cortex-config.json` | Main launcher config | [Docs](reference/configuration.md#cortex-configjson) |
| `.onboarding-state.json` | Wizard completion state | [Docs](reference/configuration.md#onboarding-statejson) |

## Intelligence and Memory

| Path | Purpose | Notes |
| --- | --- | --- |
| `intelligence-config.json` | LLM intelligence settings | Model selection/budget/caching |
| `memory-config.json` | Memory vault settings | [Docs](reference/configuration.md#memory-configjson) |

## Schemas

| Path | Purpose | Notes |
| --- | --- | --- |
| `schemas/cortex-config.schema.json` | Cortex config validation | [Docs](reference/configuration.md#cortex-configjson) |
| `schemas/memory-config.schema.json` | Memory config validation | [Docs](reference/configuration.md#memory-configjson) |
| `schemas/skill-rules.schema.json` | Skill rules validation | [Docs](reference/configuration.md#skill-rulesjson) |
| `schemas/recommendation-rules.schema.json` | Recommendation rules validation | [Docs](reference/configuration.md#recommendation-rulesjson) |
| `schemas/onboarding-state.schema.json` | Onboarding state validation | [Docs](reference/configuration.md#onboarding-statejson) |
| `schemas/agent-schema-v2.yaml` | Agent validation schema | Used by validators |

## Auto-Managed Data (for reference)

All paths below are relative to the active Claude directory.

| Path | Purpose | Notes |
| --- | --- | --- |
| `.metrics/skills/stats.json` | Skill metrics summary | Generated automatically |
| `.metrics/skills/activations.json` | Activation log | Generated automatically |
| `data/skill-ratings.db` | Skill ratings database | SQLite |
| `data/skill-rating-prompts.json` | Rating prompt state | Auto-managed |
| `intelligence/session_history.json` | Recommendation history | Auto-managed |
| `intelligence/semantic_cache/session_embeddings.jsonl` | Embedding cache | Auto-managed |
| `tasks/current/active_agents.json` | Task view state | Auto-managed |
| `tasks/current/active_workflow` | Current workflow name | Auto-managed |
| `tasks/current/workflow_status` | Workflow status | Auto-managed |
| `tasks/current/workflow_started` | Workflow start time | Auto-managed |
| `tasks/current/current_step` | Workflow step label | Auto-managed |
| `community/ratings/*.json` | Community skill ratings | Auto-managed |

## External (Claude Desktop MCP Config)

Claude Desktop config is outside `.claude` but is read for MCP server setup:

| Platform | Path |
| --- | --- |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%/Claude/claude_desktop_config.json` |
