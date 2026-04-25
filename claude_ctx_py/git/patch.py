"""Hunk-level atomic stage-and-commit via diff application.

Ports the ``--patch`` mode from ``bin/committer``:
unstage everything → apply diff to index → validate staged files → commit.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from .commit import (
    _emit_warnings,
    _normalize_path,
    _run_commit,
    _try_lock_retry,
    _unstage_all,
    _validate_inputs,
    _verify_files_exist,
)
from .run import resolve_repo_root, run_git
from .validate import check_atomicity, validate_commit_message


def git_patch(
    message: str,
    files: List[str],
    diff_content: str,
    *,
    force_lock: bool = False,
    cwd: Optional[Path] = None,
) -> Tuple[int, str]:
    """Apply a diff to the index and commit atomically.

    Returns ``(exit_code, result_message)``.

    The pipeline:
    1. Validate inputs (including non-empty diff)
    2. Warn on message format / atomicity issues
    3. Unstage everything
    4. Write diff to temp file, ``git apply --cached``
    5. Validate staged files match the allowed list
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

    if not diff_content or not diff_content.strip():
        return 1, "Error: Patch input is empty"

    # 2. Advisory warnings
    _emit_warnings(validate_commit_message(message))
    _emit_warnings(check_atomicity(message, files))

    # 3. Unstage everything
    unstage_err = _unstage_all(work_cwd)
    if unstage_err:
        return 1, f"Error: {unstage_err}"

    # 4. Write diff to temp file and apply to index
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".diff", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(diff_content)
        if not diff_content.endswith("\n"):
            tmp.write("\n")
        tmp.close()

        code, _out, apply_err = run_git(
            ["apply", "--cached", "--", tmp.name], work_cwd
        )
        if code != 0:
            return 1, f"Error: Failed to apply patch to index: {apply_err.strip()}"

        # 5. Validate staged files against allowed list
        code, staged_out, _err = run_git(["diff", "--cached", "--name-only"], work_cwd)
        staged_files = [
            line for line in staged_out.splitlines() if line.strip()
        ]

        if not staged_files:
            return 1, "No staged changes detected from patch input"

        allowed_normalized = {_normalize_path(f) for f in files}
        for staged in staged_files:
            staged_norm = _normalize_path(staged)
            if staged_norm not in allowed_normalized:
                return 1, (
                    f"Error: Patch staged unexpected file: {staged_norm}\n"
                    f"Allowed files: {' '.join(files)}"
                )

        # 6. Verify something was staged (belt-and-suspenders)
        code, _out, _err = run_git(["diff", "--staged", "--quiet"], work_cwd)
        if code == 0:
            return 1, f"No staged changes detected for: {' '.join(files)}"

        # 7. Commit the index without pathspec — passing files here would
        #    trigger git's --only mode and re-stage working-tree content,
        #    silently overwriting the hunks just applied via ``apply --cached``.
        ok, commit_err = _run_commit(message, files, work_cwd, with_pathspec=False)

        # 8. Lock retry
        if not ok and force_lock:
            ok, commit_err = _try_lock_retry(
                commit_err, message, files, work_cwd, with_pathspec=False
            )

        if not ok:
            return 1, f"Commit failed: {commit_err.strip()}"

        return 0, f'Committed "{message}" with {len(files)} file(s)'

    finally:
        Path(tmp.name).unlink(missing_ok=True)
