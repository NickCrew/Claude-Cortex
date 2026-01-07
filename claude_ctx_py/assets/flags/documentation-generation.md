# Documentation Generation Flags

Flags for generating and maintaining comprehensive documentation.

**Estimated tokens: ~170**

---

**--doc / --document-as-you-go**
- Trigger: Public APIs, complex logic, team handoff, open source projects
- Behavior: Generate documentation alongside code development
- Auto-creates: API docs, code comments, architectural decision records (ADRs)
- Formats: Markdown, JSDoc/TSDoc, Sphinx/docstrings, OpenAPI specs, Swagger
- Maintains: Documentation freshness, examples accuracy, changelog updates
- Validates: Doc/code consistency, example executability, broken link detection
- Standards: Documentation best practices, consistent structure, searchable content

**--explain-code**
- Trigger: Complex algorithms, legacy code, onboarding, knowledge transfer
- Behavior: Add explanatory comments for non-obvious code and design decisions
- Focuses: Why (not what), trade-offs, assumptions, edge cases, gotchas
- Avoids: Obvious comments, redundant documentation, stale comments
- Guidelines: Comment intent, explain non-obvious, document assumptions
- Examples: "Why this algorithm", "Trade-off: speed vs memory", "Assumes X condition"
- Related: Self-documenting code preferred, comments as last resort

**--api-spec**
- Trigger: REST/GraphQL API development, client generation, API versioning
- Behavior: Maintain API specifications (OpenAPI/Swagger, GraphQL schema) alongside implementation
- Auto-updates: API specifications when endpoints change, version bumps for breaking changes
- Validates: Request/response schemas, error codes, authentication methods, rate limits
- Generates: API reference docs, interactive API explorer, client SDKs
- Ensures: API contract compliance, backward compatibility checks, changelog generation
- Tools: Swagger/OpenAPI, GraphQL schema, API Blueprint, Postman collections

**--adr / --architecture-decisions**
- Trigger: Architectural decisions, technology choices, significant refactorings
- Behavior: Document architectural decisions with context and rationale
- Format: ADR template (Title, Status, Context, Decision, Consequences)
- Captures: Problem statement, considered alternatives, trade-offs, final decision
- Maintains: Decision history, evolution of architecture, lessons learned
- Links: Related ADRs, implementation PRs, discussion threads
- Status: Proposed, Accepted, Deprecated, Superseded

**--readme-driven**
- Trigger: New projects, feature development, library creation
- Behavior: Write README/docs before implementation (documentation-driven development)
- Ensures: Clear requirements, usage examples, API design validation
- Sections: Installation, quick start, API reference, examples, contributing
- Benefits: Design validation, user perspective, clear success criteria
- Related: Test-driven development but for documentation

**--changelog-auto**
- Trigger: Release preparation, semantic versioning, user-facing changes
- Behavior: Auto-generate changelog from commits and PRs
- Format: Keep a Changelog (Added, Changed, Deprecated, Removed, Fixed, Security)
- Sources: Conventional commits, PR labels, commit messages, release notes
- Groups: By category and version, breaking changes highlighted
- Validates: Semantic version bumps match change types
- Tools: standard-version, semantic-release, conventional-changelog
