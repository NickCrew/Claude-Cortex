# Backlog.md CLI Command Reference

Complete reference for all `backlog` CLI commands and flags.

## Task Creation

| Action             | Command                                                                             |
|--------------------|-------------------------------------------------------------------------------------|
| Create task        | `backlog task create "Title"`                                                       |
| With description   | `backlog task create "Title" -d "Description"`                                      |
| With AC            | `backlog task create "Title" --ac "Criterion 1" --ac "Criterion 2"`                 |
| With final summary | `backlog task create "Title" --final-summary "PR-style summary"`                    |
| With references    | `backlog task create "Title" --ref src/api.ts --ref https://github.com/issue/123`   |
| With documentation | `backlog task create "Title" --doc https://design-docs.example.com`                 |
| With all options   | `backlog task create "Title" -d "Desc" -a @sara -s "To Do" -l auth --priority high --ref src/api.ts --doc docs/spec.md` |
| Create draft       | `backlog task create "Title" --draft`                                               |
| Create subtask     | `backlog task create "Title" -p 42`                                                 |
| Without DoD defaults | `backlog task create "Title" --no-dod-defaults`                                   |

## Task Modification

| Action           | Command                                     |
|------------------|---------------------------------------------|
| Edit title       | `backlog task edit 42 -t "New Title"`       |
| Edit description | `backlog task edit 42 -d "New description"` |
| Change status    | `backlog task edit 42 -s "In Progress"`     |
| Assign           | `backlog task edit 42 -a @sara`             |
| Add labels       | `backlog task edit 42 -l backend,api`       |
| Set priority     | `backlog task edit 42 --priority high`      |

## Acceptance Criteria Management

| Action              | Command                                                                      |
|---------------------|------------------------------------------------------------------------------|
| Add AC              | `backlog task edit 42 --ac "New criterion" --ac "Another"`                   |
| Remove AC #2        | `backlog task edit 42 --remove-ac 2`                                         |
| Remove multiple ACs | `backlog task edit 42 --remove-ac 2 --remove-ac 4`                           |
| Check AC #1         | `backlog task edit 42 --check-ac 1`                                          |
| Check multiple ACs  | `backlog task edit 42 --check-ac 1 --check-ac 3`                             |
| Uncheck AC #3       | `backlog task edit 42 --uncheck-ac 3`                                        |
| Mixed operations    | `backlog task edit 42 --check-ac 1 --uncheck-ac 2 --remove-ac 3 --ac "New"` |

**Important AC flag rules:**
- Adding: `--ac "First" --ac "Second"` (multiple flags allowed)
- Checking/unchecking/removing: `--check-ac 1 --check-ac 2` (multiple flags allowed)
- Mixed operations work in a single command
- **Invalid formats**: `--check-ac 1,2,3` (no commas), `--check-ac 1-3` (no ranges), `--check 1` (wrong flag name)

## Definition of Done Management

| Action            | Command                                                      |
|-------------------|--------------------------------------------------------------|
| Add DoD items     | `backlog task edit 42 --dod "Run tests" --dod "Update docs"` |
| Check DoD         | `backlog task edit 42 --check-dod 1 --check-dod 2`          |
| Uncheck DoD       | `backlog task edit 42 --uncheck-dod 1`                       |
| Remove DoD        | `backlog task edit 42 --remove-dod 2`                        |

DoD defaults come from `definition_of_done` in `backlog/config.yml`. Disable per-task with `--no-dod-defaults`.

## Task Content

| Action               | Command                                                          |
|----------------------|------------------------------------------------------------------|
| Add plan             | `backlog task edit 42 --plan "1. Step one\n2. Step two"`         |
| Add notes (replace)  | `backlog task edit 42 --notes "Implementation details"`          |
| Append notes         | `backlog task edit 42 --append-notes "Another note"`             |
| Add final summary    | `backlog task edit 42 --final-summary "PR-style summary"`        |
| Append final summary | `backlog task edit 42 --append-final-summary "More details"`     |
| Clear final summary  | `backlog task edit 42 --clear-final-summary`                     |
| Add dependencies     | `backlog task edit 42 --dep task-1 --dep task-2`                 |
| Add references       | `backlog task edit 42 --ref src/api.ts --ref https://github.com/issue/123` |
| Add documentation    | `backlog task edit 42 --doc https://design-docs.example.com --doc docs/spec.md` |

## Task Operations

| Action             | Command                                          |
|--------------------|--------------------------------------------------|
| View task          | `backlog task 42 --plain`                        |
| List tasks         | `backlog task list --plain`                      |
| Search tasks       | `backlog search "topic" --plain`                 |
| Search with filter | `backlog search "api" --status "To Do" --plain`  |
| Search by type     | `backlog search "login" --type task --plain`     |
| Search by priority | `backlog search "bug" --priority high --plain`   |
| Filter by status   | `backlog task list -s "In Progress" --plain`     |
| Filter by assignee | `backlog task list -a @sara --plain`             |
| Archive task       | `backlog task archive 42`                        |
| Demote to draft    | `backlog task demote 42`                         |
| View board         | `backlog board`                                  |
| Web UI             | `backlog browser`                                |

## Multi-line Input

The CLI preserves input literally. Shells do not convert `\n` inside normal quotes. To insert real newlines:

### Bash/Zsh (ANSI-C quoting)

```bash
backlog task edit 42 --desc $'Line1\nLine2\n\nFinal'
backlog task edit 42 --plan $'1. A\n2. B'
backlog task edit 42 --notes $'Done A\nDoing B'
backlog task edit 42 --append-notes $'Progress update line 1\nLine 2'
backlog task edit 42 --final-summary $'Shipped A\nAdded B'
backlog task edit 42 --append-final-summary $'Added X\nAdded Y'
```

### POSIX portable (printf)

```bash
backlog task edit 42 --notes "$(printf 'Line1\nLine2')"
```

### PowerShell (backtick n)

```powershell
backlog task edit 42 --notes "Line1`nLine2"
```

**Note**: `"...\n..."` with regular double quotes passes the literal backslash + n — it does not create a newline.

## Implementation Notes Formatting

- Keep notes concise and time-ordered: progress, decisions, blockers
- Use short paragraphs or bullet lists
- Use Markdown bullets (`-` unordered, `1.` ordered)
- Include explicit newlines in `--append-notes`:

```bash
backlog task edit 42 --append-notes $'- Added new API endpoint\n- Updated tests\n- TODO: monitor staging deploy'
```

## Final Summary Formatting

Treat the Final Summary as a PR description. Cover:
- **What changed** and **why**
- **User impact**
- **Tests run**
- **Risks/follow-ups** when relevant

Example:

```
Added Final Summary support across CLI/MCP/Web/TUI to separate PR summaries from progress notes.

Changes:
- Added `finalSummary` to task types and markdown section parsing/serialization.
- CLI/MCP/Web/TUI now render and edit Final Summary; plain output includes it.

Tests:
- bun test src/test/final-summary.test.ts
- bun test src/test/cli-final-summary.test.ts
```

Avoid single-line summaries unless the change is truly tiny.
