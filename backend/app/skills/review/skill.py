from app.schemas.selection import ReviewResultDTO
from app.tools.review_analysis import ReviewAnalysisTool


class ReviewSkill:
    """评论分析 Skill，负责调用评论 Tool 分析用户痛点。"""

    def __init__(self, review_tool: ReviewAnalysisTool | None = None) -> None:
        self.review_tool = review_tool or ReviewAnalysisTool()

    def analyze(self, keyword: str, product_ids: list[str] | None = None, limit: int = 1000) -> ReviewResultDTO:
        """执行评论痛点分析并返回稳定 DTO。"""
        return self.review_tool.analyze(keyword=keyword, product_ids=product_ids, limit=limit)

