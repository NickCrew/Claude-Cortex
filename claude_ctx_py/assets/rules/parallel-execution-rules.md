# Parallel Execution Rules

## Core Directive
- Identify independent workstreams and run them in parallel unless a dependency requires sequencing.

## When to Parallelize
- Two or more independent tasks.
- Changes across 3+ files or multiple domains (code, tests, docs).
- Any long-running analysis that can proceed alongside implementation.

## Required Workstreams for Code Changes
- Implementation and quality (review/tests/docs) run concurrently.
- Validation runs after both complete.

## Execution Checklist
- Map dependencies first; mark what must be sequential.
- Batch file reads/edits and use parallel tool calls when safe.
- Prefer Task agents for multi-step or multi-file work.
