# Fixtures for Setup and Teardown

## Basic Fixtures

**Reusable test resources with cleanup:**
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
```

## Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default - per test function
def per_test_resource():
    return {"data": "fresh"}

@pytest.fixture(scope="class")  # Per test class
def per_class_resource():
    return {"shared": "class-level"}

@pytest.fixture(scope="module")  # Per test module
def per_module_resource():
    return {"shared": "module-level"}

@pytest.fixture(scope="session")  # Once per test session
def per_session_resource():
    return {"shared": "session-level"}
```

**Scope ordering**: `function` < `class` < `module` < `session`

## Fixture Composition

**Build complex fixtures from simple ones:**
```python
@pytest.fixture
def database_url():
    return "postgresql://localhost/test_db"

@pytest.fixture
def database_engine(database_url):
    """Depends on database_url fixture."""
    from sqlalchemy import create_engine
    return create_engine(database_url)

@pytest.fixture
def database_session(database_engine):
    """Depends on database_engine fixture."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.close()
```

## Autouse Fixtures

**Automatically run for every test:**
```python
@pytest.fixture(autouse=True)
def reset_state():
    """Auto-run cleanup before each test."""
    # Setup
    global_state.clear()
    yield
    # Teardown
    global_state.clear()
```

## Shared Fixtures in conftest.py

**tests/conftest.py:**
```python
import pytest

@pytest.fixture(scope="session")
def app_config():
    """Available to all tests."""
    return {
        "debug": True,
        "api_key": "test-key",
        "database": "sqlite:///:memory:"
    }

@pytest.fixture
def sample_user():
    """Sample user data for tests."""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com"
    }
```

## Parametrized Fixtures

**Generate multiple fixture instances:**
```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database_type(request):
    """Run tests with different database types."""
    return request.param

def test_with_all_databases(database_type):
    """This test runs 3 times, once per database."""
    assert database_type in ["sqlite", "postgres", "mysql"]
```
