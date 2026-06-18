from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from app.core.config import Settings
from app.schemas import ActionItem, ActionItemsPayload


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
class ActionItemExtractionResult:
    items: list[ActionItem]
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

    def extract_action_items(self, text: str, temperature: float) -> ActionItemExtractionResult:
        provider = self._active_provider()
        if provider == "mock":
            return self._mock_extract_action_items(text)
        return self._openai_extract_action_items(text, temperature)

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

    def _mock_extract_action_items(self, text: str) -> ActionItemExtractionResult:
        fragments = self._split_action_fragments(text)
        items = [
            ActionItem(
                title=self._clean_action_title(fragment),
                owner=self._guess_owner(fragment),
                due_date=self._guess_due_date(fragment),
                priority=self._guess_priority(fragment),
                source_text=fragment,
            )
            for fragment in fragments
        ]
        return ActionItemExtractionResult(
            items=items,
            provider="mock",
            model="mock-stage-3",
            used_mock=True,
            tokens_used=max(1, len(text.split())) + 24,
        )

    def _openai_extract_action_items(
        self,
        text: str,
        temperature: float,
    ) -> ActionItemExtractionResult:
        if not self._has_openai_key():
            raise LLMConfigurationError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

        client = OpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.llm_timeout_seconds,
        )
        try:
            response = client.responses.parse(
                model=self.settings.openai_model,
                instructions=(
                    f"{self.settings.openai_system_prompt}\n"
                    "请从用户文本中抽取行动项。没有明确行动项时返回空 items。"
                    "due_date 保留原文中的时间表达，owner 保留原文中的负责人。"
                ),
                input=text,
                text_format=ActionItemsPayload,
                temperature=temperature,
            )
        except OpenAIError as exc:
            raise LLMProviderError(str(exc)) from exc

        parsed = response.output_parsed
        items = parsed.items if parsed is not None else []
        return ActionItemExtractionResult(
            items=items,
            provider="openai",
            model=self.settings.openai_model,
            used_mock=False,
            tokens_used=self._extract_total_tokens(response),
        )

    def _split_action_fragments(self, text: str) -> list[str]:
        separators = ["\n", "。", "；", ";", "，", ","]
        fragments = [text.strip()]
        for separator in separators:
            next_fragments: list[str] = []
            for fragment in fragments:
                next_fragments.extend(part.strip() for part in fragment.split(separator))
            fragments = next_fragments

        action_keywords = [
            "完成",
            "整理",
            "开发",
            "测试",
            "提交",
            "修复",
            "跟进",
            "负责",
            "todo",
            "TODO",
        ]
        return [
            fragment
            for fragment in fragments
            if fragment and any(keyword in fragment for keyword in action_keywords)
        ]

    def _clean_action_title(self, fragment: str) -> str:
        return fragment.strip(" -:：，。；;")

    def _guess_owner(self, fragment: str) -> str | None:
        markers = ["由", "负责人：", "负责人:"]
        for marker in markers:
            if marker not in fragment:
                continue
            tail = fragment.split(marker, 1)[1].strip()
            if not tail:
                return None
            return tail.split()[0].strip("，,。；;:：")
        return None

    def _guess_due_date(self, fragment: str) -> str | None:
        due_keywords = ["今天", "明天", "后天", "本周", "下周", "月底", "周一", "周五"]
        for keyword in due_keywords:
            if keyword in fragment:
                return keyword
        return None

    def _guess_priority(self, fragment: str) -> str:
        if any(keyword in fragment for keyword in ["紧急", "尽快", "马上", "高优"]):
            return "high"
        if any(keyword in fragment for keyword in ["可选", "有空", "低优"]):
            return "low"
        return "medium"

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
