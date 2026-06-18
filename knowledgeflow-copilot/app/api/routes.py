from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.llm.client import LLMClient, LLMConfigurationError, LLMProviderError
from app.schemas import (
    ActionItemsRequest,
    ActionItemsResponse,
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
        result = client.chat(payload.message, payload.temperature)
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


@router.post("/extract/action-items", response_model=ActionItemsResponse, tags=["llm"])
def extract_action_items(payload: ActionItemsRequest) -> ActionItemsResponse:
    client = LLMClient(get_settings())
    try:
        result = client.extract_action_items(payload.text, payload.temperature)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ActionItemsResponse(
        items=result.items,
        provider=result.provider,
        model=result.model,
        used_mock=result.used_mock,
        tokens_used=result.tokens_used,
    )


@router.get("/study/status", response_model=StudyStatusResponse, tags=["learning"])
def study_status() -> StudyStatusResponse:
    return StudyStatusResponse(
        stage_name="第三课：结构化输出与信息抽取",
        goals=[
            "理解为什么大模型应用需要稳定输出结构",
            "会用 Pydantic 定义抽取结果",
            "会通过接口返回 list[ActionItem]",
            "会用 mock 方式测试结构化输出",
        ],
        next_step="阅读第三课讲义，并手动调用 /api/v1/extract/action-items。",
    )
