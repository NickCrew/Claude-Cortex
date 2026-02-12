# Questioning Techniques Reference

Socratic method applied to programming education, with question types and scaffolding progressions.

## Socratic Method Applied to Code

The Socratic method in code education replaces direct instruction with guided discovery.
Instead of telling a developer "this function violates SRP," lead them to discover it
through observation and reasoning.

### The Three Moves

| Move | Purpose | Example |
|------|---------|---------|
| **Clarifying** | Expose assumptions, sharpen definitions | "What do you mean by 'handles authentication'? What specific steps does that involve?" |
| **Probing assumptions** | Challenge unstated beliefs | "Why do you assume this function needs to do both validation and persistence?" |
| **Probing reasons/evidence** | Demand justification | "What evidence in the code tells you this approach is working well? What would it look like if it weren't?" |

### Applied to Code Review

```
Code under review: A 200-line function that validates input, queries a database,
transforms results, and sends a notification.

Clarifying:
  "If you had to write a one-sentence description of what this function does,
   what would it be?"
  → Learner struggles to write one sentence → discovers it does too much.

Probing assumptions:
  "What would happen if the notification service is down? Does validation
   still need to complete?"
  → Learner realizes unrelated concerns are coupled.

Probing evidence:
  "How would you test just the validation logic in isolation?"
  → Learner discovers the function is untestable without the database.
```

---

## Question Types and When to Use Them

### Observation Questions

**Purpose**: Get the learner to look closely at the code.

| Question | When to use |
|----------|-------------|
| "What do you notice about this function's name?" | The name doesn't match behavior |
| "How many parameters does this function take?" | Parameter list is too long |
| "What types does this function return?" | Return type is unclear or inconsistent |
| "How many lines is this function?" | Function is too long |
| "What dependencies does this class have?" | Too many dependencies injected |

### Pattern Recognition Questions

**Purpose**: Help the learner see recurring structures.

| Question | When to use |
|----------|-------------|
| "Do you see any similar blocks of code in this file?" | Duplication exists |
| "What pattern do the method names follow?" | Naming is inconsistent |
| "How does this class communicate with its collaborators?" | Coupling patterns |
| "What happens when you trace the flow from input to output?" | Complex control flow |
| "Where does the logic branch? How many paths are there?" | High cyclomatic complexity |

### Principle Discovery Questions

**Purpose**: Guide the learner from observation to principle.

| Question | Target principle |
|----------|----------------|
| "If this function's name perfectly described what it does, what would change?" | Meaningful names |
| "What if each responsibility had its own function?" | Single Responsibility |
| "If you needed to swap the database, what would you have to change?" | Dependency Inversion |
| "What would the code look like if you never had to modify this class to add a new type?" | Open/Closed Principle |
| "How could you test this function without a network connection?" | Dependency Injection |

### Synthesis Questions

**Purpose**: Connect discoveries to broader understanding.

| Question | When to use |
|----------|-------------|
| "How does what you discovered here relate to [previous principle]?" | Connecting concepts |
| "If you were writing this from scratch, what would you do differently?" | Integrating lessons |
| "What would you tell a teammate who wrote this code?" | Testing understanding |
| "Where else in the codebase might this pattern be hiding?" | Generalizing |

---

## Scaffolding Progression

### Level-Adaptive Approach

Adjust question depth based on the learner's level:

#### Beginner (High Guidance)

- Ask concrete observation questions
- Provide clear hints when the learner is stuck
- Name principles immediately after discovery
- Use simple, familiar examples

```
Q: "What do you see when you look at this variable name — 'd'?"
A: [Learner observes it's unclear]
Q: "If you came back to this code in 3 months, would you remember what 'd' means?"
A: [Learner recognizes the problem]
→ "This connects to what Robert Martin calls 'intention-revealing names.'"
```

#### Intermediate (Medium Guidance)

- Ask pattern recognition questions
- Give discovery hints only when truly stuck
- Let the learner name the principle before confirming
- Use real codebase examples

```
Q: "What pattern do you see in how these three classes handle errors?"
A: [Learner identifies duplication or inconsistency]
Q: "What principle might help here?"
A: [Learner suggests an approach]
→ "That aligns with [principle]. How would you apply it?"
```

#### Advanced (Low Guidance)

- Ask synthesis and application questions
- Expect the learner to identify both problem and principle
- Challenge them to find edge cases and trade-offs
- Use complex, ambiguous scenarios

```
Q: "How might this principle apply to your current architecture?"
A: [Learner proposes application]
Q: "What are the trade-offs of that approach?"
A: [Learner identifies downsides]
→ "Exactly. Now, how would you decide which trade-off is acceptable?"
```

### Progression Within a Single Session

A session typically moves through these phases:

```
1. Warm-up (2-3 observation questions)
   → Establish what the learner sees

2. Deepening (3-5 pattern/principle questions)
   → Guide toward the core insight

3. Naming (1 confirmation)
   → Name the principle after discovery

4. Application (2-3 synthesis questions)
   → Apply the principle to a new context

5. Wrap-up (1-2 reflection questions)
   → "What will you do differently now?"
```

### Handling Wrong Answers

When a learner gives an incorrect or incomplete answer:

| Situation | Response strategy |
|-----------|-------------------|
| Partially correct | "That's part of it. What else might be going on?" |
| Confidently wrong | "Interesting. What would happen if you tested that assumption?" |
| Stuck/silent | "Let's look at it from a different angle. What if [simpler question]?" |
| Off-track | "That's a valid observation about [what they said]. How does it connect to [the actual focus]?" |

Never say "that's wrong." Redirect with a question that exposes the gap.

### Knowing When to Tell

The Socratic method has limits. Switch to direct instruction when:

- The learner is frustrated after 3+ attempts at the same concept
- The concept requires background knowledge the learner doesn't have
- Time constraints make discovery impractical
- The learner explicitly asks for a direct explanation

Even in direct instruction mode, follow up with a question: "Now that you know [concept], where would you apply it in this code?"
