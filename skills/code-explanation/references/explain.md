# Reference: explain

# /analyze:explain - Code and Concept Explanation

## Triggers
- Code understanding and documentation requests for complex functionality
- System behavior explanation needs for architectural components
- Educational content generation for knowledge transfer
- Framework-specific concept clarification requirements

## Usage
```
/analyze:explain [target] [--level basic|intermediate|advanced] [--format text|examples|interactive] [--context domain]
```

## Behavioral Flow
1. **Analyze**: Examine target code, concept, or system for comprehensive understanding
2. **Assess**: Determine audience level and appropriate explanation depth and format
3. **Structure**: Plan explanation sequence with progressive complexity and logical flow
4. **Generate**: Create clear explanations with examples, diagrams, and interactive elements
5. **Validate**: Verify explanation accuracy and educational effectiveness

Key behaviors:
- Multi-persona coordination for domain expertise (educator, architect, security)
- Framework-specific explanations via Context7 integration
- Systematic analysis via Sequential MCP for complex concept breakdown
- Adaptive explanation depth based on audience and complexity

## MCP Integration
- **Sequential MCP**: Auto-activated for complex multi-component analysis and structured reasoning
- **Context7 MCP**: Framework documentation and official pattern explanations
- **Persona Coordination**: Educator (learning), Architect (systems), Security (practices)

## Personas (Thinking Modes)
- **educator**: Learning optimization, progressive complexity, clear communication
- **architect**: System design understanding, component relationships, architectural patterns
- **security-specialist**: Security concepts, best practices, threat awareness

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large system explanation (>10 components)
- ✅ Multi-part educational content
- ✅ Requires deep codebase exploration
- ✅ Interactive format with examples

**Available subagents**:
- **Explore**: Codebase analysis for explanation context
- **general-purpose**: Generate structured explanations, examples, documentation

**Delegation strategy for comprehensive explanation**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze code for explanation</description>
  <prompt>
    Explore target for explanation:
    - Component structure
    - Relationships
    - Patterns used
    - Dependencies
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Generate explanation with examples</description>
  <prompt>
    Create explanation for: [target]
    - Level: [basic|intermediate|advanced]
    - Format: [text|examples|interactive]
    - Context: [domain]
    Adopt educator + [architect|security] persona.
    Use Context7 for framework concepts.
    Use Sequential for complex breakdowns.
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple code explanation (single function, basic level)
- ❌ Quick concept clarification
- ❌ Framework syntax lookup

## Tool Coordination
- **Task tool**: Delegates for large system or multi-part explanations
- **Read/Grep/Glob**: Code analysis (direct for simple, by subagent for complex)
- **Write**: Explanation documentation (direct for simple, by subagent for complex)
- **TodoWrite**: Multi-part tracking (when needed)
- **Context7 MCP**: Framework-specific documentation
- **Sequential MCP**: Structured explanation reasoning

## Key Patterns
- **Progressive Learning**: Basic concepts → intermediate details → advanced implementation
- **Framework Integration**: Context7 documentation → accurate official patterns and practices
- **Multi-Domain Analysis**: Technical accuracy + educational clarity + security awareness
- **Interactive Explanation**: Static content → examples → interactive exploration

## Examples

### Basic Code Explanation
```
/analyze:explain authentication.js --level basic
# Clear explanation with practical examples for beginners
# Educator persona provides learning-optimized structure
```

### Framework Concept Explanation
```
/analyze:explain react-hooks --level intermediate --context react
# Context7 integration for official React documentation patterns
# Structured explanation with progressive complexity
```

### System Architecture Explanation
```
/analyze:explain microservices-system --level advanced --format interactive
# Architect persona explains system design and patterns
# Interactive exploration with Sequential analysis breakdown
```

### Security Concept Explanation
```
/analyze:explain jwt-authentication --context security --level basic
# Security persona explains authentication concepts and best practices
# Framework-agnostic security principles with practical examples
```

## Boundaries

**Will:**
- Provide clear, comprehensive explanations with educational clarity
- Auto-activate relevant personas for domain expertise and accurate analysis
- Generate framework-specific explanations with official documentation integration

**Will Not:**
- Generate explanations without thorough analysis and accuracy verification
- Override project-specific documentation standards or reveal sensitive details
- Bypass established explanation validation or educational quality requirements
