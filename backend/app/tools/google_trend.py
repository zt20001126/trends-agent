from decimal import Decimal
from typing import Any

import pandas as pd

from app.schemas.selection import TrendResultDTO


class GoogleTrendTool:
    """Google Trends Tool，负责获取关键词趋势并计算趋势评分。"""

    def __init__(self, enable_live: bool = True) -> None:
        self.enable_live = enable_live
        self._cache: dict[tuple[str, str], TrendResultDTO] = {}

    def analyze(self, keyword: str, country: str) -> TrendResultDTO:
        """分析关键词趋势，失败时返回中性降级结果。"""
        cache_key = (keyword.lower().strip(), country.upper().strip())
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.enable_live:
            result = self._fallback_result(keyword=keyword, country=country)
            self._cache[cache_key] = result
            return result

        try:
            interest_df, related_queries = self._fetch_live_trends(keyword=keyword, country=country)
            result = self._build_result(keyword=keyword, country=country, interest_df=interest_df, related_queries=related_queries)
        except Exception:
            # pytrends 是非官方接口，网络、限流或 Google 页面变更都可能导致失败。
            result = self._fallback_result(keyword=keyword, country=country)
        self._cache[cache_key] = result
        return result

    def _fetch_live_trends(self, keyword: str, country: str) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
        """调用 pytrends 获取实时趋势数据。"""
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([keyword], timeframe="today 12-m", geo=country)
        interest_df = pytrends.interest_over_time()
        related_payload = pytrends.related_queries().get(keyword, {})
        related_queries = self._normalize_related_queries(related_payload)
        return interest_df, related_queries

    def _build_result(
        self,
        keyword: str,
        country: str,
        interest_df: pd.DataFrame,
        related_queries: list[dict[str, Any]],
    ) -> TrendResultDTO:
        """根据趋势时间序列计算平均热度、峰值热度、增长率和趋势评分。"""
        if interest_df.empty or keyword not in interest_df:
            return self._fallback_result(keyword=keyword, country=country)

        values = [float(value) for value in interest_df[keyword].fillna(0).tolist()]
        avg_interest = sum(values) / len(values)
        peak_interest = max(values)
        first_window = values[: max(1, len(values) // 4)]
        last_window = values[-max(1, len(values) // 4) :]
        first_avg = sum(first_window) / len(first_window)
        last_avg = sum(last_window) / len(last_window)
        growth_rate = (last_avg - first_avg) / max(first_avg, 1)
        trend_score = min(100, max(0, avg_interest * 0.6 + peak_interest * 0.2 + max(growth_rate, 0) * 100 * 0.2))

        trend_series = [
            {"date": str(index.date()), "interest": float(row[keyword])}
            for index, row in interest_df.iterrows()
            if "isPartial" not in row or not bool(row.get("isPartial"))
        ]

        return TrendResultDTO(
            keyword=keyword,
            country=country,
            trend_score=Decimal(str(round(trend_score, 2))),
            growth_rate=Decimal(str(round(growth_rate, 4))),
            avg_interest=Decimal(str(round(avg_interest, 2))),
            peak_interest=Decimal(str(round(peak_interest, 2))),
            trend_series=trend_series,
            related_queries=related_queries,
            data_source="pytrends",
        )

    @staticmethod
    def _normalize_related_queries(related_payload: dict[str, Any]) -> list[dict[str, Any]]:
        """将 pytrends 相关查询结果转换为稳定结构。"""
        related_queries: list[dict[str, Any]] = []
        for query_type in ("top", "rising"):
            query_df = related_payload.get(query_type)
            if query_df is None:
                continue
            for row in query_df.head(10).to_dict(orient="records"):
                related_queries.append({"type": query_type, "query": row.get("query"), "value": row.get("value")})
        return related_queries

    @staticmethod
    def _fallback_result(keyword: str, country: str) -> TrendResultDTO:
        """趋势数据失败降级结果，使用中性分并保留数据来源。"""
        return TrendResultDTO(
            keyword=keyword,
            country=country,
            trend_score=Decimal("50.00"),
            growth_rate=Decimal("0.0000"),
            avg_interest=Decimal("50.00"),
            peak_interest=Decimal("50.00"),
            trend_series=[],
            related_queries=[],
            data_source="pytrends_fallback",
        )
