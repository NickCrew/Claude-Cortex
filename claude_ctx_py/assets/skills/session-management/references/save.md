# Reference: save

# /session:save - Session Context Persistence

## Personas (Thinking Modes)
- **project-manager**: Progress tracking, milestone documentation, session outcome assessment
- **documentation-specialist**: Context preservation, discovery archival, checkpoint clarity
- **knowledge-engineer**: Cross-session learning, memory management, insight extraction

## Delegation Protocol

**This command does NOT delegate** - Session saving is direct MCP integration.

**Why no delegation**:
- ❌ Fast Codanna MCP operations (<5 seconds)
- ❌ Direct memory persistence API calls
- ❌ Simple checkpoint creation
- ❌ Straightforward session metadata updates

**All work done directly**:
- Codanna MCP for session context persistence
- Direct API calls for memory management
- Read/Write for checkpoint files (if needed)
- TodoWrite for tracking save progress

**Note**: Personas guide what to save (PM for progress, docs for context, knowledge for learnings). Codanna MCP handles the actual persistence.

## Tool Coordination
- **Codanna MCP**: Session context persistence, memory management (direct API)
- **Write**: Checkpoint files if needed (direct)
- **Read**: Analyze current session for saving (direct)
- **TodoWrite**: Track save operations (direct)

## Triggers
- Session completion and project context persistence needs
- Cross-session memory management and checkpoint creation requests
- Project understanding preservation and discovery archival scenarios
- Session lifecycle management and progress tracking requirements

## Usage
```
/session:save [--type session|learnings|context|all] [--summarize] [--checkpoint]
```

## Behavioral Flow
1. **Analyze**: Examine session progress and identify discoveries worth preserving
2. **Persist**: Save session context and learnings using Codanna MCP memory management
3. **Checkpoint**: Create recovery points for complex sessions and progress tracking
4. **Validate**: Ensure session data integrity and cross-session compatibility
5. **Prepare**: Ready session context for seamless continuation in future sessions

Key behaviors:
- Codanna MCP integration for memory management and cross-session persistence
- Automatic checkpoint creation based on session progress and critical tasks
- Session context preservation with comprehensive discovery and pattern archival
- Cross-session learning with accumulated project insights and technical decisions

## MCP Integration
- **Codanna MCP**: Mandatory integration for session management, memory operations, and cross-session persistence
- **Memory Operations**: Session context storage, checkpoint creation, and discovery archival
- **Performance Critical**: <200ms for memory operations, <1s for checkpoint creation

## Tool Coordination
- **write_memory/read_memory**: Core session context persistence and retrieval
- **think_about_collected_information**: Session analysis and discovery identification
- **summarize_changes**: Session summary generation and progress documentation
- **TodoRead**: Task completion tracking for automatic checkpoint triggers

## Key Patterns
- **Session Preservation**: Discovery analysis → memory persistence → checkpoint creation
- **Cross-Session Learning**: Context accumulation → pattern archival → enhanced project understanding
- **Progress Tracking**: Task completion → automatic checkpoints → session continuity
- **Recovery Planning**: State preservation → checkpoint validation → restoration readiness

## Examples

### Basic Session Save
```
/session:save
# Saves current session discoveries and context to Codanna MCP
# Automatically creates checkpoint if session exceeds 30 minutes
```

### Comprehensive Session Checkpoint
```
/session:save --type all --checkpoint
# Complete session preservation with recovery checkpoint
# Includes all learnings, context, and progress for session restoration
```

### Session Summary Generation
```
/session:save --summarize
# Creates session summary with discovery documentation
# Updates cross-session learning patterns and project insights
```

### Discovery-Only Persistence
```
/session:save --type learnings
# Saves only new patterns and insights discovered during session
# Updates project understanding without full session preservation
```

## Boundaries

**Will:**
- Save session context using Codanna MCP integration for cross-session persistence
- Create automatic checkpoints based on session progress and task completion
- Preserve discoveries and patterns for enhanced project understanding

**Will Not:**
- Operate without proper Codanna MCP integration and memory access
- Save session data without validation and integrity verification
- Override existing session context without proper checkpoint preservation
