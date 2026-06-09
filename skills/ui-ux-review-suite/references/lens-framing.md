# Lens framing prompts

Each sibling is invoked with a reframing prompt that (a) scopes it to its distinct
lens so the synthesis doesn't double-count, and (b) for the two generative siblings,
turns generation into critique. Splice in the resolved scope values — `{persona}`,
`{flows}`, `{screenshots}`, `{viewports}` — from `review-scope.md`.

## 1. user-journey-mapping — flow / funnel lens

> Map the journey for `{persona}` attempting `{flows}`, using the screenshots in
> `{screenshots}`. Identify touchpoints, friction, drop-off risk, and emotional state
> at each step. **Do not redesign** — this is a diagnostic map, not a proposal. Output
> findings as `{severity, step/location, friction, recommendation}`.

Owns: where in the journey, why users stall, emotional arc.

## 2. ui-design-aesthetics — visual critique lens (generative → critique)

> **Critique** the existing visual design in `{screenshots}` across `{viewports}`
> against your principles — visual hierarchy, distinctiveness vs. generic, spacing and
> rhythm, typographic scale, polish. **Do not generate a new design or mockups.** Score
> each dimension and cite the specific screen and element. Output findings as
> `{severity, screen/element, issue, recommendation}`.

Owns: is it visually strong. Scoped out of: interaction, usability, a11y.

## 3. interaction-design — state-coverage lens (generative → critique)

> **Audit** the interaction states for `{flows}` in `{screenshots}`. For every
> interactive surface, check coverage of loading / error / empty / success / disabled
> states and the quality of feedback and micro-interactions. **Do not design new
> interactions** — list what is missing or weak. Output findings as
> `{severity, surface, missing-or-weak state, recommendation}`.

Owns: state completeness and feedback. Scoped out of: general usability heuristics
(owned by ux-review).

## 4. ux-review — usability heuristics + WCAG lens

> Run a usability-heuristic (Nielsen) and WCAG 2.2 AA conformance pass over
> `{screenshots}` for `{flows}`. **Scope to heuristics and accessibility only** — do
> not re-audit interaction states (the state-coverage lens owns those) or re-critique
> aesthetics (the visual lens owns those). Cite each heuristic violated and each WCAG
> success criterion failed, with the specific element. Output findings as
> `{severity, element, heuristic-or-SC, recommendation}`.

Owns: heuristic violations, WCAG conformance. Scoped out of: state coverage,
aesthetics.

## Expected overlap

Even scoped, `ux-review` and `interaction-design` may both flag a missing error state
(one as a heuristic violation, one as a state gap). This is expected — the synthesis
step (Phase 4) merges them into one row noting both lenses, rather than dropping
either. Do not pre-suppress it in the prompts; catch it in synthesis.
