from app.schemas.selection import ProductResultDTO
from app.tools.product_analysis import ProductAnalysisTool


class ProductSkill:
    """商品分析 Skill，负责调用商品 Metadata Tool 分析竞品结构。"""

    def __init__(self, product_tool: ProductAnalysisTool | None = None) -> None:
        self.product_tool = product_tool or ProductAnalysisTool()

    def analyze(self, keyword: str, limit: int = 500) -> ProductResultDTO:
        """执行商品竞品分析并返回稳定 DTO。"""
        return self.product_tool.analyze(keyword=keyword, limit=limit)

