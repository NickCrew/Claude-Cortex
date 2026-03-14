"""Note CRUD operations for memory vault.

Handles creating, reading, updating, and listing notes
across all note types (knowledge, projects, sessions, fixes).
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import ensure_vault_structure, get_vault_path
from .templates import NoteType


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Lowercase, hyphenated slug
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", slug)

    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    # Strip leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def _validate_path(path: Path, vault_path: Path) -> Path:
    """Validate that path is within vault_path.

    Args:
        path: Path to validate
        vault_path: Vault root path

    Returns:
        Validated absolute path

    Raises:
        ValueError: If path is outside vault
    """
    try:
        # Resolve both paths to absolute
        abs_vault = vault_path.resolve()
        abs_path = path.resolve()

        # Check if path is relative to vault
        abs_path.relative_to(abs_vault)
        return abs_path
    except (ValueError, RuntimeError) as e:
        raise ValueError(f"Path traversal detected: {path} is not within {vault_path}") from e


def get_note_path(
    note_type: NoteType,
    name: str,
    vault_path: Optional[Path] = None,
) -> Path:
    """Get the file path for a note.

    Args:
        note_type: Type of note (knowledge, projects, sessions, fixes)
        name: Note name (will be slugified)
        vault_path: Optional explicit vault path

    Returns:
        Full path to the note file
    """
    if vault_path is None:
        vault_path = get_vault_path()

    slug = slugify(name)
    # Construct path and validate
    full_path = vault_path / note_type.value / f"{slug}.md"
    return _validate_path(full_path, vault_path)


def get_session_note_path(
    title: str,
    date: Optional[datetime] = None,
    vault_path: Optional[Path] = None,
) -> Path:
    """Get the file path for a session note with date prefix.

    Session notes are named: YYYY-MM-DD-<slug>.md

    Args:
        title: Session title
        date: Session date (defaults to today)
        vault_path: Optional explicit vault path

    Returns:
        Full path to the session note file
    """
    if vault_path is None:
        vault_path = get_vault_path()

    if date is None:
        date = datetime.now()

    date_str = date.strftime("%Y-%m-%d")
    slug = slugify(title)
    base_name = f"{date_str}-{slug}"

    sessions_dir = vault_path / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Check for existing notes on same day with same slug
    note_path = sessions_dir / f"{base_name}.md"

    if note_path.exists():
        # Find next available sequence number
        seq = 2
        while True:
            note_path = sessions_dir / f"{base_name}-{seq}.md"
            if not note_path.exists():
                break
            seq += 1

    return _validate_path(note_path, vault_path)


def note_exists(
    note_type: NoteType,
    name: str,
    vault_path: Optional[Path] = None,
) -> bool:
    """Check if a note exists.

    Args:
        note_type: Type of note
        name: Note name
        vault_path: Optional explicit vault path

    Returns:
        True if note exists
    """
    path = get_note_path(note_type, name, vault_path)
    return path.exists()


def create_note(
    note_type: NoteType,
    name: str,
    content: str,
    vault_path: Optional[Path] = None,
) -> Tuple[Path, bool]:
    """Create a new note.

    Args:
        note_type: Type of note
        name: Note name
        content: Markdown content
        vault_path: Optional explicit vault path

    Returns:
        Tuple of (path, created) where created is False if note existed
    """
    if vault_path is None:
        vault_path = get_vault_path()

    # Ensure vault structure exists
    ensure_vault_structure(vault_path)

    path = get_note_path(note_type, name, vault_path)

    # Check if already exists
    existed = path.exists()

    # Write the note
    path.write_text(content, encoding="utf-8")

    return path, not existed


def create_session_note(
    title: str,
    content: str,
    date: Optional[datetime] = None,
    vault_path: Optional[Path] = None,
) -> Path:
    """Create a new session note.

    Session notes use date-prefixed filenames and auto-increment
    if multiple notes are created on the same day with the same title.

    Args:
        title: Session title
        content: Markdown content
        date: Session date (defaults to today)
        vault_path: Optional explicit vault path

    Returns:
        Path to created note
    """
    if vault_path is None:
        vault_path = get_vault_path()

    # Ensure vault structure exists
    ensure_vault_structure(vault_path)

    path = get_session_note_path(title, date, vault_path)

    # Write the note
    path.write_text(content, encoding="utf-8")

    return path


def read_note(
    note_type: NoteType,
    name: str,
    vault_path: Optional[Path] = None,
) -> Optional[str]:
    """Read a note's content.

    Args:
        note_type: Type of note
        name: Note name
        vault_path: Optional explicit vault path

    Returns:
        Note content or None if not found
    """
    path = get_note_path(note_type, name, vault_path)

    if not path.exists():
        return None

    return path.read_text(encoding="utf-8")


def update_note(
    note_type: NoteType,
    name: str,
    content: str,
    vault_path: Optional[Path] = None,
) -> Tuple[Path, bool]:
    """Update an existing note or create if not exists.

    Args:
        note_type: Type of note
        name: Note name
        content: New markdown content
        vault_path: Optional explicit vault path

    Returns:
        Tuple of (path, updated) where updated is True if note existed
    """
    return create_note(note_type, name, content, vault_path)


def list_notes(
    note_type: Optional[NoteType] = None,
    vault_path: Optional[Path] = None,
    recent: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """List notes in the vault.

    Args:
        note_type: Filter by note type (None for all)
        vault_path: Optional explicit vault path
        recent: Limit to N most recent notes
        tags: Filter by tags

    Returns:
        List of note metadata dicts with keys:
        - path: Full path to note
        - name: Note name (slug)
        - type: Note type
        - title: Extracted title from content
        - modified: Last modified timestamp
        - tags: List of tags if found
    """
    if vault_path is None:
        vault_path = get_vault_path()

    notes = []

    # Determine which directories to scan
    if note_type is not None:
        dirs = [vault_path / note_type.value]
    else:
        dirs = [vault_path / nt.value for nt in NoteType]

    for dir_path in dirs:
        if not dir_path.exists():
            continue

        note_type_value = dir_path.name

        for file_path in dir_path.glob("*.md"):
            note_info = _extract_note_info(file_path, note_type_value)

            # Filter by tags if specified
            if tags:
                note_tags = note_info.get("tags", [])
                if not any(tag in note_tags for tag in tags):
                    continue

            notes.append(note_info)

    # Sort by modified time (most recent first)
    notes.sort(key=lambda x: x["modified"], reverse=True)

    # Limit to recent if specified
    if recent is not None:
        notes = notes[:recent]

    return notes


def _extract_note_info(file_path: Path, note_type: str) -> Dict[str, Any]:
    """Extract metadata from a note file.

    Args:
        file_path: Path to note file
        note_type: Note type (directory name)

    Returns:
        Note metadata dict
    """
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Extract title (first # heading)
    title = file_path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract tags
    tags = []
    for line in lines:
        if line.startswith("tags:"):
            # Parse tags like: tags: #knowledge #python
            tag_str = line[5:].strip()
            tags = [t.strip().lstrip("#") for t in tag_str.split() if t.strip()]
            break

    # Get modification time
    stat = file_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime)

    return {
        "path": str(file_path),
        "name": file_path.stem,
        "type": note_type,
        "title": title,
        "modified": modified,
        "tags": tags,
    }


def delete_note(
    note_type: NoteType,
    name: str,
    vault_path: Optional[Path] = None,
) -> bool:
    """Delete a note.

    Args:
        note_type: Type of note
        name: Note name
        vault_path: Optional explicit vault path

    Returns:
        True if note was deleted, False if not found
    """
    path = get_note_path(note_type, name, vault_path)

    if not path.exists():
        return False

    path.unlink()
    return True


def extract_topic_from_text(text: str) -> str:
    """Extract a topic name from text for knowledge notes.

    Uses simple heuristics to find the main subject:
    1. Look for "X is..." pattern
    2. Look for quoted text
    3. Fall back to first noun phrase (simplified)

    Args:
        text: Input text to extract topic from

    Returns:
        Extracted topic string
    """
    # Pattern 1: "X is..." (most common for corrections)
    is_match = re.search(r"^([^,]+?)\s+is\s+", text, re.IGNORECASE)
    if is_match:
        return is_match.group(1).strip()

    # Pattern 2: Quoted text
    quote_match = re.search(r'"([^"]+)"', text)
    if quote_match:
        return quote_match.group(1).strip()

    # Pattern 3: Text before "for", "when", "because"
    for_match = re.search(
        r"^(.+?)\s+(?:for|when|because|not|uses|handles)\s+",
        text,
        re.IGNORECASE,
    )
    if for_match:
        return for_match.group(1).strip()

    # Fallback: First 3-4 words
    words = text.split()
    if len(words) <= 4:
        return text.strip()

    return " ".join(words[:4]).strip()
