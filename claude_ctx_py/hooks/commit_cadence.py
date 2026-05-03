"""Nudge the model to commit when stopping with uncommitted changes.

Exposed to the harness as ``cortex hooks commit-cadence``. Registered in
``~/.claude/settings.json`` via ``cortex hooks install commit-cadence``.

Hook event: Stop.

Reads ``git status --porcelain`` from the current working directory. If the
working tree has uncommitted changes, prints a short reminder to stdout — the
Claude Code harness surfaces stdout as a system reminder on the next turn,
which is the triggering event the model needs to consider offering to commit.
Always exits 0; this is a nudge, never a block.

Environment variables:
- ``COMMIT_CADENCE_DISABLE``: any non-empty value silences the hook for the
  current session.
"""

from __future__ import annotations

import os
import subprocess
from typing import List

from .skill_suggest import _log_hook


_MAX_LISTED = 10


def _porcelain_paths() -> List[str]:
    try:
        output = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    paths: List[str] = []
    for line in output.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if path:
            paths.append(path)
    return paths


def main() -> int:
    if os.getenv("COMMIT_CADENCE_DISABLE", "").strip():
        return 0

    paths = _porcelain_paths()
    if not paths:
        return 0

    listed = paths[:_MAX_LISTED]
    overflow = len(paths) - len(listed)
    listing = "\n".join(f"- {p}" for p in listed)
    if overflow > 0:
        listing += f"\n- ... and {overflow} more"

    noun = "file" if len(paths) == 1 else "files"
    _log_hook(f"commit-cadence: {len(paths)} uncommitted {noun}")
    print(
        f"Commit cadence: {len(paths)} uncommitted {noun} in working tree:\n"
        f"{listing}\n"
        "If any are deliverable, offer to commit before ending the turn."
    )
    return 0


def run() -> int:
    try:
        return main()
    except Exception as exc:
        try:
            _log_hook(f"commit-cadence unhandled error: {exc}")
        except Exception:
            pass
        raise
