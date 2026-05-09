import pytest
from datetime import datetime
import httpx
from bananalyzer.integrations.mcp import MCPAdapter

def test_mcp_health_check_success(mocker):
    # Arrange
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    adapter = MCPAdapter()
    
    # Act
    result = adapter.health_check()
    
    # Assert
    assert result.available is True
    assert result.status == "available"
    assert result.degraded_mode is False

def test_mcp_health_check_failure(mocker):
    # Arrange
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")
    
    adapter = MCPAdapter()
    
    # Act
    result = adapter.health_check()
    
    # Assert
    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "Connection refused" in result.last_error

def test_get_active_context_success(mocker):
    # Arrange
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "file": "src/main.py",
        "selection": "def foo():\n    pass"
    }
    mock_get.return_value = mock_response
    
    adapter = MCPAdapter()
    
    # Act
    result = adapter.get_active_context()
    
    # Assert
    assert result["ok"] is True
    assert result["data"] is not None
    assert result["data"]["file"] == "src/main.py"
    assert result["data"]["selection"] == "def foo():\n    pass"

def test_get_active_context_failure(mocker):
    # Arrange
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")
    
    adapter = MCPAdapter()
    
    # Act
    result = adapter.get_active_context()
    
    # Assert
    assert result["ok"] is False
    assert result["data"] is None
    assert result["error"] is not None
