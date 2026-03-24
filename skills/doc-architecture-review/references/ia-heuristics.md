# Information Architecture Heuristics — Detailed Criteria

Detailed scoring criteria and diagnostic questions for each IA heuristic.
Load this reference at the start of an architecture review.

---

## Heuristic 1: Findability

**Core question:** Can readers locate information without already knowing where it lives?

### Diagnostic Checks

**Orphan analysis:**
- List every page with zero inbound links from other doc pages
- List every page not present in sidebar navigation
- A page reachable *only* via direct URL is effectively hidden

**Search effectiveness:**
- Do page titles use terms readers would search for?
- Do headings match common queries? (Test: "How do I install?" — is there a heading with "install"?)
- Are synonyms handled? (e.g., "setup" vs "installation" vs "getting started")

**Navigation labeling:**
- Do navigation labels describe *what the reader gets*, not *what the system calls it*?
- "Getting Started" > "Quickstart Guide" > "Module: Init" (progressively less user-oriented)

**Multiple paths:**
- Can the reader find key content via at least 2 of: navigation, search, cross-reference, landing page?
- High-value pages (install, quick start, FAQ) should have 3+ paths

### Scoring Detail

| Score | Orphan rate | Discovery paths | Nav labels |
|-------|-------------|-----------------|------------|
| 5 | 0% orphaned | 3+ paths to every page | User-goal-oriented |
| 4 | <5% orphaned | 2+ paths to most pages | Mostly user-oriented |
| 3 | 5-15% orphaned | Most via nav, some only by link | Mixed user/system |
| 2 | 15-30% orphaned | Many only via direct URL | System-oriented |
| 1 | >30% orphaned | Most content hard to discover | Developer jargon |

---

## Heuristic 2: Hierarchy Coherence

**Core question:** Does the nesting make sense? Can a reader predict where something lives?

### Diagnostic Checks

**Depth test:**
- Max depth should be 3 levels for user-facing docs
- Depth 4 acceptable for reference subcategories
- Depth 5+ is a red flag — users lose context of where they are

**Sibling test:**
- Items at the same level should be the same "kind" of thing
- Bad: `guides/` contains `cli.md`, `tui.md`, `what-is-cortex.md` (mixed type)
- Good: `guides/` contains `cli.md`, `tui.md`, `skills.md` (all tool guides)

**Predictability test:**
- Given a topic, can you guess which directory it's in without looking?
- If you'd hesitate between two locations, the hierarchy is ambiguous

**Category overlap test:**
- Do any two directories contain pages that cover the same topic?
- Example: "configuration" documented in both `reference/` and `guides/` — is it clear which is which?

### Scoring Detail

| Score | Max depth | Sibling coherence | Predictability |
|-------|-----------|-------------------|----------------|
| 5 | ≤3 | All siblings are peers | Always predictable |
| 4 | ≤3, one area at 4 | Minor exceptions | Usually predictable |
| 3 | 4 in several areas | Some mixed siblings | Sometimes surprising |
| 2 | 4-5 | Frequent mixing | Often surprising |
| 1 | 5+ | No coherence | Unpredictable |

---

## Heuristic 3: Progressive Disclosure

**Core question:** Does the doc set layer information from simple to complex?

### Diagnostic Checks

**Learning path test:**
- Is there an explicit path from "zero knowledge" to "productive user"?
- Does the path follow: Install → First use → Core concepts → Daily workflows → Advanced topics?
- Can a new user complete the getting-started path without hitting advanced content?

**Prerequisite chains:**
- Do docs state their prerequisites?
- Are prerequisite docs linked?
- Can you follow the prerequisite chain without circular references?

**Depth layering:**
- Quick start: 5-minute path to first success
- Guides: 15-30 minute focused workflows
- Reference: complete but dense — for lookup, not learning
- Advanced: assumes fluency with basics

**Anti-patterns:**
- Tutorial that requires reading the reference first
- Quick start that takes >15 minutes
- Getting started page that mentions every feature
- Advanced topics interleaved with basics in the same page

### Scoring Detail

| Score | Learning path | Prerequisites | Layer separation |
|-------|---------------|---------------|------------------|
| 5 | Explicit, linear, <15min | Stated and linked | Clear layers, each self-sufficient |
| 4 | Exists but not prominently linked | Mostly stated | Layers exist, minor bleeding |
| 3 | Implicit — reader can piece it together | Sometimes stated | Some pages mix levels |
| 2 | Fragmented — reader backtracks frequently | Rarely stated | Significant mixing |
| 1 | No path — reader must figure out order | Never stated | All content at same depth |

---

## Heuristic 4: Cross-Linking Quality

**Core question:** Do links create useful connections or noise?

### Diagnostic Checks

**Link density distribution:**
- Pages with 0 outbound links → isolated, add cross-references
- Pages with 1-5 links → normal for focused pages
- Pages with 6-15 links → normal for landing/index pages
- Pages with 15+ links → potentially overwhelming, consider restructuring

**Contextual linking:**
- Good: "For the full list of flags, see the [CLI Reference](reference/cli.md)."
- Bad: "See [here](reference/cli.md)."
- Worst: No link at all when reader would naturally want one

**Reciprocity check:**
- If a tutorial references a concept explained elsewhere, does that explanation link back
  to the tutorial as a practical example?
- Not all links need reciprocity — but high-value connections should be bidirectional

**Dead-end check:**
- Does every non-index page have at least one "where to go next" link?
- Pages that end without a next step leave the reader stranded

### Scoring Detail

| Score | Isolation rate | Context quality | Dead ends |
|-------|---------------|-----------------|-----------|
| 5 | 0% isolated pages | All links explain why | 0 dead ends |
| 4 | <5% isolated | Most links contextual | <5% dead ends |
| 3 | 5-15% isolated | Mixed quality | 5-15% dead ends |
| 2 | 15-30% isolated | Many "click here" links | 15-30% dead ends |
| 1 | >30% isolated | No context on links | >30% dead ends |

---

## Heuristic 5: Consistency of Patterns

**Core question:** Do similar pages follow similar structures?

### Diagnostic Checks

**Template compliance:**
- Pick 3 pages of the same type (e.g., 3 reference pages). Do they have the same sections?
- Do they follow the same order?
- Do they use the same table structure for similar data?

**Metadata consistency:**
- Do all pages have front matter?
- Do similar pages use the same front matter fields?
- Are titles formatted consistently (sentence case vs title case)?

**Convention documentation:**
- Are the expected patterns documented anywhere (CONTRIBUTING.md, style guide)?
- If yes, do the actual pages follow them?

### Scoring Detail

| Score | Same-type consistency | Metadata | Conventions documented |
|-------|----------------------|----------|----------------------|
| 5 | All same-type pages match | Uniform | Yes, and followed |
| 4 | Minor variations | Mostly uniform | Yes, mostly followed |
| 3 | Some match, some don't | Inconsistent | Partially |
| 2 | Rare consistency | Very inconsistent | No |
| 1 | Every page unique | No pattern | No |

---

## Heuristic 6: Separation of Concerns

**Core question:** Are different doc types kept distinct?

### The Diataxis Framework

Use as a diagnostic lens:

| Type | Purpose | Form | Reader's question |
|------|---------|------|-------------------|
| **Tutorial** | Learning | Guided steps | "Help me get started" |
| **How-to Guide** | Problem-solving | Steps to achieve a goal | "Help me do X" |
| **Reference** | Information | Dry description of facts | "What are the details?" |
| **Explanation** | Understanding | Discursive analysis | "Help me understand why" |

**Red flags for mixing:**
- A reference page that starts with "Let's walk through..." (tutorial language)
- A tutorial that includes a full parameter table (reference content)
- A how-to guide that explains the history and design rationale (explanation content)
- An explanation page with numbered steps (how-to guide content)

### Scoring Detail

| Score | Separation | Hybrid pages | Reader impact |
|-------|------------|--------------|---------------|
| 5 | Clean — each page is one type | 0% | Reader always knows what to expect |
| 4 | Mostly clean | <10% | Minor confusion |
| 3 | Some mixing | 10-25% | Reader sometimes gets unexpected content |
| 2 | Frequent mixing | 25-50% | Reader often has to skip irrelevant sections |
| 1 | No separation | >50% | Every page tries to do everything |

---

## Heuristic 7: Maintenance Burden

**Core question:** Is the structure sustainable as docs grow?

### Diagnostic Checks

**Growth simulation:**
- If you added 5 new features tomorrow, is there a clear home for each doc?
- If you doubled the doc count, would navigation still work?
- Are there catch-all directories growing without bounds?

**Naming convention sustainability:**
- Do naming conventions scale? (`feature-X.md` works for 10 features, not 100)
- Are names descriptive enough to disambiguate at scale?

**Contribution friction:**
- How many files does a contributor need to edit to add one new doc page?
  (Best: 1 — the page itself. Worst: page + nav config + index + sidebar + breadcrumbs)
- Is there a documented process for adding docs?

**Duplication risk:**
- Are there patterns that encourage copy-paste documentation?
- Is information stated in one place and referenced, or duplicated across pages?

### Scoring Detail

| Score | Growth capacity | Contribution friction | Duplication |
|-------|----------------|----------------------|-------------|
| 5 | Clear home for new content | 1 file to add a page | Information in one place |
| 4 | Mostly clear, rare ambiguity | 1-2 files | Minor duplication |
| 3 | Sometimes unclear | 2-3 files | Moderate duplication |
| 2 | Frequently unclear | 3-5 files | Significant duplication |
| 1 | No room for growth | 5+ files | Widespread duplication |
