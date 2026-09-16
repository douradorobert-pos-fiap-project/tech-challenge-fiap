import json

from src.infrastructure.observability.logging import JsonFormatter


def test_health_returns_correlation_id(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]


def test_received_correlation_id_is_preserved(client):
    response = client.get(
        "/health", headers={"X-Correlation-ID": "test-correlation-123"}
    )
    assert response.headers["X-Correlation-ID"] == "test-correlation-123"


def test_json_formatter_contains_request_context():
    record = __import__("logging").LogRecord(
        "test", __import__("logging").INFO, __file__, 1, "message", (), None
    )
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "INFO"
    assert payload["message"] == "message"
    assert "timestamp" in payload
