---
name: knowledge-stack
description: "Use this skill whenever working inside any of Nick's repos (under ~/Developer/) or whenever a conversation touches Nick's durable cross-cutting work — Atlas Crew product strategy/brand/planning, the Unanet job, job search, interviews, tax amendment, foreclosure/tenant situation, strategic positioning. Maps Nick's three Basic Memory projects (products, work, main) and the per-repo dev trackers, and says which layer owns which kind of question. Consult before reasoning from stored memory summaries about repo architecture, product decisions, active priorities, or ongoing personal/career state — stored memory is lossy; the trackers and the Basic Memory projects are the real artifacts and should be consulted first."
keywords:
  - knowledge stack
  - durable knowledge
  - basic memory
  - products project
  - work project
  - unanet
  - atlas crew
  - backlog docs
  - repo architecture
  - active priorities
---

# Knowledge Stack

Nick's durable knowledge lives in two kinds of place: **per-repo trackers** (code-adjacent) and **three Basic Memory projects** (everything else). Stored memory summaries are lossy snapshots of these; the artifacts below are the real truth. Consult them before reasoning.

## The Layers

**Per-repo dev work** → the repo's own tracker, not Basic Memory.
- Architecture, implementation plans, active tasks, roadmap-of-code.
- Tracker depends on the repo: **Cortex** uses **backlog.md** (`backlog doc list`, `backlog task list`; see the `backlog-md` skill). The **atlas-crew repos** — Facet plus the security repos Apparatus, Chimera, Crucible, Synapse, Bridge — use **GitHub Issues + Projects** (`gh issue`, `gh project`; see the `atlas-crew-tasks` skill). Don't assume backlog.md everywhere — check the repo.

**Atlas Crew product work** → the `products` Basic Memory project (`~/Obsidian/Product_Management`).
- Product strategy, brand, positioning, pricing, GTM, planning, specs, PM docs — the *product* layer, not the *code* layer.
- Organized by Atlas Crew family: **Security** (Synapse, Chimera, Crucible, Bridge, Apparatus), **Career Intel** (Facet), **Dev Tools** (Cortex and utilities), **Writing** (Hard Stuff blog). The root `Product Management Vault Home.md` is the map.
- `_Archive/` holds frozen history (old job-search material, captured sessions). Treat as read-only context, not current state.

**The Unanet job** → the `work` Basic Memory project (`~/Obsidian/Work`, under `unanet/`).
- Personal working-memory for Nick's Senior Platform Release Engineer role: `journal/` (append-only daily firehose), `systems/`, `glossary`, `open-questions`, `observations-about-me`, etc. Its `README` defines the capture workflow.
- **This project syncs to Nick's work laptop.** The bar for what goes here is "fine if a coworker glanced over my shoulder." Candid people-notes, political tripwires, and customer/contract/proprietary specifics stay in segregated local-only files *outside* this vault — never write them into the synced `work` project. When in doubt, append to today's journal and route later; when sensitive, keep it out.

**Everything else cross-cutting** → the `main` Basic Memory project (`~/Obsidian/Default`), the **default**.
- Personal and career state that isn't an Atlas Crew product and isn't the Unanet job: job search, interviews, tax amendment, foreclosure/tenant situation, strategic positioning, misc research.
- This is the catch-all. If a topic doesn't clearly belong to `products` or `work`, it lands here.

**Ephemeral conversation context** → this chat. Promote to the right layer when worth keeping.

## Picking the project

| Topic | Project |
|---|---|
| Atlas Crew product strategy / brand / planning / Hard Stuff | `products` |
| Unanet job (people, systems, journal, glossary) | `work` (syncs to work laptop) |
| Job search, interviews, taxes, housing, personal/career | `main` (default) |
| A repo's code architecture, tasks, implementation plans | the repo's tracker (backlog.md / GitHub Issues) |

## Operational Rules

1. **Address the right project explicitly.** Basic Memory MCP tools and `basic-memory tool` take a `project` (e.g. `search-notes --project products`). `main` is the default; pass `--project work`/`--project products` for the others. Searching the wrong project returns nothing and reads as "no such note."
2. **Before reasoning about a specific repo**, list its tracker first (`backlog doc list` for Cortex, `gh issue list` for atlas-crew repos) and pull the relevant item before concluding from stored memory.
3. **Before reasoning about cross-cutting work**, search the matching Basic Memory project (search, then read the note) before reasoning from stored memory.
4. **When a chat surfaces something durable**, propose writing it to the right layer — and use the Basic Memory skills to do it well: `memory-notes` (frontmatter/observations/relations), `memory-ingest` (unstructured input → entities), `memory-research` (research a subject → entity), `memory-lifecycle` (archive/status moves), `memory-schema`/`memory-metadata-search` (structured note types), `memory-defrag`/`memory-reflect` (periodic upkeep).
5. **Don't duplicate content across layers.** If something could plausibly live in two places (e.g. a product decision that's also a code task), ask Nick which layer owns it.

## Failure Modes to Avoid

- Reasoning from stored memory summaries when fresher truth exists in a tracker or a Basic Memory project — produces stale or wrong answers.
- **Searching one Basic Memory project and concluding the knowledge doesn't exist** — it's almost certainly in one of the other two. There are three projects now; check the one that owns the topic.
- **Writing sensitive Unanet material into the synced `work` project** — it reaches the work laptop. Keep candid/proprietary content in the segregated local-only files.
- Putting Atlas Crew product strategy into a repo tracker, or code-task detail into the `products` project — knowledge drift across layers that compounds.
- Treating Obsidian as required — Nick doesn't run the Electron app. The projects are plain markdown; use the `basic-memory` CLI/MCP or any editor.
- Enumerating "Nick's repos" or which tracker a repo uses from memory and getting it wrong — `ls ~/Developer/` and check the repo (backlog.md vs GitHub Issues).
