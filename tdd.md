# AI跨境电商选品智能体 MVP TDD

## 技术选型确认

- 后端框架：FastAPI
- Agent 编排：LangGraph
- LLM 适配：LangChain-compatible DeepSeek Client
- LLM 服务：DeepSeek API
- 数据库：PostgreSQL 运行在 Docker
- ORM：SQLAlchemy 2.x
- Migration：Alembic
- 数据处理：pandas / polars
- 趋势数据：pytrends，后续支持 Google Trends CSV fallback
- 商品和评论数据：Amazon Reviews 2023 小样本或 Hugging Face streaming
- Python 环境：本机 Anaconda `hooks` 环境
- 默认站点：美国站 `US`

## 本地运行配置

### Conda 环境

后续命令默认使用：

```powershell
conda run -n hooks python
conda run -n hooks pip
conda run -n hooks pytest
```

### Docker PostgreSQL

默认数据库配置：

```env
POSTGRES_DB=trends_agent
POSTGRES_USER=trends_agent
POSTGRES_PASSWORD=trends_agent_dev_password
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://trends_agent:trends_agent_dev_password@localhost:5432/trends_agent
```

DeepSeek 配置：

```env
DEEPSEEK_API_KEY=replace_with_your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

真实 API Key 必须放入本地 `.env`，不得提交到仓库。

## 系统架构设计

```text
FastAPI
  -> Selection Service
  -> LangGraph Selection Workflow
  -> Skill Router
  -> Trend Skill
  -> Product Skill
  -> Review Skill
  -> Scoring Skill
  -> Report Skill
  -> Repository
  -> PostgreSQL
```

## 分层设计

建议目录结构：

```text
backend/
  app/
    api/
      v1/
        routes/
          selection.py
          health.py
    core/
      settings.py
      constants.py
      logging.py
    db/
      session.py
      base.py
    models/
      selection_task.py
      trend_result.py
      product_result.py
      review_result.py
      score_result.py
      report.py
    schemas/
      selection.py
      report.py
    repositories/
      selection_repository.py
    services/
      selection_service.py
    ai/
      clients/
        deepseek_client.py
      workflow/
        selection_graph.py
        state.py
      agent/
        planner.py
        router.py
    skills/
      trend/
        skill.py
      product/
        skill.py
      review/
        skill.py
      scoring/
        skill.py
      report/
        skill.py
    tools/
      google_trend.py
      product_analysis.py
      review_analysis.py
      scoring.py
      report_generation.py
    common/
      response.py
      exceptions.py
  tests/
data/
  samples/
  cache/
  imports/
alembic/
docker-compose.yml
.env.example
```

## Agent 工作流设计

LangGraph 节点：

```text
START
  -> create_task_context
  -> normalize_keyword
  -> plan_analysis
  -> run_trend_skill
  -> run_product_skill
  -> run_review_skill
  -> run_scoring_skill
  -> run_report_skill
  -> persist_results
  -> END
```

### SelectionState

```text
task_id: UUID
keyword: str
normalized_keyword: str
country: str
language: str
trend_result: dict | None
product_result: dict | None
review_result: dict | None
score_result: dict | None
report_markdown: str | None
errors: list[dict]
```

### 失败降级策略

- `pytrends` 失败：记录错误，趋势分使用中性分或 fallback provider。
- 商品 metadata 不足：记录样本不足，竞争评分降低置信度。
- 评论数量不足：报告标注“评论样本不足”，痛点评分降低置信度。
- DeepSeek 报告失败：使用模板报告生成器。

## Skill 与 Tool 协议

### Trend Skill

输入：

```json
{
  "keyword": "smart fitness band",
  "country": "US"
}
```

输出：

```json
{
  "trend_score": 72.5,
  "growth_rate": 0.18,
  "avg_interest": 54.3,
  "peak_interest": 100,
  "trend_series": [],
  "related_queries": [],
  "data_source": "pytrends"
}
```

### Product Skill

输入：

```json
{
  "keyword": "smart fitness band",
  "country": "US",
  "limit": 500
}
```

输出：

```json
{
  "matched_product_count": 128,
  "brand_distribution": {},
  "category_distribution": {},
  "price_min": 19.99,
  "price_max": 199.99,
  "price_median": 49.99,
  "price_avg": 58.25,
  "competition_score": 68.0,
  "sample_products": [],
  "data_source": "amazon_reviews_2023_metadata_sample"
}
```

### Review Skill

输入：

```json
{
  "keyword": "smart fitness band",
  "product_ids": [],
  "limit": 1000
}
```

输出：

```json
{
  "review_count": 820,
  "positive_ratio": 0.64,
  "negative_ratio": 0.21,
  "sentiment_score": 63.0,
  "pain_points": [],
  "improvements": [],
  "representative_reviews": [],
  "data_source": "amazon_reviews_2023_reviews_sample"
}
```

### Scoring Skill

输入：

```json
{
  "trend_result": {},
  "product_result": {},
  "review_result": {}
}
```

输出：

```json
{
  "trend_score": 72.5,
  "competition_score": 58.0,
  "pain_point_score": 70.0,
  "profit_score": 61.0,
  "opportunity_score": 66.35,
  "score_detail": {}
}
```

### Report Skill

输入：

```json
{
  "keyword": "智能手环",
  "normalized_keyword": "smart fitness band",
  "trend_result": {},
  "product_result": {},
  "review_result": {},
  "score_result": {}
}
```

输出：

```json
{
  "title": "选品分析报告：智能手环",
  "markdown_content": "# 选品分析报告：智能手环",
  "summary": "该品类适合进一步调研。",
  "recommendation": "cautiously_recommended"
}
```

## 数据库设计

### 命名规范

- 表名使用小写复数。
- 字段使用 `snake_case`。
- 主键统一使用 `UUID`。
- 金额使用 `NUMERIC(10, 2)`。
- 分数使用 `NUMERIC(5, 2)`，范围 0 到 100。
- 结构化分析结果使用 `JSONB`。
- 所有结果表使用 `task_id` 关联 `selection_tasks.id`。

### DDL 草案

```sql
CREATE TABLE selection_tasks (
    id UUID PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    normalized_keyword VARCHAR(255),
    country VARCHAR(10) NOT NULL DEFAULT 'US',
    language VARCHAR(20) NOT NULL DEFAULT 'zh-CN',
    status VARCHAR(30) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE trend_results (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES selection_tasks(id) ON DELETE CASCADE,
    keyword VARCHAR(255) NOT NULL,
    country VARCHAR(10) NOT NULL,
    trend_score NUMERIC(5, 2),
    growth_rate NUMERIC(8, 4),
    avg_interest NUMERIC(5, 2),
    peak_interest NUMERIC(5, 2),
    trend_series JSONB NOT NULL DEFAULT '[]'::jsonb,
    related_queries JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE product_results (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES selection_tasks(id) ON DELETE CASCADE,
    matched_product_count INTEGER NOT NULL DEFAULT 0,
    brand_distribution JSONB NOT NULL DEFAULT '{}'::jsonb,
    category_distribution JSONB NOT NULL DEFAULT '{}'::jsonb,
    price_min NUMERIC(10, 2),
    price_max NUMERIC(10, 2),
    price_median NUMERIC(10, 2),
    price_avg NUMERIC(10, 2),
    competition_score NUMERIC(5, 2),
    sample_products JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE review_results (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES selection_tasks(id) ON DELETE CASCADE,
    review_count INTEGER NOT NULL DEFAULT 0,
    positive_ratio NUMERIC(5, 4),
    negative_ratio NUMERIC(5, 4),
    sentiment_score NUMERIC(5, 2),
    pain_points JSONB NOT NULL DEFAULT '[]'::jsonb,
    improvements JSONB NOT NULL DEFAULT '[]'::jsonb,
    representative_reviews JSONB NOT NULL DEFAULT '[]'::jsonb,
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE score_results (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES selection_tasks(id) ON DELETE CASCADE,
    trend_score NUMERIC(5, 2),
    competition_score NUMERIC(5, 2),
    pain_point_score NUMERIC(5, 2),
    profit_score NUMERIC(5, 2),
    opportunity_score NUMERIC(5, 2),
    score_detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE reports (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES selection_tasks(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    markdown_content TEXT NOT NULL,
    summary TEXT,
    recommendation VARCHAR(50),
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_selection_tasks_keyword ON selection_tasks(keyword);
CREATE INDEX idx_selection_tasks_status ON selection_tasks(status);
CREATE INDEX idx_selection_tasks_created_at ON selection_tasks(created_at);
CREATE INDEX idx_trend_results_task_id ON trend_results(task_id);
CREATE INDEX idx_product_results_task_id ON product_results(task_id);
CREATE INDEX idx_review_results_task_id ON review_results(task_id);
CREATE INDEX idx_score_results_task_id ON score_results(task_id);
CREATE INDEX idx_reports_task_id ON reports(task_id);
```

## API 设计

### Health Check

```http
GET /api/v1/health
```

响应：

```json
{
  "status": "ok"
}
```

### 创建选品分析

```http
POST /api/v1/selections/analyze
```

请求：

```json
{
  "keyword": "智能手环",
  "country": "US"
}
```

响应：

```json
{
  "task_id": "uuid",
  "status": "completed",
  "report": "# 选品分析报告：智能手环"
}
```

### 查询分析任务

```http
GET /api/v1/selections/{task_id}
```

响应：

```json
{
  "task_id": "uuid",
  "keyword": "智能手环",
  "normalized_keyword": "smart fitness band",
  "status": "completed",
  "report": "# 选品分析报告：智能手环"
}
```

## 状态枚举

```text
pending
running
completed
failed
completed_with_warnings
```

## 评分模型

```text
opportunity_score =
  trend_score * 0.30
  + competition_opportunity_score * 0.25
  + pain_point_score * 0.25
  + profit_score * 0.20
```

说明：

- `competition_score` 表示竞争强度。
- `competition_opportunity_score = 100 - competition_score`。
- 评分必须输出 `score_detail`，解释每个分数来源。

## 验收标准

- 可以通过 FastAPI 创建一次选品分析任务。
- 输入“智能手环”时，系统能归一化关键词并完成全流程。
- 即使趋势、商品或评论某个数据源失败，系统也能输出带风险说明的报告。
- 所有真实密钥只来自 `.env`。
- API route 不直接调用 DeepSeek，不直接执行 SQL。
- 测试覆盖评分工具、报告降级逻辑和至少一个 Agent 工作流 happy path。
