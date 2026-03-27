"""Documentation browser TUI for cortex."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Static,
)
from textual.widgets._directory_tree import DirEntry
from rich.markdown import Markdown as RichMarkdown
from rich.text import Text


class DocsTree(DirectoryTree):
    """Custom directory tree that only shows markdown files."""

    def filter_paths(self, paths: list[Path]) -> list[Path]:
        """Filter to only show directories and .md files, hiding hidden/private folders."""
        return [
            path
            for path in paths
            if (path.is_dir() or path.suffix == ".md")
            and not path.name.startswith(".")
            and not path.name.startswith("_")
        ]


class BookmarksList(Static):
    """Widget to display bookmarks."""

    def __init__(self, bookmarks_file: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bookmarks_file = bookmarks_file
        self.bookmarks: dict[str, str] = {}
        self.load_bookmarks()

    def load_bookmarks(self) -> None:
        """Load bookmarks from file."""
        if self.bookmarks_file.exists():
            try:
                self.bookmarks = json.loads(
                    self.bookmarks_file.read_text(encoding="utf-8")
                )
            except Exception:
                self.bookmarks = {}
        self.refresh_display()

    def save_bookmarks(self) -> None:
        """Save bookmarks to file."""
        self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)
        self.bookmarks_file.write_text(
            json.dumps(self.bookmarks, indent=2) + "\n",
            encoding="utf-8"
        )

    def add_bookmark(self, name: str, path: str) -> None:
        """Add a bookmark."""
        self.bookmarks[name] = path
        self.save_bookmarks()
        self.refresh_display()

    def remove_bookmark(self, name: str) -> None:
        """Remove a bookmark."""
        if name in self.bookmarks:
            del self.bookmarks[name]
            self.save_bookmarks()
            self.refresh_display()

    def refresh_display(self) -> None:
        """Refresh the bookmarks display."""
        if not self.bookmarks:
            self.update("[dim]No bookmarks saved[/dim]")
            return

        lines = ["[bold]Bookmarks:[/bold]", ""]
        for i, (name, path) in enumerate(sorted(self.bookmarks.items()), 1):
            lines.append(f"[cyan]{i}.[/cyan] [yellow]{name}[/yellow]")
            lines.append(f"   [dim]{path}[/dim]")

        self.update("\n".join(lines))


class SearchResults(Static):
    """Widget to display search results."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.results: list[dict] = []

    def update_results(self, results: list[dict]) -> None:
        """Update search results."""
        self.results = results
        if not results:
            self.update("[dim]No results found[/dim]")
            return

        lines = [f"[bold]Found {len(results)} matches:[/bold]", ""]
        for i, result in enumerate(results[:50], 1):
            lines.append(f"[cyan]{i}.[/cyan] [green]{result['file']}[/green]:[yellow]{result['line']}[/yellow]")
            lines.append(f"   {result['content'][:80]}")
            lines.append("")

        self.update("\n".join(lines))


class DocsBrowserApp(App[None]):
    """Documentation browser TUI application."""

    TITLE = "Cortex Documentation Browser"
    CSS = """
    Screen {
        layout: horizontal;
    }

    #sidebar {
        width: 30%;
        height: 100%;
        border-right: solid $accent;
    }

    #main {
        width: 70%;
        height: 100%;
    }

    #tree-container {
        height: 60%;
        border-bottom: solid $accent;
    }

    #bookmarks-container {
        height: 40%;
        padding: 1;
    }

    #viewer-container {
        height: 90%;
    }

    #search-container {
        height: 10%;
        padding: 1;
    }

    DocsTree {
        height: 100%;
        scrollbar-gutter: stable;
    }

    BookmarksList {
        height: 100%;
        scrollbar-gutter: stable;
    }

    RichLog {
        height: 1fr;
        scrollbar-gutter: stable;
    }

    SearchResults {
        height: auto;
    }

    Input {
        width: 100%;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("b", "toggle_bookmark", "Bookmark"),
        Binding("s", "focus_search", "Search"),
        Binding("v", "focus_viewer", "View"),
        Binding("t", "focus_tree", "Tree"),
        Binding("tab", "cycle_focus", "Next Pane", show=False),
        Binding("escape", "clear_search", "Clear Search"),
        Binding("r", "reload", "Reload"),
    ]

    def __init__(
        self,
        docs_dir: Path,
        bookmarks_file: Path,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.docs_dir = docs_dir
        self.bookmarks_file = bookmarks_file
        self.current_file: Optional[Path] = None
        self.viewer: Optional[RichLog] = None
        self.docs_tree: Optional[DocsTree] = None
        self.bookmarks: Optional[BookmarksList] = None
        self.search_input: Optional[Input] = None
        self.search_results: Optional[SearchResults] = None
        self.status_label: Optional[Label] = None

    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()

        with Horizontal():
            # Left sidebar
            with Vertical(id="sidebar"):
                with Container(id="tree-container"):
                    self.docs_tree = DocsTree(self.docs_dir)
                    yield self.docs_tree

                with Container(id="bookmarks-container"):
                    self.bookmarks = BookmarksList(self.bookmarks_file)
                    yield self.bookmarks

            # Main content area
            with Vertical(id="main"):
                with Container(id="viewer-container"):
                    self.viewer = RichLog(
                        highlight=True,
                        markup=False,
                        wrap=True,
                        id="doc-viewer",
                    )
                    yield self.viewer

                with Container(id="search-container"):
                    self.search_input = Input(placeholder="Search docs... (Press 's' to focus, Esc to clear)")
                    yield self.search_input

        # Status bar
        with Container(id="status-bar"):
            self.status_label = Label("t=tree  v=view  s=search  Tab=cycle  b=bookmark  q=quit")
            yield self.status_label

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        if self.docs_tree:
            self.docs_tree.focus()
        self.update_status("Ready")

    def on_directory_tree_file_selected(self, event: DocsTree.FileSelected) -> None:
        """Handle file selection in the tree."""
        file_path = event.path
        if file_path.suffix == ".md":
            self.load_file(file_path)

    def load_file(self, file_path: Path) -> None:
        """Load and display a markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            self.current_file = file_path
            if self.viewer:
                self.viewer.clear()
                self.viewer.write(RichMarkdown(content))

            # Update status with filename
            rel_path = file_path.relative_to(self.docs_dir)
            self.update_status(f"Viewing: {rel_path}")
        except Exception as e:
            self.update_status(f"Error loading file: {e}")

    def on_key(self, event) -> None:
        """Handle key events — intercept escape when search input is focused."""
        if event.key == "escape" and self.search_input and self.search_input.has_focus:
            self.search_input.value = ""
            if self.docs_tree:
                self.docs_tree.focus()
            if self.current_file:
                self.load_file(self.current_file)
            self.update_status("Search cleared")
            event.prevent_default()
            event.stop()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search input submission."""
        query = event.value.strip().lower()
        if not query:
            return

        self.update_status(f"Searching for '{query}'...")
        results = self.search_docs(query)

        # Render search results in the viewer
        if self.viewer:
            self.viewer.clear()
            if results:
                self.viewer.write(Text(f"Search results for '{query}' ({len(results)} matches)\n", style="bold"))
                for r in results:
                    self.viewer.write(Text(f"\n--- {r['file']} ---", style="cyan"))
                    self.viewer.write(Text(r.get("context", "").strip()))
            else:
                self.viewer.write(Text(f"No results for '{query}'", style="dim"))

        self.update_status(f"Found {len(results)} matches for '{query}'")

    def search_docs(self, query: str, limit: int = 50) -> list[dict]:
        """Search through all markdown files."""
        results = []
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    if query in line.lower():
                        results.append({
                            "file": md_file.relative_to(self.docs_dir),
                            "line": line_num,
                            "content": line.strip(),
                        })
                        if len(results) >= limit:
                            return results
            except Exception:
                continue

        return results

    def action_toggle_bookmark(self) -> None:
        """Toggle bookmark for current file."""
        if not self.current_file or not self.bookmarks:
            return

        rel_path = str(self.current_file.relative_to(self.docs_dir))
        name = self.current_file.stem

        # Check if already bookmarked
        if name in self.bookmarks.bookmarks:
            self.bookmarks.remove_bookmark(name)
            self.update_status(f"Removed bookmark: {name}")
        else:
            self.bookmarks.add_bookmark(name, rel_path)
            self.update_status(f"Added bookmark: {name}")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        if self.search_input:
            self.search_input.focus()

    def action_focus_viewer(self) -> None:
        """Focus the markdown viewer for keyboard scrolling."""
        if self.viewer:
            self.viewer.focus()

    def action_focus_tree(self) -> None:
        """Focus the docs tree."""
        if self.docs_tree:
            self.docs_tree.focus()

    def action_cycle_focus(self) -> None:
        """Cycle focus between tree, viewer, and search."""
        if self.docs_tree and self.docs_tree.has_focus:
            if self.viewer:
                self.viewer.focus()
        elif self.viewer and self.viewer.has_focus:
            if self.search_input:
                self.search_input.focus()
        else:
            if self.docs_tree:
                self.docs_tree.focus()

    def action_clear_search(self) -> None:
        """Clear search and restore viewer."""
        if self.search_input:
            self.search_input.value = ""
        if self.current_file:
            self.load_file(self.current_file)
        self.update_status("Search cleared")

    def action_reload(self) -> None:
        """Reload the current file."""
        if self.current_file:
            self.load_file(self.current_file)
            self.update_status("Reloaded")

    def update_status(self, message: str) -> None:
        """Update the status bar."""
        if self.status_label:
            self.status_label.update(message)


def run_docs_browser(docs_dir: Path, bookmarks_file: Path) -> None:
    """Run the documentation browser TUI."""
    app = DocsBrowserApp(docs_dir, bookmarks_file)
    app.run()
