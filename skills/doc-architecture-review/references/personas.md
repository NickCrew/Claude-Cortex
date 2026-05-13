# Personas Library

Concrete reader profiles for evaluating documentation. Use these — don't
invent fuzzier ones — when a sub-agent needs to score a doc against
specific reader needs.

A "good" hierarchy or progressive disclosure looks different for each
persona below. A reference doc that works for the **API Looker-Up** may
fail the **Onboarding User** entirely; that's not a defect, it's a
persona mismatch. The skill flags persona mismatches *as findings*, not
as universal errors.

This file is shared with `doc-quality-review`. When updating personas
here, sync the change to that skill's `references/personas.md` to keep
evaluation consistent across the doc-* family.

## How to use this library

1. **In Phase 0**, identify the 1–3 personas that the doc set serves
   *primarily*. A doc set serving more than 3 simultaneously is usually
   doing too much; flag that as an architectural finding.
2. **In agent prompts**, inline the relevant personas verbatim. Don't
   summarize — sub-agents calibrate better with the explicit profile
   than with a one-line audience label.
3. **In findings**, name the persona affected. "Findability fails for
   Incident Responder because alert text doesn't match runbook
   headings" beats "findability is poor."
4. **For multi-persona docs**, evaluate per-persona. The synthesis
   surfaces conflicts ("works for expert lookup, fails new user
   onboarding — current bias is toward expert").

## Personas

### Onboarding User

| Field | Value |
|---|---|
| Primary task | Learn enough to complete the first meaningful action successfully |
| Entry point | README, "Get Started" link, project landing page, blog post |
| Expertise | New to this project; may have general domain background but no project-specific context |
| Time pressure | Leisurely — willing to invest time, but easily lost or abandoned if confused |
| Success criterion | Finished a representative first task without abandoning; has a working mental model of what to learn next |

**Evaluates positively:**
- Quick start visible from the front door, completable in <15 minutes
- Each step explains *why*, not just *what*, so the mental model builds
- Clear "what's next" pointer at the end of each stage
- Vocabulary is introduced before use
- Examples are complete (no "fill in your own X" without showing what X looks like)

**Evaluates negatively:**
- Front door overwhelms with everything at once (no quick-start prominence)
- Required prerequisites aren't stated
- Jargon used before definition
- Examples reference undefined variables or omit setup
- Quick start doesn't actually work end-to-end

### API Looker-Up

| Field | Value |
|---|---|
| Primary task | Find the exact signature, parameter, behavior, or return value of one specific symbol |
| Entry point | Search, IDE autocomplete pointing to docs, error message linking to a reference page |
| Expertise | Already familiar with the broader API; needs this one detail |
| Time pressure | Focused — context-switched from coding, wants to context-switch back fast |
| Success criterion | Got the precise answer in under 30 seconds, didn't have to read narrative |

**Evaluates positively:**
- Direct URL per symbol (deep-linkable)
- Flat or shallow hierarchy — no required reading order
- Tables for parameter listings
- Type signatures upfront, examples below
- Cross-links to related symbols

**Evaluates negatively:**
- Reference content embedded in tutorial prose
- Required reading of multiple sections to find one fact
- Missing edge cases (what if the parameter is null? what does it return on failure?)
- Inconsistent template across reference pages — has to relearn the layout

### Incident Responder

| Field | Value |
|---|---|
| Primary task | Identify and apply the right recovery procedure for an active incident |
| Entry point | Alert, error message, runbook link from monitoring, on-call escalation |
| Expertise | Operational familiarity with the system; may not know this specific failure mode |
| Time pressure | Urgent — production is degraded, every minute matters |
| Success criterion | Found the right procedure in under 2 minutes; executed it without misstep |

**Evaluates positively:**
- Scenario-keyed entry (alert text matches runbook heading)
- Worst-case / most-common failure first, not last
- Steps are imperative, copy-pasteable
- Decision points clearly marked ("if X, do A; if Y, do B")
- Rollback path stated explicitly

**Evaluates negatively:**
- Background / "why" content before the procedure
- Discovery flow that requires understanding the system to find the right runbook
- Steps phrased as suggestions ("you might want to check…")
- Buried prerequisites
- Multiple runbooks for related scenarios with no cross-links

### Architect Debugger

| Field | Value |
|---|---|
| Primary task | Build a mental model of how a subsystem works in order to track down a problem or plan a change |
| Entry point | Code reading led them to "what is this responsible for and why?" |
| Expertise | Senior engineer, comfortable reading code, wants design intent and constraints |
| Time pressure | Focused but patient — willing to read for understanding |
| Success criterion | Understood design intent and trade-offs; can predict component behavior under stress |

**Evaluates positively:**
- Architecture docs that explain the design *and* what alternatives were rejected
- Diagrams that match the code (citable file:line for each box)
- ADRs that capture constraints and reasoning, not just decisions
- Honest discussion of known limitations
- Cross-links between conceptual docs and the code that implements them

**Evaluates negatively:**
- Marketing-style "we built X because it's amazing" (no constraint discussion)
- Diagrams that don't match the code
- Implementation details with no design rationale
- Missing ADRs for non-obvious choices

### Contributor

| Field | Value |
|---|---|
| Primary task | Make a code or doc change that fits project conventions and gets accepted |
| Entry point | CONTRIBUTING.md, issue they're working on, PR template |
| Expertise | Comfortable with the language and tooling; new to this project's conventions |
| Time pressure | Focused — has a specific change to make, wants to ship it |
| Success criterion | PR submitted that follows conventions, passes CI, gets approving review |

**Evaluates positively:**
- CONTRIBUTING.md surfaces dev setup, test commands, style rules in one place
- Clear conventions doc (file naming, commit format, PR shape)
- Examples of well-formed contributions to model on
- Explicit ownership of areas (who reviews what)

**Evaluates negatively:**
- Conventions scattered across many docs
- "We use $TOOL" without explaining how to run it locally
- PR feedback that cites unwritten rules
- Outdated dev setup that doesn't match current code

### Operator

| Field | Value |
|---|---|
| Primary task | Deploy, configure, monitor, or upgrade the system in their environment |
| Operational expertise; may not know application internals | |
| Entry point | Installation guide, configuration reference, deployment docs, upgrade notes |
| Time pressure | Focused — has a specific deployment / change to do |
| Success criterion | System running correctly in their environment; knows how to monitor it; knows how to roll back |

**Evaluates positively:**
- Complete configuration reference (every env var and config key documented)
- Concrete deployment recipes for common platforms
- Migration paths between versions, with explicit data/state implications
- Monitoring and alerting recommendations
- Capacity / scaling guidance with real numbers

**Evaluates negatively:**
- "Configure as needed" with no list of what's configurable
- Deployment docs that assume a specific platform without saying so
- Missing upgrade notes between versions
- No rollback guidance
- Vague capacity planning

## When to define a custom persona

These six cover most projects. Define a custom persona only when:

- The doc set serves a clearly distinct audience not represented (e.g.,
  a regulator reviewing for compliance, an auditor checking security
  controls, a researcher cross-referencing methodology)
- A core persona above almost fits but a specific dimension differs
  significantly (e.g., a *low-expertise operator* who needs more
  hand-holding than the standard Operator persona above)

Custom personas use the same five-field structure plus the two
"evaluates positively / negatively" lists. Add them inline in the
relevant report — don't try to maintain a project-specific persona
library here unless the project is large enough that the six standard
ones are routinely insufficient.

## Multi-persona conflicts

A single doc legitimately serving multiple personas faces structural
conflicts. Common conflicts and how to surface them:

| Conflict | Symptom | Surface as |
|---|---|---|
| New user vs expert | Reference doc with long narrative explanations slows expert lookup but a flat reference confuses new user | Finding: "structure biased toward <persona>; for <other persona>, recommend <change>" |
| Operator vs incident responder | Configuration reference doubles as runbook, mixing leisurely setup info with urgent recovery steps | Finding: "split runbook content into separate doc keyed by alert text" |
| Onboarding vs contributor | README tries to be both "what is this?" and "how to contribute?" | Finding: "split README into landing + CONTRIBUTING; landing optimizes for Onboarding User" |

Don't pretend conflicts don't exist. The most common architectural
failure is silently optimizing for one persona while claiming to serve
all of them.
