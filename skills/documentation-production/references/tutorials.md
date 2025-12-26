# Reference: tutorials

# /docs:tutorials - Hands-On Tutorial Builder

## Triggers
- Requests for step-by-step tutorials or workshops
- Hands-on learning content for frameworks or features
- Guides needing exercises, checkpoints, and troubleshooting
- Multi-part workshop or deep-dive tutorial plans

## Usage
```
/docs:tutorials [topic] [--format quickstart|deep-dive|workshop|cookbook] [--level beginner|intermediate|advanced]
```

## Behavioral Flow
1. **Define**: Learning objectives, prerequisites, and outcomes
2. **Design**: Break topics into progressive, runnable steps
3. **Build**: Create exercises, challenges, and validation checkpoints
4. **Deliver**: Provide troubleshooting, tips, and next steps

Key behaviors:
- Show, then explain
- Include runnable examples and expected output
- Add checkpoints and error recovery guidance

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Multi-part tutorials or workshop series
- ✅ Tutorials with >10 steps or multiple tracks
- ✅ Content requiring multiple learning styles

**Available subagents**:
- **tutorial-engineer**: Tutorial structure, exercises, troubleshooting, and formatting

**Delegation strategy**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>tutorial-engineer</subagent_type>
  <description>Generate a full tutorial for the requested topic</description>
  <prompt>
    Create a tutorial with:
    - Objectives, prerequisites, and time estimate
    - Progressive steps with runnable code
    - Exercises, checkpoints, and troubleshooting
    - Summary and next steps
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Small quickstart with <5 steps
- ❌ Minor edits to existing tutorials

## Tool Coordination
- **Task tool**: Delegates to tutorial-engineer for full tutorial creation
- **Read**: Ingest specs or existing docs
- **Write**: Deliver tutorial content in Markdown

## Examples

### Quick Start
```
/docs:tutorials "Build a REST API in FastAPI" --format quickstart
```

### Deep Dive
```
/docs:tutorials "React Server Components" --format deep-dive --level advanced
```

### Workshop Series
```
/docs:tutorials "Kubernetes fundamentals" --format workshop --level beginner
```

## Boundaries

**Will:**
- Produce hands-on tutorials with exercises and checkpoints
- Add troubleshooting guidance and validation steps

**Will Not:**
- Ship tutorials without runnable examples
- Skip prerequisite setup steps when required
