"""Unit tests for claude_ctx_py.git.validate."""
from __future__ import annotations

import pytest

from claude_ctx_py.git.validate import check_atomicity, validate_commit_message


@pytest.mark.unit
class TestValidateCommitMessage:
    def test_valid_simple(self):
        assert validate_commit_message("fix: prevent race condition") == []

    def test_valid_with_scope(self):
        assert validate_commit_message("feat(auth): add login flow") == []

    def test_valid_breaking(self):
        assert validate_commit_message("feat!: drop Python 3.8") == []

    def test_invalid_format(self):
        warns = validate_commit_message("Fixed the bug")
        assert any("conventional" in w.lower() for w in warns)

    def test_unknown_type(self):
        warns = validate_commit_message("yolo: whatever")
        assert any("unknown" in w.lower() for w in warns)

    def test_empty_message(self):
        warns = validate_commit_message("")
        assert any("empty" in w.lower() for w in warns)

    def test_long_subject(self):
        long = "fix: " + "a" * 80
        warns = validate_commit_message(long)
        assert any("chars" in w or "subject" in w.lower() for w in warns)

    def test_known_types_pass(self):
        for t in ("feat", "fix", "docs", "refactor", "perf", "test", "chore"):
            assert validate_commit_message(f"{t}: do something") == []


@pytest.mark.unit
class TestCheckAtomicity:
    def test_clean_commit(self):
        assert check_atomicity("fix: single change", ["src/foo.py"]) == []

    def test_message_with_and(self):
        warns = check_atomicity("fix: auth and update styles", ["a.py"])
        assert any("and" in w.lower() for w in warns)

    def test_message_with_also(self):
        warns = check_atomicity("feat: add login also fix signup", ["a.py"])
        assert any("also" in w.lower() for w in warns)

    def test_high_file_count_for_fix(self):
        files = [f"file{i}.py" for i in range(8)]
        warns = check_atomicity("fix: thing", files)
        assert any("exceeds" in w.lower() for w in warns)

    def test_acceptable_file_count_for_refactor(self):
        files = [f"src/file{i}.py" for i in range(15)]
        warns = check_atomicity("refactor: rename module", files)
        # 15 < 20 threshold for refactor, but may warn on directory spread
        file_warns = [w for w in warns if "exceeds" in w.lower()]
        assert file_warns == []

    def test_directory_spread(self):
        files = ["src/a.py", "docs/b.md", "tests/c.py"]
        warns = check_atomicity("feat: big change", files)
        assert any("directories" in w.lower() for w in warns)

    def test_single_dir_no_warn(self):
        files = ["src/a.py", "src/b.py"]
        warns = check_atomicity("feat: change", files)
        dir_warns = [w for w in warns if "directories" in w.lower()]
        assert dir_warns == []
