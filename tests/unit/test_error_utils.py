"""Tests for error_utils module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_ctx_py.error_utils import (
    safe_read_file,
    safe_write_file,
    safe_load_yaml,
    safe_save_yaml,
    safe_load_json,
    safe_save_json,
    with_file_error_context,
    ensure_directory,
    handle_file_operation,
    format_error_for_cli,
)
from claude_ctx_py.exceptions import (
    SkillNotFoundError,
    FileAccessError,
    DirectoryNotFoundError,
    YAMLValidationError,
    InvalidMetricsDataError,
    MetricsFileError,
    MissingPackageError,
)


class TestSafeReadFile:
    """Tests for safe_read_file function."""

    def test_read_existing_file(self, tmp_path: Path):
        """Test reading an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        content = safe_read_file(test_file)

        assert content == "hello world"

    def test_read_nonexistent_file(self, tmp_path: Path):
        """Test reading non-existent file raises SkillNotFoundError."""
        missing = tmp_path / "missing.txt"

        with pytest.raises(SkillNotFoundError):
            safe_read_file(missing)

    def test_read_with_custom_encoding(self, tmp_path: Path):
        """Test reading with custom encoding."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")

        content = safe_read_file(test_file, encoding="utf-8")

        assert content == "hello"


class TestSafeWriteFile:
    """Tests for safe_write_file function."""

    def test_write_new_file(self, tmp_path: Path):
        """Test writing a new file."""
        test_file = tmp_path / "test.txt"

        safe_write_file(test_file, "hello world")

        assert test_file.read_text() == "hello world"

    def test_write_creates_parent_dirs(self, tmp_path: Path):
        """Test writing creates parent directories."""
        nested_file = tmp_path / "sub" / "dir" / "test.txt"

        safe_write_file(nested_file, "hello", create_parents=True)

        assert nested_file.read_text() == "hello"

    def test_write_without_parent_creation(self, tmp_path: Path):
        """Test writing without parent creation raises error."""
        nested_file = tmp_path / "missing_parent" / "test.txt"

        with pytest.raises(DirectoryNotFoundError):
            safe_write_file(nested_file, "hello", create_parents=False)

    def test_overwrite_existing_file(self, tmp_path: Path):
        """Test overwriting an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("old content")

        safe_write_file(test_file, "new content")

        assert test_file.read_text() == "new content"


class TestSafeLoadYaml:
    """Tests for safe_load_yaml function."""

    def test_load_valid_yaml(self, tmp_path: Path):
        """Test loading valid YAML file."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\nnumber: 42")

        data = safe_load_yaml(yaml_file)

        assert data["key"] == "value"
        assert data["number"] == 42

    def test_load_empty_yaml(self, tmp_path: Path):
        """Test loading empty YAML returns empty dict."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        data = safe_load_yaml(yaml_file)

        assert data == {}

    def test_load_invalid_yaml(self, tmp_path: Path):
        """Test loading invalid YAML raises YAMLValidationError."""
        yaml_file = tmp_path / "invalid.yaml"
        yaml_file.write_text("key: [unclosed")

        with pytest.raises(YAMLValidationError):
            safe_load_yaml(yaml_file)

    def test_load_yaml_not_dict(self, tmp_path: Path):
        """Test loading YAML that's not a dict raises error."""
        yaml_file = tmp_path / "list.yaml"
        yaml_file.write_text("- item1\n- item2")

        with pytest.raises(YAMLValidationError):
            safe_load_yaml(yaml_file)

    def test_load_nonexistent_yaml(self, tmp_path: Path):
        """Test loading non-existent YAML raises SkillNotFoundError."""
        missing = tmp_path / "missing.yaml"

        with pytest.raises(SkillNotFoundError):
            safe_load_yaml(missing)


class TestSafeSaveYaml:
    """Tests for safe_save_yaml function."""

    def test_save_yaml(self, tmp_path: Path):
        """Test saving YAML file."""
        yaml_file = tmp_path / "test.yaml"
        data = {"key": "value", "number": 42}

        safe_save_yaml(yaml_file, data)

        assert yaml_file.exists()
        content = yaml_file.read_text()
        assert "key: value" in content

    def test_save_yaml_creates_parents(self, tmp_path: Path):
        """Test saving YAML creates parent directories."""
        yaml_file = tmp_path / "sub" / "dir" / "test.yaml"

        safe_save_yaml(yaml_file, {"key": "value"})

        assert yaml_file.exists()


class TestSafeLoadJson:
    """Tests for safe_load_json function."""

    def test_load_valid_json(self, tmp_path: Path):
        """Test loading valid JSON file."""
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value", "number": 42}')

        data = safe_load_json(json_file)

        assert data["key"] == "value"
        assert data["number"] == 42

    def test_load_invalid_json(self, tmp_path: Path):
        """Test loading invalid JSON raises InvalidMetricsDataError."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text('{"key": "value"')  # Missing closing brace

        with pytest.raises(InvalidMetricsDataError):
            safe_load_json(json_file)

    def test_load_json_not_dict(self, tmp_path: Path):
        """Test loading JSON that's not an object raises error."""
        json_file = tmp_path / "array.json"
        json_file.write_text('["item1", "item2"]')

        with pytest.raises(InvalidMetricsDataError):
            safe_load_json(json_file)

    def test_load_nonexistent_json(self, tmp_path: Path):
        """Test loading non-existent JSON raises SkillNotFoundError."""
        missing = tmp_path / "missing.json"

        with pytest.raises(SkillNotFoundError):
            safe_load_json(missing)


class TestSafeSaveJson:
    """Tests for safe_save_json function."""

    def test_save_json(self, tmp_path: Path):
        """Test saving JSON file."""
        json_file = tmp_path / "test.json"
        data = {"key": "value", "number": 42}

        safe_save_json(json_file, data)

        assert json_file.exists()
        loaded = json.loads(json_file.read_text())
        assert loaded["key"] == "value"

    def test_save_json_with_indent(self, tmp_path: Path):
        """Test saving JSON with custom indent."""
        json_file = tmp_path / "test.json"

        safe_save_json(json_file, {"key": "value"}, indent=4)

        content = json_file.read_text()
        assert "    " in content  # 4-space indent

    def test_save_non_serializable(self, tmp_path: Path):
        """Test saving non-serializable data raises MetricsFileError."""
        json_file = tmp_path / "test.json"

        with pytest.raises(MetricsFileError):
            safe_save_json(json_file, {"func": lambda x: x})


class TestWithFileErrorContext:
    """Tests for with_file_error_context decorator."""

    def test_successful_operation(self, tmp_path: Path):
        """Test decorator with successful operation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        @with_file_error_context("read", test_file)
        def read_file():
            return test_file.read_text()

        result = read_file()
        assert result == "hello"

    def test_file_not_found(self, tmp_path: Path):
        """Test decorator wraps FileNotFoundError."""
        missing = tmp_path / "missing.txt"

        @with_file_error_context("read", missing)
        def read_file():
            raise FileNotFoundError()

        with pytest.raises(SkillNotFoundError):
            read_file()


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_create_new_directory(self, tmp_path: Path):
        """Test creating a new directory."""
        new_dir = tmp_path / "new_dir"

        ensure_directory(new_dir)

        assert new_dir.is_dir()

    def test_create_nested_directory(self, tmp_path: Path):
        """Test creating nested directories."""
        nested = tmp_path / "a" / "b" / "c"

        ensure_directory(nested)

        assert nested.is_dir()

    def test_existing_directory(self, tmp_path: Path):
        """Test with existing directory."""
        existing = tmp_path / "existing"
        existing.mkdir()

        ensure_directory(existing)  # Should not raise

        assert existing.is_dir()


class TestHandleFileOperation:
    """Tests for handle_file_operation function."""

    def test_successful_operation(self, tmp_path: Path):
        """Test handling successful operation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello")

        success, result, error = handle_file_operation(
            lambda: test_file.read_text(),
            test_file,
            "read"
        )

        assert success is True
        assert result == "hello"
        assert error is None

    def test_file_not_found_with_default(self, tmp_path: Path):
        """Test file not found with default value."""
        missing = tmp_path / "missing.txt"

        success, result, error = handle_file_operation(
            lambda: missing.read_text(),
            missing,
            "read",
            default_on_error=""
        )

        assert success is False
        assert result == ""
        assert "not found" in error.lower()

    def test_file_not_found_without_default(self, tmp_path: Path):
        """Test file not found without default raises."""
        missing = tmp_path / "missing.txt"

        with pytest.raises(SkillNotFoundError):
            handle_file_operation(
                lambda: missing.read_text(),
                missing,
                "read",
                default_on_error=None
            )

    def test_json_decode_error_with_default(self, tmp_path: Path):
        """Test JSON decode error with default."""
        json_file = tmp_path / "bad.json"
        json_file.write_text("not json")

        success, result, error = handle_file_operation(
            lambda: json.loads(json_file.read_text()),
            json_file,
            "parse",
            default_on_error={}
        )

        assert success is False
        assert result == {}
        assert "Invalid" in error


class TestFormatErrorForCli:
    """Tests for format_error_for_cli function."""

    def test_format_custom_error(self):
        """Test formatting custom ClaudeCtxError."""
        error = SkillNotFoundError("test-skill", search_paths=["/path"])

        result = format_error_for_cli(error)

        assert "test-skill" in result

    def test_format_file_not_found_error(self):
        """Test formatting FileNotFoundError."""
        error = FileNotFoundError("missing.txt")

        result = format_error_for_cli(error)

        assert "FileNotFoundError" in result
        assert "Hint:" in result
        assert "path" in result.lower()

    def test_format_permission_error(self):
        """Test formatting PermissionError."""
        error = PermissionError("denied")

        result = format_error_for_cli(error)

        assert "PermissionError" in result
        assert "Hint:" in result
        assert "permission" in result.lower()

    def test_format_json_decode_error(self):
        """Test formatting JSONDecodeError."""
        try:
            json.loads("not json")
        except json.JSONDecodeError as e:
            result = format_error_for_cli(e)

        assert "JSONDecodeError" in result
        assert "Hint:" in result
        assert "JSON" in result

    def test_format_generic_error(self):
        """Test formatting generic exception."""
        error = RuntimeError("something went wrong")

        result = format_error_for_cli(error)

        assert "RuntimeError" in result
        assert "something went wrong" in result
        assert "Hint:" in result
