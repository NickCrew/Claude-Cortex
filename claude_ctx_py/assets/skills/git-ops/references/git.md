# Reference: git

# /dev:git - Git Operations

## Triggers
- Git repository operations: status, add, commit, push, pull, branch
- Need for intelligent commit message generation
- Repository workflow optimization requests
- Branch management and merge operations

## Usage
```
/dev:git [operation] [args] [--smart-commit] [--interactive]
```

## Behavioral Flow
1. **Analyze**: Check repository state and working directory changes
2. **Validate**: Ensure operation is appropriate for current Git context
3. **Execute**: Run Git command with intelligent automation
4. **Optimize**: Apply smart commit messages and workflow patterns
5. **Report**: Provide status and next steps guidance

Key behaviors:
- Generate conventional commit messages based on change analysis
- Apply consistent branch naming conventions
- Handle merge conflicts with guided resolution
- Provide clear status summaries and workflow recommendations
- Do not sign off commits or name yourself as co-author

## Personas (Thinking Modes)
- **developer**: Code change understanding, commit message clarity, branch workflow
- **devops-engineer**: Repository optimization, workflow best practices, team coordination

## Delegation Protocol

**This command does NOT delegate** - Git operations are direct bash commands.

**Why no delegation**:
- ❌ Git commands are fast, atomic operations
- ❌ Commit message generation is simple analysis
- ❌ Status/log parsing doesn't require subagents
- ❌ Operations complete in <5 seconds

**All work done directly**:
- Bash executes git commands
- Direct analysis of diffs for commit messages
- Simple pattern matching for status

**Note**: While this command doesn't use Task tool, it still benefits from personas for intelligent commit message generation and workflow guidance.

## Tool Coordination
- **Bash**: Git command execution (all operations direct)
- **Read**: Repository state analysis (direct)
- **Grep**: Log parsing and status analysis (direct)
- **Write**: Commit message generation (direct)

## Key Patterns
- **Smart Commits**: Analyze changes → generate conventional commit message
- **Status Analysis**: Repository state → actionable recommendations
- **Branch Strategy**: Consistent naming and workflow enforcement
- **Error Recovery**: Conflict resolution and state restoration guidance

## Examples

### Smart Status Analysis
```
/dev:git status
# Analyzes repository state with change summary
# Provides next steps and workflow recommendations
```

### Intelligent Commit
```
/dev:git commit --smart-commit
# Generates conventional commit message from change analysis
# Applies best practices and consistent formatting
```

### Interactive Operations
```
/dev:git merge feature-branch --interactive
# Guided merge with conflict resolution assistance
```

## Boundaries

**Will:**
- Execute Git operations with intelligent automation
- Generate conventional commit messages from change analysis
- Provide workflow optimization and best practice guidance

**Will Not:**
- Modify repository configuration without explicit authorization
- Execute destructive operations without confirmation
- Handle complex merges requiring manual intervention
