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
        """
        try:
            return self.llm_report_tool.generate(report_input)
        except BusinessException:
            return self.template_report_tool.generate(report_input)

