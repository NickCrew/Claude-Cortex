# Testing Best Practices

## Test Quality Principles

### 1. One Concept Per Test
**Each test should verify a single behavior:**
```python
# Good: Tests one concept
def test_user_creation_sets_default_role():
    user = User(name="Test")
    assert user.role == "user"

def test_user_creation_generates_unique_id():
    user = User(name="Test")
    assert user.id is not None

# Bad: Tests multiple concepts
def test_user_creation():
    user = User(name="Test")
    assert user.role == "user"  # Concept 1
    assert user.id is not None  # Concept 2
    assert user.created_at is not None  # Concept 3
```

### 2. Descriptive Test Names
**Use pattern: `test_<behavior>_<condition>_<expected>`:**
```python
# Good: Clear what is being tested
def test_email_validation_with_invalid_format_returns_false():
    assert not is_valid_email("invalid")

def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError):
        divide(5, 0)

def test_user_creation_with_duplicate_email_raises_integrity_error():
    create_user("test@example.com")
    with pytest.raises(IntegrityError):
        create_user("test@example.com")

# Bad: Unclear purpose
def test_email():
    assert not is_valid_email("invalid")

def test_divide():
    with pytest.raises(ValueError):
        divide(5, 0)
```

### 3. AAA Pattern (Arrange-Act-Assert)
**Structure tests consistently:**
```python
def test_user_registration_sends_welcome_email():
    # Arrange
    user_data = {"email": "test@example.com", "name": "Test"}
    mock_email = Mock()

    # Act
    user = register_user(user_data, email_service=mock_email)

    # Assert
    assert user.email == "test@example.com"
    mock_email.send_welcome.assert_called_once_with(user)
```

### 4. Test Independence
**Tests should not depend on each other:**
```python
# Good: Each test is independent
def test_create_user():
    user = User(name="Test")
    assert user.name == "Test"

def test_update_user():
    user = User(name="Original")
    user.name = "Updated"
    assert user.name == "Updated"

# Bad: Tests depend on order
test_user = None

def test_create_user_step1():
    global test_user
    test_user = User(name="Test")  # Modifies global state

def test_update_user_step2():
    global test_user
    test_user.name = "Updated"  # Depends on step1
```

### 5. Deterministic Tests
**Same input always produces same result:**
```python
# Good: Deterministic
def test_addition():
    assert add(2, 3) == 5  # Always true

# Bad: Non-deterministic
def test_random_generation():
    import random
    value = random.randint(1, 10)
    assert value > 0  # Could fail randomly

# Fix: Control randomness
def test_random_generation_fixed():
    import random
    random.seed(42)  # Fixed seed
    value = random.randint(1, 10)
    assert value == 2  # Deterministic
```

## Fixture Design

### 6. Appropriate Scope
**Use narrowest scope needed:**
```python
# Function scope: Clean state per test (default)
@pytest.fixture
def user():
    return User(name="Test")

# Module scope: Expensive setup
@pytest.fixture(scope="module")
def database_connection():
    conn = create_connection()
    yield conn
    conn.close()

# Session scope: Once per test run
@pytest.fixture(scope="session")
def app_config():
    return load_config()
```

### 7. Fixture Composition
**Build complex fixtures from simple ones:**
```python
@pytest.fixture
def database_url():
    return "postgresql://localhost/test"

@pytest.fixture
def database_engine(database_url):
    return create_engine(database_url)

@pytest.fixture
def database_session(database_engine):
    Session = sessionmaker(bind=database_engine)
    session = Session()
    yield session
    session.close()
```

### 8. Resource Cleanup
**Always clean up in teardown:**
```python
@pytest.fixture
def temp_file():
    # Setup
    file = Path("temp.txt")
    file.write_text("test")

    yield file

    # Teardown - always runs
    if file.exists():
        file.unlink()
```

### 9. Fixture Reusability
**Share common fixtures in conftest.py:**
```python
# tests/conftest.py
@pytest.fixture
def sample_user():
    """Available to all tests."""
    return User(name="Test", email="test@example.com")

@pytest.fixture
def authenticated_client(client, sample_user):
    """Client with authentication."""
    token = create_token(sample_user)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
```

### 10. Clear Fixture Names
**Descriptive names explain purpose:**
```python
# Good: Clear purpose
@pytest.fixture
def user_with_admin_role():
    return User(name="Admin", role="admin")

@pytest.fixture
def database_session_with_rollback():
    # ...

# Bad: Unclear purpose
@pytest.fixture
def u():
    return User(name="Admin")

@pytest.fixture
def db():
    # What kind of db? What state?
```

## Mocking Strategy

### 11. Mock at Boundaries
**Mock external systems, test internal logic:**
```python
# Good: Mock external API
def test_fetch_user_data():
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"id": 1}
        result = fetch_user_data(1)
        assert result["id"] == 1

# Bad: Over-mocking
def test_process_user():
    with patch("module.User") as MockUser:  # Don't mock own code
        with patch("module.validate") as mock_validate:
            # Too much mocking
```

### 12. Don't Over-Mock
**Test real code when possible:**
```python
# Good: Test real implementation
def test_calculate_total():
    items = [{"price": 10}, {"price": 20}]
    assert calculate_total(items) == 30

# Bad: Mock everything
def test_calculate_total_with_mocks():
    mock_items = Mock()
    mock_items.return_value = 30  # Why test a mock?
```

### 13. Verify Interactions
**Assert mocks were called correctly:**
```python
def test_user_creation_sends_email():
    mock_email = Mock()

    create_user("test@example.com", email_service=mock_email)

    # Verify
    mock_email.send_welcome.assert_called_once()
    mock_email.send_welcome.assert_called_with(
        email="test@example.com"
    )
```

### 14. Reset Mocks
**Ensure clean state between tests:**
```python
@pytest.fixture
def mock_service():
    mock = Mock()
    yield mock
    mock.reset_mock()  # Clean up
```

### 15. Define Return Values
**Always specify expected returns:**
```python
# Good: Clear return value
mock_api = Mock()
mock_api.get_user.return_value = {"id": 1, "name": "Test"}

# Bad: Undefined return
mock_api = Mock()
result = mock_api.get_user()  # Returns Mock, not dict
```

## Test Organization

### 16. Parallel Structure
**Mirror source code organization:**
```
src/
├── models.py
├── services.py
└── utils.py

tests/
├── test_models.py
├── test_services.py
└── test_utils.py
```

### 17. Test Categorization
**Use markers for organization:**
```python
@pytest.mark.unit
def test_pure_function():
    pass

@pytest.mark.integration
@pytest.mark.database
def test_database_operation():
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_workflow():
    pass
```

### 18. Configuration Management
**Centralize test configuration:**
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### 19. Separate Concerns
**Different directories for different test types:**
```
tests/
├── unit/           # Fast, isolated
├── integration/    # Component interaction
└── e2e/           # Full workflows
```

### 20. Fast by Default
**Optimize for quick feedback:**
```bash
# Quick run: unit tests only
pytest tests/unit/

# Full run: all tests
pytest

# Slow tests: run less frequently
pytest -m slow
```

## Coverage Philosophy

### 21. Measure Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### 22. Quality Over Quantity
**100% coverage ≠ bug-free code**

Focus on:
- Critical business logic
- Edge cases and error handling
- Complex algorithms
- Security-sensitive code

### 23. Prioritize Critical Paths
**Test important code thoroughly:**
- User authentication
- Payment processing
- Data validation
- Security checks

### 24. Test Edge Cases
**Boundary conditions and errors:**
```python
def test_divide_edge_cases():
    # Normal case
    assert divide(10, 2) == 5

    # Edge: zero
    with pytest.raises(ValueError):
        divide(10, 0)

    # Edge: negative
    assert divide(-10, 2) == -5

    # Edge: float precision
    assert abs(divide(1, 3) - 0.333333) < 0.00001
```

### 25. Continuous Monitoring
**Track coverage in CI/CD:**
```yaml
# GitHub Actions
- name: Run tests with coverage
  run: pytest --cov=src --cov-fail-under=80
```
