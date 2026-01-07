# Mocking with unittest.mock and pytest-mock

## Basic Mocking

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
```

## Mock Types

### Mock
**Basic mock object:**
```python
mock = Mock()
mock.return_value = 42
assert mock() == 42

mock.method.return_value = "result"
assert mock.method() == "result"
```

### MagicMock
**Mock with magic methods:**
```python
mock = MagicMock()
mock.__len__.return_value = 5
assert len(mock) == 5

mock.__getitem__.return_value = "item"
assert mock[0] == "item"
```

## Patching

### Context Manager Patching
```python
with patch("module.function") as mock_func:
    mock_func.return_value = "mocked"
    result = module.function()
    assert result == "mocked"
```

### Decorator Patching
```python
@patch("module.function")
def test_something(mock_func):
    mock_func.return_value = "mocked"
    result = module.function()
    assert result == "mocked"
```

### Object Patching
```python
@patch.object(MyClass, "method")
def test_method(mock_method):
    mock_method.return_value = "mocked"
    obj = MyClass()
    assert obj.method() == "mocked"
```

## Side Effects

**Simulate exceptions or sequences:**
```python
# Raise exception
mock = Mock()
mock.side_effect = ValueError("Error message")
with pytest.raises(ValueError):
    mock()

# Return sequence
mock = Mock()
mock.side_effect = [1, 2, 3]
assert mock() == 1
assert mock() == 2
assert mock() == 3

# Custom function
def custom_behavior(x):
    return x * 2

mock = Mock()
mock.side_effect = custom_behavior
assert mock(5) == 10
```

## Assertions

**Verify mock interactions:**
```python
mock = Mock()
mock(1, 2, key="value")

# Called
assert mock.called
assert mock.call_count == 1

# Called with
mock.assert_called_once()
mock.assert_called_with(1, 2, key="value")
mock.assert_called_once_with(1, 2, key="value")

# Called with any args
mock.assert_called()

# Not called
mock_other = Mock()
mock_other.assert_not_called()
```

## pytest-mock Plugin

**Cleaner syntax with pytest:**
```python
def test_with_mocker(mocker):
    """Using pytest-mock fixture."""
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.json.return_value = {"id": 2}
    mock_get.return_value.raise_for_status.return_value = None

    client = APIClient("https://api.example.com")
    result = client.get_user(2)

    assert result["id"] == 2
```

**Benefits:**
- Automatic cleanup
- No context managers needed
- Integration with pytest fixtures
- Spy functionality

## Best Practices

1. **Mock at boundaries**: Mock external systems (APIs, databases, files)
2. **Don't over-mock**: Test real code when possible
3. **Verify interactions**: Use assertions to verify calls
4. **Clear return values**: Always define expected return values
5. **Reset between tests**: Ensure clean state
6. **Mock the interface**: Mock at the lowest dependency level
7. **Use spec**: `Mock(spec=ClassName)` prevents invalid attribute access
