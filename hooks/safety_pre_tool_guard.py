#!/usr/bin/env python3
"""Block destructive tool calls or unsafe file operations.

Hook event: PreToolUse
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


_ALLOW_ENV_VARS = ("CLAUDE_ALLOW_DESTRUCTIVE", "CORTEX_ALLOW_DESTRUCTIVE")
HOOK_LOG_ENV = ("CORTEX_HOOK_LOG_PATH", "CLAUDE_HOOK_LOG_PATH")


def _hook_log_path() -> Path:
    for name in HOOK_LOG_ENV:
        value = os.getenv(name, "").strip()
        if value:
            return Path(value).expanduser()
    return Path.home() / ".cortex" / "logs" / "hooks.log"


def _log_hook(message: str) -> None:
    try:
        path = _hook_log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"{timestamp} [{Path(__file__).name}] {message}\n")
    except Exception:
        return


def _env_truthy(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "y"}


def _bypass_enabled() -> bool:
    return any(_env_truthy(name) for name in _ALLOW_ENV_VARS)


def _repo_root() -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return Path(out)
    except Exception:
        pass
    return Path.cwd()


def _allowed_roots() -> list[Path]:
    roots = [_repo_root()]
    home = Path.home()
    roots.append(home / ".claude")
    roots.append(home / ".cortex")
    plugin_root = os.getenv("CLAUDE_PLUGIN_ROOT") or os.getenv("CORTEX_PLUGIN_ROOT")
    if plugin_root:
        roots.append(Path(plugin_root).expanduser())
    roots.append(Path("/tmp"))
    roots.append(Path("/var/tmp"))
    return roots


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def _collect_tool_payload() -> str:
    payload_parts: list[str] = []
    for key in (
        "CLAUDE_TOOL_ARGS",
        "CLAUDE_TOOL_INPUT",
        "CLAUDE_TOOL_COMMAND",
        "CLAUDE_COMMAND",
        "CLAUDE_TOOL_TEXT",
    ):
        value = os.getenv(key)
        if value:
            payload_parts.append(value)
    return " ".join(payload_parts)


def _contains_dangerous_command(payload: str) -> str | None:
    patterns = {
        r"\brm\s+-rf\s+/$": "rm -rf /",
        r"\brm\s+-rf\s+~": "rm -rf ~",
        r"\brm\s+-rf\s+\.\.": "rm -rf ..",
        r"\brm\s+-rf\s+\*": "rm -rf *",
        r"\bgit\s+reset\s+--hard\b": "git reset --hard",
        r"\bgit\s+clean\s+-[a-zA-Z]*f": "git clean -f/-fdx",
        r"\bmkfs\.": "mkfs",
        r"\bdd\s+if=": "dd if=",
        r":\(\)\s*\{:\|:&\};:": "fork bomb",
        r"\bchmod\s+-R\s+7": "chmod -R 777",
        r"\bchown\s+-R\b": "chown -R",
    }
    lowered = payload.strip()
    if not lowered:
        return None
    for pattern, label in patterns.items():
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            return label
    return None


def _is_write_like_tool(tool_name: str) -> bool:
    tokens = (
        "write",
        "delete",
        "remove",
        "move",
        "rename",
        "edit",
        "patch",
    )
    return any(token in tool_name for token in tokens)


def main() -> int:
    if _bypass_enabled():
        print("Safety guard bypassed via env override.", file=sys.stderr)
        return 0

    tool_name = os.getenv("CLAUDE_TOOL_NAME", "").strip().lower()
    file_path = os.getenv("CLAUDE_FILE_PATH", "").strip()

    payload = _collect_tool_payload()
    danger = _contains_dangerous_command(payload)
    if danger:
        _log_hook(f"Blocked destructive command: {danger}")
        print(
            f"Blocked destructive command ({danger}). Set CLAUDE_ALLOW_DESTRUCTIVE=1 to bypass.",
            file=sys.stderr,
        )
        return 1

    if file_path and _is_write_like_tool(tool_name):
        target = Path(file_path).expanduser()
        allowed = _allowed_roots()
        if not any(_is_within(target, root) for root in allowed):
            roots_display = ", ".join(str(root) for root in allowed)
            _log_hook(f"Blocked file operation outside allowed roots: {target}")
            print(
                "Blocked file operation outside allowed roots. "
                f"Path: {target}. Allowed roots: {roots_display}",
                file=sys.stderr,
            )
            return 1

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _log_hook(f"Unhandled error: {exc}")
        raise
