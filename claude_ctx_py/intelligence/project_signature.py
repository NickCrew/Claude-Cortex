"""Project signature detection for filtering skills by domain relevance.

Walks a project directory once and produces a frozen `ProjectSignature`
describing the file extensions present, well-known tooling marker files,
and directory names discovered. Used as a pre-filter for skill
recommendations: a skill whose `file_patterns` cannot plausibly intersect
the signature is dropped before ranking strategies run.

The strategy is deliberately conservative — patterns that cannot be
classified default to ``True`` (include). This filter exists to remove
*obviously irrelevant* skills (e.g., Terraform skills in a frontend-only
project), not to make subtle ranking calls.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import FrozenSet, Iterable, Iterator, List, Set, Tuple

_IGNORED_DIRS: FrozenSet[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        "dist",
        "build",
        "target",
        ".next",
        ".nuxt",
        ".cache",
        ".idea",
        ".vscode",
        "htmlcov",
        "coverage",
    }
)


_TOOLING_MARKERS: FrozenSet[str] = frozenset(
    {
        # Python
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "requirements.txt",
        "Pipfile",
        "poetry.lock",
        "uv.lock",
        # JS / TS
        "package.json",
        "tsconfig.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        # Rust
        "Cargo.toml",
        "Cargo.lock",
        # Go
        "go.mod",
        "go.sum",
        # JVM
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        # Containers
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        # CI / build
        ".github",
        "Makefile",
        "justfile",
        "Justfile",
        # IaC
        "main.tf",
        "terraform.tf",
    }
)


_MAX_FILES_SCANNED = 5000


_EXT_FROM_PATTERN = re.compile(r"\*\.([a-zA-Z0-9]+)$")


@dataclass(frozen=True)
class ProjectSignature:
    """Frozen filesystem-level signature of a project.

    Attributes:
        cwd: Resolved root directory the signature was computed from.
        file_extensions: Lowercase suffixes (with leading dot) seen during
            the walk, e.g. ``{".py", ".tsx"}``.
        tooling_markers: Names from ``_TOOLING_MARKERS`` discovered during
            the walk, e.g. ``{"pyproject.toml", "Dockerfile"}``.
        directories: Basenames of every directory walked (excluding ignored
            directories). Used to match patterns like ``**/api/**``.
    """

    cwd: Path
    file_extensions: FrozenSet[str]
    tooling_markers: FrozenSet[str]
    directories: FrozenSet[str]

    def matches_pattern(self, pattern: str) -> bool:
        """Return ``True`` if the project plausibly contains ``pattern`` matches.

        The classification ladder:

        1. Patterns ending in ``*.<ext>`` are checked against
           ``file_extensions`` — exact intersection.
        2. Patterns with no glob characters and no path separator are
           checked against ``tooling_markers`` (literal filename markers).
        3. Patterns containing ``/<dirname>/`` segments are checked against
           ``directories`` and ``tooling_markers``.
        4. Anything that doesn't classify returns ``True`` — better to
           over-include than silently drop a skill the user might need.
        """
        ext_match = _EXT_FROM_PATTERN.search(pattern)
        if ext_match is not None:
            return f".{ext_match.group(1).lower()}" in self.file_extensions

        if "*" not in pattern and "?" not in pattern and "/" not in pattern:
            return pattern in self.tooling_markers

        for component in pattern.split("/"):
            if not component or component in {"*", "**"} or "*" in component:
                continue
            if component in self.directories:
                return True
            if component in self.tooling_markers:
                return True

        return True

    def matches_any(self, patterns: Iterable[str]) -> bool:
        """Return ``True`` if at least one pattern intersects the signature.

        An empty pattern list returns ``True``: a skill without explicit
        file-pattern signals carries no negative evidence and shouldn't be
        filtered out on this basis alone.
        """
        patterns_list: List[str] = list(patterns)
        if not patterns_list:
            return True
        return any(self.matches_pattern(p) for p in patterns_list)


def compute_project_signature(
    cwd: Path | None = None,
    *,
    max_files: int = _MAX_FILES_SCANNED,
) -> ProjectSignature:
    """Walk ``cwd`` and produce a ``ProjectSignature``.

    Skips well-known noisy directories (``.git``, ``node_modules``, etc.)
    and stops after ``max_files`` to bound cost on large repos.
    """
    root = (cwd or Path.cwd()).resolve()
    if not root.exists() or not root.is_dir():
        return ProjectSignature(
            cwd=root,
            file_extensions=frozenset(),
            tooling_markers=frozenset(),
            directories=frozenset(),
        )

    extensions: Set[str] = set()
    tooling: Set[str] = set()
    directories: Set[str] = set()

    files_seen = 0
    for dirpath, dirnames, filenames in _walk_filtered(root):
        directories.add(dirpath.name)
        if dirpath.name in _TOOLING_MARKERS:
            tooling.add(dirpath.name)
        for filename in filenames:
            files_seen += 1
            suffix = Path(filename).suffix.lower()
            if suffix:
                extensions.add(suffix)
            if filename in _TOOLING_MARKERS:
                tooling.add(filename)
            if files_seen >= max_files:
                break
        # Surface child-directory tooling markers (e.g., a nested ``.github``).
        for dirname in dirnames:
            if dirname in _TOOLING_MARKERS:
                tooling.add(dirname)
        if files_seen >= max_files:
            break

    return ProjectSignature(
        cwd=root,
        file_extensions=frozenset(extensions),
        tooling_markers=frozenset(tooling),
        directories=frozenset(directories),
    )


def _walk_filtered(
    root: Path,
) -> Iterator[Tuple[Path, List[str], List[str]]]:
    """``os.walk``-equivalent that prunes ignored directories in place."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _IGNORED_DIRS]
        yield Path(dirpath), dirnames, filenames
