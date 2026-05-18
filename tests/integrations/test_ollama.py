import json

import httpx

from bananalyzer.integrations.ollama import OllamaAdapter
from bananalyzer.integrations.base import AdapterResult, HealthCheckResult


def test_generate_success(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"model": "llama3.2", "response": "Hello, Ryan!", "done": true}'
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("Hi there", system="Be helpful", model="llama3.2")

    assert result.ok is True
    assert result.data == "Hello, Ryan!"
    assert result.error is None


def test_generate_success_ndjson(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = (
        '{"model": "llama3.2", "response": "Hello", "done": false}\n'
        '{"model": "llama3.2", "response": ", Ryan!", "done": true}\n'
    )
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("Hi there", system="Be helpful", model="llama3.2")

    assert result.ok is True
    assert result.data == "Hello, Ryan!"


def test_generate_passes_options_in_body(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"model": "llama3.2", "response": "ok", "done": true}'
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate(
        "test prompt",
        system="sys",
        model="llama3.2",
        options={"temperature": 0.3, "num_ctx": 4096},
    )

    assert result.ok is True
    call_args = mock_post.call_args
    assert call_args is not None
    url_arg = call_args[0][0] if call_args[0] else call_args[1].get("url")
    assert "/api/generate" in str(url_arg)
    body = call_args[1]["json"]
    assert body["model"] == "llama3.2"
    assert body["prompt"] == "test prompt"
    assert body["system"] == "sys"
    assert body["stream"] is False
    assert body["options"] == {"temperature": 0.3, "num_ctx": 4096}


def test_generate_no_options_in_body_when_none(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = '{"model": "llama3.2", "response": "ok", "done": true}'
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", system="sys", model="llama3.2", options=None)

    assert result.ok is True
    body = mock_post.call_args[1]["json"]
    assert "options" not in body


def test_generate_connection_refused(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_post.side_effect = httpx.RequestError("Connection refused")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_request_error"
    assert "Connection refused" in result.error["message"]


def test_generate_timeout(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_post.side_effect = httpx.ReadTimeout("Request timed out")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_timeout"
    assert "timed out" in result.error["message"]


def test_generate_http_500(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("not json")
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_http_error"
    assert "500" in result.error["message"]


def test_generate_model_not_found(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "model 'unknown-model' not found"}
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="unknown-model")

    assert result.ok is False
    assert result.error is not None
    assert "not found" in result.error["message"].lower()
    assert "ollama pull unknown-model" in result.error["message"]


def test_health_check_success(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check()

    assert result.available is True
    assert result.status == "available"
    assert result.degraded_mode is False


def test_health_check_connection_refused(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "Connection refused" in result.last_error


def test_health_check_non_200_status(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert result.degraded_mode is True
    assert "500" in result.last_error


def test_health_check_model_not_found(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.2:latest"},
            {"name": "mistral:7b"},
        ]
    }
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check(model="phi3")

    assert result.available is False
    assert result.status == "degraded"
    assert result.degraded_mode is True
    assert "Model 'phi3' not found" in result.last_error
    assert "ollama pull phi3" in result.last_error


def test_health_check_model_found(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.2:latest"},
            {"name": "mistral:7b"},
        ]
    }
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check(model="llama3.2")

    assert result.available is True
    assert result.status == "available"
    assert result.degraded_mode is False


def test_is_available_returns_true(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    assert adapter.is_available() is True


def test_is_available_returns_false(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = httpx.RequestError("Connection refused")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    assert adapter.is_available() is False


def test_config_defaults_used(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    adapter = OllamaAdapter()

    assert adapter.base_url == "http://localhost:11434"
    assert adapter._timeout_seconds == 120


def test_custom_base_url_overrides_default(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://custom:9999")

    assert adapter.base_url == "http://custom:9999"


def test_health_check_does_not_raise_on_unhandled_exception(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_get.side_effect = RuntimeError("Unexpected failure")

    adapter = OllamaAdapter(base_url="http://localhost:11434")

    result = adapter.health_check()

    assert result.available is False
    assert result.status == "unavailable"
    assert "Unexpected failure" in result.last_error


def test_generate_connect_error(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_post.side_effect = httpx.ConnectError("Connection refused")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_unreachable"
    assert "ollama serve" in result.error["message"]


def test_generate_read_timeout(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_post.side_effect = httpx.ReadTimeout("Read timed out")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    adapter._timeout_seconds = 60
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_timeout"
    assert "60s" in result.error["message"]


def test_generate_json_decode_error(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "not valid json {{{"
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_post.return_value = mock_response

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_invalid_response"


def test_generate_unknown_exception(mocker):
    mock_post = mocker.patch("httpx.Client.post")
    mock_post.side_effect = ValueError("Something unexpected")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.generate("test", model="llama3.2")

    assert result.ok is False
    assert result.error is not None
    assert result.error["code"] == "ollama_unknown_error"
    assert "Something unexpected" in result.error["message"]


def test_health_check_calls_upsert_integration_health(mocker):
    mock_get = mocker.patch("httpx.Client.get")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    mock_upsert = mocker.patch.object(OllamaAdapter, "_upsert_health")

    adapter = OllamaAdapter(base_url="http://localhost:11434")
    result = adapter.health_check()

    assert result.available is True
    assert mock_upsert.called
    call_args = mock_upsert.call_args[0]
    assert call_args[0].available is True
