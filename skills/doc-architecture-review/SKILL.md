---
name: doc-architecture-review
description: 'Evaluate documentation information architecture: navigation paths, discoverability, progressive disclosure, cross-linking, and mental model alignment. This skill should be used when restructuring docs, adding new sections, or when users report difficulty finding information.'
version: 1.0.0
tags:
  - documentation
  - review
  - information-architecture
  - navigation
  - organization
triggers:
  - review doc architecture
  - doc organization review
  - documentation structure
  - can users find docs
  - doc navigation
  - information architecture
dependencies:
  skills:
    - doc-completeness-audit
  tools:
    - Read
    - Grep
    - Glob
    - Bash
    - Agent
token_estimate: ~3500
keywords:
  - doc architecture
  - doc organization
  - information architecture
  - doc
  - architecture
  - review
  - doc architecture review
---

# Documentation Architecture Review

Evaluate whether documentation is organized so that readers can find what they need,
understand where they are, and navigate efficiently. The output is an architecture
assessment with specific restructuring recommendations — not new content.

## When to Use

- When restructuring or reorganizing documentation
- When adding a new section or doc type to an existing set
- When users report "I know it's documented somewhere but can't find it"
- When the doc set has grown organically and needs rationalization
- After `doc-completeness-audit` identifies gaps — before filling them, ensure the structure
  can accommodate new content
- Periodic review of navigation and discoverability

## Quick Reference

| Resource | Purpose | Load when |
|----------|---------|-----------|
| `references/ia-heuristics.md` | Information architecture evaluation heuristics | Always (Phase 2) |

---

## Workflow Overview

```
Phase 1: Map         → Build the current doc structure map
Phase 2: Evaluate    → Assess against IA heuristics
Phase 3: Model       → Compare structure to user mental models
Phase 4: Report      → Produce the architecture review with recommendations
```

---

## Phase 1: Map the Current Structure

Build a complete picture of the documentation architecture.

### Step 1a: Physical Structure

Generate the file tree of all documentation:

```bash
find docs/ site/ -name '*.md' -o -name '*.html' | sort
```

Record:
- Directory hierarchy and nesting depth
- File count per directory
- Naming conventions (kebab-case, snake_case, mixed)

### Step 1b: Navigation Structure

Identify every way a reader can navigate:

| Navigation type | Where to find it |
|-----------------|-----------------|
| Sidebar / table of contents | `_config.yml` nav, front matter `nav_order`/`parent`, `SUMMARY.md` |
| Landing pages | `index.md` files — read each one for link lists |
| In-page cross-references | `[text](link)` and `{% link %}` references between pages |
| Breadcrumbs | Theme configuration or layout templates |
| Search | Search configuration, indexed content |
| Previous/Next links | Auto-generated or manual `nav_order` sequencing |

### Step 1c: Entry Points

Identify how readers arrive:

- **Direct** — typing a URL or bookmarking
- **Search** — site search or external search engine
- **Navigation** — sidebar, breadcrumb, landing page links
- **Cross-reference** — link from another doc page
- **External** — README, GitHub, blog post, error message linking to docs

Map which pages are reachable from each entry point. Pages unreachable from common
entry points are effectively invisible.

**Output:** A structure map with physical hierarchy, navigation paths, and entry points.

---

## Phase 2: Evaluate Against IA Heuristics

Assess the structure against seven heuristics. Load `references/ia-heuristics.md`
for detailed scoring criteria.

### Heuristic 1: Findability

Can readers locate information without knowing where it lives?

| Score | Criteria |
|-------|----------|
| 5 | Multiple discovery paths to every page. Search works. Navigation reflects user goals |
| 3 | Most content findable via navigation or search. Some pages only reachable by direct link |
| 1 | Content buried. No search. Navigation reflects implementation, not user needs |

**Check:**
- Orphaned pages (no inbound links, not in navigation)
- Dead ends (pages with no outbound links to related content)
- Search coverage (are all pages indexed? do headings use searchable terms?)
- Navigation labels (do they use user language or developer jargon?)

### Heuristic 2: Hierarchy Coherence

Does the nesting make sense? Can a reader predict where to find something?

| Score | Criteria |
|-------|----------|
| 5 | Clean, predictable hierarchy. Each level represents a meaningful grouping. Max 3 levels deep |
| 3 | Generally logical but some surprises. Occasional misplaced content. 4 levels in places |
| 1 | Arbitrary nesting. Related content scattered. Deep hierarchies (5+). Categories overlap |

**Check:**
- Depth — flag anything nested >3 levels
- Breadth — flag directories with >10 immediate children (consider subcategories)
- Sibling coherence — are items at the same level truly peers?
- Naming — do directory names describe contents from the reader's perspective?

### Heuristic 3: Progressive Disclosure

Does the doc set layer information from simple to complex?

| Score | Criteria |
|-------|----------|
| 5 | Clear learning path. Quick start → guides → reference → advanced. Each layer self-sufficient |
| 3 | Some layering exists but not explicit. Reader may hit advanced content before basics |
| 1 | All content at same depth. No distinction between introductory and advanced material |

**Check:**
- Quick start exists and is prominently linked
- Getting started path is linear and completable in <15 minutes
- Advanced topics are separated from basics, not interleaved
- Each doc states its prerequisites
- Cross-references point readers to deeper material, not shallower

### Heuristic 4: Cross-Linking Quality

Do links between pages create useful connections or noise?

| Score | Criteria |
|-------|----------|
| 5 | Links are contextual, bidirectional where appropriate, and create meaningful paths |
| 3 | Links exist but some are one-directional, orphaned, or link to the wrong section |
| 1 | Few cross-links. Pages are isolated. No "See also" or "Related" patterns |

**Check:**
- Link density — pages with zero outbound links, pages with >20
- Reciprocity — if A links to B, does B link back (where appropriate)?
- Context — links explain *why* the reader would follow them, not just "click here"
- Anchor precision — links go to the right section, not just the right page
- Broken links — links that resolve to 404 or wrong content

### Heuristic 5: Consistency of Patterns

Do similar pages follow similar structures?

| Score | Criteria |
|-------|----------|
| 5 | Clear templates per doc type. All reference pages look alike. All tutorials follow the same flow |
| 3 | Some patterns visible but not universal. Newer docs follow conventions, older ones don't |
| 1 | Every page is a snowflake. No discernible pattern across similar content types |

**Check:**
- Do all reference pages have the same sections?
- Do all tutorials follow the same progression?
- Do all guides have prerequisites and next steps?
- Are metadata conventions (front matter, titles, descriptions) consistent?

### Heuristic 6: Separation of Concerns

Are different doc types (reference, tutorial, guide, explanation) kept distinct?

| Score | Criteria |
|-------|----------|
| 5 | Clear separation. Reference is reference. Tutorials are tutorials. No hybrid pages |
| 3 | Mostly separated but some pages mix types (reference data inside a tutorial) |
| 1 | No separation. Single pages try to be reference, tutorial, and explanation simultaneously |

**Check:**
- Pages that mix "how to" with "what it is" with "API details"
- Tutorials that double as reference (readers can't scan for a specific flag)
- Reference pages that include narrative explanations better suited to guides
- Use the Diataxis framework as a lens: tutorials, how-to guides, reference, explanation

### Heuristic 7: Maintenance Burden

Is the structure sustainable as docs grow?

| Score | Criteria |
|-------|----------|
| 5 | Adding a new doc page requires no restructuring. Clear home for every doc type |
| 3 | Most new content has a natural home. Occasional need to reorganize |
| 1 | Every new page requires debate about where it goes. Structure is at capacity |

**Check:**
- Is there a clear directory/category for new feature docs?
- Are naming conventions documented and followed?
- Would doubling the doc set break the navigation?
- Are there catch-all directories growing without bounds?

---

## Phase 3: Mental Model Comparison

Compare the documentation structure to how users actually think about the product.

### User Mental Models

Identify the primary mental models users bring:

| Model type | Structure | Example |
|------------|-----------|---------|
| **Task-based** | "I want to do X" | Organized by workflow: install → configure → deploy |
| **Feature-based** | "I want to learn about X" | Organized by component: agents, skills, rules, hooks |
| **Role-based** | "I'm a [role]" | Organized by audience: user guide, admin guide, developer guide |
| **Chronological** | "What do I do first?" | Organized by sequence: getting started → daily use → advanced |

Most doc sets serve multiple models. The question is: **which model does the navigation
reflect, and does it match the primary user need?**

### Mismatch Indicators

- Users search for task-based terms but docs are organized by feature
- Getting started guide assumes feature knowledge the reader doesn't have yet
- Navigation uses internal terminology that users don't recognize
- Users land on the right page but can't find the right section

---

## Phase 4: Produce the Architecture Review

### Report Format

```markdown
# Documentation Architecture Review

**Review date:** YYYY-MM-DD
**Scope:** [doc set reviewed]
**Total pages:** N
**Max depth:** N levels
**Orphaned pages:** N

---

## Summary

[2-3 sentences: overall architecture assessment]

Heuristic scores:
| Heuristic | Score | Key Finding |
|-----------|-------|-------------|
| Findability | N/5 | [one line] |
| Hierarchy Coherence | N/5 | [one line] |
| Progressive Disclosure | N/5 | [one line] |
| Cross-Linking Quality | N/5 | [one line] |
| Consistency of Patterns | N/5 | [one line] |
| Separation of Concerns | N/5 | [one line] |
| Maintenance Burden | N/5 | [one line] |
| **Overall** | **N/35** | |

Architecture grade: [A (30-35) / B (24-29) / C (18-23) / D (12-17) / F (<12)]

---

## Structure Map

[File tree with annotations: orphan markers, depth warnings, misplacement flags]

---

## Critical Findings

### [Finding title]
**Heuristic:** [which]
**Impact:** [who is affected and how]
**Evidence:** [specific examples — pages, paths, search queries]
**Recommendation:** [specific restructuring action]

---

## Navigation Path Analysis

### Path: New User Onboarding
**Entry point:** [where they start]
**Goal:** [what they need to accomplish]
**Actual path:** [pages they traverse]
**Friction points:** [where they get lost or stuck]
**Ideal path:** [what it should be]

### Path: [Another key user journey]
...

---

## Orphaned Pages

| Page | Why It's Orphaned | Recommendation |
|------|-------------------|----------------|
| [path] | [no inbound links / not in nav] | [add to nav / link from X / archive] |

---

## Mental Model Alignment

**Primary user model:** [task / feature / role / chronological]
**Current structure model:** [which model the nav reflects]
**Alignment:** [match / partial / mismatch]
**Recommendation:** [restructure, add alternative navigation, or accept the gap]

---

## Restructuring Recommendations

Ordered by impact:

1. [Highest impact structural change]
2. [Second highest]
3. ...

---

## Strengths

[What's working well in the current architecture]
```

---

## Integration with Other Doc Skills

```
doc-maintenance         →  Structural health (links, orphans, folders)
doc-claim-validator     →  Semantic accuracy (do claims match code?)
doc-completeness-audit  →  Topic coverage (is everything documented?)
doc-quality-review      →  Prose quality (is it well-written?)
doc-architecture-review →  Information architecture (is it findable?)
```

Run this skill *after* `doc-completeness-audit` — you need to know what's missing before
evaluating whether the structure can accommodate it. Run *before* filling gaps, so new
content lands in the right place.

---

## Anti-Patterns

- Do not reorganize during the review — produce findings, not a new file tree
- Do not treat your preferred structure as the "correct" one — evaluate against user needs
- Do not evaluate archived docs (`docs/archive/`) — they are historical
- Do not confuse "I know where things are" with "a new user would know" — test with fresh eyes
- Do not recommend restructuring for its own sake — the cost of moving docs (broken links,
  muscle memory, bookmarks) must be justified by the improvement
- Do not ignore the cost of change — a mediocre-but-stable structure may be better than
  a perfect structure that requires moving 50 pages

---

## Bundled Resources

### References
- `references/ia-heuristics.md` — Detailed scoring criteria and examples for each heuristic
