---
name: knowledge-stack
description: "Use this skill whenever working inside any of Nick's repos (Atlas Crew, Inferno Lab, or any folder under ~/Developer/) or whenever a conversation touches Nick's cross-cutting personal or career work — job search, interviews, tax amendment, foreclosure/tenant situation, Hard Stuff drafts, brand or design work, strategic positioning. Describes where Nick's durable knowledge lives and which layer to consult for which kind of question. Trigger before reasoning from stored memory summaries about repo architecture, product decisions, active priorities, or ongoing personal/career state. Stored memory is lossy; the backlog docs and the Basic Memory vault are the real artifacts and should be consulted first."
---

# Knowledge Stack

Nick's durable knowledge lives in two layers. Stored memory summaries are lossy; these are the real artifacts. Consult them before reasoning.

## The Split

**Per-repo dev work** → `backlog docs` and `backlog tasks` inside each repo.
- Architecture, product strategy, implementation plans, active priorities, roadmap notes.
- Consistent pattern across Nick's repos under `~/Developer/`.
- For CLI mechanics, see the `backlog-md` skill.

**Cross-cutting personal and career** → Basic Memory vault (via the `basic-memory` MCP).
- Job search pipeline, interview prep state, tax amendment, foreclosure/tenant situation, Hard Stuff drafts, brand and design work, strategic positioning.
- Obsidian is an optional UI, not required. The vault is plain markdown; any editor works.

**Ephemeral conversation context** → this chat. Promote to the right layer when worth keeping.

## Operational Rules

1. **Before reasoning about a specific repo**, run `backlog doc list` in that repo. Pull relevant docs with `backlog doc view <id>` before forming conclusions from stored memory.
2. **Before reasoning about cross-cutting work**, search Basic Memory (`search_notes`, then `read_note`) before reasoning from stored memory.
3. **When a chat surfaces something durable**, propose writing it to the right layer. Don't silently drop context.
4. **Don't duplicate content across layers.** If something could plausibly live in both, ask Nick which layer owns it.

## Failure Modes to Avoid

- Reasoning from stored memory summaries when fresher truth exists in backlog docs or the vault — produces stale or wrong answers.
- Writing to Basic Memory what belongs in a repo's backlog docs, or vice versa — produces knowledge drift across layers that compounds over time.
- Treating Obsidian as required — Nick doesn't want the Electron app running. The vault is markdown files; use whatever editor or the MCP directly.
- Enumerating "Nick's repos" from memory and getting it wrong — just `ls ~/Developer/` or check the current working directory.
