---
name: code-review
description: Comprehensive code quality review and analysis
category: development
agents: [code-reviewer, security-auditor]
---

# /dev:code-review - Comprehensive Code Review

## Purpose
Perform systematic code review focusing on quality, security, and best practices.

## Triggers
- Pull request reviews
- Pre-commit code quality checks
- Refactoring validation
- Manual code review requests

## Usage
```
/dev:code-review [path] [--focus quality|security|performance|all]
```

## Review Process

### 1. Code Quality Analysis
- Identify code smells and anti-patterns
- Check naming conventions and consistency
- Review error handling patterns
- Assess code readability and maintainability
- Find unused imports, variables, or dead code

### 2. Security Assessment
- Scan for common vulnerabilities (OWASP Top 10)
- Check for hardcoded secrets or credentials
- Review authentication and authorization logic
- Examine input validation and sanitization
- Identify security risks in dependencies

### 3. Performance Review
- Identify potential performance bottlenecks
- Check for inefficient algorithms or queries
- Review memory usage patterns
- Analyze bundle size and optimization opportunities

### 4. Architecture Evaluation
- Evaluate code organization and separation of concerns
- Check for proper abstraction and modularity
- Review dependency management and coupling
- Assess scalability and maintainability

## Output Format

**Summary**: Overall code health score and key findings

**Critical Issues**: Must-fix problems (blocking)
**Important Issues**: Should-fix problems (high priority)
**Suggestions**: Nice-to-have improvements

**Best Practices**: Recommendations for improvement

## Agents Used
- `code-reviewer`: Primary code quality analysis
- `security-auditor`: Security-focused review (when --focus security or all)

## Example
```
/dev:code-review src/auth --focus security
```