# Parametrized Tests

## Basic Parametrization

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
```

## Custom Test IDs

**Make test output more readable:**
```python
@pytest.mark.parametrize("value,expected", [
    pytest.param(1, True, id="positive"),
    pytest.param(0, False, id="zero"),
    pytest.param(-1, False, id="negative"),
])
def test_is_positive(value, expected):
    assert (value > 0) == expected
```

**Output:**
```
test_file.py::test_is_positive[positive] PASSED
test_file.py::test_is_positive[zero] PASSED
test_file.py::test_is_positive[negative] PASSED
```

## Multiple Parameters

**Test with multiple parameter sets:**
```python
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

## Stacked Parametrization

**Generate combinations:**
```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_combinations(x, y):
    """Runs 6 times: (1,10), (1,20), (2,10), (2,20), (3,10), (3,20)"""
    assert x * y > 0
```

## Parametrize from Files

**Load test cases from external data:**
```python
import json
import pytest

def load_test_cases():
    with open("test_cases.json") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_test_cases())
def test_from_file(case):
    input_data = case["input"]
    expected = case["expected"]
    assert process(input_data) == expected
```

## Benefits

- **DRY principle**: Reduce test code duplication
- **Coverage**: Test edge cases systematically
- **Readability**: Clear input/output relationships
- **Maintainability**: Add new cases without new test functions
- **Debugging**: Failures show exact failing parameters
