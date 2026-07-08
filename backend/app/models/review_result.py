import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewResult(Base):
    """评论痛点分析结果持久化模型，用于保存情感、痛点和改进建议。"""

    __tablename__ = "review_results"
    __table_args__ = (
        CheckConstraint("review_count >= 0", name="ck_review_results_review_count"),
        CheckConstraint("positive_ratio IS NULL OR (positive_ratio >= 0 AND positive_ratio <= 1)", name="ck_review_results_positive_ratio"),
        CheckConstraint("negative_ratio IS NULL OR (negative_ratio >= 0 AND negative_ratio <= 1)", name="ck_review_results_negative_ratio"),
        CheckConstraint("sentiment_score IS NULL OR (sentiment_score >= 0 AND sentiment_score <= 100)", name="ck_review_results_sentiment_score"),
        {"comment": "评论痛点分析结果表"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="评论分析结果唯一 ID")
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("selection_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的选品分析任务 ID")
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0", comment="参与分析的评论数量")
    positive_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True, comment="正面评论比例")
    negative_ratio: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True, comment="负面评论比例")
    sentiment_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="情感评分，范围 0 到 100")
    pain_points: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="用户痛点列表")
    improvements: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="产品改进建议列表")
    representative_reviews: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"), comment="代表性评论列表")
    data_source: Mapped[str] = mapped_column(String(50), nullable=False, comment="评论数据来源")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")

