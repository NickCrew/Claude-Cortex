# Reference: code-review

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

## Personas (Thinking Modes)
- **quality-engineer**: Code quality standards, best practices, maintainability focus
- **security-specialist**: Security-first mindset, threat awareness, vulnerability prevention

## Delegation Protocol

**This command ALWAYS delegates** - code review requires specialized expertise.

**When triggered**:
- ✅ Any code review request (PR review, pre-commit, manual review)
- ✅ All focus areas (quality, security, performance, architecture)

**Delegation strategy**:

**For general quality review**:
```xml
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review code quality for [path]</description>
  <prompt>
    Perform comprehensive code review focusing on:
    - Code quality and anti-patterns
    - Best practices compliance
    - Performance considerations
    - Architecture evaluation
    Provide prioritized findings with severity levels.
  </prompt>
</invoke>
```

**For security-focused review** (--focus security or all):
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review code quality</description>
  <prompt>Quality and architecture review...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>security-auditor</subagent_type>
  <description>Security assessment</description>
  <prompt>
    Security-focused review:
    - OWASP Top 10 vulnerabilities
    - Authentication/authorization issues
    - Input validation
    - Secret scanning
    Provide security risk assessment.
  </prompt>
</invoke>
</function_calls>
```

**Tool Coordination**:
- **Task tool**: Launches code-reviewer and/or security-auditor subagents
- **Read/Grep**: Code analysis (done by subagents)
- **TodoWrite**: Track review findings (if extensive)

## Example
```
/dev:code-review src/auth --focus security
```
