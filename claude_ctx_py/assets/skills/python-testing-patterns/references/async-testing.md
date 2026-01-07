# Testing Async Code

## Basic Async Tests

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
```

## Setup

**Install pytest-asyncio:**
```bash
pip install pytest-asyncio
```

**Configure in pytest.ini:**
```ini
[pytest]
asyncio_mode = auto
```

## Concurrent Operations

**Test multiple async operations:**
```python
@pytest.mark.asyncio
async def test_concurrent_operations():
    """Test multiple async operations."""
    urls = ["url1", "url2", "url3"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    assert all("data" in r for r in results)
```

## Async Fixtures

**Create async fixtures:**
```python
@pytest.fixture
async def async_client():
    """Async fixture with setup and teardown."""
    client = {"connected": False}

    # Setup
    client["connected"] = True

    yield client

    # Teardown
    client["connected"] = False

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    """Use async fixture."""
    assert async_client["connected"] is True
```

## Testing Timeouts

**Verify timeout behavior:**
```python
@pytest.mark.asyncio
async def test_timeout():
    """Test operation with timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(long_running_task(), timeout=0.1)
```

## Testing Exception Handling

**Async exceptions:**
```python
async def failing_operation():
    await asyncio.sleep(0.1)
    raise ValueError("Async error")

@pytest.mark.asyncio
async def test_async_exception():
    """Test async exception handling."""
    with pytest.raises(ValueError, match="Async error"):
        await failing_operation()
```

## Mocking Async Functions

**Mock async calls:**
```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_with_async_mock(mocker):
    """Mock async function."""
    mock_fetch = AsyncMock(return_value={"data": "mocked"})
    mocker.patch("module.fetch_data", mock_fetch)

    result = await module.fetch_data("url")
    assert result["data"] == "mocked"
    mock_fetch.assert_awaited_once_with("url")
```

## Event Loop Management

**Custom event loop:**
```python
@pytest.fixture
def event_loop():
    """Create custom event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

## Testing Async Context Managers

```python
class AsyncResource:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def cleanup(self):
        pass

@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context manager."""
    async with AsyncResource() as resource:
        assert resource is not None
```

## Best Practices

1. **Use pytest-asyncio**: Don't write manual event loop code
2. **Mark tests**: Always use `@pytest.mark.asyncio`
3. **Async all the way**: Don't mix sync/async in fixtures
4. **Test concurrency**: Verify parallel behavior explicitly
5. **Timeout protection**: Add timeouts to prevent hanging tests
6. **AsyncMock**: Use for mocking async functions
7. **Clean event loops**: Ensure proper cleanup
