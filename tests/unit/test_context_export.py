from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py import cli
from claude_ctx_py.core.context_export import export_agents


def _write_agent(path: Path, name: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\n---\n\n# {name}\n\nAgent definition for {name}.\n",
        encoding="utf-8",
    )


@pytest.mark.unit
def test_export_agents_includes_active_and_disabled_agents(tmp_path: Path) -> None:
    claude_dir = tmp_path
    _write_agent(claude_dir / "agents" / "code-reviewer.md", "code-reviewer")
    _write_agent(claude_dir / "inactive" / "agents" / "debugger.md", "debugger")

    output_path = tmp_path / "agents-export.md"
    exit_code, message = export_agents(
        ["code-reviewer", "debugger"],
        output_path=output_path,
        claude_dir=claude_dir,
    )

    assert exit_code == 0
    assert "exported successfully" in message.lower()

    export_text = output_path.read_text(encoding="utf-8")
    assert "## agents/code-reviewer.md" in export_text
    assert "## inactive/agents/debugger.md" in export_text
    assert "Agent definition for code-reviewer." in export_text
    assert "Agent definition for debugger." in export_text


@pytest.mark.unit
def test_export_agents_returns_error_for_missing_agents(tmp_path: Path) -> None:
    claude_dir = tmp_path
    _write_agent(claude_dir / "agents" / "code-reviewer.md", "code-reviewer")

    output_path = tmp_path / "agents-export.md"
    exit_code, message = export_agents(
        ["code-reviewer", "missing-agent"],
        output_path=output_path,
        claude_dir=claude_dir,
    )

    assert exit_code == 1
    assert "missing-agent" in message
    assert not output_path.exists()


@pytest.mark.unit
def test_export_agents_supports_symlinked_active_agents(tmp_path: Path) -> None:
    claude_dir = tmp_path / ".claude"
    source_path = tmp_path / "assets" / "agents" / "code-reviewer.md"
    _write_agent(source_path, "code-reviewer")

    active_path = claude_dir / "agents" / "code-reviewer.md"
    active_path.parent.mkdir(parents=True, exist_ok=True)
    active_path.symlink_to(source_path)

    output_path = tmp_path / "agents-export.md"
    exit_code, _ = export_agents(
        ["code-reviewer"],
        output_path=output_path,
        claude_dir=claude_dir,
    )

    assert exit_code == 0
    export_text = output_path.read_text(encoding="utf-8")
    assert "## agents/code-reviewer.md" in export_text


@pytest.mark.unit
def test_export_agents_rejects_path_traversal_names(tmp_path: Path) -> None:
    claude_dir = tmp_path
    _write_agent(claude_dir / "escape.md", "escape")

    exit_code, message = export_agents(
        ["../escape"],
        output_path=tmp_path / "agents-export.md",
        claude_dir=claude_dir,
    )

    assert exit_code == 1
    assert "../escape" in message


@pytest.mark.unit
def test_export_agents_stdout_writes_bundle_and_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    claude_dir = tmp_path
    _write_agent(claude_dir / "inactive" / "agents" / "debugger.md", "debugger")

    exit_code, message = export_agents(
        ["debugger"],
        output_path="-",
        claude_dir=claude_dir,
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert message == ""
    assert "## inactive/agents/debugger.md" in captured.out
    assert "Agent definitions exported to stdout" in captured.err


@pytest.mark.unit
def test_cli_export_agents_routes_to_core_export(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_export_agents(
        agent_names: list[str],
        output_path: Path | str = "-",
        claude_dir: Path | None = None,
        agent_generic: bool = True,
    ) -> tuple[int, str]:
        captured["agent_names"] = agent_names
        captured["output_path"] = output_path
        captured["agent_generic"] = agent_generic
        return 0, "ok"

    monkeypatch.setattr(cli.core, "export_agents", fake_export_agents)

    exit_code = cli.main(
        [
            "--skip-wizard",
            "export",
            "agents",
            "code-reviewer",
            "debugger",
            "--output",
            "-",
            "--no-agent-generic",
        ]
    )

    assert exit_code == 0
    assert captured["agent_names"] == ["code-reviewer", "debugger"]
    assert captured["output_path"] == "-"
    assert captured["agent_generic"] is False
