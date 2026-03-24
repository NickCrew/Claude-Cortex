# AI Intelligence Documentation

This section used to center on experimental LLM-assisted recommendation flows.
The current Cortex recommendation stack is better understood through these
canonical pages:

- [AI Intelligence Features](../../AI_INTELLIGENCE.md)
  - current user-facing guide for **agent** recommendations
- [Skill Recommendation Engine](../../architecture/skill-recommendation-engine.md)
  - current architecture guide for **skill** recommendations
- [AI Intelligence System: Technical Architecture](../development/AI_INTELLIGENCE_ARCHITECTURE.md)
  - developer-focused agent intelligence internals
- [Skill Recommendation & Review Learning](../development/skill-recommendation-system.md)
  - developer-focused skill learning and review ingestion

## Current State

Today, the supported recommendation experience is built around:

- rule-based and history-based **agent recommendations** via `cortex ai ...`
- prompt-hook, watch-mode, and CLI **skill recommendations**
- optional semantic matching when the embedding dependency is installed

## About The Older LLM Notes In This Folder

The remaining files in this directory are not the canonical source for the
current recommendation workflow:

- `LLM_INTELLIGENCE_GUIDE.md`
  - historical deep-dive and design-note material around optional LLM-assisted
    recommendation ideas
- `LLM_QUICK_REFERENCE.md`
  - historical quick-reference material for the same exploratory path

Treat those files as design notes unless they are re-verified against the
current CLI and code paths.

If you update the recommendation system, update the canonical pages above first.
