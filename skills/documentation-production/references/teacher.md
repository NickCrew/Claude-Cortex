# Reference: teacher

# /docs:teacher - Concept Explanations & Learning Paths

## Triggers
- Requests for clear explanations of complex programming concepts
- Educational content for algorithms or system behavior
- Learning path design and progressive skill development
- Structured exercises to verify understanding

## Usage
```
/docs:teacher [topic] [--level beginner|intermediate|advanced] [--format lesson|path|exercise]
```

## Behavioral Flow
1. **Assess**: Determine learner baseline and prerequisites
2. **Explain**: Break down concepts with clear, practical examples
3. **Practice**: Provide exercises and guided application
4. **Verify**: Validate understanding with checkpoints and summaries

Key behaviors:
- Teach understanding, not memorization
- Provide multiple explanation angles
- Always include practical examples

## Delegation Protocol

**When to delegate** (use Task tool):
- ✅ Multi-topic learning paths
- ✅ Extensive tutorial sets or curricula
- ✅ Large exercise banks

**Available subagents**:
- **learning-guide**: Concept explanation, learning paths, exercises

**Delegation strategy**:
```xml
<function_calls>
<invoke name="Task">
  <subagent_type>learning-guide</subagent_type>
  <description>Develop a learning guide for the requested topic</description>
  <prompt>
    Build a learning guide with:
    - Concept breakdown
    - Progressive examples
    - Exercises and checkpoints
    - Verification questions
  </prompt>
</invoke>
</function_calls>
```

**When NOT to delegate** (use direct tools):
- ❌ Short explanations or small snippets
- ❌ Single function or concept notes

## Tool Coordination
- **Task tool**: Delegates to learning-guide for full learning plans
- **Read**: Reference source material
- **Write**: Generate lesson or exercise content

## Examples

### Concept Explanation
```
/docs:teacher "async/await" --level beginner --format lesson
```

### Learning Path
```
/docs:teacher "distributed systems" --format path --level intermediate
```

### Exercises
```
/docs:teacher "binary search" --format exercise
```

## Boundaries

**Will:**
- Provide clear educational explanations with exercises
- Build learning paths with progressive skill development

**Will Not:**
- Provide answers without explanation or context
- Skip prerequisites that are necessary for comprehension
