"""Comprehensive tests for core.agents module."""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Dict, List

import pytest
import yaml

from claude_ctx_py.core import agents as agents_mod


# ---- Helpers -----------------------------------------------------------------

def _make_claude_dir(tmp_path: Path) -> Path:
    """Create a minimal .cortex directory with active/inactive/schema roots."""
    claude_dir = tmp_path / ".cortex"
    (claude_dir / "agents").mkdir(parents=True, exist_ok=True)
    (claude_dir / "inactive" / "agents").mkdir(parents=True, exist_ok=True)
    (claude_dir / "schema").mkdir(parents=True, exist_ok=True)
    return claude_dir


def _write_agent(
    path: Path,
    *,
    name: str | None = None,
    version: str = "2.0",
    category: str = "core",
    tier_id: str = "bronze",
    activation_strategy: str = "auto",
    requires: List[str] | None = None,
    recommends: List[str] | None = None,
    tools: List[str] | None = None,
) -> Path:
    """Write a simple agent file with manually indented front matter."""
    requires = requires or []
    recommends = recommends or []
    tools = tools or ["tool-a"]

    front_lines = [
        "---",
        f"version: {version}",
        f"name: {name or path.stem}",
        f"category: {category}",
        "tier:",
        f"  id: {tier_id}",
        f"  activation_strategy: {activation_strategy}",
        "tools:",
        "  catalog:",
        *(f"    - {item}" for item in tools),
        "dependencies:",
        "  requires:",
        *(f"    - {item}" for item in requires),
        "  recommends:",
        *(f"    - {item}" for item in recommends),
        "---",
    ]

    front_text = "\n".join(front_lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{front_text}# body\n", encoding="utf-8")
    return path


def _write_schema(claude_dir: Path) -> Path:
    schema = {
        "required": ["name", "category", "tier.id", "tools.catalog"],
        "fields": {
            "category": {"enum": ["core", "support"]},
            "tier": {
                "properties": {
                    "id": {"enum": ["bronze", "silver"]},
                    "activation_strategy": {"enum": ["auto", "manual"]},
                }
            },
        },
    }
    schema_path = claude_dir / "schema" / "agent-schema-v2.yaml"
    schema_path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")
    return schema_path


@pytest.fixture
def claude_dir(tmp_path: Path) -> Path:
    return _make_claude_dir(tmp_path)


@pytest.fixture(autouse=True)
def _isolate_claude_home(monkeypatch: pytest.MonkeyPatch, claude_dir: Path) -> None:
    """Force cortex to operate inside the temporary .cortex directory."""
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))


# ---- Tests: helpers & parsing -------------------------------------------------

def test_normalize_and_display_names():
    assert agents_mod._normalize_agent_filename("alpha") == "alpha.md"
    assert agents_mod._normalize_agent_filename("beta.md") == "beta.md"
    with pytest.raises(ValueError):
        agents_mod._normalize_agent_filename("   ")
    assert agents_mod._display_agent_name("gamma.md") == "gamma"
    assert agents_mod._display_agent_name(" delta ") == "delta"


def test_front_matter_parsing_returns_metadata_and_dependencies(tmp_path: Path):
    target = tmp_path / "agent.md"
    front = textwrap.dedent(
        """\
        ---
        metadata:
          name: Friendly Agent
          dependencies:
            requires:
              - dep-one
              - dep-two
        ---
        # content
        """
    )
    target.write_text(front, encoding="utf-8")

    lines = agents_mod._read_agent_front_matter_lines(target)
    assert lines and "metadata:" in lines

    assert agents_mod._parse_agent_metadata_name(lines) == "Friendly Agent"
    requires, recommends = agents_mod._parse_dependencies_from_front(lines)
    assert requires == ["dep-one", "dep-two"]
    assert recommends == []


def test_extract_agent_name_falls_back_to_stem(tmp_path: Path):
    target = tmp_path / "nameless.md"
    target.write_text("---\nname: \n---\n", encoding="utf-8")
    assert agents_mod._extract_agent_name(target) == "nameless"


# ---- Tests: dependency map & graph -------------------------------------------

def test_generate_dependency_map_creates_and_cleans(claude_dir: Path):
    agent_a = _write_agent(
        claude_dir / "agents" / "alpha.md", requires=["dep1"], recommends=["rec1"]
    )
    _write_agent(claude_dir / "inactive" / "agents" / "beta.md", requires=["dep2"])

    agents_mod._generate_dependency_map(claude_dir)

    dep_map = claude_dir / "agents" / "dependencies.map"
    assert dep_map.is_file()
    content = dep_map.read_text(encoding="utf-8")
    assert "alpha:dep1:rec1" in content
    assert "beta:dep2:" in content

    # Removing all agents should delete the map
    agent_a.unlink()
    for path in (claude_dir / "inactive" / "agents").glob("*.md"):
        path.unlink()
    agents_mod._generate_dependency_map(claude_dir)
    assert not dep_map.exists()


def test_build_and_render_agent_graph(tmp_path: Path, claude_dir: Path):
    active = _write_agent(
        claude_dir / "agents" / "alpha.md",
        name="Alpha",
        category="core",
        tier_id="silver",
        requires=["dep-a"],
    )
    _write_agent(
        claude_dir / "inactive" / "agents" / "beta.md",
        name="Beta",
        category="support",
        recommends=["rec-a"],
    )
    # Non-v2 agent should be ignored
    _write_agent(
        claude_dir / "agents" / "legacy.md",
        version="1.0",
        name="Legacy",
    )

    nodes = agents_mod.build_agent_graph(home=tmp_path)
    assert {node.name for node in nodes} == {"Alpha", "Beta"}
    statuses = {node.name: node.status for node in nodes}
    assert statuses["Alpha"] == "active"
    assert statuses["Beta"] == "disabled"

    output = agents_mod.render_agent_graph(nodes, use_color=False)
    assert "Agent" in output.splitlines()[0]
    assert "Alpha" in output
    assert "Beta" in output
    assert "dep-a" in output

    export_path = tmp_path / "graph.txt"
    code, export_output = agents_mod.agent_graph(export_path, home=tmp_path)
    assert code == 0
    assert export_path.is_file()
    assert "Exported dependency map" in export_output


# ---- Tests: validation --------------------------------------------------------

def test_agent_validate_success_and_failure(tmp_path: Path, claude_dir: Path):
    _write_schema(claude_dir)
    good = _write_agent(claude_dir / "agents" / "valid.md", name="Good")
    bad = _write_agent(claude_dir / "agents" / "invalid.md", name="Bad", category="")

    code_ok, message_ok = agents_mod.agent_validate("valid", home=tmp_path)
    assert code_ok == 0
    assert "Agent metadata conforms" in message_ok
    assert "Validated 1 agent(s)" in message_ok

    # Validate single invalid agent
    code_bad, message_bad = agents_mod.agent_validate("invalid", home=tmp_path)
    assert code_bad == 1
    assert "missing required field 'category'" in message_bad

    # Missing schema yields error
    (claude_dir / "schema" / "agent-schema-v2.yaml").unlink()
    code_missing, msg_missing = agents_mod.agent_validate(home=tmp_path)
    assert code_missing == 1
    assert "Schema file missing" in msg_missing


def test_resolve_agent_validation_target_prefers_existing_paths(claude_dir: Path):
    target = _write_agent(claude_dir / "agents" / "here.md")
    custom = claude_dir / "custom.md"
    custom.write_text("# no front matter", encoding="utf-8")

    resolved = agents_mod._resolve_agent_validation_target(claude_dir, "here")
    assert resolved == target
    resolved_path = agents_mod._resolve_agent_validation_target(claude_dir, str(custom))
    assert resolved_path == custom
    assert (
        agents_mod._resolve_agent_validation_target(claude_dir, "missing") is None
    )


# ---- Tests: activation / deactivation ----------------------------------------

def test_agent_activation_moves_file_and_dependencies(claude_dir: Path, tmp_path: Path):
    _write_schema(claude_dir)
    dep = _write_agent(
        claude_dir / "inactive" / "agents" / "dep.md",
        name="dep",
    )
    primary = _write_agent(
        claude_dir / "inactive" / "agents" / "primary.md",
        name="primary",
        requires=["dep"],
    )

    exit_code, output = agents_mod.agent_activate("primary", home=tmp_path)
    assert exit_code == 0
    assert "Activated agent: dep" in output
    assert "Activated agent: primary" in output
    assert (claude_dir / "agents" / "primary.md").is_file()
    assert (claude_dir / "agents" / "dep.md").is_file()

    # Activating again should be idempotent
    exit_code2, output2 = agents_mod.agent_activate("primary", home=tmp_path)
    assert exit_code2 == 0
    assert "already active" in output2


def test_agent_activation_detects_cycles(claude_dir: Path, tmp_path: Path):
    _write_agent(
        claude_dir / "inactive" / "agents" / "a.md",
        name="a",
        requires=["b"],
    )
    _write_agent(
        claude_dir / "inactive" / "agents" / "b.md",
        name="b",
        requires=["a"],
    )

    code, output = agents_mod.agent_activate("a", home=tmp_path)
    assert code == 1
    assert "Dependency cycle detected" in output


def test_agent_activate_missing_returns_error(tmp_path: Path):
    code, output = agents_mod.agent_activate("ghost", home=tmp_path)
    assert code == 1
    assert "not found in disabled agents" in output


def test_agent_deactivate_respects_dependents(claude_dir: Path, tmp_path: Path):
    dep = _write_agent(claude_dir / "agents" / "dep.md", name="dep")
    _write_agent(
        claude_dir / "agents" / "consumer.md",
        name="consumer",
        requires=["dep"],
    )

    code_block, msg_block = agents_mod.agent_deactivate("dep", home=tmp_path)
    assert code_block == 1
    assert "Cannot deactivate" in msg_block
    assert dep.is_file()

    code_force, msg_force = agents_mod.agent_deactivate(
        "dep", force=True, home=tmp_path
    )
    assert code_force == 0
    assert "Deactivated agent: dep" in msg_force
    assert (claude_dir / "inactive" / "agents" / "dep.md").is_file()


def test_agent_deactivate_missing_or_inactive(tmp_path: Path):
    code, message = agents_mod.agent_deactivate("unknown", home=tmp_path)
    assert code == 1
    assert "not currently active" in message


# ---- Tests: listing and dependency reporting ---------------------------------

def test_list_agents_and_status_outputs(claude_dir: Path, tmp_path: Path):
    _write_agent(claude_dir / "agents" / "active.md", name="active")
    _write_agent(claude_dir / "inactive" / "agents" / "disabled.md", name="disabled")

    listing = agents_mod.list_agents(home=tmp_path)
    assert "active" in listing
    assert "inactive/agents" in listing

    status = agents_mod.agent_status(home=tmp_path)
    assert "Total active agents: 1" in status


def test_agent_deps_reports_statuses(claude_dir: Path, tmp_path: Path):
    _write_agent(claude_dir / "agents" / "dep-active.md", name="dep-active")
    _write_agent(
        claude_dir / "inactive" / "agents" / "dep-disabled.md", name="dep-disabled"
    )
    _write_agent(
        claude_dir / "agents" / "main.md",
        name="main",
        requires=["dep-active", "dep-disabled", "missing-dep"],
        recommends=["rec-one"],
    )

    code, output = agents_mod.agent_deps("main", home=tmp_path)
    assert code == 0
    assert "dep-active (active)" in output
    assert "dep-disabled (disabled)" in output
    assert "missing-dep (missing)" in output
    assert "rec-one (missing)" in output
