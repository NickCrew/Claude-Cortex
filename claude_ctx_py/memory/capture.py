"""Core capture functions for memory CLI commands.

Implements the main entry points for:
- memory_remember: Quick domain knowledge capture
- memory_project: Project context capture
- memory_capture: Session summary capture
- memory_fix: Bug fix documentation
- memory_auto: Auto-capture toggle
- memory_list: List notes
- memory_search: Search notes
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import (
    get_config,
    get_vault_path,
    ensure_vault_structure,
    is_auto_capture_enabled,
    set_auto_capture_enabled,
    get_last_capture,
    update_last_capture,
)
from .notes import (
    create_note,
    create_session_note,
    read_note,
    list_notes as list_notes_core,
    note_exists,
    extract_topic_from_text,
    slugify,
)
from .search import search_notes as search_notes_core
from .templates import (
    NoteType,
    render_knowledge_note,
    render_project_note,
    render_session_note,
    render_fix_note,
    append_to_knowledge_note,
)


# Color codes for output
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
NC = "\033[0m"  # No color


def _color(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{NC}"


def memory_remember(
    text: str,
    topic: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Tuple[int, str]:
    """Quick capture of domain knowledge.

    Args:
        text: Knowledge text to capture
        topic: Optional explicit topic name
        tags: Optional additional tags

    Returns:
        Tuple of (exit_code, message)
    """
    # Extract topic if not provided
    if topic is None:
        topic = extract_topic_from_text(text)

    if not topic:
        return 1, _color("Could not determine topic from text. Use --topic to specify.", RED)

    tags = tags or []

    # Check if note exists
    if note_exists(NoteType.KNOWLEDGE, topic):
        # Append to existing note
        existing = read_note(NoteType.KNOWLEDGE, topic)
        if existing:
            updated = append_to_knowledge_note(existing, [text])
            path, _ = create_note(NoteType.KNOWLEDGE, topic, updated)
            return 0, _color(f"Updated: {path}", GREEN)

    # Create new knowledge note
    content = render_knowledge_note(
        topic=topic,
        summary=text[:100] + "..." if len(text) > 100 else text,
        details=[text],
        tags=tags,
    )

    path, created = create_note(NoteType.KNOWLEDGE, topic, content)

    if created:
        return 0, _color(f"Created: {path}", GREEN)
    else:
        return 0, _color(f"Updated: {path}", GREEN)


def memory_project(
    name: str,
    path: Optional[str] = None,
    purpose: Optional[str] = None,
    related: Optional[List[str]] = None,
    update: bool = False,
) -> Tuple[int, str]:
    """Capture or update project context.

    Args:
        name: Project name
        path: Repository path
        purpose: One-line description
        related: Related project names
        update: Whether to update existing

    Returns:
        Tuple of (exit_code, message)
    """
    vault_path = get_vault_path()
    ensure_vault_structure(vault_path)

    # Convert related to proper format
    related_projects = None
    if related:
        related_projects = [(r, "related") for r in related]

    # Create content
    content = render_project_note(
        name=name,
        purpose=purpose or "No description provided",
        path=path,
        related_projects=related_projects,
    )

    note_path, created = create_note(NoteType.PROJECT, name, content)

    if created:
        return 0, _color(f"Created project note: {note_path}", GREEN)
    elif update:
        return 0, _color(f"Updated project note: {note_path}", GREEN)
    else:
        return 0, _color(f"Updated project note: {note_path}", YELLOW)


def memory_capture(
    title: Optional[str] = None,
    summary: Optional[str] = None,
    decisions: Optional[List[str]] = None,
    implementations: Optional[List[str]] = None,
    open_items: Optional[List[str]] = None,
    project: Optional[str] = None,
    quick: bool = False,
) -> Tuple[int, str]:
    """Capture session summary.

    Args:
        title: Session title
        summary: What we worked on
        decisions: Decisions made
        implementations: What was built/changed
        open_items: Things left to do
        project: Related project name
        quick: Minimal capture (summary only)

    Returns:
        Tuple of (exit_code, message)
    """
    vault_path = get_vault_path()
    ensure_vault_structure(vault_path)

    # Generate title if not provided
    if title is None:
        now = datetime.now()
        title = f"Session {now.strftime('%H:%M')}"

    # Generate summary if not provided
    if summary is None:
        summary = "Session captured via CLI"

    # Related projects
    related = [project] if project else None

    # Determine tags
    tags = ["session"]
    if project:
        tags.append(project)

    content = render_session_note(
        title=title,
        summary=summary,
        decisions=decisions,
        implementations=implementations,
        open_items=open_items,
        related=related,
        tags=tags,
    )

    note_path = create_session_note(title, content)

    # Update last capture timestamp
    update_last_capture()

    return 0, _color(f"Created session note: {note_path}", GREEN)


def memory_fix(
    title: str,
    problem: Optional[str] = None,
    cause: Optional[str] = None,
    solution: Optional[str] = None,
    files: Optional[List[str]] = None,
    project: Optional[str] = None,
) -> Tuple[int, str]:
    """Record a bug fix.

    Args:
        title: Issue title
        problem: What was broken/wrong
        cause: Root cause
        solution: How we fixed it
        files: Changed file paths
        project: Related project name

    Returns:
        Tuple of (exit_code, message)
    """
    vault_path = get_vault_path()
    ensure_vault_structure(vault_path)

    # Set defaults for required fields
    problem = problem or "Issue documented via CLI"
    cause = cause or "To be determined"
    solution = solution or "Fix documented via CLI"

    # Format files changed
    files_changed = None
    if files:
        files_changed = [(f, "modified") for f in files]

    # Related
    related = [project] if project else None

    # Tags
    tags = ["fix"]
    if project:
        tags.append(project)

    content = render_fix_note(
        title=title,
        problem=problem,
        cause=cause,
        solution=solution,
        files_changed=files_changed,
        related=related,
        tags=tags,
    )

    note_path, _ = create_note(NoteType.FIX, title, content)

    return 0, _color(f"Created fix note: {note_path}", GREEN)


def memory_auto(
    action: Optional[str] = None,
) -> Tuple[int, str]:
    """Toggle or check auto-capture state.

    Args:
        action: "on", "off", or "status" (default)

    Returns:
        Tuple of (exit_code, message)
    """
    if action == "on":
        set_auto_capture_enabled(True)
        return 0, _color("Auto-capture enabled", GREEN)

    if action == "off":
        set_auto_capture_enabled(False)
        return 0, _color("Auto-capture disabled", YELLOW)

    # Status
    enabled = is_auto_capture_enabled()
    last = get_last_capture()

    lines = [
        f"Auto-capture: {_color('enabled', GREEN) if enabled else _color('disabled', YELLOW)}",
    ]

    if last:
        lines.append(f"Last capture: {last.strftime('%Y-%m-%d %H:%M')}")
    else:
        lines.append("Last capture: never")

    return 0, "\n".join(lines)


def memory_list(
    note_type: Optional[str] = None,
    recent: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Tuple[int, str]:
    """List notes in the vault.

    Args:
        note_type: Filter by type ("knowledge", "projects", "sessions", "fixes")
        recent: Limit to N most recent
        tags: Filter by tags

    Returns:
        Tuple of (exit_code, message)
    """
    # Parse note type
    nt = None
    if note_type:
        try:
            nt = NoteType(note_type)
        except ValueError:
            return 1, _color(f"Invalid note type: {note_type}. Use: knowledge, projects, sessions, fixes", RED)

    notes = list_notes_core(note_type=nt, recent=recent, tags=tags)

    if not notes:
        return 0, _color("No notes found", YELLOW)

    # Format output
    lines = []

    # Group by type
    current_type = None
    for note in notes:
        if note["type"] != current_type:
            current_type = note["type"]
            lines.append("")
            lines.append(_color(f"[{current_type}]", BLUE))

        # Format note entry
        modified = note["modified"].strftime("%Y-%m-%d")
        tags_str = " ".join(f"#{t}" for t in note.get("tags", [])[:3])

        lines.append(f"  {note['title']}")
        lines.append(f"    {_color(modified, YELLOW)} {tags_str}")

    return 0, "\n".join(lines)


def memory_search(
    query: str,
    note_type: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[int, str]:
    """Search notes by content.

    Args:
        query: Search query
        note_type: Filter by type
        limit: Max results

    Returns:
        Tuple of (exit_code, message)
    """
    # Parse note type
    nt = None
    if note_type:
        try:
            nt = NoteType(note_type)
        except ValueError:
            return 1, _color(f"Invalid note type: {note_type}. Use: knowledge, projects, sessions, fixes", RED)

    results = search_notes_core(query, note_type=nt, limit=limit)

    if not results:
        return 0, _color(f"No results for: {query}", YELLOW)

    # Format output
    lines = [_color(f"Found {len(results)} result(s) for '{query}':", GREEN), ""]

    for result in results:
        lines.append(f"{_color(result['title'], BLUE)} ({result['type']})")
        lines.append(f"  {result['path']}")

        # Show snippet
        snippet = result.get("snippet", "")
        if snippet:
            # Truncate and indent snippet
            snippet_lines = snippet.split("\n")[:3]
            for sl in snippet_lines:
                lines.append(f"    {sl[:80]}")

        lines.append("")

    return 0, "\n".join(lines)


def get_vault_stats() -> Dict[str, Any]:
    """Get statistics about the memory vault.

    Returns:
        Dict with stats about each note type
    """
    vault_path = get_vault_path()

    stats: Dict[str, Any] = {
        "vault_path": str(vault_path),
        "exists": vault_path.exists(),
        "types": {},
    }

    for nt in NoteType:
        dir_path = vault_path / nt.value
        if dir_path.exists():
            count = len(list(dir_path.glob("*.md")))
            stats["types"][nt.value] = count
        else:
            stats["types"][nt.value] = 0

    stats["total"] = sum(stats["types"].values())

    return stats
