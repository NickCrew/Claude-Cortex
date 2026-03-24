"""Whole-file atomic stage-and-commit.

Ports the safe commit workflow from ``bin/committer``:
unstage everything → stage listed files → validate → commit.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .run import run_git, resolve_repo_root
from .validate import check_atomicity, validate_commit_message

_LOCK_RE = re.compile(r"Unable to create ['\"]?(.+?index\.lock)['\"]?")


def _normalize_path(p: str) -> str:
    """Strip leading ``./`` for comparison with ``git diff --name-only``."""
    if p.startswith("./"):
        return p[2:]
    return p


def _emit_warnings(warnings: List[str]) -> None:
    for w in warnings:
        sys.stderr.write(f"Warning: {w}\n")


def _validate_inputs(
    message: str,
    files: List[str],
    cwd: Path,
) -> Optional[str]:
    """Return an error string if inputs are invalid, else ``None``."""
    if not message or not message.strip():
        return "Commit message must not be empty"

    if os.path.exists(os.path.join(str(cwd), message)):
        return (
            f'First argument looks like a file path ("{message}"); '
            "provide the commit message first"
        )

    if not files:
        return "At least one file is required"

    for f in files:
        if f == ".":
            return '"." is not allowed; list specific paths instead'
        if os.path.isdir(os.path.join(str(cwd), f)):
            return f'"{f}" is a directory; list specific files instead'

    return None


def _verify_files_exist(files: List[str], cwd: Path) -> Optional[str]:
    """Verify each file exists on disk, in the index, or in HEAD (deletions)."""
    for f in files:
        full = cwd / f
        if full.exists():
            continue
        # Allow staging deletions: check index then HEAD.
        code, _out, _err = run_git(["ls-files", "--error-unmatch", "--", f], cwd)
        if code == 0:
            continue
        code2, _out2, _err2 = run_git(["cat-file", "-e", f"HEAD:{f}"], cwd)
        if code2 == 0:
            continue
        return f"File not found: {f}"
    return None


def _unstage_all(cwd: Path) -> Optional[str]:
    """Reset the staging area.  Returns error string on failure, else ``None``."""
    code, _out, err = run_git(["restore", "--staged", ":/"], cwd)
    if code != 0:
        # Fresh repo with no HEAD — nothing to unstage, that's fine.
        if "Could not resolve HEAD" in err or "HEAD" in err:
            return None
        return f"Failed to unstage: {err.strip()}"
    return None


def _run_commit(
    message: str,
    files: List[str],
    cwd: Path,
) -> Tuple[bool, str]:
    """Attempt ``git commit``.  Returns ``(success, stderr)``."""
    code, _out, err = run_git(
        ["commit", "-m", message, "--", *files], cwd
    )
    return code == 0, err


def _try_lock_retry(
    stderr: str,
    message: str,
    files: List[str],
    cwd: Path,
) -> Tuple[bool, str]:
    """If *stderr* indicates a stale lock, remove it and retry once."""
    match = _LOCK_RE.search(stderr)
    if not match:
        return False, stderr

    lock_path = Path(match.group(1))
    if not lock_path.exists():
        return False, stderr

    try:
        lock_path.unlink()
        sys.stderr.write(f"Removed stale git lock: {lock_path}\n")
    except OSError:
        return False, stderr

    return _run_commit(message, files, cwd)


def git_commit(
    message: str,
    files: List[str],
    *,
    force_lock: bool = False,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Stage files and commit atomically.

    Returns ``(exit_code, result_message)``.

    The pipeline:
    1. Validate inputs
    2. Warn on message format / atomicity issues (never blocks)
    3. Unstage everything
    4. ``git add -A -- <files>``
    5. Verify something was staged
    6. ``git commit``
    7. Optionally retry after removing a stale lock file
    """
    repo_root, err = resolve_repo_root(cwd)
    if err or repo_root is None:
        return 1, err or "Not a git repository"

    work_cwd = cwd or repo_root

    # 1. Validate inputs
    input_err = _validate_inputs(message, files, work_cwd)
    if input_err:
        return 1, f"Error: {input_err}"

    file_err = _verify_files_exist(files, work_cwd)
    if file_err:
        return 1, f"Error: {file_err}"

    # 2. Advisory warnings
    _emit_warnings(validate_commit_message(message))
    _emit_warnings(check_atomicity(message, files))

    # 3. Unstage everything
    unstage_err = _unstage_all(work_cwd)
    if unstage_err:
        return 1, f"Error: {unstage_err}"

    # 4. Stage specified files
    code, _out, stage_err = run_git(["add", "-A", "--", *files], work_cwd)
    if code != 0:
        return 1, f"Error staging files: {stage_err.strip()}"

    # 5. Verify something was staged
    code, _out, _err = run_git(["diff", "--staged", "--quiet"], work_cwd)
    if code == 0:
        return 1, f"No staged changes detected for: {' '.join(files)}"

    # 6. Commit
    ok, commit_err = _run_commit(message, files, work_cwd)

    # 7. Lock retry
    if not ok and force_lock:
        ok, commit_err = _try_lock_retry(commit_err, message, files, work_cwd)

    if not ok:
        return 1, f"Commit failed: {commit_err.strip()}"

    return 0, f'Committed "{message}" with {len(files)} file(s)'
