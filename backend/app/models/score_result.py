import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScoreResult(Base):
    """选品机会评分持久化模型，用于保存各维度评分和综合机会分。"""

    __tablename__ = "score_results"
    __table_args__ = (
        CheckConstraint("trend_score IS NULL OR (trend_score >= 0 AND trend_score <= 100)", name="ck_score_results_trend_score"),
        CheckConstraint("competition_score IS NULL OR (competition_score >= 0 AND competition_score <= 100)", name="ck_score_results_competition_score"),
        CheckConstraint("pain_point_score IS NULL OR (pain_point_score >= 0 AND pain_point_score <= 100)", name="ck_score_results_pain_point_score"),
        CheckConstraint("profit_score IS NULL OR (profit_score >= 0 AND profit_score <= 100)", name="ck_score_results_profit_score"),
        CheckConstraint("opportunity_score IS NULL OR (opportunity_score >= 0 AND opportunity_score <= 100)", name="ck_score_results_opportunity_score"),
        {"comment": "选品机会评分结果表"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="评分结果唯一 ID")
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("selection_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的选品分析任务 ID")
    trend_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="趋势评分")
    competition_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="竞争机会评分")
    pain_point_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="痛点机会评分")
    profit_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="利润潜力评分")
    opportunity_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True, comment="综合机会评分")
    score_detail: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb"), comment="评分明细")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")

