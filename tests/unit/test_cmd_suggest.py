"""Unit tests for claude_ctx_py.cmd_suggest (argument parsing and handler dispatch)."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from claude_ctx_py.cli import build_parser

_CMD = "claude_ctx_py.cmd_suggest"


def _parse(args: list[str]):
    return build_parser().parse_args(args)


# ── Argument Parsing ─────────────────────────────────────────────────


@pytest.mark.unit
class TestSuggestDefaultParsing:
    def test_no_flags(self):
        ns = _parse(["suggest"])
        assert ns.command == "suggest"
        assert ns.skills is False
        assert ns.agents is False
        assert ns.activate is False

    def test_skills_only(self):
        ns = _parse(["suggest", "--skills"])
        assert ns.skills is True
        assert ns.agents is False

    def test_agents_only(self):
        ns = _parse(["suggest", "--agents"])
        assert ns.agents is True
        assert ns.skills is False

    def test_project_dir(self):
        ns = _parse(["suggest", "--project-dir", "/tmp/proj"])
        assert ns.suggest_project_dir == "/tmp/proj"

    def test_project_dir_default(self):
        ns = _parse(["suggest"])
        assert ns.suggest_project_dir == "."


@pytest.mark.unit
class TestSuggestTextParsing:
    def test_text_mode(self):
        ns = _parse(["suggest", "--text", "kubernetes deployment"])
        assert ns.suggest_text == "kubernetes deployment"

    def test_no_text(self):
        ns = _parse(["suggest"])
        assert ns.suggest_text is None


@pytest.mark.unit
class TestSuggestActivateParsing:
    def test_activate(self):
        ns = _parse(["suggest", "--activate"])
        assert ns.activate is True


@pytest.mark.unit
class TestSuggestWatchParsing:
    def test_watch(self):
        ns = _parse(["suggest", "--watch"])
        assert ns.watch is True

    def test_watch_with_threshold(self):
        ns = _parse(["suggest", "--watch", "--threshold", "0.8"])
        assert ns.threshold == 0.8

    def test_watch_with_interval(self):
        ns = _parse(["suggest", "--watch", "--interval", "5.0"])
        assert ns.interval == 5.0

    def test_watch_daemon(self):
        ns = _parse(["suggest", "--watch", "--daemon"])
        assert ns.watch is True
        assert ns.daemon is True

    def test_watch_status(self):
        ns = _parse(["suggest", "--status"])
        assert ns.status is True

    def test_watch_stop(self):
        ns = _parse(["suggest", "--stop"])
        assert ns.stop is True

    def test_watch_dir(self):
        ns = _parse(["suggest", "--watch", "--dir", "/tmp/a", "--dir", "/tmp/b"])
        assert ns.watch_dirs == ["/tmp/a", "/tmp/b"]


@pytest.mark.unit
class TestSuggestExportParsing:
    def test_export_with_file(self):
        ns = _parse(["suggest", "--export", "out.json"])
        assert ns.export_file == "out.json"

    def test_export_default_filename(self):
        ns = _parse(["suggest", "--export"])
        assert ns.export_file == "suggestions.json"

    def test_no_export(self):
        ns = _parse(["suggest"])
        assert ns.export_file is None


@pytest.mark.unit
class TestSuggestReviewParsing:
    def test_review(self):
        ns = _parse(["suggest", "--review"])
        assert ns.review is True

    def test_review_dry_run(self):
        ns = _parse(["suggest", "--review", "--dry-run"])
        assert ns.review is True
        assert ns.dry_run is True

    def test_review_context(self):
        ns = _parse(["suggest", "--review", "-c", "debug", "-c", "feature"])
        assert ns.review_contexts == ["debug", "feature"]


# ── Handler Dispatch ─────────────────────────────────────────────────


@pytest.mark.unit
class TestSuggestDispatch:
    @patch(f"{_CMD}.suggest_default", return_value=0)
    def test_default_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with(
            skills_only=False,
            agents_only=False,
            project_dir=".",
        )

    @patch(f"{_CMD}.suggest_default", return_value=0)
    def test_skills_only_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--skills"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with(
            skills_only=True,
            agents_only=False,
            project_dir=".",
        )

    @patch(f"{_CMD}.suggest_text", return_value=0)
    def test_text_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--text", "some text"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with("some text")

    @patch(f"{_CMD}.suggest_activate", return_value=0)
    def test_activate_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--activate"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once()

    @patch(f"{_CMD}.suggest_watch", return_value=0)
    def test_watch_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--watch"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once()

    @patch(f"{_CMD}.suggest_export", return_value=0)
    def test_export_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--export", "out.json"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with("out.json")

    @patch(f"{_CMD}.suggest_review", return_value=0)
    def test_review_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--review"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with(
            dry_run=False,
            extra_context=None,
        )

    @patch(f"{_CMD}.suggest_review", return_value=0)
    def test_review_dry_run_dispatches(self, mock_fn: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--review", "--dry-run"])
        _handle_suggest_command(args)
        mock_fn.assert_called_once_with(
            dry_run=True,
            extra_context=None,
        )


# ── Priority Ordering ────────────────────────────────────────────────


@pytest.mark.unit
class TestSuggestDispatchPriority:
    """--text takes priority over --activate, --review, etc."""

    @patch(f"{_CMD}.suggest_text", return_value=0)
    @patch(f"{_CMD}.suggest_activate", return_value=0)
    def test_text_beats_activate(self, mock_activate: MagicMock, mock_text: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--text", "foo", "--activate"])
        _handle_suggest_command(args)
        mock_text.assert_called_once()
        mock_activate.assert_not_called()

    @patch(f"{_CMD}.suggest_watch", return_value=0)
    @patch(f"{_CMD}.suggest_review", return_value=0)
    def test_watch_beats_review(self, mock_review: MagicMock, mock_watch: MagicMock) -> None:
        from claude_ctx_py.cli import _handle_suggest_command
        args = _parse(["suggest", "--watch", "--review"])
        _handle_suggest_command(args)
        mock_watch.assert_called_once()
        mock_review.assert_not_called()
