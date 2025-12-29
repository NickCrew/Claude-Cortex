"""Comprehensive tests for intelligence module."""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_ctx_py.intelligence import (
    SessionContext,
    AgentRecommendation,
    WorkflowPrediction,
    PatternLearner,
    ContextDetector,
    IntelligentAgent,
)


class TestSessionContext:
    """Tests for SessionContext dataclass."""

    def test_session_context_creation(self):
        """Test creating a session context."""
        now = datetime.now()
        context = SessionContext(
            files_changed=["file1.py", "file2.ts"],
            file_types={".py", ".ts"},
            directories={"src", "tests"},
            has_tests=True,
            has_auth=False,
            has_api=True,
            has_frontend=True,
            has_backend=True,
            has_database=False,
            errors_count=2,
            test_failures=1,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=["test-automator"],
            active_modes=["dev"],
            active_rules=["quality"],
        )

        assert len(context.files_changed) == 2
        assert ".py" in context.file_types
        assert context.has_tests
        assert context.has_api

    def test_session_context_to_dict(self):
        """Test converting session context to dictionary."""
        now = datetime.now()
        context = SessionContext(
            files_changed=["file1.py"],
            file_types={".py"},
            directories={"src"},
            has_tests=True,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=True,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        result = context.to_dict()

        assert isinstance(result, dict)
        assert result["files_changed"] == ["file1.py"]
        assert result["file_types"] == [".py"]
        assert result["directories"] == ["src"]
        assert result["has_tests"] is True
        assert result["has_backend"] is True
        assert result["session_start"] == now.isoformat()
        assert "active_agents" in result


class TestAgentRecommendation:
    """Tests for AgentRecommendation dataclass."""

    def test_agent_recommendation_creation(self):
        """Test creating an agent recommendation."""
        rec = AgentRecommendation(
            agent_name="code-reviewer",
            confidence=0.85,
            reason="Large changeset detected",
            urgency="medium",
            auto_activate=False,
            context_triggers=["large_changeset"],
        )

        assert rec.agent_name == "code-reviewer"
        assert rec.confidence == 0.85
        assert rec.urgency == "medium"
        assert not rec.auto_activate

    def test_should_notify_high_confidence(self):
        """Test notification decision with high confidence."""
        rec = AgentRecommendation(
            agent_name="test-automator",
            confidence=0.75,
            reason="Test failures",
            urgency="medium",
            auto_activate=True,
            context_triggers=["test_failures"],
        )

        assert rec.should_notify()

    def test_should_notify_critical_urgency(self):
        """Test notification decision with critical urgency."""
        rec = AgentRecommendation(
            agent_name="security-auditor",
            confidence=0.5,
            reason="Auth changes",
            urgency="critical",
            auto_activate=True,
            context_triggers=["auth"],
        )

        assert rec.should_notify()

    def test_should_not_notify_low_confidence_and_urgency(self):
        """Test no notification with low confidence and urgency."""
        rec = AgentRecommendation(
            agent_name="docs",
            confidence=0.4,
            reason="Minor changes",
            urgency="low",
            auto_activate=False,
            context_triggers=["docs"],
        )

        assert not rec.should_notify()


class TestPatternLearner:
    """Tests for PatternLearner class."""

    def test_pattern_learner_init_new_file(self, tmp_path):
        """Test initializing pattern learner with new file."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        assert learner.history_file == history_file
        assert len(learner.patterns) == 0
        assert len(learner.agent_sequences) == 0

    def test_pattern_learner_load_existing_history(self, tmp_path):
        """Test loading existing history file."""
        history_file = tmp_path / "history.json"

        # Create history file
        data = {
            "patterns": {
                "frontend": [{"agents": ["test-automator"], "duration": 300}]
            },
            "agent_sequences": [["test-automator", "code-reviewer"]],
            "success_contexts": [],
        }
        with open(history_file, "w") as f:
            json.dump(data, f)

        learner = PatternLearner(history_file)

        assert "frontend" in learner.patterns
        assert len(learner.agent_sequences) == 1

    def test_generate_context_key_frontend(self):
        """Test generating context key for frontend."""
        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=True,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        learner = PatternLearner(Path("/tmp/test.json"))
        key = learner._generate_context_key(context)

        assert key == "frontend"

    def test_generate_context_key_multiple_components(self):
        """Test generating context key with multiple components."""
        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=True,
            has_auth=True,
            has_api=True,
            has_frontend=False,
            has_backend=True,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        learner = PatternLearner(Path("/tmp/test.json"))
        key = learner._generate_context_key(context)

        # Should be sorted
        components = key.split("_")
        assert "api" in components
        assert "auth" in components
        assert "backend" in components
        assert "tests" in components
        assert components == sorted(components)

    def test_generate_context_key_general(self):
        """Test generating context key for general case."""
        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        learner = PatternLearner(Path("/tmp/test.json"))
        key = learner._generate_context_key(context)

        assert key == "general"

    def test_record_success(self, tmp_path):
        """Test recording successful session."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=["test.py"],
            file_types={".py"},
            directories={"tests"},
            has_tests=True,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        learner.record_success(context, ["test-automator"], 300, "Tests passed")

        assert len(learner.agent_sequences) == 1
        assert learner.agent_sequences[0] == ["test-automator"]
        assert "tests" in learner.patterns
        assert history_file.exists()

    def test_predict_agents_no_history(self, tmp_path):
        """Test predicting agents with no history."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=True,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        recommendations = learner.predict_agents(context)

        # Should still get rule-based recommendations
        assert isinstance(recommendations, list)

    def test_rule_based_recommendations_auth(self, tmp_path):
        """Test rule-based recommendations for auth context."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=["auth.py"],
            file_types={".py"},
            directories={"src"},
            has_tests=False,
            has_auth=True,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        recommendations = learner._rule_based_recommendations(context)

        # Should recommend security-auditor
        security_rec = next((r for r in recommendations if r.agent_name == "security-auditor"), None)
        assert security_rec is not None
        assert security_rec.auto_activate
        assert security_rec.urgency == "high"

    def test_rule_based_recommendations_test_failures(self, tmp_path):
        """Test rule-based recommendations for test failures."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=True,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=5,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        recommendations = learner._rule_based_recommendations(context)

        # Should recommend test-automator
        test_rec = next((r for r in recommendations if r.agent_name == "test-automator"), None)
        assert test_rec is not None
        assert test_rec.auto_activate
        assert test_rec.urgency == "critical"

    def test_rule_based_recommendations_frontend_reviews(self, tmp_path):
        """Test review recommendations for frontend changes."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=["src/components/Button.tsx", "src/styles/main.css"],
            file_types={".tsx", ".css"},
            directories={"src/components", "src/styles"},
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=True,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        recommendations = learner._rule_based_recommendations(context)
        recs_by_name = {rec.agent_name: rec for rec in recommendations}

        assert "quality-engineer" in recs_by_name
        assert "code-reviewer" in recs_by_name
        assert "typescript-pro" in recs_by_name
        assert "react-specialist" in recs_by_name
        assert "ui-ux-designer" in recs_by_name

        assert recs_by_name["quality-engineer"].auto_activate
        assert recs_by_name["code-reviewer"].auto_activate
        assert recs_by_name["typescript-pro"].auto_activate
        assert recs_by_name["react-specialist"].auto_activate
        assert recs_by_name["ui-ux-designer"].auto_activate

    def test_predict_workflow_insufficient_history(self, tmp_path):
        """Test workflow prediction with insufficient history."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=True,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        prediction = learner.predict_workflow(context)

        assert prediction is None

    def test_predict_workflow_with_history(self, tmp_path):
        """Test workflow prediction with sufficient history."""
        history_file = tmp_path / "history.json"
        learner = PatternLearner(history_file)

        now = datetime.now()
        context = SessionContext(
            files_changed=[],
            file_types=set(),
            directories=set(),
            has_tests=False,
            has_auth=False,
            has_api=False,
            has_frontend=True,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=now,
            last_activity=now,
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        # Record multiple sessions with same pattern
        for _ in range(5):
            learner.record_success(context, ["test-automator", "code-reviewer"], 300, "success")

        prediction = learner.predict_workflow(context)

        assert prediction is not None
        assert prediction.workflow_name == "auto_frontend"
        assert "test-automator" in prediction.agents_sequence
        assert prediction.confidence > 0


class TestContextDetector:
    """Tests for ContextDetector class."""

    def test_detect_from_files_python(self):
        """Test detecting context from Python files."""
        files = [
            Path("src/app.py"),
            Path("tests/test_app.py"),
        ]

        context = ContextDetector.detect_from_files(files)

        assert len(context.files_changed) == 2
        assert ".py" in context.file_types
        assert context.has_tests
        assert context.has_backend

    def test_detect_from_files_frontend(self):
        """Test detecting context from frontend files."""
        files = [
            Path("src/App.tsx"),
            Path("src/components/Button.jsx"),
            Path("src/styles.css"),
        ]

        context = ContextDetector.detect_from_files(files)

        assert ".tsx" in context.file_types
        assert ".jsx" in context.file_types
        assert ".css" in context.file_types
        assert context.has_frontend

    def test_detect_from_files_auth(self):
        """Test detecting auth context."""
        files = [Path("src/auth/login.py")]

        context = ContextDetector.detect_from_files(files)

        assert context.has_auth

    def test_detect_from_files_api(self):
        """Test detecting API context."""
        files = [
            Path("src/api/endpoints.py"),
            Path("src/routes/users.py"),
        ]

        context = ContextDetector.detect_from_files(files)

        assert context.has_api

    def test_detect_from_files_database(self):
        """Test detecting database context."""
        files = [
            Path("migrations/001_init.sql"),
            Path("schema/users.sql"),
        ]

        context = ContextDetector.detect_from_files(files)

        assert context.has_database

    @patch("subprocess.run")
    def test_detect_from_git_success(self, mock_run):
        """Test detecting files from git successfully."""
        mock_run.return_value = MagicMock(
            stdout="file1.py\nfile2.ts\n",
            returncode=0,
        )

        files = ContextDetector.detect_from_git()

        assert len(files) == 2
        assert Path("file1.py") in files
        assert Path("file2.ts") in files

    @patch("subprocess.run")
    def test_detect_from_git_failure(self, mock_run):
        """Test handling git detection failure."""
        mock_run.side_effect = Exception("Git error")

        files = ContextDetector.detect_from_git()

        assert files == []


class TestIntelligentAgent:
    """Tests for IntelligentAgent class."""

    def test_intelligent_agent_init(self, tmp_path):
        """Test initializing intelligent agent."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        assert agent.data_dir.exists()
        assert agent.learner is not None
        assert agent.context_detector is not None

    def test_analyze_context_with_files(self, tmp_path):
        """Test analyzing context with provided files."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("src/app.py"), Path("tests/test_app.py")]
        context = agent.analyze_context(files)

        assert context is not None
        assert context.has_tests
        assert context.has_backend

    @patch("claude_ctx_py.intelligence.ContextDetector.detect_from_git")
    def test_analyze_context_from_git(self, mock_git, tmp_path):
        """Test analyzing context from git."""
        mock_git.return_value = [Path("src/app.py")]

        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        context = agent.analyze_context()

        assert context is not None
        mock_git.assert_called_once()

    def test_get_recommendations(self, tmp_path):
        """Test getting recommendations."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("auth/login.py")]
        agent.analyze_context(files)

        recommendations = agent.get_recommendations()

        assert isinstance(recommendations, list)
        # Should get security recommendation for auth files
        assert any(r.agent_name == "security-auditor" for r in recommendations)

    def test_get_auto_activations(self, tmp_path):
        """Test getting auto-activations."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("auth/login.py")]
        agent.analyze_context(files)

        auto_activations = agent.get_auto_activations()

        assert isinstance(auto_activations, list)
        assert "security-auditor" in auto_activations

    def test_mark_auto_activated(self, tmp_path):
        """Test marking agent as auto-activated."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        agent.mark_auto_activated("test-automator")

        assert "test-automator" in agent.auto_activated

    def test_get_auto_activations_excludes_marked(self, tmp_path):
        """Test that marked agents are excluded from auto-activation."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("auth/login.py")]
        agent.analyze_context(files)

        # Mark as activated
        agent.mark_auto_activated("security-auditor")

        # Should not include already activated
        auto_activations = agent.get_auto_activations()
        assert "security-auditor" not in auto_activations

    def test_predict_workflow(self, tmp_path):
        """Test predicting workflow."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("src/app.py")]
        agent.analyze_context(files)

        prediction = agent.predict_workflow()

        # With no history, should return None
        assert prediction is None

    def test_record_session_success(self, tmp_path):
        """Test recording session success."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("src/app.py")]
        agent.analyze_context(files)

        agent.record_session_success(["test-automator"], 300, "success")

        # Should be saved to learner
        history_file = data_dir / "session_history.json"
        assert history_file.exists()

    def test_get_smart_suggestions(self, tmp_path):
        """Test getting smart suggestions."""
        data_dir = tmp_path / "intelligence"
        agent = IntelligentAgent(data_dir)

        files = [Path("auth/login.py")]
        agent.analyze_context(files)

        suggestions = agent.get_smart_suggestions()

        assert "agent_recommendations" in suggestions
        assert "workflow_prediction" in suggestions
        assert "context" in suggestions
        assert isinstance(suggestions["agent_recommendations"], list)
        assert suggestions["context"]["files_changed"] == 1
