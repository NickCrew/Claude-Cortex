import pytest
from unittest.mock import patch, MagicMock
from claude_ctx_py.tui_overview_enhanced import EnhancedOverview

@patch("claude_ctx_py.tui_overview_enhanced.psutil")
@patch("claude_ctx_py.tui_overview_enhanced.os")
def test_create_system_health(mock_os, mock_psutil):
    # Mock psutil responses
    mock_mem = MagicMock()
    mock_mem.percent = 45.0
    mock_psutil.virtual_memory.return_value = mock_mem
    
    mock_psutil.cpu_percent.return_value = 12.5
    
    mock_disk = MagicMock()
    mock_disk.percent = 60.0
    mock_psutil.disk_usage.return_value = mock_disk
    
    mock_os.getcwd.return_value = "/tmp"
    
    health = EnhancedOverview.create_system_health()
    
    assert "Memory: 45.0%" in health
    assert "CPU Load: 12.5%" in health
    assert "Disk: 60.0%" in health
    assert "Metrics unavailable" not in health

@patch("claude_ctx_py.tui_overview_enhanced.psutil")
def test_create_system_health_failure(mock_psutil):
    # Mock psutil failure
    mock_psutil.virtual_memory.side_effect = Exception("Failed")
    
    health = EnhancedOverview.create_system_health()
    
    assert "Metrics unavailable" in health
