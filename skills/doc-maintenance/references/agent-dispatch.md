# Agent Dispatch Reference

This reference defines which subagent types to use for documentation tasks,
how to prompt them, and coordination patterns.

## Search Agents (Phase 1)

Model selection is task-calibrated. Pure pattern enumeration (find every X)
runs on `haiku` + `Explore`. Multi-file correlation and judgment runs on
`sonnet` + `general-purpose`, dispatched **per-docfile** so each call has
focused context.

### Code-to-Doc Coverage Agent

**Purpose:** Find codebase constructs that lack documentation.

**Task tool parameters:**
```
subagent_type: "Explore"
model: "haiku"
description: "Scan code for undocumented items"
```

**Prompt template:**
```
Search the codebase for publicly exported or user-facing constructs:
- Exported functions, classes, and constants
- CLI entry points and subcommands
- Configuration schemas and environment variables
- Public API endpoints
- Key data models

For each item found, check whether corresponding documentation exists in
docs/ or manual/. Report items that are NOT documented, including:
- The item name and type (function, class, CLI command, etc.)
- The source file and line number
- Which doc folder it should live in per the folder structure

Do NOT read the full contents of large files. Use Grep to find exports
and Glob to check for matching doc files.
```

### Doc-to-Code Freshness Agent (per-docfile sonnet)

**Purpose:** Verify that existing docs still match the codebase. Multi-file
trace work — handler → middleware → config — is common, so haiku's excerpt
reads aren't sufficient.

**Dispatch pattern:** One agent call per markdown file in scope. Total
calls = N markdown files. Each call has focused context (one doc + the
codebase) for higher precision.

**Task tool parameters:**
```
subagent_type: "general-purpose"
model: "sonnet"
description: "Doc-to-code freshness for <docfile>"
```

**Prompt template (one per docfile):**
```
Read the doc file at <DOCFILE_PATH>. Identify every concrete code reference:
- Function or method names
- CLI flags and commands
- File paths referenced in the doc
- Configuration keys and values
- API endpoints or routes
- Class names and module paths

For each reference, verify it still exists in the codebase. Use codanna MCP
when available; otherwise grep + Read. For each reference that has changed:

Classify as:
- RENAMED: construct exists under a different name (cite both old and new
  locations as `path:line`)
- REMOVED: construct no longer exists anywhere (cite where the doc references
  it, plus a grep that returned 0 matches)
- CHANGED: construct exists but signature/behavior differs (cite the current
  definition and quote the divergence)

Output as YAML, one entry per finding:
- doc_file: <path>
- line: <line in doc>
- reference: <what the doc says>
- status: RENAMED | REMOVED | CHANGED
- evidence: <verbatim doc line>
- current_location: <path:line> (for RENAMED/CHANGED)
- discrepancy: <what's different> (for CHANGED)

Optimize for accuracy over volume — 5 verified mismatches beat 20 with
fabricated paths. Verify each location exists before reporting.
```

### Structure Compliance Agent

**Purpose:** Verify folder layout matches the prescribed structure.

**Task tool parameters:**
```
subagent_type: "Explore"
model: "haiku"
description: "Audit doc folder structure"
```

**Prompt template:**
```
Read the folder structure specification at:
  skills/doc-maintenance/references/folder-structure.md

Then examine the actual directory trees under docs/ and manual/ using
Glob patterns. Report:
- MISSING: Required folders that do not exist
- MISPLACED: Files that exist in the wrong folder per the spec
- NAMING: Files that violate naming conventions (spaces, camelCase, etc.)
- NO_INDEX: Folders that lack an index.md or README.md

Use Glob with patterns like "docs/**/*.md" and "manual/**/*.md" to
discover all files, then classify each by its parent folder.
```

### Agent 4a — ASCII Diagram Detector (haiku, mechanical)

**Purpose:** Find ASCII/text diagrams that should be converted to Mermaid.
Pure pattern matching — find the box-drawing characters or arrow notation,
report their location.

**Task tool parameters:**
```
subagent_type: "Explore"
model: "haiku"
description: "Scan docs for ASCII diagrams to convert"
```

**Prompt template:**
```
Scan markdown files under docs/, manual/, and README.md for ASCII diagrams.

Look for:
- Box-drawing characters (─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼) in code blocks or indented sections
- Arrow notation (-->, <--, ==>) in code blocks
- Pipe-based tables used as diagrams
- Indented tree structures beyond a few simple nodes

Only flag diagrams with more than a few nodes — trivial 2-3 node diagrams can
stay as ASCII.

Output format for each finding:
- File: [path]
- Lines: [start]-[end]
- Suggested Mermaid type: [flowchart|sequenceDiagram|stateDiagram|erDiagram|etc.]
- Approximate node count: [N]

Do NOT make judgment calls about whether prose sections without ASCII diagrams
"need" a diagram — that's a separate scan handled by Agent 4b.
```

### Agent 4b — Missing-Diagram Judgment Scan (sonnet, per-docfile)

**Purpose:** Identify prose sections where adding a diagram would *meaningfully*
improve comprehension. This is judgment, not pattern matching — haiku tends to
either over-flag (every step list looks diagrammable) or under-flag (misses
implicit flow descriptions). Sonnet's calibration is what makes this signal
trustworthy.

**Dispatch pattern:** One agent call per markdown file in scope.

**Task tool parameters:**
```
subagent_type: "general-purpose"
model: "sonnet"
description: "Missing-diagram judgment for <docfile>"
```

**Prompt template (one per docfile):**
```
Read the doc file at <DOCFILE_PATH>. Identify sections where adding a Mermaid
diagram would *meaningfully* improve comprehension. Be selective.

Flag a section ONLY when ALL of these hold:
1. The prose describes a multi-step flow, architectural relationship, state
   transition, request/response sequence, data model with relationships, or
   decision tree.
2. The relationship is non-obvious from a quick read — readers would
   construct a mental diagram anyway, and putting it on the page saves effort.
3. The diagram would NOT just repeat what's already clear from the prose
   structure (numbered lists describing simple sequence don't need diagrams).
4. No diagram or visual already exists in or near the section.

Common false positives to skip:
- Any list of 3-4 steps (these read fine as prose)
- Any "if X then Y" pair (not enough to merit a diagram)
- Sections that describe a single entity's properties (use a table, not a diagram)

Output format for each finding:
- File: <path>
- Lines: <start>-<end>
- Suggested Mermaid type: <flowchart|sequenceDiagram|stateDiagram|erDiagram>
- What the diagram should depict: <one sentence>
- Why prose alone is insufficient: <one sentence — must be specific to this section, not generic>

Optimize for precision over recall. A clean log of 3 high-value diagrams beats
20 marginal candidates the user will mostly ignore.
```

---

## Remediation Agents (Phase 3)

These agents create or update documentation. Use the specific subagent types below.

### reference-builder

**Use for:** API documentation, configuration references, CLI references, parameter listings.

**Task tool parameters:**
```
subagent_type: "reference-builder"
description: "Build API/CLI reference doc"
```

**Prompt template (new doc):**
```
Create a comprehensive reference document for [ITEM].

Source code to document:
  [FILE_PATH]

Target output path:
  [TARGET_PATH per folder structure]

Requirements:
- Document every public parameter, option, and return value
- Include usage examples for each entry
- Follow the naming conventions in the folder structure spec
- Use tables for parameter listings
- Include a table of contents for documents with >5 sections
```

**Prompt template (update existing):**
```
Update the reference document at [DOC_PATH].

The following items are stale or missing:
  [LIST OF FINDINGS]

Read the current document, then read the source code at [SOURCE_PATH].
Make minimal, targeted edits to fix only the identified issues.
Do not reorganize or restyle unaffected sections.
```

### technical-writer

**Use for:** Architecture docs, developer guides, testing docs, security docs,
plans, and any internal documentation.

**Task tool parameters:**
```
subagent_type: "technical-writer"
description: "Write/update developer doc"
```

**Prompt template (new doc):**
```
Create a [DOC_TYPE] document for [TOPIC].

Relevant source files:
  [FILE_PATHS]

Target output path:
  [TARGET_PATH per folder structure]

Requirements:
- Write for a developer audience familiar with the project
- Include concrete code examples where relevant
- Follow existing doc conventions in the project
- Add to the parent folder's index.md if one exists
```

**Prompt template (update existing):**
```
Update the document at [DOC_PATH].

Findings to address:
  [LIST OF FINDINGS]

Read the current document and the relevant source code.
Fix only the identified issues. Preserve the existing structure
and voice of the document.
```

### learning-guide

**Use for:** User-facing tutorials, getting-started guides, how-to guides,
troubleshooting docs. All output goes to `manual/`.

**Task tool parameters:**
```
subagent_type: "learning-guide"
description: "Write user-facing tutorial/guide"
```

**Prompt template (new doc):**
```
Create a [GUIDE_TYPE] for [TOPIC] targeting end users.

Relevant source files for understanding the feature:
  [FILE_PATHS]

Target output path:
  [TARGET_PATH under manual/]

Requirements:
- Write for users who may not be developers
- Use progressive disclosure: start simple, add complexity
- Include concrete, copy-pasteable examples
- Add troubleshooting tips for common pitfalls
- Follow the naming convention: [CONVENTION per folder-structure.md]
```

**Prompt template (update existing):**
```
Update the user guide at [DOC_PATH].

Findings to address:
  [LIST OF FINDINGS]

Read the current guide and the relevant source code.
Fix only the identified issues. Maintain the existing
progressive-disclosure structure and user-friendly tone.
```

### mermaid-expert

**Use for:** Converting ASCII/text diagrams to Mermaid and creating new diagrams
where prose would benefit from visual representation. Diagrams are inlined into
the markdown file as fenced mermaid code blocks.

**Task tool parameters:**
```
subagent_type: "mermaid-expert"
description: "Create/convert Mermaid diagram"
```

**Prompt template (convert ASCII to Mermaid):**
```
Convert the ASCII/text diagram in [DOC_PATH] at lines [LINE_RANGE] to a
Mermaid diagram.

Read the file and understand the diagram's intent from the surrounding context.
Replace the ASCII diagram with a fenced mermaid code block:

    ```mermaid
    [diagram code]
    ```

Requirements:
- Preserve all nodes, edges, and labels from the original
- Choose the most appropriate Mermaid diagram type: [SUGGESTED_TYPE]
- Keep the diagram readable — use short node labels with longer descriptions
  in the surrounding prose if needed
- Remove the original ASCII diagram after inserting the Mermaid block
- Do not change any other content in the file
```

**Prompt template (create new diagram):**
```
Add a Mermaid diagram to [DOC_PATH] near line [LINE_NUMBER] to illustrate
the [DESCRIPTION] described in that section.

Read the file and the surrounding context. Insert an inline fenced mermaid
code block:

    ```mermaid
    [diagram code]
    ```

Requirements:
- Diagram type: [SUGGESTED_TYPE]
- Capture the key relationships/flow described in the prose
- Keep diagrams focused — 5-15 nodes is ideal, avoid overwhelming detail
- Place the diagram immediately after the prose paragraph it illustrates
- Do not duplicate information already clear from the text — the diagram
  should complement the prose, not repeat it verbatim
- Do not change any other content in the file
```

### docs-architect (Quality Gate)

**Use for:** Final review of all documentation changes from a maintenance pass.

**Task tool parameters:**
```
subagent_type: "docs-architect"
description: "Quality gate review of doc changes"
```

**Prompt template:**
```
Review all documentation changes from this maintenance pass.

Files created or modified:
  [LIST OF FILE_PATHS]

Folder structure spec:
  skills/doc-maintenance/references/folder-structure.md

Check for:
1. ACCURACY — Do docs match current code?
2. COMPLETENESS — Are all public interfaces covered?
3. ORGANIZATION — Does folder structure match the spec?
4. CROSS-REFERENCES — Are all internal links valid?
5. CONSISTENCY — Tone, formatting, heading levels
6. NO ORPHANS — Every new doc is linked from an index or parent

Output a structured verdict:
- PASS: All checks pass
- FAIL: List specific issues that must be fixed before closing

If FAIL, categorize each issue by which remediation agent should fix it.
```

---

## Coordination Patterns

### Parallel dispatch

Group independent remediation tasks and dispatch simultaneously:

```
# Good: these don't depend on each other
Task 1: reference-builder → docs/api/auth-service.md
Task 2: technical-writer  → docs/architecture/data-flow.md
Task 3: learning-guide    → manual/guides/how-to-configure-auth.md
```

### Serial dispatch

When one doc depends on another, serialize:

```
# The tutorial links to the API reference, so reference must exist first
Task 1: reference-builder → docs/api/auth-service.md
Task 2: learning-guide    → manual/tutorials/02-authentication.md  (depends on Task 1)
```

### Batch size

Dispatch up to 4 remediation agents in parallel. If more than 4 findings
need remediation, batch them in groups of 4 and wait for each batch to
complete before starting the next.
