from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import SelectionTaskStatus


class SelectionAnalyzeRequest(BaseModel):
    """选品分析请求，用于接收用户输入的商品关键词和目标站点。"""

    keyword: str = Field(..., min_length=1, max_length=255, description="用户输入的商品关键词")
    country: str = Field(default="US", min_length=2, max_length=10, description="目标站点国家代码")
    language: str = Field(default="zh-CN", min_length=2, max_length=20, description="用户输入语言")


class SelectionAnalyzeResponse(BaseModel):
    """选品分析响应，用于返回任务 ID、状态和 Markdown 报告。"""

    task_id: UUID = Field(..., description="选品分析任务 ID")
    status: SelectionTaskStatus = Field(..., description="选品分析任务状态")
    report: str | None = Field(default=None, description="Markdown 格式选品报告")


class SelectionTaskResponse(BaseModel):
    """选品任务响应，用于返回任务基础信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="选品分析任务 ID")
    keyword: str = Field(..., description="用户输入的原始商品关键词")
    normalized_keyword: str | None = Field(default=None, description="归一化后的英文关键词")
    country: str = Field(..., description="目标站点国家代码")
    language: str = Field(..., description="用户输入语言")
    status: SelectionTaskStatus = Field(..., description="任务状态")
    error_message: str | None = Field(default=None, description="错误信息")
    created_at: datetime = Field(..., description="任务创建时间")
    updated_at: datetime = Field(..., description="任务更新时间")


class TrendResultDTO(BaseModel):
    """趋势分析结果 DTO，用于在 Service、Repository 和 Agent 之间传递趋势数据。"""

    keyword: str = Field(..., description="用于趋势分析的关键词")
    country: str = Field(..., description="趋势分析国家代码")
    trend_score: Decimal | None = Field(default=None, ge=0, le=100, description="趋势评分")
    growth_rate: Decimal | None = Field(default=None, description="趋势增长率")
    avg_interest: Decimal | None = Field(default=None, ge=0, le=100, description="平均搜索热度")
    peak_interest: Decimal | None = Field(default=None, ge=0, le=100, description="峰值搜索热度")
    trend_series: list[dict[str, Any]] = Field(default_factory=list, description="趋势时间序列")
    related_queries: list[dict[str, Any]] = Field(default_factory=list, description="相关查询词")
    data_source: str = Field(..., max_length=50, description="趋势数据来源")


class ProductResultDTO(BaseModel):
    """商品分析结果 DTO，用于传递竞品数量、品牌、类目和价格统计。"""

    matched_product_count: int = Field(default=0, ge=0, description="匹配到的商品数量")
    brand_distribution: dict[str, Any] = Field(default_factory=dict, description="品牌分布统计")
    category_distribution: dict[str, Any] = Field(default_factory=dict, description="类目分布统计")
    price_min: Decimal | None = Field(default=None, ge=0, description="最低价格")
    price_max: Decimal | None = Field(default=None, ge=0, description="最高价格")
    price_median: Decimal | None = Field(default=None, ge=0, description="价格中位数")
    price_avg: Decimal | None = Field(default=None, ge=0, description="平均价格")
    competition_score: Decimal | None = Field(default=None, ge=0, le=100, description="竞争强度评分")
    sample_products: list[dict[str, Any]] = Field(default_factory=list, description="样例商品列表")
    data_source: str = Field(..., max_length=50, description="商品数据来源")


class ReviewResultDTO(BaseModel):
    """评论分析结果 DTO，用于传递情感、痛点和改进建议。"""

    review_count: int = Field(default=0, ge=0, description="参与分析的评论数量")
    positive_ratio: Decimal | None = Field(default=None, ge=0, le=1, description="正面评论比例")
    negative_ratio: Decimal | None = Field(default=None, ge=0, le=1, description="负面评论比例")
    sentiment_score: Decimal | None = Field(default=None, ge=0, le=100, description="情感评分")
    pain_points: list[dict[str, Any]] = Field(default_factory=list, description="用户痛点列表")
    improvements: list[dict[str, Any]] = Field(default_factory=list, description="产品改进建议列表")
    representative_reviews: list[dict[str, Any]] = Field(default_factory=list, description="代表性评论列表")
    data_source: str = Field(..., max_length=50, description="评论数据来源")


class ScoreResultDTO(BaseModel):
    """评分结果 DTO，用于传递四维评分和综合机会分。"""

    trend_score: Decimal | None = Field(default=None, ge=0, le=100, description="趋势评分")
    competition_score: Decimal | None = Field(default=None, ge=0, le=100, description="竞争机会评分")
    pain_point_score: Decimal | None = Field(default=None, ge=0, le=100, description="痛点机会评分")
    profit_score: Decimal | None = Field(default=None, ge=0, le=100, description="利润潜力评分")
    opportunity_score: Decimal | None = Field(default=None, ge=0, le=100, description="综合机会评分")
    score_detail: dict[str, Any] = Field(default_factory=dict, description="评分明细")


class ReportDTO(BaseModel):
    """报告结果 DTO，用于传递最终 Markdown 报告和摘要。"""

    title: str = Field(..., min_length=1, max_length=255, description="报告标题")
    markdown_content: str = Field(..., min_length=1, description="Markdown 格式报告正文")
    summary: str | None = Field(default=None, description="报告摘要")
    recommendation: str | None = Field(default=None, max_length=50, description="开发建议枚举值")


class SelectionTaskDetailResponse(BaseModel):
    """选品任务详情响应，用于聚合任务、分析结果和报告。"""

    task: SelectionTaskResponse = Field(..., description="任务基础信息")
    trend_result: dict[str, Any] | None = Field(default=None, description="趋势分析结果")
    product_result: dict[str, Any] | None = Field(default=None, description="商品分析结果")
    review_result: dict[str, Any] | None = Field(default=None, description="评论分析结果")
    score_result: dict[str, Any] | None = Field(default=None, description="评分结果")
    report: dict[str, Any] | None = Field(default=None, description="报告结果")

