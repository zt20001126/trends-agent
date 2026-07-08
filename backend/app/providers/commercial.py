from typing import Any

from app.common.exceptions import BusinessException


class BaseCommercialProvider:
    """商业数据源 Provider 基类，定义付费数据源接入边界。"""

    provider_name = "commercial"

    def fetch_product_signals(self, keyword: str, country: str) -> dict[str, Any]:
        """获取商业数据源信号，未配置时返回明确异常。"""
        raise BusinessException(
            message=f"{self.provider_name} Provider 尚未配置",
            code="COMMERCIAL_PROVIDER_NOT_CONFIGURED",
            http_status=501,
        )


class KeepaProvider(BaseCommercialProvider):
    """Keepa Provider 设计占位，用于后续接入价格、BSR 和历史销量代理信号。"""

    provider_name = "keepa"


class AmazonSpApiProvider(BaseCommercialProvider):
    """Amazon SP-API Provider 设计占位，用于后续接入授权店铺和商品数据。"""

    provider_name = "amazon_sp_api"


class SellerSpriteProvider(BaseCommercialProvider):
    """SellerSprite Provider 设计占位，用于后续接入关键词、竞争和选品指标。"""

    provider_name = "seller_sprite"

