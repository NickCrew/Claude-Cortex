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

## Output contract (every sub-agent must return this shape)

YAML block, one entry per finding:

```yaml
- callout_id: <PREFIX>-<N>      # e.g., I-1, D-12 — N starts at 1 per mode
  label: <short human label>
  citation: <repo-relative-path>:<line>
  evidence: <verbatim line content>
  relations:
    - to: <callout_id>           # must reference another finding from the same dispatch
      kind: imports | calls | emits | listens | renders | persists | derives | catches | retries | etc.
      citation: <repo-relative-path>:<line>
  confidence: high | medium | synthesized
  synthesized_justification: <required if confidence=synthesized; names ≥2 contributing files>
```

If a sub-agent returns prose without citations, treat the result as judgment-only — discard the specifics and re-dispatch with the format requirement reinforced. Do not "rescue" findings by inferring citations after the fact.

## Prompt template (skeleton)

The prompt for each sub-agent has six sections. Customize the bracketed parts; keep the structure.

```
[Mode-specific intro from references/mode-<mode>.md]

# Scope
[Path or "the entire codebase rooted at <repo-path>"]

# Task
Enumerate findings for the <MODE NAME> view of this scope.

[Mode-specific signals to look for from references/mode-<mode>.md]

# Output contract
Return a YAML block of findings using exactly this shape:

[Paste the output contract block from this file]

Notes:
- callout_id starts at <PREFIX>-1 and increments
- citation must be repo-relative path:line
- evidence is the verbatim content of the cited line, no paraphrase
- For absence claims ("no X", "missing Y") — grep first; do not assert absence without checking
- Synthesized concepts allowed but justification required (cite ≥2 contributing files in the justification)

# Verification expectation
The orchestrator will mechanically verify every citation before any node lands in a diagram. Findings whose citations don't resolve will be discarded. Optimize for accuracy over volume — 20 verified findings beat 50 with half-fabricated citations.

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
