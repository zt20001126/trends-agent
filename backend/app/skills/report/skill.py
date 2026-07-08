from app.ai.schemas import SelectionReportInput
from app.common.exceptions import BusinessException
from app.schemas.selection import ReportDTO
from app.tools.llm_report_generation import DeepSeekReportGenerationTool
from app.tools.report_generation import TemplateReportGenerationTool


class ReportSkill:
    """报告生成 Skill，负责优先使用 DeepSeek 报告 Tool，并在失败时降级模板报告。"""

    def __init__(
        self,
        llm_report_tool: DeepSeekReportGenerationTool | None = None,
        template_report_tool: TemplateReportGenerationTool | None = None,
    ) -> None:
        self.llm_report_tool = llm_report_tool or DeepSeekReportGenerationTool()
        self.template_report_tool = template_report_tool or TemplateReportGenerationTool()

    def generate(self, report_input: SelectionReportInput) -> ReportDTO:
        """生成选品报告。

        Step 1: 优先通过 DeepSeek 生成自然语言报告。
        Step 2: 当 DeepSeek 未配置、调用失败或解析失败时，降级为模板报告。
        Step 3: 强制补充数据限制和风险声明，避免报告遗漏关键边界。
        """
        try:
            report = self.llm_report_tool.generate(report_input)
        except BusinessException:
            report = self.template_report_tool.generate(report_input)
        return self._ensure_risk_notice(report)

    @staticmethod
    def _ensure_risk_notice(report: ReportDTO) -> ReportDTO:
        """确保报告包含公开数据限制和风险说明。"""
        required_notice = (
            "\n\n## 数据限制与风险说明\n"
            "- 当前未使用付费 API，无法提供真实销量、BSR、广告竞价和真实毛利。\n"
            "- 利润潜力为启发式估算，开发前仍需验证供应链、合规和物流成本。\n"
        )
        if "未使用付费 API" in report.markdown_content and ("风险说明" in report.markdown_content or "数据限制" in report.markdown_content):
            return report
        return report.model_copy(update={"markdown_content": report.markdown_content + required_notice})
