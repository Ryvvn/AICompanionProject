
import httpx

from bananalyzer.integrations.screenpipe import ScreenpipeAdapter


def test_health_check_success(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    adapter = ScreenpipeAdapter()

    result = adapter.health_check()

    assert result.available is True
    assert result.status == "available"
    assert result.degraded_mode is False


def test_health_check_http_failure(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")

    adapter = ScreenpipeAdapter()

    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "Connection refused" in result.last_error


def test_health_check_timeout(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.TimeoutException("Request timed out")

    adapter = ScreenpipeAdapter()

    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "timed out" in result.last_error.lower()


def test_health_check_non_200_status(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    adapter = ScreenpipeAdapter()

    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "500" in result.last_error


def test_get_recent_context_success(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "ocr_text": "some text content",
        "app_name": "chrome.exe",
        "window_title": "Twitter",
        "browser_url": "https://twitter.com",
    }
    mock_get.return_value = mock_response

    adapter = ScreenpipeAdapter()
    result = adapter.get_recent_context()

    assert result["ok"] is True
    assert result["signals"] is not None
    assert "app_name" in result["signals"] or "app_name" in str(result["signals"])
    assert "ocr_text" not in str(result["signals"])


def test_get_recent_context_connection_error(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")

    adapter = ScreenpipeAdapter()
    result = adapter.get_recent_context()

    assert result["ok"] is False
    assert result["signals"] is None
    assert result["error"] is not None
    assert "Connection refused" in result["error"].get("message", "")


def test_get_recent_context_timeout(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.TimeoutException("Request timed out")

    adapter = ScreenpipeAdapter()
    result = adapter.get_recent_context()

    assert result["ok"] is False
    assert result["signals"] is None
    assert result["error"] is not None
    assert result["error"].get("recoverable") is True


def test_get_recent_context_invalid_json(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    adapter = ScreenpipeAdapter()
    result = adapter.get_recent_context()

    assert result["ok"] is False
    assert result["signals"] is None
    assert result["error"] is not None
    assert result["error"].get("recoverable") is True


def test_health_check_does_not_raise_on_unhandled_exception(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = RuntimeError("Unexpected failure")

    adapter = ScreenpipeAdapter()

    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert "Unexpected failure" in result.last_error
