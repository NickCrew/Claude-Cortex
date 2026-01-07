# Reference: test-cleanup

# Clean up test directories and reports

You are tasked with organizing test files, cleaning up test reports, and improving test structure.

## Context

The user wants to maintain clean test directories by:
- Organizing test files into proper structure
- Removing generated test reports
- Consolidating test configurations
- Improving test discoverability
- Archiving obsolete tests

## Personas (Thinking Modes)
- **test-engineer**: Test organization, test categorization, test quality standards, fixture management
- **quality-engineer**: Test smell detection, coverage analysis, test health metrics
- **developer**: Test structure, import updates, test refactoring

## Delegation Protocol

**This command does NOT delegate** - Test cleanup is direct file operations and tool execution.

**Why no delegation**:
- ❌ Fast artifact removal (coverage reports, screenshots)
- ❌ Simple file reorganization (mv test files)
- ❌ Direct tool execution (grep for .skip, .only)
- ❌ Template-based documentation creation

**All work done directly**:
- Bash for removing test artifacts (rm -rf)
- Bash for reorganizing test files (mv, mkdir)
- Grep for finding test smells (.skip, .only, missing assertions)
- Write for creating tests/README.md
- TodoWrite for tracking cleanup steps

**Note**: Personas guide test organization thinking (test-engineer for structure, quality for smell detection, developer for safe refactoring).

## Tool Coordination
- **Bash**: Remove artifacts, reorganize files, create directories (direct)
- **Grep**: Find test smells and quality issues (direct)
- **Glob**: Find test files by pattern (direct)
- **Write**: Create test documentation (direct)
- **Edit**: Update .gitignore (direct)
- **TodoWrite**: Track multi-step cleanup process (direct)

## Task Requirements

### 1. Analysis Phase

**Identify test organization issues:**

**Test file locations:**
- Colocated tests: `src/**/*.test.ts`, `src/**/*.spec.ts`
- Separate tests: `tests/`, `__tests__/`, `test/`
- E2E tests: `e2e/`, `tests/e2e/`, `cypress/`, `playwright/`
- Performance tests: `perf/`, `tests/performance/`
- Integration tests: `tests/integration/`, `integration/`

**Generated test artifacts (REMOVE):**
- Coverage reports: `coverage/`, `htmlcov/`, `.nyc_output/`
- Test results: `test-results/`, `junit.xml`, `report.html`
- Screenshots: `tests/__screenshots__/`, `playwright-report/`
- Videos: `cypress/videos/`, `test-videos/`
- Traces: `playwright-traces/`, `test-traces/`
- Logs: `test-logs/`, `*.test.log`

**Test configuration:**
- Jest: `jest.config.js`, `jest.config.ts`
- Vitest: `vitest.config.ts`, `vitest.config.js`
- Playwright: `playwright.config.ts`
- Cypress: `cypress.config.ts`
- Other: `.mocharc.json`, `karma.conf.js`

### 2. Recommended Test Structure

**For unit and integration tests:**

```
tests/
  ├── unit/                   # Unit tests
  │   ├── components/        # UI component tests
  │   ├── services/          # Business logic tests
  │   ├── utils/             # Helper function tests
  │   └── hooks/             # Hook tests
  ├── integration/           # Integration tests
  │   ├── api/               # API integration tests
  │   ├── database/          # DB integration tests
  │   └── external/          # External service tests
  ├── fixtures/              # Test data and mocks
  │   ├── data/              # Mock data
  │   ├── mocks/             # Mock implementations
  │   └── factories/         # Test factories
  ├── helpers/               # Test utilities
  │   ├── setup.ts           # Test setup
  │   ├── teardown.ts        # Test teardown
  │   └── assertions.ts      # Custom matchers
  └── README.md              # Testing guide
```

**For E2E tests:**

```
tests/e2e/
  ├── specs/                 # Test specifications
  │   ├── auth/              # Authentication flows
  │   ├── user/              # User workflows
  │   └── admin/             # Admin workflows
  ├── fixtures/              # E2E test data
  ├── page-objects/          # Page object models
  └── README.md              # E2E testing guide
```

**For performance tests:**

```
tests/performance/
  ├── load/                  # Load tests
  ├── stress/                # Stress tests
  ├── spike/                 # Spike tests
  └── endurance/             # Endurance tests
```

### 3. Test File Organization

**Decision tree for test placement:**

```
Is it testing a single function/class?
├─ YES → Unit test (tests/unit/)
└─ NO → Is it testing multiple components?
    ├─ YES → Integration test (tests/integration/)
    └─ NO → Is it testing through UI?
        ├─ YES → E2E test (tests/e2e/)
        └─ NO → Is it testing performance?
            ├─ YES → Performance test (tests/performance/)
            └─ NO → Consult user
```

**Naming conventions:**

```
Unit tests:
- tests/unit/utils/string-utils.test.ts
- tests/unit/services/user-service.test.ts

Integration tests:
- tests/integration/api/user-api.test.ts
- tests/integration/database/user-repository.test.ts

E2E tests:
- tests/e2e/specs/auth/login.spec.ts
- tests/e2e/specs/user/profile-update.spec.ts

Performance tests:
- tests/performance/load/api-load.test.ts
- tests/performance/stress/database-stress.test.ts
```

### 4. Cleanup Actions

**Remove generated artifacts:**

```bash
# Coverage reports
rm -rf coverage/ htmlcov/ .nyc_output/

# Test results
rm -rf test-results/ junit.xml report.html

# E2E artifacts
rm -rf playwright-report/ test-results/
rm -rf cypress/videos/ cypress/screenshots/
rm -rf test-videos/ test-screenshots/

# Logs
rm -rf test-logs/ *.test.log
```

**Consolidate test configs:**

```bash
# Before (scattered)
jest.config.js
jest.config.unit.js
jest.config.integration.js
vitest.config.ts
playwright.config.ts

# After (organized)
tests/
  ├── config/
  │   ├── vitest.config.ts        # Main config
  │   ├── vitest.unit.config.ts   # Unit test config
  │   ├── vitest.int.config.ts    # Integration config
  │   └── playwright.config.ts     # E2E config
```

**Archive obsolete tests:**

```bash
# Tests for removed features
mkdir -p tests/archive/obsolete/
mv tests/unit/old-feature.test.ts tests/archive/obsolete/

# Skipped tests (>6 months)
mkdir -p tests/archive/skipped/
mv tests/unit/flaky-test.test.ts tests/archive/skipped/

# Document reason
echo "Archived: Feature removed in v2.0" > tests/archive/obsolete/old-feature.README.md
```

### 5. Test Quality Improvements

**Identify test smells:**

```bash
# Find skipped tests
grep -r "it.skip\|test.skip\|describe.skip" tests/

# Find focused tests (shouldn't be committed)
grep -r "it.only\|test.only\|describe.only" tests/

# Find tests without assertions
grep -L "expect\|assert" tests/**/*.test.ts

# Find large test files (>500 lines)
find tests/ -name "*.test.ts" -exec wc -l {} \; | sort -rn | head -10

# Find duplicate test descriptions
grep -rh "it('\|test('" tests/ | sort | uniq -d
```

**Report findings:**

```markdown
## Test Quality Issues

### Skipped Tests (Action Required)
- tests/unit/foo.test.ts:45 - Skipped for 8 months
- tests/integration/bar.test.ts:78 - Skipped for 3 months

### Focused Tests (Should Not Commit)
- tests/unit/baz.test.ts:23 - it.only found
- tests/e2e/qux.spec.ts:56 - test.only found

### Tests Without Assertions
- tests/unit/empty.test.ts - No expect() calls

### Large Test Files (Consider Splitting)
- tests/unit/huge.test.ts - 847 lines
- tests/integration/massive.test.ts - 623 lines
```

### 6. .gitignore Update

**Add test artifact patterns:**

```gitignore
# Test coverage
coverage/
.nyc_output/
htmlcov/
.coverage
*.cover

# Test results
test-results/
junit.xml
test-report.html
report.html

# E2E artifacts
playwright-report/
test-results-*/
cypress/videos/
cypress/screenshots/
test-videos/
test-screenshots/
playwright-traces/

# Test logs
test-logs/
*.test.log
test-output.txt

# Test cache
.vitest/
.jest/
.pytest_cache/
__pycache__/

# Test temp files
tests/tmp/
tests/temp/
tests/.cache/
```

### 7. Documentation

Create `tests/README.md`:

```markdown
# Testing Guide

## Test Structure

- `unit/` - Unit tests (isolated, fast)
- `integration/` - Integration tests (multiple components)
- `e2e/` - End-to-end tests (full workflows)
- `performance/` - Performance and load tests
- `fixtures/` - Test data and mocks
- `helpers/` - Test utilities

## Running Tests

```bash
# All tests
npm test

# Unit tests only
npm run test:unit

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## Writing Tests

See [Testing Guide](../docs/development/testing-guide.md)

## Test Naming

- Unit: `tests/unit/path/file.test.ts`
- Integration: `tests/integration/area/feature.test.ts`
- E2E: `tests/e2e/specs/workflow/action.spec.ts`
```

Create cleanup report at `docs/cleanup-reports/TEST_CLEANUP_$(date +%Y-%m-%d).md`.

## Execution Steps

Use TodoWrite to track progress:

1. **Analyze test structure**
   - Identify all test files
   - Check current organization
   - Find generated artifacts
   - Assess test quality

2. **Remove generated artifacts**
   - Delete coverage reports
   - Delete test results
   - Delete E2E artifacts
   - Delete test logs

3. **Reorganize test files**
   - Create standard structure
   - Move unit tests
   - Move integration tests
   - Move E2E tests
   - Update imports

4. **Consolidate configurations**
   - Move configs to tests/config/
   - Update references
   - Deduplicate settings

5. **Archive obsolete tests**
   - Identify removed features
   - Archive skipped tests (>6mo)
   - Document reasons

6. **Identify quality issues**
   - Find skipped tests
   - Find focused tests
   - Find tests without assertions
   - Find large test files

7. **Update .gitignore**
   - Add artifact patterns
   - Add cache patterns
   - Add temp patterns

8. **Create documentation**
   - Create tests/README.md
   - Create cleanup report
   - Update main testing guide

9. **Validate**
   - Run all tests
   - Verify passing
   - Check coverage
   - Verify imports

## Success Criteria

- [ ] Standard test structure implemented
- [ ] All generated artifacts removed
- [ ] Test files properly categorized
- [ ] Test configs consolidated
- [ ] Obsolete tests archived
- [ ] Quality issues identified
- [ ] .gitignore updated
- [ ] tests/README.md created
- [ ] All tests still passing
- [ ] Cleanup report created

## Safety Rules

**NEVER:**
- Remove test files without checking git history
- Delete tests for active features
- Move tests without updating imports
- Skip running tests after reorganization

**ALWAYS:**
- Run tests before cleanup
- Run tests after cleanup
- Use git mv for tracked files
- Document archived tests
- Keep test coverage stable

## Output Format

Provide:
1. Test structure analysis (before/after)
2. List of removed artifacts (space saved)
3. List of reorganized tests
4. Quality issues found
5. Archived tests with reasons
6. .gitignore updates
7. Validation results
8. Git commit message

## Edge Cases

**If encountering:**
- **Failing tests**: Stop and ask user
- **Unknown test framework**: Ask for guidance
- **Mixed test styles**: Propose standardization
- **Tests in multiple locations**: Consolidate with approval
- **Custom test runners**: Preserve configuration

## Common Patterns

**Jest to Vitest migration:**
```bash
# Update imports
find tests/ -name "*.test.ts" -exec sed -i '' 's/@jest\/globals/vitest/g' {} \;

# Update test functions
find tests/ -name "*.test.ts" -exec sed -i '' 's/test(/it(/g' {} \;
```

**Monorepo test cleanup:**
```bash
# Clean all apps
for app in apps/*; do
  rm -rf $app/coverage $app/test-results
done

# Standardize structure
for app in apps/*; do
  mkdir -p $app/tests/{unit,integration,e2e}
done
```

## Prevention Tips

**Include in report:**
- Add pre-commit hooks to prevent committing .only
- Configure CI to fail on skipped tests
- Set coverage thresholds
- Regular test review (quarterly)
- Monitor test execution time
- Refactor large test files
