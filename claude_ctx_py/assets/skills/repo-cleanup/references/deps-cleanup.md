# Reference: deps-cleanup

# Clean up dependencies and package management

You are tasked with cleaning up project dependencies, removing unused packages, updating outdated dependencies, and organizing package management files.

## Context

The user wants to maintain clean dependency management by:
- Removing unused dependencies
- Updating outdated packages
- Deduplicating dependencies
- Organizing lock files
- Reducing package bloat
- Improving security

## Personas (Thinking Modes)
- **developer**: Dependency usage analysis, import tracing, safe removal verification
- **security-specialist**: Vulnerability assessment, security audit, compliance checking
- **devops-engineer**: Package management, lock file maintenance, CI/CD integration
- **performance-engineer**: Bundle size optimization, install time reduction, dependency efficiency

## Delegation Protocol

**This command does NOT delegate** - Dependency cleanup is direct tooling and file operations.

**Why no delegation**:
- ❌ Direct tool execution (depcheck, npm audit, npm outdated)
- ❌ Simple package operations (pnpm remove, pnpm update)
- ❌ Fast validation cycles (test after each change)
- ❌ Atomic git operations (commit per dependency change)

**All work done directly**:
- Bash for package manager commands (pnpm remove, update, dedupe)
- Bash for analysis tools (depcheck, npm audit)
- Read for package.json analysis
- Edit for package.json updates
- TodoWrite for tracking cleanup steps

**Note**: Personas ensure thorough cleanup (developer for safety, security for vulnerabilities, devops for automation, performance for efficiency).

## Tool Coordination
- **Bash**: Package manager commands, analysis tools, testing (direct)
- **Read/Edit**: package.json analysis and updates (direct)
- **Grep**: Find package usage in codebase (direct)
- **Write**: Create dependency reports (direct)
- **TodoWrite**: Track multi-step dependency cleanup (direct)

## Task Requirements

### 1. Analysis Phase

**Identify dependency issues:**

**Unused dependencies:**
- Packages in package.json but not imported
- DevDependencies not used in scripts/tests
- Transitive dependencies (unused by used packages)

**Outdated dependencies:**
- Packages with major version updates
- Packages with security vulnerabilities
- Deprecated packages

**Duplicate dependencies:**
- Multiple versions of same package
- Overlapping functionality (lodash + lodash-es)
- Redundant utilities

**Lock file issues:**
- Uncommitted lock file changes
- Corrupted lock files
- Conflicts between package managers

### 2. Dependency Analysis Tools

**Run analysis tools:**

```bash
# Find unused dependencies
npx depcheck

# Check for outdated packages
npm outdated
# or
pnpm outdated

# Find duplicate dependencies
npm ls [package-name]
# or
pnpm list --depth Infinity | grep [package-name]

# Security audit
npm audit
# or
pnpm audit

# Find deprecated packages
npm-check -u

# Analyze bundle size impact
npx webpack-bundle-analyzer

# Check license compliance
npx license-checker --summary
```

### 3. Safe Removal Process

**Decision matrix for removal:**

| Finding | Action |
|---------|--------|
| Not in package.json | No action needed |
| In package.json, not imported | Remove (safe) |
| In devDependencies, not in scripts | Investigate, likely remove |
| Direct dep, only used by removed feature | Remove |
| Transitive dep | Don't remove (managed by parent) |
| Has security vulnerability | Update or remove |
| Deprecated | Find replacement |

**Removal process:**

```bash
# 1. Create safety branch
git checkout -b deps-cleanup

# 2. Remove suspected unused dependency
pnpm remove [package-name]

# 3. Test immediately
pnpm build
pnpm test
pnpm type-check

# 4. If tests fail, restore and investigate
git restore package.json pnpm-lock.yaml
# Find where it's actually used
grep -r "[package-name]" src/ tests/

# 5. If tests pass, commit removal
git add package.json pnpm-lock.yaml
git commit -m "chore(deps): remove unused [package-name]"
```

### 4. Update Strategy

**Update categories:**

```bash
# Safe updates (patch versions)
pnpm update --latest

# Minor version updates (review breaking changes)
pnpm update --latest --interactive

# Major version updates (careful, test thoroughly)
pnpm update --latest [package-name]

# Update all (risky, only if comprehensive tests)
pnpm update --latest --recursive
```

**Update priority:**

1. **Critical**: Security vulnerabilities (immediate)
2. **High**: Deprecated packages (next sprint)
3. **Medium**: Outdated dev dependencies (monthly)
4. **Low**: Outdated production deps (quarterly)

**Safe update process:**

```bash
# 1. Update one at a time
pnpm update [package-name]

# 2. Run full test suite
pnpm test:all

# 3. Check for breaking changes
npm info [package-name] version
npm view [package-name] changelog

# 4. Update code if needed
# [Fix breaking changes]

# 5. Commit update
git add package.json pnpm-lock.yaml
git commit -m "chore(deps): update [package-name] from X to Y"

# 6. Repeat for next package
```

### 5. Deduplication

**Find duplicates:**

```bash
# npm
npm dedupe

# pnpm (automatic deduplication, but verify)
pnpm dedupe

# Check for duplicates
pnpm list --depth Infinity | grep "─[─┬]" | sort | uniq -d
```

**Resolve version conflicts:**

```bash
# Force single version in package.json
{
  "overrides": {
    "package-name": "1.2.3"
  }
}

# Or in pnpm-workspace.yaml
{
  "pnpm": {
    "overrides": {
      "package-name": "1.2.3"
    }
  }
}
```

### 6. Lock File Maintenance

**Clean lock files:**

```bash
# Remove node_modules and lock file
rm -rf node_modules pnpm-lock.yaml

# Reinstall from scratch
pnpm install

# Verify builds and tests
pnpm build && pnpm test
```

**Fix lock file issues:**

```bash
# Resolve conflicts (use theirs/ours)
git checkout --theirs pnpm-lock.yaml
pnpm install

# Validate lock file
pnpm install --frozen-lockfile
```

**Lock file best practices:**

- Always commit lock files
- Don't edit lock files manually
- Resolve conflicts by regenerating
- Use `--frozen-lockfile` in CI
- Keep lock files up to date

### 7. Package.json Organization

**Organize dependencies:**

```json
{
  "dependencies": {
    // Alphabetical order
    // Core framework first
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    // UI libraries
    "antd": "^5.0.0",
    // Utilities
    "lodash": "^4.17.21",
    // APIs
    "axios": "^1.0.0"
  },
  "devDependencies": {
    // Type definitions
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    // Build tools
    "vite": "^5.0.0",
    // Testing
    "vitest": "^1.0.0",
    // Linting
    "eslint": "^8.0.0"
  }
}
```

**Separate concerns:**

```json
{
  "dependencies": {
    // Production runtime dependencies only
  },
  "devDependencies": {
    // Development, testing, building
  },
  "peerDependencies": {
    // Expected to be provided by consumer
  },
  "optionalDependencies": {
    // Optional enhancements
  }
}
```

### 8. Dependency Report

Create `docs/cleanup-reports/DEPS_CLEANUP_$(date +%Y-%m-%d).md`:

```markdown
# Dependency Cleanup Report - [Date]

## Summary
- Removed X unused dependencies
- Updated Y outdated packages
- Fixed Z security vulnerabilities
- Reduced package count by N%
- Reduced install size by M MB

## Actions Taken

### Removed (Unused)
| Package | Version | Reason | Size Saved |
|---------|---------|--------|------------|
| foo | 1.2.3 | Not imported | 2.3 MB |
| bar | 4.5.6 | Replaced by baz | 1.1 MB |

### Updated
| Package | From | To | Changes | Risk |
|---------|------|-----|---------|------|
| react | 17.0.0 | 18.2.0 | Breaking: [link] | Medium |
| lodash | 4.17.20 | 4.17.21 | Security fix | Low |

### Security Fixes
| Vulnerability | Package | Severity | Fix |
|---------------|---------|----------|-----|
| CVE-2023-1234 | axios | High | Updated to 1.4.0 |

### Deduplicated
| Package | Before | After |
|---------|--------|-------|
| react | 3 versions | 1 version |
| lodash | 2 versions | 1 version |

## Before/After

### Package Count
- Total packages: 245 → 198 (-47)
- Dependencies: 45 → 38 (-7)
- DevDependencies: 200 → 160 (-40)

### Install Size
- Total: 523 MB → 412 MB (-111 MB, -21%)
- node_modules: 487 MB → 385 MB (-102 MB)

### Security
- Critical vulnerabilities: 2 → 0
- High vulnerabilities: 5 → 1
- Moderate vulnerabilities: 12 → 8

## Validation

### Tests
- ✅ Unit tests: 245/245 passing
- ✅ Integration tests: 45/45 passing
- ✅ E2E tests: 12/12 passing
- ✅ Coverage: 88% (maintained)

### Builds
- ✅ Development build: Success
- ✅ Production build: Success
- ✅ Type checking: 0 errors

### Performance
- Build time: 45s → 38s (-16%)
- Install time: 2m15s → 1m48s (-20%)

## Recommendations

### Immediate
- [ ] Monitor production for issues
- [ ] Update documentation for breaking changes
- [ ] Review bundle size in production

### Next Sprint
- [ ] Evaluate replacing [heavy-package] with lighter alternative
- [ ] Consider migrating from [deprecated-package] to [recommended-package]
- [ ] Set up automated dependency updates (Renovate/Dependabot)

### Long-term
- [ ] Monthly dependency audits
- [ ] Quarterly major version updates
- [ ] Bundle size monitoring in CI
```

---

## Execution Steps

Use TodoWrite to track progress:

1. **Analyze current state**
   - Run depcheck
   - Run npm outdated
   - Run npm audit
   - Check for duplicates
   - Document current metrics

2. **Remove unused dependencies**
   - Identify unused packages
   - Test removal (one at a time)
   - Commit successful removals
   - Document removals

3. **Update outdated packages**
   - Prioritize by security/importance
   - Update patch versions (safe)
   - Update minor versions (test)
   - Update major versions (careful)
   - Document updates

4. **Fix security vulnerabilities**
   - Audit for vulnerabilities
   - Update affected packages
   - Verify fixes
   - Document fixes

5. **Deduplicate dependencies**
   - Run npm dedupe
   - Resolve version conflicts
   - Test thoroughly
   - Document deduplication

6. **Clean lock files**
   - Remove node_modules
   - Remove lock file
   - Reinstall fresh
   - Verify builds

7. **Organize package.json**
   - Alphabetize dependencies
   - Group by category
   - Add comments if helpful
   - Format consistently

8. **Validate changes**
   - Run all tests
   - Run all builds
   - Check bundle size
   - Verify security audit

9. **Document cleanup**
   - Create dependency report
   - List all changes
   - Provide commit message
   - Recommend future actions

## Success Criteria

- [ ] All unused dependencies removed
- [ ] Critical security issues fixed
- [ ] Outdated packages updated (or documented why not)
- [ ] Dependencies deduplicated
- [ ] Lock files clean and valid
- [ ] All tests passing
- [ ] All builds succeeding
- [ ] Bundle size reduced or maintained
- [ ] Security audit clean
- [ ] Dependency report created

## Safety Rules

**NEVER:**
- Remove dependencies without testing
- Update all dependencies at once
- Ignore breaking changes
- Skip testing after updates
- Commit broken lock files

**ALWAYS:**
- Update one dependency at a time
- Run full test suite after changes
- Read changelogs for major updates
- Commit lock file with package.json
- Document breaking changes

## Output Format

Provide:
1. Dependency analysis summary
2. Table of removed packages
3. Table of updated packages
4. Security fix summary
5. Before/after metrics
6. Validation results
7. Recommendations
8. Git commit message

## Edge Cases

**If encountering:**
- **Peer dependency conflicts**: Use overrides or find compatible versions
- **Missing types**: Install @types/* packages separately
- **Build failures after update**: Rollback and investigate
- **Test failures**: Fix tests or rollback update
- **Breaking changes**: Document and update code accordingly

## Monorepo Considerations

**For Nx/pnpm workspaces:**

```bash
# Update all workspace packages
pnpm update --recursive

# Remove from specific workspace
pnpm --filter @workspace/app remove package

# Deduplicate across workspace
pnpm dedupe

# Audit entire workspace
pnpm audit --recursive
```

## Prevention Tips

**Include in report:**
- Set up Dependabot or Renovate for automated updates
- Add `pnpm audit` to CI pipeline
- Monitor bundle size in CI
- Regular dependency review (monthly)
- Use `pnpm dlx npx-check -u` for interactive updates
- Document dependency decisions in ADRs
