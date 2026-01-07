"""Token counting utilities for cortex.

This module provides token estimation for markdown files to help users
understand their context window usage.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

from .core.context_export import collect_context_components


# Token estimation multiplier (words to tokens)
# Claude tokenizer typically yields ~1.3 tokens per word for English text
TOKEN_MULTIPLIER = 1.3


@dataclass
class TokenStats:
    """Token statistics for a category or file."""

    files: int
    chars: int
    words: int
    tokens: int

    @property
    def tokens_formatted(self) -> str:
        """Format token count with K suffix for readability."""
        if self.tokens >= 1000:
            return f"{self.tokens / 1000:.1f}K"
        return str(self.tokens)

    def __add__(self, other: "TokenStats") -> "TokenStats":
        """Add two TokenStats together."""
        return TokenStats(
            files=self.files + other.files,
            chars=self.chars + other.chars,
            words=self.words + other.words,
            tokens=self.tokens + other.tokens,
        )


def estimate_tokens(content: str) -> int:
    """Estimate token count for text content.

    Uses word count multiplied by ~1.3 as a reasonable approximation
    for Claude's tokenizer on English text.

    Args:
        content: Text content to estimate

    Returns:
        Estimated token count
    """
    word_count = len(content.split())
    return int(word_count * TOKEN_MULTIPLIER)


def count_file_tokens(file_path: Path) -> TokenStats:
    """Count tokens in a single file.

    Args:
        file_path: Path to the file

    Returns:
        TokenStats for the file
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        chars = len(content)
        words = len(content.split())
        tokens = int(words * TOKEN_MULTIPLIER)
        return TokenStats(files=1, chars=chars, words=words, tokens=tokens)
    except Exception:
        return TokenStats(files=0, chars=0, words=0, tokens=0)


def count_category_tokens(files: Dict[str, Path]) -> TokenStats:
    """Count tokens for all files in a category.

    Args:
        files: Dictionary mapping file keys to paths

    Returns:
        Aggregated TokenStats for the category
    """
    total = TokenStats(files=0, chars=0, words=0, tokens=0)
    for file_path in files.values():
        total = total + count_file_tokens(file_path)
    return total


def get_active_context_tokens(
    claude_dir: Optional[Path] = None,
) -> Tuple[Dict[str, TokenStats], TokenStats]:
    """Get token counts for all active context components.

    Args:
        claude_dir: Path to cortex directory (auto-detected if None)

    Returns:
        Tuple of (category_stats, total_stats)
        - category_stats: Dict mapping category name to TokenStats
        - total_stats: Aggregated TokenStats across all categories
    """
    components = collect_context_components(claude_dir)

    category_stats: Dict[str, TokenStats] = {}
    total = TokenStats(files=0, chars=0, words=0, tokens=0)

    for category, files in components.items():
        stats = count_category_tokens(files)
        category_stats[category] = stats
        total = total + stats

    return category_stats, total


def format_token_summary(
    category_stats: Dict[str, TokenStats],
    total_stats: TokenStats,
    compact: bool = False,
) -> str:
    """Format token statistics as a human-readable summary.

    Args:
        category_stats: Dict mapping category name to TokenStats
        total_stats: Total TokenStats across all categories
        compact: If True, return single-line format

    Returns:
        Formatted summary string
    """
    category_names = {
        "core": "Core",
        "rules": "Rules",
        "modes": "Modes",
        "agents": "Agents",
        "mcp_docs": "MCP",
        "skills": "Skills",
    }

    if compact:
        # Single line format for status bar
        return f"{total_stats.tokens_formatted} tokens ({total_stats.files} files)"

    # Detailed format
    lines = []
    lines.append(f"Total: {total_stats.tokens_formatted} tokens ({total_stats.files} files)")
    lines.append("")

    for category, name in category_names.items():
        stats = category_stats.get(category)
        if stats and stats.files > 0:
            lines.append(f"  {name}: {stats.tokens_formatted} ({stats.files} files)")

    return "\n".join(lines)


def get_token_breakdown_table() -> list[tuple[str, int, int, str]]:
    """Get token breakdown as table data.

    Returns:
        List of (category_name, file_count, token_count, formatted_tokens) tuples
    """
    category_stats, _ = get_active_context_tokens()

    category_names = {
        "core": "Core Framework",
        "rules": "Rules",
        "modes": "Modes",
        "agents": "Agents",
        "mcp_docs": "MCP Docs",
        "skills": "Skills",
    }

    rows = []
    for category, name in category_names.items():
        stats = category_stats.get(category)
        if stats and stats.files > 0:
            rows.append((name, stats.files, stats.tokens, stats.tokens_formatted))

    return rows
