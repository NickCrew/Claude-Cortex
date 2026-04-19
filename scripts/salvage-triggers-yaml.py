#!/usr/bin/env python3
"""One-shot: merge unique keywords + file_patterns from agents/triggers.yaml
into each agent's SKILL.md front matter, then stop referencing triggers.yaml.

Not touched: ``activation.auto``, ``activation.priority``, ``tier.id``,
``tier.activation_strategy``. These are still enforced by the agent schema
validator in claude_ctx_py/core/agents.py and get cleaned up in a separate
schema-evolution commit.

Idempotent — running twice produces no diff.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = REPO_ROOT / "agents"
TRIGGERS_PATH = AGENTS_ROOT / "triggers.yaml"


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


def _str_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    """Preserve multi-line strings as literal blocks instead of folded scalars."""
    if "\n" in data:
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", data, style="|"
        )
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_IndentedDumper.add_representer(str, _str_presenter)


def load_triggers() -> Dict[str, Dict[str, Any]]:
    data = yaml.safe_load(TRIGGERS_PATH.read_text(encoding="utf-8")) or {}
    triggers = data.get("triggers") or {}
    return {k: v for k, v in triggers.items() if isinstance(v, dict)}


def _as_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [v.strip() for v in value if isinstance(v, str) and v.strip()]


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(item)
    return result


def _format_front_matter(data: Dict[str, Any]) -> str:
    return yaml.dump(
        data,
        Dumper=_IndentedDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,
    )


def _replace_front_matter(text: str, new_fm: str) -> str:
    leading_len = len(text) - len(text.lstrip())
    leading = text[:leading_len]
    body = text[leading_len:]
    if not body.startswith("---"):
        return text
    parts = body[3:].split("---", 1)
    if len(parts) < 2:
        return text
    trailing = parts[1]
    return f"{leading}---\n{new_fm}---{trailing}"


def merge_into_agent(
    agent_path: Path,
    trigger_kws: List[str],
    trigger_fps: List[str],
) -> bool:
    original = agent_path.read_text(encoding="utf-8")
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

    activation = data.setdefault("activation", {})
    if not isinstance(activation, dict):
        return False
    existing_kws = _as_str_list(activation.get("keywords"))
    merged_kws = _dedupe_keep_order(existing_kws + trigger_kws)
    if merged_kws:
        activation["keywords"] = merged_kws

    tier = data.setdefault("tier", {})
    if not isinstance(tier, dict):
        return False
    existing_fps = _as_str_list(tier.get("conditions"))
    merged_fps = _dedupe_keep_order(existing_fps + trigger_fps)
    if merged_fps:
        tier["conditions"] = merged_fps

    new_fm = _format_front_matter(data)
    new_text = _replace_front_matter(original, new_fm)
    if new_text == original:
        return False
    agent_path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    if not TRIGGERS_PATH.exists():
        print(f"Nothing to salvage: {TRIGGERS_PATH} already gone.")
        return 0

    triggers = load_triggers()
    written = 0
    missing: List[str] = []
    for name, cfg in triggers.items():
        agent_path = AGENTS_ROOT / f"{name}.md"
        if not agent_path.exists():
            missing.append(name)
            continue
        trigger_kws = _as_str_list(cfg.get("keywords"))
        trigger_fps = _as_str_list(cfg.get("file_patterns"))
        if not (trigger_kws or trigger_fps):
            continue
        if merge_into_agent(agent_path, trigger_kws, trigger_fps):
            written += 1

    if missing:
        print(f"WARNING: {len(missing)} agents in triggers.yaml have no .md file:")
        for name in missing:
            print(f"  - {name}")

    print(f"Merged triggers.yaml into {written} agent(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
