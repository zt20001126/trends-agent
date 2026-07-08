import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductResult(Base):
    """商品竞品分析结果持久化模型，用于保存商品数量、品牌、类目和价格统计。"""

    __tablename__ = "product_results"
    __table_args__ = (
        CheckConstraint("matched_product_count >= 0", name="ck_product_results_matched_product_count"),
        CheckConstraint("competition_score IS NULL OR (competition_score >= 0 AND competition_score <= 100)", name="ck_product_results_competition_score"),
        {"comment": "商品竞品分析结果表"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="商品分析结果唯一 ID")
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("selection_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的选品分析任务 ID")
    matched_product_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="匹配到的商品数量")
    brand_distribution: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"), comment="品牌分布统计")
    category_distribution: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"), comment="类目分布统计")
    price_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="最低价格")
    price_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="最高价格")
    price_median: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="价格中位数")
    price_avg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True, comment="平均价格")
    competition_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="竞争强度评分，范围 0 到 100")
    sample_products: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="样例商品列表")
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, comment="商品数据来源")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")

