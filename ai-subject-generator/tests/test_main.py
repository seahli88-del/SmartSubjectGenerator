from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def fake_ai_client(generate_content):
    return SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content),
        ),
    )


def test_rejects_blank_topic():
    response = client.post(
        "/generate-subjects",
        json={"topic": "  ", "tone": "Professional"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Topic cannot be blank."


def test_rejects_topic_over_500_characters():
    response = client.post(
        "/generate-subjects",
        json={"topic": "x" * 501, "tone": "Professional"},
    )

    assert response.status_code == 422


def test_rejects_unsupported_tone():
    response = client.post(
        "/generate-subjects",
        json={"topic": "A spring sale", "tone": "Sarcastic"},
    )

    assert response.status_code == 422


def test_returns_generated_subject_lines(monkeypatch):
    generate_content = AsyncMock(
        return_value=SimpleNamespace(text="1. A spring sale\n2. Fresh deals"),
    )
    monkeypatch.setattr(main, "ai_client", fake_ai_client(generate_content))

    response = client.post(
        "/generate-subjects",
        json={"topic": "A spring sale", "tone": "Professional"},
    )

    assert response.status_code == 200
    assert response.json()["subject_lines"] == "1. A spring sale\n2. Fresh deals"
    generate_content.assert_awaited_once()


def test_returns_generic_error_when_generation_fails(caplog, monkeypatch):
    generate_content = AsyncMock(side_effect=RuntimeError("private provider detail"))
    monkeypatch.setattr(main, "ai_client", fake_ai_client(generate_content))

    response = client.post(
        "/generate-subjects",
        json={"topic": "A spring sale", "tone": "Professional"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Subject generation failed. Please try again later."
    assert "private provider detail" in caplog.text


def test_returns_unavailable_when_ai_client_is_missing(monkeypatch):
    monkeypatch.setattr(main, "ai_client", None)

    response = client.post(
        "/generate-subjects",
        json={"topic": "A spring sale", "tone": "Professional"},
    )

    assert response.status_code == 503


def test_limits_generation_requests_per_client_ip(monkeypatch):
    generate_content = AsyncMock(
        return_value=SimpleNamespace(text="1. A spring sale"),
    )
    monkeypatch.setattr(main, "ai_client", fake_ai_client(generate_content))
    rate_limited_client = TestClient(main.app, client=("192.0.2.10", 12345))

    responses = [
        rate_limited_client.post(
            "/generate-subjects",
            json={"topic": "A spring sale", "tone": "Professional"},
        )
        for _ in range(6)
    ]

    assert [response.status_code for response in responses] == [200] * 5 + [429]
    assert generate_content.await_count == 5
