# Agent Dispatch Reference

This reference defines which subagent types to use for documentation tasks,
how to prompt them, and coordination patterns.

## Search Agents (Phase 1)

All Phase 1 scanning agents use `model: "haiku"` for cost efficiency.
Use `subagent_type: "Explore"` for all search work.

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

### Doc-to-Code Freshness Agent

**Purpose:** Verify that existing docs still match the codebase.

**Task tool parameters:**
```
subagent_type: "Explore"
model: "haiku"
description: "Check docs against current code"
```

**Prompt template:**
```
Read every markdown file under docs/ and manual/. For each file, identify
concrete code references:
- Function or method names
- CLI flags and commands
- File paths referenced in the doc
- Configuration keys and values
- API endpoints or routes

For each reference, use Grep or Glob to verify it still exists in the
codebase. Report mismatches:
- RENAMED: the construct exists under a different name
- REMOVED: the construct no longer exists anywhere
- CHANGED: the construct exists but its signature/behavior differs

Include the doc file path, line number, and the stale reference.
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
