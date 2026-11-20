# Lens scoping prompts

Each sibling is invoked with a scoping prompt that keeps it to its distinct lens so the
synthesis doesn't double-count. Splice in the resolved scope values (`{persona}`,
`{flows}`, `{screenshots}`, `{viewports}`) from `review-scope.md`.

## 1. design-journey-review: visual and journey lens

> Review the visual system and the user journey for `{persona}` attempting `{flows}`,
> using the screenshots in `{screenshots}` across `{viewports}`. Cover aesthetic
> identity, color, typography, density, visual hierarchy, the golden path, friction,
> and daily-use fit. **Do not audit interaction states, Nielsen heuristics, or WCAG
> conformance**; the other lenses own those. Cite the specific screen and element.
> Output findings as `{severity, screen/element, issue, recommendation}`.

Owns: is it visually coherent, and does it serve the user's real workflow. Scoped out
of: interaction states, heuristics, WCAG.

## 2. ux-interaction-review: interaction-mechanics lens

> Audit the interaction mechanics for `{flows}` in `{screenshots}`. For every
> interactive surface, check coverage of loading, error, empty, success, and disabled
> states, feedback and timing, keyboard behavior and escape hatches, and error
> recovery. **Do not run a heuristic scan or a WCAG pass, and do not critique
> aesthetics.** Output findings as
> `{severity, surface, missing-or-weak state, recommendation}`.

Owns: state completeness, feedback, keyboard behavior, recovery. Scoped out of:
heuristics, WCAG, aesthetics.

## 3. ux-review: usability heuristics and WCAG lens

> Run a usability-heuristic (Nielsen) and WCAG 2.2 AA conformance pass over
> `{screenshots}` for `{flows}`. **Scope to heuristics and accessibility only.** Do
> not re-audit interaction states (the interaction-mechanics lens owns those) or
> re-critique aesthetics (the visual lens owns those). Cite each heuristic violated
> and each WCAG success criterion failed, with the specific element. Output findings as
> `{severity, element, heuristic-or-SC, recommendation}`.

Owns: heuristic violations, WCAG conformance. Scoped out of: interaction states,
aesthetics.

## Expected overlap

Even scoped, `ux-review` and `ux-interaction-review` may both flag a missing error
state (one as a heuristic violation, one as a state gap), and `design-journey-review`
and `ux-review` may both flag low contrast (one as a color-system issue, one as a WCAG
failure). This is expected. The synthesis step (Phase 4) merges each pair into one row
noting both lenses, rather than dropping either. Do not pre-suppress it in the
prompts; catch it in synthesis.
