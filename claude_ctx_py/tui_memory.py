"""Memory Vault Viewer Screen."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Optional, List, Dict, Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Markdown,
    Static,
    Label,
)
from textual import on

from .tui_icons import Icons
from .memory import (
    list_notes,
    read_note,
    NoteType,
    memory_remember,
    memory_project,
    memory_capture,
    memory_fix,
)
from .tui.dialogs import MemoryNoteCreateDialog


class MemoryScreen(Screen[None]):
    """Screen for browsing and managing the Memory Vault."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("/", "focus_search", "Search"),
        Binding("n", "new_note", "New Note"),
        Binding("r", "refresh_notes", "Refresh"),
    ]

    CSS = """
    MemoryScreen {
        layers: base overlay;
    }

    #memory-container {
        height: 100%;
        width: 100%;
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 2fr;
    }

    #left-pane {
        height: 100%;
        border-right: solid $primary;
        background: $surface;
    }

    #right-pane {
        height: 100%;
        background: $surface-darken-1;
        padding: 1 2;
        overflow-y: auto;
    }

    #search-input {
        dock: top;
        margin: 1;
        border: tall $accent;
    }

    #notes-table {
        height: 1fr;
        width: 100%;
    }

    .note-content {
        height: 100%;
    }
    
    #empty-state {
        text-align: center;
        color: $text-muted;
        padding-top: 20%;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header(show_clock=True)
        
        with Container(id="memory-container"):
            with Vertical(id="left-pane"):
                yield Input(placeholder="Search memories... (/)", id="search-input")
                yield DataTable(id="notes-table", cursor_type="row")
            
            with Vertical(id="right-pane"):
                yield Markdown(id="note-view")
                yield Static("Select a note to view details", id="empty-state")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen."""
        self.load_notes()

    def load_notes(self, query: str = "") -> None:
        """Load notes into the table."""
        table = self.query_one("#notes-table", DataTable)
        table.clear(columns=True)
        table.add_column("Type", width=10)
        table.add_column("Title")
        table.add_column("Date", width=12)

        notes = list_notes()
        
        # Filter locally for now
        if query:
            query = query.lower()
            notes = [
                n for n in notes 
                if query in n["title"].lower() 
                or query in n["name"].lower()
                or any(query in t.lower() for t in n.get("tags", []))
            ]

        for note in notes:
            note_type = note["type"]
            icon = self._get_type_icon(note_type)
            date_str = note["modified"].strftime("%Y-%m-%d")
            
            # Style the type
            type_styled = f"{icon} {note_type.title()}"
            
            table.add_row(
                type_styled,
                note["title"],
                date_str,
                key=note["path"]  # Store path as key
            )
        
        search_input = self.query_one("#search-input", Input)
        search_input.border_subtitle = f"{len(notes)} notes found"

    def _get_type_icon(self, note_type: str) -> str:
        """Get icon for note type."""
        if note_type == "knowledge":
            return "🧠"
        elif note_type == "projects":
            return "🏗️"
        elif note_type == "sessions":
            return "📅"
        elif note_type == "fixes":
            return "🔧"
        return "📝"

    @on(Input.Changed, "#search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input."""
        self.load_notes(event.value)

    @on(DataTable.RowSelected, "#notes-table")
    def on_note_selected(self, event: DataTable.RowSelected) -> None:
        """Handle note selection."""
        path = event.row_key.value
        if not path:
            return
            
        try:
            # We have the full path from list_notes
            from pathlib import Path
            content = Path(path).read_text(encoding="utf-8")
            
            # Hide empty state, show content
            self.query_one("#empty-state").display = False
            md_view = self.query_one("#note-view", Markdown)
            md_view.display = True
            md_view.update(content)
            
        except Exception as e:
            self.notify(f"Error reading note: {e}", severity="error")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_refresh_notes(self) -> None:
        """Refresh the notes list."""
        query = self.query_one("#search-input", Input).value
        self.load_notes(query)
        self.notify("Memory Vault refreshed")

    def action_new_note(self) -> None:
        """Create a new note."""
        dialog = MemoryNoteCreateDialog("New Memory Note")
        self.app.push_screen(dialog, callback=self._handle_new_note_create)

    def _normalize_note_type(self, raw: str) -> Optional[str]:
        note_type = raw.strip().lower()
        aliases = {
            "knowledge": "knowledge",
            "project": "projects",
            "projects": "projects",
            "session": "sessions",
            "sessions": "sessions",
            "fix": "fixes",
            "fixes": "fixes",
        }
        return aliases.get(note_type)

    def _handle_new_note_create(self, result: Optional[Dict[str, str]]) -> None:
        if not result:
            return

        note_type_raw = result.get("note_type", "")
        title = result.get("title", "").strip()
        summary = result.get("summary", "").strip()

        if not title:
            self.notify("Note title is required", severity="warning", timeout=2)
            return

        note_type = self._normalize_note_type(note_type_raw)
        if not note_type:
            self.notify(
                "Invalid note type. Use: knowledge, projects, sessions, fixes",
                severity="error",
                timeout=3,
            )
            return

        try:
            if note_type == "knowledge":
                text = summary or "Captured via TUI"
                exit_code, message = memory_remember(text=text, topic=title)
            elif note_type == "projects":
                exit_code, message = memory_project(
                    name=title,
                    purpose=summary or None,
                    path=None,
                    related=None,
                    update=False,
                )
            elif note_type == "sessions":
                session_summary = summary or "Session captured via TUI"
                exit_code, message = memory_capture(
                    title=title,
                    summary=session_summary,
                    quick=True,
                )
            else:
                problem = summary or "Issue documented via TUI"
                exit_code, message = memory_fix(
                    title=title,
                    problem=problem,
                )
        except Exception as e:
            self.notify(f"Error creating note: {e}", severity="error")
            return

        clean = re.sub(r"\x1b\[[0-9;]*m", "", message)
        if exit_code == 0:
            self.notify(clean or "Created memory note", severity="information", timeout=2)
            self.load_notes(self.query_one("#search-input", Input).value)
        else:
            self.notify(clean or "Failed to create memory note", severity="error", timeout=3)
