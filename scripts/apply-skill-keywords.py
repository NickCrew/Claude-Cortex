#!/usr/bin/env python3
"""Apply a JSON map of {skill_name: [keywords]} into SKILL.md front matter.

Used for Phase 6 gap-fill: seeds keywords into skills whose front matter
had empty ``keywords:`` after the legacy-registry migration.

Usage:
    python3 scripts/apply-skill-keywords.py path/to/seeds.json

Idempotent — merges with any existing keywords, dedupes case-insensitively.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"


class _IndentedDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


def _str_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.ScalarNode:
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_IndentedDumper.add_representer(str, _str_presenter)


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        lower = item.lower()
        if lower in seen:
            continue
        seen.add(lower)
        out.append(item)
    return out


def _name_to_path(name: str) -> Path | None:
    """Locate the SKILL.md for ``name``. Searches top-level then one level deep."""
    direct = SKILLS_ROOT / name / "SKILL.md"
    if direct.exists():
        return direct
    for nested in SKILLS_ROOT.glob(f"*/{name}/SKILL.md"):
        return nested
    # "playwright-cli" maps to skills/playwright/SKILL.md etc. — scan by name-in-front-matter
    for candidate in SKILLS_ROOT.rglob("SKILL.md"):
        rel = candidate.relative_to(SKILLS_ROOT)
        if any(p.startswith(".") for p in rel.parts[:-1]):
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1)) or {}
            if isinstance(fm, dict) and fm.get("name") == name:
                return candidate
        except Exception:
            continue
    return None


def merge_into_skill_md(skill_md: Path, new_keywords: List[str]) -> bool:
    original = skill_md.read_text(encoding="utf-8")
    stripped = original.lstrip()
    if not stripped.startswith("---"):
        return False
    parts = stripped[3:].split("---", 2)
    if len(parts) < 2:
        return False

    header = parts[0]
    try:
        data: Any = yaml.safe_load(header) or {}
    except yaml.YAMLError:
        return False
    if not isinstance(data, dict):
        return False

    existing = data.get("keywords")
    existing_list: List[str] = []
    if isinstance(existing, list):
        existing_list = [
            k.strip() for k in existing if isinstance(k, str) and k.strip()
        ]
    merged = _dedupe_keep_order(existing_list + new_keywords)
    if merged == existing_list:
        return False
    data["keywords"] = merged

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
    trailing = stripped[3:].split("---", 1)[1]  # content after the closing ---
    new_text = f"{leading}---\n{new_fm}---{trailing}"
    skill_md.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: apply-skill-keywords.py seeds.json", file=sys.stderr)
        return 2

    seeds_path = Path(sys.argv[1])
    seeds: Dict[str, List[str]] = json.loads(seeds_path.read_text(encoding="utf-8"))

    missing: List[str] = []
    written = 0
    for name, keywords in seeds.items():
        skill_md = _name_to_path(name)
        if skill_md is None:
            missing.append(name)
            continue
        kws = [k.strip() for k in keywords if isinstance(k, str) and k.strip()]
        if not kws:
            continue
        if merge_into_skill_md(skill_md, kws):
            written += 1

    if missing:
        print(f"WARNING: {len(missing)} skills not found:")
        for name in missing:
            print(f"  - {name}")

    print(f"Merged keywords into {written} SKILL.md file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
