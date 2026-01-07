#!/usr/bin/env python3
"""Sync bundled assets into claude_ctx_py/assets.

Usage:
  python scripts/sync_bundled_assets.py
"""

from __future__ import annotations

from pathlib import Path
import shutil


ASSET_ITEMS = [
    ".claude-plugin",
    ".mcp.json",
    ".lsp.json",
    "agents",
    "commands",
    "skills",
    "hooks",
    "modes",
    "rules",
    "workflows",
    "flags",
    "profiles",
    "scenarios",
    "tasks",
    "principles",
    "prompts",
    "templates",
    "schema",
    "mcp",
    "inactive",
    "scripts",
]


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    assets_root = repo / "claude_ctx_py" / "assets"

    if assets_root.exists():
        shutil.rmtree(assets_root)
    assets_root.mkdir(parents=True, exist_ok=True)

    for item in ASSET_ITEMS:
        src = repo / item
        if not src.exists():
            continue
        dest = assets_root / item
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    print(f"Bundled assets synced to {assets_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
