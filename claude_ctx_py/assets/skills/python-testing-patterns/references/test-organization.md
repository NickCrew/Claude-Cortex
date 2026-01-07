# Test Organization and Structure

## Directory Structure

**Organize tests for maintainability:**
```
project/
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── unit/                # Fast, isolated tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/         # Component interaction
│   │   ├── __init__.py
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/                 # End-to-end tests
│       ├── __init__.py
│       └── test_workflows.py
├── pytest.ini               # Configuration
└── pyproject.toml          # Project config
```

## Test Levels

### Unit Tests
- **Purpose**: Test individual functions/classes in isolation
- **Speed**: Fast (<1ms per test)
- **Dependencies**: None (mocked)
- **Location**: `tests/unit/`

### Integration Tests
- **Purpose**: Test component interactions
- **Speed**: Medium (10-100ms per test)
- **Dependencies**: Real databases, APIs (local)
- **Location**: `tests/integration/`

### End-to-End Tests
- **Purpose**: Test complete user workflows
- **Speed**: Slow (100ms-1s+ per test)
- **Dependencies**: Full system stack
- **Location**: `tests/e2e/`

## conftest.py for Shared Fixtures

**tests/conftest.py - Available to all tests:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def database_url():
    """Provide test database URL."""
    return "postgresql://localhost/test_db"

@pytest.fixture(scope="session")
def database_engine(database_url):
    """Create database engine."""
    return create_engine(database_url)

@pytest.fixture
def database_session(database_engine):
    """Provide database session."""
    Session = sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

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

## Nested conftest.py

**tests/integration/conftest.py - Only for integration tests:**
```python
import pytest
from myapp import create_app

@pytest.fixture
def app():
    """Create test app instance."""
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()
```

## Test Markers

**Define in pytest.ini:**
```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (medium speed)
    e2e: End-to-end tests (slow)
    slow: Slow tests (skip for quick runs)
    smoke: Smoke tests (critical functionality)
    database: Tests requiring database
    api: Tests requiring external API
```

**Use in tests:**
```python
import pytest

@pytest.mark.unit
def test_pure_function():
    """Fast unit test."""
    assert add(2, 3) == 5

@pytest.mark.integration
@pytest.mark.database
def test_database_operation(database_session):
    """Integration test with database."""
    user = User(name="Test")
    database_session.add(user)
    database_session.commit()
    assert user.id is not None

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_workflow(client):
    """End-to-end workflow test."""
    # Complex multi-step test
    pass
```

## Test Naming Conventions

**Descriptive test names:**
```python
# Good: Clear what is being tested
def test_user_creation_with_valid_data():
    pass

def test_email_validation_rejects_invalid_format():
    pass

def test_api_returns_404_for_missing_user():
    pass

# Bad: Unclear purpose
def test_user():
    pass

def test_1():
    pass
```

## Test Classes

**Group related tests:**
```python
class TestUserModel:
    """Tests for User model."""

    def test_create_user(self):
        user = User(name="Test")
        assert user.name == "Test"

    def test_user_validation(self):
        with pytest.raises(ValueError):
            User(name="")

class TestUserService:
    """Tests for User service."""

    @pytest.fixture
    def service(self):
        return UserService()

    def test_get_user(self, service):
        user = service.get_user(1)
        assert user is not None
```

## Configuration Files

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
```

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

## Running Tests by Category

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run integration and e2e tests
pytest -m "integration or e2e"

# Run all except slow tests
pytest -m "not slow"

# Run specific directory
pytest tests/unit/

# Run specific file
pytest tests/unit/test_models.py

# Run specific test
pytest tests/unit/test_models.py::test_user_creation
```

## Best Practices

1. **Parallel structure**: Mirror source code organization
2. **Clear separation**: Unit/integration/e2e in separate directories
3. **Shared fixtures**: Use conftest.py for common setup
4. **Descriptive names**: Test names describe behavior
5. **Appropriate markers**: Tag tests for selective running
6. **Fast by default**: Unit tests run most frequently
7. **Isolated tests**: No dependencies between tests
8. **Clean setup/teardown**: Use fixtures for resource management
