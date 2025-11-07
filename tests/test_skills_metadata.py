"""Metadata sanity tests for skills catalog."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1] / "skills"
SKILL_FILES = sorted(SKILL_ROOT.glob("**/SKILL.md"))


def _load_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise AssertionError(f"Skill {path} is missing front matter header")

    try:
        _, front_matter, _ = text.split("---", 2)
    except ValueError as exc:  # pragma: no cover - defensive
        raise AssertionError(f"Skill {path} has malformed front matter") from exc

    data = yaml.safe_load(front_matter) or {}
    return data


@pytest.mark.parametrize("skill_file", SKILL_FILES)
def test_skill_front_matter_has_required_fields(skill_file: Path) -> None:
    """Every SKILL.md should declare name/description, plus extra fields when needed."""

    meta = _load_front_matter(skill_file)

    assert "name" in meta and meta["name"], f"Skill {skill_file} missing name"
    assert "description" in meta and meta["description"], f"Skill {skill_file} missing description"

    # Borrowed skills must document licensing explicitly.
    if "license" in meta:
        assert "MIT" in str(meta["license"]), f"Skill {skill_file} license must mention MIT"

    # Collaboration skills should expose a slash command hook.
    if "collaboration" in skill_file.parts:
        command = meta.get("command")
        assert command and command.startswith("/ctx:"), (
            f"Skill {skill_file} must declare a /ctx:* command in front matter"
        )
