#!/usr/bin/env python3
"""Validate workspace context before spawning subagents.

Prevents agents from working on hallucinated/non-existent code structures by
validating file paths and module references in the agent prompt.

Hook event: PreToolUse (matcher: Task)

Environment variables:
- CLAUDE_TOOL_INPUT: JSON input to the Task tool
- CLAUDE_WORKING_DIRECTORY: Current working directory
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from glob import glob
from pathlib import Path
from typing import NamedTuple


HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")

# Threshold: if more than this ratio of paths don't exist, block execution
INVALID_PATH_THRESHOLD = 0.5

# Minimum paths needed before validation kicks in (avoid false positives on simple prompts)
MIN_PATHS_FOR_VALIDATION = 3

# Patterns to extract file paths from prompts
PATH_PATTERNS = [
    # Absolute paths
    re.compile(r"(/(?:Users|home|var|tmp|etc|opt)[^\s\"\'\)\]\}:,]+)"),
    # Relative paths with file extensions
    re.compile(r"(?:^|[\s\"\'\(\[\{:,])([a-zA-Z0-9_\-./]+\.(?:rs|ts|tsx|js|jsx|py|go|java|json|yaml|yml|toml|md))(?:[\s\"\'\)\]\}:,]|$)"),
    # src/ or apps/ or packages/ relative paths
    re.compile(r"(?:^|[\s\"\'\(\[\{:,])((?:src|apps|packages|libs|tests|test)/[a-zA-Z0-9_\-./]+)(?:[\s\"\'\)\]\}:,]|$)"),
    # Rust module references (e.g., synapse_pingora::module::submodule)
    re.compile(r"([a-z_][a-z0-9_]*(?:::[a-z_][a-z0-9_]*)+)"),
]

# Known project root markers
PROJECT_MARKERS = {
    "package.json",
    "Cargo.toml",
    "pyproject.toml",
    "go.mod",
    "build.gradle",
    "pom.xml",
    "nx.json",
}


class ValidationResult(NamedTuple):
    """Result of workspace validation."""
    valid: bool
    total_paths: int
    missing_paths: list[str]
    message: str


def _hook_log_path() -> Path:
    for name in HOOK_LOG_ENV:
        value = os.getenv(name, "").strip()
        if value:
            return Path(value).expanduser()
    return Path.home() / ".claude" / "logs" / "hooks.log"


def _log_hook(message: str) -> None:
    try:
        path = _hook_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} [{Path(__file__).name}] {message}\n")
    except Exception:
        return


def _extract_paths(text: str) -> set[str]:
    """Extract file paths and module references from text."""
    paths: set[str] = set()

    for pattern in PATH_PATTERNS:
        for match in pattern.finditer(text):
            path = match.group(1).strip()
            # Clean up trailing punctuation that might have slipped through
            path = path.rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)

    return paths


def _rust_module_to_paths(module: str, cwd: Path) -> list[Path]:
    """Convert Rust module reference to possible file paths.

    e.g., synapse_pingora::actor::manager ->
        - apps/synapse-pingora/src/actor/manager.rs
        - apps/synapse-pingora/src/actor/manager/mod.rs
    """
    parts = module.split("::")
    if len(parts) < 2:
        return []

    # Convert crate name (snake_case) to directory name (kebab-case)
    crate_name = parts[0].replace("_", "-")
    module_path = "/".join(parts[1:])

    candidates = []

    # Look in common Rust project locations
    for prefix in ["apps", "crates", "src", "."]:
        base = cwd / prefix / crate_name / "src" / module_path
        candidates.append(base.with_suffix(".rs"))
        candidates.append(base / "mod.rs")

        # Also try without the crate name directory
        base2 = cwd / prefix / "src" / module_path
        candidates.append(base2.with_suffix(".rs"))
        candidates.append(base2 / "mod.rs")

    return candidates


def _path_exists(path_str: str, cwd: Path) -> bool:
    """Check if a path exists, handling various formats."""
    # Handle Rust module references
    if "::" in path_str:
        candidates = _rust_module_to_paths(path_str, cwd)
        return any(c.exists() for c in candidates)

    path = Path(path_str)

    # If absolute path, check directly
    if path.is_absolute():
        return path.exists()

    # Check relative to cwd
    full_path = cwd / path
    if full_path.exists():
        return True

    # Check with glob for patterns
    if "*" in path_str:
        matches = glob(str(cwd / path_str), recursive=True)
        return len(matches) > 0

    return False


def validate_workspace(prompt: str, cwd: str) -> ValidationResult:
    """Validate that paths mentioned in prompt exist in workspace."""
    cwd_path = Path(cwd)

    # Extract all paths from the prompt
    paths = _extract_paths(prompt)

    if len(paths) < MIN_PATHS_FOR_VALIDATION:
        return ValidationResult(
            valid=True,
            total_paths=len(paths),
            missing_paths=[],
            message="Insufficient paths for validation"
        )

    # Check which paths exist
    missing: list[str] = []
    for path in paths:
        if not _path_exists(path, cwd_path):
            missing.append(path)

    # Calculate ratio
    ratio = len(missing) / len(paths) if paths else 0
    valid = ratio < INVALID_PATH_THRESHOLD

    if valid:
        message = f"Workspace validated: {len(paths) - len(missing)}/{len(paths)} paths exist"
    else:
        message = f"Too many invalid paths: {len(missing)}/{len(paths)} ({ratio:.0%}) don't exist"

    return ValidationResult(
        valid=valid,
        total_paths=len(paths),
        missing_paths=missing,
        message=message
    )


def main() -> int:
    # Get tool input from environment
    tool_input_raw = os.getenv("CLAUDE_TOOL_INPUT", "")
    tool_name = os.getenv("CLAUDE_TOOL_NAME", "")
    cwd = os.getenv("CLAUDE_WORKING_DIRECTORY", os.getcwd())

    # Only validate Task tool
    if tool_name != "Task":
        return 0

    if not tool_input_raw:
        _log_hook("No tool input provided, skipping validation")
        return 0

    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError as e:
        _log_hook(f"Failed to parse tool input: {e}")
        return 0

    # Extract the prompt from Task tool input
    prompt = tool_input.get("prompt", "")
    if not prompt:
        _log_hook("No prompt in Task tool input")
        return 0

    # Also include description for validation
    description = tool_input.get("description", "")
    full_text = f"{description}\n{prompt}"

    # Validate workspace
    result = validate_workspace(full_text, cwd)

    _log_hook(f"{result.message} | missing: {result.missing_paths[:5]}")

    if not result.valid:
        print(f"[workspace_validator] {result.message}", file=sys.stderr)
        print("Missing paths:", file=sys.stderr)
        for path in result.missing_paths[:10]:
            print(f"  - {path}", file=sys.stderr)
        if len(result.missing_paths) > 10:
            print(f"  ... and {len(result.missing_paths) - 10} more", file=sys.stderr)
        print("\nThe agent prompt references too many non-existent paths.", file=sys.stderr)
        print("This may indicate hallucinated code structures.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
