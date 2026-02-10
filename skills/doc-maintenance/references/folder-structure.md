# Documentation Folder Structure Specification

This reference defines the canonical folder structure for project documentation.
All documentation maintenance operations must conform to this layout.

## Two-Root Model

Documentation lives in two root directories:

| Root | Audience | Location |
|------|----------|----------|
| `docs/` | Developers, contributors, internal teams | Project root |
| `manual/` | End users, operators, external consumers | Project root |

These two roots must never be mixed. Developer docs belong in `docs/`, user-facing
docs belong in `manual/`.

---

## `docs/` — Developer & Internal Documentation

### `docs/architecture/`

System design and architectural decision records.

**Contains:**
- Architecture Decision Records (ADRs) — `adr-NNN-title.md`
- System diagrams and component overviews
- Data flow documentation
- Integration architecture

**Naming:** ADRs use `adr-NNN-title.md` format. Other files use kebab-case.

### `docs/development/`

Developer guides for contributing to and working with the project.

**Contains:**
- Style guides (code style, commit conventions, PR process)
- Local development setup instructions
- Issue tracking and workflow documentation
- Environment configuration guides
- Tooling guides (linters, formatters, CI)

**Naming:** kebab-case, descriptive filenames (e.g., `local-setup.md`, `style-guide.md`).

### `docs/plans/`

Proposals, RFCs, and roadmap documents.

**Contains:**
- Feature proposals and RFCs
- Release plans and roadmaps
- Migration plans
- Deprecation plans

**Naming:** `YYYY-MM-title.md` for dated proposals, kebab-case for evergreen plans.

### `docs/reviews/`

Code review records and audit reports.

**Contains:**
- Review summaries and decisions
- Audit findings and remediation tracking
- Post-mortem documents

**Naming:** `YYYY-MM-DD-title.md` for dated reviews.

### `docs/testing/`

Test strategy and coverage documentation.

**Contains:**
- Test strategy and philosophy
- Coverage reports and goals
- Test plan documents
- Testing infrastructure guides

**Naming:** kebab-case.

### `docs/reports/`

Generated reports, metrics, and analysis.

**Contains:**
- Performance benchmarks
- Dependency audit reports
- Documentation audit results
- Metrics dashboards and summaries

**Naming:** `YYYY-MM-DD-title.md` for dated reports, kebab-case for templates.

### `docs/security/`

Security policies, threat models, and audit findings.

**Contains:**
- Security policies and guidelines
- Threat models (STRIDE, attack trees)
- Vulnerability disclosures and remediation
- Compliance documentation

**Naming:** kebab-case. Sensitive findings may use restricted-access patterns.

### `docs/api/`

Internal API documentation.

**Contains:**
- OpenAPI / Swagger specs
- gRPC protobuf documentation
- Internal service API references
- Webhook schemas

**Naming:** Match the API/service name (e.g., `auth-service.md`, `openapi.yaml`).

### `docs/reference/`

CLI reference, configuration reference, and manpages.

**Contains:**
- CLI command reference (manpage sources)
- Configuration file reference
- Environment variable reference
- Glossary and terminology

**Naming:** Match the tool or config name (e.g., `cortex.1`, `config-reference.md`).

### `docs/ideas/`

Exploratory notes, spikes, and brainstorms.

**Contains:**
- Spike results and exploratory research
- Brainstorm notes
- Rough ideas not yet promoted to plans
- Technology evaluations

**Naming:** kebab-case, informal. These may be promoted to `docs/plans/` when mature.

### `docs/archive/`

Deprecated documentation preserved for historical reference.

**Contains:**
- Docs for removed features
- Superseded architecture docs
- Old plans that were completed or abandoned

**Naming:** Preserve original filename. Optionally prefix with `ARCHIVED-`.

**Rule:** Moving a doc to archive requires removing all inbound links to it or replacing
them with a note that the doc is archived.

---

## `manual/` — User-Facing Documentation

### `manual/getting-started/`

First-contact documentation for new users.

**Contains:**
- Installation instructions
- Quickstart guide
- Prerequisites and system requirements
- First-run walkthrough

**Naming:** kebab-case. Keep filenames intuitive for users (e.g., `install.md`, `quickstart.md`).

### `manual/guides/`

Task-oriented how-to guides.

**Contains:**
- How to accomplish specific tasks
- Configuration guides for common scenarios
- Integration guides with external tools
- Workflow guides

**Naming:** `how-to-VERB-NOUN.md` pattern preferred (e.g., `how-to-configure-auth.md`).

### `manual/tutorials/`

Step-by-step learning paths with progressive complexity.

**Contains:**
- Guided tutorials that build understanding
- Example-driven learning sequences
- Hands-on exercises

**Naming:** Number-prefixed for ordering (e.g., `01-basics.md`, `02-advanced-config.md`).

### `manual/reference/`

User-facing command and configuration reference.

**Contains:**
- Command reference (user-oriented, not developer-oriented)
- Configuration option reference
- Supported formats, protocols, and integrations

**Naming:** Match the feature or command name.

### `manual/troubleshooting/`

Problem-solving documentation.

**Contains:**
- FAQ
- Common errors and solutions
- Known issues and workarounds
- Diagnostic procedures

**Naming:** kebab-case (e.g., `common-errors.md`, `faq.md`).

---

## Cross-Cutting Rules

1. **Index files:** Each subfolder should contain an `index.md` or `README.md` that lists
   and briefly describes its contents.
2. **Internal links:** Always use relative paths for cross-references within the same root.
   Use `../../manual/` or `../../docs/` for cross-root references.
3. **No loose files:** Every markdown file must live in the appropriate subfolder, not
   directly in `docs/` or `manual/` (except `docs/README.md` or `manual/README.md`).
4. **Diagrams:** Store diagrams next to the doc that references them in a `diagrams/`
   subfolder, or use inline Mermaid blocks.
5. **Naming conventions:** All filenames use kebab-case. No spaces, no camelCase.
