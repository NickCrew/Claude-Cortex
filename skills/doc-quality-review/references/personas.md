# Personas Library

Concrete reader profiles for evaluating documentation quality. Use these
— don't invent fuzzier ones — when a sub-agent needs to score a doc
against specific reader needs.

A "readable" or "well-structured" doc looks different for each persona
below. Terse scannable prose works for the **API Looker-Up** but loses
the **Onboarding User**; conversational explanation builds the
Onboarding User's mental model but slows the Looker-Up. Apply the
appropriate standard, not a generic one.

This file is shared with `doc-architecture-review`. When updating
personas here, sync the change to that skill's `references/personas.md`
to keep evaluation consistent across the doc-* family.

## How to use this library

1. **In Phase 1**, identify the 1–3 personas that the doc serves
   *primarily*. Some docs serve only one persona (a runbook is for
   Incident Responder); others serve two or three (a CLI reference
   serves both API Looker-Up and Operator).
2. **In agent prompts**, inline the relevant personas verbatim. Don't
   summarize — sub-agents calibrate better with the explicit profile.
3. **Score per-persona when audiences differ.** A doc that scores 5/5
   readability for Looker-Up may score 2/5 for Onboarding User. The
   higher score isn't "right" — both are real evaluations.
4. **Surface persona mismatches as findings**, not bugs. "Tutorial
   reads like reference — works for API Looker-Up, fails Onboarding
   User" is a real architectural finding.

## Personas

### Onboarding User

| Field | Value |
|---|---|
| Primary task | Learn enough to complete the first meaningful action successfully |
| Entry point | README, "Get Started" link, project landing page, blog post |
| Expertise | New to this project; may have general domain background |
| Time pressure | Leisurely — willing to invest time, but easily lost |
| Success criterion | Finished a representative first task; has a working mental model |

**Quality signals — positive:**
- Conversational tone that builds context
- Concepts introduced before use, with brief definition or analogy
- Generous examples — "this is what success looks like"
- Cross-links pointing forward to next stage of the journey
- Active voice, second person ("you do X")

**Quality signals — negative:**
- Reference-style terseness that assumes prior knowledge
- Jargon without definition
- Walls of code with no commentary
- Implicit prerequisites
- Passive constructions ("the system can be configured")

### API Looker-Up

| Field | Value |
|---|---|
| Primary task | Find the exact signature, parameter, or behavior of one specific symbol |
| Entry point | Search, IDE autocomplete, error message link |
| Expertise | Familiar with the broader API |
| Time pressure | Focused — wants to context-switch back to coding fast |
| Success criterion | Answered in under 30 seconds without reading narrative |

**Quality signals — positive:**
- Type signatures up-front (table format ideal)
- Terse, scannable prose
- Examples are minimal and focused on the one thing
- Edge cases enumerated
- Consistent template across pages — no relearning required

**Quality signals — negative:**
- Narrative explanation before the signature
- "See also" sections that bury the answer
- Paragraphs where a table would do
- Missing edge cases (null behavior, error returns)
- Inconsistent layout across reference pages

### Incident Responder

| Field | Value |
|---|---|
| Primary task | Identify and apply the right recovery procedure for an active incident |
| Entry point | Alert text, runbook link, on-call escalation |
| Expertise | Operational familiarity, may not know this specific failure mode |
| Time pressure | Urgent — every minute costs |
| Success criterion | Found the procedure in under 2 minutes; executed without misstep |

**Quality signals — positive:**
- Imperative voice — "Run X. Verify Y. If Z, do W."
- Decision points clearly marked
- Copy-pasteable commands
- Rollback path stated up front
- Worst-case / most-common scenario first

**Quality signals — negative:**
- Hedging language ("you might want to consider…")
- Background / explanation before the procedure
- Steps that aren't actually steps ("understanding the system…")
- Missing rollback
- Cute prose ("Don't panic!" wastes time)

### Architect Debugger

| Field | Value |
|---|---|
| Primary task | Build a mental model of a subsystem to track down a problem or plan a change |
| Entry point | Code reading → "what is this responsible for?" |
| Expertise | Senior; comfortable with code |
| Time pressure | Patient if the answer is good |
| Success criterion | Understood design intent; can predict behavior |

**Quality signals — positive:**
- Honest discussion of trade-offs ("we chose X over Y because…")
- Diagrams that match the code (citable file:line per box)
- Constraints documented, not just decisions
- Known limitations called out
- Links to related ADRs and conceptual docs

**Quality signals — negative:**
- Marketing prose without trade-off analysis
- Diagrams that don't match the current code
- Implementation detail without design rationale
- "Best practice" claims without context

### Contributor

| Field | Value |
|---|---|
| Primary task | Make a change that fits conventions and gets accepted |
| Entry point | CONTRIBUTING.md, issue, PR template |
| Expertise | Knows the language; new to this project's conventions |
| Time pressure | Focused — wants to ship the change |
| Success criterion | PR submitted that follows conventions and gets approved |

**Quality signals — positive:**
- All conventions in one place (CONTRIBUTING.md or linked from it)
- Working dev-setup commands
- Concrete examples of well-formed contributions
- Explicit ownership ("@team-X reviews changes to /server")

**Quality signals — negative:**
- Conventions scattered across many docs
- Dev setup that doesn't actually work
- Implicit rules surfaced only in PR review
- Outdated examples

### Operator

| Field | Value |
|---|---|
| Primary task | Deploy / configure / monitor / upgrade in their environment |
| Entry point | Installation guide, config reference, deploy docs |
| Expertise | Operational; may not know application internals |
| Time pressure | Focused — specific deployment task |
| Success criterion | System running correctly; knows how to monitor and roll back |

**Quality signals — positive:**
- Every env var and config key documented (no "configure as needed")
- Concrete deployment recipes per platform
- Explicit upgrade paths between versions
- Monitoring / alerting recommendations
- Capacity guidance with real numbers

**Quality signals — negative:**
- "Configure as needed" without enumerating what's configurable
- Platform-specific instructions presented as platform-neutral
- Missing rollback guidance
- Vague capacity claims ("scales horizontally")

## Doc type × default persona

When persona is unclear, the doc type strongly suggests one. Use these
defaults if the doc itself doesn't make audience explicit, but always
prefer evidence over assumption.

| Doc type | Default primary persona | Common secondary |
|---|---|---|
| Quick start / Getting started | Onboarding User | Casual evaluator |
| Tutorial | Onboarding User | Contributor |
| API reference | API Looker-Up | Architect Debugger |
| CLI reference | API Looker-Up | Operator |
| Configuration reference | Operator | Architect Debugger |
| Architecture doc / ADR | Architect Debugger | Contributor |
| How-to guide | Onboarding User or Operator (depends on subject) | — |
| Runbook | Incident Responder | Operator |
| README | Onboarding User | Casual evaluator |
| CONTRIBUTING | Contributor | — |

## Multi-persona conflicts

A single doc legitimately serving multiple personas with different
needs has structural tension. Surface as findings:

| Conflict | Common symptom | How to surface |
|---|---|---|
| Looker-Up vs Onboarding User | Reference doc with long narrative explanations | "Structure biased toward Onboarding; for Looker-Up, recommend separating quick reference table from narrative" |
| Operator vs Incident Responder | Config reference embedded with runbook | "Split into config reference (Operator) + runbook (Incident Responder); current mix slows both" |
| Architect Debugger vs Contributor | Architecture doc that's also "how to contribute to this subsystem" | "Split design rationale (Architect) from contribution conventions (Contributor)" |

Persona conflicts that are *intentional and well-managed* (e.g., a
README that explicitly handles both Onboarding and Casual evaluator
with clear sections per audience) are not findings — note the
intentional split as a strength.
