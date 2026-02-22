import pytest
from unittest.mock import patch, MagicMock
from claude_ctx_py.tui_overview_enhanced import EnhancedOverview

@patch("psutil.virtual_memory")
@patch("psutil.cpu_percent")
@patch("psutil.disk_usage")
@patch("os.getcwd")
def test_create_system_health(mock_getcwd, mock_disk_usage, mock_cpu_percent, mock_virtual_memory):
    # Mock psutil responses
    mock_mem = MagicMock()
    mock_mem.percent = 45.0
    mock_virtual_memory.return_value = mock_mem
    
    mock_cpu_percent.return_value = 12.5
    
    mock_disk = MagicMock()
    mock_disk.percent = 60.0
    mock_disk_usage.return_value = mock_disk
    
    mock_getcwd.return_value = "/tmp"
    
    health = EnhancedOverview.create_system_health()
    
    assert "Memory: 45.0%" in health
    assert "CPU Load: 12.5%" in health
    assert "Disk: 60.0%" in health
    assert "Metrics unavailable" not in health

@patch("psutil.virtual_memory")
def test_create_system_health_failure(mock_virtual_memory):
    # Mock psutil failure
    mock_virtual_memory.side_effect = Exception("Failed")
    
    health = EnhancedOverview.create_system_health()
    
    assert "Metrics unavailable" in health
