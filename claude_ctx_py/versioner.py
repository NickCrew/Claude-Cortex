"""Semantic versioning utilities for Claude context system.

This module provides utilities for parsing, comparing, and managing semantic versions
for skills and other versioned components in the Claude context system.

Supported version specifications:
- Exact: @1.2.0
- Caret: @^1.2.0 (allows minor and patch updates)
- Tilde: @~1.2.0 (allows patch updates only)
- Minimum: @>=1.2.0 (allows any version >= specified)
- Latest: @latest (uses most recent version)
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import yaml

from .exceptions import (
    VersionFormatError,
    VersionCompatibilityError,
    NoCompatibleVersionError,
)
from .error_utils import safe_load_yaml


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse a semantic version string into major, minor, and patch components.

    Args:
        version_str: A semantic version string (e.g., "1.2.3" or "v1.2.3")

    Returns:
        A tuple of (major, minor, patch) version numbers

    Raises:
        VersionFormatError: If the version string is not a valid semantic version

    Examples:
        >>> parse_version("1.2.3")
        (1, 2, 3)
        >>> parse_version("v2.0.1")
        (2, 0, 1)
    """
    # Remove 'v' prefix if present
    version_str = version_str.lstrip("v")

    # Match semantic version pattern
    pattern = r"^(\d+)\.(\d+)\.(\d+)$"
    match = re.match(pattern, version_str)

    if not match:
        raise VersionFormatError(version_str, expected_format="X.Y.Z")

    major, minor, patch = match.groups()
    return int(major), int(minor), int(patch)


def check_compatibility(required: str, available: str) -> bool:
    """Check if an available version satisfies a version requirement.

    Supports various version requirement formats:
    - Exact: "1.2.0" - must match exactly
    - Caret: "^1.2.0" - allows >=1.2.0 and <2.0.0
    - Tilde: "~1.2.0" - allows >=1.2.0 and <1.3.0
    - Minimum: ">=1.2.0" - allows any version >= 1.2.0
    - Latest: "latest" - always matches

    Args:
        required: Version requirement specification
        available: Available version to check

    Returns:
        True if available version satisfies the requirement, False otherwise

    Examples:
        >>> check_compatibility("1.2.0", "1.2.0")
        True
        >>> check_compatibility("^1.2.0", "1.3.5")
        True
        >>> check_compatibility("^1.2.0", "2.0.0")
        False
        >>> check_compatibility("~1.2.0", "1.2.5")
        True
        >>> check_compatibility("~1.2.0", "1.3.0")
        False
    """
    # Handle 'latest' requirement
    if required.lower() == "latest":
        return True

    # Parse available version
    try:
        avail_major, avail_minor, avail_patch = parse_version(available)
    except ValueError:
        return False

    # Handle minimum version (>=)
    if required.startswith(">="):
        try:
            req_major, req_minor, req_patch = parse_version(required[2:])
            return (avail_major, avail_minor, avail_patch) >= (
                req_major,
                req_minor,
                req_patch,
            )
        except ValueError:
            return False

    # Handle caret (^) - allows minor and patch updates
    if required.startswith("^"):
        try:
            req_major, req_minor, req_patch = parse_version(required[1:])
            if avail_major != req_major:
                return False
            return (avail_minor, avail_patch) >= (req_minor, req_patch)
        except ValueError:
            return False

    # Handle tilde (~) - allows patch updates only
    if required.startswith("~"):
        try:
            req_major, req_minor, req_patch = parse_version(required[1:])
            if (avail_major, avail_minor) != (req_major, req_minor):
                return False
            return avail_patch >= req_patch
        except ValueError:
            return False

    # Handle exact version match
    try:
        req_major, req_minor, req_patch = parse_version(required)
        return (avail_major, avail_minor, avail_patch) == (
            req_major,
            req_minor,
            req_patch,
        )
    except ValueError:
        return False


def get_skill_versions(skill_name: str, claude_dir: Path) -> List[str]:
    """Get all available versions of a skill.

    Searches for skill directories in the format: skill_name@version

    Args:
        skill_name: Name of the skill (without version)
        claude_dir: Path to the Claude directory

    Returns:
        List of version strings found, sorted by semantic version (newest first)

    Examples:
        >>> get_skill_versions("pdf", Path("/home/user/.cortex"))
        ["2.1.0", "2.0.0", "1.5.3"]
    """
    skills_dir = claude_dir / "skills"

    if not skills_dir.exists():
        return []

    versions = []
    pattern = f"{skill_name}@*"

    for skill_dir in skills_dir.glob(pattern):
        if not skill_dir.is_dir():
            continue

        # Extract version from directory name
        dir_name = skill_dir.name
        if "@" in dir_name:
            version = dir_name.split("@", 1)[1]
            try:
                # Validate it's a proper semantic version
                parse_version(version)
                versions.append(version)
            except ValueError:
                # Skip invalid version strings
                continue

    # Sort by semantic version (newest first)
    versions.sort(key=lambda v: parse_version(v), reverse=True)

    return versions


def get_latest_version(skill_name: str, claude_dir: Path) -> str:
    """Get the latest version of a skill.

    Args:
        skill_name: Name of the skill (without version)
        claude_dir: Path to the Claude directory

    Returns:
        Latest version string, or "latest" if no versions found

    Examples:
        >>> get_latest_version("pdf", Path("/home/user/.cortex"))
        "2.1.0"
    """
    versions = get_skill_versions(skill_name, claude_dir)
    return versions[0] if versions else "latest"


def validate_version_requirement(requirement: str) -> bool:
    """Validate a version requirement string.

    Args:
        requirement: Version requirement string to validate

    Returns:
        True if the requirement is valid, False otherwise

    Examples:
        >>> validate_version_requirement("1.2.3")
        True
        >>> validate_version_requirement("^1.2.3")
        True
        >>> validate_version_requirement("~1.2.3")
        True
        >>> validate_version_requirement(">=1.2.3")
        True
        >>> validate_version_requirement("latest")
        True
        >>> validate_version_requirement("invalid")
        False
    """
    # Check for 'latest'
    if requirement.lower() == "latest":
        return True

    # Check for minimum version
    if requirement.startswith(">="):
        try:
            parse_version(requirement[2:])
            return True
        except ValueError:
            return False

    # Check for caret
    if requirement.startswith("^"):
        try:
            parse_version(requirement[1:])
            return True
        except ValueError:
            return False

    # Check for tilde
    if requirement.startswith("~"):
        try:
            parse_version(requirement[1:])
            return True
        except ValueError:
            return False

    # Check for exact version
    try:
        parse_version(requirement)
        return True
    except ValueError:
        return False


def parse_skill_with_version(skill_spec: str) -> Tuple[str, str]:
    """Parse a skill specification into name and version components.

    Args:
        skill_spec: Skill specification string (e.g., "pdf@1.2.3" or "pdf@^1.2.0")

    Returns:
        A tuple of (skill_name, version_requirement)
        If no version is specified, returns (skill_name, "latest")

    Raises:
        VersionFormatError: If version requirement format is invalid

    Examples:
        >>> parse_skill_with_version("pdf@1.2.3")
        ("pdf", "1.2.3")
        >>> parse_skill_with_version("pdf@^1.2.0")
        ("pdf", "^1.2.0")
        >>> parse_skill_with_version("pdf")
        ("pdf", "latest")
    """
    if "@" not in skill_spec:
        return skill_spec, "latest"

    parts = skill_spec.split("@", 1)
    skill_name = parts[0].strip()
    version_req = parts[1].strip() if len(parts) > 1 else "latest"

    # Validate the version requirement
    if not validate_version_requirement(version_req):
        raise VersionFormatError(
            version_req, expected_format="1.2.3, ^1.2.3, ~1.2.3, >=1.2.3, or 'latest'"
        )

    return skill_name, version_req


def format_skill_with_version(skill_name: str, version: str) -> str:
    """Format a skill name and version into a specification string.

    Args:
        skill_name: Name of the skill
        version: Version string (can include operators like ^, ~, >=)

    Returns:
        Formatted skill specification string

    Raises:
        ValueError: If skill_name is empty
        VersionFormatError: If version format is invalid

    Examples:
        >>> format_skill_with_version("pdf", "1.2.3")
        "pdf@1.2.3"
        >>> format_skill_with_version("pdf", "^1.2.0")
        "pdf@^1.2.0"
        >>> format_skill_with_version("pdf", "latest")
        "pdf@latest"
    """
    if not skill_name:
        raise ValueError("Skill name cannot be empty")

    if not version or version.lower() == "latest":
        return f"{skill_name}@latest"

    if not validate_version_requirement(version):
        raise VersionFormatError(
            version, expected_format="1.2.3, ^1.2.3, ~1.2.3, >=1.2.3, or 'latest'"
        )

    return f"{skill_name}@{version}"


def resolve_version(
    skill_name: str, version_req: str, claude_dir: Path
) -> Optional[str]:
    """Resolve a version requirement to a specific version.

    Args:
        skill_name: Name of the skill
        version_req: Version requirement string
        claude_dir: Path to the Claude directory

    Returns:
        The resolved version string, or None if no compatible version found

    Examples:
        >>> resolve_version("pdf", "^1.2.0", Path("/home/user/.cortex"))
        "1.5.3"
        >>> resolve_version("pdf", "latest", Path("/home/user/.cortex"))
        "2.1.0"
    """
    # Handle 'latest' requirement
    if version_req.lower() == "latest":
        return get_latest_version(skill_name, claude_dir)

    # Get all available versions
    available_versions = get_skill_versions(skill_name, claude_dir)

    if not available_versions:
        return None

    # Find first compatible version (versions are sorted newest first)
    for version in available_versions:
        if check_compatibility(version_req, version):
            return version

    return None


def load_skill_metadata(skill_dir: Path) -> Dict[str, Any]:
    """Load metadata from a skill's YAML file.

    Args:
        skill_dir: Path to the skill directory

    Returns:
        Dictionary containing skill metadata, or empty dict if not found/invalid

    Examples:
        >>> load_skill_metadata(Path("/home/user/.cortex/skills/pdf@1.2.3"))
        {"name": "pdf", "version": "1.2.3", "description": "..."}
    """
    yaml_files = list(skill_dir.glob("*.yaml")) + list(skill_dir.glob("*.yml"))

    if not yaml_files:
        return {}

    # Use the first YAML file found
    yaml_file = yaml_files[0]

    try:
        metadata = safe_load_yaml(yaml_file)
        return metadata if isinstance(metadata, dict) else {}
    except Exception:
        # Return empty dict on any error (backward compatibility)
        return {}


def compare_versions(version1: str, version2: str) -> int:
    """Compare two semantic versions.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2

    Raises:
        ValueError: If either version string is invalid

    Examples:
        >>> compare_versions("1.2.3", "1.2.4")
        -1
        >>> compare_versions("2.0.0", "1.9.9")
        1
        >>> compare_versions("1.2.3", "1.2.3")
        0
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0
