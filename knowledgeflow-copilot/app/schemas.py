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


class StudyStatusResponse(BaseModel):
    stage_name: str
    goals: list[str]
    next_step: str
