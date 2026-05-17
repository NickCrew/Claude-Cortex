# Sub-agent Dispatch

How the orchestrator delegates per-mode exploration to sub-agents. Designed for parallel execution, structured returns, and downstream verification.

## Agent type / model matrix

| Mode | Agent type | Model | Why |
|---|---|---|---|
| Information architecture | `Explore` | haiku | Module/package enumeration; mostly `find` + read excerpts |
| Data model | `Explore` | haiku | Schema/type/dataclass extraction; pattern-driven |
| Integrations | `Explore` | haiku | Import/export/API call enumeration; pattern-driven |
| UI surfaces | `Explore` | haiku | Route + component enumeration; pattern-driven |
| Data flow | `general-purpose` | sonnet | Cross-file tracing requires reasoning about what counts as data |
| Control flow | `general-purpose` | sonnet | Concurrency/async reasoning needs judgment |
| Failure modes | `general-purpose` | sonnet | Distinguishing real error paths from happy-path needs judgment |
| Interaction patterns | `general-purpose` | sonnet | Pattern detection from composition shape, ARIA, and state shape needs full-file reads and inference, not enumeration |

Justification for the split: `Explore` is read-only and optimized for fast pattern matching with excerpt reads. The four enumeration modes fit it well. The three reasoning modes need full-file reads and inference, which the `general-purpose` agent handles better.

## Dispatch rules

1. **One-shot, parallel.** Issue all sub-agent calls in a single message with multiple `Agent` tool blocks. Do not chain.
2. **No `team_name`.** Team-spawned agents lose their declared toolset (project memory: `feedback_team_spawn_tool_loss.md`). Always use bare `Agent` calls.
3. **One sub-agent per mode.** Do not dispatch multiple sub-agents per mode; that produces overlap that the verification phase has to reconcile, with no benefit.
4. **Pass scope explicitly.** Always include the target subtree in the prompt — `claude_ctx_py/intelligence/` is different from full repo.
5. **Return findings only, not diagrams.** Sub-agents enumerate; the orchestrator authors mermaid. Do not ask sub-agents to produce mermaid.

## Output contract (doc-led classification)

Sub-agents in doc-led mode classify each finding against the documentation spine. The orchestrator passes the relevant doc text in the prompt; the sub-agent reads the code and decides whether the code matches the doc, drifts from the doc, or does something the doc doesn't cover.

YAML block, one entry per finding:

```yaml
- callout_id: <PREFIX>-<N>           # e.g., I-1, D-12 — N starts at 1 per mode
  label: <short human label>
  citation: <repo-relative-path>:<line>
  evidence: <verbatim line content>
  classification: confirms | drift | gap | extends
  doc_ref: <path to spine doc, or null if no doc covers this>
  doc_claim: <quoted or paraphrased claim the code is being checked against; null if classification=gap>
  notes: <one-line explanation — required for drift, optional otherwise>
  relations:
    - to: <callout_id>
      kind: imports | calls | emits | listens | renders | persists | derives | catches | retries | etc.
      citation: <repo-relative-path>:<line>
  confidence: high | medium | synthesized
  synthesized_justification: <required if confidence=synthesized; names ≥2 contributing files>
```

### Classification semantics

- **confirms** — the code matches the doc claim. The cited line is evidence the doc is current. Default classification when a spine doc covers the territory.
- **drift** — the doc claims X, the code does Y. The `notes` field MUST quote both the doc claim and the code reality. Drift findings always make it into the report's drift section, never collapsed.
- **gap** — the code does something no doc covers. `doc_ref` and `doc_claim` are null. **Gaps drive the synthesis README's "Undocumented behaviors" section** — be deliberate about flagging them. A gap is something a future developer might break without knowing.
- **extends** — the code adds detail the doc doesn't claim but doesn't contradict either. Edge case; treat as a confirm unless the detail is materially important.

### Volume target

Doc-led runs should produce **fewer findings than enumeration runs** because confirmed-on-spine territory yields one finding per claim, not one per file. Optimize for:

- One confirms per substantive claim in the spine doc
- All real drift items
- All real gap items (deliberate inventory)

If a sub-agent returns 100+ findings for a doc that has 10 claims, it's over-enumerating. 30-50 findings per mode is the right zone for a well-documented codebase.

If a sub-agent returns prose without citations, treat the result as judgment-only — discard the specifics and re-dispatch.

## Prompt template (doc-led)

The prompt for each sub-agent has seven sections. The new section is **Doc spine** — paste the relevant excerpts from the spine docs (or the doc paths and let the sub-agent read them).

```
[Mode-specific intro from references/mode-<mode>.md]

# Scope
[Path or "the entire codebase rooted at <repo-path>"]

# Doc spine

The following in-tree docs are authoritative for this mode. The orchestrator has already read them; your job is to verify the code matches their claims, flag drift, and surface gaps.

[For each spine doc, paste either the full content (if short) or the
relevant section + path. Example:

  ## mainwebcode/docs/HANDLEBARS_CACHING.md (authoritative on cache layers)
  
  > Templates are compiled server-side by CF and cached in Couchbase
  > across **three layers**...
  > Layer 1 — file content cache, 60,000s TTL...
  > Layer 2 — compiled template, no expiry (persist bucket)...
  > Layer 3 — combined template list, 60,000s TTL...

If the mode has no spine doc, say:

  ## No spine doc for this mode.
  Treat every finding as classification=gap. The orchestrator will
  surface this in the synthesis README.
]

# Task
Classify code against the spine. For each authoritative claim in the spine doc(s):
- Find the canonical code citation (path:line) and emit a `confirms` finding.
- If the code disagrees with the claim, emit a `drift` finding with both citations.
- For territory the spine doesn't cover but that you find architecturally significant, emit a `gap` finding.

Do NOT re-document spine territory. The doc is the description; you are the verifier.

[Mode-specific signals to look for from references/mode-<mode>.md]

# Output contract
Return a YAML block using exactly this shape:

[Paste the output contract block from this file]

Notes:
- callout_id starts at <PREFIX>-1 and increments
- citation must be repo-relative path:line
- evidence is verbatim cited line content, no paraphrase
- Absence claims ("no X handler") — grep first; discard if X exists
- Drift findings MUST quote both the doc claim and the code reality in `notes`
- Gap findings MUST justify themselves: why is this worth flagging?
- Synthesized findings allowed but require ≥2 contributing files in justification

# Verification expectation
The orchestrator will mechanically verify every citation. Doc-led runs face the same accuracy bar as enumeration runs — drift and gap findings make it into the prominent (non-collapsed) parts of the final report, so accuracy here directly shapes what readers act on.

# Format reminder
Return only the YAML block. No prose preamble or postamble.
```

## Parallel call shape (orchestrator side)

```
[Single message containing 8 Agent tool blocks, in parallel]

Agent({subagent_type: "Explore", model: "haiku", description: "IA enum",
  prompt: <IA prompt with output contract>})
Agent({subagent_type: "Explore", model: "haiku", description: "Data model enum",
  prompt: <data-model prompt>})
Agent({subagent_type: "Explore", model: "haiku", description: "Integrations enum",
  prompt: <integrations prompt>})
Agent({subagent_type: "Explore", model: "haiku", description: "UI surfaces enum",
  prompt: <ui-surfaces prompt>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Data flow trace",
  prompt: <data-flow prompt>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Control flow trace",
  prompt: <control-flow prompt>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Failure modes scan",
  prompt: <failure-modes prompt>})
Agent({subagent_type: "general-purpose", model: "sonnet", description: "Interaction patterns",
  prompt: <interaction-patterns prompt>})
```

## After dispatch

The orchestrator collects all 8 returns, then runs the verification protocol (`references/verification-protocol.md`). Do not begin rendering until verification completes for all modes — partial rendering with un-verified findings is exactly the failure mode this skill exists to prevent.

## Re-dispatch

If a sub-agent returns malformed output (missing citations, prose-only, wrong shape), re-dispatch *that mode only* with a sharpened prompt. Do not re-dispatch all 8 — the verified ones are still valid. Limit re-dispatch to two attempts; if a third returns garbage, escalate to the user (the mode may be unsuitable for sub-agent enumeration in this codebase).
