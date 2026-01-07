# Reference: docs-cleanup

# Clean up documentation directory

You are tasked with cleaning up a documentation directory (root or docs/) by archiving completed task documentation and organizing active files.

## Context

The user wants to maintain a clean, organized documentation structure by:
- Archiving completed task documentation, POC summaries, and reports
- Keeping only actively-used documentation at the root level
- Improving discoverability and reducing cognitive load

## Personas (Thinking Modes)
- **documentation-specialist**: Content categorization, archival decisions, documentation lifecycle management
- **information-architect**: Organization structure, discoverability, taxonomy design
- **developer**: Active vs historical distinction, operational documentation needs

## Delegation Protocol

**This command does NOT delegate** - Documentation cleanup is direct file operations.

**Why no delegation**:
- ❌ Fast file moving operations (git mv)
- ❌ Simple directory creation (mkdir)
- ❌ Template-based summary creation
- ❌ Straightforward categorization (active vs archive)

**All work done directly**:
- Bash for file operations (mv, git mv, mkdir)
- Read for analyzing documentation content
- Write for creating cleanup summaries
- Glob for finding documentation files
- TodoWrite for tracking cleanup steps

**Note**: Personas guide documentation decisions (specialist for lifecycle, architect for organization, developer for operational needs).

## Tool Coordination
- **Bash**: File operations, git mv for tracked files (direct)
- **Read**: Analyze documentation content for categorization (direct)
- **Write**: Create cleanup summaries (direct)
- **Glob**: Find documentation by pattern (direct)
- **Edit**: Update .gitignore (direct)
- **TodoWrite**: Track cleanup steps (direct)

## Task Requirements

### 1. Analysis Phase

**Identify files to archive** by reading and categorizing:

**Archive candidates:**
- Task planning documents (e.g., `*PLAN*.md`, `*TASK*.md`)
- Sprint/project summaries (e.g., `*SUMMARY*.md`, `*PROGRESS*.md`)
- POC summaries (e.g., `POC_*.md`)
- Cleanup/analysis reports (e.g., `*REPORT*.md`, `*CLEANUP*.md`)
- Duplicate content (covered elsewhere)
- Historical documentation (completed initiatives)

**Keep as active:**
- Core guides (README, CONTRIBUTING, ARCHITECTURE)
- Onboarding documentation (QUICK_START, ONBOARDING_CHECKLIST)
- Operational guides (DEPLOYMENT, MAINTENANCE_CHECKLIST)
- Philosophy/design docs (DESIGN_PHILOSOPHY)
- Testing/development guides (TEST-REPORTING)

### 2. Archive Organization

Create archive structure if it doesn't exist:

```bash
mkdir -p docs/archive/completed-tasks
mkdir -p docs/archive/reports
mkdir -p docs/archive/poc
mkdir -p docs/archive/deprecated
```

**Archive categories:**
- `completed-tasks/` - Sprint plans, task docs, project summaries
- `reports/` - Analysis reports, cleanup reports, audit reports
- `poc/` - POC summaries and experimental demos
- `deprecated/` - Outdated but still referenced content

### 3. File Movement

Use `git mv` for tracked files, `mv` for untracked:

```bash
# For tracked files
git mv FILE.md docs/archive/CATEGORY/

# For untracked files
mv FILE.md docs/archive/CATEGORY/
```

**Rules:**
- Preserve file names (don't rename during archiving)
- Use git mv to maintain history for tracked files
- Group related files in same category

### 4. Generated Artifacts

**Identify and remove** (not archive):
- Generated reports with timestamps (e.g., `link-check-reports/`)
- Build artifacts (e.g., `html-report/`, `coverage/`)
- Temporary files (e.g., `tmp-*`, `.cache/`)

**Update .gitignore** to prevent future pollution:

```gitignore
# Reports and build artifacts
reports/
link-check-reports/
html-report/
coverage/
```

### 5. Documentation

Create cleanup summary at `docs/archive/[DIRECTORY]_CLEANUP_SUMMARY.md`:

**Include:**
- Date and status
- List of archived files with rationale
- List of retained files with rationale
- Before/after metrics (file count reduction)
- Archive structure explanation
- Maintenance guidelines (when to archive)
- Suggested git commit message

**Template structure:**

```markdown
# [Directory] Cleanup Summary

**Date**: YYYY-MM-DD
**Status**: ✅ Complete

## Actions Taken
[List what was archived and why]

## Structure (After Cleanup)
[Show clean structure]

## Success Metrics
[Before/after comparison table]

## Rationale
[Why these decisions were made]

## Maintenance Guidelines
[When to archive, criteria for active vs archive]

## Git Commit
[Suggested commit message]
```

### 6. Validation

**Verify:**
- Correct number of files moved
- Archive structure is organized
- No broken links created
- Active files are truly active
- Git status shows renames (R) not deletions (D)

## Execution Steps

Use TodoWrite to track progress:

1. **Analyze directory structure**
   - List all markdown files
   - Read files to understand content
   - Categorize as active or archive candidate

2. **Create archive structure**
   - Create necessary directories
   - Verify structure

3. **Archive completed tasks**
   - Move task plans and summaries
   - Move POC summaries
   - Move project completion docs

4. **Archive reports**
   - Move cleanup reports
   - Move analysis reports
   - Move audit reports

5. **Clean generated artifacts**
   - Remove timestamped reports
   - Remove build artifacts
   - Update .gitignore

6. **Create cleanup summary**
   - Document all changes
   - Provide rationale
   - Include maintenance guidelines
   - Suggest commit message

7. **Validate results**
   - Verify file counts
   - Check git status
   - Confirm organization

## Success Criteria

- [ ] Archive structure created and organized
- [ ] All historical docs archived appropriately
- [ ] Only active docs remain at root level
- [ ] Generated artifacts removed
- [ ] .gitignore updated
- [ ] Cleanup summary created
- [ ] File count reduced by 40-70%
- [ ] Clear separation of active vs historical

## Output Format

Provide:
1. Summary table (before/after file counts)
2. List of archived files with destinations
3. List of retained files with rationale
4. Git commit message (copy-pasteable)
5. Link to cleanup summary document

## Edge Cases

**If encountering:**
- **Uncertain files**: Ask user for guidance
- **Large files (>100KB)**: Confirm before archiving
- **Recently modified files**: Double-check if truly historical
- **Files referenced in code**: Keep active or create deprecation notice

## Reusability

This approach works for:
- Root-level documentation cleanup
- docs/ directory cleanup
- App-specific docs cleanup (apps/*/docs/)
- Any documentation directory needing organization

**Adjust archive location based on context:**
- Root cleanup → `docs/archive/`
- docs/ cleanup → `docs/archive/`
- App cleanup → `apps/APP/docs/archive/`
