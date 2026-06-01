from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import jsonschema
import pytest
import yaml

from claude_ctx_py.skill_index import build_index, write_index


pytestmark = pytest.mark.unit


SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"


def _visible_skill_paths() -> set[str]:
    paths: set[str] = set()
    for skill_md in SKILLS_ROOT.rglob("SKILL.md"):
        relative = skill_md.relative_to(SKILLS_ROOT)
        if any(part.startswith(".") for part in relative.parts):
            continue
        paths.add(skill_md.parent.relative_to(SKILLS_ROOT).as_posix())
    return paths


@pytest.fixture
def registry() -> dict:
    return yaml.safe_load(
        (SKILLS_ROOT / "registry.yaml").read_text(encoding="utf-8")
    )


def _sorted_skills(index: dict) -> list[dict]:
    return sorted(index["skills"], key=lambda entry: entry["name"])


def test_registry_matches_schema(registry: dict) -> None:
    schema = json.loads(
        (SKILLS_ROOT / "registry.schema.json").read_text(encoding="utf-8")
    )

    jsonschema.Draft7Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(registry)


def test_registry_and_index_cover_visible_repo_skills(registry: dict) -> None:
    visible_skill_paths = _visible_skill_paths()
    index = json.loads(
        (SKILLS_ROOT / "skill-index.json").read_text(encoding="utf-8")
    )

    registry_paths = {
        entry["path"].removesuffix("/SKILL.md")
        for entry in registry["skills"].values()
    }
    registry_names = set(registry["skills"])
    index_paths = {entry["path"] for entry in index["skills"]}
    index_names = {entry["name"] for entry in index["skills"]}

    assert registry_paths == visible_skill_paths
    assert registry_names == index_names
    assert index_paths == visible_skill_paths
    assert registry["statistics"]["total_skills"] == len(visible_skill_paths)


def test_registry_categories_are_declared(registry: dict) -> None:
    declared_categories = set(registry["categories"])

    for skill_name, entry in registry["skills"].items():
        categories = entry.get("categories", [])
        assert categories, f"{skill_name} has no categories"
        undeclared = set(categories) - declared_categories
        assert not undeclared, (
            f"{skill_name} uses undeclared categories: {sorted(undeclared)}"
        )


def test_registry_dependencies_are_flat_skill_names(registry: dict) -> None:
    for skill_name, entry in registry["skills"].items():
        dependencies = entry.get("dependencies", [])
        assert isinstance(dependencies, list), (
            f"{skill_name} dependencies must be a list"
        )
        assert all(isinstance(dependency, str) for dependency in dependencies), (
            f"{skill_name} dependencies must be flat skill-name strings"
        )
        assert not any(dependency.startswith("{") for dependency in dependencies), (
            f"{skill_name} has stringified dependency metadata"
        )
        unknown_dependencies = [
            dependency
            for dependency in dependencies
            if dependency not in registry["skills"]
        ]
        assert not unknown_dependencies, (
            f"{skill_name} has unknown dependencies: {unknown_dependencies}"
        )


def test_registry_statistics_match_entries(registry: dict) -> None:
    skills = registry["skills"]
    status_counts = Counter(entry.get("status", "active") for entry in skills.values())
    category_counts = Counter({category: 0 for category in registry["categories"]})

    for entry in skills.values():
        for category in entry.get("categories", []):
            category_counts[category] += 1

    assert registry["statistics"] == {
        "total_skills": len(skills),
        "active_skills": status_counts["active"],
        "deprecated_skills": status_counts["deprecated"],
        "experimental_skills": category_counts["experimental"],
        "by_category": dict(category_counts),
    }


def test_registry_titles_preserve_common_acronyms(registry: dict) -> None:
    common_acronyms = {
        "AI",
        "API",
        "CLI",
        "CSS",
        "CSV",
        "DOCX",
        "HTML",
        "HTTP",
        "JSON",
        "LLM",
        "MD",
        "MCP",
        "PDF",
        "PPTX",
        "PR",
        "SEO",
        "SQL",
        "TDD",
        "UI",
        "UX",
        "WCAG",
        "XLSX",
        "YAML",
    }

    for skill_name, entry in registry["skills"].items():
        words = re.findall(r"[A-Za-z0-9]+", entry["title"])
        miscapitalized = [
            word
            for word in words
            if word.upper() in common_acronyms and word != word.upper()
        ]
        assert not miscapitalized, (
            f"{skill_name} title has miscapitalized acronyms: {miscapitalized}"
        )


def test_committed_skill_index_matches_frontmatter(tmp_path: Path) -> None:
    committed = json.loads(
        (SKILLS_ROOT / "skill-index.json").read_text(encoding="utf-8")
    )
    rebuilt_path = tmp_path / "skill-index.json"
    write_index(build_index(SKILLS_ROOT), rebuilt_path)
    rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))

    assert {**committed, "skills": _sorted_skills(committed)} == {
        **rebuilt,
        "skills": _sorted_skills(rebuilt),
    }
