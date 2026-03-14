"""Search functionality for memory vault.

Provides full-text search across all note types with
snippet extraction and relevance scoring.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import get_vault_path
from .templates import NoteType


def search_notes(
    query: str,
    note_type: Optional[NoteType] = None,
    vault_path: Optional[Path] = None,
    limit: Optional[int] = None,
    context_lines: int = 1,
) -> List[Dict[str, Any]]:
    """Search for notes matching a query.

    Performs case-insensitive full-text search across note content.

    Args:
        query: Search query string
        note_type: Filter by note type (None for all)
        vault_path: Optional explicit vault path
        limit: Maximum number of results
        context_lines: Number of context lines around matches

    Returns:
        List of search result dicts with keys:
        - path: Full path to note
        - name: Note name (slug)
        - type: Note type
        - title: Note title
        - snippet: Text snippet containing match
        - score: Relevance score (higher is better)
    """
    if vault_path is None:
        vault_path = get_vault_path()

    results = []

    # Compile case-insensitive regex
    try:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
    except re.error:
        # Invalid regex, use literal search
        pattern = re.compile(re.escape(query), re.IGNORECASE)

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
            result = _search_file(file_path, pattern, note_type_value, context_lines)
            if result is not None:
                results.append(result)

    # Sort by score (higher first)
    results.sort(key=lambda x: x["score"], reverse=True)

    # Apply limit if specified
    if limit is not None:
        results = results[:limit]

    return results


def _search_file(
    file_path: Path,
    pattern: re.Pattern[str],
    note_type: str,
    context_lines: int,
) -> Optional[Dict[str, Any]]:
    """Search a single file for pattern matches.

    Args:
        file_path: Path to file
        pattern: Compiled regex pattern
        note_type: Note type string
        context_lines: Number of context lines

    Returns:
        Search result dict or None if no matches
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = content.split("\n")

    # Find all matches
    matches = list(pattern.finditer(content))
    if not matches:
        return None

    # Extract title
    title = file_path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Calculate score based on:
    # - Number of matches
    # - Match in title (bonus)
    # - Match in summary (bonus)
    score = len(matches)

    if pattern.search(title):
        score += 10  # Title match bonus

    # Check for match in summary section
    in_summary = False
    for line in lines:
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## "):
                break
            if pattern.search(line):
                score += 5  # Summary match bonus
                break

    # Extract snippet around first match
    snippet = _extract_snippet(content, matches[0], context_lines)

    return {
        "path": str(file_path),
        "name": file_path.stem,
        "type": note_type,
        "title": title,
        "snippet": snippet,
        "score": score,
        "match_count": len(matches),
    }


def _extract_snippet(
    content: str,
    match: re.Match[str],
    context_lines: int,
) -> str:
    """Extract a snippet around a match.

    Args:
        content: Full file content
        match: Regex match object
        context_lines: Number of context lines

    Returns:
        Snippet string with ellipsis if truncated
    """
    lines = content.split("\n")

    # Find which line contains the match
    char_pos = match.start()
    current_pos = 0
    match_line_idx = 0

    for i, line in enumerate(lines):
        line_end = current_pos + len(line) + 1  # +1 for newline
        if current_pos <= char_pos < line_end:
            match_line_idx = i
            break
        current_pos = line_end

    # Get context lines
    start_idx = max(0, match_line_idx - context_lines)
    end_idx = min(len(lines), match_line_idx + context_lines + 1)

    snippet_lines = lines[start_idx:end_idx]

    # Clean up snippet lines (remove empty lines at edges, markdown headers)
    while snippet_lines and not snippet_lines[0].strip():
        snippet_lines.pop(0)
    while snippet_lines and not snippet_lines[-1].strip():
        snippet_lines.pop()

    snippet = "\n".join(snippet_lines)

    # Add ellipsis if truncated
    if start_idx > 0:
        snippet = "..." + snippet
    if end_idx < len(lines):
        snippet = snippet + "..."

    return snippet


def search_by_tags(
    tags: List[str],
    note_type: Optional[NoteType] = None,
    vault_path: Optional[Path] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Search for notes by tags.

    Args:
        tags: List of tags to search for (OR logic)
        note_type: Filter by note type (None for all)
        vault_path: Optional explicit vault path
        limit: Maximum number of results

    Returns:
        List of matching note dicts
    """
    if vault_path is None:
        vault_path = get_vault_path()

    results = []

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
            result = _check_tags(file_path, tags, note_type_value)
            if result is not None:
                results.append(result)

    # Sort by number of matching tags, then by modified time
    results.sort(key=lambda x: (x["matching_tags"], x["modified"]), reverse=True)

    if limit is not None:
        results = results[:limit]

    return results


def _check_tags(
    file_path: Path,
    search_tags: List[str],
    note_type: str,
) -> Optional[Dict[str, Any]]:
    """Check if a file has any of the specified tags.

    Args:
        file_path: Path to file
        search_tags: Tags to search for
        note_type: Note type string

    Returns:
        Note info dict with matching_tags count, or None if no matches
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return None

    lines = content.split("\n")

    # Extract title
    title = file_path.stem
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Extract tags from content
    note_tags = []
    for line in lines:
        if line.startswith("tags:"):
            tag_str = line[5:].strip()
            note_tags = [t.strip().lstrip("#").lower() for t in tag_str.split() if t.strip()]
            break

    # Check for matches (case-insensitive)
    search_tags_lower = [t.lower() for t in search_tags]
    matching = [t for t in note_tags if t in search_tags_lower]

    if not matching:
        return None

    # Get modification time
    from datetime import datetime

    stat = file_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime)

    return {
        "path": str(file_path),
        "name": file_path.stem,
        "type": note_type,
        "title": title,
        "tags": note_tags,
        "matching_tags": len(matching),
        "modified": modified,
    }


def get_all_tags(
    vault_path: Optional[Path] = None,
) -> Dict[str, int]:
    """Get all tags used in the vault with counts.

    Args:
        vault_path: Optional explicit vault path

    Returns:
        Dict mapping tag names to usage counts
    """
    if vault_path is None:
        vault_path = get_vault_path()

    tag_counts: Dict[str, int] = {}

    for nt in NoteType:
        dir_path = vault_path / nt.value
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError:
                continue

            for line in content.split("\n"):
                if line.startswith("tags:"):
                    tag_str = line[5:].strip()
                    tags = [t.strip().lstrip("#").lower() for t in tag_str.split() if t.strip()]
                    for tag in tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                    break

    return tag_counts
