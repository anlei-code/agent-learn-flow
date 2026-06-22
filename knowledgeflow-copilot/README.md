# KnowledgeFlow Copilot

第一阶段学习项目：FastAPI + Pydantic + 配置 + 日志 + 测试。

这个阶段还不接真实大模型 API，先把 Python 后端应用的基本骨架搭起来。后续阶段会在这个项目上继续加入 LLM Client、RAG、Agent、评测和部署。

## 你会学到什么

- 如何组织一个 Python 后端项目。
- 如何用 FastAPI 写 API。
- 如何用 Pydantic 定义请求和响应。
- 如何用环境变量管理配置。
- 如何写最小可用测试。
- 如何为后续 LLM/RAG 项目打基础。
- 如何封装一个可切换 mock/OpenAI 的 LLM Client。

## 推荐环境

- Python 3.12 优先。
- 当前机器如果只有 Python 3.10，也可以先运行本阶段代码。
- 推荐依赖管理工具：uv。

## 使用 uv 启动

```powershell
cd D:\大模型应用开发\knowledgeflow-copilot
uv venv
uv sync --extra dev
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

打开：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

如果 PowerShell 提示 `uv` 无法识别，说明 PATH 还没有刷新。先关闭当前 PowerShell，重新打开后再试。也可以临时使用完整路径：

```powershell
& "$env:APPDATA\Python\Python310\Scripts\uv.exe" --version
& "$env:APPDATA\Python\Python310\Scripts\uv.exe" sync --extra dev
& "$env:APPDATA\Python\Python310\Scripts\uv.exe" run pytest
```

如果执行 `uv venv` 时提示 `.venv` 已存在，通常不需要重建，直接运行：

```powershell
uv sync --extra dev
```

如果你已经选择重建，并遇到 `failed to remove directory .venv\Lib: 拒绝访问`，说明有 Python、uvicorn 或终端正在占用虚拟环境。先停止服务、关闭占用 `.venv` 的终端，必要时执行：

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -like '*knowledgeflow-copilot*' -or $_.CommandLine -like '*uvicorn*' } |
  Select-Object ProcessId,Name,CommandLine
```

确认没有项目进程后再修复：

```powershell
$env:TEMP = 'D:\uv-temp'
$env:TMP = 'D:\uv-temp'
$env:UV_CACHE_DIR = 'D:\uv-cache'
New-Item -ItemType Directory -Force -Path $env:TEMP, $env:UV_CACHE_DIR
uv venv --clear
uv sync --extra dev --link-mode=copy
uv run pytest
```

## 不使用 uv 的启动方式

```powershell
cd D:\大模型应用开发\knowledgeflow-copilot
py -3.10 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

## 运行测试

```powershell
.\.venv\Scripts\python -m pytest
```

## 当前接口

### GET /api/v1/health

检查服务是否正常。

### POST /api/v1/echo

练习 Pydantic 请求校验和响应模型。

请求：

```json
{
  "message": "hello",
  "request_id": "demo-001"
}
```

响应会返回原文、大写、反转字符串和长度。

### POST /api/v1/chat/mock

模拟聊天接口。这个接口不调用真实大模型，只用于提前熟悉聊天 API 的结构。

请求：

```json
{
  "message": "我今天开始学习大模型应用开发",
  "session_id": "s1",
  "temperature": 0.2
}
```

### GET /api/v1/study/status

返回当前学习阶段、阶段目标和下一步建议。

### GET /api/v1/llm/status

查看当前 LLM 配置状态。这个接口不会返回 API Key 明文，只会告诉你是否配置了 Key。

### POST /api/v1/chat

统一聊天入口。默认 `LLM_PROVIDER=auto`：

- 如果 `.env` 里没有 `OPENAI_API_KEY`，会走本地 mock。
- 如果 `.env` 里设置了 `OPENAI_API_KEY`，会调用 OpenAI Responses API。

请求：

```json
{
  "message": "请解释什么是 LLM Client",
  "session_id": "s2",
  "temperature": 0.2
}
```

## 使用真实 OpenAI API

编辑 `.env`：

```env
LLM_PROVIDER=auto
OPENAI_API_KEY=你的 API Key
OPENAI_MODEL=gpt-5.5
OPENAI_SYSTEM_PROMPT=你是 KnowledgeFlow Copilot 的学习助手。回答要简洁、准确，适合 Python 大模型应用开发初学者。
LLM_TIMEOUT_SECONDS=30
```

然后启动服务：

```powershell
uv run uvicorn app.main:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

先调用 `GET /api/v1/llm/status`，确认 `active_provider` 是否为 `openai`。

### POST /api/v1/extract/action-items

结构化信息抽取接口。它把一段文本抽取成稳定的 `items: list[ActionItem]`。

请求：

```json
{
  "text": "明天前由小李完成接口测试。下周整理学习笔记。",
  "temperature": 0.1
}
```

返回：

```json
{
  "items": [
    {
      "title": "明天前由小李完成接口测试",
      "owner": "小李",
      "due_date": "明天前",
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

## 当前进度补充：DeepSeek provider

当前项目已经支持 `mock`、`openai`、`deepseek` 三条 LLM 路径，并通过 `LLM_PROVIDER` 切换：

```env
LLM_PROVIDER=deepseek
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
DEEPSEEK_API_KEY=你的 DeepSeek API Key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_SYSTEM_PROMPT=你是 KnowledgeFlow Copilot 的学习助手。回答要简洁、准确，适合 Python 大模型应用开发初学者。
LLM_TIMEOUT_SECONDS=30
```

不要把真实 API Key 提交到 Git；`.env` 是本地文件，`.env.example` 只保留空 key。

新增课程：

- [第 4 课：Provider 切换与 DeepSeek 接入](lessons/04_provider_switching_deepseek.md)

当前验证命令：

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
```

应通过 `15` 个测试。
