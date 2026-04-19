---
name: model-comparator
description: Use this skill when comparing AI or LLM models on benchmarks, capability, cost, latency, context window, or task-specific fit to help teams select the right model for their use case and budget. Not for training or fine-tuning models. Not for building eval frameworks from scratch.
version: 1.0.0
author: community
tags:
  - ai
  - model-comparison
  - llm
  - benchmarking
  - cost-analysis
license: MIT
keywords:
  - compare models
  - LLM evaluation
  - cost analysis
  - model
  - comparator
  - model comparator
---

# Model Comparator

## Overview
This skill helps engineering and product teams make informed, structured decisions about which AI or LLM model to use for a given task. It covers comparison across multiple dimensions: benchmark performance, real-world task capability, inference cost per token, latency (time-to-first-token and throughput), context window size, multimodal capabilities, fine-tuning availability, licensing, and data privacy. It provides frameworks for structured comparison, cost modeling at scale, and task-specific head-to-head evaluation to move beyond marketing benchmarks to production-relevant decisions.

## When to Use
- Choosing between frontier models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, etc.) for a new product feature
- Deciding whether to use a proprietary API or a self-hosted open-source model
- Selecting an embedding model for a RAG (retrieval-augmented generation) pipeline
- Evaluating cost-quality tradeoffs for a high-volume production use case
- Justifying a model switch to stakeholders with data
- Comparing models for latency-sensitive applications (real-time chat, autocomplete)
- Assessing model capabilities for a specialized domain (medical, legal, code, multilingual)

## When NOT to Use
- Building evaluation infrastructure from scratch (use eval-designer skill)
- Fine-tuning or training a model on custom data (use model training skills)
- Comparing internal model versions (use eval-designer skill with your specific metrics)
- Choosing between ML frameworks (TensorFlow vs PyTorch) — that is an infrastructure decision

## Quick Reference
| Task | Approach |
|------|----------|
| Compare on cost | Calculate input + output token cost per 1M tokens; model at expected monthly volume |
| Compare on latency | Measure TTFT and tokens/sec under expected concurrency; not just vendor specs |
| Compare on task quality | Run task-specific evals on 50–200 representative examples; don't rely on public benchmarks alone |
| Compare on context window | Check both advertised window AND effective window (quality degrades in the middle for long contexts) |
| Compare open vs proprietary | Factor in: API cost vs GPU cost, data privacy, fine-tuning, operational complexity |
| Select embedding model | Compare on retrieval recall (MTEB benchmark) and dimensions vs cost tradeoff |
| Compare multimodal models | Test on your actual image/document types — capability varies significantly by domain |

## Instructions

1. **Define the comparison criteria** — List the dimensions that matter for your use case. Typical dimensions: task accuracy, cost per 1,000 API calls at production volume, p50/p95 latency, context window needed, rate limits, data privacy requirements, fine-tuning availability, and supported modalities. Weight each dimension by importance for your use case before running any tests.

2. **Establish a candidate list** — Select 2–5 models to compare. Include: the current model (if upgrading), the most cost-effective option, and the highest-quality option. Don't compare more than 5 — the evaluation overhead scales poorly. For general-purpose tasks, typical candidates: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3 (self-hosted), Mistral Large.

3. **Build a task-specific eval set** — Pull 50–200 real examples from your production data (or realistic proxies). Public benchmarks (MMLU, HumanEval, GPQA) measure general capability but rarely predict performance on your specific task. Evaluate on your actual input distribution.

4. **Run standardized capability tests** — Use the same prompt (no model-specific optimization) across all models first to get a fair baseline. Then optionally re-run with model-specific prompting to see ceiling performance. Record both scores — the gap between them shows how prompt-sensitive each model is.

5. **Measure cost at scale** — Calculate cost per API call: (avg_input_tokens × input_price + avg_output_tokens × output_price) / 1,000,000. Then model monthly cost at your expected call volume. Include: context window overhead (system prompts, few-shot examples), output verbosity differences between models, and caching potential for repeated prompts.

6. **Benchmark latency under realistic conditions** — Don't use idle latency — test under your expected concurrent request load. Measure: Time to First Token (TTFT) for streaming UX, total latency for batch tasks, and throughput (tokens/second). Some models have fast TTFT but slow generation; others are the reverse.

7. **Assess context window quality** — Advertised context windows can be misleading. Test with the "needle in a haystack" approach: insert a key fact deep in a long document and ask the model to retrieve it. Many models degrade in the middle of their context window. For RAG, the effective useful context is often 30–50% of the advertised limit.

8. **Score against your weighted criteria** — Create a comparison matrix. For each dimension, normalize scores to 0–10 and apply your weights. The weighted total gives a framework for the decision, but don't blindly follow it — qualitative factors (vendor reliability, ecosystem support, compliance) matter too.

9. **Run a limited production pilot** — Before committing, run the top 2 candidates in production on a small traffic slice (1–5%). Measure real user outcomes (task completion, escalation rate, satisfaction) not just automated eval scores. Real users find failure modes that evals miss.

10. **Document the decision** — Write a model selection document with: candidates evaluated, criteria and weights, eval results, cost projections, the chosen model, and the criteria for when to revisit the decision (e.g., "re-evaluate if monthly cost exceeds $X or if quality benchmark drops below Y").

## Examples

### Example 1: Comparing GPT-4o vs Claude 3.5 Sonnet for a Code Review Assistant
**Input:** A developer tools company wants to choose a model for an automated code review feature. Requirements: high code quality, under $0.05/review, and < 3 second p95 latency.

**Output:**

**Comparison matrix:**
```
Dimension          | Weight | GPT-4o | Claude 3.5 Sonnet | Notes
-------------------|--------|--------|-------------------|-------
Code review quality|  35%   |  8.5   |       9.0         | Claude scores higher on nuanced feedback and security detection
Cost per review    |  25%   |  7.0   |       8.0         | Claude input cheaper; GPT-4o output slightly cheaper; net ~15% cheaper for Claude
P95 latency        |  20%   |  8.0   |       7.5         | GPT-4o has faster TTFT; Claude slower start but similar total for 500-token outputs
Context window     |  10%   |  8.0   |       9.0         | Both support large contexts; Claude better at long-file analysis
API reliability    |  10%   |  9.0   |       8.5         | OpenAI has better SLA documentation at time of eval
-------------------|--------|--------|-------------------|-------
Weighted score     |        |  8.1   |       8.5         |
```

**Cost modeling at production volume (10,000 reviews/month):**
```
Assumptions:
  - Avg input: 2,000 tokens (code file + system prompt + few-shot)
  - Avg output: 500 tokens (review comments)
  - Volume: 10,000 reviews/month

GPT-4o pricing ($5/1M input, $15/1M output):
  Input cost:  10,000 × 2,000 / 1,000,000 × $5.00  = $100
  Output cost: 10,000 × 500  / 1,000,000 × $15.00  = $75
  Monthly total: $175 → $0.0175/review ✓ (under $0.05 budget)

Claude 3.5 Sonnet ($3/1M input, $15/1M output):
  Input cost:  10,000 × 2,000 / 1,000,000 × $3.00  = $60
  Output cost: 10,000 × 500  / 1,000,000 × $15.00  = $75
  Monthly total: $135 → $0.0135/review ✓ (23% cheaper than GPT-4o)
```

**Task-specific eval results (100 code review cases):**
```
Metric                    | GPT-4o | Claude 3.5 Sonnet
--------------------------|--------|-------------------
Security issue detection  |  72%   |  81%  ← significant gap
False positive rate       |  18%   |  12%  ← Claude more precise
Code style feedback score |  4.1/5 |  4.3/5
Actionable suggestions %  |  78%   |  84%
Explanation quality (1-5) |  4.0   |  4.4
```

**Recommendation:** Claude 3.5 Sonnet — superior code review quality, lower cost, meets latency requirements. Re-evaluate in 6 months or if pricing changes by > 20%.

### Example 2: Selecting an Embedding Model for a RAG Pipeline
**Input:** A legal tech company needs an embedding model for a RAG system over legal documents. Requirements: strong retrieval on long legal text, under $10/million tokens, and deployable on-premise for data privacy.

**Output:**

**Candidate models:**
```
1. text-embedding-3-large (OpenAI) — API only, 3072 dims, $0.13/1M tokens
2. text-embedding-3-small (OpenAI) — API only, 1536 dims, $0.02/1M tokens  
3. bge-large-en-v1.5 (BAAI) — open source, 1024 dims, self-hosted, free
4. e5-mistral-7b-instruct (Microsoft) — open source, 4096 dims, self-hosted, free
5. nomic-embed-text-v1.5 (Nomic) — open source, 768 dims, self-hosted, free
```

**MTEB benchmark scores (Legal domain):**
```
Model                    | Legal MTEB | General MTEB | Dims | Self-host? | Cost/1M tokens
-------------------------|------------|--------------|------|------------|---------------
text-embedding-3-large   |    68.2    |    64.6      | 3072 |    No      | $0.13
text-embedding-3-small   |    62.1    |    62.3      | 1536 |    No      | $0.02
bge-large-en-v1.5        |    64.8    |    63.5      | 1024 |   Yes      | ~$0.01*
e5-mistral-7b-instruct   |    71.3    |    66.9      | 4096 |   Yes      | ~$0.05*
nomic-embed-text-v1.5    |    60.4    |    61.9      |  768 |   Yes      | ~$0.008*
```
*Self-hosted cost = GPU compute; estimate for A100 at $3/hr, 1M tokens/hr throughput

**On-premise requirement analysis:**
```
API-based models (OpenAI): ELIMINATED — data privacy requirement
Remaining candidates: bge-large-en-v1.5, e5-mistral-7b-instruct, nomic-embed-text-v1.5

Task-specific recall test (50 legal document retrieval queries):
  bge-large-en-v1.5:       Recall@5 = 0.74, Recall@10 = 0.82
  e5-mistral-7b-instruct:  Recall@5 = 0.81, Recall@10 = 0.88  ← winner
  nomic-embed-text-v1.5:   Recall@5 = 0.69, Recall@10 = 0.78

Inference speed (A100 GPU, batch size 32):
  bge-large-en-v1.5:       ~4,200 tokens/sec  → fast for initial indexing
  e5-mistral-7b-instruct:  ~1,100 tokens/sec  → slower but acceptable
  nomic-embed-text-v1.5:   ~6,800 tokens/sec  → fastest
```

**Recommendation:** `e5-mistral-7b-instruct` — best retrieval quality on legal text (81% Recall@5), self-hosted for privacy compliance, reasonable compute cost. Deploy on 2× A100s for production throughput. Index the full document corpus in batches overnight to avoid latency impact.

## Best Practices
- Always evaluate on your own task data — public benchmarks rarely predict production performance
- Compute cost at 10× your expected production volume to model for growth
- Test latency under concurrency, not in isolation — vendor latency specs are single-request
- For safety-critical applications, weight refusal rate and hallucination rate heavily in your criteria
- Re-run comparisons every 6 months — model pricing and capabilities change rapidly
- Include open-source alternatives in every comparison — the cost difference can be 10–100×
- When models are close in quality, choose the cheaper one — quality differences < 5% rarely matter in production

## Common Mistakes
- Relying only on MMLU or HumanEval benchmarks — they measure academic capability, not product performance
- Not accounting for output verbosity — models that write longer outputs cost more and may be slower
- Ignoring rate limits — a cheaper model with lower rate limits may be more expensive at scale due to throttling
- Comparing models at different temperatures — always hold temperature constant across model comparisons
- Not testing the full prompt including system prompt in the cost calculation — system prompts are often 20–40% of token cost
- Choosing based on a single metric — weighted multi-criteria decisions are more robust
- Neglecting data privacy requirements until after selection — always check data processing agreements first

## Tips & Tricks
- Use `LiteLLM` to swap models with a single config change — makes A/B testing trivial
- Cache embeddings aggressively — most documents don't change; caching can cut embedding costs by 80%
- For latency-sensitive use cases, test streaming TTFT, not total latency — users perceive streaming as faster
- Check if a model supports prompt caching (Anthropic, OpenAI) — repeated system prompts can be cached at 90% discount
- Fine-tuning a smaller model can often match a larger model at 10% of the inference cost — worth evaluating
- Monitor model version changes — "GPT-4" today is not the same model as 6 months ago; pin versions in production

## Related Skills
- [prompt-engineer](../prompt-engineer/SKILL.md)
- [eval-designer](../eval-designer/SKILL.md)
