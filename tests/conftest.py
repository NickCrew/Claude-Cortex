"""Pytest configuration and shared fixtures for cortex-plugin tests."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture
def temp_claude_dir(tmp_path):
    """Create a temporary cortex directory structure.

    Returns:
        Path to temporary cortex directory with standard structure
    """
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(exist_ok=True)

    # Create standard subdirectories
    (claude_dir / "skills").mkdir(exist_ok=True)
    (claude_dir / "community" / "skills").mkdir(parents=True, exist_ok=True)
    (claude_dir / "community" / "ratings").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".metrics" / "skills").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".metrics" / "exports").mkdir(parents=True, exist_ok=True)

    return claude_dir


@pytest.fixture
def sample_composition_map():
    """Sample composition map for testing dependency resolution.

    Returns:
        Dictionary mapping skill names to their dependencies
    """
    return {
        "skill-a": [],
        "skill-b": ["skill-a"],
        "skill-c": ["skill-a", "skill-b"],
        "skill-d": ["skill-c"],
        "skill-e": [],
    }


@pytest.fixture
def circular_composition_map():
    """Composition map with circular dependencies for testing.

    Returns:
        Dictionary with circular dependency: a -> b -> c -> a
    """
    return {
        "skill-a": ["skill-b"],
        "skill-b": ["skill-c"],
        "skill-c": ["skill-a"],
    }


@pytest.fixture
def composition_yaml_content():
    """Valid YAML content for composition.yaml file.

    Returns:
        String containing YAML content
    """
    return """skill-a:
  - dependency-1
  - dependency-2

skill-b:
  - skill-a
  - dependency-3

skill-c: []
"""


@pytest.fixture
def sample_skill_metadata():
    """Sample skill metadata for YAML frontmatter.

    Returns:
        Dictionary with valid skill metadata
    """
    return {
        "name": "react-hooks",
        "version": "1.0.0",
        "author": "Test Author",
        "license": "Apache-2.0",
        "description": "React hooks skill for testing",
        "tags": ["react", "frontend", "hooks"],
        "token_budget": 1500,
    }


@pytest.fixture
def sample_skill_file(temp_claude_dir, sample_skill_metadata):
    """Create a sample skill file with valid frontmatter.

    Args:
        temp_claude_dir: Temporary cortex directory
        sample_skill_metadata: Skill metadata for frontmatter

    Returns:
        Path to created skill file
    """
    skill_file = temp_claude_dir / "community" / "skills" / "react-hooks.md"

    content = f"""---
name: {sample_skill_metadata['name']}
version: {sample_skill_metadata['version']}
author: {sample_skill_metadata['author']}
license: {sample_skill_metadata['license']}
description: {sample_skill_metadata['description']}
tags:
{chr(10).join(f'  - {tag}' for tag in sample_skill_metadata['tags'])}
token_budget: {sample_skill_metadata['token_budget']}
---

## Purpose

This skill helps with React hooks patterns and best practices.

## Usage

Use this skill when working with React functional components.

## Examples

```javascript
const [state, setState] = useState(0);
```
"""

    skill_file.write_text(content, encoding="utf-8")
    return skill_file


@pytest.fixture
def sample_metrics():
    """Sample metrics data for testing.

    Returns:
        Dictionary with sample skill metrics
    """
    return {
        "skills": {
            "test-skill": {
                "activation_count": 10,
                "total_tokens_saved": 5000,
                "avg_tokens": 500,
                "success_rate": 0.9,
                "last_activated": "2025-10-01T10:00:00Z",
            },
            "another-skill": {
                "activation_count": 5,
                "total_tokens_saved": 2500,
                "avg_tokens": 500,
                "success_rate": 0.8,
                "last_activated": "2025-10-15T15:30:00Z",
            },
            "skill-c": {
                "activation_count": 3,
                "total_tokens_saved": 1200,
                "avg_tokens": 400,
                "success_rate": 0.7,
                "last_activated": "2025-09-20T08:00:00Z",
            },
        }
    }


@pytest.fixture
def metrics_file(temp_claude_dir, sample_metrics):
    """Create a metrics file with sample data.

    Args:
        temp_claude_dir: Temporary cortex directory
        sample_metrics: Sample metrics data

    Returns:
        Path to created metrics file
    """
    metrics_file = temp_claude_dir / ".metrics" / "skills" / "stats.json"
    metrics_file.write_text(json.dumps(sample_metrics, indent=2), encoding="utf-8")
    return metrics_file


@pytest.fixture
def sample_activations():
    """Sample activation log data for testing.

    Returns:
        Dictionary with sample activation records
    """
    return {
        "activations": [
            {
                "activation_id": "123e4567-e89b-12d3-a456-426614174000",
                "skill_name": "skill-a",
                "timestamp": "2025-10-17T10:00:00Z",
                "context": {
                    "agent": "main",
                    "task_type": "code_review",
                    "project_type": "python",
                    "co_activated_skills": ["skill-b"],
                },
                "metrics": {
                    "tokens_loaded": 1000,
                    "tokens_saved": 500,
                    "duration_ms": 150,
                    "success": True,
                },
                "effectiveness": {
                    "relevance_score": 0.9,
                    "completion_improvement": 0.3,
                    "user_satisfaction": 5,
                },
            },
            {
                "activation_id": "223e4567-e89b-12d3-a456-426614174001",
                "skill_name": "skill-b",
                "timestamp": "2025-10-17T11:00:00Z",
                "context": {
                    "agent": "main",
                    "task_type": "testing",
                    "project_type": "javascript",
                    "co_activated_skills": ["skill-a"],
                },
                "metrics": {
                    "tokens_loaded": 800,
                    "tokens_saved": 400,
                    "duration_ms": 120,
                    "success": True,
                },
                "effectiveness": {
                    "relevance_score": 0.85,
                    "completion_improvement": 0.25,
                    "user_satisfaction": 4,
                },
            },
        ]
    }


@pytest.fixture
def activations_file(temp_claude_dir, sample_activations):
    """Create an activations file with sample data.

    Args:
        temp_claude_dir: Temporary cortex directory
        sample_activations: Sample activations data

    Returns:
        Path to created activations file
    """
    activations_file = temp_claude_dir / ".metrics" / "skills" / "activations.json"
    activations_file.write_text(
        json.dumps(sample_activations, indent=2), encoding="utf-8"
    )
    return activations_file


@pytest.fixture
def mock_yaml_file(temp_claude_dir, monkeypatch):
    """Create a mock YAML file and return a function to write content to it.

    Args:
        temp_claude_dir: Temporary cortex directory
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Function that takes YAML content and writes it to composition.yaml
    """
    def write_yaml(content: str):
        yaml_file = temp_claude_dir / "skills" / "composition.yaml"
        yaml_file.write_text(content, encoding="utf-8")
        return yaml_file

    return write_yaml


@pytest.fixture
def skill_versions_dir(temp_claude_dir):
    """Create skill version directories for testing.

    Creates:
        - pdf@1.0.0
        - pdf@1.5.3
        - pdf@2.0.0
        - pdf@2.1.0

    Args:
        temp_claude_dir: Temporary cortex directory

    Returns:
        List of created skill version directories
    """
    skills_dir = temp_claude_dir / "skills"
    versions = ["1.0.0", "1.5.3", "2.0.0", "2.1.0"]

    created_dirs = []
    for version in versions:
        skill_dir = skills_dir / f"pdf@{version}"
        skill_dir.mkdir()

        # Create a simple metadata file
        metadata_file = skill_dir / "skill.yaml"
        metadata_file.write_text(
            f"name: pdf\nversion: {version}\ndescription: PDF skill\n",
            encoding="utf-8"
        )
        created_dirs.append(skill_dir)

    return created_dirs


@pytest.fixture
def tmp_claude_dir(tmp_path):
    """Alias for temp_claude_dir for compatibility with existing tests.

    Returns:
        Path to temporary cortex directory
    """
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(exist_ok=True)

    # Create standard subdirectories
    (claude_dir / "skills").mkdir(exist_ok=True)
    (claude_dir / "community" / "skills").mkdir(parents=True, exist_ok=True)
    (claude_dir / "community" / "ratings").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".metrics" / "skills").mkdir(parents=True, exist_ok=True)
    (claude_dir / ".metrics" / "exports").mkdir(parents=True, exist_ok=True)

    return claude_dir


@pytest.fixture
def mock_claude_home(tmp_claude_dir, monkeypatch):
    """Mock the Claude plugin root environment variable.

    Args:
        tmp_claude_dir: Temporary cortex directory
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Path to temporary cortex directory
    """
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_claude_dir))
    return tmp_claude_dir


@pytest.fixture(autouse=True)
def clean_claude_env(monkeypatch):
    """Ensure a clean environment for each test."""
    monkeypatch.delenv("CORTEX_SCOPE", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
    monkeypatch.delenv("CORTEX_ROOT", raising=False)
