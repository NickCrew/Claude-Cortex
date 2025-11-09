# Superpowers Skill Mapping (November 7, 2025)

This note captures how we will adapt obra/superpowers (MIT) skills into claude-ctx without duplicating existing assets. Every borrowed skill references the claude-ctx component that will own it so we keep one source of truth.

## Collaboration Core

| Superpowers Skill | claude-ctx source of truth | Notes |
| --- | --- | --- |
| `skills/collaboration/brainstorming/SKILL.md` | `modes/Super_Saiyan.md` + `scenarios/ideation/*.md` | Rebrand to `/ctx:brainstorm`; point to Supersaiyan visuals + Task TUI for capturing highlights. |
| `skills/collaboration/writing-plans/SKILL.md` | `workflows/` + `rules/Planning.md` | `/ctx:plan` enumerates the existing plan template, then autogenerates tasks via the new Task view. |
| `skills/collaboration/executing-plans/SKILL.md` | Orchestrate view + `tasks/current/` JSON | `/ctx:execute-plan` becomes a wrapper that seeds `active_agents.json`; no separate checklist doc. |
| `skills/collaboration/requesting-code-review/SKILL.md` | `docs/REVIEW_CHECKLIST.md` (todo) + `commands/review.yaml` | Borrow structure but link back to our review commands/rules so guidance stays centralized. |
| `skills/collaboration/receiving-code-review/SKILL.md` | `RULES.md` quality section | Reuse advice but reference claude-ctx rollout steps and Supersaiyan QA mode. |

## Quality & Testing

| Superpowers Skill | claude-ctx anchor |
| --- | --- |
| `skills/testing/test-driven-development` | `pytest.ini`, `tests/` templates, `commands/testing.yaml` |
| `skills/debugging/systematic-debugging` | `modes/Diagnostics.md` + TUI performance monitor |
| `skills/debugging/root-cause-tracing` | `docs/AI_INTELLIGENCE_GUIDE.md` + watch mode |

## Meta Skills

| Superpowers Skill | claude-ctx anchor |
| --- | --- |
| `skills/meta/writing-skills` | `CONTRIBUTING.md` writing/style section |
| `skills/meta/sharing-skills` | `docs/COMMUNITY.md` (to create) |
| `skills/meta/testing-skills-with-subagents` | `agents/security-auditor`, `agents/test-author` |

## Avoiding Redundancy

- Session-start hook will reference this skill catalog instead of restating RULES/FLAGS. Hook text says “run `/ctx:brainstorm` then `/ctx:plan` before editing”.
- Each skill links back to existing docs (AGENTS.md, RULES.md, Supersaiyan guide) so we edit content in one place.
- Task creation happens either through the Task TUI or `/ctx:execute-plan` (which writes the same JSON) to prevent double entry.
- We will keep Superpowers’ MIT license in `skills/LICENSE.superpowers` and mention attribution in each imported skill file.

Next step: add `skills/collaboration/brainstorming`, `skills/collaboration/writing-plans`, `skills/collaboration/executing-plans` with adapted content + license headers, then wire `/ctx:*` commands.

## Hook + Rule Integration

- Added `hooks/examples/skill_auto_suggester.py`, a Python hook that reads `skills/skill-rules.json` (keyword → command mapping) and emits suggested skills after each prompt. Pattern borrowed from diet103/claude-code-infrastructure-showcase.
- `skills/skill-rules.json` ships with entries for `/ctx:brainstorm`, `/ctx:plan`, `/ctx:execute-plan`, `/dev:test`, and `/dev:code-review`. Updating the JSON automatically updates the hook output.
- Documented installation steps in `hooks/README.md` so users can activate the hook alongside the existing quality gate.
