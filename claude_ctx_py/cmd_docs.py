"""Documentation viewer commands."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.tree import Tree

try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources  # type: ignore


def _get_bundled_docs_root() -> Optional[Path]:
    """Resolve the path to the bundled docs directory."""
    # First try relative to this file (development mode)
    here = Path(__file__).parent
    local_docs = here / "docs"
    if local_docs.is_dir():
        return local_docs

    # Then try package resources (installed mode)
    try:
        # For Python 3.9+
        import importlib.resources
        files = importlib.resources.files("claude_ctx_py")
        pkg_docs = files.joinpath("docs")
        if pkg_docs.is_dir():
             # In some installed environments (zip), this might not be a direct path
             # but we'll assume standard install for now or use 'as_file' if needed
             pass
        
        # Fallback to direct path resolution if possible
        # Since we copied files to claude_ctx_py/docs, it should be findable
        return local_docs
    except Exception:
        pass
        
    return None

def list_docs() -> Tuple[int, str]:
    """List available documentation."""
    root = _get_bundled_docs_root()
    if not root:
        return 1, "Documentation not found. (Bundled 'docs' directory missing)"

    console = Console()
    tree = Tree("📚 Cortex Documentation")
    
    # Add top-level files
    for path in sorted(root.glob("*.md")):
        tree.add(f"[green]{path.name}[/green]")

    # Add subdirectories
    for path in sorted(root.iterdir()):
        if path.is_dir() and not path.name.startswith("."):
            branch = tree.add(f"[bold cyan]{path.name}/[/bold cyan]")
            has_files = False
            for subpath in sorted(path.rglob("*.md")):
                rel_path = subpath.relative_to(root)
                branch.add(f"[green]{rel_path}[/green]")
                has_files = True
            if not has_files:
                branch.label = f"[dim]{path.name}/ (empty)[/dim]"

    with console.capture() as capture:
        console.print(tree)
    
    return 0, capture.get()


def view_doc(name: str) -> Tuple[int, str]:
    """View a specific documentation file."""
    root = _get_bundled_docs_root()
    if not root:
        return 1, "Documentation not found."

    # Try exact match
    target = root / name
    if not target.is_file():
        # Try with .md extension
        target = root / f"{name}.md"
    
    if not target.is_file():
         # Try recursive search if it's just a filename
        found = list(root.rglob(name)) or list(root.rglob(f"{name}.md"))
        if found:
            target = found[0]

    if not target.is_file():
        return 1, f"Document '{name}' not found."

    try:
        content = target.read_text(encoding="utf-8")
        console = Console()
        md = Markdown(content)
        with console.capture() as capture:
            console.print(md)
        return 0, capture.get()
    except Exception as e:
        return 1, f"Error reading document: {e}"
