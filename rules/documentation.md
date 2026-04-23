# Documentation Rules

- Always use kebab-case filenames for files in `**docs/*`
- Do not create documentation files in the project root without asking the user. Exceptions: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- Maintain a documentation navigator at `docs/NAVIGATOR.md`
- `site/` is the preferred location for statically generated doc sites like Github pages
- Maintain a clean logical separation between user-facing documentation and development (project) documentation.
- For plans or any documentation related to Backlog tasks, make sure the doc is stored in backlog using the MCP tool (preferred) or CLI `backlog docs` so the implementing agent can locate them easily.

## Docs Folder Structure

Organize documentation for neatly using sub-directories under `docs/`.

- `docs/asssets` - Images, JS, CSS
- `docs/NAVIGATOR.md` - File index, role-based discovery
- `docs/devel` - Development docs: instructions for setting up the local environment, managing local processes, dependencies, task runners, any reports or analysis that are only relevant to developers.
  - `docs/devel/testing` - Test methodology of the project and how to execute tests
  - `docs/devel/plans` - Future plans
  - `docs/devel/reports` - Reports, summaries, implementation details
- `docs/architecture` - Architecture, designs, diagrams
- `docs/reference` - References for APIs, CLI, etc. Feature inventories.
  - `docs/reference/api` - API Documentation
  - `docs/reference/features` - Product features
  - `docs/reference/cli`
    - `docs/reference/cli/man` - Manpages if they exist
 `docs/tutorials` - How-to
- `docs/presentations` - Slideshows, reveal.js presentations, etc
- `docs/guides` - Explanations
- `docs/archive` - Deprecated documentation, completed plans, old reports.
- `docs/site/` - Alternative location for static site content
