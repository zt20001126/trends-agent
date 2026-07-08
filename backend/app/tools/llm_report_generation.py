from app.ai.clients.deepseek_client import DeepSeekClient
from app.ai.schemas import SelectionReportInput
from app.schemas.selection import ReportDTO


class DeepSeekReportGenerationTool:
    """DeepSeek 报告生成 Tool，负责通过 AI 客户端生成 Markdown 选品报告。"""

    def __init__(self, deepseek_client: DeepSeekClient | None = None) -> None:
        self.deepseek_client = deepseek_client or DeepSeekClient()

    def generate(self, report_input: SelectionReportInput) -> ReportDTO:
        """调用 DeepSeek 生成报告，模型调用细节由 AI 客户端封装。"""
        return self.deepseek_client.generate_selection_report(report_input)

