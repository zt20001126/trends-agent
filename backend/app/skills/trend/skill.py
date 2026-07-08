from app.schemas.selection import TrendResultDTO
from app.core.settings import settings
from app.tools.google_trend import GoogleTrendTool


class TrendSkill:
    """趋势分析 Skill，负责调用 Google Trends Tool 获取市场趋势。"""

    def __init__(self, trend_tool: GoogleTrendTool | None = None) -> None:
        self.trend_tool = trend_tool or GoogleTrendTool(enable_live=settings.google_trends_live)

    def analyze(self, keyword: str, country: str) -> TrendResultDTO:
        """执行趋势分析并返回稳定 DTO。"""
        return self.trend_tool.analyze(keyword=keyword, country=country)
