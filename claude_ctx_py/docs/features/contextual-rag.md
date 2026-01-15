---
layout: default
title: Contextual RAG
nav_order: 10
---

# Contextual Retrieval Augmented Generation (RAG)

**New in January 2026** – Enhance retrieval accuracy with "Contextual Embeddings".

Traditional RAG often fails when individual chunks lack sufficient context. For example, a chunk saying "The limit is 500" is useless if you don't know *what* limit it refers to because the header was in a previous chunk.

Cortex solves this with **Contextual Ingestion**: before embedding a chunk, it uses a fast, cost-effective model (Haiku) to generate a "situating context" and prepends it to the chunk.

## Key Benefits

*   **Improved Retrieval**: Chunks carry their own context, boosting retrieval accuracy by ~5-10% (Pass@10).
*   **Cost Efficiency**: Uses Prompt Caching to process documents cheaply.
*   **Automated**: No manual context writing required.

## Usage

### Ingesting Documents

Use the `cortex rag ingest` command to process files or directories:

```bash
# Ingest a single file
cortex rag ingest docs/architecture.md --contextual

# Ingest a directory of code
cortex rag ingest src/ --contextual
```

**Requirements:**
*   `ANTHROPIC_API_KEY` environment variable must be set.
*   The `--contextual` flag is currently required.

### How it Works

1.  **Chunking**: The document is split by headers (Markdown) or logical blocks.
2.  **Situation**: For each chunk, Claude (Haiku) is prompted with the *full document* and asked to explain the chunk's context.
3.  **Optimization**: The full document is cached (Prompt Caching), so you pay for the document tokens only once, not per chunk.
4.  **Storage**: The chunk + context is stored for your RAG system (Vector DB implementation dependent on your setup).

## Integration with Agents

The **Knowledge Synthesizer** agent is optimized to use this data. When answering questions, it will:
1.  Retrieve these contextualized chunks.
2.  Provide **Grounded Responses** with native citations (e.g., `[1]`).

## Configuration

The ingestion process is configured to use `claude-3-haiku` for speed and cost. You can override the API key via CLI if needed, but environment variables are recommended.
