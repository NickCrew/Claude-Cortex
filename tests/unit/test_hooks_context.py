"""Unit tests for the shared hook helpers in ``claude_ctx_py.hooks._context``.

These helpers moved out of the retired ``skill_suggest`` hook; the tests
that used to cover them (via that hook's ``match_entries``/``main``) went
with it, so they are re-established here against the shared module that
``agent_suggest`` and the validators now depend on.
"""

from __future__ import annotations

import io

import pytest

from claude_ctx_py.hooks import _context


@pytest.mark.unit
class TestSplitChangedFiles:
    def test_empty_string_returns_empty_list(self) -> None:
        assert _context.split_changed_files("") == []

    def test_colon_separated_paths_are_split_and_stripped(self) -> None:
        assert _context.split_changed_files("a.py: b.py :c.py") == [
            "a.py",
            "b.py",
            "c.py",
        ]


@pytest.mark.unit
class TestExtractFileContext:
    def test_test_file_yields_testing_keywords(self) -> None:
        kw = _context.extract_file_context(["tests/test_widget.py"])
        assert {"test", "pytest", "python"} <= kw

    def test_react_component_yields_frontend_keywords(self) -> None:
        kw = _context.extract_file_context(["src/components/Button.tsx"])
        assert {"react", "frontend", "component", "typescript"} <= kw

    def test_unknown_path_yields_no_false_keywords(self) -> None:
        # A bare, extensionless, short-stem path should not invent keywords.
        assert _context.extract_file_context(["x"]) == set()


@pytest.mark.unit
class TestReadCodexStdin:
    def test_tty_stdin_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _TTY(io.StringIO):
            def isatty(self) -> bool:
                return True

        monkeypatch.setattr("sys.stdin", _TTY())
        assert _context._read_codex_stdin() is None

    def test_valid_payload_is_parsed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        payload = '{"hook_event_name": "UserPromptSubmit", "prompt": "hi"}'
        stream = io.StringIO(payload)
        monkeypatch.setattr(stream, "isatty", lambda: False, raising=False)
        monkeypatch.setattr("sys.stdin", stream)
        result = _context._read_codex_stdin()
        assert result is not None
        assert result["prompt"] == "hi"

    def test_malformed_json_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        stream = io.StringIO("{not json")
        monkeypatch.setattr(stream, "isatty", lambda: False, raising=False)
        monkeypatch.setattr("sys.stdin", stream)
        assert _context._read_codex_stdin() is None

    def test_json_without_event_name_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        stream = io.StringIO('{"prompt": "hi"}')
        monkeypatch.setattr(stream, "isatty", lambda: False, raising=False)
        monkeypatch.setattr("sys.stdin", stream)
        assert _context._read_codex_stdin() is None
