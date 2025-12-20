# Migration & Upgrade Flags

Flags for safe migrations, dependency upgrades, and feature flag management.

**Estimated tokens: ~170**

---

**--migrate / --safe-migration**
- Trigger: Database migrations, API version upgrades, data model changes
- Behavior: Generate safe, reversible migration strategies with zero-downtime focus
- Ensures: Zero-downtime deployments, rollback plans, data integrity preservation
- Validates: Migration scripts idempotency, backward compatibility, data preservation
- Patterns: Blue-green deployment, rolling updates, expand-contract migrations
- Generates: Migration scripts (up/down), rollback procedures, verification queries
- Checks: Foreign key constraints, index creation (online), data type changes (safe)

**--upgrade-deps**
- Trigger: Dependency updates, security patches, major version bumps
- Behavior: Intelligent dependency upgrade with compatibility analysis and testing
- Analyzes: Breaking changes, deprecations, security advisories, transitive dependencies
- Suggests: Incremental upgrade path (avoid jumping versions), code changes needed
- Strategy: Security patches → minor updates → major updates (staged approach)
- Validates: Test suite passes, no breaking API changes, deprecation warnings addressed
- Reports: Upgrade complexity, risk assessment, estimated effort, rollback difficulty
- Tools: npm-check-updates, pip-review, Dependabot, Renovate

**--feature-flag / --gradual-rollout**
- Trigger: Gradual rollouts, A/B testing, canary deployments, kill switches
- Behavior: Implement feature flagging patterns for safe, controlled deployments
- Supports: Boolean toggles, percentage rollouts, user/group targeting, environment flags
- Ensures: Flag cleanup (no permanent flags), monitoring, fallback behavior
- Patterns: Release toggles (temporary), ops toggles (circuit breakers), experiment toggles (A/B)
- Integrates: LaunchDarkly, Unleash, Split.io, custom flag systems
- Best practices: Flag naming, flag lifecycle, flag retirement, feature flag debt tracking

**--backward-compatible**
- Trigger: API changes, library updates, breaking change prevention
- Behavior: Ensure changes maintain backward compatibility
- Validates: Old clients work with new API, deprecation warnings before removal
- Patterns: API versioning, deprecation notices, graceful degradation
- Timeline: Deprecate → Warn → Remove (with sufficient notice period)
- Checks: No breaking changes in minor versions (semantic versioning)
- Generates: Migration guides, deprecation timeline, upgrade documentation

**--database-migration-safe**
- Trigger: Schema changes in production, live database modifications
- Behavior: Ensure database migrations are safe for production deployment
- Validates: No table locks during migrations, online index creation, additive changes
- Patterns: Expand-contract (add column, migrate data, remove old column in stages)
- Checks: Migration duration estimates, rollback procedures, data validation
- Ensures: No downtime, no data loss, reversible changes
- Strategies: Ghost (GitHub), pt-online-schema-change (Percona), online DDL (PostgreSQL)

**--breaking-change-protocol**
- Trigger: API redesign, major refactoring, incompatible updates
- Behavior: Structured approach to introducing breaking changes safely
- Requires: Major version bump, migration guide, deprecation period
- Checklist: Document breaking changes, provide codemods/migration scripts, announce early
- Communicates: Changelog entry, migration guide, announcement to users
- Ensures: Sufficient transition time, clear upgrade path, support for migration
- Examples: Remove deprecated API, change data format, rename configuration keys
