"""Unit tests for memory/basic_memory.py — Basic Memory CLI/MCP integration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

import pytest

from claude_ctx_py.memory import basic_memory as bm


@pytest.fixture(autouse=True)
def _clean_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORTEX_SCOPE", raising=False)
    monkeypatch.delenv("CORTEX_MEMORY_VAULT", raising=False)


class _FakeCompleted:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode


class _RecordingRunner:
    """Records the argv it was called with and returns a fixed exit code."""

    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.calls: List[List[str]] = []

    def __call__(self, argv: List[str], *a: Any, **k: Any) -> _FakeCompleted:
        self.calls.append(argv)
        return _FakeCompleted(self.returncode)


# ── runtime resolution ──────────────────────────────────────────────────────


@pytest.mark.unit
def test_resolve_runtime_prefers_uvx() -> None:
    rt = bm.resolve_runtime(which=lambda name: "/bin/" + name)  # everything present
    assert rt.command == "uvx"
    assert rt.argv("mcp") == ["uvx", "basic-memory", "mcp"]


@pytest.mark.unit
def test_resolve_runtime_falls_back_to_homebrew_basic_memory() -> None:
    def which(name: str) -> Optional[str]:
        return "/opt/homebrew/bin/basic-memory" if name == "basic-memory" else None

    rt = bm.resolve_runtime(which=which)
    assert rt.command == "basic-memory"
    assert rt.argv("mcp") == ["basic-memory", "mcp"]


@pytest.mark.unit
def test_resolve_runtime_raises_when_neither_present() -> None:
    with pytest.raises(bm.BasicMemoryUnavailable) as exc:
        bm.resolve_runtime(which=lambda name: None)
    assert "install uv" in str(exc.value).lower()


# ── project name derivation ─────────────────────────────────────────────────


@pytest.mark.unit
def test_default_project_name_project_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "My Repo"
    (project / ".claude").mkdir(parents=True)
    monkeypatch.chdir(project)
    monkeypatch.setenv("CORTEX_SCOPE", "project")

    assert bm.default_project_name() == "my-repo-notes"


# ── MCP server entry construction ───────────────────────────────────────────


@pytest.mark.unit
def test_mcp_server_entry_uvx() -> None:
    rt = bm.Runtime("uvx", ("basic-memory",))
    entry = bm.mcp_server_entry(rt, "cortex-notes")
    assert entry == {
        "command": "uvx",
        "args": ["basic-memory", "mcp", "--project", "cortex-notes"],
    }


@pytest.mark.unit
def test_mcp_server_entry_direct() -> None:
    rt = bm.Runtime("basic-memory", ())
    entry = bm.mcp_server_entry(rt, "cortex-notes")
    assert entry == {
        "command": "basic-memory",
        "args": ["mcp", "--project", "cortex-notes"],
    }


# ── init / remove command construction ──────────────────────────────────────


@pytest.mark.unit
def test_init_runs_project_add_with_vault_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vault = tmp_path / "vault"
    monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(vault))
    monkeypatch.setattr(bm, "resolve_runtime", lambda *a, **k: bm.Runtime("uvx", ("basic-memory",)))
    runner = _RecordingRunner()

    code, msg = bm.init("acme-notes", runner=runner)

    assert code == 0
    assert runner.calls == [
        ["uvx", "basic-memory", "project", "add", "acme-notes", str(vault.resolve())]
    ]
    assert vault.is_dir()  # ensure_vault_structure created it
    assert "acme-notes" in msg


@pytest.mark.unit
def test_init_propagates_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path / "vault"))
    monkeypatch.setattr(bm, "resolve_runtime", lambda *a, **k: bm.Runtime("basic-memory", ()))
    runner = _RecordingRunner(returncode=2)

    code, msg = bm.init("x-notes", runner=runner)

    assert code == 2
    assert "failed" in msg.lower()


@pytest.mark.unit
def test_remove_runs_project_remove_and_unconfigures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bm, "resolve_runtime", lambda *a, **k: bm.Runtime("uvx", ("basic-memory",)))
    runner = _RecordingRunner()
    cfg = tmp_path / ".claude.json"
    root = tmp_path / "repo"
    root.mkdir()
    cfg.write_text(
        json.dumps(
            {"projects": {str(root.resolve()): {"mcpServers": {"acme-notes": {"command": "uvx"}}}}}
        )
    )

    code, msg = bm.remove("acme-notes", runner=runner, config_path=cfg, project_root=root)

    assert code == 0
    assert runner.calls == [["uvx", "basic-memory", "project", "remove", "acme-notes"]]
    # MCP entry was cleaned up
    data = json.loads(cfg.read_text())
    assert "acme-notes" not in data["projects"][str(root.resolve())]["mcpServers"]
    assert "MCP config entry removed" in msg
    assert "vault files kept" in msg


@pytest.mark.unit
def test_remove_delete_notes_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(bm, "resolve_runtime", lambda *a, **k: bm.Runtime("basic-memory", ()))
    runner = _RecordingRunner()
    code, msg = bm.remove(
        "x-notes",
        delete_notes=True,
        runner=runner,
        config_path=tmp_path / "absent.json",
        project_root=tmp_path,
    )
    assert code == 0
    assert runner.calls == [["basic-memory", "project", "remove", "x-notes", "--delete-notes"]]
    assert "vault files deleted" in msg


# ── configure_mcp: ~/.claude.json merge ─────────────────────────────────────


@pytest.mark.unit
def test_configure_mcp_creates_entry(tmp_path: Path) -> None:
    cfg = tmp_path / ".claude.json"
    root = tmp_path / "repo"
    root.mkdir()
    rt = bm.Runtime("uvx", ("basic-memory",))

    code, msg = bm.configure_mcp(
        "acme-notes", config_path=cfg, project_root=root, runtime=rt
    )

    assert code == 0
    data = json.loads(cfg.read_text())
    entry = data["projects"][str(root.resolve())]["mcpServers"]["acme-notes"]
    assert entry == {
        "command": "uvx",
        "args": ["basic-memory", "mcp", "--project", "acme-notes"],
    }


@pytest.mark.unit
def test_configure_mcp_preserves_existing_servers(tmp_path: Path) -> None:
    cfg = tmp_path / ".claude.json"
    root = tmp_path / "repo"
    root.mkdir()
    key = str(root.resolve())
    cfg.write_text(
        json.dumps(
            {
                "someTopLevelKey": 1,
                "projects": {
                    key: {
                        "mcpServers": {"backlog": {"command": "backlog", "args": ["mcp"]}},
                        "allowedTools": ["X"],
                    }
                },
            }
        )
    )
    rt = bm.Runtime("uvx", ("basic-memory",))

    bm.configure_mcp("acme-notes", config_path=cfg, project_root=root, runtime=rt)

    data = json.loads(cfg.read_text())
    servers = data["projects"][key]["mcpServers"]
    assert "backlog" in servers  # untouched
    assert "acme-notes" in servers  # added
    assert data["someTopLevelKey"] == 1  # other keys preserved
    assert data["projects"][key]["allowedTools"] == ["X"]


@pytest.mark.unit
def test_configure_mcp_refuses_malformed_json(tmp_path: Path) -> None:
    cfg = tmp_path / ".claude.json"
    cfg.write_text("{ not valid json")
    rt = bm.Runtime("uvx", ("basic-memory",))

    code, msg = bm.configure_mcp(
        "acme-notes", config_path=cfg, project_root=tmp_path, runtime=rt
    )

    assert code == 1
    assert "Could not parse" in msg
    # original file left untouched
    assert cfg.read_text() == "{ not valid json"
