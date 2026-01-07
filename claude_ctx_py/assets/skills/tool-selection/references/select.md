# Reference: select

# /tools:select - Intelligent MCP Tool Selection

## Personas (Thinking Modes)
- **architect**: Complexity assessment, capability matching, operation analysis
- **performance-engineer**: Performance vs accuracy trade-offs, tool efficiency comparison
- **tool-specialist**: MCP tool capabilities, strength/weakness analysis, optimal routing

## Delegation Protocol

**This command does NOT delegate** - Tool selection is direct analysis and decision.

**Why no delegation**:
- ❌ Fast complexity scoring (<5 seconds)
- ❌ Direct capability matching logic
- ❌ Simple scoring matrix application
- ❌ No external execution required (just decision)

**All work done directly**:
- Parse operation requirements
- Apply complexity scoring
- Match against Codanna and Morphllm capabilities
- Select optimal tool
- Provide confidence metrics

**Note**: This command uses MCP servers (Codanna, Morphllm) for understanding their capabilities, but doesn't delegate the selection logic itself. Personas guide the selection criteria.

## Tool Coordination
- **Codanna MCP**: Capability query (direct API for metadata)
- **Morphllm MCP**: Capability query (direct API for metadata)
- **Direct analysis**: Complexity scoring and matching (direct logic)
- **No delegation needed**: Decision-making is direct

## Triggers
- Operations requiring optimal MCP tool selection between Codanna and Morphllm
- Meta-system decisions needing complexity analysis and capability matching
- Tool routing decisions requiring performance vs accuracy trade-offs
- Operations benefiting from intelligent tool capability assessment

## Usage
```
/tools:select [operation] [--analyze] [--explain]
```

## Behavioral Flow
1. **Parse**: Analyze operation type, scope, file count, and complexity indicators
2. **Score**: Apply multi-dimensional complexity scoring across various operation factors
3. **Match**: Compare operation requirements against Codanna and Morphllm capabilities
4. **Select**: Choose optimal tool based on scoring matrix and performance requirements
5. **Validate**: Verify selection accuracy and provide confidence metrics

Key behaviors:
- Complexity scoring based on file count, operation type, language, and framework requirements
- Performance assessment evaluating speed vs accuracy trade-offs for optimal selection
- Decision logic matrix with direct mappings and threshold-based routing rules
- Tool capability matching for Codanna (semantic operations) vs Morphllm (pattern operations)

## MCP Integration
- **Codanna MCP**: Optimal for semantic operations, LSP functionality, symbol navigation, and project context
- **Morphllm MCP**: Optimal for pattern-based edits, bulk transformations, and speed-critical operations
- **Decision Matrix**: Intelligent routing based on complexity scoring and operation characteristics

## Tool Coordination
- **get_current_config**: System configuration analysis for tool capability assessment
- **execute_sketched_edit**: Operation testing and validation for selection accuracy
- **Read/Grep**: Operation context analysis and complexity factor identification
- **Integration**: Automatic selection logic used by refactor, edit, implement, and improve commands

## Key Patterns
- **Direct Mapping**: Symbol operations → Codanna, Pattern edits → Morphllm, Memory operations → Codanna
- **Complexity Thresholds**: Score >0.6 → Codanna, Score <0.4 → Morphllm, 0.4-0.6 → Feature-based
- **Performance Trade-offs**: Speed requirements → Morphllm, Accuracy requirements → Codanna
- **Fallback Strategy**: Codanna → Morphllm → Native tools degradation chain

## Examples

### Complex Refactoring Operation
```
/tools:select "rename function across 10 files" --analyze
# Analysis: High complexity (multi-file, symbol operations)
# Selection: Codanna MCP (LSP capabilities, semantic understanding)
```

### Pattern-Based Bulk Edit
```
/tools:select "update console.log to logger.info across project" --explain
# Analysis: Pattern-based transformation, speed priority
# Selection: Morphllm MCP (pattern matching, bulk operations)
```

### Memory Management Operation
```
/tools:select "save project context and discoveries"
# Direct mapping: Memory operations → Codanna MCP
# Rationale: Project context and cross-session persistence
```

## Boundaries

**Will:**
- Analyze operations and provide optimal tool selection between Codanna and Morphllm
- Apply complexity scoring based on file count, operation type, and requirements
- Provide sub-100ms decision time with >95% selection accuracy

**Will Not:**
- Override explicit tool specifications when user has clear preference
- Select tools without proper complexity analysis and capability matching
- Compromise performance requirements for convenience or speed
