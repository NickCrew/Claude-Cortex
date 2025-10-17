---
name: python-testing-patterns
description: Python testing patterns and best practices using pytest, mocking, and property-based testing. Use when writing unit tests, integration tests, or implementing test-driven development in Python projects.
---

# Python Testing Patterns

Comprehensive guide to implementing robust testing strategies in Python using pytest, fixtures, mocking, parameterization, and property-based testing for building reliable, maintainable test suites.

## When to Use This Skill

- Writing unit tests for Python functions and classes
- Setting up comprehensive test suites and infrastructure
- Implementing test-driven development (TDD) workflows
- Creating integration tests for APIs, databases, and services
- Mocking external dependencies and third-party services
- Testing async code and concurrent operations
- Implementing property-based testing with Hypothesis
- Setting up CI/CD test automation
- Debugging failing tests and improving test coverage

## Core Patterns

### 1. Pytest Fundamentals

**Basic test structure with pytest:**
```python
# test_calculator.py
import pytest

class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

def test_addition():
    """Test basic addition."""
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.add(-1, 1) == 0

def test_division_by_zero():
    """Test exception handling."""
    calc = Calculator()
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(5, 0)
```

**Key concepts:**
- Test discovery: Files matching `test_*.py` or `*_test.py`
- Test functions start with `test_`
- Use `assert` statements for verification
- `pytest.raises()` for exception testing
- Run with `pytest` or `pytest -v` for verbose output

### 2. Fixtures for Setup and Teardown

**Reusable test resources and cleanup:**
```python
import pytest
from typing import Generator

class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Fixture providing database connection."""
    # Setup
    database = Database("sqlite:///:memory:")
    database.connect()

    yield database  # Provide to test

    # Teardown
    database.disconnect()

def test_database_connection(db):
    """Test using fixture."""
    assert db.connected is True

@pytest.fixture(scope="session")
def app_config():
    """Session-scoped fixture - created once."""
    return {"debug": True, "api_key": "test-key"}

@pytest.fixture(scope="module")
def api_client(app_config):
    """Module-scoped fixture."""
    client = {"config": app_config, "session": "active"}
    yield client
    client["session"] = "closed"
```

**Fixture scopes:**
- `function` (default): Per test function
- `class`: Per test class
- `module`: Per test module
- `session`: Once per test session
- `autouse=True`: Automatically used by all tests

### 3. Parametrized Tests

**Test multiple inputs efficiently:**
```python
import pytest

def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[1]

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("test.user@domain.co.uk", True),
    ("invalid.email", False),
    ("@example.com", False),
    ("user@domain", False),
])
def test_email_validation(email, expected):
    """Test email validation with multiple cases."""
    assert is_valid_email(email) == expected

# Custom test IDs for clarity
@pytest.mark.parametrize("value,expected", [
    pytest.param(1, True, id="positive"),
    pytest.param(0, False, id="zero"),
    pytest.param(-1, False, id="negative"),
])
def test_is_positive(value, expected):
    assert (value > 0) == expected

# Multiple parameter sets
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_addition(a, b, expected):
    calc = Calculator()
    assert calc.add(a, b) == expected
```

**Benefits:**
- DRY: Reduce test code duplication
- Coverage: Test edge cases systematically
- Readability: Clear input/output relationships

### 4. Mocking with unittest.mock and pytest-mock

**Isolate code from external dependencies:**
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_user(self, user_id: int) -> dict:
        response = requests.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()

def test_get_user_success():
    """Test with mock response."""
    client = APIClient("https://api.example.com")

    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "John"}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        user = client.get_user(1)

        assert user["id"] == 1
        mock_get.assert_called_once_with("https://api.example.com/users/1")

def test_get_user_error():
    """Test error handling."""
    client = APIClient("https://api.example.com")

    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    with patch("requests.get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            client.get_user(999)

# Using pytest-mock plugin
def test_with_mocker(mocker):
    """Using pytest-mock fixture."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"id": 2}
    mock_get.return_value.raise_for_status.return_value = None

    client = APIClient("https://api.example.com")
    result = client.get_user(2)

    assert result["id"] == 2
```

**Mock types:**
- `Mock`: Basic mock object
- `MagicMock`: Mock with magic methods
- `patch()`: Replace objects temporarily
- `side_effect`: Simulate exceptions or sequences

### 5. Test Organization and Structure

**Organize tests for maintainability:**
```
project/
├── src/
│   ├── __init__.py
│   ├── models.py
│   └── services.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/                # Fast, isolated tests
│   │   ├── test_models.py
│   │   └── test_utils.py
│   ├── integration/         # Component interaction
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/                 # End-to-end tests
│       └── test_workflows.py
└── pytest.ini               # Configuration
```

**conftest.py for shared fixtures:**
```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def database_url():
    """Provide test database URL."""
    return "postgresql://localhost/test_db"

@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }

@pytest.fixture(autouse=True)
def reset_state():
    """Auto-run cleanup before each test."""
    # Setup
    yield
    # Teardown
    pass
```

## Advanced Patterns

### 6. Testing Async Code

**Test coroutines and async operations:**
```python
import pytest
import asyncio

async def fetch_data(url: str) -> dict:
    await asyncio.sleep(0.1)
    return {"url": url, "data": "result"}

@pytest.mark.asyncio
async def test_fetch_data():
    """Test async function."""
    result = await fetch_data("https://api.example.com")
    assert result["url"] == "https://api.example.com"

@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple async operations."""
    urls = ["url1", "url2", "url3"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    assert all("data" in r for r in results)

@pytest.fixture
async def async_client():
    """Async fixture."""
    client = {"connected": True}
    yield client
    client["connected"] = False
```

**Requirements:**
- Install `pytest-asyncio`
- Mark async tests with `@pytest.mark.asyncio`
- Use `async def` for test functions and fixtures

### 7. Property-Based Testing with Hypothesis

**Generate test cases automatically:**
```python
from hypothesis import given, strategies as st
import pytest

def reverse_string(s: str) -> str:
    return s[::-1]

@given(st.text())
def test_reverse_twice_returns_original(s):
    """Property: double reverse equals original."""
    assert reverse_string(reverse_string(s)) == s

@given(st.text())
def test_reverse_preserves_length(s):
    """Property: length unchanged by reverse."""
    assert len(reverse_string(s)) == len(s)

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Property: a + b = b + a."""
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_sorted_list_is_ordered(lst):
    """Property: sorted list is non-decreasing."""
    sorted_lst = sorted(lst)

    # Same length
    assert len(sorted_lst) == len(lst)

    # Is ordered
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
```

**Use cases:**
- Test universal properties
- Find edge cases automatically
- Validate invariants
- Complement example-based tests

### 8. Monkeypatch for Testing

**Modify environment and attributes safely:**
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

class Config:
    debug = False

def test_monkeypatch_attribute(monkeypatch):
    """Modify object attributes."""
    config = Config()
    monkeypatch.setattr(config, "debug", True)
    assert config.debug is True
```

**Common uses:**
- Environment variables
- System attributes
- Module-level constants
- Time/datetime mocking

### 9. Temporary Files and Directories

**Test file operations safely:**
```python
import pytest
from pathlib import Path

def save_data(filepath: Path, data: str):
    filepath.write_text(data)

def load_data(filepath: Path) -> str:
    return filepath.read_text()

def test_file_operations(tmp_path):
    """Test with temporary directory."""
    test_file = tmp_path / "data.txt"

    save_data(test_file, "Hello, World!")

    assert test_file.exists()
    assert load_data(test_file) == "Hello, World!"

def test_multiple_files(tmp_path):
    """Test with multiple temporary files."""
    files = {
        "file1.txt": "Content 1",
        "file2.txt": "Content 2",
    }

    for filename, content in files.items():
        save_data(tmp_path / filename, content)

    assert len(list(tmp_path.iterdir())) == 2
```

**Fixtures:**
- `tmp_path`: Unique temporary directory per test
- `tmp_path_factory`: Create multiple temp directories
- Automatic cleanup after test completion

### 10. Test Markers and Selection

**Organize and run specific test groups:**
```python
import pytest
import os

@pytest.mark.slow
def test_slow_operation():
    """Mark as slow test."""
    import time
    time.sleep(2)

@pytest.mark.integration
def test_database_integration():
    """Mark as integration test."""
    pass

@pytest.mark.unit
def test_pure_function():
    """Mark as unit test."""
    pass

@pytest.mark.skip(reason="Feature not implemented")
def test_future_feature():
    """Skip test temporarily."""
    pass

@pytest.mark.skipif(os.name == "nt", reason="Unix only")
def test_unix_specific():
    """Conditional skip."""
    pass

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    """Mark expected failure."""
    assert False
```

**Run specific markers:**
```bash
pytest -m slow              # Run only slow tests
pytest -m "not slow"        # Skip slow tests
pytest -m "unit and not slow"  # Combine markers
```

## Coverage and Quality Metrics

### Coverage Configuration

**pytest.ini configuration:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
markers =
    slow: marks slow tests
    integration: marks integration tests
    unit: marks unit tests
    smoke: marks smoke tests
```

**Run with coverage:**
```bash
# Basic coverage
pytest --cov=src tests/

# HTML report
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# Show missing lines
pytest --cov=src --cov-report=term-missing tests/

# Fail if below threshold
pytest --cov=src --cov-fail-under=80 tests/
```

### Integration Testing Patterns

**Testing database operations:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    """Provide clean database session per test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()

def test_user_creation(db_session):
    """Test creating user in database."""
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None

    # Query to verify
    retrieved = db_session.query(User).filter_by(email="test@example.com").first()
    assert retrieved.name == "Test"
```

**Testing API endpoints:**
```python
import pytest
from fastapi.testclient import TestClient
from myapp import app

@pytest.fixture
def client():
    """Provide test client."""
    return TestClient(app)

def test_get_user(client):
    """Test GET /users/{id} endpoint."""
    response = client.get("/users/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_create_user(client):
    """Test POST /users endpoint."""
    user_data = {"name": "New User", "email": "new@example.com"}
    response = client.post("/users", json=user_data)

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
```

## Best Practices Summary

### Test Quality
1. **One concept per test**: Test single behavior per test function
2. **Descriptive names**: Use `test_<behavior>_<condition>_<expected>` pattern
3. **AAA pattern**: Arrange (setup), Act (execute), Assert (verify)
4. **Independence**: Tests should not depend on each other
5. **Deterministic**: Same input always produces same result

### Fixture Design
6. **Appropriate scope**: Use narrowest scope needed
7. **Composition**: Build complex fixtures from simple ones
8. **Cleanup**: Always clean up resources in teardown
9. **Reusability**: Share common fixtures in conftest.py
10. **Naming**: Clear, descriptive fixture names

### Mocking Strategy
11. **Mock boundaries**: Mock at system boundaries (APIs, databases)
12. **Don't over-mock**: Test real code when possible
13. **Verify interactions**: Use `assert_called_with()` to verify
14. **Reset mocks**: Ensure clean state between tests
15. **Mock return values**: Always define expected return values

### Organization
16. **Parallel structure**: Mirror source code organization
17. **Test categorization**: Use markers (unit, integration, e2e)
18. **Configuration**: Use pytest.ini or pyproject.toml
19. **Separate concerns**: Unit tests separate from integration tests
20. **Fast by default**: Run fast tests frequently, slow tests less often

### Coverage
21. **Measure coverage**: Track which code is tested
22. **Quality over quantity**: 100% coverage doesn't mean bug-free
23. **Focus on critical paths**: Prioritize important code paths
24. **Test edge cases**: Boundary conditions, error cases
25. **Continuous monitoring**: Track coverage in CI/CD

## Resources

- **pytest documentation**: https://docs.pytest.org/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **pytest-mock**: pytest wrapper for unittest.mock
- **pytest-asyncio**: Testing async code
- **pytest-cov**: Coverage reporting plugin
- **Hypothesis**: Property-based testing framework
- **pytest-xdist**: Run tests in parallel
- **tox**: Test across multiple Python versions
- **coverage.py**: Coverage measurement tool
