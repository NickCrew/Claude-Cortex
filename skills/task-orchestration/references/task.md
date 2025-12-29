# Reference: task

# /orchestrate:task - Enhanced Task Management

## Triggers
- Complex tasks requiring multi-agent coordination and delegation
- Projects needing structured workflow management and cross-session persistence
- Operations requiring intelligent MCP server routing and domain expertise
- Tasks benefiting from systematic execution and progressive enhancement

## Usage
```
/orchestrate:task [action] [target] [--strategy systematic|agile|enterprise] [--parallel] [--delegate]
```

## Behavioral Flow
1. **Analyze**: Parse task requirements and determine optimal execution strategy
2. **Delegate**: Route to appropriate MCP servers and activate relevant personas
3. **Coordinate**: Execute tasks with intelligent workflow management and parallel processing
4. **Validate**: Apply quality gates and comprehensive task completion verification
5. **Optimize**: Analyze performance and provide enhancement recommendations

Key behaviors:
- Multi-persona coordination across architect, frontend, backend, security, devops domains
- Intelligent MCP server routing (Sequential, Context7, Magic, Playwright, Morphllm, Codanna)
- Systematic execution with progressive task enhancement and cross-session persistence
- Advanced task delegation with hierarchical breakdown and dependency management

## MCP Integration
- **Sequential MCP**: Complex multi-step task analysis and systematic execution planning
- **Context7 MCP**: Framework-specific patterns and implementation best practices
- **Magic MCP**: UI/UX task coordination and design system integration
- **Playwright MCP**: Testing workflow integration and validation automation
- **Morphllm MCP**: Large-scale task transformation and pattern-based optimization
- **Codanna MCP**: Cross-session task persistence and project memory management

## Personas (Thinking Modes)
These guide Claude's perspective and decision-making approach:
- **architect**: System design thinking, scalability patterns, architectural decisions
- **analyzer**: Deep analysis, pattern recognition, dependency understanding
- **frontend**: UI/UX focus, accessibility, user experience considerations
- **backend**: API design, data modeling, server-side logic
- **security**: Security-first mindset, threat modeling, vulnerability awareness
- **devops**: Infrastructure, deployment, operational excellence
- **project-manager**: Coordination, planning, stakeholder communication

*Note: Personas influence how Claude thinks, not execution mechanism. For actual work delegation, see Delegation Protocol below.*

## Delegation Protocol

**When to delegate** (use Task tool to launch subagents):
- ✅ >3 files or >5 steps needed
- ✅ Multi-domain work (implementation + tests + docs)
- ✅ Complex analysis requiring deep exploration
- ✅ User needs visibility into progress
- ✅ Long-running operations (>30 seconds)
- ✅ Parallel workstreams possible

**Available subagents** (launched via Task tool):
- **general-purpose**: Versatile implementation work, feature development
- **code-reviewer**: Quality analysis, security review, best practices validation
- **test-automator**: Test generation, coverage analysis, test execution
- **Explore**: Codebase exploration, pattern discovery, dependency analysis
- **technical-writer**: Documentation creation (when available)
- **security-auditor**: Security-focused analysis (when available)

**How to delegate**:
```xml
<!-- Launch multiple subagents in SINGLE message for parallel execution -->
<function_calls>
<invoke name="Task">
  <subagent_type>general-purpose</subagent_type>
  <description>Implement feature X</description>
  <prompt>Detailed implementation instructions with persona guidance...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>test-automator</subagent_type>
  <description>Generate tests for feature X</description>
  <prompt>Test generation instructions...</prompt>
</invoke>
<invoke name="Task">
  <subagent_type>code-reviewer</subagent_type>
  <description>Review feature X implementation</description>
  <prompt>Quality review instructions...</prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Simple operations (1-2 files, quick reads)
- ❌ Atomic operations (<10 seconds)
- ❌ Single grep/glob searches
- ❌ Trivial edits or reads

## Tool Coordination
- **Task tool**: Claude Code's delegation mechanism - launches subagents for complex multi-step work
- **TodoWrite**: Hierarchical task breakdown and progress tracking across Epic → Story → Task levels
- **Read/Write/Edit**: Direct file operations for simple changes
- **MCP servers**: External integrations (Sequential, Context7, etc.) for specialized capabilities
- **sequentialthinking**: Structured reasoning for complex task dependency analysis

## Key Patterns
- **Task Hierarchy**: Epic-level objectives → Story coordination → Task execution → Subtask granularity
- **Strategy Selection**: Systematic (comprehensive) → Agile (iterative) → Enterprise (governance)
- **Subagent Coordination**:
  1. Activate personas (thinking modes)
  2. Determine complexity (delegate if needed)
  3. Launch Task tool with appropriate subagents
  4. Execute in parallel when possible
  5. Integrate results with persona-guided synthesis
- **Cross-Session Management**: Task persistence → context continuity → progressive enhancement

## Examples

### Complex Feature Development
```
/orchestrate:task create "enterprise authentication system" --strategy systematic --parallel
# Comprehensive task breakdown with multi-domain coordination
# Activates architect, security, backend, frontend personas
```

### Agile Sprint Coordination
```
/orchestrate:task execute "feature backlog" --strategy agile --delegate
# Iterative task execution with intelligent delegation
# Cross-session persistence for sprint continuity
```

### Multi-Domain Integration
```
/orchestrate:task execute "microservices platform" --strategy enterprise --parallel
# Enterprise-scale coordination with compliance validation
# Parallel execution across multiple technical domains
```

## Boundaries

**Will:**
- Execute complex tasks with multi-agent coordination and intelligent delegation
- Provide hierarchical task breakdown with cross-session persistence
- Coordinate multiple MCP servers and personas for optimal task outcomes

**Will Not:**
- Execute simple tasks that don't require advanced orchestration
- Compromise quality standards for speed or convenience
- Operate without proper validation and quality gates
