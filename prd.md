# AI跨境电商选品智能体 MVP PRD

## 产品概述

AI跨境电商选品智能体 MVP 面向跨境电商选品早期调研场景。用户输入一个商品关键词，系统自动调用趋势分析、竞品分析、评论痛点分析、机会评分和报告生成能力，输出 Markdown 格式的选品机会初筛报告。

本阶段不使用 Keepa、Amazon SP-API、SellerSprite、Jungle Scout 等付费数据源。系统优先使用 Google Trends、Amazon Reviews 2023 公开数据集和 DeepSeek API，帮助用户判断某个品类是否值得进一步人工验证。

## 用户角色

- 跨境电商卖家：希望快速判断某个商品关键词是否值得开发。
- 选品运营人员：希望批量或单次分析品类趋势、竞争、痛点和机会。
- 独立开发者/创业者：希望用免费或低成本数据源搭建选品分析工作流。

## 核心目标

- 输入商品关键词后自动生成选品报告。
- 默认分析美国站，国家代码为 `US`。
- 支持中文关键词输入，并归一化为适合 Google Trends 和 Amazon 数据检索的英文关键词。
- 使用 DeepSeek API 进行关键词归一化、痛点总结和报告生成。
- 使用 Docker PostgreSQL 保存任务、分析结果和报告。
- Amazon Reviews 2023 第一阶段使用小样本或按类目 streaming，不下载全量数据。
- 系统定位为选品机会初筛工具，不输出最终投资结论。

## 功能列表

### 1. 选品分析任务创建

- 用户通过 API 输入商品关键词。
- 系统创建分析任务。
- 系统记录任务状态、输入参数、错误信息和创建时间。

### 2. 关键词归一化

- 支持中文关键词，例如“智能手环”。
- 使用 DeepSeek 将关键词归一化为英文搜索词，例如 `smart fitness band`。
- 保留原始关键词和归一化关键词。

### 3. 趋势分析

- 默认使用 `pytrends` 获取 Google Trends 数据。
- 分析趋势热度、平均热度、峰值热度和增长率。
- 当 `pytrends` 不可用时，后续可使用 Google Trends CSV 或评论量时间序列作为降级数据源。

### 4. 商品竞品分析

- 使用 Amazon Reviews 2023 Product Metadata 小样本或 streaming 数据。
- 根据关键词匹配标题、描述、类目和品牌字段。
- 输出相关商品数量、品牌分布、类目分布、价格区间和竞争评分。

### 5. 评论痛点分析

- 使用 Amazon Reviews 2023 Reviews 小样本或 streaming 数据。
- 优先分析低星评论。
- 提取用户痛点、情绪倾向、代表性评论和产品改进建议。

### 6. 机会评分

- 根据市场趋势、竞争程度、用户痛点和利润潜力计算机会评分。
- 默认权重：
  - 趋势评分：30%
  - 竞争机会评分：25%
  - 痛点机会评分：25%
  - 利润潜力评分：20%

### 7. Markdown 报告生成

- 使用 DeepSeek API 生成 Markdown 报告。
- 报告包含市场分析、竞争分析、用户需求、产品机会、风险和开发建议。
- 当 LLM 调用失败时，系统可使用模板报告降级输出。

### 8. 历史任务查询

- 支持根据任务 ID 查询任务状态和最终报告。
- 支持后续扩展为任务列表、关键词缓存和重复分析复用。

## 用户流程

```text
用户输入关键词
  -> FastAPI 接收请求
  -> 创建 selection_task
  -> Agent 归一化关键词
  -> 趋势分析 Skill
  -> 商品分析 Skill
  -> 评论分析 Skill
  -> 选品评分 Skill
  -> 报告生成 Skill
  -> 保存结果
  -> 返回 Markdown 报告
```

## 页面/模块结构

MVP 第一阶段以 API 为主，不强制开发前端页面。

### API 模块

- 健康检查接口
- 创建选品分析接口
- 查询选品任务接口

### Agent 模块

- LangGraph 工作流
- Agent 状态定义
- Skill Router
- 任务规划节点

### Skill 模块

- 趋势分析 Skill
- 商品分析 Skill
- 评论分析 Skill
- 评分 Skill
- 报告 Skill

### Tool 模块

- Google Trends Tool
- Amazon Product Metadata Tool
- Amazon Review Analysis Tool
- Opportunity Score Tool
- Report Generation Tool

### 数据库模块

- SQLAlchemy ORM 模型
- Repository 层
- Alembic migration
- PostgreSQL Docker 配置

## 非功能需求

### 性能

- MVP 单次分析允许同步执行，目标响应时间控制在 30 到 120 秒。
- 长耗时任务后续可扩展为异步队列。
- Amazon 数据读取必须限制样本量，避免首次运行阻塞过久。

### 安全

- DeepSeek API Key 只能通过 `.env` 注入。
- 不允许在代码、文档示例或日志中写入真实 API Key。
- API route 不直接调用 LLM，不直接访问数据库细节。

### 可扩展性

- Tool 和 Skill 解耦，后续可替换或新增 Keepa、Amazon SP-API、SellerSprite 等商业数据源。
- LLM Client 封装为独立 AI 边界，不绑定具体供应商。
- 数据源 Provider 应支持免费数据源和商业数据源并存。

### 可维护性

- FastAPI route 只负责请求响应编排。
- 业务逻辑放在 Service / Skill / Agent 层。
- ORM Model、Pydantic Schema、业务 DTO 分离。
- 配置项集中放在 Settings，不硬编码魔法值。

### 数据限制声明

- 本系统不提供真实销量、BSR、广告竞价、FBA 费用和真实毛利。
- 利润潜力为启发式估算，不能作为最终商业投资结论。
- 报告结论只用于选品初筛，最终开发前仍需人工验证供应链、合规、物流和竞品实时数据。
