from app.ai.schemas import SelectionReportInput
from app.schemas.selection import ReportDTO


class TemplateReportGenerationTool:
    """模板报告生成 Tool，用于 LLM 不可用时生成可读 Markdown 报告。"""

    def generate(self, report_input: SelectionReportInput) -> ReportDTO:
        """根据结构化分析结果生成基础 Markdown 报告。"""
        score = report_input.score_result.get("opportunity_score", "N/A")
        recommendation = self._recommendation_from_score(score)
        title = f"选品分析报告：{report_input.keyword}"
        markdown_content = (
            f"# {title}\n\n"
            "## 1. 结论摘要\n"
            f"- 机会评分：{score}\n"
            f"- 开发建议：{recommendation}\n"
            "- 报告定位：公开数据驱动的选品机会初筛。\n\n"
            "## 2. 市场趋势分析\n"
            f"{report_input.trend_result}\n\n"
            "## 3. 竞品分析\n"
            f"{report_input.product_result}\n\n"
            "## 4. 用户痛点分析\n"
            f"{report_input.review_result}\n\n"
            "## 5. 风险说明\n"
            "- 当前未使用付费 API，无法提供真实销量、BSR、广告竞价和真实毛利。\n"
            "- 利润潜力为启发式估算，开发前仍需验证供应链、合规和物流成本。\n"
        )
        return ReportDTO(
            title=title,
            markdown_content=markdown_content,
            summary=f"机会评分为 {score}，建议为 {recommendation}。",
            recommendation=recommendation,
        )

    @staticmethod
    def _recommendation_from_score(score: object) -> str:
        """根据机会评分生成保守开发建议。"""
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            return "cautiously_recommended"
        if numeric_score >= 75:
            return "recommended"
        if numeric_score >= 55:
            return "cautiously_recommended"
        return "not_recommended"

