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
    # Force OpenAI mode with an empty key to test configuration error handling.
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    response = client.post("/api/v1/chat", json={"message": "测试配置错误"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
    }


def test_extract_action_items_returns_503_when_openai_provider_has_no_key(client, monkeypatch):
    # The structured extraction endpoint should fail before calling OpenAI.
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    response = client.post(
        "/api/v1/extract/action-items",
        json={"text": "明天前由小李完成接口测试。"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
    }


def test_chat_returns_503_when_deepseek_provider_has_no_key(client, monkeypatch):
    # Same configuration-error behavior for DeepSeek.
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "")
    get_settings.cache_clear()

    response = client.post("/api/v1/chat", json={"message": "娴嬭瘯 DeepSeek 閰嶇疆閿欒"})

    assert response.status_code == 503
    assert response.json() == {
        "detail": "DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek."
    }


def test_extract_action_items_uses_mock_structured_output(client):
    # One input sentence can produce multiple ActionItem rows.
    response = client.post(
        "/api/v1/extract/action-items",
        json={
            "text": "明天前由小李完成接口测试。下周整理学习笔记。",
            "temperature": 0.1,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["model"] == "mock-stage-3"
    assert body["used_mock"] is True
    assert len(body["items"]) == 2
    # The first fragment is "明天前由小李完成接口测试".
    assert body["items"][0]["owner"] == "小李"
    assert body["items"][0]["due_date"] == "明天前"
    assert body["items"][0]["priority"] == "medium"


def test_extract_action_items_marks_urgent_text_as_high_priority(client):
    # Mock priority is keyword-based: "紧急" and "尽快" both mean high.
    response = client.post(
        "/api/v1/extract/action-items",
        json={"text": "紧急：明天前由小李完成接口测试。尽快提交测试报告。"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["items"][0]["priority"] == "high"
    assert body["items"][1]["priority"] == "high"


def test_extract_action_items_marks_low_priority_text_as_low_priority(client):
    # Mock priority is keyword-based: "有空" and "低优" both mean low.
    response = client.post(
        "/api/v1/extract/action-items",
        json={"text": "有空由小王整理学习笔记。低优修复文档错别字。"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["items"][0]["priority"] == "low"
    assert body["items"][1]["priority"] == "low"


def test_extract_action_items_rejects_short_text(client):
    response = client.post("/api/v1/extract/action-items", json={"text": "短"})

    assert response.status_code == 422


def test_mock_chat_rejects_short_message(client):
    response = client.post("/api/v1/chat/mock", json={"message": "好"})

    assert response.status_code == 422


def test_study_status(client):
    response = client.get("/api/v1/study/status")

    assert response.status_code == 200
    body = response.json()
    assert body["stage_name"] == "第四课：Provider 切换与 DeepSeek 接入"
    assert "理解 mock、OpenAI、DeepSeek 三种 provider 的切换逻辑" in body["goals"]
    assert body["next_step"] == (
        "阅读第四课讲义，并确认 /api/v1/llm/status 当前 active_provider 是否符合预期。"
    )
