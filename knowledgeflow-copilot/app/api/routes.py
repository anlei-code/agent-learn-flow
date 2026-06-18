from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.llm.client import LLMClient, LLMConfigurationError, LLMProviderError
from app.schemas import (
    ChatRequest,
    ChatResponse,
    EchoRequest,
    EchoResponse,
    HealthResponse,
    LLMChatResponse,
    LLMStatusResponse,
    StudyStatusResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/echo", response_model=EchoResponse, tags=["learning"])
def echo(payload: EchoRequest) -> EchoResponse:
    return EchoResponse(
        message=payload.message,
        uppercase=payload.message.upper(),
        reversed_message=payload.message[::-1],
        length=len(payload.message),
        request_id=payload.request_id,
    )


@router.post("/chat/mock", response_model=ChatResponse, tags=["learning"])
def mock_chat(payload: ChatRequest) -> ChatResponse:
    words = payload.message.split()
    token_estimate = max(1, len(words)) + 24
    reply = (
        f"收到你的问题：{payload.message}\n"
        "第一阶段先练 FastAPI、Pydantic、配置和测试。"
        "等这个骨架稳定后，我们再接入真实 LLM API。"
    )
    return ChatResponse(
        reply=reply,
        model="mock-stage-1",
        session_id=payload.session_id,
        tokens_used=token_estimate,
    )


@router.get("/llm/status", response_model=LLMStatusResponse, tags=["llm"])
def llm_status() -> LLMStatusResponse:
    status = LLMClient(get_settings()).status()
    return LLMStatusResponse(
        configured_provider=status.configured_provider,
        active_provider=status.active_provider,
        model=status.model,
        has_api_key=status.has_api_key,
    )


@router.post("/chat", response_model=LLMChatResponse, tags=["llm"])
def chat(payload: ChatRequest) -> LLMChatResponse:
    client = LLMClient(get_settings())
    try:
        result = client.chat(payload.message)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return LLMChatResponse(
        reply=result.reply,
        provider=result.provider,
        model=result.model,
        session_id=payload.session_id,
        used_mock=result.used_mock,
        tokens_used=result.tokens_used,
    )


@router.get("/study/status", response_model=StudyStatusResponse, tags=["learning"])
def study_status() -> StudyStatusResponse:
    return StudyStatusResponse(
        stage_name="第二课：LLM Client 封装",
        goals=[
            "理解为什么要封装 LLMClient",
            "会用环境变量切换 mock 和 OpenAI provider",
            "会通过 FastAPI 暴露统一聊天接口",
            "会在测试中避免真实调用外部 API",
        ],
        next_step="完成第二课练习：传递 temperature、自定义 system prompt、补充 503 测试。",
    )
