# Integration Testing Patterns

## Database Testing

**Testing with SQLAlchemy:**
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User

@pytest.fixture(scope="function")
def db_session():
    """Provide clean database session per test."""
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()

@pytest.fixture(scope="function")
def db_session_with_rollback(database_engine):
    """Session with automatic rollback."""
    connection = database_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_user_creation(db_session):
    """Test creating user in database."""
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None

    # Query to verify
    retrieved = db_session.query(User).filter_by(email="test@example.com").first()
    assert retrieved.name == "Test User"

def test_user_query(db_session):
    """Test querying users."""
    # Insert test data
    users = [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
    ]
    db_session.add_all(users)
    db_session.commit()

    # Query
    results = db_session.query(User).all()
    assert len(results) == 2

def test_user_update(db_session):
    """Test updating user."""
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()

    user.name = "Updated"
    db_session.commit()

    retrieved = db_session.query(User).filter_by(id=user.id).first()
    assert retrieved.name == "Updated"
```

## API Endpoint Testing

### FastAPI
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

    data = response.json()
    assert "id" in data
    assert "name" in data

def test_create_user(client):
    """Test POST /users endpoint."""
    user_data = {
        "name": "New User",
        "email": "new@example.com"
    }
    response = client.post("/users", json=user_data)

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"

def test_authentication_required(client):
    """Test endpoint requires authentication."""
    response = client.get("/protected")
    assert response.status_code == 401

def test_with_authentication(client):
    """Test authenticated request."""
    headers = {"Authorization": "Bearer test-token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
```

### Flask
```python
import pytest
from myapp import create_app

@pytest.fixture
def app():
    """Create test app."""
    app = create_app(testing=True)
    yield app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

def test_index_page(client):
    """Test index page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_post_data(client):
    """Test POST request."""
    response = client.post("/api/data", json={"key": "value"})
    assert response.status_code == 200
    assert response.json["key"] == "value"
```

## Redis Testing

**Testing with Redis:**
```python
import pytest
import redis
from fakeredis import FakeRedis

@pytest.fixture
def redis_client():
    """Provide fake Redis client for testing."""
    client = FakeRedis()
    yield client
    client.flushall()

def test_set_get(redis_client):
    """Test Redis set and get."""
    redis_client.set("key", "value")
    assert redis_client.get("key") == b"value"

def test_expiration(redis_client):
    """Test key expiration."""
    redis_client.setex("key", 1, "value")
    assert redis_client.get("key") == b"value"

    # Wait for expiration
    import time
    time.sleep(2)
    assert redis_client.get("key") is None
```

## Message Queue Testing

**Testing with Celery:**
```python
import pytest
from celery import Celery

@pytest.fixture
def celery_app():
    """Create Celery app for testing."""
    app = Celery(broker="memory://", backend="cache+memory://")
    app.conf.task_always_eager = True  # Run tasks synchronously
    return app

def test_task_execution(celery_app):
    """Test Celery task."""
    @celery_app.task
    def add(x, y):
        return x + y

    result = add.delay(2, 3)
    assert result.get() == 5
```

## External Service Mocking

**Testing with httpx:**
```python
import pytest
import httpx
from respx import MockRouter

@pytest.fixture
def mock_api():
    """Mock external API."""
    with MockRouter() as router:
        router.get("https://api.example.com/users/1").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Test User"}
            )
        )
        yield router

def test_external_api_call(mock_api):
    """Test calling external API."""
    response = httpx.get("https://api.example.com/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

## File System Testing

**Testing file operations:**
```python
import pytest
from pathlib import Path

def test_file_creation(tmp_path):
    """Test creating and reading files."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")

    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"

def test_directory_operations(tmp_path):
    """Test directory operations."""
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    (subdir / "file1.txt").write_text("Content 1")
    (subdir / "file2.txt").write_text("Content 2")

    files = list(subdir.iterdir())
    assert len(files) == 2
```

## Docker Test Containers

**Testing with testcontainers:**
```python
import pytest
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="module")
def postgres_container():
    """Provide PostgreSQL container."""
    with PostgresContainer("postgres:14") as postgres:
        yield postgres

def test_with_postgres(postgres_container):
    """Test with real PostgreSQL."""
    import psycopg2

    conn = psycopg2.connect(postgres_container.get_connection_url())
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR)")
    cursor.execute("INSERT INTO users (name) VALUES ('Test')")
    conn.commit()

    cursor.execute("SELECT name FROM users")
    result = cursor.fetchone()
    assert result[0] == "Test"

    conn.close()
```

## Environment Setup

**Testing with different configurations:**
```python
import pytest
import os

@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setenv("DEBUG", "True")

def test_with_test_env(test_env):
    """Test with test environment."""
    assert os.getenv("DATABASE_URL") == "postgresql://localhost/test"
    assert os.getenv("DEBUG") == "True"
```

## Best Practices

1. **Isolate tests**: Each test should have clean state
2. **Use transactions**: Rollback database changes after tests
3. **Mock external services**: Don't hit real APIs in tests
4. **Test containers**: Use Docker for real dependencies
5. **Seed data**: Provide consistent test data
6. **Fast setup**: Optimize fixture creation time
7. **Parallel execution**: Tests should be independent
8. **Clean teardown**: Always clean up resources
9. **Realistic data**: Use data similar to production
10. **Test error cases**: Network failures, timeouts, etc.
