from typing import Any

from pydantic import BaseModel, Field


class KeywordNormalizationResult(BaseModel):
    """关键词归一化结果，用于统一中文输入和英文数据检索词。"""

    normalized_keyword: str = Field(..., min_length=1, max_length=255, description="归一化后的英文关键词")
    detected_language: str = Field(..., min_length=2, max_length=20, description="模型识别出的原始语言")
    search_terms: list[str] = Field(default_factory=list, description="可用于趋势和商品检索的候选关键词")


class ReviewPainPointSummary(BaseModel):
    """评论痛点总结结果，用于把评论文本压缩成可执行的产品改进方向。"""

    pain_points: list[dict[str, Any]] = Field(default_factory=list, description="用户痛点列表")
    improvements: list[dict[str, Any]] = Field(default_factory=list, description="产品改进建议列表")
    sentiment_summary: str = Field(default="", description="评论整体情绪摘要")


class SelectionReportInput(BaseModel):
    """选品报告生成输入，用于约束报告节点可使用的数据边界。"""

    keyword: str = Field(..., description="用户输入的原始关键词")
    normalized_keyword: str = Field(..., description="归一化后的英文关键词")
    country: str = Field(default="US", description="目标站点国家代码")
    trend_result: dict[str, Any] = Field(default_factory=dict, description="趋势分析结果")
    product_result: dict[str, Any] = Field(default_factory=dict, description="商品分析结果")
    review_result: dict[str, Any] = Field(default_factory=dict, description="评论分析结果")
    score_result: dict[str, Any] = Field(default_factory=dict, description="评分结果")

