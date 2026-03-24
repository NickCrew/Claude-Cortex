"""Commit message validation and atomicity detection.

All functions return lists of warning strings.  An empty list means
no issues detected.  These are **advisory only** — they never block.
"""

from __future__ import annotations

import re
from typing import Dict, FrozenSet, List

_CONVENTIONAL_COMMIT_RE = re.compile(r"^([a-z]+)(\([a-z0-9_/-]+\))?!?: .+")

_KNOWN_TYPES: FrozenSet[str] = frozenset(
    {
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
    }
)

_SUBJECT_MAX_LENGTH = 72

_FILE_THRESHOLDS: Dict[str, int] = {
    "fix": 6,
    "feat": 10,
    "docs": 15,
    "refactor": 20,
    "style": 20,
    "test": 15,
    "chore": 15,
    "build": 10,
    "ci": 10,
    "perf": 10,
}

_DEFAULT_FILE_THRESHOLD = 10

_MULTI_CHANGE_RE = re.compile(r"\b(and|also|plus)\b", re.IGNORECASE)


def validate_commit_message(msg: str) -> List[str]:
    """Validate *msg* against Conventional Commits format.

    Returns a list of warning strings (empty = all good).
    """
    warnings: List[str] = []
    subject = msg.split("\n", 1)[0].strip()

    if not subject:
        warnings.append("Commit message is empty")
        return warnings

    match = _CONVENTIONAL_COMMIT_RE.match(subject)
    if not match:
        warnings.append(
            "Message doesn't match conventional format: type(scope): summary"
        )
        return warnings

    commit_type = match.group(1)
    if commit_type not in _KNOWN_TYPES:
        warnings.append(f"Unknown commit type: {commit_type}")

    if len(subject) > _SUBJECT_MAX_LENGTH:
        warnings.append(
            f"Subject line is {len(subject)} chars (recommended max {_SUBJECT_MAX_LENGTH})"
        )

    return warnings


def _extract_type(msg: str) -> str:
    """Extract the commit type from the subject line, or return empty string."""
    subject = msg.split("\n", 1)[0].strip()
    match = _CONVENTIONAL_COMMIT_RE.match(subject)
    if not match:
        return ""
    return match.group(1)


def check_atomicity(msg: str, files: List[str]) -> List[str]:
    """Check whether a commit appears to bundle multiple logical changes.

    Returns a list of warning strings (empty = looks atomic).
    """
    warnings: List[str] = []

    # --- Message body check: look for conjunctions suggesting multiple changes ---
    subject = msg.split("\n", 1)[0]
    # Check the subject line after the type prefix for multi-change words
    # e.g. "fix: auth and update styles" -> "auth and update styles"
    colon_pos = subject.find(": ")
    if colon_pos >= 0:
        body_after_type = subject[colon_pos + 2 :]
    else:
        body_after_type = subject

    multi_match = _MULTI_CHANGE_RE.search(body_after_type)
    if multi_match:
        warnings.append(
            f"Message contains '{multi_match.group()}' — consider splitting into separate commits"
        )

    # --- File count vs type threshold ---
    commit_type = _extract_type(msg)
    threshold = _FILE_THRESHOLDS.get(commit_type, _DEFAULT_FILE_THRESHOLD)
    if len(files) > threshold:
        warnings.append(
            f"{len(files)} files exceeds typical threshold for "
            f"'{commit_type or 'unknown'}' commits ({threshold})"
        )

    # --- Directory cluster check ---
    top_dirs = set()
    for f in files:
        parts = f.replace("\\", "/").split("/")
        top_dirs.add(parts[0] if len(parts) > 1 else ".")
    if len(top_dirs) >= 3:
        sorted_dirs = sorted(top_dirs)
        warnings.append(
            f"Changes span {len(top_dirs)} top-level directories: "
            + ", ".join(sorted_dirs)
        )

    return warnings
