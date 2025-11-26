---
name: cleanup
description: "Systematically clean up code, remove dead code, and optimize project structure"
category: workflow
complexity: standard
mcp-servers: [sequential, context7]
personas: [architect, quality, security]
subagents: [general-purpose, code-reviewer, Explore]
---

# /quality:cleanup - Code and Project Cleanup

## Personas (Thinking Modes)
- **architect**: System-wide impact analysis, structural improvements, dependency management
- **quality**: Code quality standards, technical debt assessment, cleanup validation
- **security**: Security implications of changes, safe removal verification

## Delegation Protocol

**This command CONDITIONALLY delegates** - Based on cleanup scope and complexity.

**When to delegate** (use Task tool):
- ✅ Large codebase cleanup (>20 files affected)
- ✅ Complex dead code analysis (requires deep import tracing)
- ✅ Multi-domain cleanup (code + imports + files)
- ✅ Aggressive cleanup mode (needs thorough validation)

**Available subagents**:
- **Explore**: Analyze codebase for dead code and unused imports
- **general-purpose**: Execute systematic cleanup with validation
- **code-reviewer**: Validate cleanup safety and quality improvement

**Delegation strategy for comprehensive cleanup**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze codebase for cleanup opportunities</description>
  <prompt>
    Explore for dead code and cleanup:
    - Unused imports and exports
    - Dead code files
    - Optimization opportunities
    Thoroughness: medium
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Execute systematic cleanup</description>
  <prompt>
    Apply cleanup based on analysis:
    - Remove dead code safely
    - Optimize imports
    - Improve structure
    - Validate with tests
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Validate cleanup quality</description>
  <prompt>
    Review cleanup changes:
    - Verify no functionality loss
    - Assess quality improvement
    - Check for issues
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple file cleanup (<5 files)
- ❌ Single-domain cleanup (just imports OR just files)
- ❌ Safe mode (minimal changes)
- ❌ Interactive mode (user-guided)

## Tool Coordination
- **Task tool**: Delegates for large/complex cleanup (3 subagents)
- **Bash**: Direct file operations for simple cleanup (direct)
- **Read/Edit**: Code analysis and modification (direct for simple, by subagent for complex)
- **Sequential MCP**: Structured cleanup planning (direct)
- **Context7 MCP**: Framework-specific cleanup patterns (direct)
- **TodoWrite**: Track cleanup steps (direct)

## Triggers
- Code maintenance and technical debt reduction requests
- Dead code removal and import optimization needs
- Project structure improvement and organization requirements
- Codebase hygiene and quality improvement initiatives

## Usage
```
/quality:cleanup [target] [--type code|imports|files|all] [--safe|--aggressive] [--interactive]
```

## Behavioral Flow
1. **Analyze**: Assess cleanup opportunities and safety considerations across target scope
2. **Plan**: Choose cleanup approach and activate relevant personas for domain expertise
3. **Execute**: Apply systematic cleanup with intelligent dead code detection and removal
4. **Validate**: Ensure no functionality loss through testing and safety verification
5. **Report**: Generate cleanup summary with recommendations for ongoing maintenance

Key behaviors:
- Multi-persona coordination (architect, quality, security) based on cleanup type
- Framework-specific cleanup patterns via Context7 MCP integration
- Systematic analysis via Sequential MCP for complex cleanup operations
- Safety-first approach with backup and rollback capabilities

## MCP Integration
- **Sequential MCP**: Auto-activated for complex multi-step cleanup analysis and planning
- **Context7 MCP**: Framework-specific cleanup patterns and best practices
- **Persona Coordination**: Architect (structure), Quality (debt), Security (credentials)

## Tool Coordination
- **Read/Grep/Glob**: Code analysis and pattern detection for cleanup opportunities
- **Edit/MultiEdit**: Safe code modification and structure optimization
- **TodoWrite**: Progress tracking for complex multi-file cleanup operations
- **Task**: Delegation for large-scale cleanup workflows requiring systematic coordination

## Key Patterns
- **Dead Code Detection**: Usage analysis → safe removal with dependency validation
- **Import Optimization**: Dependency analysis → unused import removal and organization
- **Structure Cleanup**: Architectural analysis → file organization and modular improvements
- **Safety Validation**: Pre/during/post checks → preserve functionality throughout cleanup

## Examples

### Safe Code Cleanup
```
/quality:cleanup src/ --type code --safe
# Conservative cleanup with automatic safety validation
# Removes dead code while preserving all functionality
```

### Import Optimization
```
/quality:cleanup --type imports --preview
# Analyzes and shows unused import cleanup without execution
# Framework-aware optimization via Context7 patterns
```

### Comprehensive Project Cleanup
```
/quality:cleanup --type all --interactive
# Multi-domain cleanup with user guidance for complex decisions
# Activates all personas for comprehensive analysis
```

### Framework-Specific Cleanup
```
/quality:cleanup components/ --aggressive
# Thorough cleanup with Context7 framework patterns
# Sequential analysis for complex dependency management
```

## Boundaries

**Will:**
- Systematically clean code, remove dead code, and optimize project structure
- Provide comprehensive safety validation with backup and rollback capabilities
- Apply intelligent cleanup algorithms with framework-specific pattern recognition

**Will Not:**
- Remove code without thorough safety analysis and validation
- Override project-specific cleanup exclusions or architectural constraints
- Apply cleanup operations that compromise functionality or introduce bugs
