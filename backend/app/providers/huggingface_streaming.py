from collections.abc import Iterable
from typing import Any

from app.common.exceptions import BusinessException


class HuggingFaceStreamingProductProvider:
    """Hugging Face streaming 商品数据 Provider，预留 Amazon Reviews 2023 streaming 读取接口。"""

    def __init__(self, dataset_name: str = "McAuley-Lab/Amazon-Reviews-2023") -> None:
        self.dataset_name = dataset_name

    def iter_products(self, keyword: str, limit: int) -> Iterable[dict[str, Any]]:
        """按关键词流式读取商品 metadata。

        当前 MVP 不强制安装 `datasets`，如果本地未安装则返回可理解的业务异常。
        """
        try:
            from datasets import load_dataset
        except ImportError as exc:
            raise BusinessException(
                message="Hugging Face streaming 需要安装 datasets 依赖",
                code="DATASETS_DEPENDENCY_MISSING",
                http_status=500,
            ) from exc

        matched_count = 0
        dataset = load_dataset(self.dataset_name, "raw_meta_All_Beauty", split="full", streaming=True)
        for item in dataset:
            searchable_text = f"{item.get('title', '')} {item.get('description', '')}".lower()
            if keyword.lower() in searchable_text:
                yield dict(item)
                matched_count += 1
            if matched_count >= limit:
                break

