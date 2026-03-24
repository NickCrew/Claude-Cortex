# Cortex Documentation

This `docs/` tree is the currently published documentation source for GitHub
Pages in this repository.

## Recommendation System Entry Points

If you are looking for the recommendation stack specifically, start here:

- [AI Intelligence Features](AI_INTELLIGENCE.md)
  - user-facing overview of the **agent** recommendation system
  - covers `cortex ai recommend`, watch mode, TUI integration, and session learning
- [Skill Recommendation Engine](architecture/skill-recommendation-engine.md)
  - architecture overview of the **skill** recommendation pipeline
  - explains the prompt hook, `SkillRecommender`, rule files, and storage
- [Skill Recommendation & Review Learning](guides/development/skill-recommendation-system.md)
  - developer guide for skill-learning internals and review ingestion
- [AI Intelligence System: Technical Architecture](guides/development/AI_INTELLIGENCE_ARCHITECTURE.md)
  - developer guide for agent-learning internals and workflow prediction
- [Skills Guide](guides/skills.md)
  - user-facing skill usage, recommendation, and rating commands
- [AI Watch Mode Tutorial](tutorials/ai-watch-mode.md)
  - live walkthrough for watch mode and the AI Assistant
- [Documentation Navigator](NAVIGATOR.md)
  - broader map by audience and topic

## Broader Documentation Map

### Architecture

- [Architecture Overview](architecture/README.md)
- [Master Architecture](architecture/MASTER_ARCHITECTURE.md)
- [Quick Reference](architecture/quick-reference.md)

### User Guides

- [Getting Started](guides/getting-started.md)
- [Skills Guide](guides/skills.md)
- [Hooks Guide](guides/hooks.md)
- [TUI Guide](guides/tui.md)
- [Skill Authoring Cookbook](tutorials/skill-authoring-cookbook.md)

### Development Guides

- [Architecture](guides/development/architecture.md)
- [Skill Recommendation & Review Learning](guides/development/skill-recommendation-system.md)
- [AI Intelligence System: Technical Architecture](guides/development/AI_INTELLIGENCE_ARCHITECTURE.md)

## Notes

- The recommendation system has two distinct halves: **agent intelligence** and
  **skill recommendations**. Avoid using those terms interchangeably in docs.
- When the command surface changes, update both the user-facing pages and the
  developer-facing architecture pages in the same slice to avoid drift.
- Contributor-oriented skill onboarding lives in the Skills Guide and the Skill
  Authoring Cookbook; use those instead of reconstructing the workflow from
  historical architecture notes.
