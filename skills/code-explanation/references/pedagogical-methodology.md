# Pedagogical Methodology

Reference for explaining code and concepts using proven teaching frameworks, with strategies for different audience levels and learning styles.

## Teaching Frameworks

### Bloom's Taxonomy Applied to Code

Use Bloom's levels to calibrate explanation depth and exercise design.

| Level | Code Application | Example Prompt |
| --- | --- | --- |
| **Remember** | Recall syntax, name functions | "What does `map()` return?" |
| **Understand** | Explain what code does in own words | "Describe what this loop accomplishes" |
| **Apply** | Use a pattern in a new context | "Write a function that filters using this pattern" |
| **Analyze** | Break apart code structure, trace data flow | "Why does this produce a race condition?" |
| **Evaluate** | Compare approaches, judge trade-offs | "Which caching strategy fits this workload?" |
| **Create** | Design and implement a novel solution | "Architect a pub/sub system for these requirements" |

Target explanations to the learner's current level and exercises to one level above.

### Scaffolded Learning

Build understanding incrementally by layering support:

1. **Model**: Show a complete working example with narration
2. **Guide**: Provide a partial solution with hints for the learner to complete
3. **Fade**: Remove scaffolding progressively until the learner works independently
4. **Assess**: Verify the learner can apply the concept without support

### Concrete-Representational-Abstract (CRA)

1. **Concrete**: Start with a tangible, real-world analogy or physical metaphor
2. **Representational**: Show a diagram, flowchart, or visual model
3. **Abstract**: Present the formal code, algorithm, or API

## Progressive Learning Design

### Beginner Track

- Define every term on first use
- One concept per section
- Every code example runs as-is (no missing imports or context)
- Explicit "what just happened" summaries after each example
- Exercises: fill in blanks, predict output, fix a small bug

### Intermediate Track

- Assume familiarity with language basics
- Focus on patterns, idioms, and "why" over "what"
- Compare multiple approaches with trade-off analysis
- Exercises: extend an example, refactor for readability, add error handling

### Advanced Track

- Reference-style with links to source code and specs
- Focus on internals, performance, edge cases, and design decisions
- Exercises: design a component, optimize for a constraint, review real-world code

### Track Selection Heuristic

Ask or infer:
- Can the learner read the language's basic syntax? If no, use beginner track.
- Can they explain the concept in their own words? If no, use intermediate track.
- Are they asking about trade-offs, internals, or alternatives? Use advanced track.

## Explanation Patterns

### Analogy

Map unfamiliar concepts to familiar ones, then identify where the analogy breaks.

```
Template:
"[Concept] works like [familiar thing] because [shared property].
The difference is [where analogy breaks]."

Example:
"A Promise works like an order receipt at a restaurant.
You get the receipt immediately (the Promise), but the food (the value)
arrives later. The difference: a Promise can also tell you if the kitchen
caught fire (rejection), which receipts don't do."
```

### Visualization

Use text diagrams or Mermaid to show data flow, state transitions, or structure.

```
Request → Middleware → Route Handler → Database
                ↓              ↓
            Logging        Validation
```

When to visualize:
- Data flowing through a pipeline
- State machines and lifecycle transitions
- Tree/graph structures (DOM, AST, dependency graphs)
- Sequence of operations across components

### Worked Examples

Walk through a problem step by step, showing the reasoning at each stage.

```
Template:
1. State the problem
2. Identify what we know
3. Choose an approach (explain why)
4. Execute step by step (show intermediate state)
5. Verify the result
6. Reflect: what would change if [variation]?
```

### Socratic Questioning

Guide the learner to discover the answer rather than stating it directly.

| Purpose | Question Type | Example |
| --- | --- | --- |
| Clarify | "What do you mean by...?" | "What do you expect this function to return?" |
| Probe assumptions | "Why do you think...?" | "Why does this need to be synchronous?" |
| Explore alternatives | "What if...?" | "What if the input array is empty?" |
| Test implications | "What follows from...?" | "If we cache this, what happens on update?" |
| Surface reasoning | "How did you arrive at...?" | "What led you to use recursion here?" |

Use Socratic questioning when the learner is close to the answer or has a misconception to unpack. Avoid it when they lack the prerequisite knowledge to reason about the question.

## Understanding Verification

### Exercise Types by Bloom's Level

- **Recall**: "What does this function return when called with X?"
- **Comprehension**: "Explain this code block in plain language"
- **Application**: "Modify this code to handle edge case Y"
- **Analysis**: "Trace the execution and explain why bug Z occurs"
- **Evaluation**: "Compare approach A vs B for this scenario"
- **Creation**: "Design a solution for this requirement"

### Self-Assessment Prompts

Provide these after an explanation so learners can gauge their understanding:

```
Check your understanding:
- [ ] Can you explain [concept] without looking at the example?
- [ ] Can you predict what happens if [variation]?
- [ ] Could you implement this from scratch?
- [ ] Can you explain why this approach was chosen over alternatives?
```

### Knowledge Checks

Short inline checks embedded within longer explanations:

```
> **Quick check**: Before reading on, what do you think happens
> when `fetch()` is called with an invalid URL? Try it in your
> console, then continue.
```

## Concept Prerequisite Mapping

Before explaining a concept, identify and address its prerequisites.

```
Template:
Target concept: [X]
Prerequisites:
  1. [Prerequisite A] -- assumed / needs brief review / needs full explanation
  2. [Prerequisite B] -- assumed / needs brief review / needs full explanation
Approach: Address gaps first, then proceed to target concept.
```

### Example Prerequisite Chain

```
async/await
  ├── Promises
  │     ├── Callbacks
  │     │     └── Functions as first-class values
  │     └── Event loop basics
  └── try/catch (for error handling)
```

When a prerequisite gap is detected:
1. Provide a brief refresher (2-3 sentences + one example) if the gap is small
2. Link to a full explanation and pause if the gap is large
3. Never skip prerequisites -- the explanation will fail if built on shaky ground

## Multi-Level Explanation Strategies

### ELI5 (Explain Like I'm 5)

- Use everyday analogies with no technical terms
- One core idea only, no caveats or edge cases
- "Think of it like..."

### Intermediate

- Use correct terminology with brief definitions
- Show one clear code example with annotations
- Cover the main use case and one common gotcha
- "Here's how it works and when to use it..."

### Expert

- Reference specs, implementation details, or source code
- Compare with alternatives and analyze trade-offs
- Cover performance characteristics and edge cases
- "Under the hood, this works by..."

### Layered Explanation Template

```
## [Concept Name]

**In a nutshell**: [One sentence, no jargon]

**How it works**: [2-3 paragraphs with terminology, examples, and a code sample]

**Under the hood**: [Implementation details, performance notes, edge cases]
```

Use the layered approach when the audience is mixed or unknown. The reader self-selects their depth by reading further or stopping.
