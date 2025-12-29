# Reference: load

# /session:load - Project Context Loading

## Personas (Thinking Modes)
- **project-manager**: Project activation, workflow preparation, session planning
- **developer**: Development environment readiness, context validation, dependency awareness
- **knowledge-engineer**: Memory retrieval, cross-session continuity, learning application

## Delegation Protocol

**This command does NOT delegate** - Session loading is direct MCP integration.

**Why no delegation**:
- ❌ Fast Codanna MCP operations (<5 seconds)
- ❌ Direct memory retrieval API calls
- ❌ Simple checkpoint loading
- ❌ Straightforward context activation

**All work done directly**:
- Codanna MCP for project context loading
- Direct API calls for memory retrieval
- Read for checkpoint files (if needed)
- TodoWrite for tracking load operations

**Note**: Personas guide context interpretation (PM for planning, developer for readiness, knowledge for insights). Codanna MCP handles the actual loading.

## Tool Coordination
- **Codanna MCP**: Project context loading, memory retrieval (direct API)
- **Read**: Checkpoint files and project state (direct)
- **TodoWrite**: Track load operations (direct)
- **Direct context activation**: No Task tool needed

## Triggers
- Session initialization and project context loading requests
- Cross-session persistence and memory retrieval needs
- Project activation and context management requirements
- Session lifecycle management and checkpoint loading scenarios

## Usage
```
/session:load [target] [--type project|config|deps|checkpoint] [--refresh] [--analyze]
```

## Behavioral Flow
1. **Initialize**: Establish Codanna MCP connection and session context management
2. **Discover**: Analyze project structure and identify context loading requirements
3. **Load**: Retrieve project memories, checkpoints, and cross-session persistence data
4. **Activate**: Establish project context and prepare for development workflow
5. **Validate**: Ensure loaded context integrity and session readiness

Key behaviors:
- Codanna MCP integration for memory management and cross-session persistence
- Project activation with comprehensive context loading and validation
- Performance-critical operation with <500ms initialization target
- Session lifecycle management with checkpoint and memory coordination

## MCP Integration
- **Codanna MCP**: Mandatory integration for project activation, memory retrieval, and session management
- **Memory Operations**: Cross-session persistence, checkpoint loading, and context restoration
- **Performance Critical**: <200ms for core operations, <1s for checkpoint creation

## Tool Coordination
- **activate_project**: Core project activation and context establishment
- **list_memories/read_memory**: Memory retrieval and session context loading
- **Read/Grep/Glob**: Project structure analysis and configuration discovery
- **Write**: Session context documentation and checkpoint creation

## Key Patterns
- **Project Activation**: Directory analysis → memory retrieval → context establishment
- **Session Restoration**: Checkpoint loading → context validation → workflow preparation
- **Memory Management**: Cross-session persistence → context continuity → development efficiency
- **Performance Critical**: Fast initialization → immediate productivity → session readiness

## Examples

### Basic Project Loading
```
/session:load
# Loads current directory project context with Codanna memory integration
# Establishes session context and prepares for development workflow
```

### Specific Project Loading
```
/session:load /path/to/project --type project --analyze
# Loads specific project with comprehensive analysis
# Activates project context and retrieves cross-session memories
```

### Checkpoint Restoration
```
/session:load --type checkpoint --checkpoint session_123
# Restores specific checkpoint with session context
# Continues previous work session with full context preservation
```

### Dependency Context Loading
```
/session:load --type deps --refresh
# Loads dependency context with fresh analysis
# Updates project understanding and dependency mapping
```

## Boundaries

**Will:**
- Load project context using Codanna MCP integration for memory management
- Provide session lifecycle management with cross-session persistence
- Establish project activation with comprehensive context loading

**Will Not:**
- Modify project structure or configuration without explicit permission
- Load context without proper Codanna MCP integration and validation
- Override existing session context without checkpoint preservation
