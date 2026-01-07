"""Tests for token_counter module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_ctx_py.token_counter import (
    TokenStats,
    estimate_tokens,
    count_file_tokens,
    count_category_tokens,
    format_token_summary,
    TOKEN_MULTIPLIER,
)


class TestTokenStats:
    """Tests for TokenStats dataclass."""

    def test_create_token_stats(self):
        """Test creating TokenStats instance."""
        stats = TokenStats(files=5, chars=1000, words=200, tokens=260)
        assert stats.files == 5
        assert stats.chars == 1000
        assert stats.words == 200
        assert stats.tokens == 260

    def test_tokens_formatted_small(self):
        """Test formatting small token counts."""
        stats = TokenStats(files=1, chars=100, words=20, tokens=26)
        assert stats.tokens_formatted == "26"

    def test_tokens_formatted_thousands(self):
        """Test formatting token counts over 1000."""
        stats = TokenStats(files=10, chars=10000, words=2000, tokens=2600)
        assert stats.tokens_formatted == "2.6K"

    def test_tokens_formatted_exact_thousand(self):
        """Test formatting exactly 1000 tokens."""
        stats = TokenStats(files=5, chars=5000, words=769, tokens=1000)
        assert stats.tokens_formatted == "1.0K"

    def test_add_token_stats(self):
        """Test adding two TokenStats together."""
        stats1 = TokenStats(files=2, chars=500, words=100, tokens=130)
        stats2 = TokenStats(files=3, chars=300, words=60, tokens=78)

        result = stats1 + stats2

        assert result.files == 5
        assert result.chars == 800
        assert result.words == 160
        assert result.tokens == 208

    def test_add_empty_stats(self):
        """Test adding empty TokenStats."""
        stats1 = TokenStats(files=2, chars=500, words=100, tokens=130)
        empty = TokenStats(files=0, chars=0, words=0, tokens=0)

        result = stats1 + empty

        assert result.files == 2
        assert result.chars == 500


class TestEstimateTokens:
    """Tests for estimate_tokens function."""

    def test_estimate_empty_string(self):
        """Test estimating tokens for empty string."""
        assert estimate_tokens("") == 0

    def test_estimate_single_word(self):
        """Test estimating tokens for single word."""
        result = estimate_tokens("hello")
        expected = int(1 * TOKEN_MULTIPLIER)
        assert result == expected

    def test_estimate_multiple_words(self):
        """Test estimating tokens for multiple words."""
        result = estimate_tokens("hello world how are you")
        expected = int(5 * TOKEN_MULTIPLIER)
        assert result == expected

    def test_estimate_long_text(self):
        """Test estimating tokens for longer text."""
        text = " ".join(["word"] * 100)
        result = estimate_tokens(text)
        expected = int(100 * TOKEN_MULTIPLIER)
        assert result == expected

    def test_estimate_with_newlines(self):
        """Test that newlines are handled correctly."""
        text = "hello\nworld\nhow\nare\nyou"
        result = estimate_tokens(text)
        expected = int(5 * TOKEN_MULTIPLIER)
        assert result == expected

    def test_estimate_with_multiple_spaces(self):
        """Test text with multiple spaces."""
        text = "hello   world"
        result = estimate_tokens(text)
        # split() handles multiple spaces
        expected = int(2 * TOKEN_MULTIPLIER)
        assert result == expected


class TestCountFileTokens:
    """Tests for count_file_tokens function."""

    def test_count_existing_file(self, tmp_path: Path):
        """Test counting tokens in an existing file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("hello world how are you")

        stats = count_file_tokens(test_file)

        assert stats.files == 1
        assert stats.chars == 23
        assert stats.words == 5
        assert stats.tokens == int(5 * TOKEN_MULTIPLIER)

    def test_count_nonexistent_file(self, tmp_path: Path):
        """Test counting tokens in non-existent file returns zeros."""
        missing_file = tmp_path / "missing.md"

        stats = count_file_tokens(missing_file)

        assert stats.files == 0
        assert stats.chars == 0
        assert stats.words == 0
        assert stats.tokens == 0

    def test_count_empty_file(self, tmp_path: Path):
        """Test counting tokens in empty file."""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("")

        stats = count_file_tokens(empty_file)

        assert stats.files == 1
        assert stats.chars == 0
        assert stats.words == 0
        assert stats.tokens == 0

    def test_count_file_with_unicode(self, tmp_path: Path):
        """Test counting tokens in file with unicode content."""
        unicode_file = tmp_path / "unicode.md"
        unicode_file.write_text("héllo wörld 你好 мир")

        stats = count_file_tokens(unicode_file)

        assert stats.files == 1
        assert stats.words == 4


class TestCountCategoryTokens:
    """Tests for count_category_tokens function."""

    def test_count_empty_category(self):
        """Test counting tokens for empty category."""
        stats = count_category_tokens({})

        assert stats.files == 0
        assert stats.tokens == 0

    def test_count_single_file_category(self, tmp_path: Path):
        """Test counting tokens for category with one file."""
        test_file = tmp_path / "test.md"
        test_file.write_text("hello world")

        files = {"test": test_file}
        stats = count_category_tokens(files)

        assert stats.files == 1
        assert stats.words == 2

    def test_count_multiple_files_category(self, tmp_path: Path):
        """Test counting tokens for category with multiple files."""
        file1 = tmp_path / "file1.md"
        file1.write_text("hello world")
        file2 = tmp_path / "file2.md"
        file2.write_text("foo bar baz")

        files = {"file1": file1, "file2": file2}
        stats = count_category_tokens(files)

        assert stats.files == 2
        assert stats.words == 5

    def test_count_mixed_existing_missing(self, tmp_path: Path):
        """Test counting tokens with mix of existing and missing files."""
        existing = tmp_path / "existing.md"
        existing.write_text("hello world")
        missing = tmp_path / "missing.md"

        files = {"existing": existing, "missing": missing}
        stats = count_category_tokens(files)

        assert stats.files == 1  # Only existing file counted
        assert stats.words == 2


class TestFormatTokenSummary:
    """Tests for format_token_summary function."""

    def test_format_compact_summary(self):
        """Test compact format summary."""
        category_stats = {}
        total_stats = TokenStats(files=5, chars=1000, words=200, tokens=260)

        result = format_token_summary(category_stats, total_stats, compact=True)

        assert "260 tokens" in result
        assert "5 files" in result

    def test_format_compact_with_thousands(self):
        """Test compact format with thousands of tokens."""
        category_stats = {}
        total_stats = TokenStats(files=10, chars=50000, words=10000, tokens=13000)

        result = format_token_summary(category_stats, total_stats, compact=True)

        assert "13.0K tokens" in result

    def test_format_detailed_summary(self):
        """Test detailed format summary."""
        category_stats = {
            "core": TokenStats(files=3, chars=500, words=100, tokens=130),
            "rules": TokenStats(files=2, chars=300, words=60, tokens=78),
        }
        total_stats = TokenStats(files=5, chars=800, words=160, tokens=208)

        result = format_token_summary(category_stats, total_stats, compact=False)

        assert "Total:" in result
        assert "208 tokens" in result
        assert "Core:" in result
        assert "Rules:" in result

    def test_format_detailed_empty_categories(self):
        """Test detailed format with empty categories."""
        category_stats = {
            "core": TokenStats(files=0, chars=0, words=0, tokens=0),
        }
        total_stats = TokenStats(files=0, chars=0, words=0, tokens=0)

        result = format_token_summary(category_stats, total_stats, compact=False)

        assert "Total:" in result
        # Empty categories should not appear
        assert "Core:" not in result

    def test_format_detailed_all_categories(self):
        """Test detailed format with all known categories."""
        category_stats = {
            "core": TokenStats(files=1, chars=100, words=20, tokens=26),
            "rules": TokenStats(files=2, chars=200, words=40, tokens=52),
            "modes": TokenStats(files=3, chars=300, words=60, tokens=78),
            "agents": TokenStats(files=4, chars=400, words=80, tokens=104),
            "mcp_docs": TokenStats(files=1, chars=100, words=20, tokens=26),
            "skills": TokenStats(files=5, chars=500, words=100, tokens=130),
        }
        total_stats = TokenStats(files=16, chars=1600, words=320, tokens=416)

        result = format_token_summary(category_stats, total_stats, compact=False)

        assert "Core:" in result
        assert "Rules:" in result
        assert "Modes:" in result
        assert "Agents:" in result
        assert "MCP:" in result
        assert "Skills:" in result


class TestTokenMultiplier:
    """Tests for TOKEN_MULTIPLIER constant."""

    def test_multiplier_value(self):
        """Test that TOKEN_MULTIPLIER is reasonable."""
        # Claude tokenizer typically yields ~1.3 tokens per word
        assert 1.0 < TOKEN_MULTIPLIER < 2.0
        assert TOKEN_MULTIPLIER == 1.3
