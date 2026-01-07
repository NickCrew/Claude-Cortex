"""Context-driven skill suggestions based on project analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set


def detect_project_type(project_dir: Path) -> Dict[str, bool]:
    """
    Detect project characteristics based on file patterns and configurations.

    Returns:
        Dictionary with boolean flags for detected technologies:
        - has_python: Python project detected
        - has_typescript: TypeScript project detected
        - has_javascript: JavaScript project detected
        - has_react: React project detected
        - has_vue: Vue.js project detected
        - has_angular: Angular project detected
        - has_kubernetes: Kubernetes configuration detected
        - has_terraform: Terraform configuration detected
        - has_docker: Docker configuration detected
        - has_fastapi: FastAPI framework detected
        - has_django: Django framework detected
        - has_express: Express.js framework detected
        - has_nextjs: Next.js framework detected
        - has_backend: Backend API patterns detected
        - has_database: Database configuration detected
    """
    features: Dict[str, bool] = {}

    # Python detection
    features["has_python"] = any(
        [
            (project_dir / "requirements.txt").exists(),
            (project_dir / "pyproject.toml").exists(),
            (project_dir / "setup.py").exists(),
            (project_dir / "Pipfile").exists(),
        ]
    )

    # TypeScript detection
    package_json_path = project_dir / "package.json"
    tsconfig_exists = (project_dir / "tsconfig.json").exists()

    features["has_typescript"] = tsconfig_exists
    features["has_javascript"] = package_json_path.exists()

    # Parse package.json for framework detection
    if package_json_path.exists():
        try:
            package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
            dependencies = {
                **package_data.get("dependencies", {}),
                **package_data.get("devDependencies", {}),
            }

            features["has_react"] = "react" in dependencies
            features["has_vue"] = "vue" in dependencies
            features["has_angular"] = "@angular/core" in dependencies
            features["has_nextjs"] = "next" in dependencies
            features["has_express"] = "express" in dependencies

            # If typescript is in deps but no tsconfig, still mark as typescript project
            if "typescript" in dependencies and not features["has_typescript"]:
                features["has_typescript"] = True
        except (json.JSONDecodeError, Exception):
            pass

    # Framework-specific detection for Python
    if features.get("has_python", False):
        # Check for FastAPI
        for req_file in ["requirements.txt", "pyproject.toml"]:
            req_path = project_dir / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text(encoding="utf-8").lower()
                    if "fastapi" in content:
                        features["has_fastapi"] = True
                    if "django" in content:
                        features["has_django"] = True
                except Exception:
                    pass

    # Kubernetes detection
    k8s_indicators = [
        (project_dir / "k8s").is_dir(),
        (project_dir / "kubernetes").is_dir(),
        any((project_dir / ".kube").glob("*.yaml")),
    ]

    # Check for k8s yaml files
    yaml_files = list(project_dir.glob("*.yaml")) + list(project_dir.glob("*.yml"))
    for yaml_file in yaml_files:
        try:
            content = yaml_file.read_text(encoding="utf-8")
            if "kind:" in content and ("apiVersion:" in content):
                k8s_indicators.append(True)
                break
        except Exception:
            pass

    features["has_kubernetes"] = any(k8s_indicators)

    # Terraform detection
    features["has_terraform"] = len(list(project_dir.glob("*.tf"))) > 0

    # Docker detection
    features["has_docker"] = any(
        [
            (project_dir / "Dockerfile").exists(),
            (project_dir / "docker-compose.yml").exists(),
            (project_dir / "docker-compose.yaml").exists(),
        ]
    )

    # Backend detection (heuristic)
    backend_indicators = [
        features.get("has_fastapi", False),
        features.get("has_django", False),
        features.get("has_express", False),
        (project_dir / "api").is_dir(),
        (project_dir / "src" / "api").is_dir(),
    ]
    features["has_backend"] = any(backend_indicators)

    # Database detection
    db_indicators = []
    for config_file in [
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env",
        ".env.example",
    ]:
        config_path = project_dir / config_file
        if config_path.exists():
            try:
                content = config_path.read_text(encoding="utf-8").lower()
                if any(
                    db in content
                    for db in ["postgres", "mysql", "mongodb", "redis", "database"]
                ):
                    db_indicators.append(True)
                    break
            except Exception:
                pass

    features["has_database"] = any(db_indicators)

    return features


def suggest_skills_for_project(project_dir: Path) -> List[str]:
    """
    Suggest skills based on detected project characteristics.

    Args:
        project_dir: Path to the project directory

    Returns:
        List of suggested skill names
    """
    features = detect_project_type(project_dir)
    suggestions: Set[str] = set()

    # Python-based suggestions
    if features.get("has_python", False):
        suggestions.add("async-python-patterns")
        suggestions.add("python-testing-patterns")
        suggestions.add("python-performance-optimization")

        if features.get("has_fastapi", False):
            suggestions.add("api-design-patterns")
            suggestions.add("async-python-patterns")

        if features.get("has_django", False):
            suggestions.add("python-testing-patterns")
            suggestions.add("database-design-patterns")

    # TypeScript/JavaScript suggestions
    if features.get("has_typescript", False):
        suggestions.add("typescript-advanced-patterns")

    if features.get("has_react", False):
        suggestions.add("react-performance-optimization")

        if features.get("has_typescript", False):
            suggestions.add("typescript-advanced-patterns")

    if features.get("has_nextjs", False):
        suggestions.add("react-performance-optimization")
        suggestions.add("typescript-advanced-patterns")

    if features.get("has_express", False):
        suggestions.add("api-design-patterns")
        if features.get("has_typescript", False):
            suggestions.add("typescript-advanced-patterns")

    # Infrastructure suggestions
    if features.get("has_kubernetes", False):
        suggestions.add("kubernetes-deployment-patterns")
        suggestions.add("kubernetes-security-policies")
        suggestions.add("helm-chart-patterns")
        suggestions.add("gitops-workflows")

    if features.get("has_terraform", False):
        suggestions.add("terraform-best-practices")

    if features.get("has_docker", False):
        suggestions.add("docker-best-practices")

    # Backend suggestions
    if features.get("has_backend", False):
        suggestions.add("api-design-patterns")
        suggestions.add("microservices-patterns")

        if features.get("has_database", False):
            suggestions.add("database-design-patterns")

    # Security suggestions (always relevant for web/backend projects)
    if any(
        [
            features.get("has_backend", False),
            features.get("has_react", False),
            features.get("has_kubernetes", False),
        ]
    ):
        suggestions.add("owasp-top-10")
        suggestions.add("secure-coding-practices")

    return sorted(list(suggestions))


def suggest_complementary_skills(active_skills: List[str]) -> List[str]:
    """
    Suggest complementary skills based on currently active skills.

    Args:
        active_skills: List of currently active skill names

    Returns:
        List of suggested complementary skill names
    """
    # Define skill relationships
    complementary_map: Dict[str, List[str]] = {
        "api-design-patterns": [
            "api-gateway-patterns",
            "microservices-patterns",
            "event-driven-architecture",
        ],
        "microservices-patterns": [
            "event-driven-architecture",
            "cqrs-event-sourcing",
            "distributed-systems-patterns",
            "api-gateway-patterns",
        ],
        "kubernetes-deployment-patterns": [
            "kubernetes-security-policies",
            "helm-chart-patterns",
            "gitops-workflows",
            "observability-patterns",
        ],
        "kubernetes-security-policies": [
            "kubernetes-deployment-patterns",
            "owasp-top-10",
            "secure-coding-practices",
        ],
        "owasp-top-10": [
            "secure-coding-practices",
            "threat-modeling-techniques",
            "security-testing-patterns",
        ],
        "secure-coding-practices": [
            "owasp-top-10",
            "threat-modeling-techniques",
            "security-testing-patterns",
        ],
        "react-performance-optimization": [
            "typescript-advanced-patterns",
            "web-performance-patterns",
            "frontend-testing-patterns",
        ],
        "async-python-patterns": [
            "python-performance-optimization",
            "python-testing-patterns",
            "concurrent-programming-patterns",
        ],
        "database-design-patterns": [
            "sql-optimization-techniques",
            "nosql-patterns",
            "cqrs-event-sourcing",
        ],
        "event-driven-architecture": [
            "cqrs-event-sourcing",
            "microservices-patterns",
            "message-queue-patterns",
        ],
        "terraform-best-practices": [
            "infrastructure-as-code-patterns",
            "cloud-architecture-patterns",
            "gitops-workflows",
        ],
        "helm-chart-patterns": [
            "kubernetes-deployment-patterns",
            "gitops-workflows",
            "kubernetes-security-policies",
        ],
        "gitops-workflows": [
            "kubernetes-deployment-patterns",
            "helm-chart-patterns",
            "ci-cd-patterns",
        ],
    }

    suggestions: Set[str] = set()
    active_set = set(active_skills)

    for skill in active_skills:
        if skill in complementary_map:
            for suggested in complementary_map[skill]:
                # Don't suggest skills that are already active
                if suggested not in active_set:
                    suggestions.add(suggested)

    return sorted(list(suggestions))


def format_suggestions(suggestions: List[str], reason: str) -> str:
    """
    Format skill suggestions for CLI output.

    Args:
        suggestions: List of suggested skill names
        reason: Reason for the suggestions

    Returns:
        Formatted string for display
    """
    if not suggestions:
        return "No skill suggestions available."

    lines = [
        f"\033[0;34mSuggested skills based on {reason}:\033[0m",
        "",
    ]

    for skill in suggestions:
        lines.append(f"  \033[0;32m{skill}\033[0m")

    lines.append("")
    lines.append(f"Total suggestions: {len(suggestions)}")
    lines.append("")
    lines.append("To activate a skill:")
    lines.append("  \033[0;33mcortex skills activate <skill_name>\033[0m")

    return "\n".join(lines)
