# Citation Protocol

The load-bearing rule of this skill. A diagram is a set of falsifiable claims; a citation is what makes a claim falsifiable. Without strict citation, the skill produces confident-looking release fiction.

## Core rules

1. **Every node carries a callout ID and a citation.**
   - Format A — file citation: `path/to/file.ext:LINE`. Use repo-relative paths consistently.
   - Format B — eve-mcp citation: `eve-mcp:<tool>:<query-summary>`. Examples:
     - `eve-mcp:GetManifest:name=crm-services`
     - `eve-mcp:ShowEnvironments:channel=prod`
     - `eve-mcp:ShowDeploymentCrons:namespace=crm-services-prod`
   - The line cited (Format A) is the line where the symbol or directive is *defined*. Not where it is used.
   - The query (Format B) is the call that returns the cited fact. The `<query-summary>` is a short, deterministic identifier — running the same query should return the same answer.

2. **Every edge carries a citation.**
   - The line where the relationship is established: a `depends_on:` directive, an `image:` reference, a manifest metadata patch, an Eve audit record showing a promotion event.
   - Edges between cloud topology nodes preferentially cite eve-mcp queries.

3. **Absence claims grep first (and query first).**
   - Findings of the shape "no recovery procedure documented", "no healthcheck", "no rollback for X" must verify before recording.
   - For file-side absence: grep across the target subtree.
   - For cloud-side absence: query eve-mcp. "No deploy cron exists" is verified by `eve-mcp:ShowDeploymentCrons` returning empty for the relevant scope, not by absence in the repo.

4. **Quoted code or query-result is exact.**
   - Evidence strings are verbatim. Paraphrase counts as fabrication.

## eve-mcp citation rules

The `eve-mcp:<tool>:<query>` format is treated as a first-class citation when eve-mcp is available. Specific rules:

- **Query summary must be deterministic.** `eve-mcp:GetManifest:name=crm-services` is good. `eve-mcp:GetManifest:the production manifest` is not.
- **Same query, same answer.** A reader should be able to re-run the query and get a result that confirms the finding. If the query depends on time-of-day state (audit records, current pinned versions), include a timestamp in the query summary or capture the result inline in the report.
- **Eve queries do not replace file citations when both apply.** A manifest's *current pinned version* is an eve-mcp fact; the manifest's *YAML structure* is a file fact. Cite both when both are relevant.
- **Eve-mcp citations are not allowed for synthesized concepts.** Synthesized concepts span multiple files; the eve-mcp interface is per-resource. If you find yourself wanting to synthesize via eve-mcp, the finding probably belongs in a different mode.

## Synthesized concepts

Some release truths don't live in a single file or query. Examples:

- **The promotion policy** — embodied across CI publish jobs, channel definitions, and manual evebot conventions. No single line declares it.
- **The recovery convention** — implicit in how multiple services have similar `restart:` policies and similar healthcheck patterns. Not stated anywhere.
- **The configuration override layer ordering** — emerges from `up.sh` invocations, compose merge semantics, and Eve manifest metadata resolution.

These are real and worth diagramming. They are also the primary vector for fabrication. The escape hatch:

### Synthesized-node requirements

- Marked in mermaid with `classDef synthesized stroke-dasharray:5,stroke:#888`.
- Listed in a dedicated **Synthesized concepts** section of the report with a written justification.
- Justification names the *contributing files* (cited individually) and explains why no single line owns the concept.
- Cap: **≤20% of nodes per mode.** Release-analysis modes are less emergent than interaction-patterns, so no raised cap applies.

If a mode exceeds its cap:
- **Promote**: pick the most-canonical contributing file for each weakest synthesized node and re-classify as cited.
- **Drop**: remove weakest synthesized nodes until under cap.
- **Escalate**: tell the user the synthesized share is high. For release analysis, high synthesized share usually means the release process is undocumented — sometimes that's the finding.

Edges into or out of a synthesized node still need citations on the *cited* end.

## Citation format inside reports

```markdown
| ID | Label | Citation | Confidence |
|----|-------|----------|------------|
| R-1 | CI publish to JFrog | .gitlab-ci.yml:84 | high |
| R-2 | Manifest pinned version | eve-mcp:GetManifest:name=crm-services | high |
| R-3 | Promotion policy | — | synthesized |
```

In narrative prose, refer to a callout by ID alone (`[R-1]`). The callout table is the source of truth.

## What is NOT a citation

- A path with no line number (`compose/compose.jobs.yml`) — too vague.
- A line range (`up.sh:1-50`) — pick the canonical line.
- A search query as a stand-in (`grep depends_on compose/`) — that's how to find the citation, not the citation.
- An eve-mcp tool name with no query (`eve-mcp:GetManifest`) — the query is mandatory.
- A vague query summary (`eve-mcp:GetManifest:the prod one`) — must be deterministic.

## Verification log section

Every per-mode `report.md` includes a **Verification log** section listing:

- Findings discarded as fabricated.
- Absence claims rejected (with grep or eve-mcp evidence the asserted-missing thing exists).
- Synthesized cap pressure (if approached).
- Citations the orchestrator could not verify and why.
- **Release-specific**: any cloud-side claims that fell back to repo-side citations because eve-mcp was unavailable. Note the fallback explicitly — it changes the trust level of the claim.

A clean verification log is suspicious. A real run nearly always discards something.
