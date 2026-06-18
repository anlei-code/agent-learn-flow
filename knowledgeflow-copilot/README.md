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
