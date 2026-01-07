# Pytest Fundamentals

## Basic Test Structure

**Simple test with pytest:**
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

## Key Concepts

- **Test discovery**: Files matching `test_*.py` or `*_test.py`
- **Test functions**: Start with `test_`
- **Assertions**: Use `assert` statements for verification
- **Exception testing**: `pytest.raises()` for exception testing
- **Running tests**: `pytest` or `pytest -v` for verbose output

## Command Line Options

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::test_addition

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run last failed tests
pytest --lf
```

## AAA Pattern

**Arrange, Act, Assert:**
```python
def test_user_creation():
    # Arrange
    username = "testuser"
    email = "test@example.com"

    # Act
    user = User(username=username, email=email)

    # Assert
    assert user.username == username
    assert user.email == email
```
