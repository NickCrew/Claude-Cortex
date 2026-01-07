# Reference: generate-tests

# /test:generate-tests - Test Generation

## Purpose
Automatically generate comprehensive test suites for code coverage and quality assurance.

## Triggers
- New feature implementation
- Low test coverage areas
- Regression testing needs
- API endpoint testing

## Usage
```
/test:generate-tests [path] [--type unit|integration|e2e|all] [--coverage-target 80]
```

## Test Generation Process

### 1. Code Analysis
- Analyze code structure and dependencies
- Identify testable units and edge cases
- Map code paths and decision points
- Determine test requirements

### 2. Test Creation
- Generate unit tests for core logic
- Create integration tests for component interactions
- Build e2e tests for user workflows
- Add edge case and error scenario tests

### 3. Coverage Analysis
- Measure code coverage percentage
- Identify uncovered code paths
- Generate coverage reports
- Suggest additional test cases

### 4. Test Quality
- Ensure test independence and isolation
- Implement proper setup and teardown
- Add descriptive test names and documentation
- Follow testing best practices

## Test Types

**Unit Tests**
- Individual function/method testing
- Mocked dependencies
- Fast execution
- High coverage of business logic

**Integration Tests**
- Component interaction testing
- Database and API integration
- Service communication
- Realistic scenarios

**End-to-End Tests**
- User workflow testing
- Full system integration
- Browser automation (if web app)
- Production-like environment

## Coverage Targets
- Unit tests: 80%+ coverage
- Integration tests: Key workflows covered
- E2e tests: Critical user paths validated

## Output
- Generated test files in appropriate directories
- Coverage report with metrics
- Test execution commands
- Suggested improvements for uncovered areas

## Personas (Thinking Modes)
- **qa-specialist**: Quality standards, testing strategies, comprehensive coverage mindset
- **developer**: Understand code structure, realistic test scenarios, practical test cases

## Delegation Protocol

**This command ALWAYS delegates** - test generation is complex work requiring specialized analysis.

**When triggered**:
- ✅ Test generation for any non-trivial code (>1 function)
- ✅ Coverage analysis needed
- ✅ Multiple test types required
- ✅ Quality validation needed

**Subagents launched** (via Task tool):
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate test suite for [path]</description>
  <prompt>
    Analyze code structure and generate comprehensive tests:
    - Type: [unit|integration|e2e|all]
    - Coverage target: [percentage]
    - Include edge cases and error scenarios
    - Follow testing best practices
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>quality-engineer</subagent_type>
  <description>Validate test quality</description>
  <prompt>
    Review generated tests for:
    - Test independence and isolation
    - Proper setup/teardown
    - Descriptive naming
    - Coverage completeness
  </prompt>
</invoke>
</function_calls>
```

**Tool Coordination**:
- **Task tool**: Launches test-automator and quality-engineer subagents
- **Read/Grep/Glob**: Code analysis (done by subagents)
- **Write**: Test file creation (done by subagents)

## Example
```
/test:generate-tests src/api --type integration --coverage-target 90
```
