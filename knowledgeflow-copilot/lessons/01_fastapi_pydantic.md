# 第 1 课：FastAPI + Pydantic 项目骨架

## 学习目标

完成这一课后，你应该能看懂：

- `app/main.py` 如何创建 FastAPI 应用。
- `app/core/config.py` 如何读取环境变量。
- `app/schemas.py` 如何定义请求和响应模型。
- `app/api/routes.py` 如何声明路由。
- `tests/test_api.py` 如何验证接口。

## 建议阅读顺序

1. 先读 `app/main.py`。
2. 再读 `app/core/config.py`。
3. 再读 `app/schemas.py`。
4. 再读 `app/api/routes.py`。
5. 最后读 `tests/test_api.py`。

## 动手练习

练习 1：修改 `/api/v1/echo`

- 给 `EchoResponse` 增加一个字段 `reversed_message`。
- 返回用户输入的反转字符串。
- 给测试补一条断言。

练习 2：修改 `/api/v1/chat/mock`

- 当用户输入少于 2 个字时，返回 422 校验错误。
- 提示：修改 `ChatRequest.message` 的 `min_length`。

练习 3：新增接口 `/api/v1/study/status`

- 返回当前阶段名称。
- 返回本阶段目标列表。
- 返回下一步建议。

## 学习重点

第一阶段不要急着接大模型 API。你先要习惯“输入输出都有明确结构”的写法，因为后面结构化输出、工具调用、RAG 评测都会依赖这个工程基础。

