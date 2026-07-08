import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrendResult(Base):
    """趋势分析结果持久化模型，用于保存 Google Trends 或降级趋势数据。"""

    __tablename__ = "trend_results"
    __table_args__ = (
        CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 100)", name="ck_trend_results_trend_score"),
        {"comment": "趋势分析结果表"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="趋势分析结果唯一 ID")
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("selection_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的选品分析任务 ID")
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, comment="用于趋势分析的关键词")
    country: Mapped[str] = mapped_column(String(10), nullable=False, comment="趋势分析国家代码")
    trend_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="趋势评分，范围 0 到 100")
    growth_rate: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True, comment="趋势增长率")
    avg_interest: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="平均搜索热度")
    peak_interest: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="峰值搜索热度")
    trend_series: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="趋势时间序列")
    related_queries: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="相关查询词")
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, comment="趋势数据来源")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")

