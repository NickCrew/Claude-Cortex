# Basic Usage Example

This document demonstrates a simple use case for the skill with annotated explanations.

## Scenario

**User Request**: "Help me [describe the task the user wants to accomplish]"

**Context**:
- Project type: [e.g., Python web application, TypeScript library]
- Existing codebase: [e.g., small startup, large enterprise]
- Constraints: [e.g., must maintain backward compatibility]

## Input

The user provides the following information or context:

```
[Example user input - this could be a description, code snippet, or specification]
```

### Key Input Elements

Annotated breakdown of what the skill extracts from the input:

| Element | Value | Why It Matters |
|---------|-------|----------------|
| Primary goal | [Description] | Determines which patterns to apply |
| Constraints | [List] | Shapes implementation approach |
| Quality requirements | [List] | Affects validation criteria |

## Processing Steps

How the skill processes this request:

### Step 1: Analyze Input

<!-- ANNOTATION: The skill first identifies the core request and any constraints -->

```
Analysis:
- Primary objective: [identified objective]
- Secondary needs: [identified secondary needs]
- Potential challenges: [anticipated issues]
```

### Step 2: Select Appropriate Pattern

<!-- ANNOTATION: Based on analysis, choose from the skill's pattern library -->

**Pattern Selected**: [Pattern Name from SKILL.md]

**Rationale**: This pattern was chosen because:
- [Reason 1 - relates to user's stated requirements]
- [Reason 2 - addresses identified constraints]
- [Reason 3 - aligns with quality requirements]

**Alternatives Considered**:
- [Alternative Pattern 1]: Not selected because [reason]
- [Alternative Pattern 2]: Not selected because [reason]

### Step 3: Apply Pattern

<!-- ANNOTATION: Demonstrate the actual implementation -->

```language
// Implementation applying the selected pattern
// Each section is annotated with explanations

/**
 * ANNOTATION: This comment explains WHY we're using this approach,
 * not just WHAT the code does.
 */
function implementedSolution(input) {
    // ANNOTATION: Validation first - following skill's best practices
    if (!isValid(input)) {
        throw new ValidationError('Input must meet criteria X');
    }

    // ANNOTATION: Core logic applies the pattern's main transformation
    const processed = applyTransformation(input);

    // ANNOTATION: Format output according to skill's standards
    return formatOutput(processed);
}
```

### Step 4: Validate Output

<!-- ANNOTATION: Check the output against the skill's quality criteria -->

**Validation Checklist**:
- [x] Meets primary objective
- [x] Satisfies all constraints
- [x] Follows skill's best practices
- [x] No anti-patterns present
- [x] Code is testable

## Output

The skill produces the following result:

```language
// Final output ready for use
// This is what the user receives

[Complete, working solution]
```

### Output Breakdown

| Component | Purpose | Quality Notes |
|-----------|---------|---------------|
| [Component 1] | [What it does] | [Why it's implemented this way] |
| [Component 2] | [What it does] | [Quality consideration] |
| [Component 3] | [What it does] | [Trade-off acknowledged] |

## Key Decisions Explained

### Decision 1: [Choice Made]

**What**: Description of the decision

**Why**: Rationale aligned with skill principles

**Trade-off**: What was sacrificed and why it was acceptable

### Decision 2: [Another Choice]

**What**: Description

**Why**: Rationale

**Alternative**: What could have been done differently and when that would be preferable

## Quality Assessment

Using the rubric from `validation/rubric.yaml`:

| Dimension | Score | Justification |
|-----------|-------|---------------|
| Clarity | 4/5 | Code is well-commented, structure is logical |
| Completeness | 5/5 | All requirements addressed, edge cases considered |
| Accuracy | 5/5 | Implementation is correct, follows best practices |
| Usefulness | 4/5 | Directly applicable, minor adaptation for specific contexts |

**Weighted Score**: 4.5/5 (Exceptional)

## Common Variations

### Variation A: Different Constraint

If the user had specified [different constraint], the approach would change:

```language
// Modified implementation for different constraint
modified_approach()
```

### Variation B: Different Scale

For larger scale applications:

```language
// Scaled implementation
scaled_approach()
```

## Testing the Example

To verify this example works correctly:

```language
// Test case demonstrating the example works
describe('Basic Usage Example', () => {
    it('produces expected output for standard input', () => {
        const input = prepareStandardInput();
        const result = implementedSolution(input);
        expect(result).toMatchExpectedOutput();
    });

    it('handles edge cases gracefully', () => {
        const edgeInput = prepareEdgeCaseInput();
        const result = implementedSolution(edgeInput);
        expect(result).toHandleEdgeCaseCorrectly();
    });
});
```

## What to Watch For

When adapting this example for your use case:

1. **Customize validation rules** - Your domain may have different constraints
2. **Adjust formatting** - Output format may need to match your conventions
3. **Add logging** - Production code should include appropriate logging
4. **Handle async** - If your implementation involves async operations, adjust accordingly

## Related Examples

- `examples/advanced.md` - More complex scenarios with multiple patterns
- `examples/integration.md` - Integration with external systems
- `examples/troubleshooting.md` - Common issues and fixes

---

*This example follows the annotated example pattern from the cortex cookbook.*
