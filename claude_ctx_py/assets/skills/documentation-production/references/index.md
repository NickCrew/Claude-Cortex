# Reference: index

# /docs:index - Project Documentation

## Triggers
- Project documentation creation and maintenance requirements
- Knowledge base generation and organization needs
- API documentation and structure analysis requirements
- Cross-referencing and navigation enhancement requests

## Usage
```
/docs:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]
```

## Behavioral Flow
1. **Analyze**: Examine project structure and identify key documentation components
2. **Organize**: Apply intelligent organization patterns and cross-referencing strategies
3. **Generate**: Create comprehensive documentation with framework-specific patterns
4. **Validate**: Ensure documentation completeness and quality standards
5. **Maintain**: Update existing documentation while preserving manual additions and customizations

Key behaviors:
- Multi-persona coordination (architect, scribe, quality) based on documentation scope and complexity
- Sequential MCP integration for systematic analysis and comprehensive documentation workflows
- Context7 MCP integration for framework-specific patterns and documentation standards
- Intelligent organization with cross-referencing capabilities and automated maintenance

## MCP Integration
- **Sequential MCP**: Complex multi-step project analysis and systematic documentation generation
- **Context7 MCP**: Framework-specific documentation patterns and established standards
- **Persona Coordination**: Architect (structure), Scribe (content), Quality (validation)

## Personas (Thinking Modes)
- **architect**: Structural organization, cross-referencing strategy, logical documentation hierarchy
- **technical-writer**: Clear communication, audience-appropriate content, comprehensive coverage
- **quality-engineer**: Documentation completeness, accuracy verification, standards compliance

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Large project documentation (>10 components)
- ✅ Comprehensive API documentation
- ✅ Knowledge base generation
- ✅ Multi-type documentation (structure + API + guides)

**Available subagents**:
- **Explore**: Project structure analysis, component discovery, relationship mapping
- **technical-writer**: User guides, tutorials, knowledge base content
- **api-documenter**: API reference documentation, endpoint descriptions, schemas

**Delegation strategy for comprehensive docs**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze project structure and components</description>
  <prompt>
    Explore project for documentation:
    - Component identification
    - API endpoints discovery
    - Architecture patterns
    - Cross-reference opportunities
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>api-documenter</subagent_type>
  <description>Generate API documentation</description>
  <prompt>
    Create API documentation:
    - Endpoint descriptions
    - Request/response schemas
    - Authentication
    - Usage examples
    Format: [md|json|yaml]
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>technical-writer</subagent_type>
  <description>Generate project documentation</description>
  <prompt>
    Create project docs with architect guidance:
    - Project structure overview
    - Component relationships
    - Getting started guide
    - Cross-references
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple README updates
- ❌ Single component documentation
- ❌ Quick API reference for <5 endpoints

## Tool Coordination
- **Task tool**: Delegates to Explore, technical-writer, api-documenter for comprehensive documentation
- **Read/Grep/Glob**: Project analysis (by subagents for complex, direct for simple)
- **Write**: Documentation creation (by subagents for complex, direct for simple)
- **TodoWrite**: Progress tracking for multi-component workflows

## Key Patterns
- **Structure Analysis**: Project examination → component identification → logical organization → cross-referencing
- **Documentation Types**: API docs → Structure docs → README → Knowledge base approaches
- **Quality Validation**: Completeness assessment → accuracy verification → standard compliance → maintenance planning
- **Framework Integration**: Context7 patterns → official standards → best practices → consistency validation

## Examples

### Project Structure Documentation
```
/docs:index project-root --type structure --format md
# Comprehensive project structure documentation with intelligent organization
# Creates navigable structure with cross-references and component relationships
```

### API Documentation Generation
```
/docs:index src/api --type api --format json
# API documentation with systematic analysis and validation
# Scribe and quality personas ensure completeness and accuracy
```

### Knowledge Base Creation
```
/docs:index . --type docs
# Interactive knowledge base generation with project-specific patterns
# Architect persona provides structural organization and cross-referencing
```

## Boundaries

**Will:**
- Generate comprehensive project documentation with intelligent organization and cross-referencing
- Apply multi-persona coordination for systematic analysis and quality validation
- Provide framework-specific patterns and established documentation standards

**Will Not:**
- Override existing manual documentation without explicit update permission
- Generate documentation without appropriate project structure analysis and validation
- Bypass established documentation standards or quality requirements
