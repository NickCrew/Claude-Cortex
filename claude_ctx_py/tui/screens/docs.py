"""Documentation viewer screen for the TUI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Footer, Header, Markdown, Tree
from textual.widgets.tree import TreeNode

from ...cmd_docs import _get_bundled_docs_root


class DocsScreen(Screen[None]):
    """Screen for viewing bundled documentation."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.docs_root = _get_bundled_docs_root()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="docs-container"):
            yield Tree("Documentation", id="docs-tree")
            yield Markdown("", id="docs-content")
        yield Footer()

    def on_mount(self) -> None:
        """Load the documentation tree."""
        if not self.docs_root:
            self.query_one(Markdown).update("# Documentation not found\n\nBundled docs directory is missing.")
            return

        tree = self.query_one(Tree)
        tree.root.expand()
        
        self._populate_tree(self.docs_root, tree.root)
        
        # Load README by default if exists
        readme = self.docs_root / "README.md"
        if readme.exists():
            self.load_doc(readme)

    def _populate_tree(self, path: Path, node: "TreeNode[Path]") -> None:
        """Recursively populate the file tree."""
        # Files first
        for file_path in sorted(path.glob("*.md")):
            node.add(file_path.name, data=file_path)

        # Then directories
        for dir_path in sorted(path.iterdir()):
            if dir_path.is_dir() and not dir_path.name.startswith("."):
                sub_node = node.add(dir_path.name, expand=False)
                self._populate_tree(dir_path, sub_node)

    def on_tree_node_selected(self, event: "Tree.NodeSelected[Path]") -> None:
        """Handle tree selection."""
        if event.node.data:
            self.load_doc(event.node.data)

    def load_doc(self, path: Path) -> None:
        """Load and display a markdown file."""
        try:
            content = path.read_text(encoding="utf-8")
            self.query_one(Markdown).update(content)
        except Exception as e:
            self.query_one(Markdown).update(f"# Error\n\nFailed to load {path.name}: {e}")

