# AI跨境电商选品智能体 MVP TODO

## 0. 工程初始化

- [ ] 确认当前目录是否需要初始化 git 仓库。
- [ ] 创建 Python 项目基础结构。
- [ ] 创建 `backend/app` 分层目录。
- [ ] 创建 `.env.example`，包含 DeepSeek 和 PostgreSQL 配置示例。
- [ ] 创建 `.gitignore`，排除 `.env`、缓存、虚拟环境、数据大文件。
- [ ] 确认 Anaconda `hooks` 环境可用。

## 1. Docker PostgreSQL

- [ ] 创建 `docker-compose.yml`。
- [ ] 配置 PostgreSQL 服务名、数据库、用户、密码和端口。
- [ ] 使用数据库名 `trends_agent`。
- [ ] 使用用户名 `trends_agent`。
- [ ] 使用默认端口 `5432`。
- [ ] 验证 PostgreSQL 容器可以启动。
- [ ] 验证本机可以连接 `trends_agent` 数据库。

## 2. 后端基础设施

- [ ] 创建 FastAPI 应用入口。
- [ ] 创建 `/api/v1/health` 接口。
- [ ] 创建 Settings 配置类。
- [ ] 创建统一异常类。
- [ ] 创建统一响应结构。
- [ ] 配置基础日志。

## 3. 数据库与 ORM

- [ ] 安装 SQLAlchemy 2.x、psycopg、Alembic。
- [ ] 创建数据库连接 session。
- [ ] 创建 SQLAlchemy Base。
- [ ] 创建 `SelectionTask` ORM 模型。
- [ ] 创建 `TrendResult` ORM 模型。
- [ ] 创建 `ProductResult` ORM 模型。
- [ ] 创建 `ReviewResult` ORM 模型。
- [ ] 创建 `ScoreResult` ORM 模型。
- [ ] 创建 `Report` ORM 模型。
- [ ] 初始化 Alembic。
- [ ] 生成第一版 migration。
- [ ] 执行 migration 创建表。

## 4. Schema 与 Repository

- [ ] 创建选品分析请求 schema。
- [ ] 创建选品分析响应 schema。
- [ ] 创建任务详情响应 schema。
- [ ] 创建分析结果 DTO。
- [ ] 创建 Selection Repository。
- [ ] 实现任务创建方法。
- [ ] 实现任务状态更新方法。
- [ ] 实现分析结果保存方法。
- [ ] 实现任务详情查询方法。

## 5. DeepSeek AI 边界

- [ ] 创建 DeepSeek Client。
- [ ] 从 `.env` 读取 `DEEPSEEK_API_KEY`。
- [ ] 从 `.env` 读取 `DEEPSEEK_BASE_URL`。
- [ ] 从 `.env` 读取 `DEEPSEEK_MODEL`。
- [ ] 实现关键词归一化方法。
- [ ] 实现痛点总结方法。
- [ ] 实现报告生成方法。
- [ ] 增加 LLM 调用失败异常处理。
- [ ] 确保 API route 不直接调用 DeepSeek Client。

## 6. Tool 层

- [ ] 实现 Google Trends Tool。
- [ ] 为 Google Trends Tool 增加缓存和失败返回。
- [ ] 实现 Amazon Product Metadata Tool。
- [ ] 支持从 `data/samples` 读取小样本。
- [ ] 预留 Hugging Face streaming 数据读取接口。
- [ ] 实现 Review Analysis Tool。
- [ ] 支持低星评论筛选。
- [ ] 支持痛点关键词提取。
- [ ] 实现 Opportunity Score Tool。
- [ ] 实现模板 Report Generation Tool。

## 7. Skill 层

- [ ] 实现 Trend Skill。
- [ ] 实现 Product Skill。
- [ ] 实现 Review Skill。
- [ ] 实现 Scoring Skill。
- [ ] 实现 Report Skill。
- [ ] 确保 Skill 只组合 Tool，不直接处理 API 请求。
- [ ] 确保 Tool 输出结构稳定，方便测试。

## 8. LangGraph Agent

- [ ] 创建 SelectionState。
- [ ] 创建关键词归一化节点。
- [ ] 创建任务规划节点。
- [ ] 创建趋势分析节点。
- [ ] 创建商品分析节点。
- [ ] 创建评论分析节点。
- [ ] 创建评分节点。
- [ ] 创建报告生成节点。
- [ ] 创建结果持久化节点。
- [ ] 实现失败降级和错误收集。
- [ ] 实现 Agent 工作流 happy path 测试。

## 9. API 接口

- [ ] 实现 `POST /api/v1/selections/analyze`。
- [ ] 实现 `GET /api/v1/selections/{task_id}`。
- [ ] 在 Service 层调用 Agent。
- [ ] API route 只做参数接收和响应返回。
- [ ] 返回 Markdown 报告。

## 10. 测试

- [ ] 测试 Opportunity Score Tool 权重计算。
- [ ] 测试竞争评分反向转换。
- [ ] 测试报告模板降级。
- [ ] 测试 Repository 创建和查询。
- [ ] 测试 Health Check。
- [ ] 测试选品分析接口 happy path。
- [ ] 测试 pytrends 失败时仍可生成报告。

## 11. 数据样本

- [ ] 确定 Amazon Reviews 2023 使用的第一批类目。
- [ ] 准备 metadata 小样本。
- [ ] 准备 reviews 小样本。
- [ ] 编写样本数据格式说明。
- [ ] 避免提交大体积数据文件。

## 12. 本地运行验证

- [ ] 启动 Docker PostgreSQL。
- [ ] 执行 Alembic migration。
- [ ] 启动 FastAPI。
- [ ] 使用关键词“智能手环”跑完整流程。
- [ ] 使用关键词“portable blender”跑完整流程。
- [ ] 使用关键词“dog water bottle”跑完整流程。
- [ ] 检查报告是否包含数据限制和风险说明。

## 13. 后续扩展

- [ ] 设计 Keepa Provider 接口。
- [ ] 设计 Amazon SP-API Provider 接口。
- [ ] 设计 SellerSprite Provider 接口。
- [ ] 支持异步任务队列。
- [ ] 支持报告历史列表。
- [ ] 支持批量关键词分析。
- [ ] 支持前端页面展示。
