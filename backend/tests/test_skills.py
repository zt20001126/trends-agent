from decimal import Decimal

from app.ai.schemas import SelectionReportInput
from app.common.exceptions import BusinessException
from app.schemas.selection import ReportDTO
from app.skills.product.skill import ProductSkill
from app.skills.report.skill import ReportSkill
from app.skills.review.skill import ReviewSkill
from app.skills.scoring.skill import ScoringSkill
from app.skills.trend.skill import TrendSkill
from app.tools.google_trend import GoogleTrendTool


class FailingReportTool:
    """测试用失败报告 Tool，用于验证模板降级。"""

    def generate(self, report_input: SelectionReportInput) -> ReportDTO:
        raise BusinessException(message="failed")


class RisklessReportTool:
    """测试用报告 Tool，用于验证风险声明兜底。"""

    def generate(self, report_input: SelectionReportInput) -> ReportDTO:
        return ReportDTO(
            title="测试报告",
            markdown_content="# 测试报告",
            summary="测试",
            recommendation="recommended",
        )


def test_analysis_skills_call_tools_and_return_dtos() -> None:
    """验证趋势、商品、评论和评分 Skill 可以串联基础 Tool。"""
    trend_result = TrendSkill(trend_tool=GoogleTrendTool(enable_live=False)).analyze("smart fitness band", "US")
    product_result = ProductSkill().analyze("smart fitness band")
    review_result = ReviewSkill().analyze("smart fitness band")
    score_result = ScoringSkill().calculate(trend_result, product_result, review_result)

    assert trend_result.data_source == "pytrends_fallback"
    assert product_result.matched_product_count == 2
    assert review_result.review_count == 3
    assert score_result.opportunity_score is not None


def test_report_skill_falls_back_to_template_report() -> None:
    """验证 DeepSeek 报告失败时 Report Skill 会降级为模板报告。"""
    report_input = SelectionReportInput(
        keyword="智能手环",
        normalized_keyword="smart fitness band",
        score_result={"opportunity_score": Decimal("66.50")},
    )

    result = ReportSkill(llm_report_tool=FailingReportTool()).generate(report_input)

    assert result.title == "选品分析报告：智能手环"
    assert result.recommendation == "cautiously_recommended"


def test_report_skill_ensures_risk_notice() -> None:
    """验证 LLM 报告遗漏风险声明时会被强制补齐。"""
    report_input = SelectionReportInput(keyword="portable blender", normalized_keyword="portable blender")

    result = ReportSkill(llm_report_tool=RisklessReportTool()).generate(report_input)

    assert "未使用付费 API" in result.markdown_content
    assert "风险说明" in result.markdown_content
