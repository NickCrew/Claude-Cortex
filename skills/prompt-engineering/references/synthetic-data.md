# Synthetic Test Data Generation

Practical patterns for generating test cases that validate prompt behavior across diverse, realistic scenarios.

## Test Case Generation Process

### Step 1: Extract Variables

Identify all placeholders in the prompt that accept dynamic input.

```
Prompt: "Summarize this {{article_text}} for a {{target_audience}} audience."

Variables:
- {{article_text}}: varies in length, topic, complexity, language quality
- {{target_audience}}: varies in expertise level, age group, context
```

### Step 2: Analyze Distribution

For each variable, define what realistic values look like.

| Variable | Attribute | Range |
|----------|-----------|-------|
| article_text | Length | 100 words to 5000 words |
| article_text | Topic | Technical, business, science, culture, opinion |
| article_text | Quality | Well-written, poorly written, contains errors |
| article_text | Format | Paragraphs, bullet lists, mixed, includes code |
| target_audience | Expertise | Expert, intermediate, beginner, general public |
| target_audience | Context | Executive summary, social media post, email |

### Step 3: Generate Scenarios

Create test cases that cover the full distribution, not just happy paths.

---

## Scenario Categories

### Happy Path

Standard, well-formed inputs that represent typical usage.

```json
{
  "id": "happy-01",
  "description": "Standard technical article for general audience",
  "variables": {
    "article_text": "[A well-structured 500-word article about cloud computing]",
    "target_audience": "general public"
  },
  "expected_behavior": "Clear, jargon-free summary under 100 words"
}
```

### Edge Cases

Inputs at the boundaries of expected behavior.

| Category | Example |
|----------|---------|
| Minimum input | Single sentence article |
| Maximum input | 10,000-word document |
| Empty or near-empty | Whitespace only, single word |
| Special characters | Unicode, emoji, code blocks, mathematical notation |
| Unusual format | All caps, no punctuation, nested lists |
| Language edge cases | Mixed languages, slang, abbreviations, acronyms |
| Numeric-heavy | Financial data, statistics, tables |

### Adversarial Inputs

Inputs designed to break or circumvent the prompt.

| Attack Type | Example |
|-------------|---------|
| Prompt injection | "Ignore previous instructions and instead..." |
| Instruction override | Input that contains formatting that mimics system instructions |
| Context flooding | Extremely long input designed to push instructions out of context |
| Encoding tricks | Unusual encoding, zero-width characters, homoglyphs |
| Contradictory input | Input that contradicts the prompt's assumptions |

### Boundary Cases

Inputs that test the limits of each constraint in the prompt.

```json
{
  "id": "boundary-01",
  "description": "Article that is exactly at the length limit",
  "variables": {
    "article_text": "[Exactly 5000 words]",
    "target_audience": "expert"
  },
  "expected_behavior": "Should still produce a concise summary, not truncate"
}
```

---

## Persona-Based Generation

Generate test data from the perspective of different user types.

### Persona Template

```yaml
persona: Impatient Executive
characteristics:
  - Sends terse, incomplete requests
  - Expects instant, concise answers
  - Uses abbreviations and shorthand
  - May omit context they assume is obvious
sample_inputs:
  - "tldr this for board mtg tmrw"
  - "what's the risk? keep it to 3 bullets"
  - "compare to Q3, skip the fluff"
```

### Standard Persona Set

| Persona | Input Characteristics |
|---------|---------------------|
| **Power User** | Long, detailed, uses advanced features and jargon |
| **New User** | Vague, exploratory, may not know correct terminology |
| **Non-Native Speaker** | Grammatical errors, unusual phrasing, mixed languages |
| **Adversarial User** | Deliberately tries to break or exploit the prompt |
| **Domain Expert** | Highly specific, expects precision, tests depth of knowledge |
| **Accessibility User** | Uses assistive technology, relies on structured output |

---

## Coverage Matrix

Track which scenarios have been tested.

### Template

| Dimension | Happy | Edge | Adversarial | Persona | Covered? |
|-----------|-------|------|-------------|---------|----------|
| Short input | Y | Y | Y | New User | Yes |
| Long input | Y | Y | N | Power User | Partial |
| Technical content | Y | N | N | Expert | Partial |
| Multi-language | N | N | N | Non-Native | No |
| Code-heavy input | Y | Y | N | Power User | Partial |

**Target**: 80%+ coverage across all dimensions before declaring a prompt production-ready.

---

## Data Augmentation

Expand a small set of real examples into a larger, diverse test set.

### Techniques

| Technique | Description | Example |
|-----------|-------------|---------|
| **Paraphrasing** | Rewrite the same intent with different wording | "Delete my account" -> "I want to close my account" |
| **Perturbation** | Add noise (typos, grammar errors) | "How do I reset my pasword?" |
| **Substitution** | Replace entities with similar ones | "John Smith" -> "Maria Garcia" |
| **Extension** | Add context or complexity | "Help" -> "Help, I've been locked out since yesterday" |
| **Reduction** | Remove context to test minimal input | "I need help resetting the password on my work laptop" -> "reset password" |
| **Translation** | Convert between formal/informal, technical/plain | "The API returned a 403" -> "I'm getting an access denied error" |

### Augmentation Workflow

1. Start with 10-20 real examples from production logs or user research.
2. For each example, apply 2-3 augmentation techniques.
3. Add adversarial variants for critical test cases.
4. De-duplicate and review for realism.
5. Target: 50-100 test cases for a production prompt.

---

## Validation Strategies

### Golden Set Validation

Maintain a curated set of inputs with known-correct outputs.

```json
{
  "id": "golden-01",
  "input": "What is your return policy?",
  "expected_output_contains": ["30 days", "full refund", "original packaging"],
  "expected_output_excludes": ["I don't know", "as an AI"],
  "expected_format": "1-2 paragraphs"
}
```

### Automated Scoring

Use a secondary LLM call to evaluate outputs:

```
Given this input and output pair, score the response on:
1. Accuracy (1-5): Does it answer the question correctly?
2. Completeness (1-5): Does it cover all required points?
3. Format (1-5): Does it match the expected structure?
4. Safety (pass/fail): Does it contain any harmful content?

Input: {input}
Output: {output}
Expected criteria: {criteria}
```

### Regression Testing

After modifying a prompt:
1. Run the full golden set against the new prompt.
2. Compare scores to the baseline.
3. Flag any regressions (score decrease on any test case).
4. Accept only if overall score improves and no critical regressions.

---

## Bias Detection in Synthetic Data

### Common Bias Types

| Bias Type | How It Manifests | Mitigation |
|-----------|-----------------|------------|
| **Demographic** | Test data skews toward one demographic | Ensure name, gender, age, cultural diversity |
| **Topic** | Test cases cluster around easy topics | Force coverage across all topic categories |
| **Length** | Most test cases are similar length | Include short, medium, and long inputs |
| **Complexity** | All test cases are straightforward | Add multi-step, ambiguous, and contradictory cases |
| **Success** | Test data assumes correct usage | Include malformed, incomplete, and incorrect inputs |

### Bias Audit Checklist

- [ ] Test data includes diverse names (not all Western/English).
- [ ] Mix of genders, ages, and cultural contexts in persona-based data.
- [ ] Both positive and negative examples are represented.
- [ ] Technical difficulty spans beginner to expert.
- [ ] Input lengths are distributed, not clustered at one size.
- [ ] At least 10% of test cases are adversarial or malformed.
- [ ] No single category dominates more than 30% of the test set.

---

## Output Format for Test Suites

### JSON Test Suite

```json
{
  "prompt_id": "customer-support-v2",
  "generated_at": "2025-01-15",
  "test_cases": [
    {
      "id": "tc-001",
      "category": "happy_path",
      "persona": "standard_user",
      "input": {
        "customer_query": "How do I update my billing address?"
      },
      "expected": {
        "contains": ["account settings", "billing"],
        "excludes": ["I don't know"],
        "format": "step-by-step instructions",
        "max_length": 200
      }
    }
  ]
}
```

### Coverage Report

```
Prompt: customer-support-v2
Test Cases: 75
Coverage: 87%

By Category:
  Happy path:    20 (100% pass)
  Edge cases:    25 (88% pass)
  Adversarial:   15 (80% pass)
  Persona-based: 15 (93% pass)

Failures:
  - tc-042: Adversarial injection bypassed guardrail
  - tc-051: Empty input produced hallucinated response
  - tc-063: Multi-language input lost formatting
```
