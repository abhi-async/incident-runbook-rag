"""
Basic API tests using FastAPI TestClient (no real LLM calls needed).
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_empty_question():
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 400


@patch("app.api.query_runbooks")
def test_query_success(mock_qr):
    mock_qr.return_value = {
        "answer": "Stop the consumer group, fix the offset, restart.",
        "sources": ["runbooks/kafka-consumer-lag.md"],
    }
    response = client.post("/query", json={"question": "How do I fix Kafka consumer lag?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["sources"], list)
