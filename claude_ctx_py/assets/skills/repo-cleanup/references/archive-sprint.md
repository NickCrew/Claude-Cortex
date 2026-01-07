# Reference: archive-sprint

# Archive completed sprint artifacts

You are tasked with archiving all artifacts from a completed sprint, including plans, summaries, reports, and temporary files.

## Context

The user has completed a sprint/project and wants to:
- Archive all sprint-specific documentation
- Clean up temporary files and branches
- Preserve work for future reference
- Reset workspace for next sprint
- Document sprint outcomes

## Personas (Thinking Modes)
- **project-manager**: Sprint retrospectives, completion criteria, outcome documentation, metrics tracking
- **documentation-specialist**: Archive organization, summary writing, information preservation
- **devops-engineer**: Branch cleanup, workspace hygiene, artifact management

## Delegation Protocol

**This command does NOT delegate** - Sprint archival is direct file operations.

**Why no delegation**:
- ❌ Fast file moving and copying operations (<2 minutes)
- ❌ Straightforward git branch cleanup (atomic commands)
- ❌ Template-based summary generation (fill-in-the-blanks)
- ❌ Simple directory structure creation

**All work done directly**:
- Bash for file operations (mv, mkdir, rm)
- Write for sprint summary creation
- Read for identifying sprint artifacts
- Git commands for branch cleanup
- TodoWrite for tracking cleanup steps

**Note**: While this doesn't delegate, the personas guide thinking to ensure comprehensive archival (PM for metrics, documentation for clarity, devops for cleanliness).

## Tool Coordination
- **Bash**: File operations, git branch cleanup (direct)
- **Write**: Create sprint summary from template (direct)
- **Read**: Identify sprint artifacts and documentation (direct)
- **Glob**: Find sprint-related files by pattern (direct)
- **TodoWrite**: Track multi-step archival process (direct)

## Task Requirements

### 1. Analysis Phase

**Identify sprint artifacts:**

**Documentation:**
- Sprint plans: `*PLAN*.md`, `*SPRINT*.md`
- Task breakdowns: `*TASKS*.md`, `*TODO*.md`
- Progress summaries: `*PROGRESS*.md`, `*SUMMARY*.md`
- Status reports: `*STATUS*.md`, `*REPORT*.md`
- POC documents: `POC_*.md`, `*POC*.md`
- Meeting notes: `*NOTES*.md`, `*MINUTES*.md`

**Code artifacts:**
- Feature branches
- Experimental code: `experiments/`, `prototype/`
- Debug scripts: `debug-*.ts`, `test-*.ts`
- Temporary utilities: `tmp-*.ts`, `scratch-*.ts`

**Generated files:**
- Test reports
- Coverage reports
- Performance benchmarks
- Build artifacts
- Log files

**Configuration:**
- Temporary configs: `config.tmp.*`, `*.backup`
- Environment files: `.env.backup`, `.env.old`

### 2. Archive Structure

Create sprint-specific archive:

```
docs/archive/sprints/
  └── YYYY-MM-sprint-name/
      ├── README.md              # Sprint summary
      ├── plans/                 # Sprint planning docs
      │   ├── sprint-plan.md
      │   ├── task-breakdown.md
      │   └── acceptance-criteria.md
      ├── progress/              # Progress tracking
      │   ├── daily-updates/
      │   ├── weekly-summaries/
      │   └── blockers.md
      ├── poc/                   # POCs and experiments
      │   ├── poc-summary.md
      │   └── experimental-code/
      ├── reports/               # Sprint reports
      │   ├── completion-report.md
      │   ├── metrics.md
      │   └── retrospective.md
      ├── code-samples/          # Notable code examples
      └── assets/                # Screenshots, diagrams
```

### 3. Sprint Summary Template

Create `docs/archive/sprints/YYYY-MM-sprint-name/README.md`:

```markdown
# Sprint: [Sprint Name] - [YYYY-MM]

**Duration**: [Start Date] - [End Date]
**Status**: ✅ Complete / ⚠️ Partial / ❌ Incomplete

---

## Sprint Goals

### Primary Objectives
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

### Stretch Goals
1. [Stretch 1]
2. [Stretch 2]

---

## Outcomes

### Completed ✅
- [Task 1] - [Brief description]
- [Task 2] - [Brief description]
- [Task 3] - [Brief description]

### Incomplete ❌
- [Task X] - [Reason not completed]
- [Task Y] - [Moved to next sprint]

### Success Metrics
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Test Coverage | 85% | 88% | ✅ |
| Tasks Completed | 15 | 14 | ⚠️ |
| Bugs Fixed | 10 | 12 | ✅ |
| Documentation | 100% | 95% | ⚠️ |

---

## Key Deliverables

1. **[Deliverable 1]**
   - Location: [Path or URL]
   - Description: [What was delivered]
   - Status: [Deployed/Merged/Complete]

2. **[Deliverable 2]**
   - Location: [Path or URL]
   - Description: [What was delivered]
   - Status: [Deployed/Merged/Complete]

---

## Technical Decisions

### Architecture Changes
- [Decision 1]: [Rationale]
- [Decision 2]: [Rationale]

### Technology Adopted
- [Technology]: [Why and how used]

### Deprecated/Removed
- [What was removed]: [Why]

---

## Challenges & Solutions

### Challenge 1: [Description]
**Impact**: [How it affected sprint]
**Solution**: [How it was resolved]
**Learning**: [What we learned]

### Challenge 2: [Description]
**Impact**: [How it affected sprint]
**Solution**: [How it was resolved]
**Learning**: [What we learned]

---

## Code Changes

### Files Added
- [List significant new files]

### Files Modified
- [List significantly changed files]

### Files Removed
- [List deleted files]

### Pull Requests
- #123 - [PR title and description]
- #124 - [PR title and description]

---

## Testing

### Test Coverage
- Unit tests: [X tests, Y% coverage]
- Integration tests: [X tests]
- E2E tests: [X tests]

### Known Issues
- [Issue 1]: [Description and plan]
- [Issue 2]: [Description and plan]

---

## Documentation

### Created
- [Doc 1]: [Description]
- [Doc 2]: [Description]

### Updated
- [Doc 1]: [What changed]
- [Doc 2]: [What changed]

---

## Retrospective

### What Went Well 🎉
- [Success 1]
- [Success 2]
- [Success 3]

### What Could Be Improved 🔧
- [Area 1]: [Suggestion]
- [Area 2]: [Suggestion]

### Action Items for Next Sprint
- [ ] [Action 1]
- [ ] [Action 2]
- [ ] [Action 3]

---

## Metrics

### Velocity
- Story points completed: [X]
- Story points planned: [Y]
- Velocity: [X/Y = Z%]

### Time Breakdown
- Development: [X hours]
- Testing: [Y hours]
- Code Review: [Z hours]
- Meetings: [A hours]
- Documentation: [B hours]

### Quality
- Bugs introduced: [X]
- Bugs fixed: [Y]
- Code review cycles: [Avg Z per PR]
- Build failures: [X]

---

## Team

### Contributors
- [Name 1] - [Role/Contribution]
- [Name 2] - [Role/Contribution]

### Thanks To
- [Person] - [Why thanking them]

---

## Next Steps

### Immediate (Next Sprint)
- [ ] [Task from incomplete items]
- [ ] [Follow-up work]

### Future (Backlog)
- [ ] [Long-term improvement]
- [ ] [Tech debt item]

---

## References

### Documentation
- [Link to sprint plan]
- [Link to task breakdown]
- [Link to retrospective notes]

### Code
- [Link to feature branch]
- [Link to deployment]
- [Link to merged PRs]

### External
- [Link to designs]
- [Link to requirements]
```

---

## Execution Steps

Use TodoWrite to track progress:

1. **Identify sprint artifacts**
   - Search for sprint-related docs
   - Identify temporary files
   - List feature branches
   - Check for POC code

2. **Create archive structure**
   - Create sprint directory
   - Create subdirectories
   - Set up README template

3. **Archive documentation**
   - Move sprint plans
   - Move progress updates
   - Move reports
   - Move meeting notes

4. **Archive code artifacts**
   - Archive experimental code
   - Archive debug scripts
   - Document removed features
   - Save code samples

5. **Clean temporary files**
   - Remove debug scripts
   - Remove temporary configs
   - Remove backup files
   - Remove scratch files

6. **Document outcomes**
   - Fill sprint summary
   - List deliverables
   - Document decisions
   - Record metrics

7. **Clean git branches**
   - List merged branches
   - Delete merged branches
   - Archive unmerged branches (tags)

8. **Validate workspace**
   - Verify clean git status
   - Run tests
   - Run build
   - Check for leftover artifacts

## Success Criteria

- [ ] Sprint summary created
- [ ] All sprint docs archived
- [ ] Temporary files removed
- [ ] Code artifacts preserved
- [ ] Branches cleaned up
- [ ] Metrics documented
- [ ] Retrospective recorded
- [ ] Next steps identified
- [ ] Workspace clean for next sprint

## Git Branch Cleanup

**Safe branch deletion:**

```bash
# List all branches
git branch -a

# List merged branches
git branch --merged main

# Delete merged branches (after confirmation)
git branch -d feature/sprint-x-task-1
git branch -d feature/sprint-x-task-2

# For unmerged but completed work, create tags
git tag archive/sprint-x-feature-y feature/sprint-x-feature-y
git branch -D feature/sprint-x-feature-y

# Delete remote branches (after confirmation)
git push origin --delete feature/sprint-x-task-1
```

**Branch archive strategy:**

```bash
# Create archive tags for all sprint branches
for branch in $(git branch --list "feature/sprint-x-*"); do
  tag="archive/sprint-x/$(basename $branch)"
  git tag $tag $branch
  echo "Archived $branch as $tag"
done

# Push archive tags
git push origin --tags

# Delete local sprint branches
git branch --list "feature/sprint-x-*" | xargs git branch -D

# Delete remote sprint branches
git branch -r --list "origin/feature/sprint-x-*" | \
  sed 's/origin\///' | \
  xargs -I {} git push origin --delete {}
```

## Output Format

Provide:
1. Sprint summary with key metrics
2. List of archived documentation
3. List of cleaned temporary files
4. List of deleted branches
5. Workspace validation results
6. Retrospective highlights
7. Next sprint preparation checklist
8. Git commit message

## Edge Cases

**If encountering:**
- **Unmerged work**: Tag before deleting branches
- **Incomplete features**: Document reason in summary
- **Sensitive data**: Ask before archiving
- **Large files**: Compress or link to external storage
- **Ongoing work**: Clarify sprint boundaries with user

## Common Sprint Types

### Feature Sprint
- Focus on sprint summary completeness
- Archive POC code
- Document architecture decisions
- Preserve code samples

### Bug Fix Sprint
- Document bugs fixed
- Archive debugging tools
- Record solutions
- Update known issues

### Refactoring Sprint
- Document code changes
- Before/after comparisons
- Performance improvements
- Tech debt reduction

### Research Sprint
- Archive research findings
- Preserve POC code
- Document recommendations
- Link to external resources

## Prevention Tips

**Include in summary:**
- Use sprint-specific branches
- Maintain daily progress updates
- Document decisions as you go
- Clean up incrementally during sprint
- Schedule archival as last sprint task
- Automate branch cleanup in CI
