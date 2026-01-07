"""Error handling utilities for cortex-plugin.

This module provides reusable error handling functions that wrap common
operations and provide consistent, actionable error messages.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from .exceptions import (
    DirectoryNotFoundError,
    FileAccessError,
    InvalidMetricsDataError,
    MetricsFileError,
    MissingPackageError,
    SkillNotFoundError,
    YAMLValidationError,
)

T = TypeVar("T")


def safe_read_file(filepath: Path, encoding: str = "utf-8") -> str:
    """Safely read a file with descriptive error handling.

    Args:
        filepath: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        File content as string

    Raises:
        SkillNotFoundError: If file doesn't exist
        FileAccessError: If file can't be read due to permissions
        UnicodeDecodeError: If file encoding is invalid
    """
    if not filepath.exists():
        raise SkillNotFoundError(filepath.stem, search_paths=[str(filepath.parent)])

    try:
        return filepath.read_text(encoding=encoding)
    except PermissionError as exc:
        raise FileAccessError(str(filepath), "read") from exc
    except UnicodeDecodeError as exc:
        raise UnicodeDecodeError(
            exc.encoding,
            exc.object,
            exc.start,
            exc.end,
            f"Invalid {encoding} encoding in '{filepath}'. Try a different encoding.",
        ) from exc


def safe_write_file(
    filepath: Path, content: str, encoding: str = "utf-8", create_parents: bool = True
) -> None:
    """Safely write to a file with descriptive error handling.

    Args:
        filepath: Path to the file to write
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_parents: Whether to create parent directories (default: True)

    Raises:
        DirectoryNotFoundError: If parent directory doesn't exist
        FileAccessError: If file can't be written due to permissions
        OSError: If disk is full or other OS-level error occurs
    """
    if create_parents:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    elif not filepath.parent.exists():
        raise DirectoryNotFoundError(
            str(filepath.parent), purpose="parent directory for file write"
        )

    try:
        filepath.write_text(content, encoding=encoding)
    except PermissionError as exc:
        raise FileAccessError(str(filepath), "write") from exc
    except OSError as exc:
        if "No space left on device" in str(exc):
            raise OSError(
                f"Cannot write '{filepath}': No space left on device. "
                "Free up disk space and try again."
            ) from exc
        raise


def safe_load_yaml(filepath: Path) -> Dict[str, Any]:
    """Safely load and parse a YAML file.

    Args:
        filepath: Path to the YAML file

    Returns:
        Parsed YAML content as dictionary

    Raises:
        MissingPackageError: If PyYAML is not installed
        SkillNotFoundError: If file doesn't exist
        YAMLValidationError: If YAML syntax is invalid
        FileAccessError: If file can't be read
    """
    if yaml is None:
        raise MissingPackageError("pyyaml", purpose="YAML file parsing")

    content = safe_read_file(filepath)

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        # Extract line and column info if available
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            details = f"line {mark.line + 1}, column {mark.column + 1}"
        else:
            details = str(exc)

        raise YAMLValidationError(str(filepath), details) from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise YAMLValidationError(
            str(filepath), f"Expected dictionary, got {type(data).__name__}"
        )

    return data


def safe_save_yaml(filepath: Path, data: Dict[str, Any]) -> None:
    """Safely save data to a YAML file.

    Args:
        filepath: Path to the YAML file
        data: Data to save

    Raises:
        MissingPackageError: If PyYAML is not installed
        FileAccessError: If file can't be written
    """
    if yaml is None:
        raise MissingPackageError("pyyaml", purpose="YAML file writing")

    try:
        content = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    except yaml.YAMLError as exc:
        raise YAMLValidationError(
            str(filepath), f"Failed to serialize data: {exc}"
        ) from exc

    safe_write_file(filepath, content)


def safe_load_json(filepath: Path) -> Dict[str, Any]:
    """Safely load and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON content as dictionary

    Raises:
        SkillNotFoundError: If file doesn't exist
        InvalidMetricsDataError: If JSON syntax is invalid
        FileAccessError: If file can't be read
    """
    content = safe_read_file(filepath)

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise InvalidMetricsDataError(
            str(filepath),
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc

    if not isinstance(data, dict):
        raise InvalidMetricsDataError(
            str(filepath), f"Expected JSON object, got {type(data).__name__}"
        )

    return data


def safe_save_json(filepath: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """Safely save data to a JSON file.

    Args:
        filepath: Path to the JSON file
        data: Data to save
        indent: Indentation level (default: 2)

    Raises:
        MetricsFileError: If file can't be written or data can't be serialized
    """
    try:
        content = json.dumps(data, indent=indent)
    except (TypeError, ValueError) as exc:
        raise MetricsFileError(
            str(filepath), "serialize", f"Data is not JSON serializable: {exc}"
        ) from exc

    try:
        safe_write_file(filepath, content)
    except (FileAccessError, OSError) as exc:
        raise MetricsFileError(str(filepath), "write", str(exc)) from exc


def with_file_error_context(
    operation: str, filepath: Path
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to add file operation context to errors.

    Args:
        operation: Description of the operation (e.g., "read", "write")
        filepath: Path being operated on

    Returns:
        Decorator function

    Example:
        @with_file_error_context("read", skill_file)
        def load_skill():
            return skill_file.read_text()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as exc:
                raise SkillNotFoundError(
                    filepath.stem, search_paths=[str(filepath.parent)]
                ) from exc
            except PermissionError as exc:
                raise FileAccessError(str(filepath), operation) from exc
            except OSError as exc:
                raise OSError(f"Failed to {operation} '{filepath}': {exc}") from exc

        return wrapper

    return decorator


def ensure_directory(directory: Path, purpose: str = "") -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to the directory
        purpose: Description of what the directory is for (optional)

    Raises:
        FileAccessError: If directory can't be created due to permissions
        OSError: If directory creation fails
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        raise FileAccessError(str(directory), "create directory") from exc
    except OSError as exc:
        purpose_str = f" ({purpose})" if purpose else ""
        raise OSError(
            f"Failed to create directory '{directory}'{purpose_str}: {exc}"
        ) from exc


def handle_file_operation(
    operation: Callable[[], T],
    filepath: Path,
    operation_name: str,
    default_on_error: Optional[T] = None,
) -> Tuple[bool, Optional[T], Optional[str]]:
    """Execute a file operation with consistent error handling.

    Args:
        operation: Function to execute
        filepath: Path being operated on
        operation_name: Human-readable operation description
        default_on_error: Default value to return on error (if None, re-raises)

    Returns:
        Tuple of (success, result, error_message)

    Example:
        success, data, error = handle_file_operation(
            lambda: json.loads(file.read_text()),
            file,
            "load metrics",
            default_on_error={}
        )
    """
    try:
        result = operation()
        return True, result, None
    except FileNotFoundError:
        error = f"File not found: {filepath}"
        if default_on_error is not None:
            return False, default_on_error, error
        raise SkillNotFoundError(filepath.stem, search_paths=[str(filepath.parent)])
    except PermissionError:
        error = f"Permission denied: cannot {operation_name} '{filepath}'"
        if default_on_error is not None:
            return False, default_on_error, error
        raise FileAccessError(str(filepath), operation_name)
    except json.JSONDecodeError as exc:
        error = f"Invalid file format in '{filepath}': {exc}"
        if default_on_error is not None:
            return False, default_on_error, error
        raise InvalidMetricsDataError(str(filepath), str(exc))
    except Exception as exc:
        if yaml is not None and isinstance(exc, yaml.YAMLError):
            error = f"Invalid file format in '{filepath}': {exc}"
            if default_on_error is not None:
                return False, default_on_error, error
            raise InvalidMetricsDataError(str(filepath), str(exc))
        error = f"Failed to {operation_name} '{filepath}': {exc}"
        if default_on_error is not None:
            return False, default_on_error, error
        raise


def format_error_for_cli(error: Exception) -> str:
    """Format an error for CLI display with recovery hints.

    Args:
        error: Exception to format

    Returns:
        Formatted error message string
    """
    from .exceptions import ClaudeCtxError

    if isinstance(error, ClaudeCtxError):
        # Custom exceptions already have good formatting
        return str(error)

    # Format standard exceptions with context
    error_type = type(error).__name__
    message = str(error)

    # Add recovery hints for common errors
    hints = {
        "FileNotFoundError": "Check that the path is correct",
        "PermissionError": "Check file/directory permissions",
        "JSONDecodeError": "Verify JSON syntax is valid",
        "UnicodeDecodeError": "Try a different file encoding",
        "OSError": "Check disk space and permissions",
    }

    hint = hints.get(error_type, "See documentation for more information")

    return f"{error_type}: {message}\n  Hint: {hint}"
