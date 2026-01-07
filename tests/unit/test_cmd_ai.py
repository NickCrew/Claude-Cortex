"""Tests for cmd_ai CLI helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import pytest

from claude_ctx_py import cmd_ai
from claude_ctx_py.intelligence import (
    AgentRecommendation,
    WorkflowPrediction,
    SessionContext,
)


# --------------------------------------------------------------------------- fixtures

@pytest.fixture(autouse=True)
def _tmp_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Force commands to operate inside a temp .cortex directory."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))
    return claude_dir


# --------------------------------------------------------------------------- helpers

class DummyAgent:
    def __init__(
        self,
        recommendations: List[AgentRecommendation] | None = None,
        workflow: WorkflowPrediction | None = None,
        context: SessionContext | None = None,
        auto: List[str] | None = None,
        smart: dict | None = None,
    ):
        self.recommendations = recommendations or []
        self.workflow = workflow
        self.current_context = context
        self.auto = auto or []
        self.smart = smart or {}
        self.analyzed = False
        self.auto_marked: List[str] = []
        self.recorded: dict | None = None
        self.intelligence_dir = None

    def analyze_context(self):
        self.analyzed = True
        return self.current_context

    def get_recommendations(self):
        return self.recommendations

    def predict_workflow(self):
        return self.workflow

    def get_auto_activations(self):
        return self.auto

    def mark_auto_activated(self, name: str):
        self.auto_marked.append(name)

    def get_smart_suggestions(self):
        return self.smart

    def record_session_success(self, *, agents_used, duration, outcome):
        self.recorded = {
            "agents_used": agents_used,
            "duration": duration,
            "outcome": outcome,
        }


# --------------------------------------------------------------------------- tests


def test_ai_recommend_no_results(monkeypatch: pytest.MonkeyPatch, capsys):
    dummy = DummyAgent()
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_args, **_kwargs: dummy)

    code = cmd_ai.ai_recommend()
    captured = capsys.readouterr().out

    assert code == 0
    assert "No recommendations" in captured
    assert dummy.analyzed is True


def test_ai_recommend_with_data(monkeypatch: pytest.MonkeyPatch, capsys):
    recs = [
        AgentRecommendation(
            agent_name="code-reviewer",
            confidence=0.82,
            reason="Tests failed",
            urgency="high",
            auto_activate=True,
            context_triggers=["tests"],
        )
    ]
    workflow = WorkflowPrediction(
        workflow_name="Fix Tests",
        agents_sequence=["code-reviewer", "debugger"],
        confidence=0.9,
        estimated_duration=125,
        success_probability=0.8,
        based_on_pattern="recent-fails",
    )
    ctx = SessionContext(
        files_changed=["a.py", "b.py"],
        file_types={".py"},
        directories={"src"},
        has_tests=True,
        has_auth=False,
        has_api=True,
        has_frontend=False,
        has_backend=True,
        has_database=False,
        errors_count=1,
        test_failures=1,
        build_failures=0,
        session_start=None,  # type: ignore[arg-type]
        last_activity=None,  # type: ignore[arg-type]
        active_agents=[],
        active_modes=[],
        active_rules=[],
    )
    dummy = DummyAgent(recommendations=recs, workflow=workflow, context=ctx)
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_a, **_k: dummy)

    code = cmd_ai.ai_recommend()
    out = capsys.readouterr().out

    assert code == 0
    assert "code-reviewer" in out
    assert "Fix Tests" in out
    assert "Issues: 1 errors, 1 test failures" in out
    assert dummy.analyzed is True


def test_ai_auto_activate_handles_success_and_failure(monkeypatch: pytest.MonkeyPatch, capsys):
    dummy = DummyAgent(auto=["a1", "a2"])
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_a, **_k: dummy)

    def fake_activate(name):
        return (0, "ok") if name == "a1" else (1, "boom")

    monkeypatch.setattr("claude_ctx_py.core.agent_activate", fake_activate)

    code = cmd_ai.ai_auto_activate()
    out = capsys.readouterr().out

    assert code == 1  # because one failed
    assert "Auto-activating 2 agents" in out
    assert "✓ a1" in out
    assert "✗ a2" in out
    assert dummy.auto_marked == ["a1"]


def test_ai_export_json_writes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    suggestions = {
        "agent_recommendations": [{"agent": "x"}],
        "workflow_prediction": {"confidence": 0.7},
    }
    dummy = DummyAgent(smart=suggestions)
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_a, **_k: dummy)

    out_file = tmp_path / "out.json"
    code = cmd_ai.ai_export_json(output_file=str(out_file))

    output = capsys.readouterr().out
    assert code == 0
    assert out_file.is_file()
    data = json.loads(out_file.read_text())
    assert data == suggestions
    assert "Exported AI recommendations" in output


def test_ai_record_success_with_active_agents(monkeypatch: pytest.MonkeyPatch, _tmp_home: Path, capsys):
    active_file = _tmp_home / "agents" / "active.txt"
    active_file.parent.mkdir(parents=True, exist_ok=True)
    active_file.write_text("alpha\nbeta\n", encoding="utf-8")

    ctx = SessionContext(
        files_changed=["a.py"],
        file_types={".py"},
        directories={"src"},
        has_tests=True,
        has_auth=False,
        has_api=True,
        has_frontend=False,
        has_backend=True,
        has_database=False,
        errors_count=0,
        test_failures=0,
        build_failures=0,
        session_start=None,  # type: ignore[arg-type]
        last_activity=None,  # type: ignore[arg-type]
        active_agents=[],
        active_modes=[],
        active_rules=[],
    )
    dummy = DummyAgent(context=ctx)
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_a, **_k: dummy)

    code = cmd_ai.ai_record_success(outcome="win")
    out = capsys.readouterr().out

    assert code == 0
    assert "Recorded successful session" in out
    assert dummy.recorded is not None
    assert dummy.recorded["agents_used"] == ["alpha", "beta"]
    assert dummy.recorded["outcome"] == "win"


def test_ai_record_success_no_active_agents(monkeypatch: pytest.MonkeyPatch, _tmp_home: Path, capsys):
    dummy = DummyAgent()
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *_a, **_k: dummy)

    code = cmd_ai.ai_record_success()
    out = capsys.readouterr().out

    assert code == 1
    assert "No active agents" in out
