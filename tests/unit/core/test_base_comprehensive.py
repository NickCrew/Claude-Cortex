"""Comprehensive tests for core.base module."""

from __future__ import annotations

import builtins
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from unittest import mock

import pytest
import yaml

from claude_ctx_py.core import base


# --------------------------------------------------------------------------- fixtures

@pytest.fixture(autouse=True)
def _tmp_claude_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))
    return claude_dir


# --------------------------------------------------------------------------- _resolve_claude_dir

def test_resolve_claude_dir_prefers_env_overrides(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    plugin = tmp_path / "plugin-home"
    plugin.mkdir()
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin))
    result_plugin = base._resolve_claude_dir()
    assert result_plugin == plugin


def test_resolve_claude_dir_falls_back_to_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    home_override = tmp_path / "home"
    result = base._resolve_claude_dir(home_override)
    assert result == home_override / ".cortex"



def test_resolve_claude_dir_scope_global_ignores_plugin_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    home_override = tmp_path / "home"
    monkeypatch.setenv("CORTEX_SCOPE", "global")
    result = base._resolve_claude_dir(home_override)
    assert result == home_override / ".cortex"


def test_resolve_claude_dir_scope_project_uses_nearest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    project = tmp_path / "project"
    project.mkdir()
    (project / ".claude").mkdir()
    child = project / "child"
    child.mkdir()
    monkeypatch.setenv("CORTEX_SCOPE", "project")
    result = base._resolve_claude_dir(cwd=child)
    assert result == project / ".claude"


# --------------------------------------------------------------------------- path + inactive helpers

def test_init_slug_for_path_generates_stable_slug(tmp_path: Path):
    target = tmp_path / "Proj Ünicode!"
    target.mkdir()
    slug1 = base._init_slug_for_path(target)
    slug2 = base._init_slug_for_path(target)
    assert slug1 == slug2
    assert slug1.startswith("proj-unicode")
    assert len(slug1.split("-")[-1]) == 12  # sha1 prefix length


def test_inactive_helpers_produce_aliases(tmp_path: Path):
    claude_dir = tmp_path / ".cortex"
    canonical = base._inactive_category_dir(claude_dir, "agents")
    candidates = base._inactive_dir_candidates(claude_dir, "agents")
    assert canonical in candidates
    assert any("agents-disabled" in str(p) for p in candidates)
    ensured = base._ensure_inactive_category_dir(claude_dir, "agents")
    assert ensured.is_dir()


# --------------------------------------------------------------------------- front matter parsing

def test_extract_front_matter_and_tokenization():
    text = "---\nname: alpha\nnested:\n  key: value\n---\nbody"
    front = base._extract_front_matter(text)
    assert "name: alpha" in front
    tokens = base._tokenize_front_matter(front.splitlines())
    assert tokens == [(0, "name: alpha"), (0, "nested:"), (2, "key: value")]


def test_extract_values_and_scalar_from_paths():
    lines = [
        "name: test",
        "metadata:",
        "  category: core",
        "  items:",
        "    - one",
        "    - two",
    ]
    tokens = base._tokenize_front_matter(lines)
    values = base._extract_values_from_paths(tokens, (("metadata", "items"),))
    assert values == ["one", "two"]
    scalar = base._extract_scalar_from_paths(tokens, (("metadata", "category"),))
    assert scalar == "core"


def test_extract_values_handles_inline_lists():
    tokens = base._tokenize_front_matter(["metadata:", "  items: [a, b, c]"])
    values = base._extract_values_from_paths(tokens, (("metadata", "items"),))
    assert values == ["a", "b", "c"]


# --------------------------------------------------------------------------- YAML + validation helpers

def test_load_yaml_and_dict(tmp_path: Path):
    good = tmp_path / "data.yaml"
    good.write_text("a: 1\nb: 2\n", encoding="utf-8")
    ok, data, msg = base._load_yaml(good)
    assert ok and data == {"a": 1, "b": 2} and msg == ""

    ok_dict, dict_data, msg_dict = base._load_yaml_dict(good)
    assert ok_dict and dict_data["a"] == 1 and msg_dict == ""

    bad = tmp_path / "bad.yaml"
    bad.write_text("- not-a-map\n", encoding="utf-8")
    ok_dict2, dict_data2, msg2 = base._load_yaml_dict(bad)
    assert not ok_dict2
    assert "mapping" in msg2


def test_flatten_mixed_and_ensure_list_messages():
    assert base._flatten_mixed(None) == []
    assert base._flatten_mixed(" one ") == ["one"]
    assert base._flatten_mixed(["a", "  ", {"k": "v"}, 5]) == ["a", "k:v", "5"]

    messages: List[str] = []
    assert base._ensure_list(["x"], "field", messages) == ["x"]
    assert base._ensure_list("oops", "field", messages) == []
    assert messages == ["'field' must be a list"]


def test_now_iso_returns_utc_stamp(monkeypatch: pytest.MonkeyPatch):
    fixed = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(base.datetime, "datetime", mock.Mock(now=lambda tz=None: fixed))
    value = base._now_iso()
    assert value.endswith("Z")
    assert value.startswith("2025-01-01T12:00:00")


# --------------------------------------------------------------------------- detection + selection helpers

def test_load_detection_file_parses_json(tmp_path: Path):
    path = tmp_path / "detect.json"
    payload = {"language": "python"}
    path.write_text(json.dumps(payload), encoding="utf-8")
    data, error, raw = base._load_detection_file(path)
    assert data == payload
    assert error is None
    assert raw == json.dumps(payload)

    path.write_text("not json", encoding="utf-8")
    data2, error2, raw2 = base._load_detection_file(path)
    assert data2 is None
    assert "invalid JSON" in error2
    assert raw2 == "not json"


def test_resolve_init_target_with_paths(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    slug, resolved, err = base._resolve_init_target("init", str(proj), cwd=tmp_path)
    assert slug.startswith("proj-")
    assert resolved == proj.resolve()
    assert err is None

    slug2, resolved2, err2 = base._resolve_init_target("init", "proj", cwd=tmp_path)
    assert slug2 and resolved2 == proj.resolve() and err2 is None

    slug3, resolved3, err3 = base._resolve_init_target("init", "../bad/slug", cwd=proj)
    assert slug3 is None
    assert "invalid project slug" in err3


def test_parse_selection_validates_against_available():
    ok, items, err = base._parse_selection("A,b", ["A", "B", "C"], label="items")
    assert ok and items == ["A", "B"] and err is None

    ok2, items2, err2 = base._parse_selection("unknown", ["A"], label="items")
    assert not ok2 and "Unknown items" in err2


def test_format_detection_summary_and_header():
    summary = base._format_detection_summary({"language": "py", "framework": "fastapi", "types": ["mypy"]})
    assert any("Language: py" in line for line in summary)
    assert any("Types: mypy" in line for line in summary)

    header = base._format_header("Title")
    assert "Title" in header
    assert "━" in header


# --------------------------------------------------------------------------- append + list helpers

def test_append_session_log_and_listing(tmp_path: Path, _tmp_claude_home: Path):
    project = tmp_path / "project"
    project.mkdir()
    base._append_session_log(project, ["line1", "line2"])
    assert (project / "session-log.md").read_text(encoding="utf-8").strip().endswith("line2")

    # prepare agent/mode files across active + inactive locations
    active_agents = _tmp_claude_home / "agents"
    inactive_agents = _tmp_claude_home / "inactive" / "agents"
    active_agents.mkdir(parents=True, exist_ok=True)
    inactive_agents.mkdir(parents=True, exist_ok=True)
    (active_agents / "alpha.md").touch()
    (inactive_agents / "beta.md").touch()

    active_modes = _tmp_claude_home / "modes"
    inactive_modes = _tmp_claude_home / "inactive" / "modes"
    active_modes.mkdir(parents=True, exist_ok=True)
    inactive_modes.mkdir(parents=True, exist_ok=True)
    (active_modes / "One.md").touch()
    (inactive_modes / "Two.md").touch()

    agents = base._list_available_agents(_tmp_claude_home)
    modes = base._list_available_modes(_tmp_claude_home)
    assert agents == ["alpha", "beta"]
    assert modes == ["One", "Two"]


# --------------------------------------------------------------------------- CLI prompting helpers

def test_confirm_and_prompt_respect_defaults(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(builtins, "input", lambda prompt="": "")
    assert base._prompt_user("Question?", default="abc") == "abc"
    assert base._confirm("Proceed?", default=True) is True
    assert base._confirm("Proceed?", default=False) is False

    monkeypatch.setattr(builtins, "input", lambda prompt="": "Yes")
    assert base._confirm("Proceed?", default=False) is True
