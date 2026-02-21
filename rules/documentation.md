# Documentation Rules

- Always use kebab-case filenames for files in `**docs/*`
- Do not create documentation files in the project root without asking the user. Exceptions: `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` 
- Maintain a documentation navigator at `docs/NAVIGATOR.md`
- Maintain a clean logical separation between user-facing documentation and development (project) documentation. 

## Docs Folder Structure

Organize documentation neatly using sub-directories under `docs/`:

- `docs/archive` - Deprecated documentation, completed plans, old reports.
- `docs/development` - Instructions for setting up the local environment, managing local processes, dependencies, task runners, any reports or analysis that are only relevant to developers.
- `docs/development/testing` - Test methodology of the project and how to execute tests
- `docs/development/plans` - Future plans
- `docs/development/reports` - Reports, summaries, implementation details
- `docs/architecture` - Architecture, designs, diagrams
- `docs/reference` - References for APIs, CLI, etc. Feature inventories.
- `docs/user-guides` - User-facing content (tutorials, walk-throughs, guides, etc)
