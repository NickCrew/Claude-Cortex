"""Regression tests for the skill-suggest hook ranker.

The hook fires on every UserPromptSubmit. In a shared repo where multiple
agents collaborate, the git log and changed-files list are cross-task
pollution rather than per-agent intent — so the ranker requires the
user's own prompt to mention a skill keyword before surfacing anything.
These tests pin that contract.

The hook also dispatches on harness shape: Claude Code passes input via
env vars and expects plain stdout; Codex passes JSON on stdin and
expects a JSON ``hookSpecificOutput`` envelope. Both paths share the
same matching logic and multi-agent gate.
"""

from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from claude_ctx_py.hooks import skill_suggest

_MOD = "claude_ctx_py.hooks.skill_suggest"


@pytest.mark.unit
class TestMatchEntries:
    def test_zero_prompt_hits_returns_empty(self) -> None:
        """A short prompt with no keyword matches must produce no suggestions
        even when shared context (git/files) hits skill keywords."""
        entries = [
            {"name": "doc-health-audit", "keywords": ["doc", "audit"]},
            {"name": "doc-architecture-review", "keywords": ["doc"]},
        ]
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="yeah",
                files=["docs/foo.md"],
                entries=entries,
            )
        assert result == []

    def test_pure_context_match_is_dropped_in_mixed_case(self) -> None:
        """When the prompt matches some skills, context-only matches for
        unrelated skills must be filtered out."""
        entries = [
            {"name": "test-driven-development", "keywords": ["test"]},
            {"name": "doc-quality-review", "keywords": ["doc"]},
        ]
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="write a test for this",
                files=["docs/foo.md"],
                entries=entries,
            )
        names = [entry["name"] for _, entry in result]
        assert names == ["test-driven-development"]

    def test_prompt_match_outranks_context_among_kept_entries(self) -> None:
        """Among prompt-matched entries, prompt hits weigh PROMPT_HIT_WEIGHT
        times more than context hits."""
        entries = [
            {"name": "a-test-skill", "keywords": ["test"]},  # prompt only
            {"name": "z-test-skill", "keywords": ["test", "doc"]},  # prompt + context
        ]
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="test",
                files=["docs/foo.md"],
                entries=entries,
            )
        names = [entry["name"] for _, entry in result]
        # z-test-skill has the same prompt_hits but an extra context_hit
        # via "doc" matching context_text from .md files
        assert names == ["z-test-skill", "a-test-skill"]

    def test_alphabetical_tiebreak(self) -> None:
        """Equal-score entries sort alphabetically by name."""
        entries = [
            {"name": "z-skill", "keywords": ["review"]},
            {"name": "a-skill", "keywords": ["review"]},
            {"name": "m-skill", "keywords": ["review"]},
        ]
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="please review this",
                files=[],
                entries=entries,
            )
        names = [entry["name"] for _, entry in result]
        assert names == ["a-skill", "m-skill", "z-skill"]

    def test_max_results_cap(self) -> None:
        """Only the top max_results entries are returned."""
        entries = [
            {"name": f"skill-{i:02d}", "keywords": ["review"]} for i in range(10)
        ]
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="review",
                files=[],
                entries=entries,
                max_results=3,
            )
        assert len(result) == 3

    def test_empty_entries_returns_empty(self) -> None:
        """No index → no suggestions, regardless of prompt or context."""
        with patch(f"{_MOD}.get_git_context", return_value=set()):
            result = skill_suggest.match_entries(
                prompt="anything goes here",
                files=["a.py", "b.tsx"],
                entries=[],
            )
        assert result == []


@pytest.mark.unit
class TestMainIntegration:
    """End-to-end tests for the hook's main() — verifies that Layer 2
    (the recommender) is also gated when Layer 1 finds no prompt match."""

    def test_main_silenced_on_zero_prompt_hits(self, capsys, monkeypatch) -> None:
        """A short prompt with no keyword match must produce no stdout
        even if the recommender would otherwise fire on shared context."""
        monkeypatch.setenv("CLAUDE_HOOK_PROMPT", "yeah")
        monkeypatch.setenv("CLAUDE_CHANGED_FILES", "docs/foo.md:src/auth.py")
        monkeypatch.setenv("CORTEX_SKIP_RECOMMENDER", "1")
        with patch(
            f"{_MOD}.load_entries",
            return_value=[{"name": "doc-foo", "keywords": ["doc"]}],
        ), patch(f"{_MOD}.get_git_context", return_value=set()):
            exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out == ""

    def test_main_emits_when_prompt_matches(self, capsys, monkeypatch) -> None:
        """When the prompt hits a skill keyword, suggestions are emitted."""
        monkeypatch.setenv("CLAUDE_HOOK_PROMPT", "please review this")
        monkeypatch.setenv("CLAUDE_CHANGED_FILES", "")
        monkeypatch.setenv("CORTEX_SKIP_RECOMMENDER", "1")
        with patch(
            f"{_MOD}.load_entries",
            return_value=[{"name": "code-review", "keywords": ["review"]}],
        ), patch(f"{_MOD}.get_git_context", return_value=set()):
            exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "code-review" in captured.out


def _codex_stdin(payload: dict) -> io.StringIO:
    """Build a fake Codex hook stdin from a payload dict, with isatty False."""
    stream = io.StringIO(json.dumps(payload))
    stream.isatty = lambda: False  # type: ignore[method-assign]
    return stream


@pytest.mark.unit
class TestCodexDispatch:
    """Codex passes JSON on stdin; output must be a hookSpecificOutput envelope."""

    def test_codex_json_input_emits_hookSpecificOutput(
        self, capsys, monkeypatch
    ) -> None:
        """Codex prompt with a real keyword → JSON envelope on stdout."""
        monkeypatch.delenv("CLAUDE_HOOK_PROMPT", raising=False)
        monkeypatch.delenv("CLAUDE_CHANGED_FILES", raising=False)
        monkeypatch.setenv("CORTEX_SKIP_RECOMMENDER", "1")
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "s1",
            "cwd": "/tmp",
            "model": "gpt-5",
            "prompt": "please review this code",
        }
        monkeypatch.setattr("sys.stdin", _codex_stdin(payload))
        with patch(
            f"{_MOD}.load_entries",
            return_value=[{"name": "code-review", "keywords": ["review"]}],
        ), patch(f"{_MOD}.get_git_context", return_value=set()), patch(
            f"{_MOD}._git_changed_files", return_value=[]
        ):
            exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0

        # Output must be valid JSON in the Codex contract shape
        parsed = json.loads(captured.out)
        assert parsed["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        assert "code-review" in parsed["hookSpecificOutput"]["additionalContext"]

    def test_codex_silenced_on_zero_prompt_hits(self, capsys, monkeypatch) -> None:
        """Multi-agent gate applies to Codex too: 'yeah' → empty stdout."""
        monkeypatch.delenv("CLAUDE_HOOK_PROMPT", raising=False)
        monkeypatch.delenv("CLAUDE_CHANGED_FILES", raising=False)
        monkeypatch.setenv("CORTEX_SKIP_RECOMMENDER", "1")
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "s1",
            "cwd": "/tmp",
            "model": "gpt-5",
            "prompt": "yeah",
        }
        monkeypatch.setattr("sys.stdin", _codex_stdin(payload))
        with patch(
            f"{_MOD}.load_entries",
            return_value=[{"name": "doc-foo", "keywords": ["doc"]}],
        ), patch(f"{_MOD}.get_git_context", return_value=set()), patch(
            f"{_MOD}._git_changed_files", return_value=["docs/foo.md"]
        ):
            exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out == ""

    def test_no_input_returns_silently(self, capsys, monkeypatch) -> None:
        """Manual invocation with no env vars and no stdin JSON → exit 0,
        no output. Avoids confusing terminal behavior when developers run
        `cortex hooks skill-suggest` directly without input."""
        monkeypatch.delenv("CLAUDE_HOOK_PROMPT", raising=False)
        monkeypatch.delenv("CLAUDE_CHANGED_FILES", raising=False)
        # stdin is a TTY-like object: no payload available
        empty_stream = io.StringIO("")
        empty_stream.isatty = lambda: True  # type: ignore[method-assign]
        monkeypatch.setattr("sys.stdin", empty_stream)
        exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out == ""

    def test_codex_malformed_json_falls_through_silently(
        self, capsys, monkeypatch
    ) -> None:
        """Garbage on stdin without Claude env vars → no crash, no output."""
        monkeypatch.delenv("CLAUDE_HOOK_PROMPT", raising=False)
        bad_stream = io.StringIO("not-json-at-all")
        bad_stream.isatty = lambda: False  # type: ignore[method-assign]
        monkeypatch.setattr("sys.stdin", bad_stream)
        exit_code = skill_suggest.main()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert captured.out == ""
