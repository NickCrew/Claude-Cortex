# Reference: test

# /dev:test - Testing and Quality Assurance

## Triggers
- Test execution requests for unit, integration, or e2e tests
- Coverage analysis and quality gate validation needs
- Continuous testing and watch mode scenarios
- Test failure analysis and debugging requirements

## Usage
```
/dev:test [target] [--type unit|integration|e2e|all] [--coverage] [--watch] [--fix]
```

## Behavioral Flow
1. **Discover**: Categorize available tests using runner patterns and conventions
2. **Configure**: Set up appropriate test environment and execution parameters
3. **Execute**: Run tests with monitoring and real-time progress tracking
4. **Analyze**: Generate coverage reports and failure diagnostics
5. **Report**: Provide actionable recommendations and quality metrics

Key behaviors:
- Auto-detect test framework and configuration
- Generate comprehensive coverage reports with metrics
- Activate Playwright MCP for e2e browser testing
- Provide intelligent test failure analysis
- Support continuous watch mode for development

## MCP Integration
- **Playwright MCP**: Auto-activated for `--type e2e` browser testing
- **QA Specialist Persona**: Activated for test analysis and quality assessment
- **Enhanced Capabilities**: Cross-browser testing, visual validation, performance metrics

## Personas (Thinking Modes)
- **qa-specialist**: Quality standards, test strategy, comprehensive coverage mindset
- **developer**: Code understanding, debugging, practical test scenarios

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Test failure analysis (--fix flag with complex failures)
- ✅ Test generation (discovered gaps need new tests)
- ✅ E2E testing with deep validation
- ✅ Coverage gap analysis (>20% uncovered)

**Available subagents**:
- **general-purpose**: Test failure diagnosis and fixes
- **test-automator**: Generate missing tests for coverage gaps

**Delegation strategy for test issues**:
```xml
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Analyze and fix test failures</description>
  <prompt>
    Tests failing. Diagnose and fix:
    - Parse test output
    - Identify failure patterns
    - Apply appropriate fixes
    - Re-run tests
    - Verify resolution
    QA specialist thinking for quality.
  </prompt>
</invoke>
```

**Delegation for coverage gaps**:
```xml
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate tests for uncovered code</description>
  <prompt>
    Coverage below target. Generate tests for:
    - Identified uncovered code paths
    - Edge cases
    - Error scenarios
    Target: [coverage-target]%
  </prompt>
</invoke>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple test execution (tests passing)
- ❌ Watch mode (continuous execution)
- ❌ Quick coverage report generation

## Tool Coordination
- **Task tool**: Delegates for complex failure analysis or test generation
- **Bash**: Test execution (direct)
- **Glob**: Test discovery (direct)
- **Grep**: Result parsing (direct for simple, by subagent for complex)
- **Write**: Coverage reports (direct)

## Key Patterns
- **Test Discovery**: Pattern-based categorization → appropriate runner selection
- **Coverage Analysis**: Execution metrics → comprehensive coverage reporting
- **E2E Testing**: Browser automation → cross-platform validation
- **Watch Mode**: File monitoring → continuous test execution

## Examples

### Basic Test Execution
```
/dev:test
# Discovers and runs all tests with standard configuration
# Generates pass/fail summary and basic coverage
```

### Targeted Coverage Analysis
```
/dev:test src/components --type unit --coverage
# Unit tests for specific directory with detailed coverage metrics
```

### Browser Testing
```
/dev:test --type e2e
# Activates Playwright MCP for comprehensive browser testing
# Cross-browser compatibility and visual validation
```

### Development Watch Mode
```
/dev:test --watch --fix
# Continuous testing with automatic simple failure fixes
# Real-time feedback during development
```

## Boundaries

**Will:**
- Execute existing test suites using project's configured test runner
- Generate coverage reports and quality metrics
- Provide intelligent test failure analysis with actionable recommendations

**Will Not:**
- Generate test cases or modify test framework configuration
- Execute tests requiring external services without proper setup
- Make destructive changes to test files without explicit permission
