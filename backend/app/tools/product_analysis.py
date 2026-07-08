import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path
from statistics import mean, median
from typing import Any

from app.schemas.selection import ProductResultDTO


class ProductAnalysisTool:
    """Amazon 商品 Metadata Tool，负责基于公开样本数据分析竞品结构。"""

    def __init__(self, sample_path: Path | None = None) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self.sample_path = sample_path or repo_root / "data" / "samples" / "products_sample.json"

    def analyze(self, keyword: str, limit: int = 500) -> ProductResultDTO:
        """根据关键词匹配商品样本并输出竞品统计。"""
        products = self._load_products()[:limit]
        matched_products = [product for product in products if self._matches_keyword(product, keyword)]
        prices = [float(product["price"]) for product in matched_products if self._is_valid_price(product.get("price"))]

        brand_distribution = Counter(str(product.get("brand") or "Unknown") for product in matched_products)
        category_distribution = Counter(self._category_name(product.get("categories")) for product in matched_products)
        competition_score = self._calculate_competition_score(
            matched_count=len(matched_products),
            brand_count=len(brand_distribution),
            category_count=len(category_distribution),
        )

        return ProductResultDTO(
            matched_product_count=len(matched_products),
            brand_distribution=dict(brand_distribution.most_common(10)),
            category_distribution=dict(category_distribution.most_common(10)),
            price_min=Decimal(str(round(min(prices), 2))) if prices else None,
            price_max=Decimal(str(round(max(prices), 2))) if prices else None,
            price_median=Decimal(str(round(median(prices), 2))) if prices else None,
            price_avg=Decimal(str(round(mean(prices), 2))) if prices else None,
            competition_score=Decimal(str(round(competition_score, 2))),
            sample_products=matched_products[:10],
            data_source="amazon_reviews_2023_metadata_sample",
        )

    def _load_products(self) -> list[dict[str, Any]]:
        """读取本地商品样本，样本不存在时返回空列表。"""
        if not self.sample_path.exists():
            return []
        with self.sample_path.open("r", encoding="utf-8") as sample_file:
            payload = json.load(sample_file)
        return payload if isinstance(payload, list) else []

    @staticmethod
    def _matches_keyword(product: dict[str, Any], keyword: str) -> bool:
        """基于标题、描述、类目和品牌做轻量关键词匹配。"""
        tokens = [token for token in re.split(r"\W+", keyword.lower()) if token]
        searchable_text = " ".join(
            [
                str(product.get("title") or ""),
                str(product.get("description") or ""),
                str(product.get("brand") or ""),
                " ".join(product.get("categories") or []),
            ]
        ).lower()
        return bool(tokens) and all(token in searchable_text for token in tokens)

    @staticmethod
    def _is_valid_price(price: Any) -> bool:
        """判断价格是否可用于数值统计。"""
        return isinstance(price, int | float) and price >= 0

    @staticmethod
    def _category_name(categories: Any) -> str:
        """提取最细类目名称。"""
        if isinstance(categories, list) and categories:
            return str(categories[-1])
        return "Unknown"

    @staticmethod
    def _calculate_competition_score(matched_count: int, brand_count: int, category_count: int) -> float:
        """计算竞争强度评分，分数越高代表竞争越强。"""
        volume_score = min(70, matched_count * 2)
        brand_score = min(20, brand_count * 2)
        category_score = min(10, category_count * 2)
        return min(100, volume_score + brand_score + category_score)

