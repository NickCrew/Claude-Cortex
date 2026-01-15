# Documentation Viewer Guide

The **Documentation Viewer** allows you to browse, search, and read the comprehensive Cortex documentation directly from your terminal. It is available as both a CLI command and an interactive TUI screen.

## CLI Usage

Use the `cortex docs` command to list or view documentation.

### List Documentation
Run `cortex docs` without arguments to see a tree of all available documentation pages.

```bash
cortex docs
```

### View a Specific Page
Provide the name or path of a documentation page to render it as formatted Markdown in your terminal.

```bash
# View by exact path
cortex docs architecture/MASTER_ARCHITECTURE

# View by filename (recursive search)
cortex docs MASTER_ARCHITECTURE

# View top-level files
cortex docs README
```

## TUI Usage

The Documentation Viewer is integrated into the Cortex TUI for a seamless browsing experience.

### Opening the Viewer
1. Launch the TUI: `cortex tui`
2. Press **`d`** from any view (where not bound to another action) or use the **Command Palette** (**`Ctrl+P`**) and search for "Docs".

### Navigation
- **Left Pane (Tree):** Use arrow keys or `j`/`k` to navigate the documentation hierarchy. Press **Enter** to expand/collapse directories or select a file.
- **Right Pane (Content):** Use arrow keys, `PageUp`/`PageDown`, or `j`/`k` to scroll through the rendered Markdown.
- **Search:** Use the TUI's global search or the Command Palette to find specific documentation topics.
- **Back:** Press **`Esc`** or **`q`** to close the documentation viewer and return to your previous view.

## Features

- **Bundled Documentation:** The viewer serves documentation that is bundled directly with the Python package, ensuring you always have access to the correct version of the docs for your installed CLI.
- **Rich Rendering:** Markdown is rendered with syntax highlighting, tables, and formatted lists using the `rich` library (CLI) and `textual` (TUI).
- **Recursive Search:** The CLI command can find files deep in the directory structure even if you only provide the filename.
- **Context-Aware:** In specific TUI views, pressing `d` may open documentation relevant to that context (e.g., MCP server documentation when in the MCP view). If no specific docs are linked, it falls back to the general documentation viewer.

## Troubleshooting

If you see a "Documentation not found" message:
1. Ensure you are running the latest version of the `claude-cortex` package.
2. If you are developing locally, ensure the `claude_ctx_py/docs` directory has been populated (run `just docs-sync` or similar).
