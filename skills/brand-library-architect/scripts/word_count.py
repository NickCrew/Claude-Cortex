#!/usr/bin/env python3
"""Verify word counts in brand/FAQ.md and brand/BIOS.md.

Usage:
    python3 scripts/word_count.py path/to/FAQ.md
    python3 scripts/word_count.py path/to/BIOS.md

For FAQ: each ## section is treated as one Q&A. Answer body must be 50-150 words.
For BIOS: each ### section under "## Founder" or "## Company" is treated as a
bio variant. Word count must match the heading's word count target (50/100/250)
within ±5 words.
"""

import re
import sys
from pathlib import Path


def count_words_in_blockquote(text: str) -> int:
    """Count words in a blockquote-prefixed prose block."""
    # Match consecutive blockquote lines (including bare ">" separators)
    bq_match = re.search(r"((?:^>.*\n?)+)", text, re.MULTILINE)
    if not bq_match:
        return 0
    bq = bq_match.group(1)
    # Strip "> " or just ">" prefix
    body = re.sub(r"^>\s?", "", bq, flags=re.MULTILINE)
    # Collapse whitespace
    body = " ".join(body.split())
    return len(body.split())


def count_chars_in_blockquote(text: str) -> int:
    """Count chars in a blockquote-prefixed block (for social bios)."""
    bq_match = re.search(r"((?:^>.*\n?)+)", text, re.MULTILINE)
    if not bq_match:
        return 0
    bq = bq_match.group(1)
    body = re.sub(r"^>\s?", "", bq, flags=re.MULTILINE)
    body = " ".join(body.split())
    return len(body)


def check_faq(path: Path) -> int:
    """Verify each ## answer is 50-150 words. Returns 0 on success, 1 on failure."""
    content = path.read_text()
    parts = re.split(r"^## ", content, flags=re.MULTILINE)
    failures = 0

    for part in parts[1:]:
        lines = part.split("\n", 1)
        question = lines[0].strip()
        # Skip non-question sections (intro headings, "Notes for use", etc.)
        if not (question.endswith("?") or question.lower().startswith(
            ("what", "is", "how", "why", "can", "does", "are", "do")
        )):
            continue
        body = lines[1] if len(lines) > 1 else ""
        word_count = count_words_in_blockquote(body)
        # Some FAQ answers are direct prose without blockquote — fall back to
        # counting the body text directly
        if word_count == 0:
            text = " ".join(body.split())
            # Strip until first heading or end-of-body
            text = re.split(r"^##|^###", text, maxsplit=1, flags=re.MULTILINE)[0]
            word_count = len(text.split())

        status = "✓" if 50 <= word_count <= 150 else "✗"
        if status == "✗":
            failures += 1
        print(f"{status} {word_count:>3} words  {question}")

    return 1 if failures else 0


def check_bios(path: Path) -> int:
    """Verify founder/company bios match 50/100/250 ±5 word targets, and social
    bios fit char caps. Returns 0 on success, 1 on failure."""
    content = path.read_text()
    failures = 0

    # Founder/company word-count sections (### sections under ## Founder / ## Company)
    for match in re.finditer(r"^### (Founder bio|Company boilerplate) — (\d+) words", content, re.MULTILINE):
        section_label = match.group(0)
        target = int(match.group(2))
        # Find the blockquote following this heading
        rest = content[match.end():]
        word_count = count_words_in_blockquote(rest)
        diff = abs(word_count - target)
        status = "✓" if diff <= 5 else "✗"
        if status == "✗":
            failures += 1
        print(f"{status} {word_count:>3}/{target:>3} words  {section_label}")

    # Social profile char caps
    char_caps = {
        "Twitter": 160,
        "LinkedIn company tagline": 120,
        "GitHub bio": 160,
        "BlueSky": 256,
    }
    for label, cap in char_caps.items():
        # Match "### Twitter (≤160 chars)" or similar
        match = re.search(rf"^### {re.escape(label)}\b.*\n", content, re.MULTILINE)
        if not match:
            continue
        rest = content[match.end():]
        char_count = count_chars_in_blockquote(rest)
        status = "✓" if char_count <= cap else "✗"
        if status == "✗":
            failures += 1
        print(f"{status} {char_count:>3}/≤{cap}  {label}")

    return 1 if failures else 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: word_count.py <path-to-FAQ.md-or-BIOS.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2

    name = path.name.lower()
    if "faq" in name:
        return check_faq(path)
    elif "bios" in name or "bio" in name:
        return check_bios(path)
    else:
        print(f"Unknown doc type for {path.name} — expected FAQ.md or BIOS.md", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
