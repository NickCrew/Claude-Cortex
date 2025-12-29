# GitHub Issue Tracking for Parallel Workstreams

This document provides templates and guidance for tracking the 6 parallel workstreams using GitHub Issues and Projects.

---

## GitHub Project Board Setup

### Board Structure

**Project Name**: `claude-ctx Comprehensive Improvements`

**Views**:
1. **By Workstream** (Board view with columns)
2. **By Priority** (Table view)
3. **By Timeline** (Roadmap view)
4. **Overall Progress** (Dashboard)

### Columns (Board View)

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ 📋 Backlog   │ 🏃 In Prog   │ 👀 Review    │ ✅ Done      │ ⏸️ Blocked   │ ❌ Won't Do  │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### Workstream Swimlanes

- **WS1**: Testing (🧪)
- **WS2**: Refactoring (🔧)
- **WS3**: Features (✨)
- **WS4**: Documentation (📚)
- **WS5**: Quality (🛡️)
- **WS6**: CI/CD (🚀)

---

## Issue Labels

### Workstream Labels
- `ws1-testing` 🧪 - Testing workstream
- `ws2-refactoring` 🔧 - Refactoring workstream
- `ws3-features` ✨ - Features workstream
- `ws4-documentation` 📚 - Documentation workstream
- `ws5-quality` 🛡️ - Quality workstream
- `ws6-cicd` 🚀 - CI/CD workstream

### Priority Labels
- `priority-critical` 🔴 - Blocking issue, fix immediately
- `priority-high` 🟠 - Important, fix this week
- `priority-medium` 🟡 - Should fix soon
- `priority-low` 🟢 - Nice to have

### Type Labels
- `type-bug` 🐛 - Bug fix
- `type-enhancement` ✨ - New feature
- `type-refactor` 🔧 - Code refactoring
- `type-test` 🧪 - Test improvement
- `type-docs` 📚 - Documentation
- `type-ci` 🚀 - CI/CD improvement

### Status Labels
- `status-blocked` ⏸️ - Blocked by dependency
- `status-in-progress` 🏃 - Currently working on it
- `status-review` 👀 - Ready for review
- `status-needs-info` ❓ - Needs more information

### Size Labels (T-shirt sizing)
- `size-xs` - < 2 hours
- `size-s` - 2-4 hours
- `size-m` - 4-8 hours (1 day)
- `size-l` - 8-16 hours (2 days)
- `size-xl` - 16-40 hours (1 week)

---

## Epic/Milestone Structure

### Milestones

**Week 0**: Foundation (COMPLETE ✅)
- Baseline capture
- Documentation setup
- Quick wins

**Week 1-2**: Testing + CI/CD Foundation
- Core module testing
- CI/CD improvements
- Quality quick fixes

**Week 3-4**: Testing Expansion + TUI Start
- TUI testing framework
- Integration tests
- TUI refactoring begins

**Week 5-7**: Features + Refactoring
- Feature development starts
- Intelligence refactoring
- Configuration management

**Week 8-10**: Integration + Polish
- Final testing
- Documentation complete
- Quality gates passing

### Epics (GitHub Issues with `epic` label)

1. **Epic: Core Module Test Coverage** (`ws1-testing`)
   - Target: 15% → 80% coverage
   - Duration: Weeks 1-4
   - Sub-issues: One per module

2. **Epic: TUI Testing Framework** (`ws1-testing`)
   - Target: 0% → 70% coverage
   - Duration: Weeks 3-6
   - Sub-issues: Framework setup, per-view tests

3. **Epic: TUI Modularization** (`ws2-refactoring`)
   - Target: 2,914 lines → <500 per file
   - Duration: Weeks 4-6
   - Sub-issues: Per-component extraction

4. **Epic: Intelligence Refactoring** (`ws2-refactoring`)
   - Target: Pluggable learning strategies
   - Duration: Weeks 5-7
   - Sub-issues: Abstraction, implementation

5. **Epic: Advanced AI Features** (`ws3-features`)
   - Target: Embedding-based recommender
   - Duration: Weeks 5-8
   - Sub-issues: Prototype, evaluation, integration

6. **Epic: Architecture Documentation** (`ws4-documentation`)
   - Target: Complete docs site
   - Duration: Weeks 1-6
   - Sub-issues: Architecture, contributor guide, API docs

7. **Epic: Error Handling Standardization** (`ws5-quality`)
   - Target: Zero warnings, structured errors
   - Duration: Weeks 1-4
   - Sub-issues: SQLite fixes, datetime migration, docs

8. **Epic: CI/CD Pipeline** (`ws6-cicd`)
   - Target: All quality gates passing
   - Duration: Weeks 1-3
   - Sub-issues: Coverage, markers, performance

---

## Issue Templates

### Template 1: Core Module Testing

```markdown
## Core Module Testing: [module_name]

**Workstream**: WS1 - Testing 🧪
**Epic**: Core Module Test Coverage
**Priority**: High 🟠
**Size**: M (4-8 hours)

### Current Status
- Coverage: X%
- Target: Y%
- Lines: Z

### Test Checklist
- [ ] Public API tests (methods, functions)
- [ ] Error handling tests
- [ ] Edge case tests
- [ ] Integration points tests
- [ ] Documentation examples tested

### Success Criteria
- [ ] Coverage ≥ Y%
- [ ] All tests passing
- [ ] No flaky tests
- [ ] Code reviewed

### Related Issues
- Epic: #N
- Depends on: #M

### Notes
[Any additional context]
```

### Template 2: TUI Component Testing

```markdown
## TUI Testing: [component_name]

**Workstream**: WS1 - Testing 🧪
**Epic**: TUI Testing Framework
**Priority**: Medium 🟡
**Size**: L (8-16 hours)

### Component Details
- File: `tui/[filename].py`
- Lines: Z
- Views/Widgets: List

### Test Strategy
- [ ] Widget rendering tests
- [ ] User interaction tests (hotkeys, navigation)
- [ ] State management tests
- [ ] Error display tests
- [ ] Performance tests (if applicable)

### Textual Testing Setup
- [ ] Headless testing framework configured
- [ ] Snapshot tests (if applicable)
- [ ] Mock dependencies

### Success Criteria
- [ ] Coverage ≥ 70%
- [ ] All user flows tested
- [ ] No TUI rendering issues
- [ ] Performance acceptable (<100ms interactions)

### Related Issues
- Epic: #N
- Blocked by: #M (if any)

### Notes
[Any additional context]
```

### Template 3: Refactoring Task

```markdown
## Refactor: [component_name]

**Workstream**: WS2 - Refactoring 🔧
**Epic**: [TUI Modularization / Intelligence Refactoring]
**Priority**: High 🟠
**Size**: L (8-16 hours)

### Current State
- File: [path]
- Lines: Z (target: <500)
- Complexity: [description]

### Refactoring Goals
- [ ] Extract [ComponentA] (X lines)
- [ ] Extract [ComponentB] (Y lines)
- [ ] Create [abstraction/interface]
- [ ] Maintain backward compatibility

### Testing Strategy
- [ ] Regression tests before refactoring
- [ ] Tests pass after each extraction
- [ ] No API changes (or migration guide)
- [ ] Performance maintained or improved

### Success Criteria
- [ ] Target line count achieved
- [ ] All tests passing
- [ ] Code review approved
- [ ] Documentation updated

### Risk Assessment
- Risk level: [Low/Medium/High]
- Mitigation: [strategies]

### Related Issues
- Epic: #N
- Depends on: #M (tests)

### Notes
[Any additional context]
```

### Template 4: Feature Development

```markdown
## Feature: [feature_name]

**Workstream**: WS3 - Features ✨
**Epic**: [Advanced AI Features / Interactive TUI / Performance]
**Priority**: Medium 🟡
**Size**: XL (16-40 hours)

### Feature Description
[What does this feature do?]

### Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Implementation Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Testing Strategy
- [ ] Unit tests
- [ ] Integration tests
- [ ] User acceptance testing
- [ ] Performance testing (if applicable)

### Documentation
- [ ] API documentation
- [ ] User guide
- [ ] Examples
- [ ] Migration guide (if breaking)

### Success Criteria
- [ ] All requirements met
- [ ] Tests passing (≥80% coverage)
- [ ] Code review approved
- [ ] Documentation complete
- [ ] User feedback positive

### Related Issues
- Epic: #N
- Depends on: #M

### Notes
[Any additional context]
```

### Template 5: Documentation Task

```markdown
## Documentation: [topic]

**Workstream**: WS4 - Documentation 📚
**Epic**: [Architecture / Contributor Guide / API Docs]
**Priority**: Medium 🟡
**Size**: S (2-4 hours)

### Documentation Scope
[What needs to be documented?]

### Content Outline
1. [Section 1]
2. [Section 2]
3. [Section 3]

### Deliverables
- [ ] Main document
- [ ] Examples (if applicable)
- [ ] Diagrams (if applicable)
- [ ] Cross-links to related docs

### Success Criteria
- [ ] Accurate and up-to-date
- [ ] Clear and concise
- [ ] Reviewed by 2+ people
- [ ] Examples tested
- [ ] Published to docs site

### Related Issues
- Epic: #N

### Notes
[Any additional context]
```

### Template 6: Quality/Bug Fix

```markdown
## Fix: [issue_description]

**Workstream**: WS5 - Quality 🛡️
**Epic**: [Error Handling / Resource Cleanup]
**Priority**: High 🟠
**Size**: XS-S (< 4 hours)

### Issue Description
[What's the problem?]

### Root Cause
[Why is this happening?]

### Proposed Fix
[How will you fix it?]

### Testing Strategy
- [ ] Add test to reproduce issue
- [ ] Verify fix resolves issue
- [ ] Check for similar issues elsewhere
- [ ] Run relevant test suite

### Success Criteria
- [ ] Issue resolved
- [ ] Test added (regression prevention)
- [ ] No side effects
- [ ] Code review approved

### Related Issues
- Epic: #N
- Fixes: #M (if bug report)

### Notes
[Any additional context]
```

### Template 7: CI/CD Improvement

```markdown
## CI/CD: [improvement_name]

**Workstream**: WS6 - CI/CD 🚀
**Epic**: CI/CD Pipeline
**Priority**: High 🟠
**Size**: S-M (2-8 hours)

### Current State
[What's the current CI/CD status?]

### Proposed Improvement
[What will you improve?]

### Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Verification
- [ ] CI pipeline runs successfully
- [ ] All checks passing
- [ ] No performance regression
- [ ] Team notified of changes

### Success Criteria
- [ ] Improvement implemented
- [ ] CI passing
- [ ] Documentation updated (if needed)
- [ ] Team trained (if needed)

### Related Issues
- Epic: #N

### Notes
[Any additional context]
```

---

## Initial Issue Creation Commands

### Using GitHub CLI (`gh`)

```bash
# WS1: Core Module Testing Issues
gh issue create --title "Core Module Testing: intelligence.py" \
  --label "ws1-testing,priority-high,type-test,size-m" \
  --milestone "Week 1-2" \
  --body-file templates/core-module-template.md

gh issue create --title "Core Module Testing: agents.py" \
  --label "ws1-testing,priority-high,type-test,size-m" \
  --milestone "Week 1-2"

# WS5: Quality Quick Fixes
gh issue create --title "Fix: SQLite resource leaks in skill_recommender.py" \
  --label "ws5-quality,priority-critical,type-bug,size-s" \
  --milestone "Week 1-2"

gh issue create --title "Fix: Replace deprecated datetime.utcnow() (5 remaining)" \
  --label "ws5-quality,priority-high,type-bug,size-xs" \
  --milestone "Week 1-2"

# WS6: CI/CD (completed)
gh issue create --title "CI/CD: Register pytest markers" \
  --label "ws6-cicd,priority-critical,type-ci,size-xs" \
  --milestone "Week 0" \
  --state closed

# WS4: Documentation
gh issue create --title "Documentation: Contributor Getting Started Guide" \
  --label "ws4-documentation,priority-medium,type-docs,size-m" \
  --milestone "Week 1-2"
```

---

## Project Board Automation

### Recommended Automations

1. **New issues** → Automatically add to project
2. **Issues labeled `status-blocked`** → Move to "⏸️ Blocked" column
3. **Pull request opened** → Link to related issue, move to "👀 Review"
4. **Pull request merged** → Move issue to "✅ Done"
5. **Issue closed** → Move to "✅ Done" or "❌ Won't Do"

### GitHub Actions Integration

```yaml
# .github/workflows/project-automation.yml
name: Project Board Automation

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, closed]

jobs:
  update-project:
    runs-on: ubuntu-latest
    steps:
      - name: Add to project
        uses: actions/add-to-project@v0.3.0
        with:
          project-url: https://github.com/users/[USER]/projects/[N]
          github-token: ${{ secrets.ADD_TO_PROJECT_PAT }}
```

---

## Tracking Metrics

### Weekly Metrics to Track

**Coverage**:
- Overall coverage % (target: +5-10% per week)
- Core module coverage %
- TUI coverage %

**Testing**:
- Total test count
- Tests added this week
- Test pass rate

**Quality**:
- Open bugs
- Bugs fixed
- Warnings remaining

**Velocity**:
- Issues completed
- Story points completed (if using)
- Issues in progress

**Workstream Health**:
- WS1-6 completion %
- Blockers count
- On-track vs. delayed

### Dashboard View Fields

Add custom fields to GitHub Project:

- **Workstream**: Select (WS1-6)
- **Priority**: Select (Critical, High, Medium, Low)
- **Size**: Select (XS, S, M, L, XL)
- **Coverage Δ**: Number (coverage increase from this issue)
- **Week**: Select (Week 1, Week 2, etc.)
- **Status**: Select (Backlog, In Progress, Review, Done, Blocked)

---

## Example Issue List (Week 1)

### Critical (Do First)
1. ⏸️ Fix test collection error (WS1) - #[TBD]
2. ✅ Register pytest markers (WS6) - DONE
3. ✅ Adjust coverage gate (WS6) - DONE
4. 🏃 Fix SQLite resource leaks (WS5) - #[TBD]
5. 🏃 Complete datetime.utcnow() migration (WS5) - #[TBD]

### High Priority (Week 1)
6. 📋 Core Module Testing: intelligence.py (WS1) - #[TBD]
7. 📋 Core Module Testing: agents.py (WS1) - #[TBD]
8. 📋 Core Module Testing: base.py (WS1) - #[TBD]
9. 📋 Documentation: Contributor Guide (WS4) - #[TBD]
10. 📋 Documentation: Testing Conventions (WS4) - #[TBD]

### Medium Priority (Week 1-2)
11. 📋 TUI Testing Framework Setup (WS1) - #[TBD]
12. 📋 Integration Test: AI Recommendation Flow (WS1) - #[TBD]
13. 📋 Documentation: API Reference Structure (WS4) - #[TBD]
14. 📋 CI/CD: Pre-commit Hooks (WS6) - #[TBD]

---

## Quick Reference Commands

### Create Epic
```bash
gh issue create --title "Epic: [Epic Name]" \
  --label "epic,ws[N]-[workstream]" \
  --milestone "[Milestone]" \
  --body "Epic description and goals"
```

### Bulk Add Labels
```bash
gh label create "ws1-testing" --color "0e8a16" --description "Testing workstream"
gh label create "ws2-refactoring" --color "fbca04" --description "Refactoring workstream"
gh label create "ws3-features" --color "d93f0b" --description "Features workstream"
gh label create "ws4-documentation" --color "0075ca" --description "Documentation workstream"
gh label create "ws5-quality" --color "5319e7" --description "Quality workstream"
gh label create "ws6-cicd" --color "1d76db" --description "CI/CD workstream"
```

### List Issues by Workstream
```bash
gh issue list --label "ws1-testing" --state all
gh issue list --label "ws5-quality" --state open
```

### Close Issue with Message
```bash
gh issue close [N] --comment "Fixed in PR #M"
```

---

## Next Steps

1. [ ] Create GitHub Project Board
2. [ ] Add custom fields (Workstream, Priority, Size, etc.)
3. [ ] Create labels (workstream, priority, type, size)
4. [ ] Set up automation rules
5. [ ] Create initial issues for Week 1 (see example list)
6. [ ] Add team members to project
7. [ ] Schedule weekly project review

---

**Note**: Adapt this structure to your team's GitHub organization and workflow preferences. The key is maintaining clear workstream separation while enabling cross-workstream visibility and coordination.
