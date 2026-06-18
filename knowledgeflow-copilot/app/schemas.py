from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    app: str
    version: str
    environment: str
    timestamp: datetime


class EchoRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=500,
        description="Text to echo back.",
        examples=["hello FastAPI"],
    )
    request_id: str | None = Field(
        default=None,
        description="Optional client request id for tracing.",
        examples=["demo-001"],
    )


class EchoResponse(BaseModel):
    message: str
    uppercase: str
    reversed_message: str
    length: int = Field(ge=0)
    request_id: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=2,
        max_length=2000,
        description="User message. This mock endpoint does not call a real LLM yet.",
        examples=["我今天开始学习大模型应用开发"],
    )
    session_id: str | None = Field(
        default=None,
        description="Optional conversation session id.",
        examples=["session-001"],
    )
    temperature: float = Field(
        default=0.2,
        ge=0,
        le=2,
        description="Reserved for future real LLM calls.",
    )


class ChatResponse(BaseModel):
    reply: str
    model: str
    session_id: str | None = None
    tokens_used: int = Field(ge=0)


class LLMChatResponse(BaseModel):
    reply: str
    provider: str
    model: str
    session_id: str | None = None
    used_mock: bool
    tokens_used: int | None = Field(default=None, ge=0)


class LLMStatusResponse(BaseModel):
    configured_provider: str
    active_provider: str
    model: str
    has_api_key: bool


class ActionItem(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    owner: str | None = Field(default=None, max_length=50)
    due_date: str | None = Field(default=None, max_length=50)
    priority: Literal["low", "medium", "high"] = "medium"
    source_text: str = Field(min_length=1, max_length=500)


class ActionItemsPayload(BaseModel):
    items: list[ActionItem]


class ActionItemsRequest(BaseModel):
    text: str = Field(
        min_length=5,
        max_length=4000,
        description="Text to extract action items from.",
        examples=["明天前由小李完成接口测试，下周整理学习笔记。"],
    )
    temperature: float = Field(
        default=0.1,
        ge=0,
        le=2,
        description="Reserved for real LLM structured extraction.",
    )


class ActionItemsResponse(BaseModel):
    items: list[ActionItem]
    provider: str
    model: str
    used_mock: bool
    tokens_used: int | None = Field(default=None, ge=0)


class StudyStatusResponse(BaseModel):
    stage_name: str
    goals: list[str]
    next_step: str
