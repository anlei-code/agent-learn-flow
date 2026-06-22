# 第 2 课：封装 LLM Client

## 学习目标

这一课的目标不是直接在路由里写 OpenAI 调用，而是学会把大模型调用封装成一个独立模块。

你需要掌握：

- 为什么不要把 API 调用直接写进 `routes.py`。
- `.env` 配置如何进入 `Settings`。
- `LLMClient` 如何隐藏 provider 差异。
- mock 模式和真实 OpenAI 模式如何切换。
- API 调用失败时如何转换成 HTTP 状态码。

## 本课新增文件

```text
app/llm/
  __init__.py
  client.py
```

核心文件：

- `app/llm/client.py`：封装 LLM 调用。
- `app/core/config.py`：新增 LLM 相关配置。
- `app/api/routes.py`：新增 `/chat` 和 `/llm/status`。
- `tests/test_api.py`：新增 LLM Client mock 模式测试。

## 为什么要封装 LLMClient

不要这样写：

```python
@router.post("/chat")
def chat(payload: ChatRequest):
    client = OpenAI()
    response = client.responses.create(...)
    return response.output_text
```

这种写法的问题是：

- 路由和模型供应商强绑定。
- 测试时很容易真的调用外部 API。
- 后面切换模型、加重试、加日志、加成本统计会很难。
- RAG 和 Agent 阶段会复用聊天能力，直接写路由里会重复。

更好的做法：

```text
routes.py 只处理 HTTP
LLMClient 只处理模型调用
settings 只处理配置
schemas.py 只处理输入输出结构
```

## 当前配置

`.env` 中新增：

```env
LLM_PROVIDER=auto
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_SYSTEM_PROMPT=你是 KnowledgeFlow Copilot 的学习助手。回答要简洁、准确，适合 Python 大模型应用开发初学者。
LLM_TIMEOUT_SECONDS=30
```

`LLM_PROVIDER` 当前支持四个值：

- `auto`：有 `DEEPSEEK_API_KEY` 就用 DeepSeek，否则有 `OPENAI_API_KEY` 就用 OpenAI，没有 key 就用 mock。
- `mock`：强制使用本地 mock。
- `openai`：强制使用 OpenAI，没有 Key 时返回 503。
- `deepseek`：强制使用 DeepSeek，没有 Key 时返回 503。

## 当前接口

### GET /api/v1/llm/status

查看当前 LLM 运行状态。

返回示例：

```json
{
  "configured_provider": "auto",
  "active_provider": "mock",
  "model": "gpt-5.5",
  "has_api_key": false
}
```

### POST /api/v1/chat

统一聊天入口。

没有 API Key 时返回 mock：

```json
{
  "reply": "收到你的问题...",
  "provider": "mock",
  "model": "mock-stage-2",
  "session_id": "s2",
  "used_mock": true,
  "tokens_used": 36
}
```

有 API Key 时会调用 OpenAI Responses API。

## 本课关键代码

`LLMClient.chat()` 是统一入口：

```python
def chat(self, message: str, temperature: float) -> LLMResult:
    provider = self._active_provider()
    if provider == "mock":
        return self._mock_chat(message, temperature)
    if provider == "deepseek":
        return self._deepseek_chat(message, temperature)
    return self._openai_chat(message)
```

这段代码表达的是：

```text
业务层不关心到底是 mock 还是 OpenAI
它只要拿到 LLMResult
```

## 真实 API 调用

OpenAI 官方文档推荐新项目使用 Responses API。Python SDK 的基本形态是：

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-5.5",
    input="Write a one-sentence bedtime story."
)
print(response.output_text)
```

本项目把它封装在 `_openai_chat()` 里。

## 动手练习

练习 1：给 `/api/v1/chat` 增加 `temperature`

- 现在 `ChatRequest` 里已经有 `temperature` 字段。
- 把它传入 `LLMClient.chat()`。
- 先只在 mock 回复中显示 temperature。
- 完成状态：已完成。

练习 2：新增 `system_prompt`

- 在 `.env` 中新增 `OPENAI_SYSTEM_PROMPT`。
- 在 `Settings` 中读取。
- 在 `_openai_chat()` 中替代写死的 `instructions`。
- 完成状态：已完成。

练习 3：错误处理

- 把 `LLM_PROVIDER=openai` 且没有 API Key 的情况手动测一遍。
- 观察 `/api/v1/chat` 是否返回 503。
- 给这个行为补一个测试。
- 完成状态：已完成，测试名为 `test_chat_returns_503_when_openai_provider_has_no_key`。

## 本课练习完成记录

- `/api/v1/chat` 已经把 `ChatRequest.temperature` 传入 `LLMClient.chat()`。
- mock 回复中会显示当前 temperature。
- `.env`、`.env.example` 和 `Settings` 已新增 `OPENAI_SYSTEM_PROMPT`。
- `_openai_chat()` 已使用 `self.settings.openai_system_prompt` 作为 OpenAI Responses API 的 `instructions`。
- `LLM_PROVIDER=openai` 且没有 `OPENAI_API_KEY` 时，`/api/v1/chat` 返回 503。
- 已补充 503 行为测试。

## 本课验收

你应该能解释：

- `LLMClient` 为什么不放在 `routes.py` 里。
- `LLM_PROVIDER=auto` 是怎么决定 active provider 的。
- 为什么测试里要强制设置 `LLM_PROVIDER=mock`。
- `.env`、`Settings`、`LLMClient`、`routes.py` 之间的调用链。
