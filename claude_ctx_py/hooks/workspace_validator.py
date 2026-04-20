"""Validate workspace paths before spawning a subagent.

Exposed to the harness as ``cortex hooks workspace-validator``. Registered
in ``~/.claude/settings.json`` via
``cortex hooks install workspace-validator``.

Hook event: PreToolUse (matcher: Task).

Fails (exit 1) when too many paths referenced in the Task prompt do not
exist in the workspace, heuristically flagging hallucinated module or file
references before the subagent runs.

Environment variables:
- ``CLAUDE_TOOL_INPUT``: JSON envelope for the Task tool invocation.
- ``CLAUDE_TOOL_NAME``: only validates when this equals ``"Task"``.
- ``CLAUDE_WORKING_DIRECTORY``: cwd against which relative paths resolve
  (defaults to ``os.getcwd()``).
"""

from __future__ import annotations

import json
import os
import re
import sys
from glob import glob
from pathlib import Path
from typing import List, NamedTuple, Set

from .skill_suggest import _log_hook


INVALID_PATH_THRESHOLD = 0.5
MIN_PATHS_FOR_VALIDATION = 3

PATH_PATTERNS = [
    re.compile(r"(/(?:Users|home|var|tmp|etc|opt)[^\s\"\'\)\]\}:,]+)"),
    re.compile(
        r"(?:^|[\s\"\'\(\[\{:,])"
        r"([a-zA-Z0-9_\-./]+\.(?:rs|ts|tsx|js|jsx|py|go|java|json|yaml|yml|toml|md))"
        r"(?:[\s\"\'\)\]\}:,]|$)"
    ),
    re.compile(
        r"(?:^|[\s\"\'\(\[\{:,])"
        r"((?:src|apps|packages|libs|tests|test)/[a-zA-Z0-9_\-./]+)"
        r"(?:[\s\"\'\)\]\}:,]|$)"
    ),
    re.compile(r"([a-z_][a-z0-9_]*(?:::[a-z_][a-z0-9_]*)+)"),
]


class ValidationResult(NamedTuple):
    valid: bool
    total_paths: int
    missing_paths: List[str]
    message: str


def _extract_paths(text: str) -> Set[str]:
    paths: Set[str] = set()
    for pattern in PATH_PATTERNS:
        for match in pattern.finditer(text):
            path = match.group(1).strip().rstrip(".,;:!?")
            if path and len(path) > 2:
                paths.add(path)
    return paths


def _rust_module_to_paths(module: str, cwd: Path) -> List[Path]:
    """Convert a ``crate::mod::sub`` reference to candidate ``.rs`` paths."""
    parts = module.split("::")
    if len(parts) < 2:
        return []

    crate_name = parts[0].replace("_", "-")
    module_path = "/".join(parts[1:])
    candidates: List[Path] = []

    for prefix in ["apps", "crates", "src", "."]:
        base = cwd / prefix / crate_name / "src" / module_path
        candidates.append(base.with_suffix(".rs"))
        candidates.append(base / "mod.rs")

        base2 = cwd / prefix / "src" / module_path
        candidates.append(base2.with_suffix(".rs"))
        candidates.append(base2 / "mod.rs")

    return candidates


def _path_exists(path_str: str, cwd: Path) -> bool:
    if "::" in path_str:
        return any(c.exists() for c in _rust_module_to_paths(path_str, cwd))

    path = Path(path_str)
    if path.is_absolute():
        return path.exists()
    if (cwd / path).exists():
        return True
    if "*" in path_str:
        return bool(glob(str(cwd / path_str), recursive=True))
    return False


def validate_workspace(prompt: str, cwd: str) -> ValidationResult:
    cwd_path = Path(cwd)
    paths = _extract_paths(prompt)

    if len(paths) < MIN_PATHS_FOR_VALIDATION:
        return ValidationResult(
            valid=True,
            total_paths=len(paths),
            missing_paths=[],
            message="Insufficient paths for validation",
        )

    missing = [p for p in paths if not _path_exists(p, cwd_path)]
    ratio = len(missing) / len(paths) if paths else 0
    valid = ratio < INVALID_PATH_THRESHOLD

    if valid:
        message = (
            f"Workspace validated: {len(paths) - len(missing)}/{len(paths)} "
            "paths exist"
        )
    else:
        message = (
            f"Too many invalid paths: {len(missing)}/{len(paths)} "
            f"({ratio:.0%}) don't exist"
        )

    return ValidationResult(
        valid=valid,
        total_paths=len(paths),
        missing_paths=missing,
        message=message,
    )


def main() -> int:
    tool_input_raw = os.getenv("CLAUDE_TOOL_INPUT", "")
    tool_name = os.getenv("CLAUDE_TOOL_NAME", "")
    cwd = os.getenv("CLAUDE_WORKING_DIRECTORY", os.getcwd())

    if tool_name != "Task":
        return 0

    if not tool_input_raw:
        _log_hook("workspace-validator: no tool input provided, skipping")
        return 0

    try:
        tool_input = json.loads(tool_input_raw)
    except json.JSONDecodeError as exc:
        _log_hook(f"workspace-validator: failed to parse tool input: {exc}")
        return 0

    prompt = tool_input.get("prompt", "")
    if not prompt:
        _log_hook("workspace-validator: no prompt in Task tool input")
        return 0

    description = tool_input.get("description", "")
    result = validate_workspace(f"{description}\n{prompt}", cwd)

    _log_hook(
        f"workspace-validator: {result.message} | "
        f"missing: {result.missing_paths[:5]}"
    )

    if not result.valid:
        print(f"[workspace-validator] {result.message}", file=sys.stderr)
        print("Missing paths:", file=sys.stderr)
        for path in result.missing_paths[:10]:
            print(f"  - {path}", file=sys.stderr)
        if len(result.missing_paths) > 10:
            print(
                f"  ... and {len(result.missing_paths) - 10} more",
                file=sys.stderr,
            )
        print(
            "\nThe agent prompt references too many non-existent paths.",
            file=sys.stderr,
        )
        print(
            "This may indicate hallucinated code structures.",
            file=sys.stderr,
        )
        return 1

    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:
        try:
            _log_hook(f"workspace-validator unhandled error: {exc}")
        except Exception:
            pass
        raise
