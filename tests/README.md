# Test Suite for claude-ctx-plugin

This directory contains the test suite for the claude-ctx-plugin project.

## Structure

```
tests/
├── conftest.py           # Shared pytest fixtures
├── unit/                 # Unit tests for individual modules
│   ├── test_composer.py  # Skill composition and dependency resolution
│   ├── test_versioner.py # Semantic versioning utilities
│   ├── test_metrics.py   # Metrics tracking
│   ├── test_analytics.py # Analytics and reporting
│   ├── test_activator.py # Activation system
│   └── test_community.py # Community skill management
└── integration/          # Integration tests
    └── test_cli.py       # CLI command integration tests
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### Specific Module
```bash
pytest tests/unit/test_composer.py
```

### With Coverage Report
```bash
pytest --cov=claude_ctx_py --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in your browser.

## Test Markers

Tests are marked with the following categories:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for CLI and workflows
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.requires_yaml` - Tests that require PyYAML to be installed

### Run Specific Marker
```bash
pytest -m unit           # Run only unit tests
pytest -m integration    # Run only integration tests
pytest -m "not slow"     # Skip slow tests
```

## Fixtures

Common fixtures are defined in `conftest.py`:

- `tmp_claude_dir` - Temporary .claude directory with standard structure
- `mock_claude_home` - Sets CLAUDE_PLUGIN_ROOT to temporary directory
- `sample_skill_metadata` - Sample skill metadata for testing
- `sample_metrics` - Sample metrics data
- `metrics_file` - Creates metrics file with sample data
- `sample_composition_map` - Sample skill composition map
- `composition_file` - Creates composition.yaml with sample data
- `skill_directory` - Sample skill directory with metadata
- `activations_file` - Sample activations data for analytics

## Coverage Goals

Target: 80% coverage across the codebase

Current coverage can be checked with:
```bash
pytest --cov=claude_ctx_py --cov-report=term-missing
```

## Writing Tests

### Unit Test Example
```python
import pytest
from claude_ctx_py import module_name


@pytest.mark.unit
class TestFeature:
    """Tests for feature X."""
    
    def test_basic_functionality(self) -> None:
        """Test that feature works in basic case."""
        result = module_name.function()
        assert result == expected_value
```

### Using Fixtures
```python
@pytest.mark.unit
def test_with_fixture(tmp_claude_dir: Path) -> None:
    """Test using temporary .claude directory."""
    # tmp_claude_dir is automatically created and cleaned up
    skill_dir = tmp_claude_dir / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    # Test code here...
```

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Scheduled nightly builds

CI configuration requires:
- Python 3.9+
- All dev dependencies from pyproject.toml
- pytest, pytest-cov, pytest-mock
