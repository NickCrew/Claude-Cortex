"""Tests for context-driven skill suggestion module.

This module tests the suggester.py module which detects project
types and suggests appropriate skills based on detected technologies.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claude_ctx_py.suggester import (
    detect_project_type,
    format_suggestions,
    suggest_complementary_skills,
    suggest_skills_for_project,
)


class TestDetectProjectType:
    """Tests for detect_project_type function."""

    def test_empty_directory(self, tmp_path):
        """Empty directory returns all false flags."""
        result = detect_project_type(tmp_path)
        assert result.get("has_python", False) is False
        assert result.get("has_typescript", False) is False
        assert result.get("has_kubernetes", False) is False

    # Python detection
    def test_detects_python_requirements_txt(self, tmp_path):
        """Detects Python from requirements.txt."""
        (tmp_path / "requirements.txt").write_text("flask==2.0.0")
        result = detect_project_type(tmp_path)
        assert result["has_python"] is True

    def test_detects_python_pyproject_toml(self, tmp_path):
        """Detects Python from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        result = detect_project_type(tmp_path)
        assert result["has_python"] is True

    def test_detects_python_setup_py(self, tmp_path):
        """Detects Python from setup.py."""
        (tmp_path / "setup.py").write_text("")
        result = detect_project_type(tmp_path)
        assert result["has_python"] is True

    def test_detects_python_pipfile(self, tmp_path):
        """Detects Python from Pipfile."""
        (tmp_path / "Pipfile").write_text("")
        result = detect_project_type(tmp_path)
        assert result["has_python"] is True

    def test_detects_fastapi(self, tmp_path):
        """Detects FastAPI from requirements.txt."""
        (tmp_path / "requirements.txt").write_text("fastapi==0.100.0\nuvicorn")
        result = detect_project_type(tmp_path)
        assert result.get("has_fastapi") is True

    def test_detects_django(self, tmp_path):
        """Detects Django from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text(
            "[project]\ndependencies=['django>=4.0']"
        )
        result = detect_project_type(tmp_path)
        assert result.get("has_django") is True

    # JavaScript/TypeScript detection
    def test_detects_javascript_package_json(self, tmp_path):
        """Detects JavaScript from package.json."""
        (tmp_path / "package.json").write_text("{}")
        result = detect_project_type(tmp_path)
        assert result["has_javascript"] is True

    def test_detects_typescript_tsconfig(self, tmp_path):
        """Detects TypeScript from tsconfig.json."""
        (tmp_path / "tsconfig.json").write_text("{}")
        result = detect_project_type(tmp_path)
        assert result["has_typescript"] is True

    def test_detects_typescript_in_deps(self, tmp_path):
        """Detects TypeScript from package.json dependencies."""
        package_data = {"devDependencies": {"typescript": "^5.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result["has_typescript"] is True

    def test_detects_react(self, tmp_path):
        """Detects React from package.json dependencies."""
        package_data = {"dependencies": {"react": "^18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result.get("has_react") is True

    def test_detects_vue(self, tmp_path):
        """Detects Vue from package.json dependencies."""
        package_data = {"dependencies": {"vue": "^3.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result.get("has_vue") is True

    def test_detects_angular(self, tmp_path):
        """Detects Angular from package.json dependencies."""
        package_data = {"dependencies": {"@angular/core": "^16.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result.get("has_angular") is True

    def test_detects_nextjs(self, tmp_path):
        """Detects Next.js from package.json dependencies."""
        package_data = {"dependencies": {"next": "^13.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result.get("has_nextjs") is True

    def test_detects_express(self, tmp_path):
        """Detects Express from package.json dependencies."""
        package_data = {"dependencies": {"express": "^4.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        result = detect_project_type(tmp_path)
        assert result.get("has_express") is True

    def test_handles_invalid_package_json(self, tmp_path):
        """Handles invalid package.json gracefully."""
        (tmp_path / "package.json").write_text("not valid json")
        result = detect_project_type(tmp_path)
        assert result["has_javascript"] is True  # Still detected
        assert result.get("has_react", False) is False  # But no framework

    # Kubernetes detection
    def test_detects_kubernetes_k8s_dir(self, tmp_path):
        """Detects Kubernetes from k8s directory."""
        (tmp_path / "k8s").mkdir()
        result = detect_project_type(tmp_path)
        assert result.get("has_kubernetes") is True

    def test_detects_kubernetes_kubernetes_dir(self, tmp_path):
        """Detects Kubernetes from kubernetes directory."""
        (tmp_path / "kubernetes").mkdir()
        result = detect_project_type(tmp_path)
        assert result.get("has_kubernetes") is True

    def test_detects_kubernetes_from_yaml(self, tmp_path):
        """Detects Kubernetes from YAML with apiVersion and kind."""
        (tmp_path / "deployment.yaml").write_text(
            "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: test"
        )
        result = detect_project_type(tmp_path)
        assert result.get("has_kubernetes") is True

    def test_ignores_non_k8s_yaml(self, tmp_path):
        """Doesn't detect k8s from non-k8s YAML."""
        (tmp_path / "config.yaml").write_text("name: test\nvalue: 123")
        result = detect_project_type(tmp_path)
        assert result.get("has_kubernetes", False) is False

    # Terraform detection
    def test_detects_terraform(self, tmp_path):
        """Detects Terraform from .tf files."""
        (tmp_path / "main.tf").write_text("")
        result = detect_project_type(tmp_path)
        assert result.get("has_terraform") is True

    def test_no_terraform_without_tf_files(self, tmp_path):
        """No Terraform detection without .tf files."""
        (tmp_path / "main.py").write_text("")
        result = detect_project_type(tmp_path)
        assert result.get("has_terraform", False) is False

    # Docker detection
    def test_detects_dockerfile(self, tmp_path):
        """Detects Docker from Dockerfile."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.11")
        result = detect_project_type(tmp_path)
        assert result.get("has_docker") is True

    def test_detects_docker_compose_yml(self, tmp_path):
        """Detects Docker from docker-compose.yml."""
        (tmp_path / "docker-compose.yml").write_text("version: '3'")
        result = detect_project_type(tmp_path)
        assert result.get("has_docker") is True

    def test_detects_docker_compose_yaml(self, tmp_path):
        """Detects Docker from docker-compose.yaml."""
        (tmp_path / "docker-compose.yaml").write_text("version: '3'")
        result = detect_project_type(tmp_path)
        assert result.get("has_docker") is True

    # Backend detection
    def test_detects_backend_from_api_dir(self, tmp_path):
        """Detects backend from api directory."""
        (tmp_path / "api").mkdir()
        result = detect_project_type(tmp_path)
        assert result.get("has_backend") is True

    def test_detects_backend_from_src_api_dir(self, tmp_path):
        """Detects backend from src/api directory."""
        (tmp_path / "src" / "api").mkdir(parents=True)
        result = detect_project_type(tmp_path)
        assert result.get("has_backend") is True

    def test_detects_backend_from_fastapi(self, tmp_path):
        """Detects backend from FastAPI."""
        (tmp_path / "requirements.txt").write_text("fastapi")
        result = detect_project_type(tmp_path)
        assert result.get("has_backend") is True

    # Database detection
    def test_detects_database_from_docker_compose(self, tmp_path):
        """Detects database from docker-compose.yml."""
        (tmp_path / "docker-compose.yml").write_text(
            "services:\n  postgres:\n    image: postgres:15"
        )
        result = detect_project_type(tmp_path)
        assert result.get("has_database") is True

    def test_detects_database_from_env(self, tmp_path):
        """Detects database from .env file."""
        (tmp_path / ".env").write_text("DATABASE_URL=postgres://localhost/db")
        result = detect_project_type(tmp_path)
        assert result.get("has_database") is True


class TestSuggestSkillsForProject:
    """Tests for suggest_skills_for_project function."""

    def test_python_project_suggestions(self, tmp_path):
        """Python project gets Python-related skills."""
        (tmp_path / "pyproject.toml").write_text("")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "async-python-patterns" in suggestions
        assert "python-testing-patterns" in suggestions
        assert "python-performance-optimization" in suggestions

    def test_fastapi_project_suggestions(self, tmp_path):
        """FastAPI project gets API-related skills."""
        (tmp_path / "requirements.txt").write_text("fastapi\nuvicorn")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "api-design-patterns" in suggestions
        assert "async-python-patterns" in suggestions

    def test_django_project_suggestions(self, tmp_path):
        """Django project gets database-related skills."""
        (tmp_path / "requirements.txt").write_text("django>=4.0")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "python-testing-patterns" in suggestions
        assert "database-design-patterns" in suggestions

    def test_typescript_project_suggestions(self, tmp_path):
        """TypeScript project gets TypeScript skills."""
        (tmp_path / "tsconfig.json").write_text("{}")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "typescript-advanced-patterns" in suggestions

    def test_react_project_suggestions(self, tmp_path):
        """React project gets React-related skills."""
        package_data = {"dependencies": {"react": "^18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        suggestions = suggest_skills_for_project(tmp_path)
        assert "react-performance-optimization" in suggestions

    def test_react_typescript_project_suggestions(self, tmp_path):
        """React + TypeScript project gets both skill sets."""
        package_data = {"dependencies": {"react": "^18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        (tmp_path / "tsconfig.json").write_text("{}")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "react-performance-optimization" in suggestions
        assert "typescript-advanced-patterns" in suggestions

    def test_nextjs_project_suggestions(self, tmp_path):
        """Next.js project gets React and TypeScript skills."""
        package_data = {"dependencies": {"next": "^13.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        suggestions = suggest_skills_for_project(tmp_path)
        assert "react-performance-optimization" in suggestions
        assert "typescript-advanced-patterns" in suggestions

    def test_express_project_suggestions(self, tmp_path):
        """Express project gets API skills."""
        package_data = {"dependencies": {"express": "^4.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        suggestions = suggest_skills_for_project(tmp_path)
        assert "api-design-patterns" in suggestions

    def test_kubernetes_project_suggestions(self, tmp_path):
        """Kubernetes project gets K8s-related skills."""
        (tmp_path / "k8s").mkdir()
        suggestions = suggest_skills_for_project(tmp_path)
        assert "kubernetes-deployment-patterns" in suggestions
        assert "kubernetes-security-policies" in suggestions
        assert "helm-chart-patterns" in suggestions
        assert "gitops-workflows" in suggestions

    def test_terraform_project_suggestions(self, tmp_path):
        """Terraform project gets Terraform skills."""
        (tmp_path / "main.tf").write_text("")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "terraform-best-practices" in suggestions

    def test_docker_project_suggestions(self, tmp_path):
        """Docker project gets Docker skills."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.11")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "docker-best-practices" in suggestions

    def test_backend_project_suggestions(self, tmp_path):
        """Backend project gets API and microservices skills."""
        (tmp_path / "api").mkdir()
        suggestions = suggest_skills_for_project(tmp_path)
        assert "api-design-patterns" in suggestions
        assert "microservices-patterns" in suggestions

    def test_backend_with_database_suggestions(self, tmp_path):
        """Backend with database gets database skills."""
        (tmp_path / "api").mkdir()
        (tmp_path / ".env").write_text("DATABASE_URL=postgres://localhost/db")
        suggestions = suggest_skills_for_project(tmp_path)
        assert "database-design-patterns" in suggestions

    def test_security_suggestions_for_backend(self, tmp_path):
        """Backend projects get security skills."""
        (tmp_path / "api").mkdir()
        suggestions = suggest_skills_for_project(tmp_path)
        assert "owasp-top-10" in suggestions
        assert "secure-coding-practices" in suggestions

    def test_security_suggestions_for_react(self, tmp_path):
        """React projects get security skills."""
        package_data = {"dependencies": {"react": "^18.0.0"}}
        (tmp_path / "package.json").write_text(json.dumps(package_data))
        suggestions = suggest_skills_for_project(tmp_path)
        assert "owasp-top-10" in suggestions
        assert "secure-coding-practices" in suggestions

    def test_returns_sorted_list(self, tmp_path):
        """Suggestions are returned sorted."""
        (tmp_path / "pyproject.toml").write_text("")
        suggestions = suggest_skills_for_project(tmp_path)
        assert suggestions == sorted(suggestions)

    def test_empty_project_no_suggestions(self, tmp_path):
        """Empty project returns empty suggestions."""
        suggestions = suggest_skills_for_project(tmp_path)
        assert len(suggestions) == 0


class TestSuggestComplementarySkills:
    """Tests for suggest_complementary_skills function."""

    def test_api_design_complements(self):
        """API design suggests related patterns."""
        suggestions = suggest_complementary_skills(["api-design-patterns"])
        assert "api-gateway-patterns" in suggestions
        assert "microservices-patterns" in suggestions
        assert "event-driven-architecture" in suggestions

    def test_microservices_complements(self):
        """Microservices suggests related patterns."""
        suggestions = suggest_complementary_skills(["microservices-patterns"])
        assert "event-driven-architecture" in suggestions
        assert "cqrs-event-sourcing" in suggestions
        assert "api-gateway-patterns" in suggestions

    def test_kubernetes_complements(self):
        """Kubernetes suggests related patterns."""
        suggestions = suggest_complementary_skills(["kubernetes-deployment-patterns"])
        assert "kubernetes-security-policies" in suggestions
        assert "helm-chart-patterns" in suggestions
        assert "gitops-workflows" in suggestions

    def test_security_complements(self):
        """Security skills suggest related patterns."""
        suggestions = suggest_complementary_skills(["owasp-top-10"])
        assert "secure-coding-practices" in suggestions
        assert "threat-modeling-techniques" in suggestions
        assert "security-testing-patterns" in suggestions

    def test_react_complements(self):
        """React suggests related patterns."""
        suggestions = suggest_complementary_skills(["react-performance-optimization"])
        assert "typescript-advanced-patterns" in suggestions

    def test_python_complements(self):
        """Async Python suggests related patterns."""
        suggestions = suggest_complementary_skills(["async-python-patterns"])
        assert "python-performance-optimization" in suggestions
        assert "python-testing-patterns" in suggestions

    def test_database_complements(self):
        """Database design suggests related patterns."""
        suggestions = suggest_complementary_skills(["database-design-patterns"])
        assert "cqrs-event-sourcing" in suggestions

    def test_terraform_complements(self):
        """Terraform suggests related patterns."""
        suggestions = suggest_complementary_skills(["terraform-best-practices"])
        assert "gitops-workflows" in suggestions

    def test_gitops_complements(self):
        """GitOps suggests related patterns."""
        suggestions = suggest_complementary_skills(["gitops-workflows"])
        assert "kubernetes-deployment-patterns" in suggestions
        assert "helm-chart-patterns" in suggestions

    def test_excludes_already_active(self):
        """Doesn't suggest skills that are already active."""
        active = ["api-design-patterns", "microservices-patterns"]
        suggestions = suggest_complementary_skills(active)
        # microservices-patterns should not be suggested since it's active
        assert "microservices-patterns" not in suggestions

    def test_multiple_skills_combine_suggestions(self):
        """Multiple active skills combine their suggestions."""
        active = ["api-design-patterns", "kubernetes-deployment-patterns"]
        suggestions = suggest_complementary_skills(active)
        # Should have suggestions from both
        assert "microservices-patterns" in suggestions
        assert "helm-chart-patterns" in suggestions

    def test_unknown_skill_returns_empty(self):
        """Unknown skill returns empty suggestions."""
        suggestions = suggest_complementary_skills(["unknown-skill"])
        assert len(suggestions) == 0

    def test_empty_active_returns_empty(self):
        """Empty active skills returns empty suggestions."""
        suggestions = suggest_complementary_skills([])
        assert len(suggestions) == 0

    def test_returns_sorted_list(self):
        """Suggestions are returned sorted."""
        suggestions = suggest_complementary_skills(["api-design-patterns"])
        assert suggestions == sorted(suggestions)


class TestFormatSuggestions:
    """Tests for format_suggestions function."""

    def test_empty_suggestions(self):
        """Empty suggestions returns no suggestions message."""
        result = format_suggestions([], "project analysis")
        assert "No skill suggestions available." in result

    def test_includes_reason(self):
        """Formatted output includes the reason."""
        result = format_suggestions(["api-design-patterns"], "project analysis")
        assert "project analysis" in result

    def test_includes_skill_names(self):
        """Formatted output includes skill names."""
        skills = ["api-design-patterns", "microservices-patterns"]
        result = format_suggestions(skills, "project analysis")
        assert "api-design-patterns" in result
        assert "microservices-patterns" in result

    def test_includes_count(self):
        """Formatted output includes total count."""
        skills = ["api-design-patterns", "microservices-patterns"]
        result = format_suggestions(skills, "project analysis")
        assert "Total suggestions: 2" in result

    def test_includes_activation_hint(self):
        """Formatted output includes activation instructions."""
        skills = ["api-design-patterns"]
        result = format_suggestions(skills, "project analysis")
        assert "cortex skills activate" in result

    def test_contains_ansi_colors(self):
        """Formatted output contains ANSI color codes."""
        skills = ["api-design-patterns"]
        result = format_suggestions(skills, "project analysis")
        # Check for ANSI escape codes
        assert "\033[" in result
