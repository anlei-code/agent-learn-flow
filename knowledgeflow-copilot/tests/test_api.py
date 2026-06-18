def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "KnowledgeFlow Copilot"
    assert body["version"] == "0.1.0"


def test_echo(client):
    response = client.post(
        "/api/v1/echo",
        json={"message": "hello FastAPI", "request_id": "demo-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "hello FastAPI"
    assert body["uppercase"] == "HELLO FASTAPI"
    assert body["length"] == 13
    assert body["request_id"] == "demo-001"


def test_echo_requires_message(client):
    response = client.post("/api/v1/echo", json={"message": ""})

    assert response.status_code == 422


def test_mock_chat(client):
    response = client.post(
        "/api/v1/chat/mock",
        json={"message": "我今天开始学习大模型应用开发", "session_id": "session-001"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "第一阶段" in body["reply"]
    assert body["model"] == "mock-stage-1"
    assert body["session_id"] == "session-001"
    assert body["tokens_used"] > 0

