# Reference: code-cleanup

# Clean up code directories

You are tasked with cleaning up source code directories by removing build artifacts, dead code, unused files, and organizing test/example files.

## Context

The user wants to maintain clean code directories by:
- Removing build artifacts and generated files
- Identifying and removing dead/unused code
- Organizing example and test files
- Improving project structure
- Reducing repository bloat

## Personas (Thinking Modes)
- **developer**: Code organization, dead code identification, import analysis, refactoring safety
- **quality-engineer**: Code health metrics, technical debt management, cleanup standards
- **devops-engineer**: Build artifact management, .gitignore patterns, workspace hygiene

## Delegation Protocol

**This command does NOT delegate** - Code cleanup is direct file and tooling operations.

**Why no delegation**:
- ❌ Fast file removal (rm, git rm operations)
- ❌ Simple tool execution (ts-prune, depcheck, unimported)
- ❌ Straightforward file reorganization (mv, git mv)
- ❌ Direct .gitignore editing

**All work done directly**:
- Bash for build artifact removal and file reorganization
- Bash for running analysis tools (ts-prune, depcheck)
- Read/Write for .gitignore updates
- Grep for import/reference searching
- TodoWrite for tracking cleanup steps

**Note**: Personas ensure thorough cleanup (developer for safety, quality for standards, devops for automation patterns).

## Tool Coordination
- **Bash**: Remove artifacts, reorganize files, run analysis tools (direct)
- **Grep**: Search for imports and references (direct)
- **Glob**: Find files by pattern for cleanup (direct)
- **Edit/Write**: Update .gitignore (direct)
- **TodoWrite**: Track multi-step cleanup process (direct)

## Task Requirements

### 1. Analysis Phase

**Identify files to remove or reorganize:**

**Remove (build artifacts & generated files):**
- Build output directories: `dist/`, `build/`, `.next/`, `.nuxt/`, `out/`
- Cache directories: `.vite/`, `.turbo/`, `.nx/cache/`, `.parcel-cache/`
- Coverage reports: `coverage/`, `.nyc_output/`, `htmlcov/`
- Test reports: `test-results/`, `junit.xml`, `report.html`
- Temporary files: `*.tmp`, `*.temp`, `.cache/`, `tmp-*`
- Lock files (if regenerable): `package-lock.json` conflicts

**Remove (OS/IDE artifacts):**
- `.DS_Store` (macOS)
- `Thumbs.db` (Windows)
- `*.swp`, `*.swo` (Vim)
- `.vscode/` (if not shared)
- `.idea/` (if not shared)

**Reorganize (misplaced files):**
- Example scripts not in `examples/`
- Test files not in `tests/` or `__tests__/`
- Debug scripts not in `scripts/debug/`
- Documentation not in `docs/`

**Investigate (potential dead code):**
- Files not imported anywhere
- Functions/classes not used
- Commented-out code blocks (>20 lines)
- TODO/FIXME comments (catalog)

### 2. Safe Removal Process

**Before removing anything:**

1. **Run tests** to establish baseline
2. **Check git history** for recent changes
3. **Search for imports/references** in codebase
4. **Verify it's generated** (can be rebuilt)

**Removal categories:**

```bash
# Safe to delete immediately
rm -rf dist/ build/ coverage/ .vite/ .DS_Store

# Move to archive before deleting (30-day hold)
mkdir -p .cleanup-archive/$(date +%Y-%m-%d)
mv SUSPICIOUS_FILE .cleanup-archive/$(date +%Y-%m-%d)/

# Ask user before removing
echo "Found potential dead code: FILE - used in 0 places"
```

### 3. Code Organization

**Standard structure:**

```
src/
  ├── components/     # React/Vue components
  ├── services/       # Business logic
  ├── utils/          # Helper functions
  ├── types/          # TypeScript types
  ├── hooks/          # React hooks
  ├── store/          # State management
  └── __tests__/      # Unit tests (colocated)

tests/
  ├── unit/           # Unit tests
  ├── integration/    # Integration tests
  ├── e2e/            # End-to-end tests
  └── fixtures/       # Test data

examples/
  ├── basic/          # Simple examples
  ├── advanced/       # Complex examples
  └── integrations/   # Integration examples

scripts/
  ├── build/          # Build scripts
  ├── deploy/         # Deployment scripts
  └── debug/          # Debug utilities
```

**Move misplaced files:**

```bash
# Example scripts
mv debug-*.ts examples/debug/
mv test-*.ts examples/testing/

# Test files
mv src/foo.test.ts tests/unit/
mv integration-test.ts tests/integration/

# Documentation
mv HOWTO.md docs/guides/
```

### 4. Dead Code Detection

**Use tools:**

```bash
# TypeScript - find unused exports
npx ts-prune

# JavaScript - find unused code
npx depcheck

# Find files not imported
npx unimported

# Find unused dependencies
npx depcheck --json > unused-deps.json
```

**Manual inspection:**

1. Search for imports: `grep -r "from './FILE'" .`
2. Check git log: `git log --follow FILE`
3. Check last modified: `find . -name "FILE" -mtime +180`
4. Count references: `grep -r "FUNCTION_NAME" . | wc -l`

**Decision matrix:**

| Condition | Action |
|-----------|--------|
| No imports, >6 months old | Remove |
| No imports, <6 months old | Ask user |
| Imported but unused | Investigate further |
| TODO/FIXME, >1 year old | Ask user |
| Commented code, >50 lines | Remove |

### 5. .gitignore Update

**Ensure comprehensive .gitignore:**

```gitignore
# Build artifacts
dist/
build/
out/
.next/
.nuxt/

# Cache
.cache/
.vite/
.turbo/
.nx/cache/
.parcel-cache/
node_modules/.cache/

# Testing
coverage/
.nyc_output/
test-results/
playwright-report/
htmlcov/
.pytest_cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*.swn

# OS
.DS_Store
Thumbs.db
Desktop.ini

# Temporary
*.tmp
*.temp
tmp-*
.cleanup-archive/

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```

### 6. Documentation

Create cleanup report at `docs/cleanup-reports/CODE_CLEANUP_$(date +%Y-%m-%d).md`:

```markdown
# Code Cleanup Report - [Date]

## Summary
- Removed X build artifacts
- Cleaned Y cache directories
- Reorganized Z misplaced files
- Identified A potential dead code files

## Actions Taken

### Removed (Build Artifacts)
- [List removed directories/files]
- Disk space saved: XXX MB

### Removed (Dead Code)
- [List removed files with justification]

### Reorganized
- [List moved files with before/after paths]

### .gitignore Updates
- [List patterns added]

## Potential Issues
- [List files needing user decision]
- [List TODO/FIXME items found]

## Validation
- [ ] Tests still passing
- [ ] Build succeeds
- [ ] No broken imports
- [ ] Git status clean

## Prevention
- [Recommendations to avoid future bloat]
```

## Execution Steps

Use TodoWrite to track progress:

1. **Analyze directory structure**
   - List all files
   - Identify build artifacts
   - Find cache directories
   - Check for OS/IDE files

2. **Safe removal (build artifacts)**
   - Remove dist/build directories
   - Remove cache directories
   - Remove test reports
   - Remove temporary files

3. **Update .gitignore**
   - Add missing patterns
   - Ensure comprehensive coverage
   - Test with `git status`

4. **Detect dead code**
   - Run ts-prune/depcheck
   - Search for unused imports
   - Check file ages
   - Catalog findings

5. **Reorganize misplaced files**
   - Move examples to examples/
   - Move tests to tests/
   - Move scripts to scripts/
   - Update imports

6. **Remove dead code (with approval)**
   - Present findings to user
   - Get confirmation
   - Remove approved files
   - Update references

7. **Validate**
   - Run tests
   - Run build
   - Check for broken imports
   - Verify git status

8. **Document cleanup**
   - Create cleanup report
   - List all changes
   - Provide commit message

## Success Criteria

- [ ] All build artifacts removed
- [ ] Cache directories cleaned
- [ ] OS/IDE artifacts removed
- [ ] .gitignore updated
- [ ] Misplaced files reorganized
- [ ] Dead code identified (and removed if approved)
- [ ] Tests passing
- [ ] Build succeeds
- [ ] Cleanup report created
- [ ] Disk space saved (>50MB typical)

## Safety Rules

**NEVER remove without checking:**
- Files modified in last 7 days
- Files with unclear purpose
- Files that might be data/config
- Files referenced in docs

**ALWAYS:**
- Run tests before and after
- Use git mv for reorganization
- Create cleanup report
- Ask user for uncertain files
- Verify builds succeed

## Output Format

Provide:
1. Summary table (files removed, space saved)
2. List of removed build artifacts
3. List of reorganized files
4. Dead code findings (with recommendations)
5. .gitignore updates
6. Validation results
7. Git commit message (copy-pasteable)

## Edge Cases

**If encountering:**
- **Large files (>10MB)**: Report size, ask before removing
- **Recently modified artifacts**: Verify they're truly artifacts
- **Unknown file types**: Ask user
- **Potential configuration**: Keep and ask user
- **Data files**: Never remove, ask user

## Common Patterns

**Monorepo cleanup:**
```bash
# Clean all apps
for app in apps/*; do
  rm -rf $app/dist $app/coverage $app/.vite
done

# Clean all packages
for pkg in packages/*; do
  rm -rf $pkg/dist $pkg/coverage
done
```

**TypeScript project:**
```bash
# Remove build outputs
rm -rf dist/ build/ lib/

# Remove TypeScript cache
rm -rf .tsbuildinfo

# Regenerate
pnpm build
```

**React/Next.js project:**
```bash
# Remove build artifacts
rm -rf .next/ out/ build/

# Remove cache
rm -rf .cache/ node_modules/.cache/

# Rebuild
pnpm build
```

## Prevention Tips

**Include in report:**
- Set up pre-commit hooks to prevent committing artifacts
- Add comprehensive .gitignore early
- Configure IDE to exclude build directories
- Regular cleanup (monthly/quarterly)
- Use tools like `npx ts-prune` in CI
- Monitor repository size trends
