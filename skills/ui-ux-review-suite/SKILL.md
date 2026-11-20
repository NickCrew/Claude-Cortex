---
name: ui-ux-review-suite
description: User-triggered orchestrator that runs a comprehensive UI/UX review by coaching the user through three sibling review skills as distinct lenses against one shared target, then synthesizing their findings into a single prioritized report. Composes design-journey-review (visual and journey lens), ux-interaction-review (interaction-mechanics lens), and ux-review (usability-heuristics and WCAG lens). Resolves the review target once at suite start (the app or URL, the screens or flows under review, the viewports, and the user persona and goal) so every lens inherits the same scope and captured screenshots. Coaches rather than auto-runs. At each step it presents the next lens with its scoping prompt and an approval gate, and the user invokes the sibling and confirms before moving on. Produces one authored synthesis report of deduped findings grouped by severity and lens, not a navigation shell. Trigger on "run a full UX review," "comprehensive UI/UX review," "review this screen across all lenses," "do a complete design review," or when the user names two-or-more UI/UX lenses to coordinate. Not for running a single lens in isolation (invoke it directly), not for generating new UI, and not for bypassing approval gates (this skill coaches, never autoruns).
keywords:
  - ux review suite
  - full ux review
  - comprehensive ui review
  - design review
  - ui ux audit
  - multi-lens ux review
triggers:
  - full ux review
  - comprehensive ui/ux review
  - complete design review
  - ux review suite
  - review across all lenses
---

# UI/UX Review Suite

## Overview

You have three skills that review a UI from different angles:
`design-journey-review`, `ux-interaction-review`, and `ux-review`. Run individually
they each produce a narrow slice; run by hand together they re-resolve the same target
three times, double-count the findings at their edges, and leave you with three
separate outputs to reconcile.

This skill owns the coordination. It resolves the review target once, assigns each
sibling a **distinct lens** so the overlaps don't double-count, coaches you through
invoking the three, and writes **one prioritized synthesis report** at the end.

The skill is a **coach, not an autorunner** (same contract as `mapping-suite`). At
each step it presents the next lens, its scoping prompt, and an approval gate. You
invoke the sibling; the orchestrator captures what landed and proposes the next step.

## The three lenses

Each sibling owns one concern, and the scoping prompts in
`references/lens-framing.md` keep it there so the synthesis does not double-count:

| Sibling | Lens it owns | Scoped *out* of |
|---------|--------------|-----------------|
| `design-journey-review` | Visual system and journey: color, type, density, hierarchy, golden path, friction, daily-use fit | interaction states, heuristics, WCAG |
| `ux-interaction-review` | Interaction mechanics: state coverage, feedback and timing, keyboard behavior, error recovery | heuristics, WCAG, aesthetics |
| `ux-review` | Usability heuristics (Nielsen) and WCAG conformance | interaction states, aesthetics |

## When to use

Trigger this skill when:

- You want a complete UI/UX review of a screen, flow, or component before release.
- You name two or more lenses to run together — "do a journey map and a heuristic review of checkout."
- You want one prioritized report spanning all the angles, not three separate ones.

Do not trigger when:

- You only need one lens — invoke the sibling directly.
- You want to *generate* UI — use `ui-design-aesthetics` or `super-saiyan` directly.
- You want hands-off execution — this skill pauses at every gate by design.
- You're already mid-flight in another suite — don't nest.

## Workflow

Six phases. Phases 0 and 5 are unique to this skill; 1–4 are the coaching loop.

| Phase | Name | Purpose |
|-------|------|---------|
| 0 | Resolve target + capture | Resolve app/screens/viewports/persona once; capture screenshots every lens shares. |
| 1 | Choose recipe | `full-review` (all three) or `quick-review` (two), or a custom lens set. |
| 2 | Generate run plan | Ordered lens invocations with the scoping prompt for each. |
| 3 | Coach through the plan | For each lens: present, wait for user to invoke, capture findings, update manifest, propose next. |
| 4 | Synthesize | Merge the lenses' findings into one deduped, prioritized report. |
| 5 | Hand-off | Recommend fixes and follow-up skills based on what surfaced. |

### 0. Resolve target and capture (one-time)

The review target is richer than a repo path — the visual and interaction lenses need
to *see* the UI. Resolve and persist:

- **Target**: running app URL, or a set of screens/components.
- **Flows**: the journeys under review (e.g. "sign-up → first project").
- **Viewports**: desktop / mobile / both. State coverage and visual critique differ per breakpoint.
- **Persona / goal**: who the user is and what they're trying to do. The journey half of `design-journey-review` cannot run without this.

Capture screenshots of each screen/state via `webapp-testing` or `ctx:playwright`
(per flow, per viewport) into a shared dir. Every lens that needs to see the UI reads
these instead of re-driving the browser.

Persist to `docs/<date>-ux-review/review-scope.md`:

```markdown
---
review_date: 2026-06-09
target: http://localhost:3000
flows:
  - sign-up to first project
viewports: [desktop, mobile]
persona: first-time solo founder, no prior account
screenshots: docs/2026-06-09-ux-review/screens/
---
```

Confirm the scope with the user before proceeding.

### 1. Choose recipe

```
Two recipes are available. Which fits this review?

1. full-review  - all three lenses (visual and journey, interaction mechanics, heuristics and WCAG)
2. quick-review - ux-review and ux-interaction-review only (fastest pre-merge pass)

Or name a custom lens set.
```

If the user named a recipe or lenses in the trigger, skip the prompt and confirm.

### 2. Generate run plan

Order the lenses `design-journey-review`, then `ux-interaction-review`, then
`ux-review`. The journey pass establishes the flow context the later lenses
reference. Write the plan to
`docs/<date>-ux-review/suite.yaml` (schema mirrors `mapping-suite`'s manifest), each
step `status: pending`, each carrying its scoping prompt from
`references/lens-framing.md`.

### 3. Coach through the plan

For each lens in order:

1. **Present.** Show the lens name, the one-sentence reason, the scoping prompt
   verbatim (as a copyable code block, with the screenshot dir and persona spliced
   in), and what findings to expect.
2. **Wait for user invocation.** The user runs the sibling skill. The orchestrator
   does not auto-invoke.
3. **Capture findings.** Collect the sibling's findings as a list of
   `{severity, location, finding, recommendation}`. Append to the manifest under the
   lens's step.
4. **Update manifest.** Mark `completed` (or `skipped` with a note).
5. **Propose next.** "Visual lens done — 3 findings. Next: state coverage. Proceed?"

If a lens errors or the user hits a blocker, mark `failed` with the reason and offer
retry / skip / pause. Do not silently retry.

### 4. Synthesize

This suite's siblings emit **inline findings**, not standalone HTML — so the
orchestrator *authors* the synthesis rather than linking outputs. Produce
`docs/<date>-ux-review/synthesis.md`:

1. **Collect** every finding from the manifest into one table:
   `id | lens | severity | location | finding | recommendation`.
2. **Dedup.** When two lenses report the same issue at the same location, merge into
   one row and note both lenses. (Expected between `ux-review` and `ux-interaction-review`
   despite the scoping. Flag and merge, don't drop.)
3. **Prioritize.** Group by severity (blocker → major → minor → polish). Within a
   severity, order by how many lenses flagged it.
4. **Summarize.** A short opening: the persona/flow reviewed, the count by severity,
   and the 3 highest-impact issues.

The synthesis report is the deliverable. It is the orchestrator's only authored
content — it has no opinions of its own about the UI beyond merging and ranking what
the lenses found.

### 5. Hand-off

Survey findings and recommend follow-up — never auto-invoke:

- **Visual/aesthetic gaps dominate** → recommend `ui-design-aesthetics` or
  `super-saiyan` to implement the fixes (now in *generate* mode).
- **WCAG violations** → recommend a deep `accessibility-audit` pass on the worst.
- **Journey drop-off with no instrumentation** → recommend the team add analytics
  before re-reviewing.
- **Missing interaction states** → list them as concrete implementation tasks, and
  recommend `interaction-design` to design the states before building them.
- **Journey problems that span more than this UI** → recommend `user-journey-mapping`
  for a cross-touchpoint journey map.

## Output layout

```
docs/2026-06-09-ux-review/
├── review-scope.md     # Phase 0: target, flows, viewports, persona
├── screens/            # Phase 0: shared screenshots (all lenses read these)
├── suite.yaml          # Phase 2-3: run manifest, findings per lens
└── synthesis.md        # Phase 4: the deliverable — deduped, prioritized report
```

## Resources

- `references/lens-framing.md`: the three scoping prompts that keep each sibling to
  its distinct lens.

## What this skill does NOT do

- **Auto-invoke siblings.** Always pauses at approval gates.
- **Run a single lens.** Use the sibling directly.
- **Generate new UI.** Phase 5 recommends the generative skills for implementing fixes.
- **Form its own opinions.** The synthesis only merges and ranks the lenses' findings.
- **Re-resolve scope per lens.** Phase 0 resolves once; every lens inherits it.
