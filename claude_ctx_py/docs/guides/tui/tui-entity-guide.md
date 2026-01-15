# Cortex TUI Entity Relationship Guide

Understand how the TUI slices the Cortex plugin into manageable pieces so you can tell at a glance what to touch—profiles, modes, workflows, scenarios, agents, and rules each solve a different layer of control. This page focuses on the Rich/Textual TUI (`cortex tui`) but the concepts match the CLI and context bundle.

## Quick Reference Map

| Entity     | What it controls | Source files | TUI entry point | Downstream impact |
|------------|-----------------|--------------|-----------------|-------------------|
| Agents     | Individual specialists with triggers, dependencies, and skills | `agents/*.md`, `inactive/agents/` | View `2` (Agents) | Form the workforce that workflows/scenarios schedule |
| Modes      | Behavioral overlays that rewrite execution rules (e.g., `Architect`, `Token_Efficiency`) | `modes/*.md`, `.active-modes` | View `3` (Modes) | Change how every active agent executes tasks |
| Rules      | Instruction blocks (workflow, quality, efficiency) loaded into `CLAUDE.md` | `rules/*.md`, `inactive/rules/` | View `4` (Rules) | Provide guardrails that profiles/modes rely on; active when the file is in `rules/` |
| Principles | Engineering principles snippets | `principles/*.md`, `.active-principles` | View `p` (Principles) | Shapes the baseline reasoning framework |
| Skills     | Discrete capabilities/commands surfaced in the palette | `skills/**/SKILL.md` | View `5` (Skills) | Extend what agents can automate |
| Profiles   | Bundles of agents + modes + rules + resource limits | `profiles/**.profile` | View `8` (Profiles) | One tap switches the entire operating posture |
| Workflows  | Ordered, restartable sequences of steps | `workflows/*.yaml` | View `6` (Workflows) | Drive long-running operations; feed Orchestrate view |
| Scenarios  | Event playbooks with triggers, phases, monitoring, and rollback | `scenarios/*.yaml` | Hotkey `S` (Scenarios view) | Can activate profiles, agents, and workflows per phase |
| Orchestrate / Tasks | Real-time agent task board with per-task notes + log streaming | Hotkey `o` (Orchestrate) / `t` (Tasks) | Pulls from workflow/scenario executions |
| AI Assistant | Predictive recommendations across the stack | View `0` | Suggests which profile/workflow/scenario fits the current repo state |
| Shortcuts / Help | Keyboard overlays and command palette tips | `docs/guides/tui/tui-keyboard-reference.md` | `?` (help overlay) / `Ctrl+P` (command palette) | Keeps operators aligned on the hotkeys tied to each entity |

## Profiles vs. Modes

* **Modes** are single behavioral overlays. The TUI lists mode files from `modes/` and tracks activation in `.active-modes`. Press `Space` to toggle a mode on or off; the status chip flips between `● ACTIVE` and `○ inactive`.
* **Profiles** bundle multiple modes, rules, and agent tiers. Looking at `profiles/enhanced/incident-response.profile` you can see `MODES="Orchestration"`, `RULES="workflow-rules efficiency-rules"`, agent tiers, activation strategy, and workflow hints. In View `8`, `Space` applies a profile, `n` snapshots the current selection, and `D` deletes a saved profile. Applying a profile simultaneously toggles the listed modes/rules and preloads the referenced agents, so it is the fastest way to change the operating posture.

Use modes when you need a targeted behavior tweak (e.g., temporarily enabling `Super_Saiyan`), and use profiles when you need a whole operating bundle (agents + modes + rules + concurrency limits).

## Workflows vs. Scenarios

| Aspect | Workflows | Scenarios |
|--------|-----------|-----------|
| Format | Simple YAML with `steps`, `trigger`, and `success_criteria` (see `workflows/feature-development.yaml`) | Rich YAML with `phases`, `monitoring`, `alerts`, and `rollback` (see `scenarios/product-launch.yaml`) |
| TUI access | View `6` (press `6` or pick “Show Workflows”) | Press `S` (or use the command palette → “Show Scenarios”) |
| Actions | View live status/progress, detect paused/running workflows, and read steps. (Run/resume via CLI `cortex workflow run ...`.) | Preview (`P`), auto-run (`R`), schema-validate (`V`), and inspect status history (`H`) directly inside the TUI.
| Scope | Linear, execution-focused (e.g., Feature Development) | Event/incident playbooks that stitch profiles + agents per phase, include monitoring + rollback |

Workflows are ideal for predictable, repeatable sequences (feature work, bug fixes). Highlight one in the Workflows view and press `Shift+R` to run it or `s` to stop it without leaving the dashboard. Scenarios add orchestration metadata for messy or long-lived events: highlight a scenario in the Scenarios view and press `Shift+R` to auto-run it (use `s` to clear the lock if you need to abort). The `product-launch` scenario, for instance, wires four named phases, assigns profiles (`quality`, `meta`), and lists success criteria and monitoring thresholds.

## How the TUI Threads Everything Together

1. **Overview (1)** – Shows total/active counts for agents, modes, rules, skills, and running workflows so you know when a profile or scenario actually toggled something. The banner pulls directly from the same data structures the per-entity views use.
2. **Agents (2)** – Use `Space` to activate/deactivate individuals; enter displays dependency/tier info so you understand what a profile or scenario is about to call.
3. **Modes (3) & Rules (4)** – After applying a profile, flip to these views to confirm which enforcement layers actually changed.
4. **Skills (5)** – Optional but handy: when a workflow step references `/dev:git` or `/ctx:test`, the skill view lets you validate/install them before orchestrating.
5. **Workflows (6)** – Shows YAML-derived metadata, current step, and progress bar. Press `Shift+R` to launch the highlighted workflow or `s` to stop the active one; the Orchestrate view reflects each agent task once it starts.
6. **Scenarios (`S`)** – Catalog every operational playbook living under `~/.claude/scenarios`. Rows display priority coloring, count of phases/agents, last run timestamp, and quick actions (`P`, `Shift+R`, `s`, `V`, `H`).
7. **Orchestrate (`o`) & Tasks (`t`)** – Live task board that aggregates whatever the workflows/scenarios launched. Press `s` for the full detail modal, `L` to tail the source log inside the TUI, or `O` to pop the log open in your native viewer. Critical for verifying that the parallel workstreams a profile demands are actually running.
8. **Profiles (8)** – When you apply or save a profile snapshot, the next pass through Overview/Agents/Modes immediately reflects the new state.
9. **AI Assistant (0)** – Consumes metrics collected from agents/modes/workflows to recommend “next best” actions (e.g., “Run performance-optimize workflow” when runtime metrics spike). It is a guidance layer that keeps the pieces aligned.

## Relationship Cheat Codes

* **Profiles call Modes/Rules** – Every `.profile` file lists `MODES=` and `RULES=`, so applying a profile is equivalent to toggling multiple modes/rules in one action.
* **Workflows call Agents** – `workflows/*.yaml` enumerates `steps[].agent`. When a workflow is running, the Orchestrate view will show those agents as tasks; canceling a task from Orchestrate pauses the workflow.
* **Scenarios call Profiles + Agents** – `phases[].profiles` tell the orchestrator which profile to apply before scheduling the `phases[].agents`. That means a single scenario may switch contexts several times as it advances.
* **AI Assistant predicts Workflows/Scenarios** – Recommendations are based on the currently active agents/modes/workflows; it often suggests the matching workflow or scenario when it detects keywords or repo signals.

## Typical End-to-End Flow

1. **Choose a profile** (View 8, `Space`) – e.g., `quality` for audit work. The TUI toggles the associated modes/rules instantly.
2. **Verify the enforcement layers** – Spot-check Modes (3) and Rules (4) to ensure the profile change stuck.
3. **Kick off a workflow** – Either via CLI or the command palette suggestion. Monitor its status in View 6 and watch Orchestrate (`o`) populate.
4. **Escalate to a scenario if needed** – If the situation is broader (e.g., release goes sideways), hit `S`, preview the relevant scenario, and run it with `R`. The scenario may swap profiles between phases; the Overview view will show those transitions.
5. **Capture learnings** – Save the tuned setup as a new profile (`n` in View 8) so you can reapply the same mix next time.

Following that loop keeps the “profiles vs. modes vs. workflows vs. scenarios” distinction tangible—you always know which layer you are manipulating, which files back it, and exactly where to look in the TUI to confirm the state.
