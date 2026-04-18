"""Build and read skills/skill-index.json from SKILL.md front matter.

The skill index is the single source of truth consumed by the UserPromptSubmit
hook, the SkillRecommender rule strategy, and `cortex skills analyze`. It is
generated from each skill's own SKILL.md front matter via
``cortex skills rebuild-index`` and committed to the repo.

Output is deterministic: skills are sorted by name, keywords and file patterns
are deduplicated and sorted, and keys are written in a fixed order so repeated
regeneration produces zero git diff.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict

import yaml

from .core.base import _extract_front_matter, _resolve_cortex_root


SKILL_INDEX_VERSION = "2026-04-18"
DEFAULT_CONFIDENCE = 0.8
SCHEMA_REF = "../schemas/skill-index.schema.json"


class IndexEntry(TypedDict):
    name: str
    path: str
    description: str
    keywords: List[str]
    file_patterns: List[str]
    confidence: float


class IndexDoc(TypedDict):
    version: str
    generated_from: str
    skills: List[IndexEntry]


class SkillIndexError(Exception):
    """Raised when the skill index cannot be built or loaded."""


def build_index(skills_root: Path) -> IndexDoc:
    """Walk ``skills_root`` for SKILL.md files and build a sorted index.

    Emits warnings to stderr for skills with empty keyword lists; raises
    ``SkillIndexError`` on duplicate skill names, missing required front
    matter fields, or malformed YAML.
    """
    if not skills_root.is_dir():
        raise SkillIndexError(f"skills root not found: {skills_root}")

    entries: List[IndexEntry] = []
    seen_names: Dict[str, str] = {}
    warnings: List[str] = []

    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        if _is_hidden(skill_md, skills_root):
            continue
        entry = _parse_skill_front_matter(skill_md, skills_root)
        if entry is None:
            warnings.append(
                f"skipped (no front matter): {skill_md.relative_to(skills_root)}"
            )
            continue
        name = entry["name"]
        if name in seen_names:
            raise SkillIndexError(
                f"duplicate skill name {name!r} in both "
                f"{seen_names[name]!r} and {entry['path']!r}"
            )
        seen_names[name] = entry["path"]
        if not entry["keywords"]:
            warnings.append(f"empty keywords: {name}")
        entries.append(entry)

    entries.sort(key=lambda e: e["name"])

    for message in warnings:
        print(f"skill-index: warning: {message}", file=sys.stderr)

    return {
        "version": SKILL_INDEX_VERSION,
        "generated_from": "SKILL.md front matter",
        "skills": entries,
    }


def load_index(index_path: Path) -> IndexDoc:
    """Load an existing ``skill-index.json`` with light validation."""
    try:
        raw_text = index_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SkillIndexError(f"skill index not found: {index_path}") from exc

    try:
        raw: Any = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise SkillIndexError(
            f"skill index is not valid JSON ({index_path}): {exc}"
        ) from exc

    if not isinstance(raw, dict) or "skills" not in raw or not isinstance(
        raw["skills"], list
    ):
        raise SkillIndexError(
            f"skill index missing 'skills' array: {index_path}"
        )

    skills: List[IndexEntry] = []
    for item in raw["skills"]:
        if not isinstance(item, dict) or "name" not in item:
            raise SkillIndexError(
                f"malformed skill entry in {index_path}: {item!r}"
            )
        skills.append(
            {
                "name": str(item["name"]),
                "path": str(item.get("path", "")),
                "description": str(item.get("description", "")),
                "keywords": [str(k) for k in item.get("keywords", []) or []],
                "file_patterns": [
                    str(p) for p in item.get("file_patterns", []) or []
                ],
                "confidence": float(
                    item.get("confidence", DEFAULT_CONFIDENCE)
                ),
            }
        )

    return {
        "version": str(raw.get("version", "")),
        "generated_from": str(raw.get("generated_from", "")),
        "skills": skills,
    }


def write_index(doc: IndexDoc, out_path: Path) -> None:
    """Write ``doc`` to ``out_path`` with canonical key order and trailing newline."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    serializable = _canonical_doc(doc)
    text = json.dumps(serializable, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(text, encoding="utf-8")


def _canonical_doc(doc: IndexDoc) -> Dict[str, Any]:
    return {
        "$schema": SCHEMA_REF,
        "version": doc["version"],
        "generated_from": doc["generated_from"],
        "skills": [_canonical_entry(entry) for entry in doc["skills"]],
    }


def _canonical_entry(entry: IndexEntry) -> Dict[str, Any]:
    return {
        "name": entry["name"],
        "path": entry["path"],
        "description": entry["description"],
        "keywords": sorted({k for k in entry["keywords"] if k}),
        "file_patterns": sorted({p for p in entry["file_patterns"] if p}),
        "confidence": entry["confidence"],
    }


def _parse_skill_front_matter(
    skill_md: Path, skills_root: Path
) -> Optional[IndexEntry]:
    """Parse one SKILL.md file's front matter into an :class:`IndexEntry`.

    Returns ``None`` when the file has no YAML front matter block. Raises
    :class:`SkillIndexError` on malformed YAML or missing required fields.
    """
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    raw_front_matter = _extract_front_matter(text)
    if raw_front_matter is None:
        return None

    try:
        data: Any = yaml.safe_load(raw_front_matter) or {}
    except yaml.YAMLError as exc:
        raise SkillIndexError(
            f"malformed YAML front matter in "
            f"{skill_md.relative_to(skills_root)}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise SkillIndexError(
            f"front matter is not a YAML mapping in "
            f"{skill_md.relative_to(skills_root)}"
        )

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise SkillIndexError(
            f"missing or invalid 'name' in "
            f"{skill_md.relative_to(skills_root)}"
        )

    description_raw = data.get("description", "")
    description = (
        description_raw.strip()
        if isinstance(description_raw, str)
        else str(description_raw)
    )

    keywords = _coerce_str_list(data.get("keywords")) + _coerce_str_list(
        data.get("triggers")
    )
    file_patterns = _coerce_str_list(data.get("file_patterns"))

    confidence = _coerce_confidence(
        data.get("confidence"), skill_md.relative_to(skills_root)
    )

    rel_path = skill_md.parent.relative_to(skills_root).as_posix()

    return {
        "name": name.strip(),
        "path": rel_path,
        "description": description,
        "keywords": keywords,
        "file_patterns": file_patterns,
        "confidence": confidence,
    }


def _is_hidden(skill_md: Path, skills_root: Path) -> bool:
    """Return True if any path segment under skills_root starts with a dot.

    Keeps `.system/`, `.cache/`, and similar infrastructure directories out of
    the index so they do not collide with user-facing skills of the same name.
    """
    rel = skill_md.relative_to(skills_root)
    return any(part.startswith(".") for part in rel.parts[:-1])


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


def _coerce_confidence(value: Any, rel_path: Path) -> float:
    if value is None:
        return DEFAULT_CONFIDENCE
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SkillIndexError(
            f"confidence must be a number in {rel_path}: got {value!r}"
        )
    conf = float(value)
    if conf < 0.0 or conf > 1.0:
        raise SkillIndexError(
            f"confidence out of range [0,1] in {rel_path}: {conf}"
        )
    return conf


def rebuild_index(
    skills_root: Optional[Path] = None,
    out_path: Optional[Path] = None,
) -> Tuple[int, str]:
    """CLI handler for ``cortex skills rebuild-index``.

    Returns ``(exit_code, message)``. ``exit_code`` is ``0`` on success,
    ``1`` on failure.
    """
    resolved_root = skills_root or (_resolve_cortex_root() / "skills")
    resolved_out = out_path or (resolved_root / "skill-index.json")

    try:
        doc = build_index(resolved_root)
    except SkillIndexError as exc:
        return 1, f"error building skill index: {exc}"

    try:
        write_index(doc, resolved_out)
    except OSError as exc:
        return 1, f"error writing {resolved_out}: {exc}"

    return 0, f"Wrote {resolved_out} ({len(doc['skills'])} skills)"
