---
name: atlas-crew-tasks
description: "Use when filing, updating, sequencing, or querying tasks in any atlas-crew repo (Facet + the Atlas Crew Security repos: Apparatus, Chimera, Crucible, Synapse, Bridge). These repos track work in GitHub Issues on Projects v2 boards, NOT backlog.md. Covers the two boards, the Type/Area/Status field model, cross-repo Initiative grouping, gh seq execution ordering, and the non-obvious gh/GraphQL mechanics for setting issue types and project fields. Trigger on: file an issue, create a task, set priority/type/area/status, add to board, what should I work on next, execution order, sequencing, blocked-by, milestone, where does this task go."
keywords:
  - github projects
  - issue tracking
  - gh project
  - gh seq
  - issue type
  - sequencing
  - blocked-by
  - atlas-crew board
  - file a task
---

# Atlas Crew Task Tracking

Work for these repos lives in **GitHub Issues** on **Projects v2** boards, not
backlog.md. (A repo's `backlog/` directory is a frozen archive of completed
pre-migration work — read-only.)

## The two boards

| Board | Repos | URL |
| --- | --- | --- |
| **#8 Atlas Crew Security** (shared) | Apparatus, Chimera, Crucible, Synapse, Bridge | `https://github.com/orgs/atlas-crew/projects/8` |
| **#9 Facet** (standalone) | Facet | `https://github.com/orgs/atlas-crew/projects/9` |

Both are **org-owned** by `atlas-crew`. Always pass `--owner atlas-crew`.

## Classification model (three orthogonal axes)

Keep these separate — do not encode type or area as a label.

- **Type** → GitHub **Issue Type** (org-owned, shared by every repo):
  `Feature`, `Bug`, `Task`, `Chore` (refactor/tech-debt/maintenance),
  `Spike` (time-boxed investigation).
- **Area** → an **Area** single-select project field. *Facet #9 only* so far
  (Identity, Pipeline, Prep, Letters, Research, Build/Resume, Debrief,
  AI/Proxy, UI/Design System, Persistence, Testing/Infra, Docs, Cross-cutting).
  Board #8 has no Area field yet.
- **Concern** → **labels**: `accessibility`, `security`, `ux`, `cross-cutting`,
  `testing`, `documentation`, `playwright`, plus GitHub/dependabot conventions.

**Cross-repo grouping** is the **Initiative** single-select on board #8 (e.g.
"Platform Hardening", "Vuln Content") — use it for milestones that span ACS
repos. Within a single repo, use native GitHub **milestones**.

**Status** differs per board:
- #9 Facet: `Backlog → Todo → In Progress → Blocked → Done`.
- #8 ACS: `Todo → In Progress → Done` (not yet refined).

## Filing a task

```sh
# 1. create the issue (type can be set at creation via REST; see gotcha below)
gh issue create --repo atlas-crew/Facet --title "..." --body "..." --label ux

# 2. add it to the board
gh project item-add 9 --owner atlas-crew --url <issue-url>

# 3. set Type (see gotcha), then set project fields (Priority/Area/Status)
```

## Sequencing — what to work on next

Execution order is **not** a board field. It is derived from native issue
dependencies (`blocked-by`) + sub-issues, reconstructed into waves by `gh seq`:

```sh
gh seq --repo atlas-crew/Facet --order-by Priority      # single repo
gh seq --project 8 --owner atlas-crew --order-by Priority # whole ACS board
```

The GitHub UI cannot render topological order; `gh seq` is the canonical
"what can I start now" view. Set Status to **Blocked** on issues waiting in the
dependency graph (Facet #9).

## Mechanical gotchas (the parts that waste time if rediscovered)

**Setting an Issue Type — `gh issue edit` has NO `--type` flag.** Use the REST
issues endpoint, which takes the type name directly:
```sh
gh api -X PATCH /repos/atlas-crew/Facet/issues/13 -f type=Feature
```

**Creating a new org Issue Type needs the `admin:org` scope:**
```sh
gh auth refresh -h github.com -s admin:org
gh api -X POST /orgs/atlas-crew/issue-types -f name=Chore -F is_enabled=true \
  -f color=gray -f description="..."
```

**Setting a project single-select field (Priority/Area/Status) needs three
IDs** — project, field, option — and the item's id. Look them up; never
hardcode (they drift):
```sh
# field + option ids:
gh project field-list 9 --owner atlas-crew --format json
# item ids (maps issue number -> item id):
gh project item-list 9 --owner atlas-crew --format json
# then:
gh api graphql -f query='mutation{updateProjectV2ItemFieldValue(input:{
  projectId:"<PID>", itemId:"<ITEM>", fieldId:"<FIELD>",
  value:{singleSelectOptionId:"<OPTION>"}}){projectV2Item{id}}}'
```

**Editing single-select options (e.g. adding a Status value) — preserve
existing option IDs.** `ProjectV2SingleSelectFieldOptionInput` accepts `id`;
re-send existing options *with their id* and append new ones, or you detach
every item's current assignment.

**Views cannot be created via API** — there is no `createProjectV2View`
mutation. View setup is manual in the board UI.

## Reference

Each repo's board conventions and view configs:
`docs/development/project-board.md` (Facet has one; mirror it per repo as the
ACS board gains fields).
