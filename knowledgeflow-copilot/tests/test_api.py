from app.core.config import get_settings


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
    assert body["reversed_message"] == "IPAtsaF olleh"
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


def test_llm_status_uses_mock_provider(client):
    response = client.get("/api/v1/llm/status")

    assert response.status_code == 200
    body = response.json()
    assert body["configured_provider"] == "mock"
    assert body["active_provider"] == "mock"
    assert body["has_api_key"] is False


def test_chat_uses_llm_client_mock_when_no_key(client):
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "请解释什么是 LLM Client",
            "session_id": "session-002",
            "temperature": 0.7,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-stage-2"
    assert body["session_id"] == "session-002"
    assert body["used_mock"] is True
    assert "第二课" in body["reply"]
    assert "temperature=0.7" in body["reply"]


def test_chat_returns_503_when_openai_provider_has_no_key(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    response = client.post("/api/v1/chat", json={"message": "测试配置错误"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
    }


def test_mock_chat_rejects_short_message(client):
    response = client.post("/api/v1/chat/mock", json={"message": "好"})

    assert response.status_code == 422


def test_study_status(client):
    response = client.get("/api/v1/study/status")

    assert response.status_code == 200
    body = response.json()
    assert body["stage_name"] == "第二课：LLM Client 封装"
    assert "理解为什么要封装 LLMClient" in body["goals"]
    assert (
        body["next_step"]
        == "完成第二课练习：传递 temperature、自定义 system prompt、补充 503 测试。"
    )
