import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.schemas.selection import ReviewResultDTO


class ReviewAnalysisTool:
    """Amazon Reviews Tool，负责基于公开样本评论提取用户痛点。"""

    PAIN_POINT_KEYWORDS = {
        "battery": "续航不足",
        "charge": "充电体验差",
        "app": "APP体验差",
        "sync": "同步不稳定",
        "accuracy": "数据准确性不足",
        "screen": "屏幕体验差",
        "strap": "佩戴舒适度不足",
    }

    def __init__(self, sample_path: Path | None = None) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self.sample_path = sample_path or repo_root / "data" / "samples" / "reviews_sample.json"

    def analyze(self, keyword: str, product_ids: list[str] | None = None, limit: int = 1000) -> ReviewResultDTO:
        """分析评论情感、痛点和改进建议。"""
        reviews = self._load_reviews()[:limit]
        matched_reviews = [
            review for review in reviews if self._matches_review(review, keyword=keyword, product_ids=product_ids or [])
        ]
        if not matched_reviews:
            return self._empty_result()

        ratings = [float(review.get("rating", 0)) for review in matched_reviews if review.get("rating") is not None]
        positive_reviews = [review for review in matched_reviews if float(review.get("rating", 0)) >= 4]
        negative_reviews = [review for review in matched_reviews if float(review.get("rating", 0)) <= 3]
        pain_points = self._extract_pain_points(negative_reviews)

        return ReviewResultDTO(
            review_count=len(matched_reviews),
            positive_ratio=Decimal(str(round(len(positive_reviews) / len(matched_reviews), 4))),
            negative_ratio=Decimal(str(round(len(negative_reviews) / len(matched_reviews), 4))),
            sentiment_score=Decimal(str(round((sum(ratings) / len(ratings)) / 5 * 100, 2))) if ratings else None,
            pain_points=pain_points,
            improvements=self._build_improvements(pain_points),
            representative_reviews=negative_reviews[:5],
            data_source="amazon_reviews_2023_reviews_sample",
        )

    def _load_reviews(self) -> list[dict[str, Any]]:
        """读取本地评论样本，样本不存在时返回空列表。"""
        if not self.sample_path.exists():
            return []
        with self.sample_path.open("r", encoding="utf-8") as sample_file:
            payload = json.load(sample_file)
        return payload if isinstance(payload, list) else []

    @staticmethod
    def _matches_review(review: dict[str, Any], keyword: str, product_ids: list[str]) -> bool:
        """根据商品 ID 或关键词匹配评论。"""
        if product_ids and str(review.get("parent_asin") or review.get("asin")) in product_ids:
            return True

        tokens = [token for token in re.split(r"\W+", keyword.lower()) if token]
        searchable_text = f"{review.get('title', '')} {review.get('text', '')}".lower()
        return bool(tokens) and all(token in searchable_text for token in tokens)

    def _extract_pain_points(self, reviews: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """从低星评论中提取痛点关键词。"""
        counter: Counter[str] = Counter()
        evidence: dict[str, str] = {}
        for review in reviews:
            text = str(review.get("text") or "").lower()
            for keyword, pain_point in self.PAIN_POINT_KEYWORDS.items():
                if keyword in text:
                    counter[pain_point] += 1
                    evidence.setdefault(pain_point, str(review.get("text") or ""))

        return [
            {"name": pain_point, "count": count, "evidence": evidence.get(pain_point, "")}
            for pain_point, count in counter.most_common(10)
        ]

    @staticmethod
    def _build_improvements(pain_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """根据痛点生成基础产品改进建议。"""
        return [
            {"name": f"优化{pain_point['name']}", "reason": pain_point.get("evidence", "")}
            for pain_point in pain_points
        ]

    @staticmethod
    def _empty_result() -> ReviewResultDTO:
        """评论样本为空或未匹配时的稳定返回。"""
        return ReviewResultDTO(
            review_count=0,
            positive_ratio=Decimal("0.0000"),
            negative_ratio=Decimal("0.0000"),
            sentiment_score=None,
            pain_points=[],
            improvements=[],
            representative_reviews=[],
            data_source="amazon_reviews_2023_reviews_sample",
        )
