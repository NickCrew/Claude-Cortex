# Reference: adjust

# /reasoning:adjust - Dynamic Reasoning Depth Control

## Personas (Thinking Modes)
- **performance-engineer**: Depth optimization, runtime efficiency, complexity assessment
- **architect**: Task complexity analysis, appropriate reasoning level, quality requirements
- **cost-optimizer**: Budget awareness, depth-cost trade-offs, efficiency recommendations

## Delegation Protocol

**This command does NOT delegate** - Reasoning adjustment is configuration change.

**Why no delegation**:
- ❌ Fast configuration update (<1 second)
- ❌ Simple parameter adjustment
- ❌ Direct MCP server activation/deactivation
- ❌ No complex execution required

**All work done directly**:
- Assess current reasoning depth
- Validate requested adjustment
- Update configuration parameters
- Reconfigure MCP server activation

**Note**: Personas guide adjustment decisions (performance for efficiency, architect for appropriateness, optimizer for cost).

## Tool Coordination
- **Direct configuration**: Reasoning depth adjustment (direct)
- **MCP reconfiguration**: Server activation based on depth (direct)
- **No delegation needed**: Simple configuration change

## Triggers
- Need to escalate or reduce reasoning depth during complex task execution
- Initial analysis insufficient or overly verbose for current subtask
- Performance optimization during long-running operations
- Runtime adaptation based on emerging task complexity

## Usage
```
/reasoning:adjust [low|medium|high|ultra] [--scope current|remaining]
```

## Behavioral Flow
1. **Assess**: Evaluate current reasoning depth and task context
2. **Validate**: Confirm depth change is appropriate for operation type
3. **Adjust**: Reconfigure analysis parameters and MCP server activation
4. **Apply**: Execute remaining work with new depth configuration
5. **Track**: Monitor effectiveness and suggest further adjustments if needed

Key behaviors:
- Runtime depth switching without restarting task execution
- Intelligent scope control (current subtask vs remaining work)
- MCP server activation/deactivation based on depth changes
- Token budget reallocation for optimal resource utilization

## Reasoning Depth Levels

### Low (~2K tokens)
- **Use case**: Simple operations, quick iterations, prototyping
- **MCP servers**: None (native tools only)
- **Analysis style**: Direct solutions, minimal exploration
- **Token budget**: ~2,000 tokens per analysis phase

### Medium (~4K tokens)
- **Use case**: Standard development tasks, moderate complexity
- **MCP servers**: Sequential (structured reasoning)
- **Analysis style**: Systematic exploration, hypothesis testing
- **Token budget**: ~4,000 tokens per analysis phase
- **Equivalent**: `--think` flag

### High (~10K tokens)
- **Use case**: Architectural decisions, system-wide dependencies
- **MCP servers**: Sequential + Context7 (official patterns)
- **Analysis style**: Deep exploration, trade-off analysis, pattern research
- **Token budget**: ~10,000 tokens per analysis phase
- **Equivalent**: `--think-hard` flag

### Ultra (~32K tokens)
- **Use case**: Critical redesigns, legacy modernization, complex debugging
- **MCP servers**: All available (Sequential, Context7, Codanna, etc.)
- **Analysis style**: Maximum depth, exhaustive exploration, meta-analysis
- **Token budget**: ~32,000 tokens per analysis phase
- **Equivalent**: `--ultrathink` flag
- **Auto-enables**: `--introspect` transparency markers

## Scope Control

### --scope current
- Apply depth change to current subtask only
- Revert to previous depth after completion
- Use for: Isolated complexity spikes

### --scope remaining
- Apply depth change to all remaining work (default)
- Persist through task hierarchy
- Use for: Sustained complexity adjustment

## Tool Coordination
- **TodoWrite**: Update task tracking with depth change notifications
- **Read/Grep**: Adjust file analysis thoroughness based on depth
- **MCP Servers**: Activate/deactivate based on depth level

## Key Patterns
- **Escalation**: Low → Medium → High → Ultra (complexity increases)
- **De-escalation**: Ultra → High → Medium → Low (optimization/iteration)
- **Targeted**: Maintain base depth, spike for specific subtasks
- **Adaptive**: Monitor effectiveness, suggest further adjustments

## Examples

### Escalate for Complex Subtask
```
/reasoning:adjust ultra --scope current
# Escalate to maximum depth for current complex subtask only
# Reverts to previous depth after completion
```

### Optimize Long-Running Analysis
```
/reasoning:adjust medium --scope remaining
# Reduce depth for faster iteration in remaining work
# Useful when initial deep analysis provided sufficient context
```

### Spike for Architecture Decision
```
/reasoning:adjust high --scope current
# Deep analysis for architectural decision point
# Return to standard depth for implementation
```

### Maximum Depth Investigation
```
/reasoning:adjust ultra --scope remaining
# Full depth for complex debugging or system redesign
# Enables all MCP servers and introspection markers
```

## Boundaries

**Will:**
- Dynamically adjust reasoning depth during task execution
- Reconfigure MCP server activation and token budgets
- Provide scope control for targeted vs sustained adjustments
- Suggest optimal depth based on task characteristics

**Will Not:**
- Override explicit user depth preferences without confirmation
- Change depth mid-analysis (waits for subtask boundaries)
- Disable critical safety validations regardless of depth
- Adjust depth for operations requiring specific configurations
