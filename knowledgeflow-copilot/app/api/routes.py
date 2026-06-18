from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    EchoRequest,
    EchoResponse,
    HealthResponse,
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


@router.get("/study/status", response_model=StudyStatusResponse, tags=["learning"])
def study_status() -> StudyStatusResponse:
    return StudyStatusResponse(
        stage_name="第一阶段：Python 后端基础",
        goals=[
            "会启动一个 FastAPI 服务",
            "会用 Pydantic 定义请求和响应",
            "会用环境变量管理配置",
            "会写基础接口测试",
            "会读懂一个可扩展项目结构",
        ],
        next_step="继续完成第一阶段练习，然后进入真实 LLM Client 封装。",
    )
