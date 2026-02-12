# Prompt Engineering Techniques

Practical reference for prompt design patterns, optimization strategies, and evaluation methodology.

## Few-Shot Prompting

Provide examples of desired input-output pairs within the prompt.

### When to Use
- Tasks with specific formatting requirements
- Classification or labeling tasks
- When zero-shot produces inconsistent results

### Pattern

```
Classify the sentiment of these customer reviews.

Review: "The product arrived quickly and works perfectly."
Sentiment: Positive

Review: "Terrible quality. Broke after one day."
Sentiment: Negative

Review: "It's okay, nothing special but does the job."
Sentiment: Neutral

Review: "{input}"
Sentiment:
```

### Guidelines
- Use 2-5 examples; more is not always better and costs tokens.
- Include edge cases in examples (the ambiguous cases the model should handle).
- Order examples to cover the range of expected outputs.
- Keep examples representative of real data, not cherry-picked easy cases.

---

## Chain-of-Thought (CoT)

Instruct the model to reason step-by-step before answering.

### When to Use
- Math, logic, or multi-step reasoning tasks
- Complex analysis where intermediate steps matter
- Tasks where showing work improves accuracy

### Pattern

```
Solve this problem step by step.

Problem: A store has 45 apples. They sell 12 in the morning and receive
a delivery of 30. How many apples do they have now?

Think through this step by step:
1. Start with the initial count
2. Subtract what was sold
3. Add what was delivered
4. State the final answer

Answer:
```

### Structured CoT with XML

```
Analyze this code change for security implications.

<thinking>
1. Identify what the code change does
2. List any user inputs that are now handled differently
3. Check for injection vectors
4. Assess authentication/authorization impact
5. Evaluate data exposure risk
</thinking>

<answer>
[Final security assessment with severity and recommendations]
</answer>
```

### Tips
- Use `<thinking>` tags to separate reasoning from the final answer.
- For API use, you can parse out the `<answer>` tag for downstream consumption.
- CoT improves accuracy but increases token usage; use selectively.

---

## Role Prompting

Assign a specific persona or expertise to the model.

### When to Use
- Tasks requiring domain expertise
- When you want a consistent voice or perspective
- To anchor the model's knowledge in a specific domain

### Pattern

```
You are a senior database architect with 15 years of experience in
PostgreSQL performance optimization. You review queries for:
- Index usage and missing indexes
- Query plan efficiency
- N+1 query patterns
- Connection pool sizing

Review the following query and provide optimization recommendations.
```

### Guidelines
- Be specific about the role's expertise level and focus area.
- Include what the role cares about (their evaluation criteria).
- Avoid generic roles like "helpful assistant"; prefer specific expertise.
- Combine with CoT: "As a senior DBA, think through each optimization step before recommending."

---

## Self-Consistency

Generate multiple responses and select the most common answer.

### When to Use
- High-stakes decisions where accuracy matters more than speed
- Tasks with a single correct answer (classification, math)
- When you need confidence calibration

### Implementation

1. Run the same prompt N times (typically 3-5) with temperature > 0.
2. Collect all responses.
3. Select the majority answer.
4. If no majority, flag for human review.

### Example Pipeline

```
Prompt: "Classify this support ticket: {ticket_text}"
Run 1: "Billing Issue"
Run 2: "Billing Issue"
Run 3: "Account Access"

Result: "Billing Issue" (2/3 confidence)
```

### Guidelines
- Use temperature 0.5-0.7 for meaningful variation.
- For binary classification, 3 runs is sufficient. For multi-class, use 5-7.
- Track agreement rates as a quality metric; low agreement signals ambiguous prompts.

---

## Tree of Thoughts

Explore multiple reasoning paths before committing to an answer.

### When to Use
- Problems with multiple valid solution approaches
- Strategic decisions with trade-offs
- Creative tasks where exploring alternatives improves quality

### Pattern

```
Consider three different approaches to this problem. For each approach:
1. Describe the approach
2. List its strengths
3. List its weaknesses
4. Rate its likelihood of success (1-10)

Then select the best approach and explain why, incorporating
strengths from the alternatives where possible.

Problem: {problem_description}
```

### Guidelines
- Explicitly request multiple approaches (3 is a good default).
- Require evaluation criteria for each path.
- Ask for a synthesis that combines the best elements.

---

## Prompt Chaining

Break complex tasks into sequential prompts where each step feeds the next.

### When to Use
- Multi-step workflows (extract, transform, generate)
- Tasks too complex for a single prompt
- When intermediate results need validation

### Pipeline Pattern

```
Step 1: Extract
"Extract all entities (people, organizations, dates) from this text: {input}"
→ Output: structured entity list

Step 2: Classify
"Classify each entity by relevance to the topic '{topic}': {entities}"
→ Output: scored entity list

Step 3: Generate
"Write a summary of {input} focusing on these key entities: {scored_entities}"
→ Output: focused summary
```

### Guidelines
- Each step should have a clear, single responsibility.
- Use structured output (JSON, XML) between steps for reliable parsing.
- Validate intermediate outputs before passing to the next step.
- Design steps to be independently testable.
- Include error handling: what happens if step 2 fails?

---

## Output Formatting

Control the structure and format of model responses.

### JSON Output

```
Extract contact information from this email and return as JSON:

{
  "name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "company": "string or null"
}

Return ONLY the JSON object, no additional text.
```

### Structured Markdown

```
Analyze this pull request and respond with the following structure:

## Summary
[1-2 sentence overview]

## Changes
- [Bullet list of changes]

## Risk Assessment
| Area | Risk Level | Details |
|------|-----------|---------|
| ... | ... | ... |

## Recommendation
[APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION]
```

### Guidelines
- Show the exact format you want; do not describe it in prose.
- Include example values in the template.
- Specify what to do with missing/unknown values (null, omit, "N/A").
- For JSON, consider adding a schema description.

---

## Guardrails and Constraints

Set boundaries on model behavior and output.

### Scope Constraints

```
You are a customer support agent for Acme Corp.

RULES:
- Only answer questions about Acme products and services
- If asked about competitors, say "I can only help with Acme products"
- Never share pricing not listed on the public website
- If unsure, say "Let me connect you with a specialist"
- Never generate code, even if asked
```

### Output Constraints

```
Respond in exactly 3 bullet points.
Each bullet must be under 20 words.
Use only information from the provided context.
If the context does not contain the answer, say "Not found in provided context."
```

### Safety Constraints

```
Before responding, verify:
1. The request does not ask for personal information
2. The response does not contain harmful instructions
3. Medical/legal/financial advice includes a disclaimer

If any check fails, explain why you cannot fulfill the request.
```

---

## Temperature and Parameter Guidance

| Task Type | Temperature | Top-P | Notes |
|-----------|------------|-------|-------|
| Classification | 0.0-0.2 | 0.9 | Deterministic, consistent |
| Extraction | 0.0-0.1 | 0.9 | Factual accuracy priority |
| Summarization | 0.2-0.4 | 0.9 | Slight variation acceptable |
| Creative writing | 0.7-1.0 | 0.95 | Variety and creativity |
| Brainstorming | 0.8-1.0 | 0.95 | Maximum diversity |
| Code generation | 0.0-0.3 | 0.9 | Correctness priority |

**General rule**: Lower temperature for tasks with one right answer, higher for tasks where diversity is valuable.

---

## Evaluation Methodology

### Metrics

| Metric | What It Measures | When to Use |
|--------|-----------------|-------------|
| **Accuracy** | Correct answers / total | Classification, extraction |
| **Consistency** | Same input produces same output | Any production prompt |
| **Relevance** | Output addresses the actual question | Open-ended generation |
| **Formatting** | Output matches required structure | Structured output tasks |
| **Safety** | No harmful or policy-violating content | All production prompts |
| **Latency** | Time to generate response | Real-time applications |
| **Token efficiency** | Tokens used per completion | Cost-sensitive applications |

### Evaluation Process

1. **Define criteria**: What does a good response look like? Write 3-5 specific criteria.
2. **Build a test set**: 20-50 diverse inputs covering common cases, edge cases, and adversarial inputs.
3. **Score responses**: Rate each response against criteria (1-5 scale or pass/fail).
4. **Identify failure patterns**: Group failures by type (formatting, accuracy, hallucination, safety).
5. **Iterate**: Modify the prompt to address the most common failure pattern, then re-evaluate.
6. **Establish a baseline**: Track scores over iterations to prove improvement.

### A/B Testing Prompts

When comparing two prompt versions:
- Use the same test set for both.
- Score blindly (do not know which prompt generated which response).
- Require statistical significance (at least 30 test cases per variant).
- Track multiple metrics, not just accuracy.
