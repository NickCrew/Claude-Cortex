# Cookbook Insights & Integration Strategy

This document synthesizes key patterns and techniques extracted from the `claude-cookbooks` repository, specifically focusing on Frontend Aesthetics, Metaprompting, and RAG strategies. These insights are intended to enhance the `cortex-plugin` framework.

## 1. Frontend Aesthetics Generation

**Source:** `claude-resources/claude-cookbooks/coding/prompting_for_frontend_aesthetics.ipynb`

### The Problem
Claude tends to default to "safe," generic designs (e.g., "AI slop" with purple gradients and Inter/Roboto fonts) unless explicitly guided.

### Strategies
1.  **Guide Specific Dimensions:** Targeted instructions for Typography, Color/Theme, Motion, and Backgrounds.
2.  **Reference Inspirations:** Mention specific aesthetics (e.g., "Solarpunk", "IDE themes").
3.  **Negative Constraints:** Explicitly forbid common defaults (Inter, Arial, purple gradients).

### Integration: `prompts/templates/frontend-aesthetics.md`

We should add a reusable prompt template for high-quality frontend generation.

```markdown
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. Avoid this. Focus on:

**Typography:**
- Avoid generic fonts (Arial, Inter, Roboto).
- Use distinctive choices (JetBrains Mono, Playfair Display, Space Grotesk).
- Use extreme weights (100/900) rather than safe middles (400/600).

**Color & Theme:**
- Commit to a cohesive aesthetic (e.g., Solarpunk, Swiss Style, Brutalism).
- Use CSS variables for consistency.
- Avoid "clichéd" purple-on-white gradients.

**Motion:**
- Prioritize CSS-only animations.
- Focus on high-impact page load reveals (staggered `animation-delay`).

**Backgrounds:**
- Create depth with layered gradients, noise, or geometric patterns.
- Avoid flat solid colors.

**Interpret creatively:** Make unexpected choices that feel genuinely designed.
</frontend_aesthetics>
```

### Proposed Slash Command
A `/design` command could inject this prompt automatically when the user asks for UI components.

## 2. Metaprompting (Prompt Optimization)

**Source:** `claude-resources/claude-cookbooks/misc/metaprompt.ipynb`

### The Concept
A "Metaprompt" is a powerful multi-shot prompt that instructs Claude to act as an expert Prompt Engineer. It takes a raw task description and outputs a structured, high-performance prompt template.

### Key Patterns
*   **Variable Separation:** Define inputs explicitly (e.g., `{$FAQ}`, `{$QUESTION}`) in `<Inputs>` tags.
*   **Chain of Thought (CoT):** Instruct the model to use `<thinking>` tags before `<answer>` tags to improve reasoning.
*   **Structured Output:** Use XML tags for all sections (e.g., `<instructions>`, `<example>`, `<scratchpad>`).
*   **Example-Driven:** The metaprompt itself contains 5-6 examples of "Task -> Good Prompt" pairs to few-shot prompt Claude.

### Integration Strategy
1.  **Enhance `prompt-engineer` Agent:** Update the `agents/prompt-engineer.md` system prompt to utilize this specific metaprompt structure when asked to "optimize a prompt".
2.  **New Command:** `cortex prompts optimize <file>` could run the metaprompt logic against an existing user prompt to suggest improvements.

## 3. Retrieval Augmented Generation (RAG)

**Source:** `claude-resources/claude-cookbooks/capabilities/retrieval_augmented_generation/`

### RAG Architecture
*   **Chunking:** Split documents by logical headings/subheadings rather than arbitrary token counts.
*   **Embeddings:** Use high-quality models (Voyage AI `voyage-2` or similar).
*   **Retrieval:** Cosine similarity.

### Evaluation Strategy (Critical)
The cookbook emphasizes separating **Retrieval Metrics** from **End-to-End Metrics**.

**Retrieval Metrics:**
*   **Precision:** % of retrieved chunks that are relevant.
*   **Recall:** % of all relevant chunks that were retrieved.
*   **MRR (Mean Reciprocal Rank):** How high up the first relevant chunk appears.

**End-to-End Metrics (LLM-as-Judge):**
*   **Accuracy:** Use a strong model (Opus/Sonnet) to judge if the generated answer matches a "Gold Standard" answer.
*   **Rubric:**
    1.  Substance matches?
    2.  No critical info missing?
    3.  No contradictions?

### Integration: `knowledge-synthesizer`
The `knowledge-synthesizer` agent should be updated to:
1.  Use **LLM-as-a-judge** patterns for validating its own summaries.
2.  Implement a specific "Evaluation Mode" where it generates synthetic QA pairs (using the `prompt-engineer`'s synthetic data capability) to test its retrieval quality.

## 4. Advanced RAG: Contextual Embeddings & Hybrid Search

**Source:** `claude-resources/claude-cookbooks/capabilities/contextual-embeddings/guide.ipynb`

### The Problem
Traditional chunking loses context. A chunk saying "The limit is 500" is useless if you don't know *what* limit it refers to because the header was in a previous chunk.

### The Solution: Contextual Embeddings
**Technique:** Before embedding a chunk, use a cheap model (Haiku) to generate a "situating context" and prepend it to the chunk.

**Prompt Pattern:**
```markdown
<document>{full_doc}</document>
Here is the chunk we want to situate:
<chunk>{chunk_content}</chunk>
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval.
```

**Implementation Details:**
*   **Prompt Caching:** Essential for cost efficiency. Cache the `{full_doc}` prefix so you only pay for it once per document, not per chunk.
*   **Performance:** Improved Pass@10 from 87% to 92% in benchmarks.

### Hybrid Search & Reranking
*   **Hybrid:** Combine Vector Search (Semantic) + BM25 (Keyword/Exact Match). Use Reciprocal Rank Fusion (RRF) to combine scores.
*   **Reranking:** Retrieve top 100 chunks, then use a reranker (e.g., Cohere) to sort them. This pushed performance to ~97%.

## 5. Structured Data & Dynamic UI

**Source:** `claude-resources/claude-cookbooks/tool_use/extracting_structured_json.ipynb`

### The Pattern
To populate dynamic UIs reliably, **do not** ask for "JSON text". Instead, **force Tool Use**.

### Strategy
1.  Define a tool that represents your UI's schema.
    *   *Example:* `render_dashboard(stats: List[Stat], charts: List[Chart])`
2.  Force the model to use this tool (`tool_choice: {"type": "tool", "name": "render_dashboard"}`).
3.  The model's output will be strictly validated JSON matching your schema, which can be directly passed to frontend components.

### Handling Unknown Structure
If the schema is dynamic, use `additionalProperties: True` in the tool definition to allow open-ended JSON objects while still enforcing a tool-call structure.

## 6. Grounded Responses with Citations

**Source:** `claude-resources/claude-cookbooks/misc/using_citations.ipynb`

### Native Citations
Claude 3.5 Sonnet supports native citations to reduce hallucinations and provide user trust.

### Implementation
Pass documents with the `citations` enabled flag:
```json
{
  "role": "user",
  "content": [
    {
      "type": "document",
      "source": {"type": "text", "media_type": "text/plain", "data": "Full text content..."},
      "title": "Q3 Financial Report",
      "citations": {"enabled": true}
    }
  ]
}
```

### Output Handling
The response will contain a `citations` list. The UI should render these as interactive markers (e.g., `[1]`) that link to the source text.

## Actionable Next Steps
1.  **Create** `prompts/templates/frontend-aesthetics.md` with the extracted design rules.
2.  **Update** `agents/prompt-engineer.md` to reference the Metaprompt patterns (CoT, XML structure).
3.  **Implement** a `cortex rag ingest --contextual` command that uses the "Situate Context" prompt pattern.
4.  **Refine** `knowledge-synthesizer` to use Native Citations when answering from knowledge base documents.
