"""Pytest configuration and shared fixtures for claude-cortex tests.

This module provides:
- Shared fixtures for common test scenarios
- Test configuration and markers
- Temporary directories and file fixtures
- Mock/stub objects for testing
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests.

    Yields:
        A temporary directory that is automatically cleaned up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_dir(temp_dir: Path) -> Path:
    """Provide a temporary config directory structure.

    Creates a directory with the structure:
    - .claude/
      - settings.json
      - agents/
      - skills/
      - rules/

    Args:
        temp_dir: The temporary directory to use as base.

    Returns:
        Path to the .claude directory.
    """
    claude_dir = temp_dir / ".claude"
    claude_dir.mkdir()

    # Create subdirectories
    (claude_dir / "agents").mkdir()
    (claude_dir / "skills").mkdir()
    (claude_dir / "rules").mkdir()

    # Create empty settings.json
    (claude_dir / "settings.json").write_text("{}")

    return claude_dir


@pytest.fixture
def cortex_root_dir(temp_dir: Path) -> Path:
    """Provide a temporary CORTEX_ROOT directory structure.

    Creates a directory with bundled assets:
    - agents/
    - skills/
    - rules/
    - hooks/

    Args:
        temp_dir: The temporary directory to use as base.

    Returns:
        Path to the mock CORTEX_ROOT directory.
    """
    cortex_root = temp_dir / "cortex_root"
    cortex_root.mkdir()

    # Create bundled asset directories
    (cortex_root / "agents").mkdir()
    (cortex_root / "skills").mkdir()
    (cortex_root / "rules").mkdir()
    (cortex_root / "hooks").mkdir()

    return cortex_root


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "fast: mark test as fast (< 1 second) [fast]"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (> 1 second) [slow]"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test [unit]"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test [integration]"
    )
    config.addinivalue_line(
        "markers", "tui: mark test as testing TUI components [tui]"
    )
    config.addinivalue_line(
        "markers", "cli: mark test as testing CLI interface [cli]"
    )
