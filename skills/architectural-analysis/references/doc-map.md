# Doc Map (Phase 2 Output)

The doc map is the spine of the report. Phase 2 produces it by reading every in-tree doc and deciding which subsystem each one is authoritative on.

## Authoring rules

- **Read every doc** in `docs-inventory.txt`. The orchestrator does this directly; do not delegate.
- **One row per topic, not per doc.** A multi-doc topic (e.g., cache migration with three READMEs) gets one row pointing at all three.
- **Mode column** lists the mode reports that should lead with this doc. A doc may appear in multiple modes if it's authoritative on more than one.
- **Stale marker** (`*(stale)*`) when the doc describes a topology, stack, or convention that the codebase no longer matches. Mark and explain in the synthesis README's drift section. Do NOT treat a stale doc as authoritative.

## Template

```markdown
# Doc map — <YYYY-MM-DD>

This is the documentation spine the rest of the report builds on. Each row names a topic, the canonical doc(s) for that topic, and which mode reports lead with it. Stale docs are marked `*(stale)*` and do not anchor a mode.

| Topic | Doc(s) | Modes | Status |
|-------|--------|-------|--------|
| <topic-1> | <path/to/doc.md> | data-flow, control-flow | authoritative |
| <topic-2> | <path/to/a.md>, <path/to/b.md> | data-model | authoritative |
| <topic-3> | <path/to/legacy.md> | information | *(stale)* |

## Coverage by mode

- **information** — <list spine docs for this mode, or "no spine doc; greenfield">
- **data-model** — …
- **data-flow** — …
- **integrations** — …
- **ui-surfaces** — …
- **interaction-patterns** — …
- **control-flow** — …
- **failure-modes** — …

## Notes

<Anything worth surfacing that doesn't fit a row: docs that nearly cover a topic but stop short, docs that overlap each other, etc.>
```

## What constitutes a "topic"

A topic is the unit at which a sub-agent treats the doc as authoritative. Examples:

- "The 3-layer Handlebars cache" — one topic, one doc.
- "KV-store migration mechanics" — one topic, three docs (overview + two READMEs). Group them.
- "Container shutdown signal flow" — one topic, two docs (GRACEFUL + QUICK_REFERENCE).
- "Okta admin auth handshake" — one topic, one doc. Treat as authoritative for the *admin-side* auth flow only; the JWT cookie path is a separate (un-spined) topic.

If a sub-agent's mode covers territory across two topics, the mode's report leads with both spine references in its Summary.

## What does NOT belong in the map

- **Operational/runbook content** (e.g., `cosential-proxy/README.md` describing local dev setup) is not a spine for the architecture report. List it in the inventory; do not promote.
- **Code-only inventories** (e.g., a `CHANGELOG.md` listing every release) are reference material, not architecture spine.
- **Aspirational docs** (e.g., a "future architecture" plan that doesn't reflect current code) — note in the doc-map "Notes" section, do not anchor a mode.
