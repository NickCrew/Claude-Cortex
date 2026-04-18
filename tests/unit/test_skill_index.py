"""Unit tests for claude_ctx_py.skill_index."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest

from claude_ctx_py.skill_index import (
    DEFAULT_CONFIDENCE,
    SKILL_INDEX_VERSION,
    SkillIndexError,
    build_index,
    load_index,
    rebuild_index,
    write_index,
)


def _make_skill(
    skills_root: Path,
    rel_path: str,
    *,
    name: str,
    description: str = "A test skill",
    keywords: list[str] | None = None,
    file_patterns: list[str] | None = None,
    confidence: float | None = None,
    body: str = "Skill body.",
    extra_fields: dict[str, object] | None = None,
) -> Path:
    """Create a SKILL.md at skills_root/rel_path with the given front matter."""
    skill_dir = skills_root / rel_path
    skill_dir.mkdir(parents=True, exist_ok=True)

    fm_lines = [f"name: {name}", f"description: {description}"]
    if keywords is not None:
        fm_lines.append("keywords:")
        for kw in keywords:
            fm_lines.append(f"  - {kw}")
    if file_patterns is not None:
        fm_lines.append("file_patterns:")
        for fp in file_patterns:
            fm_lines.append(f'  - "{fp}"')
    if confidence is not None:
        fm_lines.append(f"confidence: {confidence}")
    if extra_fields:
        for key, value in extra_fields.items():
            fm_lines.append(f"{key}:")
            if isinstance(value, list):
                for item in value:
                    fm_lines.append(f"  - {item}")
            else:
                fm_lines[-1] = f"{key}: {value}"

    content = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body + "\n"
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(content, encoding="utf-8")
    return skill_md


@pytest.mark.unit
class TestBuildIndex:
    def test_happy_path(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "alpha",
            name="alpha",
            description="First skill",
            keywords=["alpha", "foo"],
            file_patterns=["**/alpha/**"],
            confidence=0.9,
        )
        _make_skill(
            skills_root,
            "beta",
            name="beta",
            description="Second skill",
            keywords=["beta"],
        )

        doc = build_index(skills_root)

        assert doc["version"] == SKILL_INDEX_VERSION
        assert doc["generated_from"] == "SKILL.md front matter"
        assert [e["name"] for e in doc["skills"]] == ["alpha", "beta"]

        alpha = doc["skills"][0]
        assert alpha["path"] == "alpha"
        assert alpha["keywords"] == ["alpha", "foo"]
        assert alpha["file_patterns"] == ["**/alpha/**"]
        assert alpha["confidence"] == 0.9

        beta = doc["skills"][1]
        assert beta["confidence"] == DEFAULT_CONFIDENCE
        assert beta["file_patterns"] == []

    def test_sorted_by_name(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "zulu", name="zulu", keywords=["z"])
        _make_skill(skills_root, "alpha", name="alpha", keywords=["a"])
        _make_skill(skills_root, "mike", name="mike", keywords=["m"])

        doc = build_index(skills_root)

        assert [e["name"] for e in doc["skills"]] == ["alpha", "mike", "zulu"]

    def test_nested_paths(self, tmp_path: Path) -> None:
        """Skills under category subdirectories keep their nested path."""
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "collaboration/brainstorming",
            name="brainstorming",
            keywords=["brainstorm"],
        )
        _make_skill(
            skills_root,
            "top-level",
            name="top-level",
            keywords=["top"],
        )

        doc = build_index(skills_root)

        by_name = {e["name"]: e for e in doc["skills"]}
        assert by_name["brainstorming"]["path"] == "collaboration/brainstorming"
        assert by_name["top-level"]["path"] == "top-level"

    def test_duplicate_names_raises(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "first", name="shared", keywords=["a"])
        _make_skill(skills_root, "second", name="shared", keywords=["b"])

        with pytest.raises(SkillIndexError, match="duplicate skill name"):
            build_index(skills_root)

    def test_missing_name_raises(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        skill_dir = skills_root / "nameless"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: no name\n---\n\nBody\n", encoding="utf-8"
        )

        with pytest.raises(SkillIndexError, match="missing or invalid 'name'"):
            build_index(skills_root)

    def test_skill_without_front_matter_skipped(self, tmp_path: Path) -> None:
        """Files without YAML front matter are skipped with a warning, not errored."""
        skills_root = tmp_path / "skills"
        skill_dir = skills_root / "plain"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "# Plain skill\n\nNo front matter here.\n", encoding="utf-8"
        )
        _make_skill(skills_root, "with-fm", name="with-fm", keywords=["ok"])

        doc = build_index(skills_root)

        assert [e["name"] for e in doc["skills"]] == ["with-fm"]

    def test_empty_keywords_warns_not_errors(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "no-kw", name="no-kw", keywords=[])

        doc = build_index(skills_root)

        assert len(doc["skills"]) == 1
        assert doc["skills"][0]["keywords"] == []
        captured = capsys.readouterr()
        assert "empty keywords: no-kw" in captured.err

    def test_triggers_treated_as_keywords(self, tmp_path: Path) -> None:
        """`triggers:` in front matter is merged into keywords (migration alias)."""
        skills_root = tmp_path / "skills"
        skill_dir = skills_root / "trigger-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            dedent(
                """\
                ---
                name: trigger-skill
                description: Uses triggers field
                keywords:
                  - kw-one
                triggers:
                  - trig-one
                  - trig-two
                ---

                Body.
                """
            ),
            encoding="utf-8",
        )

        doc = build_index(skills_root)
        entry = doc["skills"][0]
        # write_index dedupes+sorts; build_index preserves append order of kw+trig
        assert set(entry["keywords"]) == {"kw-one", "trig-one", "trig-two"}

    def test_malformed_yaml_raises(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        skill_dir = skills_root / "broken"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: broken\n  bad: : indent\n---\n\nBody\n",
            encoding="utf-8",
        )

        with pytest.raises(SkillIndexError, match="malformed YAML"):
            build_index(skills_root)

    def test_confidence_out_of_range_raises(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "bad-conf",
            name="bad-conf",
            keywords=["x"],
            confidence=1.5,
        )

        with pytest.raises(SkillIndexError, match="out of range"):
            build_index(skills_root)

    def test_missing_skills_root_raises(self, tmp_path: Path) -> None:
        with pytest.raises(SkillIndexError, match="not found"):
            build_index(tmp_path / "does-not-exist")

    def test_hidden_directories_skipped(self, tmp_path: Path) -> None:
        """SKILL.md files under dot-prefixed dirs (.system/, .cache/) are ignored."""
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            ".system/skill-creator",
            name="skill-creator",
            keywords=["hidden"],
        )
        _make_skill(
            skills_root,
            "skill-creator",
            name="skill-creator",
            keywords=["visible"],
        )

        doc = build_index(skills_root)

        assert len(doc["skills"]) == 1
        assert doc["skills"][0]["path"] == "skill-creator"
        assert doc["skills"][0]["keywords"] == ["visible"]


@pytest.mark.unit
class TestWriteAndLoad:
    def test_write_is_deterministic(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "alpha",
            name="alpha",
            keywords=["b", "a", "a"],
            file_patterns=["*.py", "*.py"],
        )
        _make_skill(skills_root, "beta", name="beta", keywords=["c"])

        out_1 = tmp_path / "out1.json"
        out_2 = tmp_path / "out2.json"

        doc = build_index(skills_root)
        write_index(doc, out_1)
        write_index(build_index(skills_root), out_2)

        assert out_1.read_bytes() == out_2.read_bytes()

    def test_write_dedupes_and_sorts_keywords(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "sorted",
            name="sorted",
            keywords=["zebra", "apple", "mango", "apple"],
        )

        out = tmp_path / "index.json"
        write_index(build_index(skills_root), out)

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["skills"][0]["keywords"] == ["apple", "mango", "zebra"]

    def test_write_includes_schema_ref(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "s", name="s", keywords=["x"])

        out = tmp_path / "index.json"
        write_index(build_index(skills_root), out)

        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["$schema"] == "../schemas/skill-index.schema.json"

    def test_load_round_trips(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(
            skills_root,
            "alpha",
            name="alpha",
            description="First",
            keywords=["a"],
            file_patterns=["**/a/**"],
            confidence=0.7,
        )

        out = tmp_path / "index.json"
        write_index(build_index(skills_root), out)

        loaded = load_index(out)
        assert loaded["version"] == SKILL_INDEX_VERSION
        assert len(loaded["skills"]) == 1
        entry = loaded["skills"][0]
        assert entry["name"] == "alpha"
        assert entry["keywords"] == ["a"]
        assert entry["file_patterns"] == ["**/a/**"]
        assert entry["confidence"] == 0.7

    def test_load_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(SkillIndexError, match="not found"):
            load_index(tmp_path / "missing.json")

    def test_load_malformed_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with pytest.raises(SkillIndexError, match="not valid JSON"):
            load_index(bad)

    def test_load_missing_skills_array(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text('{"version": "x"}', encoding="utf-8")
        with pytest.raises(SkillIndexError, match="missing 'skills' array"):
            load_index(bad)


@pytest.mark.unit
class TestRebuildIndexEntrypoint:
    def test_writes_to_skills_root(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "one", name="one", keywords=["x"])

        exit_code, message = rebuild_index(skills_root=skills_root)

        index_path = skills_root / "skill-index.json"
        assert exit_code == 0
        assert index_path.exists()
        assert "1 skills" in message
        data = json.loads(index_path.read_text(encoding="utf-8"))
        assert data["skills"][0]["name"] == "one"

    def test_returns_error_code_on_bad_input(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        skill_dir = skills_root / "dup1"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: same\n---\n\nBody\n", encoding="utf-8"
        )
        skill_dir2 = skills_root / "dup2"
        skill_dir2.mkdir(parents=True)
        (skill_dir2 / "SKILL.md").write_text(
            "---\nname: same\n---\n\nBody\n", encoding="utf-8"
        )

        exit_code, message = rebuild_index(skills_root=skills_root)
        assert exit_code == 1
        assert "duplicate skill name" in message

    def test_idempotent_write(self, tmp_path: Path) -> None:
        skills_root = tmp_path / "skills"
        _make_skill(skills_root, "a", name="a", keywords=["x", "y"])
        _make_skill(skills_root, "b", name="b", keywords=["z"])

        rebuild_index(skills_root=skills_root)
        first = (skills_root / "skill-index.json").read_bytes()
        rebuild_index(skills_root=skills_root)
        second = (skills_root / "skill-index.json").read_bytes()

        assert first == second
