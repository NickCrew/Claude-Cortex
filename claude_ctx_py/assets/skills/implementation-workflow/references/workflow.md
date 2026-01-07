# Reference: workflow

# /design:workflow - Implementation Workflow Generator

## Triggers
- PRD and feature specification analysis for implementation planning
- Structured workflow generation for development projects
- Multi-persona coordination for complex implementation strategies
- Cross-session workflow management and dependency mapping

## Usage
```
/design:workflow [prd-file|feature-description] [--strategy systematic|agile|enterprise] [--depth shallow|normal|deep] [--parallel]
```

## Behavioral Flow
1. **Analyze**: Parse PRD and feature specifications to understand implementation requirements
2. **Plan**: Generate comprehensive workflow structure with dependency mapping and task orchestration
3. **Coordinate**: Activate multiple personas for domain expertise and implementation strategy
4. **Execute**: Create structured step-by-step workflows with automated task coordination
5. **Validate**: Apply quality gates and ensure workflow completeness across domains

Key behaviors:
- Multi-persona orchestration across architecture, frontend, backend, security, and devops domains
- Advanced MCP coordination with intelligent routing for specialized workflow analysis
- Systematic execution with progressive workflow enhancement and parallel processing
- Cross-session workflow management with comprehensive dependency tracking

## MCP Integration
- **Sequential MCP**: Complex multi-step workflow analysis and systematic implementation planning
- **Context7 MCP**: Framework-specific workflow patterns and implementation best practices
- **Magic MCP**: UI/UX workflow generation and design system integration strategies
- **Playwright MCP**: Testing workflow integration and quality assurance automation
- **Morphllm MCP**: Large-scale workflow transformation and pattern-based optimization
- **Codanna MCP**: Cross-session workflow persistence, memory management, and project context

## Personas (Thinking Modes)
- **architect**: System design, component organization, scalability planning
- **analyzer**: Deep analysis, dependency mapping, complexity assessment
- **frontend**: UI/UX workflow, user interaction patterns, accessibility
- **backend**: API design, data flow, service orchestration
- **security**: Security requirements, threat modeling, compliance
- **devops**: Deployment workflow, infrastructure, CI/CD
- **project-manager**: Task coordination, risk management, resource planning

## Delegation Protocol

**This command USUALLY delegates** - workflow generation is complex multi-persona work.

**When to delegate** (use Task tool):
- ✅ Any PRD or feature spec analysis
- ✅ Multi-domain workflows (>2 technical domains)
- ✅ Complex dependency mapping
- ✅ Enterprise or systematic strategies

**Available subagents**:
- **Explore**: Codebase analysis, existing patterns, integration points
- **general-purpose**: Workflow generation, task decomposition, dependency mapping
- **code-reviewer**: Technical validation, feasibility assessment

**Delegation strategy for PRD workflow**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>Explore</subagent_type>
  <description>Analyze existing codebase and patterns</description>
  <prompt>
    Explore for workflow planning:
    - Current architecture
    - Framework patterns
    - Existing components for reuse
    - Integration constraints
    Thoroughness: [shallow|normal|deep based on --depth]
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Generate implementation workflow from PRD</description>
  <prompt>
    Analyze PRD and generate workflow:
    - Strategy: [systematic|agile|enterprise]
    - Multi-persona coordination
    - Task decomposition with DoD
    - Dependency mapping
    - Quality gates integration
    MCP: Sequential for analysis, Context7 for patterns
  </prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Validate workflow feasibility</description>
  <prompt>
    Review generated workflow:
    - Technical feasibility
    - Dependency accuracy
    - Risk assessment
    - Completeness check
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple task list (not a full workflow)
- ❌ Workflow refinement (already generated)
- ❌ Quick feature breakdown (<3 tasks)

## Tool Coordination
- **Task tool**: Launches subagents for PRD analysis and workflow generation
- **Read**: PRD/spec analysis (by subagents)
- **Write**: Workflow documentation (by subagents)
- **TodoWrite**: Task tracking integration
- **WebSearch**: Technology research (by subagents if needed)
- **MCP servers**: Sequential (analysis), Context7 (patterns), Codanna (persistence)

## Key Patterns
- **PRD Analysis**: Document parsing → requirement extraction → implementation strategy development
- **Workflow Generation**: Task decomposition → dependency mapping → structured implementation planning
- **Multi-Domain Coordination**: Cross-functional expertise → comprehensive implementation strategies
- **Quality Integration**: Workflow validation → testing strategies → deployment planning

## Examples

### Systematic PRD Workflow
```
/design:workflow ClaudeDocs/PRD/feature-spec.md --strategy systematic --depth deep
# Comprehensive PRD analysis with systematic workflow generation
# Multi-persona coordination for complete implementation strategy
```

### Agile Feature Workflow
```
/design:workflow "user authentication system" --strategy agile --parallel
# Agile workflow generation with parallel task coordination
# Context7 and Magic MCP for framework and UI workflow patterns
```

### Enterprise Implementation Planning
```
/design:workflow enterprise-prd.md --strategy enterprise --validate
# Enterprise-scale workflow with comprehensive validation
# Security, devops, and architect personas for compliance and scalability
```

### Cross-Session Workflow Management
```
/design:workflow project-brief.md --depth normal
# Codanna MCP manages cross-session workflow context and persistence
# Progressive workflow enhancement with memory-driven insights
```

## Boundaries

**Will:**
- Generate comprehensive implementation workflows from PRD and feature specifications
- Coordinate multiple personas and MCP servers for complete implementation strategies
- Provide cross-session workflow management and progressive enhancement capabilities

**Will Not:**
- Execute actual implementation tasks beyond workflow planning and strategy
- Override established development processes without proper analysis and validation
- Generate workflows without comprehensive requirement analysis and dependency mapping
