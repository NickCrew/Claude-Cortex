"""Tests for registry-backed skill category helpers.

Covers the loader, the many-to-many slug->categories map, and the bulk
activate/deactivate-by-category operations that back the TUI Skills view.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.core.skills import (
    activate_skills_by_category,
    deactivate_skills_by_category,
    load_skills_registry,
    skill_categories_map,
)

pytestmark = [pytest.mark.unit, pytest.mark.core]


SAMPLE_REGISTRY = {
    "categories": {
        "security": {"name": "Security", "icon": "🔒"},
        "testing": {"name": "Testing", "icon": "🧪"},
    },
    "skills": {
        "skill-a": {"categories": ["security"]},
        "skill-b": {"categories": ["security", "testing"]},
        "skill-c": {"categories": ["testing"]},
        "skill-d": {"categories": []},
        "skill-e": "not-a-dict",  # malformed entry must not crash the map
    },
}


class TestSkillCategoriesMap:
    def test_builds_many_to_many_map(self) -> None:
        result = skill_categories_map(SAMPLE_REGISTRY)
        assert result["skill-a"] == ["security"]
        assert result["skill-b"] == ["security", "testing"]
        assert result["skill-c"] == ["testing"]

    def test_skill_with_no_categories_maps_to_empty_list(self) -> None:
        assert skill_categories_map(SAMPLE_REGISTRY)["skill-d"] == []

    def test_malformed_entry_does_not_crash(self) -> None:
        assert skill_categories_map(SAMPLE_REGISTRY)["skill-e"] == []

    def test_empty_registry_yields_empty_map(self) -> None:
        assert skill_categories_map({}) == {}


class TestLoadSkillsRegistry:
    def test_loads_yaml_from_cortex_root(self, temp_dir: Path) -> None:
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "registry.yaml").write_text(
            "categories: {security: {icon: '🔒'}}\n"
            "skills: {skill-a: {categories: [security]}}\n",
            encoding="utf-8",
        )
        registry = load_skills_registry(cortex_root=temp_dir)
        assert registry["skills"]["skill-a"]["categories"] == ["security"]

    def test_missing_file_returns_empty_dict(self, temp_dir: Path) -> None:
        assert load_skills_registry(cortex_root=temp_dir) == {}

    def test_malformed_yaml_returns_empty_dict(self, temp_dir: Path) -> None:
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "registry.yaml").write_text(
            "{ this: is: broken", encoding="utf-8"
        )
        assert load_skills_registry(cortex_root=temp_dir) == {}


@pytest.fixture
def category_env(temp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Set up a CORTEX_ROOT with skill sources and a target home directory.

    Returns (cortex_root, home). skill_activate resolves the source from the
    CORTEX_ROOT env var and the target from the passed `home`.
    """
    cortex_root = temp_dir / "cortex"
    home = temp_dir / "home"
    (cortex_root / "skills").mkdir(parents=True)
    home.mkdir()
    for slug in ("skill-a", "skill-b", "skill-c"):
        (cortex_root / "skills" / slug).mkdir()
    monkeypatch.setenv("CORTEX_ROOT", str(cortex_root))
    monkeypatch.delenv("CORTEX_SCOPE", raising=False)
    return cortex_root, home


class TestActivateSkillsByCategory:
    def test_activates_only_skills_in_category(
        self, category_env: tuple[Path, Path]
    ) -> None:
        _, home = category_env
        count, _ = activate_skills_by_category("security", SAMPLE_REGISTRY, home=home)

        skills_dir = home / ".claude" / "skills"
        # skill-a (security) and skill-b (security+testing) activate; skill-c not.
        assert count == 2
        assert (skills_dir / "skill-a").is_symlink()
        assert (skills_dir / "skill-b").is_symlink()
        assert not (skills_dir / "skill-c").exists()

    def test_overlapping_category_activates_shared_skill(
        self, category_env: tuple[Path, Path]
    ) -> None:
        _, home = category_env
        activate_skills_by_category("testing", SAMPLE_REGISTRY, home=home)
        skills_dir = home / ".claude" / "skills"
        # skill-b is in both; testing also brings in skill-c.
        assert (skills_dir / "skill-b").is_symlink()
        assert (skills_dir / "skill-c").is_symlink()

    def test_unknown_category_activates_nothing(
        self, category_env: tuple[Path, Path]
    ) -> None:
        _, home = category_env
        count, _ = activate_skills_by_category("nope", SAMPLE_REGISTRY, home=home)
        assert count == 0


class TestDeactivateSkillsByCategory:
    def test_deactivates_only_skills_in_category(
        self, category_env: tuple[Path, Path]
    ) -> None:
        _, home = category_env
        # Activate everything first so there is something to remove.
        activate_skills_by_category("security", SAMPLE_REGISTRY, home=home)
        activate_skills_by_category("testing", SAMPLE_REGISTRY, home=home)

        count, _ = deactivate_skills_by_category("security", SAMPLE_REGISTRY, home=home)
        skills_dir = home / ".claude" / "skills"
        # security removes skill-a and skill-b; skill-c (testing only) stays.
        assert count == 2
        assert not (skills_dir / "skill-a").exists()
        assert not (skills_dir / "skill-b").exists()
        assert (skills_dir / "skill-c").is_symlink()
