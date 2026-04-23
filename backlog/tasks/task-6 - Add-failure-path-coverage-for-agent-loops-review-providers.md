---
id: TASK-6
title: Add failure-path coverage for agent-loops review providers
status: To Do
assignee: []
created_date: '2026-04-10 00:16'
labels:
  - tests
  - agent-loops
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cover the remaining failure-path gaps in agent-loops review tooling: exhaustion of the full provider fallback chain and failure handling for explicitly requested providers.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 specialist-review.sh has a test proving all-provider failure exits non-zero with a clear error
- [ ] #2 diff-test-audit.sh has a test proving all-provider failure exits non-zero with a clear error
- [ ] #3 both scripts have a test proving explicit --provider failure does not fall back to another provider
- [ ] #4 targeted review-script tests or equivalent focused verification pass
<!-- AC:END -->
