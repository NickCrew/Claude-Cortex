# Reference: improve

# /quality:improve - Code Improvement

## Triggers
- Code quality enhancement and refactoring requests
- Performance optimization and bottleneck resolution needs
- Maintainability improvements and technical debt reduction
- Best practices application and coding standards enforcement

## Usage
```
/quality:improve [target] [--type quality|performance|maintainability|style] [--safe] [--interactive]
```

## Behavioral Flow
1. **Analyze**: Examine codebase for improvement opportunities and quality issues
2. **Plan**: Choose improvement approach and activate relevant personas for expertise
3. **Execute**: Apply systematic improvements with domain-specific best practices
4. **Validate**: Ensure improvements preserve functionality and meet quality standards
5. **Document**: Generate improvement summary and recommendations for future work

Key behaviors:
- Multi-persona coordination (architect, performance, quality, security) based on improvement type
- Framework-specific optimization via Context7 integration for best practices
- Systematic analysis via Sequential MCP for complex multi-component improvements
- Safe refactoring with comprehensive validation and rollback capabilities

## MCP Integration
- **Sequential MCP**: Auto-activated for complex multi-step improvement analysis and planning
- **Context7 MCP**: Framework-specific best practices and optimization patterns
- **Persona Coordination**: Architect (structure), Performance (speed), Quality (maintainability), Security (safety)

## Personas (Thinking Modes)
- **architect**: System structure, design patterns, architectural improvements
- **performance-engineer**: Bottleneck identification, optimization strategies, efficiency focus
- **quality-engineer**: Code quality standards, maintainability, best practices
- **security-specialist**: Security patterns, vulnerability prevention, secure coding

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large-scale improvements (>5 files)
- ✅ Multi-domain improvements (quality + performance + security)
- ✅ Complex refactoring requiring analysis
- ✅ Performance optimization needing profiling
- ✅ Interactive improvement mode (user decisions needed)

**Available subagents**:
- **Explore**: Codebase analysis, improvement opportunity identification
- **general-purpose**: Apply improvements, refactoring, optimization implementation
- **code-reviewer**: Validate improvements, ensure quality preservation

**Delegation strategy for systematic improvements**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze codebase for improvement opportunities</description>
  <prompt>
    Identify improvements in: [target]
    Focus: [quality|performance|maintainability|security]
    Find: Technical debt, bottlenecks, code smells, security issues
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Apply systematic improvements</description>
  <prompt>
    Apply improvements with [persona] guidance:
    - Safe refactoring
    - Best practices
    - Framework-specific optimizations (Context7)
    Mode: [--safe|--interactive]
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Validate improvements</description>
  <prompt>
    Verify improvements:
    - Functionality preserved
    - Quality enhanced
    - No regressions introduced
    - Standards compliance
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple style fixes (1-2 files)
- ❌ Trivial refactoring
- ❌ Quick maintainability tweaks

## Tool Coordination
- **Task tool**: Delegates to Explore + general-purpose + code-reviewer for complex improvements
- **Read/Grep/Glob**: Code analysis (direct for simple, by subagent for complex)
- **Edit/MultiEdit**: Code modifications (direct for simple, by subagent for complex)
- **TodoWrite**: Progress tracking for multi-file operations

## Key Patterns
- **Quality Improvement**: Code analysis → technical debt identification → refactoring application
- **Performance Optimization**: Profiling analysis → bottleneck identification → optimization implementation
- **Maintainability Enhancement**: Structure analysis → complexity reduction → documentation improvement
- **Security Hardening**: Vulnerability analysis → security pattern application → validation verification

## Examples

### Code Quality Enhancement
```
/quality:improve src/ --type quality --safe
# Systematic quality analysis with safe refactoring application
# Improves code structure, reduces technical debt, enhances readability
```

### Performance Optimization
```
/quality:improve api-endpoints --type performance --interactive
# Performance persona analyzes bottlenecks and optimization opportunities
# Interactive guidance for complex performance improvement decisions
```

### Maintainability Improvements
```
/quality:improve legacy-modules --type maintainability --preview
# Architect persona analyzes structure and suggests maintainability improvements
# Preview mode shows changes before application for review
```

### Security Hardening
```
/quality:improve auth-service --type security --validate
# Security persona identifies vulnerabilities and applies security patterns
# Comprehensive validation ensures security improvements are effective
```

## Boundaries

**Will:**
- Apply systematic improvements with domain-specific expertise and validation
- Provide comprehensive analysis with multi-persona coordination and best practices
- Execute safe refactoring with rollback capabilities and quality preservation

**Will Not:**
- Apply risky improvements without proper analysis and user confirmation
- Make architectural changes without understanding full system impact
- Override established coding standards or project-specific conventions
