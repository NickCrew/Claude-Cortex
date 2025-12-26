# Reference: implement

# /dev:implement - Feature Implementation

> **Context Framework Note**: This behavioral instruction activates when Claude Code users type `/dev:implement` patterns. It guides Claude to coordinate specialist personas and MCP tools for comprehensive implementation.

## Triggers
- Feature development requests for components, APIs, or complete functionality
- Code implementation needs with framework-specific requirements
- Multi-domain development requiring coordinated expertise
- Implementation projects requiring testing and validation integration

## Context Trigger Pattern
```
/dev:implement [feature-description] [--type component|api|service|feature] [--framework react|vue|express] [--safe] [--with-tests]
```
**Usage**: Type this in Claude Code conversation to activate implementation behavioral mode with coordinated expertise and systematic development approach.

## Behavioral Flow
1. **Analyze**: Examine implementation requirements and detect technology context
2. **Plan**: Choose approach and activate relevant personas for domain expertise
3. **Generate**: Create implementation code with framework-specific best practices
4. **Validate**: Apply security and quality validation throughout development
5. **Integrate**: Update documentation and provide testing recommendations

Key behaviors:
- Context-based persona activation (architect, frontend, backend, security, qa)
- Framework-specific implementation via Context7 and Magic MCP integration
- Systematic multi-component coordination via Sequential MCP
- Comprehensive testing integration with Playwright for validation

## MCP Integration
- **Context7 MCP**: Framework patterns and official documentation for React, Vue, Angular, Express
- **Magic MCP**: Auto-activated for UI component generation and design system integration
- **Sequential MCP**: Complex multi-step analysis and implementation planning
- **Playwright MCP**: Testing validation and quality assurance integration

## Personas (Thinking Modes)
Context-based activation guides Claude's domain expertise:
- **architect**: System design, component relationships, scalability considerations
- **frontend**: UI/UX focus, accessibility, responsive design, user experience
- **backend**: API design, data modeling, business logic, performance optimization
- **security**: Threat modeling, secure coding practices, vulnerability prevention
- **qa-specialist**: Quality standards, testing strategies, edge case consideration

*Note: Personas guide thinking. For actual delegation, see Delegation Protocol below.*

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Feature spans >3 files or >3 domains (UI + API + tests)
- ✅ Complex implementation requiring >5 steps
- ✅ Need parallel work (implementation + tests + docs)
- ✅ Large-scale refactoring or system changes
- ✅ User wants progress visibility

**Available subagents**:
- **general-purpose**: Primary implementation work, feature development
- **code-reviewer**: Quality/security analysis, best practices validation
- **test-automator**: Test generation, coverage analysis
- **Explore**: Codebase analysis to understand existing patterns (when needed)

**Delegation strategy for features**:
```xml
<!-- For complex features, launch parallel workstreams -->
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement feature X</description>
  <prompt>Build feature with [persona] guidance...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate tests for feature X</description>
  <prompt>Create comprehensive test suite...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review feature X</description>
  <prompt>Quality and security review...</prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple component (single file, <100 lines)
- ❌ Trivial changes (typo fixes, small refactors)
- ❌ Quick additions (<5 minute work)

## Tool Coordination
- **Task tool**: Delegation mechanism for complex features - launches subagents for parallel work
- **Write/Edit/MultiEdit**: Direct code generation for simple implementations
- **Read/Grep/Glob**: Project analysis and pattern detection for consistency
- **TodoWrite**: Progress tracking for multi-step implementations
- **MCP servers**: Context7 (framework docs), Magic (UI generation), Playwright (testing)

## Key Patterns
- **Context Detection**: Framework/tech stack → appropriate persona and MCP activation
- **Implementation Flow**: Requirements → code generation → validation → integration
- **Multi-Persona Coordination**: Frontend + Backend + Security → comprehensive solutions
- **Quality Integration**: Implementation → testing → documentation → validation

## Examples

### React Component Implementation
```
/dev:implement user profile component --type component --framework react
# Magic MCP generates UI component with design system integration
# Frontend persona ensures best practices and accessibility
```

### API Service Implementation
```
/dev:implement user authentication API --type api --safe --with-tests
# Backend persona handles server-side logic and data processing
# Security persona ensures authentication best practices
```

### Full-Stack Feature
```
/dev:implement payment processing system --type feature --with-tests
# Multi-persona coordination: architect, frontend, backend, security
# Sequential MCP breaks down complex implementation steps
```

### Framework-Specific Implementation
```
/dev:implement dashboard widget --framework vue
# Context7 MCP provides Vue-specific patterns and documentation
# Framework-appropriate implementation with official best practices
```

## Boundaries

**Will:**
- Implement features with intelligent persona activation and MCP coordination
- Apply framework-specific best practices and security validation
- Provide comprehensive implementation with testing and documentation integration

**Will Not:**
- Make architectural decisions without appropriate persona consultation
- Implement features conflicting with security policies or architectural constraints
- Override user-specified safety constraints or bypass quality gates
