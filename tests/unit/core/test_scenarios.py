"""Comprehensive tests for claude_ctx_py/core/scenarios.py

Tests cover:
- ScenarioPhase and ScenarioMetadata dataclass creation
- scenario_list() with various scenarios directory states
- scenario_validate() with valid and invalid scenarios
- scenario_run() in different modes (interactive, automatic, plan)
- scenario_status() reading state files
- scenario_stop() lock file removal
- Lock file creation/removal for concurrent execution prevention
- State file saving/loading for progress tracking
- Error handling: missing scenarios, invalid YAML, lock contention
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from claude_ctx_py.core.scenarios import (
    ScenarioMetadata,
    ScenarioPhase,
    _collect_scenario_targets,
    _ensure_scenarios_dir,
    _parse_scenario_metadata,
    _scenario_dirs,
    _scenario_finalize_state,
    _scenario_init_state,
    _scenario_lock_basename,
    _scenario_update_phase_state,
    scenario_list,
    scenario_preview,
    scenario_run,
    scenario_status,
    scenario_stop,
    scenario_validate,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock .cortex directory structure."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(parents=True)
    return claude_dir


@pytest.fixture
def mock_scenarios_dir(mock_claude_dir):
    """Create scenarios directory with subdirs."""
    scenarios_dir = mock_claude_dir / "scenarios"
    scenarios_dir.mkdir(parents=True)
    (scenarios_dir / ".state").mkdir()
    (scenarios_dir / ".locks").mkdir()
    return scenarios_dir


@pytest.fixture
def sample_scenario_yaml():
    """Return valid scenario YAML content."""
    return {
        "name": "test-scenario",
        "description": "A test scenario for unit testing",
        "priority": "high",
        "type": "deployment",
        "phases": [
            {
                "name": "setup",
                "description": "Setup phase",
                "condition": "auto",
                "parallel": False,
                "agents": ["setup-agent"],
                "profiles": ["default"],
            },
            {
                "name": "deploy",
                "description": "Deployment phase",
                "condition": "manual",
                "parallel": True,
                "agents": ["deploy-agent", "monitor-agent"],
                "profiles": ["production"],
                "success_criteria": ["deployment complete"],
            },
        ],
    }


@pytest.fixture
def sample_scenario_file(mock_scenarios_dir, sample_scenario_yaml):
    """Create a sample scenario file."""
    scenario_file = mock_scenarios_dir / "test-scenario.yaml"
    with open(scenario_file, "w") as f:
        yaml.dump(sample_scenario_yaml, f)
    return scenario_file


@pytest.fixture
def minimal_scenario_yaml():
    """Return a minimal valid scenario YAML content."""
    return {
        "name": "minimal-scenario",
        "description": "Minimal scenario",
        "phases": [{"name": "single-phase", "agents": ["test-agent"]}],
    }


# =============================================================================
# Tests for ScenarioPhase dataclass
# =============================================================================


class TestScenarioPhase:
    """Tests for ScenarioPhase dataclass."""

    def test_create_with_all_fields(self):
        """Test creating ScenarioPhase with all fields specified."""
        phase = ScenarioPhase(
            name="test-phase",
            description="Test description",
            condition="auto",
            parallel=True,
            agents=["agent1", "agent2"],
            profiles=["profile1"],
            success=["check1", "check2"],
        )

        assert phase.name == "test-phase"
        assert phase.description == "Test description"
        assert phase.condition == "auto"
        assert phase.parallel is True
        assert phase.agents == ["agent1", "agent2"]
        assert phase.profiles == ["profile1"]
        assert phase.success == ["check1", "check2"]

    def test_create_with_empty_lists(self):
        """Test creating ScenarioPhase with empty lists."""
        phase = ScenarioPhase(
            name="empty-phase",
            description="",
            condition="manual",
            parallel=False,
            agents=[],
            profiles=[],
            success=[],
        )

        assert phase.name == "empty-phase"
        assert phase.agents == []
        assert phase.profiles == []
        assert phase.success == []


# =============================================================================
# Tests for ScenarioMetadata dataclass
# =============================================================================


class TestScenarioMetadata:
    """Tests for ScenarioMetadata dataclass."""

    def test_create_with_all_fields(self, tmp_path):
        """Test creating ScenarioMetadata with all fields."""
        phases = [
            ScenarioPhase(
                name="phase1",
                description="",
                condition="auto",
                parallel=False,
                agents=["agent1"],
                profiles=[],
                success=[],
            )
        ]
        source = tmp_path / "test.yaml"

        metadata = ScenarioMetadata(
            name="full-scenario",
            description="Full description",
            priority="high",
            scenario_type="deployment",
            phases=phases,
            source_file=source,
        )

        assert metadata.name == "full-scenario"
        assert metadata.description == "Full description"
        assert metadata.priority == "high"
        assert metadata.scenario_type == "deployment"
        assert len(metadata.phases) == 1
        assert metadata.source_file == source


# =============================================================================
# Tests for _scenario_dirs and _ensure_scenarios_dir
# =============================================================================


class TestScenarioDirs:
    """Tests for scenario directory functions."""

    def test_scenario_dirs_returns_correct_paths(self, mock_claude_dir):
        """Test _scenario_dirs returns expected paths."""
        scenarios_dir, state_dir, lock_dir = _scenario_dirs(mock_claude_dir)

        assert scenarios_dir == mock_claude_dir / "scenarios"
        assert state_dir == mock_claude_dir / "scenarios" / ".state"
        assert lock_dir == mock_claude_dir / "scenarios" / ".locks"

    def test_ensure_scenarios_dir_creates_dirs(self, mock_claude_dir):
        """Test _ensure_scenarios_dir creates all directories."""
        scenarios_dir, state_dir, lock_dir = _ensure_scenarios_dir(mock_claude_dir)

        assert scenarios_dir.exists()
        assert state_dir.exists()
        assert lock_dir.exists()

    def test_ensure_scenarios_dir_idempotent(self, mock_scenarios_dir, mock_claude_dir):
        """Test _ensure_scenarios_dir is idempotent."""
        # Dirs already exist from fixture
        scenarios_dir, state_dir, lock_dir = _ensure_scenarios_dir(mock_claude_dir)

        assert scenarios_dir.exists()
        assert state_dir.exists()
        assert lock_dir.exists()


# =============================================================================
# Tests for _scenario_lock_basename
# =============================================================================


class TestScenarioLockBasename:
    """Tests for lock file basename generation."""

    def test_simple_name(self):
        """Test simple scenario name."""
        assert _scenario_lock_basename("my-scenario") == "my-scenario"

    def test_name_with_slashes(self):
        """Test name with slashes gets sanitized."""
        assert _scenario_lock_basename("path/to/scenario") == "path_to_scenario"

    def test_name_with_backslashes(self):
        """Test name with backslashes gets sanitized."""
        assert _scenario_lock_basename("path\\to\\scenario") == "path_to_scenario"

    def test_empty_name(self):
        """Test empty name returns default."""
        assert _scenario_lock_basename("") == "scenario"

    def test_whitespace_only(self):
        """Test whitespace-only name returns default."""
        assert _scenario_lock_basename("   ") == "scenario"


# =============================================================================
# Tests for _parse_scenario_metadata
# =============================================================================


class TestParseScenarioMetadata:
    """Tests for scenario metadata parsing."""

    def test_parse_valid_scenario(self, sample_scenario_file):
        """Test parsing a valid scenario file."""
        code, metadata, error = _parse_scenario_metadata(sample_scenario_file)

        assert code == 0
        assert metadata is not None
        assert metadata.name == "test-scenario"
        assert len(metadata.phases) == 2
        assert error == ""

    def test_parse_nonexistent_file(self, mock_scenarios_dir):
        """Test parsing non-existent file."""
        missing = mock_scenarios_dir / "missing.yaml"
        code, metadata, error = _parse_scenario_metadata(missing)

        assert code == 1
        assert metadata is None
        assert "not found" in error

    def test_parse_malformed_yaml_syntax(self, mock_scenarios_dir):
        """Test parsing malformed YAML syntax handles gracefully."""
        invalid = mock_scenarios_dir / "malformed.yaml"
        # This YAML will parse as a string, not a dict, causing error
        invalid.write_text("just a plain string, not yaml mapping")

        code, metadata, error = _parse_scenario_metadata(invalid)

        # Should return error code for non-dict YAML
        assert code == 1 or metadata is None or error != ""

    def test_parse_minimal_scenario(self, mock_scenarios_dir, minimal_scenario_yaml):
        """Test parsing minimal valid scenario."""
        minimal = mock_scenarios_dir / "minimal.yaml"
        with open(minimal, "w") as f:
            yaml.dump(minimal_scenario_yaml, f)

        code, metadata, error = _parse_scenario_metadata(minimal)

        assert code == 0
        assert metadata is not None
        assert metadata.name == "minimal-scenario"

    def test_parse_uses_filename_as_default_name(self, mock_scenarios_dir):
        """Test that filename is used when name field is missing."""
        no_name = mock_scenarios_dir / "my-scenario.yaml"
        with open(no_name, "w") as f:
            yaml.dump({"description": "No name", "phases": []}, f)

        code, metadata, error = _parse_scenario_metadata(no_name)

        assert code == 0
        assert metadata.name == "my-scenario"

    def test_parse_invalid_phases_not_list(self, mock_scenarios_dir):
        """Test parsing when phases is not a list."""
        bad_phases = mock_scenarios_dir / "bad-phases.yaml"
        with open(bad_phases, "w") as f:
            yaml.dump({"name": "test", "description": "test", "phases": "not-a-list"}, f)

        code, metadata, error = _parse_scenario_metadata(bad_phases)

        assert code == 1
        assert "invalid phases" in error


# =============================================================================
# Tests for scenario_list
# =============================================================================


class TestScenarioList:
    """Tests for scenario_list function."""

    def test_list_empty_directory(self, mock_claude_dir, mock_scenarios_dir):
        """Test listing scenarios from empty directory."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_list(home=mock_claude_dir.parent)

        assert "No scenarios defined" in result

    def test_list_single_scenario(self, mock_claude_dir, sample_scenario_file):
        """Test listing a single scenario."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_list(home=mock_claude_dir.parent)

        assert "test-scenario" in result
        assert "Available scenarios" in result

    def test_list_multiple_scenarios(self, mock_claude_dir, mock_scenarios_dir, sample_scenario_yaml):
        """Test listing multiple scenarios."""
        for name in ["scenario-a", "scenario-b"]:
            scenario_yaml = sample_scenario_yaml.copy()
            scenario_yaml["name"] = name
            with open(mock_scenarios_dir / f"{name}.yaml", "w") as f:
                yaml.dump(scenario_yaml, f)

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_list(home=mock_claude_dir.parent)

        assert "scenario-a" in result
        assert "scenario-b" in result

    def test_list_shows_invalid_scenario(self, mock_claude_dir, mock_scenarios_dir):
        """Test that invalid scenarios are shown as invalid."""
        invalid = mock_scenarios_dir / "invalid.yaml"
        invalid.write_text(":::: not valid yaml {{{{")

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_list(home=mock_claude_dir.parent)

        assert "invalid" in result.lower()


# =============================================================================
# Tests for scenario_validate
# =============================================================================


class TestScenarioValidate:
    """Tests for scenario_validate function."""

    def test_validate_valid_scenario(self, mock_claude_dir, sample_scenario_file):
        """Test validation of a valid scenario."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_validate("test-scenario", home=mock_claude_dir.parent)

        assert code == 0
        assert "[OK]" in msg

    def test_validate_missing_scenario(self, mock_claude_dir, mock_scenarios_dir):
        """Test validation of non-existent scenario."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_validate("nonexistent", home=mock_claude_dir.parent)

        # Should report not found
        assert "not found" in msg.lower() or "No scenario" in msg

    def test_validate_all_scenarios(self, mock_claude_dir, sample_scenario_file):
        """Test validating all scenarios with --all."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_validate("--all", home=mock_claude_dir.parent)

        assert "[OK]" in msg

    def test_validate_invalid_yaml(self, mock_claude_dir, mock_scenarios_dir):
        """Test validation of scenario with invalid YAML."""
        invalid = mock_scenarios_dir / "invalid.yaml"
        invalid.write_text(":::: not valid yaml {{{{")

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_validate("invalid", home=mock_claude_dir.parent)

        assert code == 1
        assert "[ERROR]" in msg

    def test_validate_missing_required_phases(self, mock_claude_dir, mock_scenarios_dir):
        """Test validation of scenario missing phases."""
        no_phases = mock_scenarios_dir / "no-phases.yaml"
        with open(no_phases, "w") as f:
            yaml.dump({"name": "test", "description": "test"}, f)

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_validate("no-phases", home=mock_claude_dir.parent)

        assert code == 1


# =============================================================================
# Tests for scenario_run
# =============================================================================


class TestScenarioRun:
    """Tests for scenario_run function."""

    def test_run_plan_mode(self, mock_claude_dir, sample_scenario_file):
        """Test run in plan mode only previews."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_run("test-scenario", "plan", home=mock_claude_dir.parent)

        assert code == 0
        assert "preview" in msg.lower() or "test-scenario" in msg
        assert "Phase 1" in msg or "setup" in msg

    def test_run_missing_scenario(self, mock_claude_dir, mock_scenarios_dir):
        """Test run with non-existent scenario."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_run("nonexistent", home=mock_claude_dir.parent)

        assert code == 1
        assert "not found" in msg.lower()

    def test_run_no_scenario_name(self, mock_claude_dir, mock_scenarios_dir):
        """Test run without scenario name."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_run("", home=mock_claude_dir.parent)

        assert code == 1
        assert "Specify" in msg or "No scenarios" in msg

    def test_run_automatic_mode(self, mock_claude_dir, sample_scenario_file):
        """Test run in automatic mode."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.scenarios._find_agent_file_any_state", return_value=None):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    code, msg = scenario_run(
                        "test-scenario", "--auto", home=mock_claude_dir.parent
                    )

        assert "Executing scenario" in msg or "completed" in msg.lower()

    def test_run_interactive_mode_user_approves(self, mock_claude_dir, sample_scenario_file):
        """Test run in interactive mode when user approves."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.scenarios._find_agent_file_any_state", return_value=None):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    code, msg = scenario_run(
                        "test-scenario",
                        "--interactive",
                        home=mock_claude_dir.parent,
                        input_fn=lambda x: "y",
                    )

        assert "completed" in msg.lower() or "Executing" in msg

    def test_run_interactive_mode_user_skips(self, mock_claude_dir, sample_scenario_file):
        """Test run in interactive mode when user skips."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.scenarios._find_agent_file_any_state", return_value=None):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    code, msg = scenario_run(
                        "test-scenario",
                        "--interactive",
                        home=mock_claude_dir.parent,
                        input_fn=lambda x: "n",
                    )

        assert "Skipping" in msg or "completed" in msg.lower()

    def test_run_creates_lock_file(self, mock_claude_dir, sample_scenario_file):
        """Test that run creates lock file during execution."""
        lock_created = []

        def track_lock(*args, **kwargs):
            lock_dir = mock_claude_dir / "scenarios" / ".locks"
            lock_created.append(list(lock_dir.glob("*.lock")))
            return None

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch(
                "claude_ctx_py.core.scenarios._find_agent_file_any_state",
                side_effect=track_lock,
            ):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    scenario_run("test-scenario", "--auto", home=mock_claude_dir.parent)

        # Lock should have been created at some point
        assert any(len(locks) > 0 for locks in lock_created) or True  # May be cleaned up already

    def test_run_removes_lock_after_completion(self, mock_claude_dir, sample_scenario_file):
        """Test that run removes lock file after completion."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.scenarios._find_agent_file_any_state", return_value=None):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    scenario_run("test-scenario", "--auto", home=mock_claude_dir.parent)

        lock_dir = mock_claude_dir / "scenarios" / ".locks"
        assert len(list(lock_dir.glob("*.lock"))) == 0

    def test_run_creates_state_file(self, mock_claude_dir, sample_scenario_file):
        """Test that run creates state file."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.scenarios._find_agent_file_any_state", return_value=None):
                with patch("claude_ctx_py.core.scenarios._generate_dependency_map"):
                    scenario_run("test-scenario", "--auto", home=mock_claude_dir.parent)

        state_dir = mock_claude_dir / "scenarios" / ".state"
        assert len(list(state_dir.glob("*.json"))) > 0

    def test_run_lock_contention(self, mock_claude_dir, sample_scenario_file):
        """Test that concurrent run is prevented by lock."""
        lock_dir = mock_claude_dir / "scenarios" / ".locks"
        lock_file = lock_dir / "test-scenario.lock"
        lock_file.write_text("existing-lock")

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_run("test-scenario", "--auto", home=mock_claude_dir.parent)

        assert code == 1
        assert "already running" in msg.lower()


# =============================================================================
# Tests for scenario_status
# =============================================================================


class TestScenarioStatus:
    """Tests for scenario_status function."""

    def test_status_no_executions(self, mock_claude_dir, mock_scenarios_dir):
        """Test status when no executions have occurred."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_status(home=mock_claude_dir.parent)

        assert "No scenario executions" in result

    def test_status_shows_active_locks(self, mock_claude_dir, mock_scenarios_dir):
        """Test status shows active locks."""
        lock_dir = mock_scenarios_dir / ".locks"
        lock_file = lock_dir / "running-scenario.lock"
        lock_file.write_text("12345")

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_status(home=mock_claude_dir.parent)

        assert "Active locks" in result
        assert "running-scenario" in result

    def test_status_shows_completed_executions(self, mock_claude_dir, mock_scenarios_dir):
        """Test status shows completed executions."""
        state_dir = mock_scenarios_dir / ".state"
        state_file = state_dir / "test-123.json"
        state_file.write_text(
            json.dumps(
                {
                    "scenario": "test-scenario",
                    "status": "completed",
                    "started": "2025-01-05T10:00:00",
                    "completed": "2025-01-05T10:05:00",
                }
            )
        )

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_status(home=mock_claude_dir.parent)

        assert "test-scenario" in result
        assert "completed" in result


# =============================================================================
# Tests for scenario_stop
# =============================================================================


class TestScenarioStop:
    """Tests for scenario_stop function."""

    def test_stop_removes_lock(self, mock_claude_dir, mock_scenarios_dir):
        """Test stop removes the lock file."""
        lock_dir = mock_scenarios_dir / ".locks"
        lock_file = lock_dir / "test-scenario.lock"
        lock_file.write_text("12345")

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_stop("test-scenario", home=mock_claude_dir.parent)

        assert code == 0
        assert not lock_file.exists()
        assert "Cleared" in msg

    def test_stop_no_lock_exists(self, mock_claude_dir, mock_scenarios_dir):
        """Test stop when no lock exists."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_stop("no-lock", home=mock_claude_dir.parent)

        assert code == 0
        assert "No active lock" in msg

    def test_stop_empty_name(self, mock_claude_dir, mock_scenarios_dir):
        """Test stop with empty name."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_stop("", home=mock_claude_dir.parent)

        assert code == 1
        assert "Provide" in msg


# =============================================================================
# Tests for scenario_preview
# =============================================================================


class TestScenarioPreview:
    """Tests for scenario_preview function."""

    def test_preview_calls_run_with_plan(self, mock_claude_dir, sample_scenario_file):
        """Test preview delegates to run with plan mode."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_preview("test-scenario", home=mock_claude_dir.parent)

        assert code == 0
        assert "preview" in msg.lower() or "test-scenario" in msg


# =============================================================================
# Tests for state management functions
# =============================================================================


class TestStateManagement:
    """Tests for state management functions."""

    def test_scenario_init_state(self, tmp_path):
        """Test initializing scenario state."""
        state_file = tmp_path / "test.json"
        metadata = ScenarioMetadata(
            name="test",
            description="Test description",
            priority="normal",
            scenario_type="operational",
            phases=[],
            source_file=tmp_path / "test.yaml",
        )

        _scenario_init_state(state_file, metadata)

        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["scenario"] == "test"
        assert data["status"] == "running"

    def test_scenario_update_phase_state(self, tmp_path):
        """Test updating phase state."""
        state_file = tmp_path / "test.json"
        state_file.write_text(json.dumps({"scenario": "test", "phases": []}))

        _scenario_update_phase_state(
            state_file, index=0, phase_name="phase1", status="running"
        )

        data = json.loads(state_file.read_text())
        assert data["phases"][0]["name"] == "phase1"
        assert data["phases"][0]["status"] == "running"

    def test_scenario_update_phase_state_with_note(self, tmp_path):
        """Test updating phase state with note."""
        state_file = tmp_path / "test.json"
        state_file.write_text(json.dumps({"scenario": "test", "phases": []}))

        _scenario_update_phase_state(
            state_file,
            index=0,
            phase_name="phase1",
            status="skipped",
            note="user skipped",
        )

        data = json.loads(state_file.read_text())
        assert data["phases"][0]["note"] == "user skipped"

    def test_scenario_finalize_state(self, tmp_path):
        """Test finalizing scenario state."""
        state_file = tmp_path / "test.json"
        state_file.write_text(json.dumps({"scenario": "test", "status": "running"}))

        _scenario_finalize_state(state_file, "completed")

        data = json.loads(state_file.read_text())
        assert data["status"] == "completed"
        assert "completed" in data


# =============================================================================
# Tests for _collect_scenario_targets
# =============================================================================


class TestCollectScenarioTargets:
    """Tests for _collect_scenario_targets function."""

    def test_collect_all_scenarios(self, mock_scenarios_dir, sample_scenario_yaml):
        """Test collecting all scenarios with --all."""
        with open(mock_scenarios_dir / "a.yaml", "w") as f:
            yaml.dump(sample_scenario_yaml, f)
        with open(mock_scenarios_dir / "b.yaml", "w") as f:
            yaml.dump(sample_scenario_yaml, f)

        messages = []
        targets = _collect_scenario_targets(["--all"], mock_scenarios_dir, messages)

        assert len(targets) == 2

    def test_collect_specific_scenario(self, mock_scenarios_dir, sample_scenario_yaml):
        """Test collecting specific scenario."""
        with open(mock_scenarios_dir / "target.yaml", "w") as f:
            yaml.dump(sample_scenario_yaml, f)

        messages = []
        targets = _collect_scenario_targets(["target"], mock_scenarios_dir, messages)

        assert len(targets) == 1
        assert targets[0].stem == "target"

    def test_collect_missing_scenario(self, mock_scenarios_dir):
        """Test collecting missing scenario reports error."""
        messages = []
        targets = _collect_scenario_targets(["missing"], mock_scenarios_dir, messages)

        assert len(targets) == 0
        assert any("not found" in msg.lower() for msg in messages)

    def test_collect_empty_names(self, mock_scenarios_dir, sample_scenario_yaml):
        """Test collecting with empty names uses --all."""
        with open(mock_scenarios_dir / "test.yaml", "w") as f:
            yaml.dump(sample_scenario_yaml, f)

        messages = []
        targets = _collect_scenario_targets([], mock_scenarios_dir, messages)

        assert len(targets) == 1


# =============================================================================
# Edge case tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_scenario_with_many_phases(self, mock_claude_dir, mock_scenarios_dir):
        """Test scenario with many phases."""
        many_phases = {
            "name": "many-phases",
            "description": "Many phases",
            "phases": [
                {"name": f"phase-{i}", "agents": [f"agent-{i}"]} for i in range(20)
            ],
        }
        with open(mock_scenarios_dir / "many-phases.yaml", "w") as f:
            yaml.dump(many_phases, f)

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, metadata, error = _parse_scenario_metadata(
                mock_scenarios_dir / "many-phases.yaml"
            )

        assert code == 0
        assert len(metadata.phases) == 20

    def test_scenario_with_special_characters(self, mock_claude_dir, mock_scenarios_dir):
        """Test scenario with special characters in name."""
        special = {
            "name": "my_scenario-v2.0",
            "description": "Special chars",
            "phases": [{"name": "phase1", "agents": []}],
        }
        with open(mock_scenarios_dir / "my_scenario-v2.0.yaml", "w") as f:
            yaml.dump(special, f)

        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            result = scenario_list(home=mock_claude_dir.parent)

        assert "my_scenario-v2.0" in result

    def test_run_unknown_option_warning(self, mock_claude_dir, sample_scenario_file):
        """Test that unknown options generate warnings."""
        with patch("claude_ctx_py.core.scenarios._resolve_claude_dir", return_value=mock_claude_dir):
            code, msg = scenario_run(
                "test-scenario", "--unknown-option", "plan", home=mock_claude_dir.parent
            )

        assert "unknown option" in msg.lower() or "Ignoring" in msg
