# 第 3 课：结构化输出与信息抽取

## 学习目标

这一课要解决一个真实的大模型应用问题：不能总让模型返回一段自由文本，而是要让它返回稳定结构。

你需要掌握：

- 为什么大模型应用需要结构化输出。
- 如何用 Pydantic 定义抽取结果。
- 如何让 API 返回 `list[ActionItem]`。
- 如何用 mock 模式测试结构化输出。
- 如何为真实 OpenAI structured output 预留路径。

## 本课新增能力

新增接口：

```text
POST /api/v1/extract/action-items
```

它接收一段文本，返回行动项列表。

请求示例：

```json
{
  "text": "明天前由小李完成接口测试。下周整理学习笔记。",
  "temperature": 0.1
}
```

返回示例：

```json
{
  "items": [
    {
      "title": "明天前由小李完成接口测试",
      "owner": "小李完成接口测试",
      "due_date": "明天",
      "priority": "medium",
      "source_text": "明天前由小李完成接口测试"
    }
  ],
  "provider": "mock",
  "model": "mock-stage-3",
  "used_mock": true,
  "tokens_used": 28
}
```

## 关键模型

在 `app/schemas.py` 中新增：

```python
class ActionItem(BaseModel):
    title: str
    owner: str | None = None
    due_date: str | None = None
    priority: Literal["low", "medium", "high"] = "medium"
    source_text: str
```

这就是结构化输出的核心。

自由文本是这样：

```text
明天前由小李完成接口测试
```

结构化后是这样：

```json
{
  "title": "明天前由小李完成接口测试",
  "owner": "小李完成接口测试",
  "due_date": "明天",
  "priority": "medium",
  "source_text": "明天前由小李完成接口测试"
}
```

## 为什么重要

如果模型只返回一段话，后端和前端很难稳定处理。

结构化输出可以直接用于：

- 页面表格展示。
- 数据库存储。
- RAG 引用来源。
- Agent 工具参数。
- 自动评测。
- 工作流下一步输入。

## 当前实现

`LLMClient.extract_action_items()` 是统一入口：

```python
def extract_action_items(self, text: str, temperature: float) -> ActionItemExtractionResult:
    provider = self._active_provider()
    if provider == "mock":
        return self._mock_extract_action_items(text)
    return self._openai_extract_action_items(text, temperature)
```

当前没有 API Key 时走 mock：

```python
return self._mock_extract_action_items(text)
```

有 API Key 且 provider 为 OpenAI 时，走 OpenAI structured output：

```python
response = client.responses.parse(
    model=self.settings.openai_model,
    instructions=...,
    input=text,
    text_format=ActionItemsPayload,
    temperature=temperature,
)
```

这里的 `text_format=ActionItemsPayload` 表示希望 OpenAI 按 Pydantic 模型返回结构化结果。

## 动手练习

练习 1：优化 owner 抽取

- 当前 mock 的 owner 抽取比较粗糙。
- 把 `明天前由小李完成接口测试` 的 owner 优化成 `小李`。

练习 2：新增 priority 规则

- 如果文本包含 `紧急`、`尽快`，返回 `high`。
- 如果文本包含 `有空`、`低优`，返回 `low`。
- 给这两个场景补测试。

练习 3：补 OpenAI 配置错误测试

- 设置 `LLM_PROVIDER=openai`。
- 删除 `OPENAI_API_KEY`。
- 调用 `/api/v1/extract/action-items`。
- 断言返回 503。

## 本课验收

你应该能解释：

- `ActionItem` 和 `ActionItemsResponse` 的区别。
- 为什么 `ActionItemsPayload` 不直接作为 API response。
- mock 结构化输出和 OpenAI structured output 的切换逻辑。
- 为什么结构化输出是 RAG 和 Agent 的基础。

