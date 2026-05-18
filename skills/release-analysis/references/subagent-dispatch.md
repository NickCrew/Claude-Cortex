# Sub-agent Dispatch

How the orchestrator delegates per-mode exploration to sub-agents. Designed for parallel execution, structured returns, and downstream verification.

## Agent type / model matrix

| Mode | Agent type | Model | Why |
|---|---|---|---|
| Promotion path | `general-purpose` | sonnet | Crosses CI, registry, and platform boundaries; needs reasoning, not enumeration |
| Environment matrix | `Explore` | haiku | Topology enumeration; mostly listing manifests/profiles. Switches to general-purpose if eve-mcp must drive the discovery (haiku can't reliably orchestrate MCP calls) |
| Configuration provenance | `general-purpose` | sonnet | Override-order resolution requires reading multiple sources and reasoning about precedence |
| Recovery & rollback | `general-purpose` | sonnet | Recovery procedures are inherently multi-step; gap detection requires judgment |

Justification: release-analysis modes lean reasoning-heavy more than enumeration-heavy. Three of four modes use `general-purpose:sonnet`. Environment matrix is the exception when scope is purely topological — but escalates to sonnet if eve-mcp orchestration is required.

## Dispatch rules

1. **One-shot, parallel.** Issue all four sub-agent calls in a single message with multiple `Agent` tool blocks. Do not chain.
2. **No `team_name`.** Team-spawned agents lose their declared toolset. Always use bare `Agent` calls.
3. **One sub-agent per mode.** Do not split modes across sub-agents.
4. **Pass scope explicitly.** Always include the target subtree in the prompt — `~/source/dev-stack/` is different from `~/source/{dev-stack,mainwebcode}`.
5. **Pass scope shape.** Each sub-agent gets `scope_shape: compose-only | kube-only | hybrid` so it knows which signal sets to apply.
6. **Pass ingested findings.** When Phase 0 ingested arch-analysis findings, pass them by callout ID with one-line summaries. Sub-agents reference these IDs rather than re-deriving the underlying facts.
7. **Pass eve-mcp availability.** Sub-agents only attempt eve-mcp queries when told the server is configured. They do not probe for availability themselves.
8. **Return findings only, not diagrams.** Sub-agents enumerate; the orchestrator authors mermaid.

## Output contract (every sub-agent must return this shape)

YAML block, one entry per finding:

```yaml
- callout_id: <PREFIX>-<N>      # R-1, E-1, K-1, V-1 — N starts at 1 per mode
  label: <short human label>
  citation: <repo-relative-path>:<line> | eve-mcp:<tool>:<query>
  evidence: <verbatim line content or excerpt of query result>
  relations:
    - to: <callout_id>           # may reference another finding from same dispatch OR an ingested arch-analysis ID (I-, C-, F-, X-)
      kind: builds | publishes | pulls | promotes | depends-on | overrides | resolves-from | restarts | rolls-back | etc.
      citation: <path>:<line> | eve-mcp:<tool>:<query>
  confidence: high | medium | synthesized
  synthesized_justification: <required if synthesized; names ≥2 contributing files or queries>
```

If a sub-agent returns prose without citations, treat the result as judgment-only — discard the specifics and re-dispatch with the format requirement reinforced.

## Prompt template (skeleton)

The prompt for each sub-agent has eight sections.

```
[Mode-specific intro from references/mode-<mode>.md]

# Scope
[Path or paths. For multi-repo systems, list all relevant roots.]

# Scope shape
[compose-only | kube-only | driver-only | compose+kube | driver+compose | driver+kube | all-three]
[For driver-shaped targets: the unit of analysis is the release operations the tool performs on
 other systems, not how the tool itself deploys. See SKILL.md "Driver-shaped reframe" and the
 mode reference's "Driver-shaped (orchestrator)" subsection for signal-set adjustments.]

# eve-mcp availability
[available | unavailable]
[If available, you may use the following read-only tools for verification and discovery:
  - Topology: ShowChannels, ShowEnvironments, ShowClusters, ShowNamespaces, ShowManifests, GetChannel
  - Apps & images: ShowApplications, GetApplication, GetApplicationVersions, ShowImages
  - Manifests & plans: GetManifest, GetManifestPlan
  - Deployments: ShowDeployments, GetDeployment, ShowDeploymentRequests, GetDeploymentRequest
  - Versioning: ShowReleaseCandidates, GetReleaseCandidate
  - Audit: GetAuditRecords
  - Crons: ShowDeploymentCrons, GetDeploymentCron, ShowDeploymentCronJobs
  - Permissions: GetPermissions
 **You may not call any of these eve-mcp tools, regardless of whether the project's CLAUDE.md
 also forbids them**: Deploy, RunManifest, RestartManifest, SetManifestVersion, SetNamespaceVersion,
 UnpinManifestVersion, UnpinNamespaceVersion, PatchManifestMetadata, UpdateManifestMetadata,
 UpdateManifestDefinitions. These are release levers — they change live state. This skill is read-only
 analysis. The constraint comes from the skill itself; if the project's CLAUDE.md happens to agree,
 cite the skill rule (this file), not the project's rule. The skill's rule applies in projects without
 a CLAUDE.md saying the same thing. Action tools may be referenced as mechanism citations in
 recovery-rollback findings — naming the lever and what it does — but the lever is never invoked.]

# Ingested findings from prior architectural-analysis
[List of [I-N], [C-N], [F-N], [X-N] callouts with one-line summaries.
Reference these by ID. Do not re-derive their underlying facts.
If your finding extends one of them, cite both.
If empty: no prior arch-analysis report was ingested.

Boundary-marker references: when a large block of arch-analysis callouts represents a single
conceptual boundary (e.g., "all service-internal failure modes manifest as Done Unhealthy"),
reference them collectively as [F-1]…[F-40] in a single relation rather than enumerating each one.
This is a legitimate ingest pattern when the prior scope is upstream/downstream of this scope and
the callouts function as a single boundary line rather than as individually-relevant findings.
The synthesis README's cross-mode index lists boundary-markers under their own "(arch-analysis: <mode>)"
entry with the range and a one-line label.]

# Task
Enumerate findings for the <MODE NAME> view of this scope.

[Mode-specific signals to look for from references/mode-<mode>.md]

# Output contract
Return a YAML block of findings using exactly this shape:

[Paste the output contract block from this file]

Notes:
- callout_id starts at <PREFIX>-1 and increments
- citation is either repo-relative path:line OR eve-mcp:<tool>:<query>
- evidence is the verbatim content of the cited line or query result excerpt
- For absence claims — verify first (grep for file-side, eve-mcp query for cloud-side)
- Synthesized concepts allowed but justification required (≥2 contributing sources)
- Override-order claims must be backed by reading the actual resolution mechanism, not inferred from filename

# Verification expectation
The orchestrator will mechanically verify every citation before any node lands in a diagram. Findings whose citations don't resolve will be discarded. Optimize for accuracy over volume.

# Format reminder
Return only the YAML block. No prose preamble or postamble.
```

## Parallel call shape (orchestrator side)

```
[Single message containing 4 Agent tool blocks, in parallel]

Agent({subagent_type: "general-purpose", model: "sonnet", description: "Promotion path",
  prompt: <promotion-path prompt>})
Agent({subagent_type: "Explore", model: "haiku", description: "Env matrix enum",
  prompt: <env-matrix prompt — or sonnet/general-purpose if eve-mcp orchestration heavy>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Config provenance",
  prompt: <config-provenance prompt>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Recovery & rollback",
  prompt: <recovery-rollback prompt>})
```

## After dispatch

The orchestrator collects all 4 returns, then runs the verification protocol (`references/verification-protocol.md`). Do not begin rendering until verification completes for all modes.

## Re-dispatch

If a sub-agent returns malformed output, re-dispatch *that mode only*. Limit re-dispatch to two attempts; if a third returns garbage, escalate to the user.

## Sub-agents and eve-mcp permissions

If eve-mcp is configured but the sub-agent is unable to call it (permission prompt or unavailable in subagent context), the sub-agent should:
1. Note the failure in its return.
2. Fall back to repo-side citations only.
3. Mark all cloud-side findings as `confidence: medium` pending orchestrator verification.

The orchestrator can then run the cloud-side eve-mcp queries from its own context to upgrade or discard findings during the verification pass.
