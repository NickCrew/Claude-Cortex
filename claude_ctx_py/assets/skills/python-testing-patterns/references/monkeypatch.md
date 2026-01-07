# Monkeypatch for Testing

## Environment Variables

**Modify environment safely:**
```python
import os
import pytest

def get_api_key() -> str:
    return os.environ.get("API_KEY", "default-key")

def test_api_key_from_env(monkeypatch):
    """Test with custom environment variable."""
    monkeypatch.setenv("API_KEY", "test-key-123")
    assert get_api_key() == "test-key-123"

def test_api_key_default(monkeypatch):
    """Test default value."""
    monkeypatch.delenv("API_KEY", raising=False)
    assert get_api_key() == "default-key"
```

## Object Attributes

**Modify object attributes temporarily:**
```python
class Config:
    debug = False
    timeout = 30

def test_monkeypatch_attribute(monkeypatch):
    """Modify object attributes."""
    config = Config()
    monkeypatch.setattr(config, "debug", True)
    monkeypatch.setattr(config, "timeout", 60)

    assert config.debug is True
    assert config.timeout == 60
```

## Module Attributes

**Replace module-level functions or constants:**
```python
import module

def test_monkeypatch_module_function(monkeypatch):
    """Replace module function."""
    def mock_function():
        return "mocked"

    monkeypatch.setattr(module, "original_function", mock_function)
    assert module.original_function() == "mocked"

def test_monkeypatch_constant(monkeypatch):
    """Replace module constant."""
    monkeypatch.setattr(module, "MAX_RETRIES", 5)
    assert module.MAX_RETRIES == 5
```

## Dictionary Items

**Modify dictionaries:**
```python
def test_monkeypatch_dict(monkeypatch):
    """Modify dictionary items."""
    config = {"key": "original"}
    monkeypatch.setitem(config, "key", "modified")
    monkeypatch.setitem(config, "new_key", "value")

    assert config["key"] == "modified"
    assert config["new_key"] == "value"

def test_delete_dict_item(monkeypatch):
    """Delete dictionary items."""
    config = {"key": "value", "delete_me": "gone"}
    monkeypatch.delitem(config, "delete_me")

    assert "delete_me" not in config
```

## System Path

**Modify sys.path:**
```python
import sys

def test_monkeypatch_syspath(monkeypatch):
    """Add to sys.path temporarily."""
    monkeypatch.syspath_prepend("/custom/path")
    assert "/custom/path" in sys.path
```

## Time Mocking

**Mock time and datetime:**
```python
from datetime import datetime

def test_mock_datetime(monkeypatch):
    """Mock datetime.now()."""
    class MockDateTime:
        @classmethod
        def now(cls):
            return datetime(2024, 1, 1, 12, 0, 0)

    monkeypatch.setattr("datetime.datetime", MockDateTime)
    assert datetime.now() == datetime(2024, 1, 1, 12, 0, 0)
```

## Working Directory

**Change working directory:**
```python
def test_change_directory(monkeypatch, tmp_path):
    """Change working directory temporarily."""
    monkeypatch.chdir(tmp_path)
    assert os.getcwd() == str(tmp_path)
```

## Common Patterns

### Mock External API Calls
```python
def test_mock_requests(monkeypatch):
    """Mock requests library."""
    class MockResponse:
        @staticmethod
        def json():
            return {"key": "value"}

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    import requests
    response = requests.get("https://api.example.com")
    assert response.json() == {"key": "value"}
```

### Mock Database Connections
```python
def test_mock_database(monkeypatch):
    """Mock database connection."""
    class MockDB:
        def query(self, sql):
            return [{"id": 1, "name": "test"}]

    monkeypatch.setattr("module.Database", MockDB)

    db = module.Database()
    results = db.query("SELECT * FROM users")
    assert len(results) == 1
```

## Undo Changes

**All changes automatically reverted after test:**
```python
def test_automatic_cleanup(monkeypatch):
    """Changes reverted after test."""
    original_value = os.environ.get("TEST_VAR")

    monkeypatch.setenv("TEST_VAR", "temporary")
    assert os.environ["TEST_VAR"] == "temporary"

    # After test completes, TEST_VAR reverts to original_value
```

## Best Practices

1. **Use for simple mocking**: Monkeypatch is simpler than mock.patch for basic cases
2. **Environment variables**: Preferred method for env var mocking
3. **Automatic cleanup**: No need for teardown, monkeypatch handles it
4. **Combine with fixtures**: Use monkeypatch in fixtures for reusable mocking
5. **Type safety**: Be careful with type checkers, may need type: ignore
6. **Integration with pytest**: Native pytest fixture, well-integrated
7. **Not for complex mocking**: Use unittest.mock for complex scenarios
