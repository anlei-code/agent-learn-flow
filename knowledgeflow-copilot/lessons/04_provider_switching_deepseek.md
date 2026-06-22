# 第 4 课：Provider 切换与 DeepSeek 接入

## 学习目标

这一课的重点是：让同一个业务接口可以在 mock、OpenAI、DeepSeek 之间切换，而不是把某一个模型供应商写死在路由里。

你需要掌握：

- 为什么 LLM provider 要配置化。
- DeepSeek 为什么可以复用 OpenAI SDK。
- `LLM_PROVIDER=auto` 如何选择真实 provider。
- 为什么单元测试要强制走 mock。
- 为什么真实模型返回 JSON 后仍然要做 Pydantic 校验。

## 本课新增能力

当前项目支持四种 provider 配置：

```env
LLM_PROVIDER=auto
LLM_PROVIDER=mock
LLM_PROVIDER=openai
LLM_PROVIDER=deepseek
```

其中：

- `mock`：本地规则模拟，不联网，适合测试。
- `openai`：调用 OpenAI Responses API。
- `deepseek`：调用 DeepSeek 的 OpenAI 兼容接口。
- `auto`：优先使用 DeepSeek key，其次 OpenAI key，最后 fallback 到 mock。

## 配置项

`.env.example` 中保留空 key，真实 key 只放在本地 `.env`：

```env
LLM_PROVIDER=deepseek
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_SYSTEM_PROMPT=你是 KnowledgeFlow Copilot 的学习助手。回答要简洁、准确，适合 Python 大模型应用开发初学者。
LLM_TIMEOUT_SECONDS=30
```

注意：不要把真实 API Key 提交到 Git。

## 为什么 DeepSeek 可以复用 OpenAI SDK

DeepSeek 提供 OpenAI 兼容接口，所以代码可以这样创建客户端：

```python
client = OpenAI(
    api_key=self.settings.deepseek_api_key,
    base_url=self.settings.deepseek_base_url,
    timeout=self.settings.llm_timeout_seconds,
)
```

关键是 `base_url`：

```text
https://api.deepseek.com
```

它告诉 OpenAI SDK：请求不要发到 OpenAI，而是发到 DeepSeek。

## Provider 切换逻辑

核心代码在 `LLMClient._active_provider()`：

```python
def _active_provider(self) -> str:
    if self.settings.llm_provider == "mock":
        return "mock"
    if self.settings.llm_provider == "deepseek":
        return "deepseek"
    if self.settings.llm_provider == "openai":
        return "openai"
    if self._has_deepseek_key():
        return "deepseek"
    if self._has_openai_key():
        return "openai"
    return "mock"
```

这段逻辑表达的是：

```text
明确指定的 provider 优先。
auto 模式下，谁有 key 就用谁。
都没有 key 时，本地 mock 兜底。
```

## 聊天接口的统一入口

`/api/v1/chat` 不关心底层是谁：

```python
def chat(self, message: str, temperature: float) -> LLMResult:
    provider = self._active_provider()
    if provider == "mock":
        return self._mock_chat(message, temperature)
    if provider == "deepseek":
        return self._deepseek_chat(message, temperature)
    return self._openai_chat(message)
```

路由层只拿 `LLMResult`：

```python
return LLMChatResponse(
    reply=result.reply,
    provider=result.provider,
    model=result.model,
    used_mock=result.used_mock,
    tokens_used=result.tokens_used,
)
```

这就是封装的价值：路由层稳定，provider 可以替换。

## 结构化输出的差异

OpenAI 路径使用 `responses.parse`：

```python
response = client.responses.parse(
    model=self.settings.openai_model,
    input=text,
    text_format=ActionItemsPayload,
)
```

这里 OpenAI SDK 可以直接把结果解析成 Pydantic 模型。

DeepSeek 路径使用 JSON 输出：

```python
response = client.chat.completions.create(
    model=self.settings.deepseek_model,
    messages=[...],
    response_format={"type": "json_object"},
)
```

然后项目自己校验：

```python
parsed = ActionItemsPayload.model_validate_json(raw_content)
```

所以 DeepSeek 的结构化流程是：

```text
提示模型返回 JSON
        ↓
拿到 JSON 字符串
        ↓
Pydantic 校验成 ActionItemsPayload
        ↓
返回 items: list[ActionItem]
```

## 为什么还要 Pydantic 校验

即使模型被要求返回 JSON，也不能完全相信它。

可能的问题包括：

- 字段名写错，比如返回 `tasks` 而不是 `items`。
- `priority` 返回 `urgent`，但项目只允许 `low`、`medium`、`high`。
- 少了 `source_text`。
- 返回了 JSON 外面的解释文本。

Pydantic 校验的作用是把不稳定的模型输出挡在业务系统外面。

## 测试隔离

`tests/conftest.py` 里强制测试走 mock：

```python
monkeypatch.setenv("LLM_PROVIDER", "mock")
monkeypatch.delenv("OPENAI_API_KEY", raising=False)
monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
get_settings.cache_clear()
```

这样单元测试不会：

- 花钱。
- 依赖网络。
- 因为外部模型返回变化而失败。
- 泄露真实 key。

真实 provider 是否可用，可以用单独的集成测试或手动命令验证。

## 本课练习

练习 1：增加 DeepSeek 配置错误测试

- 设置 `LLM_PROVIDER=deepseek`。
- 设置 `DEEPSEEK_API_KEY=""`。
- 调用 `/api/v1/extract/action-items`。
- 断言返回 503。

练习 2：给 `/api/v1/llm/status` 增加 base_url

- 当前接口只返回 provider、model、has_api_key。
- 试着新增一个可选字段 `base_url`。
- 注意不要返回 API Key。

练习 3：设计一个集成测试开关

- 只有设置 `RUN_REAL_LLM_TESTS=1` 时才调用真实 DeepSeek。
- 默认情况下跳过真实模型测试。
- 思考：为什么真实 API 测试不应该和普通单元测试混在一起。

## 本课验收

你应该能解释：

- 为什么 provider 选择逻辑不应该写在 `routes.py`。
- `mock`、`openai`、`deepseek` 三条路径分别做什么。
- DeepSeek 为什么要设置 `base_url`。
- 为什么模型返回 JSON 后还要用 `ActionItemsPayload` 校验。
- 为什么 RAG 和 Agent 阶段需要可切换、可测试、可校验的 LLM Client。

