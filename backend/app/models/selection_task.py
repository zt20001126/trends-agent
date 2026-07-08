import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SelectionTask(Base):
    """选品分析任务持久化模型，用于记录每次关键词分析的生命周期。"""

    __tablename__ = "selection_tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed', 'completed_with_warnings')",
            name="ck_selection_tasks_status",
        ),
        {"comment": "选品分析任务主表"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="选品分析任务唯一 ID")
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, comment="用户输入的原始商品关键词")
    normalized_keyword: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="归一化后的英文检索关键词")
    country: Mapped[str] = mapped_column(String(10), nullable=False, default="US", server_default="US", comment="目标站点国家代码")
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="zh-CN", server_default="zh-CN", comment="用户输入语言")
    status: Mapped[str] = mapped_column(String(30), nullable=False, comment="任务状态")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="任务失败或部分失败的错误信息")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间")

