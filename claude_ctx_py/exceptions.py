"""Custom exceptions for cortex-plugin.

This module defines a hierarchy of exceptions used throughout the plugin
to provide specific, actionable error messages with recovery suggestions.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence, Union

PathLike = Union[str, Path]


class ClaudeCtxError(Exception):
    """Base exception for all cortex errors.

    All custom exceptions inherit from this base class, allowing users
    to catch all cortex specific errors with a single except clause.
    """

    def __init__(self, message: str, recovery_hint: str = ""):
        """Initialize the exception.

        Args:
            message: Primary error message describing what went wrong
            recovery_hint: Optional suggestion for how to fix the error
        """
        self.message = message
        self.recovery_hint = recovery_hint
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with recovery hint if available."""
        if self.recovery_hint:
            return f"{self.message}\n  Hint: {self.recovery_hint}"
        return self.message


# File-related exceptions


class FileOperationError(ClaudeCtxError):
    """Base class for file operation errors."""

    pass


class SkillNotFoundError(FileOperationError):
    """Raised when a requested skill file cannot be found."""

    def __init__(
        self, skill_name: str, search_paths: Optional[Sequence[PathLike]] = None
    ) -> None:
        message = f"Skill '{skill_name}' not found"
        if search_paths:
            paths = ", ".join(str(p) for p in search_paths)
            message += f" in: {paths}"

        recovery_hint = "Run 'cortex skills list' to see available skills"
        super().__init__(message, recovery_hint)
        self.skill_name = skill_name
        self.search_paths = list(search_paths) if search_paths else None


class DirectoryNotFoundError(FileOperationError):
    """Raised when a required directory is missing."""

    def __init__(self, directory: str, purpose: str = ""):
        message = f"Directory not found: {directory}"
        if purpose:
            message += f" ({purpose})"

        recovery_hint = f"Create the directory with: mkdir -p {directory}"
        super().__init__(message, recovery_hint)
        self.directory = directory


class FileAccessError(FileOperationError):
    """Raised when file permissions prevent an operation."""

    def __init__(self, filepath: str, operation: str = "access"):
        message = f"Permission denied: cannot {operation} '{filepath}'"
        recovery_hint = f"Check file permissions with: ls -l {filepath}"
        super().__init__(message, recovery_hint)
        self.filepath = filepath
        self.operation = operation


# Validation exceptions


class ValidationError(ClaudeCtxError):
    """Base class for validation errors."""

    pass


class YAMLValidationError(ValidationError, ValueError):
    """Raised when YAML content is invalid or malformed."""

    def __init__(self, filepath: str, details: str = ""):
        message = f"Invalid YAML in '{filepath}'"
        if details:
            message += f": {details}"

        recovery_hint = (
            "Validate YAML syntax at https://www.yamllint.com/ or fix syntax errors"
        )
        ValidationError.__init__(self, message, recovery_hint)
        self.filepath = filepath


class SkillValidationError(ValidationError):
    """Raised when skill content fails validation."""

    def __init__(self, skill_name: str, errors: Sequence[str]) -> None:
        error_list = "\n  - ".join(errors)
        message = f"Skill '{skill_name}' validation failed:\n  - {error_list}"
        recovery_hint = "Fix validation errors and try again"
        super().__init__(message, recovery_hint)
        self.skill_name = skill_name
        self.validation_errors = list(errors)


class VersionFormatError(ValidationError, ValueError):
    """Raised when a version string has invalid format."""

    def __init__(self, version: str, expected_format: str = "X.Y.Z"):
        message = f"Invalid semantic version: '{version}'"
        recovery_hint = (
            f"Use semantic versioning format: {expected_format} (e.g., 1.2.3)"
        )
        ValidationError.__init__(self, message, recovery_hint)
        self.version = version


class DependencyError(ValidationError):
    """Base class for dependency-related errors."""

    pass


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected."""

    def __init__(self, cycle_path: Sequence[str]) -> None:
        cycle_list = list(cycle_path)
        cycle_str = " -> ".join(cycle_list)
        message = f"Circular dependency detected: {cycle_str}"
        recovery_hint = "Remove one of the dependencies to break the cycle"
        super().__init__(message, recovery_hint)
        self.cycle_path = cycle_list


class MissingDependencyError(DependencyError):
    """Raised when a required dependency is not available."""

    def __init__(self, dependency_name: str, required_by: str = ""):
        message = f"Missing dependency: '{dependency_name}'"
        if required_by:
            message += f" (required by '{required_by}')"

        recovery_hint = f"Install with: cortex skills install {dependency_name}"
        super().__init__(message, recovery_hint)
        self.dependency_name = dependency_name
        self.required_by = required_by


# Version-related exceptions


class VersionError(ClaudeCtxError):
    """Base class for version-related errors."""

    pass


class VersionCompatibilityError(VersionError):
    """Raised when version requirements are not met."""

    def __init__(self, required: str, available: str, skill_name: str = ""):
        message = f"Version mismatch: required '{required}', but found '{available}'"
        if skill_name:
            message = f"Skill '{skill_name}': {message}"

        recovery_hint = f"Install compatible version or update requirement"
        super().__init__(message, recovery_hint)
        self.required = required
        self.available = available
        self.skill_name = skill_name


class NoCompatibleVersionError(VersionError):
    """Raised when no version satisfies requirements."""

    def __init__(
        self,
        skill_name: str,
        requirement: str,
        available_versions: Sequence[str],
    ) -> None:
        available_list = list(available_versions)
        versions_str = ", ".join(available_list) if available_list else "none"
        message = f"No version of '{skill_name}' satisfies requirement '{requirement}'"
        message += f"\n  Available versions: {versions_str}"

        recovery_hint = "Adjust version requirement or check for newer releases"
        super().__init__(message, recovery_hint)
        self.skill_name = skill_name
        self.requirement = requirement
        self.available_versions = available_list


# Community-related exceptions


class CommunityError(ClaudeCtxError):
    """Base class for community skill errors."""

    pass


class SkillInstallationError(CommunityError):
    """Raised when skill installation fails."""

    def __init__(self, skill_name: str, reason: str = ""):
        message = f"Failed to install skill '{skill_name}'"
        if reason:
            message += f": {reason}"

        recovery_hint = "Check skill availability and permissions, then try again"
        super().__init__(message, recovery_hint)
        self.skill_name = skill_name


class RatingError(CommunityError):
    """Raised when skill rating fails."""

    def __init__(
        self, skill_name: str, rating_value: Optional[int] = None, reason: str = ""
    ) -> None:
        message = f"Failed to rate skill '{skill_name}'"
        if rating_value is not None:
            message += f" with value {rating_value}"
        if reason:
            message += f": {reason}"

        recovery_hint = "Rating must be an integer between 1 and 5"
        super().__init__(message, recovery_hint)
        self.skill_name = skill_name
        self.rating_value = rating_value


# Metrics and analytics exceptions


class MetricsError(ClaudeCtxError):
    """Base class for metrics-related errors."""

    pass


class MetricsFileError(MetricsError):
    """Raised when metrics file operations fail."""

    def __init__(self, filepath: str, operation: str, reason: str = ""):
        message = f"Failed to {operation} metrics file '{filepath}'"
        if reason:
            message += f": {reason}"

        recovery_hint = "Check file permissions and disk space"
        super().__init__(message, recovery_hint)
        self.filepath = filepath
        self.operation = operation


class InvalidMetricsDataError(MetricsError):
    """Raised when metrics data is corrupted or invalid."""

    def __init__(self, filepath: str, details: str = ""):
        message = f"Invalid metrics data in '{filepath}'"
        if details:
            message += f": {details}"

        recovery_hint = "Delete corrupted file or restore from backup"
        super().__init__(message, recovery_hint)
        self.filepath = filepath


class ExportError(MetricsError):
    """Raised when metrics export fails."""

    def __init__(self, format_type: str, reason: str = ""):
        message = f"Failed to export metrics as '{format_type}'"
        if reason:
            message += f": {reason}"

        recovery_hint = "Supported formats: json, csv, text"
        super().__init__(message, recovery_hint)
        self.format_type = format_type


# Composition and dependency resolution exceptions


class CompositionError(ClaudeCtxError):
    """Base class for composition-related errors."""

    pass


class InvalidCompositionError(CompositionError, ValueError):
    """Raised when composition.yaml is invalid."""

    def __init__(self, details: str):
        message = f"Invalid composition configuration: {details}"
        recovery_hint = "Check composition.yaml syntax and structure"
        CompositionError.__init__(self, message, recovery_hint)


# Missing package exceptions


class MissingPackageError(ClaudeCtxError):
    """Raised when a required Python package is not installed."""

    def __init__(self, package_name: str, purpose: str = ""):
        message = f"Required package '{package_name}' is not installed"
        if purpose:
            message += f" ({purpose})"

        recovery_hint = f"Install with: pip install {package_name}"
        super().__init__(message, recovery_hint)
        self.package_name = package_name
