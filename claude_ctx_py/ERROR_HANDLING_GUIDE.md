# Error Handling Developer Guide

Quick reference for using the improved error handling system in claude-ctx-plugin.

## Quick Start

### Import the exceptions you need:
```python
from .exceptions import (
    SkillNotFoundError,
    YAMLValidationError,
    MetricsFileError,
)
from .error_utils import safe_load_yaml, safe_read_file
```

### Use safe utilities instead of raw file operations:
```python
# Before
with open(file_path, 'r') as f:
    data = yaml.safe_load(f)

# After
data = safe_load_yaml(file_path)  # Raises YAMLValidationError with line/column
```

## Common Patterns

### Reading Files
```python
from .error_utils import safe_read_file
from .exceptions import SkillNotFoundError, FileAccessError

try:
    content = safe_read_file(skill_file)
except SkillNotFoundError as e:
    # Handle missing skill
    print(f"Skill not found: {e}")
except FileAccessError as e:
    # Handle permission issues
    print(f"Cannot read file: {e}")
```

### Loading YAML
```python
from .error_utils import safe_load_yaml
from .exceptions import YAMLValidationError

try:
    config = safe_load_yaml(config_file)
except YAMLValidationError as e:
    # Error includes line/column numbers
    print(f"Invalid YAML: {e}")
```

### Loading JSON
```python
from .error_utils import safe_load_json
from .exceptions import InvalidMetricsDataError

try:
    metrics = safe_load_json(metrics_file)
except InvalidMetricsDataError as e:
    # Error includes JSON parse details
    print(f"Corrupted data: {e}")
    # Fall back to defaults
    metrics = {"skills": {}}
```

### Writing Files
```python
from .error_utils import safe_write_file, safe_save_json
from .exceptions import FileAccessError, MetricsFileError

# Text files
safe_write_file(output_file, content, create_parents=True)

# JSON files
safe_save_json(metrics_file, data, indent=2)
```

### Creating Directories
```python
from .error_utils import ensure_directory

ensure_directory(skills_dir, purpose="skill storage")
```

## Exception Hierarchy

### Choose the right exception:

**File Operations:**
- File doesn't exist? → `SkillNotFoundError`
- Permission denied? → `FileAccessError`
- Directory missing? → `DirectoryNotFoundError`

**Validation:**
- Invalid YAML? → `YAMLValidationError`
- Skill validation failed? → `SkillValidationError`
- Invalid version? → `VersionFormatError`
- Circular deps? → `CircularDependencyError`

**Metrics:**
- Can't read metrics? → `MetricsFileError`
- Corrupted data? → `InvalidMetricsDataError`
- Export failed? → `ExportError`

**Community:**
- Installation failed? → `SkillInstallationError`
- Rating failed? → `RatingError`

**Composition:**
- Invalid composition? → `InvalidCompositionError`

**Dependencies:**
- Missing package? → `MissingPackageError`

## Creating Custom Exceptions

### Basic usage:
```python
from .exceptions import ClaudeCtxError

class MyCustomError(ClaudeCtxError):
    def __init__(self, detail: str):
        message = f"Operation failed: {detail}"
        recovery_hint = "Try restarting the application"
        super().__init__(message, recovery_hint)
```

### With context:
```python
from .exceptions import FileOperationError

class ConfigurationError(FileOperationError):
    def __init__(self, config_file: str, reason: str):
        message = f"Invalid configuration in '{config_file}': {reason}"
        recovery_hint = f"Check {config_file} syntax and try again"
        super().__init__(message, recovery_hint)
        self.config_file = config_file
        self.reason = reason
```

## Error Messages Best Practices

### DO:
- Be specific about what went wrong
- Include file paths and names
- Provide actionable recovery steps
- Use present tense ("File not found" not "File wasn't found")

### DON'T:
- Use generic "Error occurred" messages
- Include stack traces in user messages
- Use technical jargon without explanation
- Blame the user ("You provided an invalid file")

### Good Examples:
```python
# Good
raise SkillNotFoundError(
    skill_name='react-hooks',
    search_paths=[skills_dir]
)
# → Skill 'react-hooks' not found in: /home/user/.claude/skills
#   Hint: Run 'claude-ctx skills list' to see available skills

# Good
raise YAMLValidationError(
    str(config_file),
    "line 5, column 3: expected a mapping"
)
# → Invalid YAML in '/home/user/.claude/config.yaml': line 5, column 3: expected a mapping
#   Hint: Validate YAML syntax at https://www.yamllint.com/

# Bad
raise ValueError("Invalid file")
# → ValueError: Invalid file
```

## Catching Exceptions

### Specific to general:
```python
try:
    data = safe_load_yaml(file_path)
except YAMLValidationError as e:
    # Handle YAML syntax errors
    return {"error": str(e)}
except SkillNotFoundError as e:
    # Handle missing files
    return {"error": str(e)}
except ClaudeCtxError as e:
    # Catch all claude-ctx errors
    return {"error": str(e)}
except Exception as e:
    # Last resort for unexpected errors
    logger.error(f"Unexpected error: {e}")
    raise
```

### With recovery:
```python
from .exceptions import InvalidMetricsDataError

def load_metrics_with_fallback(metrics_file: Path) -> Dict:
    """Load metrics with automatic fallback on errors."""
    try:
        return safe_load_json(metrics_file)
    except InvalidMetricsDataError as e:
        logger.warning(f"Corrupted metrics file: {e}")
        # Return default structure
        return {"skills": {}}
    except FileNotFoundError:
        # File doesn't exist yet, return defaults
        return {"skills": {}}
```

## CLI Integration

### Format errors for users:
```python
from .error_utils import format_error_for_cli

try:
    result = perform_operation()
except Exception as e:
    error_msg = format_error_for_cli(e)
    print(error_msg, file=sys.stderr)
    return 1
```

### Custom formatting:
```python
from .exceptions import ClaudeCtxError

try:
    result = perform_operation()
except ClaudeCtxError as e:
    # Custom exceptions have recovery hints built-in
    print(f"Error: {e}", file=sys.stderr)
    return 1
except Exception as e:
    # Standard exceptions need manual formatting
    print(f"Error: {e}", file=sys.stderr)
    print("  Hint: Check logs for more information", file=sys.stderr)
    return 1
```

## Testing Error Handling

### Test that errors are raised:
```python
import pytest
from claude_ctx_py.exceptions import SkillNotFoundError

def test_missing_skill_raises_error():
    with pytest.raises(SkillNotFoundError) as exc_info:
        load_skill("nonexistent-skill")

    assert "nonexistent-skill" in str(exc_info.value)
    assert "not found" in str(exc_info.value).lower()
```

### Test recovery hints:
```python
def test_error_includes_recovery_hint():
    with pytest.raises(SkillNotFoundError) as exc_info:
        load_skill("missing-skill")

    error_message = str(exc_info.value)
    assert "Hint:" in error_message
    assert "claude-ctx skills list" in error_message
```

### Test error attributes:
```python
def test_error_attributes():
    error = SkillNotFoundError(
        skill_name="test-skill",
        search_paths=[Path("/path1"), Path("/path2")]
    )

    assert error.skill_name == "test-skill"
    assert len(error.search_paths) == 2
```

## Migration Checklist

When updating existing code:

1. [ ] Replace `except Exception` with specific exceptions
2. [ ] Use safe utilities (`safe_load_yaml`, `safe_read_file`, etc.)
3. [ ] Add recovery hints to error messages
4. [ ] Include context (file paths, skill names, etc.)
5. [ ] Test error cases
6. [ ] Update docstrings with `Raises:` section
7. [ ] Update calling code to catch new exceptions
