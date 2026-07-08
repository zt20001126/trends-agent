import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Report(Base):
    """选品报告持久化模型，用于保存最终 Markdown 报告和摘要。"""

    __tablename__ = "reports"
    __table_args__ = {"comment": "选品分析报告表"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="报告唯一 ID")
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("selection_tasks.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的选品分析任务 ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="报告标题")
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False, comment="Markdown 格式报告正文")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="报告摘要")
    recommendation: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="开发建议枚举值")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")

