---
name: generate-tests
description: Generate comprehensive test suite with high coverage
category: testing
agents: [test-automator, quality-engineer]
---

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

## Agents Used
- `test-automator`: Primary test generation
- `quality-engineer`: Test quality validation

## Example
```
/test:generate-tests src/api --type integration --coverage-target 90
```