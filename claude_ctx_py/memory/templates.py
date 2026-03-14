"""Markdown templates for memory notes.

Defines template rendering functions for each note type:
- Knowledge notes: Domain knowledge, gotchas, corrections
- Project notes: Project context and relationships
- Session notes: Session summaries and decisions
- Fix notes: Bug fixes and solutions
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Tuple


class NoteType(Enum):
    """Types of memory notes."""

    KNOWLEDGE = "knowledge"
    PROJECT = "projects"
    SESSION = "sessions"
    FIX = "fixes"


def _format_tags(tags: List[str]) -> str:
    """Format tags for YAML frontmatter style."""
    if not tags:
        return ""
    return " ".join(f"#{tag}" for tag in tags)


def _format_date(dt: Optional[datetime] = None) -> str:
    """Format date as YYYY-MM-DD."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def _format_related(related: List[str], note_type: NoteType) -> str:
    """Format related links section."""
    if not related:
        return ""

    lines = ["## Related"]
    for item in related:
        # Determine if it's a project or knowledge reference
        if "/" in item:
            lines.append(f"- [{item}]({item})")
        else:
            # Default to projects for cross-references
            lines.append(f"- [{item}](../projects/{item}.md)")

    return "\n".join(lines)


def render_knowledge_note(
    topic: str,
    summary: str,
    details: List[str],
    tags: Optional[List[str]] = None,
    related: Optional[List[str]] = None,
    captured: Optional[datetime] = None,
) -> str:
    """Render a knowledge note.

    Args:
        topic: Topic name (title of the note)
        summary: One-line description
        details: List of key facts, corrections, gotchas
        tags: Optional list of tags
        related: Optional list of related notes
        captured: Capture date (defaults to now)

    Returns:
        Rendered markdown content
    """
    tags = tags or ["knowledge"]
    if "knowledge" not in tags:
        tags = ["knowledge"] + tags

    related = related or []
    date_str = _format_date(captured)

    details_section = "\n".join(f"- {detail}" for detail in details) if details else ""
    related_section = _format_related(related, NoteType.KNOWLEDGE)

    sections = [
        f"# {topic}",
        "",
        "## Summary",
        summary,
        "",
        "## Details",
        details_section,
    ]

    if related_section:
        sections.extend(["", related_section])

    sections.extend([
        "",
        "---",
        f"tags: {_format_tags(tags)}",
        f"captured: {date_str}",
    ])

    return "\n".join(sections)


def render_project_note(
    name: str,
    purpose: str,
    path: Optional[str] = None,
    remote: Optional[str] = None,
    architecture: Optional[str] = None,
    related_projects: Optional[List[Tuple[str, str]]] = None,
    key_files: Optional[List[Tuple[str, str]]] = None,
    gotchas: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    captured: Optional[datetime] = None,
    updated: Optional[datetime] = None,
) -> str:
    """Render a project note.

    Args:
        name: Project name
        purpose: What this project does
        path: Local repository path
        remote: Git remote URL
        architecture: Key components and relationships
        related_projects: List of (name, relationship) tuples
        key_files: List of (path, description) tuples
        gotchas: Things to remember
        tags: Optional list of tags
        captured: Capture date
        updated: Last updated date

    Returns:
        Rendered markdown content
    """
    tags = tags or ["project"]
    if "project" not in tags:
        tags = ["project"] + tags

    date_str = _format_date(captured)

    sections = [
        f"# {name}",
        "",
        "## Purpose",
        purpose,
    ]

    # Repository section
    if path or remote:
        sections.extend(["", "## Repository"])
        if path:
            sections.append(f"- Path: `{path}`")
        if remote:
            sections.append(f"- Remote: {remote}")

    # Architecture section
    if architecture:
        sections.extend([
            "",
            "## Architecture",
            architecture,
        ])

    # Related projects
    if related_projects:
        sections.extend(["", "## Related Projects"])
        for proj_name, relationship in related_projects:
            sections.append(f"- [{proj_name}](../projects/{proj_name}.md) - {relationship}")

    # Key files
    if key_files:
        sections.extend(["", "## Key Files"])
        for file_path, description in key_files:
            sections.append(f"- `{file_path}` - {description}")

    # Gotchas
    if gotchas:
        sections.extend(["", "## Gotchas"])
        for gotcha in gotchas:
            sections.append(f"- {gotcha}")

    # Footer
    sections.extend([
        "",
        "---",
        f"tags: {_format_tags(tags)}",
        f"captured: {date_str}",
    ])

    if updated:
        sections.append(f"updated: {_format_date(updated)}")

    return "\n".join(sections)


def render_session_note(
    title: str,
    summary: str,
    decisions: Optional[List[str]] = None,
    implementations: Optional[List[str]] = None,
    open_items: Optional[List[str]] = None,
    related: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    captured: Optional[datetime] = None,
) -> str:
    """Render a session note.

    Args:
        title: Session title
        summary: What we worked on
        decisions: Decisions made and rationale
        implementations: What was built/changed
        open_items: Things left to do
        related: Related projects/notes
        tags: Optional list of tags
        captured: Capture date

    Returns:
        Rendered markdown content
    """
    tags = tags or ["session"]
    if "session" not in tags:
        tags = ["session"] + tags

    captured = captured or datetime.now()
    date_str = _format_date(captured)

    sections = [
        f"# {title}",
        "",
        "## Date",
        date_str,
        "",
        "## Summary",
        summary,
    ]

    if decisions:
        sections.extend(["", "## Decisions"])
        for decision in decisions:
            sections.append(f"- {decision}")

    if implementations:
        sections.extend(["", "## Implementations"])
        for impl in implementations:
            sections.append(f"- {impl}")

    if open_items:
        sections.extend(["", "## Open Items"])
        for item in open_items:
            sections.append(f"- {item}")

    if related:
        sections.extend(["", "## Related"])
        for item in related:
            if item.startswith("../") or "/" in item:
                sections.append(f"- [{item}]({item})")
            else:
                sections.append(f"- [{item}](../projects/{item}.md)")

    sections.extend([
        "",
        "---",
        f"tags: {_format_tags(tags)}",
        f"captured: {date_str}",
    ])

    return "\n".join(sections)


def render_fix_note(
    title: str,
    problem: str,
    cause: str,
    solution: str,
    files_changed: Optional[List[Tuple[str, str]]] = None,
    prevention: Optional[str] = None,
    related: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    captured: Optional[datetime] = None,
) -> str:
    """Render a fix note.

    Args:
        title: Issue title
        problem: What was broken/wrong
        cause: Root cause
        solution: How we fixed it
        files_changed: List of (path, description) tuples
        prevention: How to avoid this in future
        related: Related projects/notes
        tags: Optional list of tags
        captured: Capture date

    Returns:
        Rendered markdown content
    """
    tags = tags or ["fix"]
    if "fix" not in tags:
        tags = ["fix"] + tags

    date_str = _format_date(captured)

    sections = [
        f"# {title}",
        "",
        "## Problem",
        problem,
        "",
        "## Cause",
        cause,
        "",
        "## Solution",
        solution,
    ]

    if files_changed:
        sections.extend(["", "## Files Changed"])
        for file_path, description in files_changed:
            sections.append(f"- `{file_path}` - {description}")

    if prevention:
        sections.extend([
            "",
            "## Prevention",
            prevention,
        ])

    if related:
        sections.extend(["", "## Related"])
        for item in related:
            if item.startswith("../") or "/" in item:
                sections.append(f"- [{item}]({item})")
            else:
                sections.append(f"- [{item}](../projects/{item}.md)")

    sections.extend([
        "",
        "---",
        f"tags: {_format_tags(tags)}",
        f"captured: {date_str}",
    ])

    return "\n".join(sections)


def append_to_knowledge_note(
    existing_content: str,
    new_details: List[str],
    updated: Optional[datetime] = None,
) -> str:
    """Append new details to an existing knowledge note.

    Args:
        existing_content: Current note content
        new_details: New details to add
        updated: Update timestamp

    Returns:
        Updated markdown content
    """
    date_str = _format_date(updated)

    # Find the Details section and append
    lines = existing_content.split("\n")
    result_lines = []
    in_details = False
    details_added = False

    for i, line in enumerate(lines):
        result_lines.append(line)

        if line.strip() == "## Details":
            in_details = True
            continue

        if in_details and not details_added:
            # Check if we've reached the next section or end
            if line.startswith("## ") or line.startswith("---"):
                # Insert new details before this line
                result_lines.pop()  # Remove the current line temporarily
                for detail in new_details:
                    result_lines.append(f"- {detail}")
                result_lines.append(line)  # Re-add the current line
                details_added = True
                in_details = False
            elif line.strip() == "":
                # End of details section items, add new ones
                for detail in new_details:
                    result_lines.append(f"- {detail}")
                details_added = True
                in_details = False

    # If we never added (details section at end), add before footer
    if not details_added:
        # Find --- separator and insert before
        for i, line in enumerate(result_lines):
            if line.strip() == "---":
                for detail in reversed(new_details):
                    result_lines.insert(i, f"- {detail}")
                break

    # Update the 'updated' field or add it
    final_lines = []
    updated_field_found = False

    for line in result_lines:
        if line.startswith("updated:"):
            final_lines.append(f"updated: {date_str}")
            updated_field_found = True
        else:
            final_lines.append(line)

    if not updated_field_found:
        final_lines.append(f"updated: {date_str}")

    return "\n".join(final_lines)
