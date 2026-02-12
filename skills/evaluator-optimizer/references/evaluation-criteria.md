# Evaluation Criteria

Quality rubrics, scoring frameworks, and convergence patterns for the evaluator-optimizer workflow. Use these criteria when evaluating code, documentation, or designs during refinement cycles.

## Code Quality Rubric

### Readability

| Score | Description |
|-------|-------------|
| 1-2 | Incomprehensible: no naming conventions, no structure, magic numbers everywhere |
| 3-4 | Poor: inconsistent naming, large functions, unclear control flow |
| 5-6 | Adequate: mostly readable but requires effort to follow in places |
| 7-8 | Good: clear naming, logical structure, well-organized modules |
| 9-10 | Excellent: reads like prose, self-documenting, intent obvious at every level |

**What to check**:
- Variable and function names describe their purpose
- Functions are short and do one thing
- Complex logic has explanatory comments (why, not what)
- Consistent formatting and indentation
- No deeply nested conditionals (max 3 levels)

### Performance

| Score | Description |
|-------|-------------|
| 1-2 | Severe: O(n^3) or worse where O(n) is possible, blocking operations in hot paths |
| 3-4 | Poor: unnecessary allocations, N+1 queries, no caching where obvious |
| 5-6 | Adequate: no severe issues but room for optimization |
| 7-8 | Good: appropriate algorithms, efficient data structures, reasonable caching |
| 9-10 | Excellent: optimal complexity, lazy evaluation where appropriate, measured and profiled |

**What to check**:
- Algorithm complexity matches the problem size
- Database queries are batched, not in loops
- Large data structures are not copied unnecessarily
- Hot paths avoid allocations
- Caching is used where data is expensive to compute and stable

### Security

| Score | Description |
|-------|-------------|
| 1-2 | Critical: SQL injection, XSS, unvalidated input in commands, secrets in code |
| 3-4 | Poor: missing input validation, overly broad permissions, no rate limiting |
| 5-6 | Adequate: basic validation present but incomplete edge case coverage |
| 7-8 | Good: input validated at boundaries, principle of least privilege, secrets managed properly |
| 9-10 | Excellent: defense in depth, security by default, audit logging, threat model addressed |

**What to check**:
- All user input is validated and sanitized
- Authentication and authorization are enforced consistently
- Secrets are not hardcoded or logged
- SQL queries use parameterized statements
- File paths and URLs are validated against traversal attacks
- Error messages do not leak internal details

### Maintainability

| Score | Description |
|-------|-------------|
| 1-2 | Unmaintainable: monolithic, no tests, undocumented, tightly coupled |
| 3-4 | Poor: some structure but high coupling, few tests, hard to modify safely |
| 5-6 | Adequate: modular but not fully decoupled, partial test coverage |
| 7-8 | Good: clear module boundaries, good test coverage, easy to extend |
| 9-10 | Excellent: SOLID principles, comprehensive tests, changes are isolated and safe |

**What to check**:
- Code follows single responsibility principle
- Dependencies are injected, not hardcoded
- Tests cover the critical paths
- Changing one module does not require changes in unrelated modules
- Configuration is externalized, not buried in code

---

## Documentation Scoring

### Accuracy

| Score | Description |
|-------|-------------|
| 1-2 | Contains factual errors, outdated information, or contradictions |
| 3-4 | Mostly correct but some inaccuracies or missing updates |
| 5-6 | Accurate for the main points but edge cases or caveats are missing |
| 7-8 | Correct and up-to-date with minor omissions |
| 9-10 | Fully accurate, verified against source, all edge cases documented |

**What to check**:
- Code examples compile and run correctly
- API endpoints, parameters, and return values match the implementation
- Version-specific information is labeled with versions
- No outdated screenshots or references

### Clarity

| Score | Description |
|-------|-------------|
| 1-2 | Impenetrable: jargon without definition, wall of text, no structure |
| 3-4 | Confusing: inconsistent terminology, unclear instructions, missing context |
| 5-6 | Passable: understandable with effort, could be clearer in spots |
| 7-8 | Clear: well-structured, defined terms, logical flow |
| 9-10 | Crystal clear: scannable headings, progressive complexity, a joy to read |

**What to check**:
- Jargon is defined on first use
- Sentences are concise (under 25 words preferred)
- Each section has a clear purpose
- Examples appear immediately after concepts
- Headings form a scannable outline

### Completeness

| Score | Description |
|-------|-------------|
| 1-2 | Severely incomplete: missing major sections, no examples |
| 3-4 | Gaps: covers the happy path but skips error handling, configuration, and edge cases |
| 5-6 | Adequate: covers the main use cases but missing advanced topics |
| 7-8 | Thorough: covers all common scenarios with examples and troubleshooting |
| 9-10 | Comprehensive: covers every scenario including edge cases, migration, and deprecation |

**What to check**:
- All public APIs/functions are documented
- Error scenarios are documented with recovery steps
- Prerequisites and setup are covered
- Examples cover basic and advanced usage
- FAQ or troubleshooting section addresses common issues

### Accessibility

| Score | Description |
|-------|-------------|
| 1-2 | Inaccessible: no structure, images without alt text, broken links |
| 3-4 | Poor: minimal structure, inconsistent formatting, hard to navigate |
| 5-6 | Adequate: proper headings and links but could be more navigable |
| 7-8 | Good: logical hierarchy, working links, table of contents, alt text |
| 9-10 | Excellent: fully accessible, multi-format, searchable, localized |

---

## Design Evaluation

### Usability

| Score | Description |
|-------|-------------|
| 1-2 | Unusable: users cannot complete basic tasks without help |
| 3-4 | Difficult: high cognitive load, unclear paths, frequent errors |
| 5-6 | Functional: tasks are completable but friction points exist |
| 7-8 | Good: intuitive flows, clear feedback, minimal learning curve |
| 9-10 | Excellent: delightful, efficient, anticipates user needs |

**What to check**:
- Primary actions are immediately discoverable
- Error states provide clear recovery paths
- Forms have sensible defaults and validation
- Navigation structure matches the user's mental model
- Onboarding guides new users to their first success

### Consistency

| Score | Description |
|-------|-------------|
| 1-2 | Chaotic: every page uses different patterns, colors, and interactions |
| 3-4 | Inconsistent: similar elements behave differently, mixed conventions |
| 5-6 | Mostly consistent: follows patterns in most places, occasional deviations |
| 7-8 | Consistent: uses a design system, predictable behavior throughout |
| 9-10 | Fully systematic: every element derives from a shared system, no exceptions |

**What to check**:
- Same action has the same visual treatment everywhere
- Spacing, typography, and colors use design tokens
- Interaction patterns are predictable (same gesture = same result)
- Terminology is consistent across the interface
- Icons have consistent meaning and style

### Accessibility (Design)

| Score | Description |
|-------|-------------|
| 1-2 | Failing: color contrast too low, no keyboard support, missing labels |
| 3-4 | Poor: some ARIA labels but major gaps, keyboard traps, tiny touch targets |
| 5-6 | Partial: passes automated checks but fails manual testing |
| 7-8 | Good: WCAG AA compliant, keyboard navigable, screen reader tested |
| 9-10 | Excellent: WCAG AAA, inclusive by design, tested with assistive technology users |

---

## Iteration Patterns

### Diminishing Returns

Each iteration should produce measurable improvement. Track the score delta:

| Iteration | Score | Delta | Action |
|-----------|-------|-------|--------|
| 1 | 45 | - | Continue |
| 2 | 68 | +23 | Continue |
| 3 | 82 | +14 | Continue |
| 4 | 89 | +7 | Continue |
| 5 | 91 | +2 | Stop (threshold met) |

If delta drops below 2 for two consecutive iterations, stop. Further iteration is unlikely to yield meaningful improvement.

### Common Iteration Sequence

For code refinement, address issues in this order:

1. **Correctness first**: Fix bugs and logic errors.
2. **Security second**: Close vulnerabilities.
3. **Readability third**: Rename, restructure, simplify.
4. **Performance fourth**: Optimize hot paths.
5. **Style last**: Polish formatting, comments, conventions.

For documentation refinement:

1. **Accuracy first**: Fix incorrect information.
2. **Completeness second**: Fill gaps in coverage.
3. **Clarity third**: Simplify language, improve examples.
4. **Accessibility last**: Structure, links, alt text.

---

## Convergence Criteria

### When to Stop

The evaluator-optimizer loop should terminate when any of these conditions are met:

| Condition | Description |
|-----------|-------------|
| **Quality threshold** | Overall score >= 90/100 |
| **Plateau** | Two consecutive iterations with delta < 2 |
| **Max iterations** | 5 iterations without reaching threshold (escalate for human review) |
| **Regression** | A refinement made the score worse (revert and stop) |
| **Scope creep** | Refinements are adding new features instead of improving existing ones |

### Quality Gate Template

Before declaring an artifact "done", verify:

```markdown
## Quality Gate

- [ ] Correctness: All tests pass, logic verified
- [ ] Security: No known vulnerabilities, inputs validated
- [ ] Readability: A new team member can understand this in 5 minutes
- [ ] Performance: No O(n^2) or worse in common paths
- [ ] Style: Matches project conventions
- [ ] Documentation: Public interfaces are documented
- [ ] Edge cases: Null, empty, max, concurrent scenarios handled

Overall score: __/100
Iterations completed: __
Recommendation: [SHIP / NEEDS REVIEW / NEEDS REWORK]
```

---

## Artifact-Specific Checklists

### Code Refinement Checklist

- [ ] All functions have a single, clear purpose
- [ ] No duplicated logic (DRY but not over-abstracted)
- [ ] Error paths are handled, not swallowed
- [ ] Types/contracts are explicit at module boundaries
- [ ] Tests cover happy path and at least 2 edge cases per function
- [ ] No TODO or FIXME comments remain (resolved or tracked)

### Documentation Refinement Checklist

- [ ] Every code example is tested and works
- [ ] All sections flow logically (no forward references without links)
- [ ] Prerequisites are stated upfront
- [ ] Troubleshooting covers the top 3 failure modes
- [ ] Language is direct: no "basically", "simply", "just"

### Design Refinement Checklist

- [ ] All states are designed (loading, empty, error, success, disabled)
- [ ] Color contrast passes WCAG AA (4.5:1 for text, 3:1 for large text)
- [ ] Touch targets are at least 44x44px
- [ ] Focus order is logical and visible
- [ ] Animations respect prefers-reduced-motion
