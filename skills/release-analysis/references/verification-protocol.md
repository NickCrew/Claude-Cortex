# Verification Protocol

The orchestrator's mechanical pass over candidate findings returned by sub-agents. This is what enforces the citation policy. Sub-agents fabricate at predictable rates; verification is the structural safeguard.

## Inputs

A list of candidate findings from one or more sub-agents, each shaped per `subagent-dispatch.md`.

## Pass 1 — Symbol / query resolution

For each finding's `citation`:

### File citations (`path:line`)

1. **Codanna first** if `.codanna/` exists in the target. Use `mcp__codanna_*` tools to confirm the symbol is defined at the cited path.
2. **Grep fallback** if codanna is unavailable. `grep -n "<symbol-or-anchor>" <path>`.
3. **Read the line.** Use `Read` with `offset=<line-1>` and a small `limit` to fetch the cited line plus context.
4. **Match evidence to line.** The `evidence` string must appear verbatim on (or starting at) the cited line. Trim whitespace; match on substring.

### Eve-mcp citations (`eve-mcp:<tool>:<query>`)

1. **Run the query.** Issue the cited eve-mcp tool with the cited query parameters.
2. **Match evidence to result.** The `evidence` string must appear in the query response.
3. **If eve-mcp is unavailable**, the citation is treated as **unverified** — the finding is downgraded to medium confidence and a fallback file citation is required, or the finding is discarded.

If any of these fail, the finding is **discarded** and logged.

## Pass 2 — Absence claims

A finding whose label or evidence asserts absence (`"no recovery procedure"`, `"no healthcheck"`, `"missing rollback path"`, `"no deploy cron"`) is checked separately:

### File-side absence

1. Construct a grep target for the asserted-missing symbol/directive.
2. Grep across the *target subtree*, not just the file the sub-agent looked at.
3. If the symbol turns up, the finding is discarded.

### Cloud-side absence (eve-mcp available)

1. Query the relevant eve-mcp tool. For "no deploy cron" → `eve-mcp:ShowDeploymentCrons` for the scope.
2. If the result is non-empty, the finding is discarded.

### Cloud-side absence (eve-mcp unavailable)

The finding is downgraded to medium confidence and the verification log notes the fallback. Do not assert cloud-side absence with high confidence based on repo-side absence alone — the repo may be incomplete.

## Pass 3 — Configuration override-order claims (release-specific)

A finding that asserts a configuration override order (e.g., "`.env.local` overrides `.env`", "stage manifest metadata overrides base manifest") must be verified by reading the actual resolution mechanism.

For compose:
1. Read the entrypoint (`up.sh`, `Makefile`, `justfile`) that invokes `docker compose`.
2. Confirm the file flag order matches the asserted override order. Compose merge order is deterministic from the `-f` flag sequence.
3. If `.env` files are involved, confirm the `--env-file` flag (or default `.env`) matches the asserted source.

For Eve manifests:
1. Query `eve-mcp:GetManifest:name=<name>` for the asserted-overriding env.
2. Compare to `eve-mcp:GetManifest:name=<name>` for the asserted-base env.
3. The override order is the platform's documented behavior, not the order of fields in YAML. If the resolution is ambiguous, escalate.

Findings that fail this check are discarded as inferred-from-filename, not verified.

## Pass 4 — Synthesized validation

For each finding marked `confidence: synthesized`:

1. Confirm a `synthesized_justification` field exists and names ≥2 contributing files.
2. Cite each contributing file at a representative line.
3. Track synthesized count per mode.

After all findings are processed:

```
synthesized_share = synthesized_count / (synthesized_count + cited_count)
```

Cap: 0.20 for all release-analysis modes. If exceeded, **Promote / Drop / Escalate** per `citation-protocol.md`.

## Pass 5 — Edge consistency

For each verified node, walk its `relations`. Each relation's `to` must be the callout ID of another verified node — including ingested arch-analysis callouts (`I-`, `C-`, `F-`, `X-`) when the prior report is in scope. Dangling edges are dropped, and the drop is logged.

## Pass 6 — Cross-skill callout reuse

Verify that ingested arch-analysis callouts referenced in this run still resolve:

1. For each `[I-N]`, `[C-N]`, `[F-N]`, `[X-N]` reference, look up the callout in the prior report's callout table.
2. If the prior report is older than 30 days, re-verify the underlying citation (the file may have moved or changed). Use the same Pass 1 mechanism.
3. If the callout no longer resolves, surface it: either the prior report is stale, or this run depended on a finding that no longer holds. Either is a signal to the user.

## Outputs

Two artifacts feed the rendering phase:

1. **Verified findings** — survivors of all six passes.
2. **Discard log** — every dropped finding with reason. Goes verbatim into the report's "Verification log" section.

## Tooling preference

When checking citations, prefer in this order:

1. **eve-mcp** — for cloud-side topology, manifests, channels, audit records.
2. **codanna MCP** — `mcp__codanna_codebase-intelligence__*` for symbol-level questions when `.codanna/` exists.
3. **`Read`** — for fetching specific line ranges.
4. **`grep` via Bash** — for absence checks and bulk lookups.

Do not delegate verification to a sub-agent. Verification is the orchestrator's job.

## Performance

Verification is the bottleneck. Budget per ~30 findings × 4 modes:

- Symbol resolution: ~200ms with codanna, ~500ms with grep.
- eve-mcp query: ~1s per call (network).
- Total: 1–3 minutes for a full release-analysis run with mixed file + eve-mcp citations.

Acceptable. Skipping verification to save time is not.

## When verification cannot run

If neither codanna, grep, nor eve-mcp can verify a substantial fraction of the findings (e.g., the target is a remote codebase you can't read, and eve-mcp is also unavailable), this skill cannot produce trustworthy diagrams. Tell the user:

> Release analysis with strict citations requires either local read access to the target, or eve-mcp access for cloud-side topology, or both. Verification cannot run without at least one. Either grant access or rescope the analysis.

Do not produce diagrams with un-verified citations.
