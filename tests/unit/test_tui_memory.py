import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from claude_ctx_py.tui_memory import MemoryScreen

@pytest.fixture
def mock_list_notes():
    with patch("claude_ctx_py.tui_memory.list_notes") as mock:
        yield mock

def test_memory_screen_load_notes(mock_list_notes):
    """Test that MemoryScreen loads notes into the table."""
    # Setup mock data
    mock_list_notes.return_value = [
        {
            "type": "knowledge",
            "title": "Test Note",
            "name": "test-note",
            "path": "/path/to/test-note.md",
            "modified": datetime(2024, 1, 1),
            "tags": ["test"]
        }
    ]

    screen = MemoryScreen()
    
    # Mock query_one to return a mock table/input
    mock_widget = MagicMock()
    screen.query_one = MagicMock(return_value=mock_widget)
    
    screen.load_notes()
    
    # Verify list_notes was called
    mock_list_notes.assert_called_once()
    
    # Verify table was cleared and populated
    mock_widget.clear.assert_called_with(columns=True)
    mock_widget.add_column.assert_called()
    mock_widget.add_row.assert_called()
    
    # Check if the row contains expected data
    args, kwargs = mock_widget.add_row.call_args
    # The first arg is type (styled), second is title, third is date
    assert "Test Note" in args
    assert "2024-01-01" in args
    assert kwargs["key"] == "/path/to/test-note.md"

def test_memory_screen_filter(mock_list_notes):
    """Test that load_notes filters results."""
    mock_list_notes.return_value = [
        {
            "type": "knowledge",
            "title": "Alpha",
            "name": "alpha",
            "path": "/a.md",
            "modified": datetime(2024, 1, 1),
            "tags": []
        },
        {
            "type": "knowledge",
            "title": "Beta",
            "name": "beta",
            "path": "/b.md",
            "modified": datetime(2024, 1, 1),
            "tags": []
        }
    ]

    screen = MemoryScreen()
    mock_widget = MagicMock()
    screen.query_one = MagicMock(return_value=mock_widget)

    # Filter for "Alpha"
    screen.load_notes(query="Alpha")
    
    # Should only add one row
    assert mock_widget.add_row.call_count == 1
    args, _ = mock_widget.add_row.call_args
    assert "Alpha" in args
