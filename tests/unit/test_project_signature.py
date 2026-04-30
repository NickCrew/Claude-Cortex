"""Unit tests for claude_ctx_py.intelligence.project_signature."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.intelligence.project_signature import (
    ProjectSignature,
    compute_project_signature,
)

pytestmark = [pytest.mark.unit, pytest.mark.intelligence]


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


class TestComputeProjectSignature:
    """Compute signature from a synthesized filesystem layout."""

    def test_python_project(self, tmp_path: Path) -> None:
        _touch(tmp_path / "pyproject.toml")
        _touch(tmp_path / "src" / "app.py")
        _touch(tmp_path / "tests" / "test_app.py")
        _touch(tmp_path / "README.md")

        sig = compute_project_signature(tmp_path)

        assert ".py" in sig.file_extensions
        assert ".md" in sig.file_extensions
        assert "pyproject.toml" in sig.tooling_markers
        assert "src" in sig.directories
        assert "tests" in sig.directories

    def test_frontend_project(self, tmp_path: Path) -> None:
        _touch(tmp_path / "package.json")
        _touch(tmp_path / "tsconfig.json")
        _touch(tmp_path / "src" / "App.tsx")
        _touch(tmp_path / "src" / "components" / "Button.tsx")

        sig = compute_project_signature(tmp_path)

        assert ".tsx" in sig.file_extensions
        assert "package.json" in sig.tooling_markers
        assert "tsconfig.json" in sig.tooling_markers
        assert "components" in sig.directories
        assert ".py" not in sig.file_extensions

    def test_polyglot_project(self, tmp_path: Path) -> None:
        _touch(tmp_path / "Cargo.toml")
        _touch(tmp_path / "src" / "main.rs")
        _touch(tmp_path / "scripts" / "deploy.py")
        _touch(tmp_path / "Dockerfile")

        sig = compute_project_signature(tmp_path)

        assert ".rs" in sig.file_extensions
        assert ".py" in sig.file_extensions
        assert "Cargo.toml" in sig.tooling_markers
        assert "Dockerfile" in sig.tooling_markers

    def test_ignored_directories_are_skipped(self, tmp_path: Path) -> None:
        _touch(tmp_path / "src" / "app.py")
        _touch(tmp_path / "node_modules" / "react" / "index.js")
        _touch(tmp_path / ".venv" / "lib" / "site.py")

        sig = compute_project_signature(tmp_path)

        # node_modules and .venv contents must not leak into the signature
        assert "node_modules" not in sig.directories
        assert ".venv" not in sig.directories
        assert ".js" not in sig.file_extensions

    def test_missing_path_returns_empty_signature(self, tmp_path: Path) -> None:
        sig = compute_project_signature(tmp_path / "does-not-exist")

        assert sig.file_extensions == frozenset()
        assert sig.tooling_markers == frozenset()
        assert sig.directories == frozenset()

    def test_max_files_caps_walk(self, tmp_path: Path) -> None:
        for i in range(50):
            _touch(tmp_path / f"file_{i}.py")

        sig = compute_project_signature(tmp_path, max_files=5)

        # Even with the cap, we should still see the .py extension —
        # the cap bounds cost, not correctness for early-detected signals.
        assert ".py" in sig.file_extensions


class TestMatchesPattern:
    """Pattern-classification ladder for ProjectSignature.matches_pattern."""

    @pytest.fixture
    def py_signature(self) -> ProjectSignature:
        return ProjectSignature(
            cwd=Path("/fake"),
            file_extensions=frozenset({".py", ".md"}),
            tooling_markers=frozenset({"pyproject.toml"}),
            directories=frozenset({"src", "tests"}),
        )

    def test_extension_pattern_matches(self, py_signature: ProjectSignature) -> None:
        assert py_signature.matches_pattern("**/*.py") is True
        assert py_signature.matches_pattern("*.md") is True

    def test_extension_pattern_misses(self, py_signature: ProjectSignature) -> None:
        assert py_signature.matches_pattern("**/*.rs") is False
        assert py_signature.matches_pattern("*.tsx") is False

    def test_literal_filename_matches_tooling(
        self, py_signature: ProjectSignature
    ) -> None:
        assert py_signature.matches_pattern("pyproject.toml") is True

    def test_literal_filename_misses_when_absent(
        self, py_signature: ProjectSignature
    ) -> None:
        assert py_signature.matches_pattern("Cargo.toml") is False

    def test_directory_component_matches(self, py_signature: ProjectSignature) -> None:
        assert py_signature.matches_pattern("**/src/**") is True
        assert py_signature.matches_pattern("**/tests/**") is True

    def test_unclassifiable_pattern_is_permissive(
        self, py_signature: ProjectSignature
    ) -> None:
        # Patterns we cannot confidently negate default to True so we never
        # silently drop a skill the user might need.
        assert py_signature.matches_pattern("**/openapi.*") is True
        assert py_signature.matches_pattern("**/swagger.*") is True


class TestMatchesAny:
    """ProjectSignature.matches_any aggregation behavior."""

    @pytest.fixture
    def py_signature(self) -> ProjectSignature:
        return ProjectSignature(
            cwd=Path("/fake"),
            file_extensions=frozenset({".py"}),
            tooling_markers=frozenset(),
            directories=frozenset(),
        )

    def test_empty_patterns_returns_true(self, py_signature: ProjectSignature) -> None:
        # No file_patterns means no negative evidence — keep the skill.
        assert py_signature.matches_any([]) is True

    def test_any_match_returns_true(self, py_signature: ProjectSignature) -> None:
        assert py_signature.matches_any(["**/*.rs", "**/*.py"]) is True

    def test_no_match_returns_false(self, py_signature: ProjectSignature) -> None:
        assert py_signature.matches_any(["**/*.rs", "**/*.go"]) is False


class TestSkillRecommenderFilter:
    """Integration: SkillRecommender drops irrelevant skills when given a signature."""

    def _make_recommender(
        self, tmp_path: Path
    ) -> "object":  # SkillRecommender, deferred import
        from claude_ctx_py.skill_recommender import SkillRecommender

        # Use tmp_path as home so the recommender doesn't touch real state.
        recommender = SkillRecommender(home=tmp_path, enable_semantic=False)
        # Hand-stub the rule set so we control which skills have which
        # patterns — bypasses skill-index.json discovery entirely.
        recommender.rules = [
            {
                "trigger": {"file_patterns": ["**/*.rs", "Cargo.toml"]},
                "recommend": [
                    {
                        "skill": "rust-only-skill",
                        "confidence": 0.9,
                        "reason": "rust signal",
                    }
                ],
            },
            {
                "trigger": {"file_patterns": ["**/*.py"]},
                "recommend": [
                    {
                        "skill": "python-only-skill",
                        "confidence": 0.9,
                        "reason": "python signal",
                    }
                ],
            },
            {
                # An always-on skill that happens to also have a Rust pattern.
                # Should survive filtering regardless of the project.
                "trigger": {"file_patterns": ["**/*.rs"]},
                "recommend": [
                    {
                        "skill": "atomic-commits",
                        "confidence": 0.85,
                        "reason": "always-on with rust pattern",
                    }
                ],
            },
        ]
        return recommender

    def _make_context(self, files: list[str], file_types: set[str]) -> "object":
        from datetime import datetime

        from claude_ctx_py.intelligence import SessionContext

        return SessionContext(
            files_changed=files,
            file_types=file_types,
            directories={"src"},
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=True,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

    def test_signature_drops_unrelated_skills(self, tmp_path: Path) -> None:
        # Project layout has Python only — signature carries no .rs.
        _touch(tmp_path / "project" / "pyproject.toml")
        _touch(tmp_path / "project" / "src" / "app.py")
        signature = compute_project_signature(tmp_path / "project")

        recommender = self._make_recommender(tmp_path)
        # Both rules fire (Python and Rust files in changeset), so both
        # candidate skills enter the merged set; only the filter should
        # decide who survives.
        context = self._make_context(
            files=["src/app.py", "src/lib.rs"], file_types={".py", ".rs"}
        )

        recs = recommender.recommend_for_context(  # type: ignore[attr-defined]
            context, project_signature=signature
        )
        names = {r.skill_name for r in recs}

        assert "python-only-skill" in names
        assert "rust-only-skill" not in names

    def test_always_on_bypasses_filter(self, tmp_path: Path) -> None:
        # Python-only project — atomic-commits's stub patterns are Rust,
        # which would normally be filtered out for this signature.
        _touch(tmp_path / "project" / "src" / "app.py")
        signature = compute_project_signature(tmp_path / "project")

        recommender = self._make_recommender(tmp_path)
        # Use a Rust file in the changeset so the atomic-commits rule
        # fires, putting it in the candidate set for the filter to
        # potentially drop.
        context = self._make_context(files=["src/lib.rs"], file_types={".rs"})

        recs = recommender.recommend_for_context(  # type: ignore[attr-defined]
            context, project_signature=signature
        )
        names = {r.skill_name for r in recs}

        assert "atomic-commits" in names

    def test_no_signature_means_no_filtering(self, tmp_path: Path) -> None:
        recommender = self._make_recommender(tmp_path)
        context = self._make_context(files=["src/lib.rs"], file_types={".rs"})

        recs = recommender.recommend_for_context(context)  # type: ignore[attr-defined]
        names = {r.skill_name for r in recs}

        assert "rust-only-skill" in names
