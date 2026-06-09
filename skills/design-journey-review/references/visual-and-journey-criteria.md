# Visual & Journey Evaluation Criteria

Practical criteria and checklists for the design-journey-review skill. Use these tables during evaluation; they are the "what to look for" companion to the workflow steps in SKILL.md.

---

## Aesthetic Archetypes

| Archetype | Key Signals | Common Pitfalls |
|-----------|------------|-----------------|
| Mission control | Dark bg, monospace data, status-colored indicators, dense | Illegible small text, color overload |
| Swiss/minimal | White space, geometric sans, strict grid, muted palette | Feels empty with real data, poor density |
| Linear/GitHub | Dark panels, pill chips, subtle borders, blue accent | Looks generic without distinctive elements |
| Editorial | Large type, serif headings, generous spacing | Wastes space on operational tools |
| Dashboard/enterprise | Card grid, neutral colors, chart-heavy | Cookie-cutter, lacks personality |

---

## Color System Evaluation

### Layer Depth

| Layer | Purpose | Minimum contrast with adjacent |
|-------|---------|-------------------------------|
| Background (--bg) | Page canvas | N/A (deepest) |
| Surface 1 (--panel) | Card/section background | 2-4% luminance shift from bg |
| Surface 2 (--panel-2) | Nested or elevated surface | 2-4% from surface 1 |
| Elevated (popover, dropdown) | Floating above content | Shadow + 3-5% from surface 2 |
| Border | Separation between elements | Visible but not dominant |

### Semantic Colors

| Semantic | Hue Band | Must NOT collide with |
|----------|---------|----------------------|
| Success/good | Green (120-160) | Phase colors using green |
| Warning/warn | Amber/yellow (30-60) | Phase colors using gold/yellow |
| Error/bad | Red (340-10) | Phase colors using red/pink |
| Info/accent | Blue/purple (200-280) | Phase colors using blue |
| Stale/neutral | Gray (desaturated) | Disabled states |

### Phase/Category Colors

Evaluation questions:
- Are any two adjacent in hue wheel AND used together? (collision risk)
- At chip size (12px text, ~60px wide), can a user distinguish each from its neighbors?
- In light mode, do the same colors maintain their identity? (not all become "pastel mush")
- Do any share the same hue band as a semantic color? (confusion between "phase 3" and "success")

---

## Typography Evaluation

### Size Scale Assessment

| Role | Typical Range | Red Flag If |
|------|--------------|-------------|
| Page title | 18-24px | Larger than 28px (eats viewport) |
| Section heading | 14-18px | Same size as body (no hierarchy) |
| Body/primary content | 13-15px | Below 12px (strain) |
| Secondary/metadata | 11-13px | Below 10px (illegible on 96dpi) |
| Smallest (badges, timestamps) | 10-11px | Below 9px (unreadable) |

### Weight Usage

| Weight | Correct Usage | Overuse Signal |
|--------|---------------|----------------|
| 700 (bold) | Primary identifiers, headings, warnings | More than ~15% of visible text |
| 600 (semibold) | Secondary emphasis, labels | Indistinguishable from 700 at small sizes |
| 400 (normal) | Body text, metadata | Everything else uses 400 (no hierarchy) |
| 300 (light) | Decorative only, large sizes | Used below 16px (too thin to read) |

### Monospace Checklist

Monospace should be reserved for:
- [ ] Version numbers / semver strings
- [ ] Branch names / git refs
- [ ] Code snippets / CLI commands
- [ ] Identifiers that are "typed somewhere" (URLs, keys)

Monospace should NOT be used for:
- [ ] Labels and headings
- [ ] Prose descriptions
- [ ] Navigation items
- [ ] Button text

---

## Spacing Rhythm

### Base Unit Detection

Count the most common padding/margin values. The base unit is typically:
- 4px (tight, data-dense tools)
- 8px (standard, most apps)
- Multiples should be 1x, 1.5x, 2x, 3x, 4x (not arbitrary)

### Rhythm Breaks

A rhythm break is when adjacent elements use incompatible spacing:
- Section A has 16px gap below, section B has 12px above (visual hiccup)
- Cards use 12px internal padding but 24px between them (feels disconnected)
- Inline elements use 4px gaps but their container has 20px padding (scale mismatch)

---

## Information Density

### Density Evaluation Matrix

For each major UI section, assess:

| Question | Score |
|----------|-------|
| How often does the user look at this per session? | daily / weekly / once |
| Does it answer a question the user has RIGHT NOW? | yes / sometimes / rarely |
| Could it be collapsed without losing "at a glance" value? | no / yes-after-first-use / yes-always |
| What percentage of viewport does it consume? | measure |

Scoring:
- daily + yes + no-collapse + <20% viewport = **justified**
- once + rarely + yes-always + >15% viewport = **overweight, collapse**
- daily + yes + yes-after-first-use = **auto-collapse after Nth visit**

### Density Inversions

A density inversion is when low-value content occupies high-value position:
- Above the fold but used once a week
- Large section header with tiny actual content below
- Instructional text taking more space than the data it describes
- Help text visible after the user already knows the tool

---

## User Journey Evaluation

### Golden Path Friction Scoring

For each step in the golden path, score friction:

| Friction Type | Score | Example |
|---------------|-------|---------|
| Extra click (could be zero-click) | 1 | Tab switch to reach content |
| Scroll required | 1 | Key content below fold |
| Context switch (leave this view) | 2 | Open another tool to complete |
| Wait (>500ms) | 2 | Slow render, network fetch |
| Memory required | 3 | Remember a value from elsewhere |
| Manual transcription | 4 | Retype/copy data between tools |

Total golden path friction = sum of all step scores.
- 0-3: Excellent
- 4-7: Good, minor optimization possible
- 8-12: Moderate friction, worth addressing
- 13+: High friction, structural change needed

### Session Pattern Assessment

| Pattern | Indicator | Optimization |
|---------|-----------|--------------|
| Glance (5-15s) | User checks one metric and leaves | Surface it immediately, no clicks |
| Scan (30-60s) | User reads several sections | Ordering matters, group by importance |
| Work session (2-5min) | User takes actions based on data | Reduce friction between read and act |
| Investigation (5-15min) | User digs into details | Progressive disclosure, breadcrumbs |

### Emotional Curve

Map emotion to journey stages:

| Emotion | Design Signal | Watch For |
|---------|--------------|-----------|
| Confidence | Clear status, no ambiguity | Vague states, missing data |
| Satisfaction | Task completed, clear confirmation | Missing feedback, dangling state |
| Frustration | Extra steps, broken flow, missing data | Multi-click paths, dead ends |
| Anxiety | Unclear consequences, missing undo | Destructive actions without confirmation |
| Trust | Accurate data, consistent behavior | Stale timestamps, inconsistent counts |

---

## Daily-Driver Checklist

Quick pass for tools used repeatedly by the same person:

- [ ] Most-used view is reachable in 0 clicks (tab persistence, deep link)
- [ ] Primary question answered within 2 seconds of page load
- [ ] No instructional text visible after 5th session (collapse or hide)
- [ ] State persists across sessions (selections, preferences, scroll position)
- [ ] Deep-linkable sections (URL hash or query param)
- [ ] Copy-to-clipboard for anything the user regularly transcribes elsewhere
- [ ] Stale data is visually distinct from fresh (timestamp, fading, banner)
- [ ] The most actionable item is visually prominent (not buried in a list)
- [ ] Keyboard shortcuts exist for the top 3 actions (expert users)
- [ ] Theme/density preferences are remembered

---

## Report Quality Checklist

Before submitting a design-journey review, verify:

- [ ] Aesthetic identity named (not "it looks nice" or "it looks bad")
- [ ] Color collisions explicitly called out with hex values or variable names
- [ ] Typography range stated (smallest to largest, in px)
- [ ] Density table includes viewport percentage estimates
- [ ] Golden path documented with step count and friction score
- [ ] "Preserve these" section exists (don't only criticize)
- [ ] Recommendations are actionable (not "improve the hierarchy")
- [ ] Priority levels assigned to every finding
