from app.schemas.selection import ProductResultDTO, ReviewResultDTO, ScoreResultDTO, TrendResultDTO
from app.tools.scoring import OpportunityScoreTool


class ScoringSkill:
    """选品评分 Skill，负责组合趋势、商品和评论结果计算机会分。"""

    def __init__(self, score_tool: OpportunityScoreTool | None = None) -> None:
        self.score_tool = score_tool or OpportunityScoreTool()

    def calculate(
        self,
        trend_result: TrendResultDTO,
        product_result: ProductResultDTO,
        review_result: ReviewResultDTO,
    ) -> ScoreResultDTO:
        """执行选品机会评分并返回稳定 DTO。"""
        return self.score_tool.calculate(
            trend_result=trend_result,
            product_result=product_result,
            review_result=review_result,
        )

