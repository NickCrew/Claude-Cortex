"""Unit tests for claude_ctx_py.core.output_styles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claude_ctx_py.core import output_styles as os_mod

pytestmark = [pytest.mark.unit, pytest.mark.core]

_STYLE_BODY = """\
---
name: {name}
description: {desc}
---

# Output Style: {name}

Body text.
"""


@pytest.fixture
def sandbox(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point cortex root + claude dir at an isolated tmp tree.

    Returns the repo's ``output-styles`` source dir so tests can add styles.
    """
    repo = tmp_path / "repo"
    source = repo / "output-styles"
    source.mkdir(parents=True)
    (repo / "agents").mkdir()  # so _resolve_cortex_root recognizes a repo
    (repo / "pyproject.toml").write_text("", encoding="utf-8")

    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setenv("CORTEX_ROOT", str(repo))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("CORTEX_SCOPE", raising=False)
    return source


def _add_style(source: Path, slug: str, name: str, desc: str = "A style") -> Path:
    path = source / f"{slug}.md"
    path.write_text(_STYLE_BODY.format(name=name, desc=desc), encoding="utf-8")
    return path


def _settings(home_claude: Path) -> dict:
    return json.loads((home_claude / "settings.json").read_text(encoding="utf-8"))


class TestDiscovery:
    def test_parses_front_matter_and_state(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering", "Explains the why")

        styles = os_mod.list_output_styles()

        assert len(styles) == 1
        style = styles[0]
        assert style.slug == "engineering"
        assert style.name == "Engineering"
        assert style.description == "Explains the why"
        assert style.installed is False
        assert style.active is False

    def test_empty_when_no_source_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        empty = tmp_path / "norepo"
        empty.mkdir()
        monkeypatch.setenv("CORTEX_ROOT", str(empty))
        monkeypatch.setenv("HOME", str(tmp_path / "h"))
        monkeypatch.delenv("CORTEX_SCOPE", raising=False)
        assert os_mod.list_output_styles() == []


class TestInstall:
    def test_install_creates_symlink_to_source(self, sandbox: Path) -> None:
        src = _add_style(sandbox, "engineering", "Engineering")

        code, _ = os_mod.install_output_style("engineering")

        assert code == 0
        link = os_mod._target_dir() / "engineering.md"
        assert link.is_symlink()
        assert link.resolve() == src.resolve()
        assert os_mod.list_output_styles()[0].installed is True

    def test_install_is_idempotent(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        assert os_mod.install_output_style("engineering")[0] == 0
        assert os_mod.install_output_style("engineering")[0] == 0
        link = os_mod._target_dir() / "engineering.md"
        assert link.is_symlink()

    def test_install_missing_style_errors(self, sandbox: Path) -> None:
        code, msg = os_mod.install_output_style("nope")
        assert code == 1
        assert "not found" in msg

    def test_uninstall_removes_symlink(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        os_mod.install_output_style("engineering")

        code, _ = os_mod.uninstall_output_style("engineering")

        assert code == 0
        assert not (os_mod._target_dir() / "engineering.md").exists()

    def test_uninstall_not_installed_errors(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        code, msg = os_mod.uninstall_output_style("engineering")
        assert code == 1
        assert "not installed" in msg


class TestActivate:
    def test_activate_writes_flat_name_and_autoinstalls(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")

        code, _ = os_mod.activate_output_style("engineering")

        assert code == 0
        # auto-installed so Claude Code can find it
        assert (os_mod._target_dir() / "engineering.md").is_symlink()
        # flat string equal to the front-matter name
        settings = _settings(os_mod._resolve_claude_dir())
        assert settings["outputStyle"] == "Engineering"
        assert os_mod.get_active_output_style() == "Engineering"
        assert os_mod.list_output_styles()[0].active is True

    def test_activate_preserves_other_settings_keys(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        claude_dir = os_mod._resolve_claude_dir()
        claude_dir.mkdir(parents=True, exist_ok=True)
        (claude_dir / "settings.json").write_text(
            json.dumps({"statusLine": "cortex statusline", "model": "opus"}),
            encoding="utf-8",
        )

        os_mod.activate_output_style("engineering")

        settings = _settings(claude_dir)
        assert settings["outputStyle"] == "Engineering"
        assert settings["statusLine"] == "cortex statusline"
        assert settings["model"] == "opus"

    def test_deactivate_resets_to_default(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        os_mod.activate_output_style("engineering")

        code, _ = os_mod.deactivate_output_style()

        assert code == 0
        assert os_mod.get_active_output_style() == "default"

    def test_uninstall_active_style_resets_to_default(self, sandbox: Path) -> None:
        _add_style(sandbox, "engineering", "Engineering")
        os_mod.activate_output_style("engineering")
        assert os_mod.get_active_output_style() == "Engineering"

        os_mod.uninstall_output_style("engineering")

        assert os_mod.get_active_output_style() == "default"


class TestCheckActionGating:
    """The per-view binding gating that lets shared keys (i/u/space/d) resolve.

    Tested against the unbound method with a stub so we don't launch the app.
    """

    @staticmethod
    def _check(view: str, action: str) -> object:
        from types import SimpleNamespace

        from claude_ctx_py.tui.main import AgentTUI

        stub = SimpleNamespace(current_view=view)
        return AgentTUI.check_action(stub, action, ())  # type: ignore[arg-type]

    def test_unscoped_actions_always_enabled(self) -> None:
        for view in ("agents", "output_styles", "assets", "settings"):
            assert self._check(view, "refresh") is True
            assert self._check(view, "view_output_styles") is True

    def test_install_keys_resolve_to_owning_view(self) -> None:
        # `i` is bound to asset_install, setting_install, watch_adjust_interval,
        # and output_style_install — exactly one is enabled per view.
        assert self._check("assets", "asset_install") is True
        assert self._check("settings", "asset_install") is False
        assert self._check("output_styles", "asset_install") is False

        # Settings `i` now resolves correctly (was a latent shadow bug).
        assert self._check("settings", "setting_install") is True
        assert self._check("assets", "setting_install") is False

        assert self._check("output_styles", "output_style_install") is True
        assert self._check("assets", "output_style_install") is False

    def test_multiview_actions_only_disabled_in_output_styles(self) -> None:
        # toggle (space) and docs_context (d) stay enabled everywhere except the
        # output_styles view, where they fall through to the style actions.
        assert self._check("agents", "toggle") is True
        assert self._check("rules", "toggle") is True
        assert self._check("output_styles", "toggle") is False

        assert self._check("skills", "docs_context") is True
        assert self._check("output_styles", "docs_context") is False

    def test_output_style_actions_scoped(self) -> None:
        for action in (
            "output_style_activate",
            "output_style_deactivate",
            "output_style_uninstall",
        ):
            assert self._check("output_styles", action) is True
            assert self._check("agents", action) is False
