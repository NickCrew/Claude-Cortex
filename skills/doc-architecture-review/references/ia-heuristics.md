# Information Architecture Heuristics — Doc-Type-Aware Criteria

Detailed scoring criteria for each IA heuristic, parameterized by doc
type. A "good" architecture for a reference doc looks different from a
"good" architecture for a tutorial — applying a single rubric across
both produces systematic misjudgment.

Pair this file with `references/personas.md`. Each heuristic specifies
which personas it matters most for; the doc-type criteria say what 5/5
looks like for that combination.

## Doc types

These types appear throughout the heuristics below. Each has a
characteristic shape that informs scoring.

| Type | Characteristic shape | Default primary persona |
|---|---|---|
| **Reference** (API, CLI, config) | Flat, scannable, optimized for lookup | API Looker-Up |
| **Tutorial** | Linear, sequential, builds mental model | Onboarding User |
| **Guide / How-to** | Task-focused, prereq → task → next steps | Onboarding User or Operator |
| **Explanation / Conceptual** | Topic-grouped, dependency-ordered | Architect Debugger |
| **ADR / Decision Record** | Self-contained, chronological set | Architect Debugger |
| **Runbook** | Scenario-keyed, urgency-ordered | Incident Responder |
| **README / Landing** | Entry point, route to other types | Onboarding User + Casual evaluator |

A doc set typically contains multiple types. Evaluate each type against
its own criteria; the synthesis identifies cross-type problems
(misplaced docs, type-mixing).

---

## Heuristic 1: Findability

**Core question:** Can the target persona locate this content without
already knowing where it lives?

### Per-doc-type criteria for 5/5

| Doc type | "Findable" looks like |
|---|---|
| Reference | Stable URL per symbol; deep-linkable; alphabetical/categorical lookup; appears in IDE/tooling links |
| Tutorial | Visible from the front door; sequence position clear ("step 2 of 5") |
| Guide | Discoverable by task name; matches search queries readers would actually type |
| Explanation | Surfaceable when the concept is encountered elsewhere (linked from reference and tutorial) |
| ADR | Listed in an ADR index; filterable by status (proposed / accepted / superseded) |
| Runbook | Alert text matches runbook heading; runbook URL appears in the alert payload itself |
| README | Visible from project root, package registry page, CI badge, every entry surface |

### Diagnostic checks (universal)

- **Orphan analysis** — pages with zero inbound links. Excludes README/index entry points. (`scripts/link_graph.py` produces this.)
- **Search effectiveness** — do headings match queries the relevant persona would type? Test specifically: an Incident Responder searching the alert text, an Onboarding User searching "how to install"
- **Multiple discovery paths** — high-value pages should have ≥2 paths (nav + cross-link, or nav + search hit)
- **Navigation labeling** — labels reflect persona language, not internal jargon

### Persona-specific failure modes

- **Onboarding User**: front door doesn't surface quick start; terms are jargon
- **Looker-Up**: deep links don't work; reference content embedded in tutorial prose
- **Incident Responder**: runbook URL not in alert; alert text doesn't match heading
- **Operator**: config docs scattered; missing config items

### Scoring

| Score | Mechanical (link graph) | Qualitative |
|-------|-------------------------|-------------|
| 5 | 0% orphans (excluding entry pages) | Persona language; multiple discovery paths to high-value pages |
| 4 | <5% orphans | Mostly user-oriented; minor jargon |
| 3 | 5–15% orphans | Mixed user/system language |
| 2 | 15–30% orphans | System-oriented labels |
| 1 | >30% orphans | Developer jargon throughout |

---

## Heuristic 2: Hierarchy Coherence

**Core question:** Can the target persona predict where to find
something?

### Per-doc-type criteria for 5/5

| Doc type | "Coherent hierarchy" looks like |
|---|---|
| Reference | Flat or shallow (≤2 levels). Categorical groupings (by symbol kind, by module). Predictable lookup. |
| Tutorial | Linear with phases (1 level). Order matters. Phase boundaries visible. |
| Guide | 2 levels max — task category → task. Predictable: "how to X" for any X has an obvious home. |
| Explanation | Concept dependency graph respected. Foundational concepts before derived. |
| ADR | Flat list, sometimes filtered by status. Numbered for citation. |
| Runbook | 2 levels — scenario family → specific runbook. Family matches alert type. |
| README | Mostly flat — landing → 5–10 top-level destinations. |

### Why depth differs by doc type

A reference doc going 3 levels deep means the Looker-Up has to know the
category before they can find the symbol. A tutorial *needs* phase
hierarchy because order matters. A runbook *should* be 2 levels because
scenarios cluster naturally. Forcing reference into tutorial-style
depth, or flattening a tutorial into reference-style, both fail.

### Diagnostic checks

- **Depth test** — flag deviations from the type's expected depth
- **Sibling coherence** — items at the same level should be the same *kind*
- **Predictability test** — given a topic, can the persona guess the directory? Hesitation = ambiguity
- **Category overlap** — same topic in two directories signals unclear hierarchy

### Persona-specific failure modes

- **Looker-Up**: reference nested deeper than necessary; category guesswork required
- **Onboarding User**: tutorial flattened; phase boundaries invisible
- **Incident Responder**: runbook scenarios too granular (50 specific scenarios) or too broad (3 catch-all docs)

### Scoring

Apply the type-appropriate depth from the table above:

| Score | Depth deviation | Sibling coherence | Predictability |
|-------|-----------------|-------------------|----------------|
| 5 | At expected depth | All siblings are peers | Always predictable |
| 4 | One step deviation | Minor exceptions | Usually predictable |
| 3 | Some areas deviate | Some mixed siblings | Sometimes surprising |
| 2 | Frequently deviates | Frequent mixing | Often surprising |
| 1 | Wrong shape entirely | No coherence | Unpredictable |

---

## Heuristic 3: Progressive Disclosure

**Core question:** Does the doc set layer information appropriately for
its readers? **This heuristic applies very differently by doc type.**

### Per-doc-type criteria

| Doc type | Progressive disclosure expectation |
|---|---|
| Reference | **Anti-applies.** Forcing progressive disclosure into reference is the failure mode. Score N/A or score against "is the flat structure consistent and complete?" |
| Tutorial | **Required.** Each step builds on prior. Concepts introduced before use. No forward references. |
| Guide | **Light.** Prerequisites stated, task itself focused, "next steps" optional. |
| Explanation | **Required.** Foundational concepts before derived ones. Reading order matters. |
| ADR | **Anti-applies.** Each ADR is a self-contained unit. Score N/A. |
| Runbook | **Inverted.** Most urgent / most common scenario first, edge cases later. The "most basic" content is the *least useful* under incident pressure. |
| README | **Required at the doc-set level.** README is where the journey starts; it should layer toward Quick Start prominently. |

### Common misjudgment to avoid

A reference doc with no Quick Start section is *correctly structured*,
not deficient. Scoring it 2/5 because "advanced topics are interleaved
with basics" misreads what reference structure is for. Score N/A or
focus on reference-appropriate criteria (completeness, scannability)
instead.

### Diagnostic checks (apply only when doc type uses progressive disclosure)

- **Quick Start prominence** — for tutorial/guide/README sets, can the
  reader find quick start in <10 seconds from the front door?
- **Linear path completability** — can a fresh reader complete the
  getting-started path in <15 minutes?
- **Prerequisites stated** — each tutorial/guide names what the reader
  must already know
- **Forward references** — flag tutorials that reference concepts
  before introducing them

### Persona-specific failure modes

- **Onboarding User**: doc set lacks visible Quick Start; advanced before basics
- **Looker-Up**: reference forced into "intro / basics / advanced" structure that slows lookup
- **Incident Responder**: runbook starts with "understanding the system" before the procedure

### Scoring

| Score | For types where applies | For types where N/A |
|-------|-------------------------|---------------------|
| 5 | Clear layered path; each step builds | Score N/A — evaluate completeness/scannability instead |
| 3 | Layering exists but inconsistent | — |
| 1 | All content at same depth; no quick start | — |

---

## Heuristic 4: Cross-Linking Quality

**Core question:** Do links between pages create useful connections for
the relevant personas?

### Per-doc-type criteria for 5/5

| Doc type | Cross-linking pattern |
|---|---|
| Reference | Links to related symbols, types, methods. Low narrative density. Mutual links between related symbols. |
| Tutorial | Forward to next step, back to prerequisites. Sparse external links (don't break the flow). |
| Guide | Links to relevant references, related guides, optional deep-dives. |
| Explanation | Links to other concepts (dependency-aware), examples in tutorials, the code that implements the concept. |
| ADR | Links to superseded/superseding ADRs, related decisions, the code/system the ADR affects. |
| Runbook | Links to related runbooks (scenario neighbors), monitoring dashboards, incident channels. *No* deep design rationale links — wrong context. |
| README | Links to all major doc destinations + external project page. |

### Mechanical inputs (from `link_graph.py`)

- Reciprocity ratio (mutual link pairs / total directed edges)
- Link density per doc (avg outbound links per page)
- Hub identification (in-degree distribution)

### Qualitative checks (sonnet sub-agent)

- **Contextual links** — do links explain *why* the reader would follow them, or are they "click here" / dumped lists?
- **Anchor precision** — do links go to the right section, not just the right page?
- **Relevance per persona** — does the linked-to content serve the linking persona's task?

### Persona-specific failure modes

- **Looker-Up**: reference pages with no cross-links to related symbols (forces back-and-forth between pages)
- **Onboarding User**: tutorial links jump to advanced reference too eagerly
- **Architect Debugger**: ADRs that don't link to the code they affect or the ADRs they supersede

### Scoring

| Score | Reciprocity | Contextual links | Anchor precision |
|-------|-------------|------------------|------------------|
| 5 | >0.6 | All links contextual | Anchored to section |
| 4 | 0.4–0.6 | Mostly contextual | Mostly anchored |
| 3 | 0.2–0.4 | Mix of contextual and dumped | Page-level |
| 2 | 0.1–0.2 | Mostly "see also" lists | Page-level only |
| 1 | <0.1 | Few cross-links at all | — |

---

## Heuristic 5: Consistency of Patterns

**Core question:** Do similar pages follow similar structures?

### Per-doc-type criteria for 5/5

For *each* doc type, all instances of that type should follow a
consistent template. The templates differ by type but consistency
within type is universal.

| Doc type | Template signals to check |
|---|---|
| Reference | Same heading structure (Signature, Parameters, Returns, Examples, Edge cases). Same parameter table format. |
| Tutorial | Same step structure (Goal, Prereqs, Steps, Verify, Next). Same pacing. |
| Guide | Same opening (When to use, Prereqs), same closing (Next steps, Related). |
| Explanation | Same structure (Context, Concept, Examples, Related). |
| ADR | Same template (Context, Decision, Consequences, Status). Numbered. |
| Runbook | Same urgent structure (Symptoms, Recovery, Verification, Rollback, Postmortem reminder). |
| README | Standard sections (What it is, Why use it, Install, Quick start, Docs links, Contributing). |

### Diagnostic checks

- **Template adherence per type** — for each doc type, identify the implicit template and flag deviations
- **Frontmatter consistency** — same fields, same conventions
- **Heading hierarchy consistency** — `##` vs `###` use, capitalization
- **Code block conventions** — language tags, indentation

### When deviation is acceptable

A doc that intentionally deviates from the template for a documented
reason is not a finding. Score the deviation only if the agent can
identify *no* reason for the difference.

### Scoring

| Score | Within-type consistency |
|-------|-------------------------|
| 5 | Clear template per type. All instances follow it. Deviations are documented. |
| 4 | Templates visible. Most instances follow. Newer pages adhere more than older. |
| 3 | Some patterns visible per type, but not universal. |
| 2 | Frequent inconsistency within type. |
| 1 | Every page is a snowflake. No discernible per-type pattern. |

---

## Heuristic 6: Separation of Concerns

**Core question:** Are different doc types kept distinct, or do
individual pages mix types?

### What "separation" means per type

| Type | Should NOT contain |
|---|---|
| Reference | Long narrative tutorials. Decision rationale. (Cite the ADR / link the tutorial.) |
| Tutorial | Exhaustive parameter listings. (Link the reference.) Design rationale. |
| Guide | Reference data dumps. ADR content. |
| Explanation | Step-by-step procedures (link the tutorial). Exhaustive reference. |
| ADR | How-to content. (Decisions describe what was chosen, not how to use it.) |
| Runbook | Design rationale. Background reading. (Cite the architecture doc.) |
| README | Deep technical content. (Link the docs.) Tutorial content beyond a Quick Start tease. |

### Diataxis as a lens

The Diataxis framework (tutorial / how-to guide / reference /
explanation) is useful here. Single pages that try to be three of these
at once — the README that's also tutorial that's also reference — are
the dominant failure mode. Persona-mismatched mixing is the second.

### Persona-specific failure modes

- **Looker-Up reading reference**: narrative explanations slow lookup
- **Onboarding User reading tutorial**: parameter exhaustiveness drowns the journey
- **Incident Responder reading runbook**: background context wastes seconds during incidents
- **Architect Debugger reading ADR**: how-to instructions instead of decision rationale

### Diagnostic checks

- **Page audit** — for each page, identify its declared type and check for content of other types
- **Hybrid detection** — pages that combine 3+ types are almost always doing too much
- **Persona impact** — score the cost of the mixing per persona

### Scoring

| Score | Separation |
|-------|------------|
| 5 | Clear separation. Each page does one thing. Type-mixing rare and intentional. |
| 4 | Mostly separated. Occasional pages mix two types. |
| 3 | Notable mixing. Reference docs include narrative; tutorials include reference data. |
| 2 | Pervasive mixing. Most pages mix 2+ types. |
| 1 | No separation visible. Everything is everything. |

---

## Heuristic 7: Maintenance Burden

**Core question:** Is the structure sustainable as the doc set grows?

### Per-doc-type criteria for 5/5

| Doc type | Sustainable looks like |
|---|---|
| Reference | Auto-generates from code OR has clear update triggers tied to code changes |
| Tutorial | Stable backbone with versioned variants (or clear deprecation path for old tutorials) |
| Guide | Task-focused (ages well) rather than implementation-focused (rots fast) |
| Explanation | Concept-stable; updated when design actually changes, not on every code change |
| ADR | Append-only — never edit, supersede with new ADR |
| Runbook | Tested in incident drills; obvious owner; updated after each related incident |
| README | Minimal surface to maintain — link out rather than duplicate |

### Diagnostic checks

- **Adding a new doc** — does any new feature have an obvious home in the existing structure?
- **Naming conventions** — are they documented and followed?
- **Catch-all directories** — are any directories growing unbounded (e.g., `docs/misc/`)?
- **Doubling test** — would a 2x doc-set break the navigation or hierarchy?

### Persona-specific impact

- Maintenance burden is felt mostly by **Contributor**, but its symptoms surface to all personas as stale docs
- A doc set that's hard to maintain produces stale content that fails every persona

### Scoring

| Score | Maintainability |
|-------|----------------|
| 5 | New docs have clear homes. Conventions documented and followed. Doubling-tested. |
| 4 | Most new content has a natural home. Occasional reorg needed. |
| 3 | Several gray-area placements. Some catch-all directories growing. |
| 2 | Frequent placement debate. Catch-all directories expanding. |
| 1 | Structure at capacity. Each new doc requires restructuring. |

---

## Aggregating per-persona scores

When evaluating a doc set against multiple personas, score each
heuristic per-persona, not as a single average. The synthesis surfaces
conflicts:

```
Heuristic 2 (Hierarchy Coherence)
  For Looker-Up: 5/5 (flat reference structure, predictable lookup)
  For Onboarding User: 2/5 (no learning path; expected to navigate flat
    structure without guidance)
  Synthesis: structure biased toward Looker-Up. If Onboarding User is
    a primary persona, recommend layering a Quick Start above the
    flat reference.
```

Per-persona scoring is what makes the audit useful when audiences
conflict. A single average score hides the bias and produces
recommendations that help one persona at the cost of another.
