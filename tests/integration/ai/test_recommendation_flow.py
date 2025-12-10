"""Integration test for AI recommendation CLI flow."""

from __future__ import annotations

import pytest

from claude_ctx_py import cli
from claude_ctx_py import cmd_ai
from claude_ctx_py.intelligence import AgentRecommendation, WorkflowPrediction, SessionContext


class DummyAgent:
    def __init__(self):
        self.analyzed = False
        self.auto_marked = []
        self.current_context = None

    def analyze_context(self):
        self.analyzed = True
        self.current_context = SessionContext(
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
        return self.current_context

    def get_recommendations(self):
        return [
            AgentRecommendation(
                agent_name="code-reviewer",
                confidence=0.9,
                reason="Tests changed",
                urgency="high",
                auto_activate=True,
                context_triggers=["tests"],
            )
        ]

    def predict_workflow(self):
        return WorkflowPrediction(
            workflow_name="Review Cycle",
            agents_sequence=["code-reviewer"],
            confidence=0.8,
            estimated_duration=60,
            success_probability=0.7,
            based_on_pattern="pattern",
        )

    def get_auto_activations(self):
        return ["code-reviewer"]

    def mark_auto_activated(self, name: str):
        self.auto_marked.append(name)

    def get_smart_suggestions(self):
        return {"agent_recommendations": [{"agent": "code-reviewer"}]}

    def record_session_success(self, **kwargs):
        pass


@pytest.mark.integration
def test_ai_recommendation_cli_flow(monkeypatch: pytest.MonkeyPatch, capsys, test_project):
    dummy = DummyAgent()
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *a, **k: dummy)

    code = cli.main(["ai", "recommend"])
    output = capsys.readouterr().out

    assert code == 0
    assert "code-reviewer" in output
    assert dummy.analyzed


@pytest.mark.integration
def test_ai_auto_activate_cli_flow(monkeypatch: pytest.MonkeyPatch, capsys, test_project):
    dummy = DummyAgent()
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *a, **k: dummy)
    monkeypatch.setattr("claude_ctx_py.core.agent_activate", lambda name: (0, "ok"))

    code = cli.main(["ai", "auto-activate"])
    output = capsys.readouterr().out

    assert code == 0
    assert "Auto-activating" in output
    assert dummy.auto_marked == ["code-reviewer"]


@pytest.mark.integration
def test_ai_export_and_record_success(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path, test_project):
    dummy = DummyAgent()
    dummy.current_context = dummy.analyze_context()
    dummy.smart = {
        "agent_recommendations": [{"agent": "code-reviewer"}],
        "workflow_prediction": {"confidence": 0.8},
    }
    monkeypatch.setattr(cmd_ai, "IntelligentAgent", lambda *a, **k: dummy)

    out_path = tmp_path / "out.json"
    code_export = cli.main(["ai", "export", "--output", str(out_path)])
    export_out = capsys.readouterr().out
    assert code_export == 0
    assert out_path.is_file()
    assert "Exported AI recommendations" in export_out

    # Prepare active agents file for record-success
    claude_dir = test_project / ".claude"
    active_file = claude_dir / "agents" / "active.txt"
    active_file.parent.mkdir(parents=True, exist_ok=True)
    active_file.write_text("code-reviewer\n", encoding="utf-8")

    code_record = cli.main(["ai", "record-success", "--outcome", "win"])
    record_out = capsys.readouterr().out
    assert code_record == 0
    assert "Recorded successful session" in record_out
