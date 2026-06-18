from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from app.core.config import Settings


class LLMConfigurationError(RuntimeError):
    """Raised when the selected LLM provider is missing required configuration."""


class LLMProviderError(RuntimeError):
    """Raised when the external LLM provider call fails."""


@dataclass(frozen=True)
class LLMResult:
    reply: str
    provider: str
    model: str
    used_mock: bool
    tokens_used: int | None = None


@dataclass(frozen=True)
class LLMStatus:
    configured_provider: str
    active_provider: str
    model: str
    has_api_key: bool


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def status(self) -> LLMStatus:
        return LLMStatus(
            configured_provider=self.settings.llm_provider,
            active_provider=self._active_provider(),
            model=self.settings.openai_model,
            has_api_key=self._has_openai_key(),
        )

    def chat(self, message: str, temperature: float) -> LLMResult:
        provider = self._active_provider()
        if provider == "mock":
            return self._mock_chat(message, temperature)
        return self._openai_chat(message)

    def _active_provider(self) -> str:
        if self.settings.llm_provider == "mock":
            return "mock"
        if self.settings.llm_provider == "openai":
            return "openai"
        if self._has_openai_key():
            return "openai"
        return "mock"

    def _has_openai_key(self) -> bool:
        return bool(self.settings.openai_api_key and self.settings.openai_api_key.strip())

    def _mock_chat(self, message: str, temperature: float) -> LLMResult:
        words = message.split()
        token_estimate = max(1, len(words)) + 32
        return LLMResult(
            reply=(
                f"收到你的问题：{message}\n"
                f"当前 temperature={temperature}。\n"
                "这是第二课的本地 mock 回复。"
                "当你在 .env 中设置 OPENAI_API_KEY 后，/chat 会切换到真实 LLM 调用。"
            ),
            provider="mock",
            model="mock-stage-2",
            used_mock=True,
            tokens_used=token_estimate,
        )

    def _openai_chat(self, message: str) -> LLMResult:
        if not self._has_openai_key():
            raise LLMConfigurationError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

        client = OpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.llm_timeout_seconds,
        )
        try:
            response = client.responses.create(
                model=self.settings.openai_model,
                instructions=self.settings.openai_system_prompt,
                input=message,
            )
        except OpenAIError as exc:
            raise LLMProviderError(str(exc)) from exc

        return LLMResult(
            reply=response.output_text,
            provider="openai",
            model=self.settings.openai_model,
            used_mock=False,
            tokens_used=self._extract_total_tokens(response),
        )

    def _extract_total_tokens(self, response: object) -> int | None:
        usage = getattr(response, "usage", None)
        if usage is None:
            return None
        total_tokens = getattr(usage, "total_tokens", None)
        if total_tokens is not None:
            return int(total_tokens)
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        if input_tokens is not None and output_tokens is not None:
            return int(input_tokens) + int(output_tokens)
        return None
