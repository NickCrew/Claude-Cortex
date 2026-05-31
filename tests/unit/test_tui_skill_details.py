import asyncio
from pathlib import Path
from typing import Any, Dict, List

import pytest

from claude_ctx_py.tui.main import AgentTUI
from claude_ctx_py.tui.widgets import AdaptiveFooter, ShortcutDef, VIEW_SHORTCUTS


pytestmark = [pytest.mark.unit, pytest.mark.tui]


def _bare_app() -> AgentTUI:
    return AgentTUI()


def test_show_selected_skill_definition_opens_skill_file(tmp_path: Path) -> None:
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text(
        "---\nname: Example Skill\n---\n\nBody text\n", encoding="utf-8"
    )

    app = _bare_app()
    shown: List[tuple[str, str]] = []

    async def show_text_dialog(title: str, body: str) -> None:
        shown.append((title, body))

    app._selected_skill = lambda: {  # type: ignore[method-assign]
        "name": "Example Skill",
        "path": str(skill_file),
    }
    app._show_text_dialog = show_text_dialog  # type: ignore[method-assign]
    app.refresh_status_bar = lambda: None  # type: ignore[method-assign]
    app.status_message = ""

    asyncio.run(app._show_selected_skill_definition())

    assert shown == [
        ("Example Skill Definition", "---\nname: Example Skill\n---\n\nBody text\n")
    ]
    assert app.status_message == "Viewing skill: Example Skill"


def test_show_selected_skill_definition_accepts_skill_directory(
    tmp_path: Path,
) -> None:
    skill_dir = tmp_path / "example-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("Directory body\n", encoding="utf-8")

    app = _bare_app()
    shown: List[tuple[str, str]] = []

    async def show_text_dialog(title: str, body: str) -> None:
        shown.append((title, body))

    app._selected_skill = lambda: {  # type: ignore[method-assign]
        "name": "Example Skill",
        "path": str(skill_dir),
    }
    app._show_text_dialog = show_text_dialog  # type: ignore[method-assign]
    app.refresh_status_bar = lambda: None  # type: ignore[method-assign]

    asyncio.run(app._show_selected_skill_definition())

    assert shown == [("Example Skill Definition", "Directory body\n")]


def test_show_selected_skill_definition_warns_when_nothing_selected() -> None:
    app = _bare_app()
    notices: List[Dict[str, Any]] = []

    app._selected_skill = lambda: None  # type: ignore[method-assign]
    app.notify = (  # type: ignore[method-assign]
        lambda message, **kwargs: notices.append({"message": message, **kwargs})
    )

    asyncio.run(app._show_selected_skill_definition())

    assert notices == [
        {
            "message": "Select a skill to view details",
            "severity": "warning",
            "timeout": 2,
        }
    ]


def test_show_selected_skill_definition_warns_when_path_is_missing() -> None:
    app = _bare_app()
    notices: List[Dict[str, Any]] = []

    app._selected_skill = lambda: {"name": "Broken Skill"}  # type: ignore[method-assign]
    app.notify = (  # type: ignore[method-assign]
        lambda message, **kwargs: notices.append({"message": message, **kwargs})
    )

    asyncio.run(app._show_selected_skill_definition())

    assert notices == [
        {
            "message": "No source file available for this skill",
            "severity": "warning",
            "timeout": 2,
        }
    ]


def test_show_selected_skill_definition_reports_file_read_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("body", encoding="utf-8")

    app = _bare_app()
    notices: List[Dict[str, Any]] = []

    def fail_read_text(self: Path, *, encoding: str) -> str:
        raise OSError("cannot read")

    app._selected_skill = lambda: {  # type: ignore[method-assign]
        "name": "Unreadable Skill",
        "path": str(skill_file),
    }
    app.notify = (  # type: ignore[method-assign]
        lambda message, **kwargs: notices.append({"message": message, **kwargs})
    )
    monkeypatch.setattr(Path, "read_text", fail_read_text)

    asyncio.run(app._show_selected_skill_definition())

    assert notices == [
        {
            "message": "Failed to load Unreadable Skill: cannot read",
            "severity": "error",
            "timeout": 3,
        }
    ]


def test_selected_skill_in_llm_view_skips_provider_header() -> None:
    app = _bare_app()
    app.__dict__["_reactive_current_view"] = "codex_skills"
    app.active_provider = "codex"
    app.provider_native_skills = [
        {"name": "Native Skill", "slug": "native-skill", "path": "native/SKILL.md"}
    ]
    app.skills = [
        {"name": "Claude Skill", "slug": "claude-skill", "path": "claude/SKILL.md"}
    ]

    app._table_cursor_index = lambda: 0  # type: ignore[method-assign]
    assert app._selected_skill() is None

    app._table_cursor_index = lambda: 1  # type: ignore[method-assign]
    assert app._selected_skill() == {
        "name": "Native Skill",
        "slug": "native-skill",
        "path": "native/SKILL.md",
        "source": "codex",
    }

    app._table_cursor_index = lambda: 2  # type: ignore[method-assign]
    assert app._selected_skill() == {
        "name": "Claude Skill",
        "slug": "claude-skill",
        "path": "claude/SKILL.md",
        "source": "claude",
    }


def test_copy_definition_supports_llm_skill_view() -> None:
    app = _bare_app()
    calls: List[bool] = []

    async def copy_skill_definition() -> None:
        calls.append(True)

    app.__dict__["_reactive_current_view"] = "codex_skills"
    app._copy_skill_definition = copy_skill_definition  # type: ignore[method-assign]

    asyncio.run(app.action_copy_definition())

    assert calls == [True]


@pytest.mark.parametrize(
    ("view", "action"),
    [
        ("assets", "asset_details"),
        ("memory", "memory_view_note"),
        ("settings", "setting_view_file"),
    ],
)
def test_view_item_dispatches_specialized_view_actions(view: str, action: str) -> None:
    app = _bare_app()
    calls: List[str] = []

    async def run_action(action_name: str) -> None:
        calls.append(action_name)

    app.__dict__["_reactive_current_view"] = view
    app.run_action = run_action  # type: ignore[method-assign]

    asyncio.run(app.action_view_item())

    assert calls == [action]


@pytest.mark.parametrize("view", ["skills", "codex_skills"])
def test_view_item_opens_skill_details_in_skill_views(view: str) -> None:
    app = _bare_app()
    calls: List[bool] = []

    async def show_selected_skill_definition() -> None:
        return None

    def run_worker(worker: Any, *, exclusive: bool = False) -> None:
        calls.append(exclusive)
        worker.close()

    app.__dict__["_reactive_current_view"] = view
    app._show_selected_skill_definition = (  # type: ignore[method-assign]
        show_selected_skill_definition
    )
    app.run_worker = run_worker  # type: ignore[method-assign]

    asyncio.run(app.action_view_item())

    assert calls == [True]


def test_enter_bindings_route_through_view_item() -> None:
    enter_actions = [
        binding.action for binding in AgentTUI.BINDINGS if binding.key == "enter"
    ]

    assert len(enter_actions) == 1
    assert set(enter_actions) == {"view_item"}


def test_adaptive_footer_resolves_skill_shortcuts_from_global_mapping() -> None:
    footer = AdaptiveFooter()

    assert footer._get_view_shortcuts("skills")[:4] == [
        ("Enter", "View"),
        ("v", "Validate"),
        ("m", "Metrics"),
        ("d", "Docs"),
    ]
    assert footer._get_view_shortcuts("codex_skills") == [
        ("Enter", "View"),
        ("l", "Link"),
        ("Tab", "Provider"),
    ]


def test_adaptive_footer_keeps_fallback_shortcuts() -> None:
    footer = AdaptiveFooter()

    assert footer._get_view_shortcuts("worktrees") == [
        ("^n", "New"),
        ("^o", "Open"),
        ("^w", "Remove"),
        ("^k", "Prune"),
        ("B", "Base Dir"),
    ]
    assert footer._get_view_shortcuts("unknown") == []


def test_adaptive_footer_sorts_global_shortcuts_by_priority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    footer = AdaptiveFooter()
    monkeypatch.setitem(
        VIEW_SHORTCUTS,
        "out_of_order",
        [
            ShortcutDef("z", "Last", priority=30),
            ShortcutDef("a", "First", priority=10),
            ShortcutDef("m", "Middle", priority=20),
        ],
    )

    assert footer._get_view_shortcuts("out_of_order") == [
        ("a", "First"),
        ("m", "Middle"),
        ("z", "Last"),
    ]
