from decimal import Decimal

from app.schemas.selection import ProductResultDTO, ReviewResultDTO, ScoreResultDTO, TrendResultDTO


class OpportunityScoreTool:
    """选品评分 Tool，基于趋势、竞争、痛点和利润潜力计算机会分。"""

    TREND_WEIGHT = Decimal("0.30")
    COMPETITION_WEIGHT = Decimal("0.25")
    PAIN_POINT_WEIGHT = Decimal("0.25")
    PROFIT_WEIGHT = Decimal("0.20")

    def calculate(
        self,
        trend_result: TrendResultDTO,
        product_result: ProductResultDTO,
        review_result: ReviewResultDTO,
    ) -> ScoreResultDTO:
        """计算选品机会评分。"""
        trend_score = self._score_or_neutral(trend_result.trend_score)
        competition_opportunity_score = Decimal("100.00") - self._score_or_neutral(product_result.competition_score)
        pain_point_score = self._calculate_pain_point_score(review_result)
        profit_score = self._calculate_profit_score(product_result)
        opportunity_score = (
            trend_score * self.TREND_WEIGHT
            + competition_opportunity_score * self.COMPETITION_WEIGHT
            + pain_point_score * self.PAIN_POINT_WEIGHT
            + profit_score * self.PROFIT_WEIGHT
        )

        return ScoreResultDTO(
            trend_score=self._round_score(trend_score),
            competition_score=self._round_score(competition_opportunity_score),
            pain_point_score=self._round_score(pain_point_score),
            profit_score=self._round_score(profit_score),
            opportunity_score=self._round_score(opportunity_score),
            score_detail={
                "weights": {
                    "trend": float(self.TREND_WEIGHT),
                    "competition": float(self.COMPETITION_WEIGHT),
                    "pain_point": float(self.PAIN_POINT_WEIGHT),
                    "profit": float(self.PROFIT_WEIGHT),
                },
                "note": "competition_score 已从竞争强度反向转换为竞争机会分。",
            },
        )

    @staticmethod
    def _calculate_pain_point_score(review_result: ReviewResultDTO) -> Decimal:
        """根据负面比例和痛点数量估算改进机会。"""
        negative_ratio = review_result.negative_ratio or Decimal("0")
        pain_count_score = min(Decimal("40"), Decimal(len(review_result.pain_points)) * Decimal("8"))
        negative_score = min(Decimal("60"), negative_ratio * Decimal("100"))
        return pain_count_score + negative_score

    @staticmethod
    def _calculate_profit_score(product_result: ProductResultDTO) -> Decimal:
        """基于价格中位数做启发式利润潜力估算。"""
        price_median = product_result.price_median
        if price_median is None:
            return Decimal("50.00")
        if price_median < Decimal("20"):
            return Decimal("45.00")
        if price_median <= Decimal("80"):
            return Decimal("70.00")
        if price_median <= Decimal("200"):
            return Decimal("60.00")
        return Decimal("40.00")

    @staticmethod
    def _score_or_neutral(score: Decimal | None) -> Decimal:
        """空分数使用中性分，保证评分链路稳定。"""
        return score if score is not None else Decimal("50.00")

    @staticmethod
    def _round_score(score: Decimal) -> Decimal:
        """统一分数精度。"""
        return score.quantize(Decimal("0.01"))

