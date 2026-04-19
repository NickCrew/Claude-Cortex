#!/usr/bin/env python3
"""Remove schema-evolution fiction fields from every agent's front matter.

Strips:
- ``tier.activation_strategy`` — the Claude Code harness has no concept of
  sequential/parallel/tiered orchestration between agents at runtime.
- ``activation.auto`` — agents can't be auto-activated mid-session.
- ``activation.priority`` — no priority queue exists.
- ``activation.events`` — no event dispatch exists.

Preserved:
- ``activation.keywords`` — consumed by the agent-suggest hook.
- ``tier.id`` — kept as a descriptive label (the enum was relaxed to
  free-form strings).
- ``tier.conditions`` — consumed by agent-suggest as ``file_patterns``.

Idempotent — running twice produces no diff.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = REPO_ROOT / "agents"


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


def _str_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_IndentedDumper.add_representer(str, _str_presenter)


def _prune(data: Dict[str, Any]) -> bool:
    """Drop fiction fields in-place. Returns True when anything changed."""
    changed = False

    tier = data.get("tier")
    if isinstance(tier, dict):
        if "activation_strategy" in tier:
            tier.pop("activation_strategy", None)
            changed = True

    activation = data.get("activation")
    if isinstance(activation, dict):
        for key in ("auto", "priority", "events"):
            if key in activation:
                activation.pop(key, None)
                changed = True
        # If only empty things remain, fine — leave the block; it still
        # holds keywords for future edits.

    return changed


def strip(agent_md: Path) -> bool:
    original = agent_md.read_text(encoding="utf-8")
    stripped = original.lstrip()
    if not stripped.startswith("---"):
        return False
    parts = stripped[3:].split("---", 2)
    if len(parts) < 2:
        return False
    header = parts[0]
    try:
        data = yaml.safe_load(header) or {}
    except yaml.YAMLError:
        return False
    if not isinstance(data, dict):
        return False
    if not _prune(data):
        return False

    new_fm = yaml.dump(
        data,
        Dumper=_IndentedDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,
    )

    leading_len = len(original) - len(stripped)
    leading = original[:leading_len]
    trailing = stripped[3:].split("---", 1)[1]
    new_text = f"{leading}---\n{new_fm}---{trailing}"
    agent_md.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    written = 0
    for agent_md in sorted(AGENTS_ROOT.glob("*.md")):
        if agent_md.name.lower() in {"readme.md", "triggers.md"}:
            continue
        if strip(agent_md):
            written += 1
    print(f"Stripped fiction fields from {written} agent file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
