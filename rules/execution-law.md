# Execution Law

## MANDATORY - NO EXCEPTIONS

### 1. WRITE TO DISK
- Code blocks in chat = FAILURE
- Every code artifact MUST be written via file tools
- Verify with `ls -la` before claiming completion
- If file doesn't exist on disk, task is NOT done

### 2. PARALLEL BY DEFAULT
- Independent tasks execute SIMULTANEOUSLY
- Sequential only when Task B literally cannot start without Task A's output
- "Safer to go serial" = WRONG. Parallel is the default.
- Multi-file changes = batch into single parallel operation

### 3. RUN REVIEW GATE
Before marking ANY implementation task complete:
```bash
cortex review
```
This command:
- Activates context-appropriate reviewer agents
- Lists relevant skills to apply
- Outputs a completion checklist

DO NOT skip this step. DO NOT claim "I would run review" - ACTUALLY RUN IT.

### 4. READ SKILLS WHEN LISTED
If `cortex review` outputs skills, READ THEM before writing code:
```bash
cat skills/<skill-name>/SKILL.md
```
Skills contain patterns, anti-patterns, and best practices. Ignoring them = lower quality output.

### 5. PROOF OF WORK
After review gate, verify:
```
1. ls -la [files created/modified]
2. Run tests (not "will run" - ACTUALLY RUN)
3. Show output
```

No proof = not done.
