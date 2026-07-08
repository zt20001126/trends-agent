from decimal import Decimal

from app.ai.schemas import SelectionReportInput
from app.schemas.selection import ProductResultDTO, ReviewResultDTO, TrendResultDTO
from app.tools.google_trend import GoogleTrendTool
from app.tools.product_analysis import ProductAnalysisTool
from app.tools.report_generation import TemplateReportGenerationTool
from app.tools.review_analysis import ReviewAnalysisTool
from app.tools.scoring import OpportunityScoreTool


def test_google_trend_tool_returns_fallback_when_live_disabled() -> None:
    """验证 Google Trends Tool 可以稳定返回降级结果。"""
    result = GoogleTrendTool(enable_live=False).analyze(keyword="smart fitness band", country="US")

    assert result.trend_score == Decimal("50.00")
    assert result.data_source == "pytrends_fallback"


def test_product_analysis_tool_reads_sample_products() -> None:
    """验证商品分析 Tool 可以从样本中统计竞品信息。"""
    result = ProductAnalysisTool().analyze(keyword="smart fitness band")

    assert result.matched_product_count == 2
    assert result.price_median == Decimal("44.99")
    assert result.brand_distribution["FitNova"] == 1


def test_review_analysis_tool_extracts_pain_points() -> None:
    """验证评论分析 Tool 可以从低星评论中提取痛点。"""
    result = ReviewAnalysisTool().analyze(keyword="smart fitness band")

    assert result.review_count == 3
    assert any(pain_point["name"] == "续航不足" for pain_point in result.pain_points)
    assert any(pain_point["name"] == "APP体验差" for pain_point in result.pain_points)


def test_opportunity_score_tool_reverses_competition_score() -> None:
    """验证评分 Tool 会将竞争强度反向转换为竞争机会分。"""
    trend_result = TrendResultDTO(keyword="smart fitness band", country="US", trend_score=Decimal("80"), data_source="test")
    product_result = ProductResultDTO(
        matched_product_count=10,
        competition_score=Decimal("60"),
        price_median=Decimal("49.99"),
        data_source="test",
    )
    review_result = ReviewResultDTO(
        review_count=10,
        negative_ratio=Decimal("0.30"),
        pain_points=[{"name": "续航不足"}],
        data_source="test",
    )

    result = OpportunityScoreTool().calculate(trend_result, product_result, review_result)

    assert result.competition_score == Decimal("40.00")
    assert result.opportunity_score == Decimal("57.50")


def test_template_report_generation_tool_builds_markdown() -> None:
    """验证模板报告 Tool 可以在无 LLM 时生成 Markdown 报告。"""
    report_input = SelectionReportInput(
        keyword="智能手环",
        normalized_keyword="smart fitness band",
        score_result={"opportunity_score": 66.5},
    )

    result = TemplateReportGenerationTool().generate(report_input)

    assert result.title == "选品分析报告：智能手环"
    assert "# 选品分析报告：智能手环" in result.markdown_content
