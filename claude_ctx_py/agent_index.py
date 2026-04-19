"""Build and read agents/agent-index.json from each agent's front matter.

The agent index is the single source of truth consumed by
``cortex hooks agent-suggest``. It is generated from each agent's own ``.md``
front matter via ``cortex agent rebuild-index`` and committed to the repo.

Output is deterministic: agents sorted by name, keywords/file_patterns/aliases
deduplicated and sorted, keys written in a fixed order.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import yaml

from .core.base import _extract_front_matter, _resolve_cortex_root


AGENT_INDEX_VERSION = "2026-04-19"
SCHEMA_REF = "../schemas/agent-index.schema.json"
ALLOWED_DELEGATE_WHEN = {"isolation", "independence", "parallel", "large_scope"}


class AgentIndexEntry(TypedDict):
    name: str
    path: str
    description: str
    aliases: List[str]
    keywords: List[str]
    file_patterns: List[str]
    delegate_when: List[str]


class AgentIndexDoc(TypedDict):
    version: str
    generated_from: str
    agents: List[AgentIndexEntry]


class AgentIndexError(Exception):
    pass


def build_index(agents_root: Path) -> AgentIndexDoc:
    """Walk top-level ``agents/*.md`` and build a sorted index."""
    if not agents_root.is_dir():
        raise AgentIndexError(f"agents root not found: {agents_root}")

    entries: List[AgentIndexEntry] = []
    seen_names: Dict[str, str] = {}
    warnings: List[str] = []

    for agent_md in sorted(agents_root.glob("*.md")):
        if agent_md.name.lower() in {"readme.md", "triggers.md"}:
            continue
        entry = _parse_agent_front_matter(agent_md, agents_root)
        if entry is None:
            warnings.append(f"skipped (no front matter): {agent_md.name}")
            continue
        name = entry["name"]
        if name in seen_names:
            raise AgentIndexError(
                f"duplicate agent name {name!r} in {seen_names[name]!r} and {entry['path']!r}"
            )
        seen_names[name] = entry["path"]
        if not entry["keywords"]:
            warnings.append(f"empty keywords: {name}")
        entries.append(entry)

    entries.sort(key=lambda e: e["name"])
    for message in warnings:
        print(f"agent-index: warning: {message}", file=sys.stderr)

    return {
        "version": AGENT_INDEX_VERSION,
        "generated_from": "agent .md front matter",
        "agents": entries,
    }


def load_index(index_path: Path) -> AgentIndexDoc:
    try:
        raw_text = index_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise AgentIndexError(f"agent index not found: {index_path}") from exc
    try:
        raw: Any = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise AgentIndexError(
            f"agent index is not valid JSON ({index_path}): {exc}"
        ) from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("agents"), list):
        raise AgentIndexError(f"agent index missing 'agents' array: {index_path}")

    agents: List[AgentIndexEntry] = []
    for item in raw["agents"]:
        if not isinstance(item, dict) or "name" not in item:
            raise AgentIndexError(f"malformed agent entry in {index_path}: {item!r}")
        agents.append(
            {
                "name": str(item["name"]),
                "path": str(item.get("path", "")),
                "description": str(item.get("description", "")),
                "aliases": [str(a) for a in item.get("aliases", []) or []],
                "keywords": [str(k) for k in item.get("keywords", []) or []],
                "file_patterns": [
                    str(p) for p in item.get("file_patterns", []) or []
                ],
                "delegate_when": [
                    str(d) for d in item.get("delegate_when", []) or []
                ],
            }
        )

    return {
        "version": str(raw.get("version", "")),
        "generated_from": str(raw.get("generated_from", "")),
        "agents": agents,
    }


def write_index(doc: AgentIndexDoc, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = _canonical_doc(doc)
    text = json.dumps(serializable, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(text, encoding="utf-8")


def _canonical_doc(doc: AgentIndexDoc) -> Dict[str, Any]:
    return {
        "$schema": SCHEMA_REF,
        "version": doc["version"],
        "generated_from": doc["generated_from"],
        "agents": [_canonical_entry(entry) for entry in doc["agents"]],
    }


def _canonical_entry(entry: AgentIndexEntry) -> Dict[str, Any]:
    return {
        "name": entry["name"],
        "path": entry["path"],
        "description": entry["description"],
        "aliases": sorted({a for a in entry["aliases"] if a}),
        "keywords": sorted({k for k in entry["keywords"] if k}),
        "file_patterns": sorted({p for p in entry["file_patterns"] if p}),
        "delegate_when": sorted({d for d in entry["delegate_when"] if d}),
    }


def _parse_agent_front_matter(
    agent_md: Path, agents_root: Path
) -> Optional[AgentIndexEntry]:
    text = agent_md.read_text(encoding="utf-8", errors="replace")
    raw = _extract_front_matter(text)
    if raw is None:
        return None
    try:
        data: Any = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise AgentIndexError(
            f"malformed YAML front matter in {agent_md.name}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise AgentIndexError(
            f"front matter is not a mapping in {agent_md.name}"
        )

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise AgentIndexError(
            f"missing or invalid 'name' in {agent_md.name}"
        )

    description_raw = data.get("description") or data.get("summary", "")
    description = (
        description_raw.strip()
        if isinstance(description_raw, str)
        else str(description_raw)
    )

    activation = data.get("activation") or {}
    keywords = (
        _coerce_str_list(activation.get("keywords"))
        if isinstance(activation, dict)
        else []
    )

    tier = data.get("tier") or {}
    file_patterns = (
        _coerce_str_list(tier.get("conditions"))
        if isinstance(tier, dict)
        else []
    )

    aliases = _coerce_str_list(data.get("alias"))
    delegate_when_raw = _coerce_str_list(data.get("delegate_when"))
    invalid = [d for d in delegate_when_raw if d not in ALLOWED_DELEGATE_WHEN]
    if invalid:
        raise AgentIndexError(
            f"invalid delegate_when values in {agent_md.name}: {invalid} "
            f"(allowed: {sorted(ALLOWED_DELEGATE_WHEN)})"
        )

    rel_path = agent_md.relative_to(agents_root).as_posix()

    return {
        "name": name.strip(),
        "path": rel_path,
        "description": description,
        "aliases": aliases,
        "keywords": keywords,
        "file_patterns": file_patterns,
        "delegate_when": delegate_when_raw,
    }


def _coerce_str_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                out.append(stripped)
    return out


def rebuild_index(
    agents_root: Optional[Path] = None,
    out_path: Optional[Path] = None,
) -> Tuple[int, str]:
    """CLI handler for ``cortex agent rebuild-index``."""
    resolved_root = agents_root or (_resolve_cortex_root() / "agents")
    resolved_out = out_path or (resolved_root / "agent-index.json")

    try:
        doc = build_index(resolved_root)
    except AgentIndexError as exc:
        return 1, f"error building agent index: {exc}"

    try:
        write_index(doc, resolved_out)
    except OSError as exc:
        return 1, f"error writing {resolved_out}: {exc}"

    return 0, f"Wrote {resolved_out} ({len(doc['agents'])} agents)"
