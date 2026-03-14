"""Memory capture system for persistent knowledge storage.

This module provides functionality for capturing and storing:
- Domain knowledge corrections and gotchas
- Project context and relationships
- Session summaries and decisions
- Bug fixes and solutions

Notes are stored in Markdown format in ~/basic-memory/ by default.
"""

from .config import (
    MemoryConfig,
    get_config,
    save_config,
    get_vault_path,
    is_auto_capture_enabled,
    set_auto_capture_enabled,
)

from .templates import (
    NoteType,
    render_knowledge_note,
    render_project_note,
    render_session_note,
    render_fix_note,
)

from .notes import (
    create_note,
    update_note,
    read_note,
    list_notes,
    note_exists,
    get_note_path,
    slugify,
)

from .capture import (
    memory_remember,
    memory_project,
    memory_capture,
    memory_fix,
    memory_auto,
    memory_list,
    memory_search,
    get_vault_stats,
)

__all__ = [
    # Config
    "MemoryConfig",
    "get_config",
    "save_config",
    "get_vault_path",
    "is_auto_capture_enabled",
    "set_auto_capture_enabled",
    # Templates
    "NoteType",
    "render_knowledge_note",
    "render_project_note",
    "render_session_note",
    "render_fix_note",
    # Notes
    "create_note",
    "update_note",
    "read_note",
    "list_notes",
    "note_exists",
    "get_note_path",
    "slugify",
    # Capture (CLI functions)
    "memory_remember",
    "memory_project",
    "memory_capture",
    "memory_fix",
    "memory_auto",
    "memory_list",
    "memory_search",
    "get_vault_stats",
]
