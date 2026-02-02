# Quality Gate Rules

## Core Directive
- Every code change must run a parallel quality workstream (review, tests, docs).
- If a gate can’t run, say why and propose the next best verification.

## Required Gates
- **Code review**: correctness, security, performance, and convention checks.
- **Tests**: add or update coverage for changed behavior; run relevant suites.
- **Docs**: update public APIs, user-facing behavior, or complex logic.

## Completion Criteria
- Address all reported issues before marking the task complete.
