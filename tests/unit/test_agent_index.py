"""Unit tests for claude_ctx_py.agent_index."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claude_ctx_py.agent_index import (
    AGENT_INDEX_VERSION,
    AgentIndexError,
    build_index,
    load_index,
    rebuild_index,
    write_index,
)


def _make_agent(
    agents_root: Path,
    filename: str,
    *,
    name: str,
    description: str = "Test agent",
    keywords: list[str] | None = None,
    file_patterns: list[str] | None = None,
    delegate_when: list[str] | None = None,
    aliases: list[str] | None = None,
    body: str = "Agent body.",
) -> Path:
    agents_root.mkdir(parents=True, exist_ok=True)
    fm = [f"name: {name}", f"description: {description}"]
    if aliases is not None:
        fm.append("alias:")
        for a in aliases:
            fm.append(f"  - {a}")
    if keywords is not None or file_patterns is not None:
        if keywords is not None:
            fm.append("activation:")
            fm.append("  keywords:")
            for kw in keywords:
                fm.append(f"    - {kw}")
        if file_patterns is not None:
            fm.append("tier:")
            fm.append("  conditions:")
            for p in file_patterns:
                fm.append(f'    - "{p}"')
    if delegate_when is not None:
        fm.append("delegate_when:")
        for d in delegate_when:
            fm.append(f"  - {d}")

    content = "---\n" + "\n".join(fm) + "\n---\n\n" + body + "\n"
    path = agents_root / filename
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.unit
class TestBuildIndex:
    def test_happy_path(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(
            agents,
            "alpha.md",
            name="alpha",
            keywords=["alpha", "foo"],
            file_patterns=["**/alpha/**"],
            delegate_when=["independence"],
        )
        _make_agent(
            agents,
            "beta.md",
            name="beta",
            keywords=["beta"],
        )

        doc = build_index(agents)

        assert doc["version"] == AGENT_INDEX_VERSION
        assert [a["name"] for a in doc["agents"]] == ["alpha", "beta"]
        alpha = doc["agents"][0]
        assert alpha["keywords"] == ["alpha", "foo"]
        assert alpha["file_patterns"] == ["**/alpha/**"]
        assert alpha["delegate_when"] == ["independence"]
        beta = doc["agents"][1]
        assert beta["delegate_when"] == []

    def test_aliases_preserved(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(
            agents,
            "code-reviewer.md",
            name="code-reviewer",
            aliases=["quality-guardian"],
            keywords=["review"],
        )
        doc = build_index(agents)
        assert doc["agents"][0]["aliases"] == ["quality-guardian"]

    def test_duplicate_name_raises(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(agents, "a.md", name="shared", keywords=["x"])
        _make_agent(agents, "b.md", name="shared", keywords=["y"])
        with pytest.raises(AgentIndexError, match="duplicate agent name"):
            build_index(agents)

    def test_missing_name_raises(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "orphan.md").write_text(
            "---\ndescription: no name\n---\n\nBody\n", encoding="utf-8"
        )
        with pytest.raises(AgentIndexError, match="missing or invalid 'name'"):
            build_index(agents)

    def test_no_front_matter_skipped(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "plain.md").write_text("# no front matter\n", encoding="utf-8")
        _make_agent(agents, "real.md", name="real", keywords=["x"])
        doc = build_index(agents)
        assert [a["name"] for a in doc["agents"]] == ["real"]

    def test_invalid_delegate_when_raises(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(
            agents,
            "bad.md",
            name="bad",
            keywords=["x"],
            delegate_when=["nonsense"],
        )
        with pytest.raises(AgentIndexError, match="invalid delegate_when"):
            build_index(agents)

    def test_readme_skipped(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        agents.mkdir()
        (agents / "README.md").write_text("# Agents readme\n", encoding="utf-8")
        _make_agent(agents, "actual.md", name="actual", keywords=["x"])
        doc = build_index(agents)
        assert [a["name"] for a in doc["agents"]] == ["actual"]

    def test_missing_root_raises(self, tmp_path: Path) -> None:
        with pytest.raises(AgentIndexError, match="not found"):
            build_index(tmp_path / "nope")


@pytest.mark.unit
class TestWriteAndLoad:
    def test_deterministic_write(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(agents, "z.md", name="zulu", keywords=["z", "z"])
        _make_agent(agents, "a.md", name="alpha", keywords=["a"])

        out1 = tmp_path / "one.json"
        out2 = tmp_path / "two.json"
        write_index(build_index(agents), out1)
        write_index(build_index(agents), out2)
        assert out1.read_bytes() == out2.read_bytes()

    def test_keywords_sorted_and_deduped(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(
            agents,
            "dev.md",
            name="dev",
            keywords=["zebra", "apple", "apple", "mango"],
        )
        out = tmp_path / "idx.json"
        write_index(build_index(agents), out)
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["agents"][0]["keywords"] == ["apple", "mango", "zebra"]

    def test_load_round_trip(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(
            agents,
            "rr.md",
            name="rr",
            keywords=["a"],
            file_patterns=["**/x/**"],
            delegate_when=["independence"],
            aliases=["roundup"],
        )
        out = tmp_path / "idx.json"
        write_index(build_index(agents), out)
        loaded = load_index(out)
        assert loaded["agents"][0]["aliases"] == ["roundup"]
        assert loaded["agents"][0]["delegate_when"] == ["independence"]

    def test_load_malformed(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.json"
        p.write_text("{not json", encoding="utf-8")
        with pytest.raises(AgentIndexError, match="not valid JSON"):
            load_index(p)


@pytest.mark.unit
class TestRebuildEntrypoint:
    def test_writes_and_idempotent(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(agents, "one.md", name="one", keywords=["x"])
        _make_agent(agents, "two.md", name="two", keywords=["y"])

        exit_code, message = rebuild_index(agents_root=agents)
        assert exit_code == 0
        assert "2 agents" in message

        out = agents / "agent-index.json"
        first = out.read_bytes()
        rebuild_index(agents_root=agents)
        assert out.read_bytes() == first

    def test_duplicate_returns_error_code(self, tmp_path: Path) -> None:
        agents = tmp_path / "agents"
        _make_agent(agents, "a.md", name="same", keywords=["x"])
        _make_agent(agents, "b.md", name="same", keywords=["y"])
        exit_code, message = rebuild_index(agents_root=agents)
        assert exit_code == 1
        assert "duplicate" in message
