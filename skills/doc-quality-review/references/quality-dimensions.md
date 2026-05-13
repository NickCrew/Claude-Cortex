# Quality Dimensions — Doc-Type-Aware Scoring Rubrics

Detailed scoring criteria with examples per dimension and doc type. A
"readable" doc looks different for a tutorial than for a reference;
applying a single rubric to both produces systematic misjudgment.

Pair this file with `references/personas.md`. Each dimension specifies
what 5/5 looks like for each doc type and which personas are most
affected.

## Doc types referenced below

| Type | Default primary persona | Characteristic prose style |
|---|---|---|
| Reference | API Looker-Up | Terse, scannable, table-heavy |
| Tutorial | Onboarding User | Conversational, second-person, example-rich |
| Guide | Onboarding User or Operator | Task-focused, step-oriented |
| Explanation / ADR | Architect Debugger | Discursive, trade-off aware |
| Runbook | Incident Responder | Imperative, decision-tree shaped |
| README | Onboarding User + Casual evaluator | Welcoming, route-out structure |

---

## Readability

**Core question:** Can the target persona read this without effort,
given their context and time pressure?

### Per-doc-type criteria

#### Reference — 5/5 looks like

```
authenticate(token: str, *, scope: str = "user") -> Session

Validates `token` and returns a Session. Raises InvalidTokenError if
the token is malformed or expired.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| token | str  | (required) | JWT bearer token |
| scope | str  | "user"     | Access scope: "user", "admin", or "service" |

Examples:
    auth.authenticate(jwt_token)
    auth.authenticate(jwt_token, scope="admin")
```

Terse. Signature first. Table for parameters. Examples last. Reader
finds what they need without reading prose.

#### Tutorial — 5/5 looks like

```
Now we'll create a Session for the current user. Sessions hold the
user's identity and access permissions, and most subsequent calls need
one.

Add this to `auth.py`:

```python
session = auth.authenticate(token)
print(f"Hello, {session.user.name}!")
```

If you see "Hello, <your name>!" — great, the token worked. If you see
`InvalidTokenError`, double-check the token in the previous step.
```

Conversational. Explains *why*, not just *what*. Shows expected
output. Anticipates the failure mode.

#### Runbook — 5/5 looks like

```
## Auth service returning 503

**Symptom:** Auth API returns 503 for >1% of requests.

**Recovery:**
1. Check `/health` endpoint: `curl prod.auth/health`
2. If returns 200: secondary issue — check downstream (ratelimit, db).
3. If returns 5xx or hangs: restart auth pods.
   ```bash
   kubectl rollout restart deploy/auth -n prod
   ```
4. Verify recovery: `/health` returns 200, error rate drops to <0.1%.

**Rollback:** None — restart is the recovery action.
**Escalation:** Page on-call DBA if error rate doesn't drop within 5min.
```

Imperative voice. Copy-pasteable. Decision points explicit. No prose
about *why* the auth service might fail.

#### Common failure across types

| Doc type | Common readability failure |
|---|---|
| Reference | Narrative paragraphs where a table would do |
| Tutorial | Reference-style terseness; reader can't follow the journey |
| Guide | Mixing imperative and descriptive voice |
| Runbook | Hedging language ("you might want to consider…"); background context before procedure |
| Explanation | Bullet lists where prose would explain trade-offs better |
| README | Marketing copy without actual signal; no Quick Start |

### Score levels

| Score | Reference | Tutorial | Runbook | Other types |
|-------|-----------|----------|---------|-------------|
| 5 | Terse, scannable, table-heavy where appropriate | Conversational, builds mental model, anticipates failures | Imperative, copy-pasteable, decision points clear | Type-appropriate prose for the persona |
| 3 | Some narrative bloat; signature still findable | Builds context but slows in places | Steps clear but hedged in places | Generally readable; some friction |
| 1 | Wall of prose; reader can't find one parameter | Pacing wrong; reader lost | Hedging throughout; too much background | Consistently hard for the target persona |

### Universal readability flags (apply across types)

| Flag | When |
|------|------|
| Sentence length | >30 words *unless* type/audience tolerates (an Architect Debugger reading an explanation can handle 40-word sentences; a runbook step shouldn't) |
| Paragraph length | >6 sentences in non-explanation types |
| Passive voice density | >40% of sentences — almost always a problem |
| Undefined jargon | Technical term used before definition (or before being established as audience-known vocabulary) |
| Ambiguous pronoun | "it/this/that" without referent within 1 sentence |

---

## Consistency

**Core question:** Does this doc use the same terms, formatting, and
conventions throughout — and match the rest of the doc set?

### Per-doc-type criteria

Consistency is largely universal — the same concept should use the
same word, the same admonition style, the same heading hierarchy
across the doc set. But the *templates* differ by type:

| Type | Template signals to check |
|---|---|
| Reference | Same heading structure (Signature, Parameters, Returns, Examples). Same parameter table format across pages. |
| Tutorial | Same step structure (Goal, Prereqs, Steps, Verify, Next). Same pacing across tutorials. |
| Guide | Same opening (When to use, Prereqs), same closing (Next steps, Related). |
| Explanation | Same structure (Context, Concept, Examples, Related). |
| ADR | Same sections (Context, Decision, Consequences, Status). Numbered. |
| Runbook | Same urgent-shape (Symptoms, Recovery, Verification, Rollback, Escalation). |
| README | Standard sections (What it is, Why use it, Install, Quick start, Docs links). |

### Score levels

| Score | Within-type | Across set |
|-------|-------------|------------|
| 5 | Clear template per type. All instances follow it. | Same vocabulary; consistent admonition / heading / code-block conventions |
| 3 | Templates visible but not universally followed | Most pages consistent; some drift |
| 1 | Every page is a snowflake | Different terminology / formatting on each page |

### Examples (across types)

**5/5:** Every reference page uses the same Parameters table format. Every
tutorial follows Goal → Prereqs → Steps → Verify. The term "skill" is used
consistently — never "module" or "capability" for the same concept.

**3/5:** Some reference pages have a Parameters table, others use a bulleted
list. Most tutorials follow the same shape but a few are structured
differently. "config" and "configuration" both appear, used interchangeably.

**1/5:** Each reference page has a different layout. Tutorials are written
by different authors at different times with different shapes. The same
feature is called "hooks" in some docs and "automations" in others.

---

## Audience Fit

**Core question:** Is the content calibrated for its intended persona?

### Per-doc-type criteria

This dimension is *by definition* persona-dependent. The agent must
score against the identified personas, not a generic standard.

#### Reference for API Looker-Up — 5/5

Assumes the reader knows what an API is, knows what they're looking
for, and just wants the precise answer. No "what is authentication?"
preamble. Type signatures are upfront. Edge cases enumerated.

#### Tutorial for Onboarding User — 5/5

States prerequisites explicitly. Introduces concepts before use. Builds
mental model layer by layer. No "obviously…" or "as you know…"
phrasing.

#### Runbook for Incident Responder — 5/5

Imperative. Steps are atomic. Decision points marked. Doesn't explain
*why* the failure mode exists (link to a postmortem or design doc if
the responder later wants context).

#### ADR for Architect Debugger — 5/5

Trade-offs explicit. Alternatives considered named. Constraints stated.
Honest about limitations. The reader can reconstruct the reasoning.

### Common audience misfits

| Doc type | Persona | Misfit symptom |
|---|---|---|
| Reference | API Looker-Up | Long narrative explanation before the signature |
| Tutorial | Onboarding User | Reference terseness; assumes knowledge they don't have |
| Tutorial | Onboarding User | Patronizing — explains things they already know from the prereqs |
| Runbook | Incident Responder | Background context before procedure; hedging language |
| ADR | Architect Debugger | Marketing prose; no trade-off discussion |
| Operator docs | Operator | "Configure as needed" without enumeration |

### Score levels

| Score | Audience fit |
|-------|--------------|
| 5 | Perfectly pitched for the named persona. Prerequisites stated. Right depth. No unexplained leaps or unnecessary explanation. |
| 4 | Mostly well-calibrated. Occasional knowledge gap or over-explanation. |
| 3 | Uneven. Some sections over- or under-pitched. |
| 2 | Significant mismatch. Doc would work better for a different persona. |
| 1 | Wrong audience entirely. Doc reads as if written for a persona other than the stated one. |

---

## Structure & Scannability

**Core question:** Can the target persona find what they need without
reading linearly?

### Per-doc-type criteria

Scannability requirements differ sharply by persona time pressure.

#### Reference (Looker-Up) — 5/5

Tables for parameter listings. Each symbol on its own deep-linkable
page. Front-loaded type signature. Examples below. No long prose
sections.

#### Tutorial (Onboarding User) — 5/5

Linear is the *expected* shape. Headings name the goal of each step.
Reader doesn't scan — they follow. But: clear "where am I" markers (Step
2 of 5). Each step ends with a verification.

#### Guide (Onboarding User or Operator) — 5/5

Goal at top. Prereqs visible. Numbered steps. Final "what's next"
section. Code examples immediately follow the concept they illustrate.

#### Runbook (Incident Responder) — 5/5

Symptom heading matches alert text. Recovery steps numbered, copy-
pasteable. Decision points marked. Critical info above the fold.

#### Explanation (Architect Debugger) — 5/5

Hierarchical headings build a mental outline. Trade-offs as named
sub-sections. Diagrams placed near related prose. References at the
bottom.

#### ADR — 5/5

Always 4 sections (Context / Decision / Consequences / Status). Status
header at the top. Date and number visible.

#### README — 5/5

Above-the-fold: what it is, why use it, Quick Start link. Below:
detailed sections, optional. Reader who scrolls only sees more depth,
not different content.

### Score levels

| Score | Behavior |
|-------|---------|
| 5 | Type-appropriate structure. Persona finds what they need without reading linearly (or follows the linear path with clear markers). |
| 4 | Mostly scannable for the persona. Minor friction. |
| 3 | Adequate structure. Some sections too long, some headings unhelpful. |
| 2 | Poor structure. Persona misses key info or has to read prose to find facts. |
| 1 | No useful structure. Wall of text or misleading headings. |

### Common structure failures

| Type | Failure |
|---|---|
| Reference | Long prose explanation before signatures; no parameter tables |
| Tutorial | No "where am I" markers; phases invisible |
| Runbook | Recovery buried below background; no skim path |
| Explanation | Bullet lists where prose with named sub-sections would build the model |
| ADR | Free-form structure (each ADR shaped differently) |
| README | Marketing copy above-the-fold instead of "what it is + Quick Start" |

---

## Actionability

**Core question:** Can the persona *do something* after reading?

### Per-doc-type criteria

Actionability matters very differently per type. Some docs aren't
supposed to drive action.

| Type | Actionability expectation |
|---|---|
| Reference | Modest — the reader was already coding; they extract one fact and resume |
| Tutorial | High — the reader follows steps, expects a working result |
| Guide | High — the reader has a task, expects to complete it |
| Explanation | Low — the reader is building a mental model; action follows later |
| ADR | Very low — the reader is researching context, not acting |
| Runbook | Very high — every line should map to an action |
| README | Modest — main action is "go install" or "go to docs" |

### Per-doc-type 5/5 examples

#### Tutorial / Guide — 5/5

```
1. Install with pip:
   ```bash
   pip install cortex-cli
   ```
2. Verify the install:
   ```bash
   cortex --version
   ```
   Expected output: `cortex 1.4.2` (or later).
3. If `cortex --version` says "command not found", check:
   - That `pip install` succeeded above
   - That your shell's `$PATH` includes pip's bin directory
```

Every step has a command. Expected output shown. Common failure mode
addressed.

#### Runbook — 5/5

Same shape but with the urgency of an incident: minimal prose,
imperative voice, decision points clear. (See Runbook example under
Readability.)

#### Reference — 5/5

```
auth.refresh_token(token)

Returns: new_token (str)
Raises:  InvalidTokenError if `token` is expired by more than 24h
Example: new_token = auth.refresh_token(old_token)
```

Action is implicit — the reader copies the call shape into their
code. Doesn't need step-by-step instructions; just needs the precise
contract.

#### Explanation — 5/5

```
Cortex separates "skills" (knowledge packages) from "agents" (personas)
because the failure modes differ. A skill that's wrong gives every agent
that uses it the wrong knowledge; an agent that's wrong only affects work
done by that agent.

This separation has a cost: skills and agents must coordinate. We chose
this trade-off because…
```

Builds the mental model. The "action" is later — when the reader is
designing skills or agents, they'll apply this understanding. Score
actionability low here is correct, not a failure.

### Score levels per doc type

| Doc type | 5/5 | 1/5 |
|---|---|---|
| Tutorial / Guide | Every step has a command + expected output | Tells reader "what" without showing "how" |
| Runbook | Imperative, copy-pasteable, decision-tree clear | Hedging language; reader has to infer steps |
| Reference | Precise contract; example shows the call shape | Vague description; reader can't tell what to write |
| Explanation | Mental model built; action follows later | (N/A — actionability shouldn't dominate explanation) |
| ADR | Context for future decisions captured | (N/A — ADRs aren't action-oriented) |

---

## Dimension weighting by doc type

The weights below reflect that some dimensions matter more for some
doc types. Apply these weights when computing the weighted total.

| Dimension | Reference | Tutorial | Guide | Explanation | ADR | Runbook | README |
|-----------|-----------|----------|-------|-------------|-----|---------|--------|
| Readability | 1.0 | 1.2 | 1.2 | 1.3 | 1.2 | 1.2 | 1.2 |
| Consistency | 1.2 | 0.8 | 1.0 | 0.8 | 1.2 | 1.0 | 1.0 |
| Audience Fit | 0.8 | 1.3 | 1.2 | 1.2 | 1.0 | 1.4 | 1.3 |
| Structure | 1.3 | 1.0 | 1.0 | 0.8 | 1.0 | 1.4 | 1.2 |
| Actionability | 1.0 | 1.5 | 1.3 | 0.5 | 0.5 | 1.6 | 1.0 |

Notes:
- Runbook weights actionability highest (1.6) — under incident pressure, structure and actionability dominate
- Explanation deprioritizes actionability (0.5) — building mental models is the goal
- ADR weights consistency high (1.2) — template adherence matters for an ADR set
- Reference weights structure high (1.3) — scannability is core to lookup

---

## Universal flags (apply across types)

| Metric | Flag when |
|--------|-----------|
| Sentence length | >30 words (relax to 40 for explanation/ADR) |
| Paragraph length | >6 sentences in non-explanation types |
| Passive voice density | >40% of sentences in a section |
| Undefined jargon | Technical term used before definition (in non-reference contexts) |
| Section length | >500 words without a subheading |
| Code example | Missing imports, incomplete, or wouldn't run |
| Ambiguous pronoun | "it/this/that" without clear referent within 1 sentence |
| Missing prerequisite | Instruction assumes knowledge not established |

These flags are universal *signals*, but their weight differs by type
and persona — see per-dimension scoring above.
