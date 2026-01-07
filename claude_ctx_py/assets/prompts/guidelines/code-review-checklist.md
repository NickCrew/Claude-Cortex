---
name: Code Review Checklist
description: Comprehensive checklist for reviewing pull requests and code changes
tokens: 350
---

# Code Review Checklist

Use this checklist when reviewing code changes to ensure quality and consistency.

## Correctness
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is appropriate
- [ ] No obvious bugs or regressions
- [ ] Unit tests cover new functionality

## Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation on user data
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (proper escaping)
- [ ] Authentication/authorization checks in place

## Performance
- [ ] No N+1 queries or obvious performance issues
- [ ] Appropriate use of caching where needed
- [ ] Large data sets are paginated
- [ ] Async operations where appropriate

## Code Quality
- [ ] Follows project conventions and style guide
- [ ] Names are descriptive and consistent
- [ ] Functions are focused (single responsibility)
- [ ] No dead code or commented-out blocks
- [ ] Documentation for public APIs

## Architecture
- [ ] Changes are in the right location
- [ ] No circular dependencies introduced
- [ ] Abstractions are appropriate (not over/under-engineered)
- [ ] Compatible with existing patterns

## Testing
- [ ] Tests are meaningful (not trivial assertions)
- [ ] Edge cases are covered
- [ ] Tests are isolated and repeatable
- [ ] Integration tests for API changes
