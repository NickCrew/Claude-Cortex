# Synthesis Workflow Reference

Detailed techniques for each phase of knowledge synthesis.

## Pattern Recognition Across Interactions

### Signal Detection

Look for these pattern types across agent interactions and outcomes:

| Pattern Type | What to look for | Example |
|-------------|------------------|---------|
| **Success pattern** | Repeated approaches that lead to good outcomes | "Agents that read tests before modifying code produce fewer regressions" |
| **Failure mode** | Recurring mistakes or breakdowns | "API calls without retry logic fail silently in 15% of runs" |
| **Decision heuristic** | Rules of thumb that agents converge on | "When file count exceeds 20, switch from sequential to parallel processing" |
| **Workflow shortcut** | Steps that can be safely skipped | "Lint checks redundant when using pre-commit hooks" |
| **Anti-pattern** | Approaches that seem right but produce bad outcomes | "Caching database queries without TTL leads to stale data bugs" |

### Confidence Scoring

Assign confidence based on evidence strength:

| Level | Criteria | Action |
|-------|----------|--------|
| **High** | 5+ corroborating instances, no contradictions | Codify as best practice |
| **Medium** | 2-4 instances, minor contradictions resolved | Document with caveats |
| **Low** | Single instance or unresolved contradictions | Flag for further observation |
| **Speculative** | Inferred from related patterns, not directly observed | Record as hypothesis only |

### Cross-Domain Transfer

When a pattern from one domain applies to another:

1. Identify the **abstract principle** behind the domain-specific pattern
2. Map the principle to the target domain's vocabulary and constraints
3. Validate with at least one concrete example in the target domain
4. Document both the source and target domain applications

---

## RAG Optimization Techniques

### Structuring Knowledge for Retrieval

Organize knowledge artifacts so retrieval systems can find the right content:

**Chunking Strategy**
- One knowledge nugget per chunk (avoid mixing topics)
- Include context preamble in each chunk (don't rely on surrounding chunks)
- Keep chunks between 200-800 tokens for embedding quality
- Use descriptive headings that match likely query terms

**Metadata Enrichment**
- Tag every artifact with: domain, workflow type, agent roles, confidence level
- Include synonyms and alternative phrasings in metadata
- Add "related to" links between associated artifacts
- Timestamp with creation and last-validated dates

**Embedding Quality**
- Write titles that capture the core insight (not just topic)
- Front-load the most important information in each chunk
- Use consistent terminology across related chunks
- Include concrete examples -- they improve semantic search relevance

### Retrieval Testing

After adding or updating knowledge:

1. Formulate 3-5 natural-language queries that should surface the new content
2. Run each query and verify the content appears in top results
3. Identify any queries that miss -- adjust chunk text or metadata
4. Test negative queries that should NOT surface this content

---

## Citation Methodology

### Citation Format

Use a numbered reference system throughout all synthesized outputs:

```
Inline: "Pattern X reduces errors by 30% [1] and improves throughput [2]."

References:
[1] Session 2025-03-12, agent: search-specialist -- "Error rate: 12% → 8.4%"
[2] Benchmark run #47, workflow: data-pipeline -- "Throughput: 150 → 195 ops/sec"
```

### Source Hierarchy

When multiple sources exist, prefer:

1. **Direct measurement** -- logs, metrics, test results
2. **Agent output** -- synthesized findings from specialist agents
3. **Documented convention** -- established practices in project docs
4. **Inferred pattern** -- derived from indirect evidence

### Citation Integrity Rules

- Never cite a source you haven't read or verified
- When paraphrasing, ensure the citation accurately represents the original
- If a source is ambiguous, quote the relevant passage directly
- Update citations when source material changes

---

## Knowledge Graph Construction

### Node Types

| Node | Represents | Key attributes |
|------|-----------|----------------|
| **Pattern** | A recognized approach or behavior | name, confidence, domain |
| **Outcome** | A measured result | metric, value, context |
| **Agent** | An agent role or instance | name, capabilities, domain |
| **Workflow** | A sequence of steps | name, phases, triggers |
| **Artifact** | A document, file, or dataset | type, path, last_updated |

### Edge Types

| Edge | Connects | Meaning |
|------|----------|---------|
| `produces` | Workflow → Outcome | "This workflow produces this outcome" |
| `uses` | Agent → Pattern | "This agent applies this pattern" |
| `evidences` | Outcome → Pattern | "This outcome supports this pattern" |
| `contradicts` | Outcome → Pattern | "This outcome challenges this pattern" |
| `references` | Artifact → Pattern | "This artifact documents this pattern" |
| `depends_on` | Pattern → Pattern | "This pattern requires this other pattern" |

### Graph Maintenance

- Prune nodes with no edges quarterly
- Merge duplicate patterns when discovered
- Update confidence scores as new evidence arrives
- Archive (don't delete) deprecated patterns with deprecation reason

---

## Insight Extraction

### The Extraction Pipeline

```
Raw Data → Filter → Cluster → Abstract → Validate → Codify
```

1. **Filter** -- Remove noise (routine logs, expected outcomes, duplicate signals)
2. **Cluster** -- Group related signals by theme, workflow, or agent
3. **Abstract** -- Extract the underlying principle from concrete instances
4. **Validate** -- Check against existing knowledge for contradictions
5. **Codify** -- Write the insight as a Knowledge Nugget with citations

### Extraction Questions

For each cluster of signals, ask:

- What is the common thread across these instances?
- Does this pattern hold outside the specific context where it was observed?
- What would falsify this pattern?
- Who needs to know about this?

---

## Continuous Learning Loops

### The Learning Cycle

```
Observe → Hypothesize → Test → Codify → Apply → Observe (repeat)
```

### Triggering a Learning Review

Schedule reviews when:

- A new workflow completes 10+ runs
- An agent reports an unexpected outcome
- A pattern's confidence score changes (up or down)
- Cross-domain transfer is attempted for the first time

### Review Checklist

- [ ] New patterns identified since last review
- [ ] Existing patterns with changed confidence levels
- [ ] Patterns that were applied and their outcomes
- [ ] Knowledge gaps identified by failed retrievals
- [ ] Stale artifacts that need re-validation

---

## Best Practice Codification

### When to Codify

A pattern is ready for codification when:

- Confidence is **High** (5+ corroborating instances)
- No unresolved contradictions remain
- The pattern has been applied successfully in at least 2 contexts
- A clear, actionable description can be written

### Codification Template

```markdown
# Best Practice: [Name]

## Context
When [situation], and [conditions apply].

## Practice
Do [specific action] because [evidence-backed reason].

## Evidence
- [Citation 1]: [outcome]
- [Citation 2]: [outcome]
- [Citation 3]: [outcome]

## Caveats
- Does not apply when [exception]
- Requires [prerequisite]

## Related
- See also: [related pattern]
- Supersedes: [older pattern, if applicable]
```

### Versioning Practices

- Use semantic versioning for major practice revisions
- Document what changed and why in each revision
- Keep previous versions accessible for reference
- Note when a practice is deprecated and what replaces it
