from collections.abc import Iterable
from typing import Protocol
from typing import Any


class ProductDataProvider(Protocol):
    """商品数据 Provider 协议，用于统一免费样本、streaming 和商业数据源。"""

    def iter_products(self, keyword: str, limit: int) -> Iterable[dict[str, Any]]:
        """按关键词返回商品数据迭代器。"""


class CommercialProductProvider(Protocol):
    """商业选品数据 Provider 协议，用于 Keepa、Amazon SP-API 和 SellerSprite 扩展。"""

    provider_name: str

    def fetch_product_signals(self, keyword: str, country: str) -> dict[str, Any]:
        """获取商业数据源提供的商品信号。"""
