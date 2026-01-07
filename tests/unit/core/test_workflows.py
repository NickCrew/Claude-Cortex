"""Unit tests for core.workflows module."""

import time
from pathlib import Path
from unittest import mock
import pytest
from claude_ctx_py.core import workflows

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def temp_claude_dir(tmp_path):
    """Create a temporary .cortex directory structure."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir()
    (claude_dir / "workflows").mkdir()
    (claude_dir / "tasks").mkdir()
    (claude_dir / "tasks" / "current").mkdir()
    return claude_dir

@pytest.fixture
def sample_workflow(temp_claude_dir):
    """Create a sample workflow file."""
    workflow_path = temp_claude_dir / "workflows" / "deploy-prod.yaml"
    content = """name: Deploy to Production
description: Deploys the current build to production environment
steps:
  - name: Build
    command: just build
  - name: Test
    command: just test
  - name: Deploy
    command: just deploy
"""
    workflow_path.write_text(content, encoding="utf-8")
    return "deploy-prod"

# --------------------------------------------------------------------------- workflow_list

def test_workflow_list_empty(temp_claude_dir, monkeypatch):
    """Test listing workflows when none exist."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    result = workflows.workflow_list()
    # It returns just the header if empty
    assert "Available workflows:" in result
    assert "deploy-prod" not in result

def test_workflow_list_valid(temp_claude_dir, sample_workflow, monkeypatch):
    """Test listing available workflows."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    result = workflows.workflow_list()
    assert "Available workflows:" in result
    assert "deploy-prod" in result
    assert "Deploys the current build to production environment" in result

def test_workflow_list_missing_dir(tmp_path, monkeypatch):
    """Test listing when workflows directory is missing."""
    empty_home = tmp_path / "empty"
    empty_home.mkdir()
    (empty_home / ".cortex").mkdir()
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: empty_home / ".cortex")
    
    result = workflows.workflow_list()
    # Returns just header if directory missing
    assert "Available workflows:" in result

# --------------------------------------------------------------------------- workflow_run

def test_workflow_run_success(temp_claude_dir, sample_workflow, monkeypatch):
    """Test starting a workflow successfully."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    exit_code, msg = workflows.workflow_run("deploy-prod")
    
    assert exit_code == 0
    assert "Started workflow: deploy-prod" in msg
    
    # Check state files
    state_dir = temp_claude_dir / "tasks" / "current"
    assert (state_dir / "active_workflow").read_text() == "deploy-prod"
    # Implementation sets status to 'pending'
    assert (state_dir / "workflow_status").read_text() == "pending"

def test_workflow_run_not_found(temp_claude_dir, monkeypatch):
    """Test running a non-existent workflow."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    exit_code, msg = workflows.workflow_run("missing-workflow")
    
    assert exit_code == 1
    # Implementation uses repr() for workflow name: "Workflow 'missing-workflow' not found"
    assert "Workflow 'missing-workflow' not found" in msg

def test_workflow_run_overwrites_active(temp_claude_dir, sample_workflow, monkeypatch):
    """Test running a workflow when one is already active (overwrites)."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    # Set active state
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("existing-workflow")
    
    # Implementation currently overwrites active workflow
    exit_code, msg = workflows.workflow_run("deploy-prod")
    
    assert exit_code == 0
    assert "Started workflow: deploy-prod" in msg
    assert (state_dir / "active_workflow").read_text() == "deploy-prod"

# --------------------------------------------------------------------------- workflow_status

def test_workflow_status_none_active(temp_claude_dir, monkeypatch):
    """Test status when no workflow is active."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    exit_code, result = workflows.workflow_status()
    assert exit_code == 0
    assert "No active workflow" in result

def test_workflow_status_running(temp_claude_dir, monkeypatch):
    """Test status of a running workflow."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("test-workflow")
    (state_dir / "workflow_status").write_text("running")
    (state_dir / "current_step").write_text("2")
    (state_dir / "workflow_started").write_text(str(int(time.time()) - 3600))  # 1 hour ago
    
    exit_code, result = workflows.workflow_status()
    
    assert exit_code == 0
    assert "=== Active Workflow ===" in result
    assert "Workflow: \x1b[0;32mtest-workflow\x1b[0m" in result
    assert "Status: running" in result
    assert "Elapsed time: 1h 0m" in result
    assert "Current step: \x1b[0;33m2\x1b[0m" in result

def test_workflow_status_missing_state_files(temp_claude_dir, monkeypatch):
    """Test status when state files are incomplete."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("test-workflow")
    # Missing other files
    
    exit_code, result = workflows.workflow_status()
    
    assert exit_code == 0
    assert "Status: unknown" in result
    # Elapsed time calculation uses 0 if file missing -> huge elapsed time relative to epoch 0
    # or current time if 0. Implementation: int(time.time()) - 0.
    # So elapsed time will be huge. We just check output structure.
    assert "Workflow: \x1b[0;32mtest-workflow\x1b[0m" in result

# --------------------------------------------------------------------------- workflow_stop

def test_workflow_stop_success(temp_claude_dir, monkeypatch):
    """Test stopping an active workflow."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("test-workflow")
    
    exit_code, msg = workflows.workflow_stop("test-workflow")
    
    assert exit_code == 0
    assert "Stopped workflow 'test-workflow'" in msg
    assert not (state_dir / "active_workflow").exists()

def test_workflow_stop_no_active(temp_claude_dir, monkeypatch):
    """Test stopping when no workflow is active."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    # Implementation returns 0 if no active workflow
    exit_code, msg = workflows.workflow_stop()
    
    assert exit_code == 0
    assert "No active workflow to stop" in msg

def test_workflow_stop_mismatch(temp_claude_dir, monkeypatch):
    """Test stopping a specific workflow that isn't the active one."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("active-one")
    
    exit_code, msg = workflows.workflow_stop("other-one")
    
    assert exit_code == 1
    assert "Active workflow 'active-one' does not match 'other-one'" in msg

# --------------------------------------------------------------------------- workflow_resume

def test_workflow_resume_success(temp_claude_dir, monkeypatch):
    """Test resuming a workflow."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    state_dir = temp_claude_dir / "tasks" / "current"
    (state_dir / "active_workflow").write_text("test-workflow")
    
    exit_code, msg = workflows.workflow_resume()
    
    assert exit_code == 0
    assert "Resuming workflow: test-workflow" in msg

def test_workflow_resume_none_active(temp_claude_dir, monkeypatch):
    """Test resuming when no workflow is active."""
    monkeypatch.setattr(workflows, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    exit_code, msg = workflows.workflow_resume()
    
    assert exit_code == 1
    assert "No workflow to resume" in msg
