# Reference: generate

# /docs:generate - Focused Documentation Generation

## Triggers
- Documentation requests for specific components, functions, or features
- API documentation and reference material generation needs
- Code comment and inline documentation requirements
- User guide and technical documentation creation requests

## Usage
```
/docs:generate [target] [--type inline|external|api|guide] [--style brief|detailed]
```

## Behavioral Flow
1. **Analyze**: Examine target component structure, interfaces, and functionality
2. **Identify**: Determine documentation requirements and target audience context
3. **Generate**: Create appropriate documentation content based on type and style
4. **Format**: Apply consistent structure and organizational patterns
5. **Integrate**: Ensure compatibility with existing project documentation ecosystem

Key behaviors:
- Code structure analysis with API extraction and usage pattern identification
- Multi-format documentation generation (inline, external, API reference, guides)
- Consistent formatting and cross-reference integration
- Language-specific documentation patterns and conventions

## Personas (Thinking Modes)
- **technical-writer**: Clear communication, audience-appropriate language, comprehensive coverage
- **developer**: Code understanding, practical examples, implementation focus

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ API documentation (>5 endpoints or complex interfaces)
- ✅ Multi-component documentation projects
- ✅ Comprehensive user guides requiring >10 pages
- ✅ Documentation requiring deep code analysis

**Available subagents**:
- **technical-writer**: User guides, tutorials, explanatory documentation
- **api-documenter**: API reference, endpoint documentation, schemas

**Delegation strategy for API docs**:
```xml
<invoke name="Task">
  <subagent_type>api-documenter</subagent_type>
  <description>Generate API documentation for [path]</description>
  <prompt>
    Create comprehensive API documentation:
    - Endpoint descriptions
    - Request/response schemas
    - Authentication requirements
    - Usage examples
    - Error responses
    Style: [brief|detailed]
  </prompt>
</invoke>
```

**Delegation strategy for user guides**:
```xml
<invoke name="Task">
  <subagent_type>technical-writer</subagent_type>
  <description>Generate user guide for [feature]</description>
  <prompt>
    Create user-focused documentation:
    - Feature overview
    - Step-by-step tutorials
    - Code examples
    - Common use cases
    - Troubleshooting
  </prompt>
</invoke>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple inline comments (single file, <50 lines)
- ❌ Basic JSDoc/docstring generation
- ❌ Quick README updates

## Tool Coordination
- **Task tool**: Delegates to technical-writer or api-documenter for complex docs
- **Read**: Component analysis (direct or by subagent)
- **Grep**: Reference extraction (direct or by subagent)
- **Write**: Documentation file creation (direct for simple, by subagent for complex)
- **Glob**: Multi-file coordination

## Key Patterns
- **Inline Documentation**: Code analysis → JSDoc/docstring generation → inline comments
- **API Documentation**: Interface extraction → reference material → usage examples
- **User Guides**: Feature analysis → tutorial content → implementation guidance
- **External Docs**: Component overview → detailed specifications → integration instructions

## Examples

### Inline Code Documentation
```
/docs:generate src/auth/login.js --type inline
# Generates JSDoc comments with parameter and return descriptions
# Adds comprehensive inline documentation for functions and classes
```

### API Reference Generation
```
/docs:generate src/api --type api --style detailed
# Creates comprehensive API documentation with endpoints and schemas
# Generates usage examples and integration guidelines
```

### User Guide Creation
```
/docs:generate payment-module --type guide --style brief
# Creates user-focused documentation with practical examples
# Focuses on implementation patterns and common use cases
```

### Component Documentation
```
/docs:generate components/ --type external
# Generates external documentation files for component library
# Includes props, usage examples, and integration patterns
```

## Boundaries

**Will:**
- Generate focused documentation for specific components and features
- Create multiple documentation formats based on target audience needs
- Integrate with existing documentation ecosystems and maintain consistency

**Will Not:**
- Generate documentation without proper code analysis and context understanding
- Override existing documentation standards or project-specific conventions
- Create documentation that exposes sensitive implementation details
