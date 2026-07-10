# AI 跨境电商选品智能体 MVP

这是一个基于 Python、FastAPI、LangGraph、PostgreSQL 和 DeepSeek API 的跨境电商选品智能体 MVP。

用户输入商品关键词后，系统会自动完成关键词归一化、趋势分析、竞品分析、评论痛点分析、机会评分和 Markdown 选品报告生成。

当前项目定位是：

> 使用免费公开数据源和可扩展 Tool/Skill 架构，完成跨境电商选品机会初筛。

本项目不直接使用 Keepa、Amazon SP-API、SellerSprite、Jungle Scout 等付费 API，但已经预留商业数据源 Provider 扩展边界。

## 核心能力

- 输入中文或英文商品关键词。
- 默认分析美国站，国家代码为 `US`。
- 使用 DeepSeek API 做关键词归一化、评论痛点总结和报告生成。
- 使用 Google Trends 免费数据源，支持 pytrends 实时获取和失败降级。
- 使用 Amazon Reviews 2023 小样本数据做商品和评论分析。
- 通过 LangGraph 编排选品分析工作流。
- 通过 Skill + Tool 分层解耦分析能力。
- 使用 PostgreSQL 保存任务、分析结果和报告。
- 支持同步分析、异步分析、批量分析和历史任务查询。
- 输出 Markdown 格式选品报告。
- 提供一个最小本地前端页面。

## 技术栈

- Python 3.12
- FastAPI
- LangGraph
- LangChain 兼容 AI 边界
- DeepSeek API
- PostgreSQL
- Docker Compose
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- pytrends
- pandas
- scikit-learn
- pytest

## 项目结构

```text
trend-agent/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── ai/                 # DeepSeek Client、LangGraph 工作流、Agent 边界
│   │   ├── api/                # FastAPI 路由
│   │   ├── common/             # 统一响应、异常、枚举
│   │   ├── core/               # 配置和日志
│   │   ├── db/                 # 数据库连接和 ORM Base
│   │   ├── dependencies/       # FastAPI 依赖注入
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── providers/          # 免费/商业数据源 Provider 扩展边界
│   │   ├── repositories/       # 数据访问层
│   │   ├── schemas/            # Pydantic 请求、响应、DTO
│   │   ├── services/           # 业务服务层
│   │   ├── skills/             # 趋势、商品、评论、评分、报告 Skill
│   │   ├── static/             # 最小前端页面
│   │   └── tools/              # Google Trends、商品、评论、评分、报告 Tool
│   └── tests/
├── data/
│   └── samples/                # MVP 小样本数据
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── prd.md
├── tdd.md
└── todo.md
```

## 本地环境要求

- Docker Desktop 可正常运行。
- 本地 Anaconda 环境中存在 `hooks` 环境。
- Python 依赖已安装到 `hooks` 环境。
- 如果要调用真实 DeepSeek API，需要配置本地 `.env`。

检查环境：

```powershell
conda run -n hooks python --version
docker --version
docker compose version
```

## 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env`，填写你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=replace_with_your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

数据库默认配置：

```env
POSTGRES_DB=trends_agent
POSTGRES_USER=trends_agent
POSTGRES_PASSWORD=trends_agent_dev_password
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://trends_agent:trends_agent_dev_password@localhost:5432/trends_agent
```

注意：不要提交真实 `.env` 或 API Key。

## 启动数据库

```powershell
docker compose up -d postgres
```

检查数据库容器状态：

```powershell
docker compose ps
```

执行数据库迁移：

```powershell
$env:PYTHONPATH="D:\Work\code\trend-agent\backend"
conda run -n hooks alembic upgrade head
```

## 启动后端服务

```powershell
conda run -n hooks uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

访问：

- API 文档：http://127.0.0.1:8000/docs
- 最小前端：http://127.0.0.1:8000/api/v1/
- 健康检查：http://127.0.0.1:8000/api/v1/health

## API 示例

### 健康检查

```http
GET /api/v1/health
```

### 同步选品分析

```http
POST /api/v1/selections/analyze
Content-Type: application/json

{
  "keyword": "智能手环",
  "country": "US"
}
```

### 异步选品分析

```http
POST /api/v1/selections/analyze-async
Content-Type: application/json

{
  "keyword": "智能手环",
  "country": "US"
}
```

### 批量选品分析

```http
POST /api/v1/selections/batch-analyze
Content-Type: application/json

{
  "keywords": ["智能手环", "portable blender", "dog water bottle"],
  "country": "US"
}
```

### 查询任务详情

```http
GET /api/v1/selections/{task_id}
```

### 查询历史任务

```http
GET /api/v1/selections?limit=20&offset=0
```

## 运行测试

```powershell
$env:PYTHONPATH="D:\Work\code\trend-agent\backend"
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
conda run -n hooks pytest backend/tests -q
```

当前测试覆盖：

- Health Check
- DeepSeek Client 结构化解析和异常转换
- Repository 与 Service
- Google Trends 失败降级
- 商品分析 Tool
- 评论痛点分析 Tool
- 机会评分 Tool
- 报告模板降级
- Skill 组合
- LangGraph 工作流
- 同步分析 API
- 异步分析 API
- 批量分析 API
- 历史任务查询
- 最小前端页面
- 商业数据源 Provider 边界

## Agent 工作流

```text
create_task_context
  -> normalize_keyword
  -> plan_analysis
  -> run_trend_skill
  -> run_product_skill
  -> run_review_skill
  -> run_scoring_skill
  -> run_report_skill
  -> persist_results
```

说明：

- LangGraph 负责编排固定、可控的工作流。
- Skill 负责组合 Tool 并返回业务 DTO。
- Tool 负责数据获取或纯计算。
- Service 负责事务和业务编排。
- Repository 负责数据库读写。
- API route 只负责接收请求和返回响应。

## 数据源说明

当前 MVP 使用：

- Google Trends：通过 pytrends 获取，默认关闭实时请求，使用中性降级结果保证本地稳定。
- Amazon Reviews 2023：当前使用 `data/samples` 中的小样本数据。
- DeepSeek API：用于关键词归一化、评论总结和报告生成；未配置 API Key 时会自动降级到模板报告。

已预留：

- Hugging Face streaming 数据读取接口。
- Keepa Provider 接口。
- Amazon SP-API Provider 接口。
- SellerSprite Provider 接口。

## 数据限制与风险说明

本项目当前不提供：

- Amazon 实时销量
- BSR 排名
- 广告竞价
- FBA 费用
- 真实毛利
- 实时竞品抓取

因此报告只适合作为选品机会初筛，不应作为最终商业投资决策。

开发真实产品前，仍需要人工验证：

- 供应链成本
- 物流和关税
- 平台佣金
- 合规认证
- 广告成本
- 实时竞品状态

## 常用命令

启动数据库：

```powershell
docker compose up -d postgres
```

停止数据库：

```powershell
docker compose down
```

执行迁移：

```powershell
$env:PYTHONPATH="D:\Work\code\trend-agent\backend"
conda run -n hooks alembic upgrade head
```

启动 API：

```powershell
conda run -n hooks uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

运行测试：

```powershell
$env:PYTHONPATH="D:\Work\code\trend-agent\backend"
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONUTF8="1"
conda run -n hooks pytest backend/tests -q
```
