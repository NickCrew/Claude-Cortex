# Task Management Mode

**Purpose**: Hierarchical task organization with persistent memory for complex multi-step operations

## Activation Triggers
- Operations with >3 steps requiring coordination
- Multiple file/directory scope (>2 directories OR >3 files)
- Complex dependencies requiring phases
- Manual flags: `--task-manage`, `--delegate`
- Quality improvement requests: polish, refine, enhance

## Task Hierarchy with Memory

📋 **Plan** → write_memory("plan", goal_statement)
→ 🎯 **Phase** → write_memory("phase_X", milestone)
  → 📦 **Task** → write_memory("task_X.Y", deliverable)
    → ✓ **Todo** → TodoWrite + write_memory("todo_X.Y.Z", status)

## Memory Operations

### Session Start
```
1. list_memories() → Show existing task state
2. read_memory("current_plan") → Resume context
3. think_about_collected_information() → Understand where we left off
```

### During Execution
```
1. write_memory("task_2.1", "completed: auth middleware")
2. think_about_task_adherence() → Verify on track
3. Update TodoWrite status in parallel
4. write_memory("checkpoint", current_state) every 30min
```

### Session End
```
1. think_about_whether_you_are_done() → Assess completion
2. write_memory("session_summary", outcomes)
3. delete_memory() for completed temporary items
```

## Physical Task Tracking

Tasks are also tracked physically in `~/.claude/tasks/current/`:

```
tasks/current/
├── active.json           # Currently active task
├── active_workflow       # Active workflow name (if any)
├── workflow_status       # Workflow progress
├── checkpoint            # Latest checkpoint
├── queue/               # Pending tasks
├── completed/           # Finished tasks with timestamps
└── checkpoints/         # Session snapshots
```

### Physical Task Operations

**Create Task File**:
```json
{
  "id": "task_2.1",
  "description": "Implement auth middleware",
  "phase": "2",
  "priority": "high",
  "created": 1234567890,
  "dependencies": ["task_1.1"]
}
```

**Move Task Through States**:
```bash
queue/task_2.1.json → active.json → completed/task_2.1.1234567890.json
```

**Checkpoint Creation**:
```bash
Write to checkpoints/checkpoint_1234567890.json
Include: current task, progress, blockers, next steps
```

## Execution Pattern

1. **Load**: list_memories() + check physical tasks → Resume state
2. **Plan**: Create hierarchy → write_memory() + create task files
3. **Track**: TodoWrite + memory updates + move task files in parallel
4. **Execute**: Update memories + move tasks through states
5. **Checkpoint**: write_memory() + create physical checkpoint every 30min
6. **Complete**: Final memory update + move task to completed/ with outcomes

## Hybrid Tracking Pattern

**Start Task**:
```
1. write_memory("task_2.1", "started: auth middleware")
2. Create queue/task_2.1.json
3. Move to active.json
4. TodoWrite status update
```

**Complete Task**:
```
1. write_memory("task_2.1", "completed: auth middleware working")
2. Move active.json to completed/task_2.1.timestamp.json
3. TodoWrite mark complete
4. Update checkpoint
```

**Resume Session**:
```
1. list_memories() → Get memory context
2. Read tasks/current/active.json → Get current task
3. Read tasks/current/checkpoint → Get last state
4. think_about_collected_information() → Synthesize context
```

## Tool Selection

| Task Type | Primary Tool | Memory Key |
|-----------|-------------|------------|
| Analysis | Sequential MCP | "analysis_results" |
| Implementation | MultiEdit/Morphllm | "code_changes" |
| UI Components | Magic MCP | "ui_components" |
| Testing | Playwright MCP | "test_results" |
| Documentation | Context7 MCP | "doc_patterns" |

## Memory Schema

```
plan_[timestamp]: Overall goal statement
phase_[1-5]: Major milestone descriptions
task_[phase].[number]: Specific deliverable status
todo_[task].[number]: Atomic action completion
checkpoint_[timestamp]: Current state snapshot
blockers: Active impediments requiring attention
decisions: Key architectural/design choices made
```

## Examples

### Session 1: Start Authentication Task (Hybrid Tracking)
```
# Memory-based
list_memories() → Empty
write_memory("plan_auth", "Implement JWT authentication system")
write_memory("phase_1", "Analysis - security requirements review")

# Physical task creation
Create tasks/current/queue/task_1.1.json:
  {"id": "task_1.1", "description": "Review existing auth patterns", "phase": "1"}

# Combined tracking
write_memory("task_1.1", "pending: Review existing auth patterns")
Move queue/task_1.1.json → active.json
TodoWrite: Create 5 specific todos

# Execution
Execute task 1.1
write_memory("task_1.1", "completed: Found 3 patterns")
Move active.json → completed/task_1.1.timestamp.json
```

### Session 2: Resume After Interruption (Hybrid Recovery)
```
# Memory recovery
list_memories() → Shows plan_auth, phase_1, task_1.1

# Physical state recovery
Read tasks/current/checkpoint → Last state: "Completed task 1.1"
Read tasks/current/completed/ → See task_1.1 finished

# Synthesize context
read_memory("plan_auth") → "Implement JWT authentication system"
think_about_collected_information() → "Analysis complete, start implementation"

# Continue execution
write_memory("phase_2", "Implementation - middleware and endpoints")
Create tasks/current/queue/task_2.1.json
Continue with implementation tasks...
```

### Session 3: Completion Check (Hybrid Validation)
```
# Check both systems
think_about_whether_you_are_done() → "Testing phase remains incomplete"
list_memories() → See all phase memories
ls tasks/current/completed/ → Count completed tasks

# Complete remaining work
Complete remaining testing tasks
write_memory("outcome_auth", "Successfully implemented with 95% test coverage")

# Cleanup
delete_memory("checkpoint_*") → Clean temporary states
Archive tasks/current/ → tasks/archive/auth_system_timestamp/
write_memory("session_summary", "Auth system complete and validated")
```

## CLI Integration

Use `claude-ctx` CLI for task management:

```bash
# Resume last task
claude-ctx task resume

# Check task status
claude-ctx task status

# Mark task complete
claude-ctx task complete task_2.1

# View task history
ls ~/.claude/tasks/current/completed/
```