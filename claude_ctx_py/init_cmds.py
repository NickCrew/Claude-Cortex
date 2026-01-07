"""Init command implementations for cortex."""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import List, Tuple, TypedDict

# Import color constants and helpers from core
from .core import (
    BLUE,
    GREEN,
    RED,
    YELLOW,
    _color,
    _resolve_claude_dir,
    profile_backend,
    profile_minimal,
)


class DetectionResult(TypedDict):
    language: str | None
    framework: str | None
    infrastructure: str | None
    types: List[str]


def _generate_project_slug(project_path: Path) -> str:
    """Generate a short hash slug for a project path."""
    path_str = str(project_path.resolve())
    hash_hex = hashlib.sha256(path_str.encode("utf-8")).hexdigest()
    return hash_hex[:12]


def _get_init_state_dir(home: Path | None = None) -> Path:
    """Get the init state directory."""
    claude_dir = _resolve_claude_dir(home)
    return claude_dir / ".init"


def _get_init_projects_dir(home: Path | None = None) -> Path:
    """Get the init projects directory."""
    return _get_init_state_dir(home) / "projects"


def _get_project_state_dir(project_path: Path, home: Path | None = None) -> Path:
    """Get the state directory for a specific project."""
    slug = _generate_project_slug(project_path)
    projects_dir = _get_init_projects_dir(home)

    # Check if we have an existing project with this slug
    if projects_dir.is_dir():
        for existing_dir in projects_dir.glob("*"):
            if existing_dir.is_dir() and existing_dir.name.endswith(f"-{slug}"):
                return existing_dir

    # Generate a new directory name using project name or timestamp
    project_name = project_path.name
    # Clean project name for filesystem
    clean_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "-" for c in project_name
    )
    return projects_dir / f"{clean_name}-{slug}"


def _detect_project_type(project_path: Path) -> DetectionResult:
    """Detect project type, language, and framework."""
    detection: DetectionResult = {
        "language": None,
        "framework": None,
        "infrastructure": None,
        "types": [],
    }

    # Check for common files
    try:
        files = list(project_path.glob("*"))
    except OSError:
        return detection

    file_names = {f.name for f in files if f.is_file()}

    # Python detection
    if (
        "setup.py" in file_names
        or "pyproject.toml" in file_names
        or "requirements.txt" in file_names
    ):
        detection["language"] = "python"
        detection["types"].append("python")

        # Check for common Python frameworks
        if "manage.py" in file_names or (project_path / "django").exists():
            detection["framework"] = "django"
        elif "app.py" in file_names or "wsgi.py" in file_names:
            detection["framework"] = "flask"

    # Node.js detection
    if "package.json" in file_names:
        detection["language"] = "javascript"
        detection["types"].append("node")

        # Check for common Node.js frameworks
        try:
            package_json = project_path / "package.json"
            data = json.loads(package_json.read_text(encoding="utf-8"))
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            if "react" in deps or "react-dom" in deps:
                detection["framework"] = "react"
            elif "vue" in deps:
                detection["framework"] = "vue"
            elif "next" in deps:
                detection["framework"] = "nextjs"
            elif "express" in deps:
                detection["framework"] = "express"
        except (OSError, json.JSONDecodeError):
            pass

    # TypeScript detection
    if "tsconfig.json" in file_names:
        detection["language"] = "typescript"
        detection["types"].append("typescript")

    # Go detection
    if "go.mod" in file_names or "go.sum" in file_names:
        detection["language"] = "go"
        detection["types"].append("go")

    # Rust detection
    if "Cargo.toml" in file_names:
        detection["language"] = "rust"
        detection["types"].append("rust")

    # Infrastructure detection
    if "docker-compose.yml" in file_names or "docker-compose.yaml" in file_names:
        detection["infrastructure"] = "docker-compose"
    elif "Dockerfile" in file_names:
        detection["infrastructure"] = "docker"

    try:
        tf_files = list(project_path.glob("*.tf"))
        if tf_files:
            detection["infrastructure"] = "terraform"
    except OSError:
        pass

    return detection


def _write_detection_json(
    state_dir: Path,
    project_path: Path,
    detection: DetectionResult,
    analysis_output: str = "",
) -> None:
    """Write detection results to JSON file."""
    slug = _generate_project_slug(project_path)
    data = {
        "path": str(project_path.resolve()),
        "slug": slug,
        "timestamp": datetime.datetime.now(datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        **detection,
        "analysis_output": analysis_output,
    }

    state_dir.mkdir(parents=True, exist_ok=True)
    detection_file = state_dir / "detection.json"
    detection_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_session_log(
    state_dir: Path, project_path: Path, slug: str, analysis_output: str = ""
) -> None:
    """Write session log markdown file."""
    timestamp = (
        datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    )

    lines = [
        "# Init Detection Session",
        f"- Timestamp: {timestamp}",
        f"- Path: {project_path.resolve()}",
        f"- Slug: {slug}",
        "",
        "## Detection Summary",
        "",
        "## analyze_project Output",
        analysis_output,
    ]

    state_dir.mkdir(parents=True, exist_ok=True)
    log_file = state_dir / "session-log.md"
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _recommend_profile(detection: DetectionResult) -> str:
    """Recommend a profile based on project detection."""
    language = detection.get("language")
    framework = detection.get("framework")

    # Backend frameworks
    if framework in {"django", "flask", "express"}:
        return "backend"

    # Frontend frameworks
    if framework in {"react", "vue", "nextjs"}:
        return "frontend"

    # Data/AI projects
    if language == "python":
        return "backend"

    # Default to minimal
    return "minimal"


def init_detect(
    project_path: str | Path | None = None, home: Path | None = None
) -> Tuple[int, str]:
    """Detect project type and recommend configuration."""
    if project_path is None:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path).expanduser().resolve()

    if not project_path.is_dir():
        return 1, _color(f"Project path does not exist: {project_path}", RED)

    # Detect project type
    detection = _detect_project_type(project_path)

    # Generate analysis output
    analysis_lines = [
        "Analyzing project structure...",
        "",
        "Project Analysis:",
    ]

    if detection["language"]:
        analysis_lines.append(f"  Language: {detection['language']}")
    if detection["framework"]:
        analysis_lines.append(f"  Framework: {detection['framework']}")
    if detection["infrastructure"]:
        analysis_lines.append(f"  Infrastructure: {detection['infrastructure']}")

    # Recommend profile
    recommended_profile = _recommend_profile(detection)
    analysis_lines.extend(
        [
            "",
            "Recommended Configuration:",
            f"  Profile: {recommended_profile}",
        ]
    )

    if detection["language"] or detection["framework"]:
        analysis_lines.append(
            f"  Detected: {detection['language'] or 'unknown'} project"
        )
    else:
        analysis_lines.append("  Using basic configuration")

    analysis_output = "\n".join(analysis_lines)

    # Write state files
    state_dir = _get_project_state_dir(project_path, home)
    slug = _generate_project_slug(project_path)
    _write_detection_json(state_dir, project_path, detection, analysis_output)
    _write_session_log(state_dir, project_path, slug, analysis_output)

    # Build output message
    output_lines = [
        _color("=== Project Detection ===", BLUE),
        "",
        analysis_output,
        "",
        f"Apply this configuration with: cortex init profile {recommended_profile}",
    ]

    return 0, "\n".join(output_lines)


def init_minimal(
    project_path: str | Path | None = None, home: Path | None = None
) -> Tuple[int, str]:
    """Initialize with minimal profile without detection."""
    if project_path is None:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path).expanduser().resolve()

    # Apply minimal profile
    exit_code, profile_message = profile_minimal(home=home)
    if exit_code != 0:
        return exit_code, profile_message

    # Write state
    state_dir = _get_project_state_dir(project_path, home)
    slug = _generate_project_slug(project_path)
    detection: DetectionResult = {
        "language": None,
        "framework": None,
        "infrastructure": None,
        "types": [],
    }
    analysis = "Initialized with minimal profile (no detection)"
    _write_detection_json(state_dir, project_path, detection, analysis)
    _write_session_log(state_dir, project_path, slug, analysis)

    lines = [
        _color("=== Init Minimal ===", BLUE),
        "",
        profile_message,
        "",
        _color(f"Initialized: {project_path}", GREEN),
    ]

    return 0, "\n".join(lines)


def init_profile(
    profile_name: str, project_path: str | Path | None = None, home: Path | None = None
) -> Tuple[int, str]:
    """Initialize with a specific profile."""
    if project_path is None:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path).expanduser().resolve()

    # Apply the profile
    if profile_name == "minimal":
        exit_code, profile_message = profile_minimal(home=home)
    elif profile_name == "backend":
        exit_code, profile_message = profile_backend(home=home)
    else:
        return 1, _color(f"Profile '{profile_name}' not yet implemented", RED)

    if exit_code != 0:
        return exit_code, profile_message

    # Write state
    state_dir = _get_project_state_dir(project_path, home)
    slug = _generate_project_slug(project_path)
    detection: DetectionResult = {
        "language": None,
        "framework": None,
        "infrastructure": None,
        "types": [],
    }
    analysis = f"Initialized with {profile_name} profile"
    _write_detection_json(state_dir, project_path, detection, analysis)
    _write_session_log(state_dir, project_path, slug, analysis)

    lines = [
        _color(f"=== Init Profile: {profile_name} ===", BLUE),
        "",
        profile_message,
        "",
        _color(f"Initialized: {project_path}", GREEN),
    ]

    return 0, "\n".join(lines)


def init_status(
    project_path: str | Path | None = None, home: Path | None = None
) -> Tuple[int, str]:
    """Show initialization status for a project."""
    if project_path is None:
        project_path = Path.cwd()
    else:
        project_path = Path(project_path).expanduser().resolve()

    state_dir = _get_project_state_dir(project_path, home)
    detection_file = state_dir / "detection.json"

    if not detection_file.is_file():
        return 0, _color("Project not initialized", YELLOW)

    # Read detection data
    try:
        data = json.loads(detection_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return 1, _color(f"Failed to read detection data: {exc}", RED)

    lines = [
        _color("=== Init Status ===", BLUE),
        "",
        f"Project: {data.get('path', 'unknown')}",
        f"Slug: {data.get('slug', 'unknown')}",
        f"Initialized: {data.get('timestamp', 'unknown')}",
        "",
        _color("Detection:", BLUE),
    ]

    if data.get("language"):
        lines.append(f"  Language: {data['language']}")
    if data.get("framework"):
        lines.append(f"  Framework: {data['framework']}")
    if data.get("infrastructure"):
        lines.append(f"  Infrastructure: {data['infrastructure']}")

    if not data.get("language") and not data.get("framework"):
        lines.append("  No specific detection")

    return 0, "\n".join(lines)


def init_wizard(home: Path | None = None) -> Tuple[int, str]:
    """Interactive wizard for project initialization (stub)."""
    return 1, _color("init wizard: not yet implemented", YELLOW)


def init_reset(home: Path | None = None) -> Tuple[int, str]:
    """Reset initialization state (stub)."""
    return 1, _color("init reset: not yet implemented", YELLOW)


def init_resume(home: Path | None = None) -> Tuple[int, str]:
    """Resume interrupted initialization (stub)."""
    return 1, _color("init resume: not yet implemented", YELLOW)
