# Sequential MCP Server

**Purpose**: Structured multi-step reasoning, hypothesis testing, and systematic problem-solving

## Triggers
- Complex debugging requiring methodical investigation
- System design and architecture decisions
- Multi-component analysis with dependencies
- Root cause analysis for production issues
- Hypothesis-driven development and testing
- Decision trees with multiple branches

## Choose When
- **Over native reasoning**: When problems require explicit reasoning steps
- **Over Context7**: When you need to reason about implementation, not just lookup docs
- **For debugging**: Systematic hypothesis testing vs trial-and-error
- **For architecture**: Structured evaluation of design alternatives
- **For complexity**: When mental models need to be explicit and tracked
- **For verification**: When each step must be validated before proceeding

## Works Best With
- **Context7**: Sequential reasons about implementation → Context7 validates patterns
- **Codanna**: Sequential analyzes architecture → Codanna maps symbols and dependencies
- **Magic**: Sequential designs component → Magic generates implementation

## Core Capabilities
- **Hypothesis generation**: Create testable theories about problems
- **Sequential validation**: Test hypotheses in logical order
- **Decision tracking**: Record reasoning path and alternatives considered
- **Backtracking**: Revisit assumptions when hypotheses fail
- **Parallel hypotheses**: Evaluate multiple theories simultaneously
- **Conclusion synthesis**: Combine findings into actionable recommendations

## Examples
```
"why is the API slow?" → Sequential (systematic performance analysis)
"choose between REST and GraphQL" → Sequential (structured decision-making)
"debug this memory leak" → Sequential (hypothesis-driven debugging)
"design the authentication system" → Sequential (architectural reasoning)
"analyze this error pattern" → Sequential (root cause investigation)
"what's 2+2?" → Native Claude (simple calculation, no reasoning needed)
```

## Reasoning Workflow

### Phase 1: Problem Definition
- Understand the question or issue
- Identify knowns and unknowns
- Define success criteria

### Phase 2: Hypothesis Generation
- Create testable theories
- Prioritize by likelihood
- Consider alternatives

### Phase 3: Sequential Testing
- Test hypotheses in order
- Record results
- Adjust based on findings

### Phase 4: Synthesis
- Combine validated findings
- Recommend solution
- Document reasoning path

## Performance Considerations
- **Depth control**: Use `--think`, `--think-hard`, or `--ultrathink` for depth
- **Time vs accuracy**: More steps = better accuracy but slower
- **Token budget**: Deep reasoning uses more tokens
- **Parallel hypotheses**: Can test multiple theories simultaneously

## Integration Patterns

### With Context7 (Framework-Compliant Design):
```
1. Sequential: Reason about design alternatives
2. Context7: Validate against official patterns
3. Sequential: Synthesize compliant solution
```

### With Codanna (Architecture Understanding):
```
1. Codanna: Map current architecture and symbols
2. Sequential: Reason about improvements
3. Codanna: Analyze impact of changes
```

## Quality Gates
When using Sequential, ensure:
- [ ] Problem clearly defined before reasoning
- [ ] Hypotheses specific and testable
- [ ] Each step validated before proceeding
- [ ] Alternatives considered and documented
- [ ] Final recommendation backed by evidence
- [ ] Reasoning path traceable and reproducible
